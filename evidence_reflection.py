# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %run ./service

# COMMAND ----------

# MAGIC %run ./consts

# COMMAND ----------

# MAGIC %run ./bottleneck_schemas

# COMMAND ----------

# MAGIC %run ./bottleneck_definitions

# COMMAND ----------

"""
Bottleneck Reflection - Minimal quality-control pass.

- Takes validated results where is_bottleneck_evidence == True
- Joins to the extractions table to get the extracted evidence span
- For each span, asks the LLM:

    "This was previously marked as evidence for this bottleneck.
     Should we KEEP it as evidence, or OVERTURN it and say it's not evidence?"

- Writes results to ..._reflection_results
"""

from typing import Optional, Literal
import pandas as pd
from tqdm import tqdm
from pydantic import BaseModel, Field

REFLECTION_SYSTEM_PROMPT = """
You are a cautious PFM diagnostic reviewer.
Each input span has ALREADY been marked as evidence for a specific bottleneck
by an earlier process.

Your ONLY job is to do a second-pass quality check and decide:
- Should we KEEP this span as valid evidence for THIS bottleneck?
- Or should we OVERTURN that decision and say this span is NOT evidence?

You must NOT upgrade or broaden any decision.
You can ONLY:
- confirm existing positives, or
- overturn them to non-evidence.

Be conservative and avoid false positives.
"""

class ReflectionDecision(BaseModel):
    """
    Minimal reflection output for a previously positive evidence item.

    - keep_as_evidence: True  -> confirm as valid evidence
                        False -> overturn to not evidence
    - decision: "confirm" or "overturn" (mirrors the boolean)
    - rationale: explanation
    - change_explanation: optional detail on why it was overturned
    """

    keep_as_evidence: bool = Field(
        ...,
        description=(
            "True if, after reflection, this span should STILL be treated as evidence "
            "for this bottleneck. False if the earlier positive should be overturned."
        ),
    )

    decision: Literal["confirm", "overturn"] = Field(
        ...,
        description=(
            '"confirm" → keep as evidence; '
            '"overturn" → mark as not evidence.'
        ),
    )

    rationale: str = Field(
        ...,
        description=(
            "2–4 sentence explanation referencing the extracted span and the bottleneck "
            "definition. Be concrete and avoid speculation."
        ),
    )

    change_explanation: Optional[str] = Field(
        None,
        description=(
            "If you overturn the original decision (decision='overturn'), briefly explain "
            "what was problematic about treating this as evidence."
        ),
    )

def build_reflection_prompt(bottleneck_def: dict, extracted_span: str) -> str:
    """
    Build the reflection prompt from:
    - bottleneck definition (and extended definition)
    - the extracted evidence span
    """
    name = bottleneck_def["name"]
    description = bottleneck_def["description"]
    extended = bottleneck_def.get("extended_definition") or ""

    return f"""
        You are reviewing whether a text span is genuinely evidence of a Public Finance Management bottleneck.

        IMPORTANT:
        - This span was ALREADY marked as evidence for this bottleneck in a previous step.
        - Your job is to either CONFIRM that decision or OVERTURN it.
        - You are NOT allowed to broaden or upgrade anything, only to keep or reject.

        BOTTLENECK:
        {name}

        DESCRIPTION:
        {description}

        EXTENDED DEFINITION:
        {extended}

        EXTRACTED SPAN (candidate evidence, previously marked POSITIVE):
        \"\"\"{extracted_span}\"\"\"

        TASK:
        Compare the EXTRACTED SPAN directly with the bottleneck definition and extended definition.

        Decide ONLY one of the following:
        - "confirm"  → the span clearly and specifically supports THIS bottleneck;
                    we should keep it as evidence.
        - "overturn" → the span does NOT sufficiently support this bottleneck, is too vague,
                    or is about something else; we should NOT treat it as evidence.

        Be conservative and avoid false positives.

        Return ONLY JSON that matches the ReflectionDecision schema you have been given.
        Do NOT invent other labels or keys.
        """

def run_reflection(schema: str, bottleneck_id: str):
    """
    Run reflection on validated evidence for a given bottleneck.

    - Reads:
        rpf_bottleneck_{id}_validated_results
        rpf_bottleneck_{id}_extractions
    - Filters:
        Only rows where is_bottleneck_evidence == True
    - Writes:
        rpf_bottleneck_{id}_reflection_results
    """

    validated_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_validated_results"
    extraction_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"
    reflection_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_reflection_results"

    if spark.catalog.tableExists(f"{schema}.{reflection_table}"):
        print(f"Skipping reflection; table exists: {schema}.{reflection_table}")
        return

    data = load_bottlenecks()
    challenge_id = int(bottleneck_id.split(".")[0])
    challenge = data["challenges"][challenge_id]

    bottleneck_def = None
    for bn in challenge["bottlenecks"]:
        if bn["id"] == bottleneck_id:
            bottleneck_def = bn
            break

    if bottleneck_def is None:
        raise ValueError(f"Bottleneck {bottleneck_id} not found in definitions")

    validated_df = spark.table(f"{schema}.{validated_table}").toPandas()
    if validated_df.empty:
        print(f"No validated results found for {bottleneck_id}")
        return

    positives = validated_df[validated_df["is_bottleneck_evidence"] == True].copy()
    if positives.empty:
        print(f"No positive evidence to reflect for {bottleneck_id}")
        return

    extraction_df = (
        spark.table(f"{schema}.{extraction_table}")
        .select("node_id", "chunk_id", "extracted_evidence")
        .toPandas()
    )

    merged = positives.merge(
        extraction_df,
        on=["node_id", "chunk_id"],
        how="left",
        validate="many_to_one",
    )

    print(f"Reflecting on {len(merged)} items for bottleneck {bottleneck_id}...")

    service = Service(dbutils)
    results = []

    for idx, row in tqdm(merged.iterrows(), total=merged.shape[0]):
        row_dict = row.to_dict()
        span = row_dict.get("extracted_evidence") or ""

        prompt = build_reflection_prompt(bottleneck_def, span)

        try:
            reflection: ReflectionDecision = service.execute(
                prompt=prompt,
                model=LLM_MODEL,
                response_model=ReflectionDecision,
                system_message=REFLECTION_SYSTEM_PROMPT,
            )

            ref = reflection.model_dump()

            original_was_positive = True  
            final_is_positive = ref["keep_as_evidence"]

            ref["node_id"] = row_dict["node_id"]
            ref["chunk_id"] = row_dict["chunk_id"]
            ref["bottleneck_id"] = bottleneck_id
            ref["extracted_span"] = span
            ref["original_decision"] = row_dict["decision"]
            ref["original_is_bottleneck_evidence"] = original_was_positive

            if ref["keep_as_evidence"]:
                ref["decision"] = "confirm"
            else:
                ref["decision"] = "overturn"

            ref["decision_changed"] = (final_is_positive != original_was_positive)

            results.append(ref)

        except Exception as e:
            print(f"Error reflecting chunk {row_dict.get('chunk_id')}: {e}")
            results.append(
                {
                    "node_id": row_dict["node_id"],
                    "chunk_id": row_dict["chunk_id"],
                    "bottleneck_id": bottleneck_id,
                    "extracted_span": span,
                    "original_decision": row_dict["decision"],
                    "original_is_bottleneck_evidence": True,
                    "keep_as_evidence": False,
                    "decision": "overturn",
                    "rationale": "Reflection step failed; conservatively overturning.",
                    "change_explanation": f"Error: {str(e)}",
                    "decision_changed": True,
                }
            )

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{reflection_table}")

    changed = results_df["decision_changed"].sum()
    print(f"Reflection completed. {changed} / {len(results_df)} decisions were overturned.")
    print(f"Saved to {schema}.{reflection_table}")

