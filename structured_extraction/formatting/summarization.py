"""
Evidence summarization and formatting for final reports
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
import pandas as pd


class StructuredSummaryFields(BaseModel):
    """Structured fields extracted from evidence for report generation"""
    
    country: str = Field(
        ..., 
        description="Country referenced in the extracted evidence."
    )
    
    issue_area: Optional[str] = Field(
        None, 
        description="Main sector or topic affected by the bottleneck."
    )
    
    reference_to_policy_or_program: Optional[str] = Field(
        None, 
        description="Any specific or general policy referenced in the context of the extracted evidence."
    )
    
    reference_outcome: Optional[str] = Field(
        None, 
        description=(
            "What development or sectoral outcome is affected by the lack of leadership commitment? "
            "This could include unmet policy goals, reduced service delivery, poor implementation, "
            "or failure to achieve intended change. This is from the reference extracted evidence for the bottleneck"
        )
    )
    
    key_constraint: str = Field(
        ..., 
        description="Describe what constraint is being evidenced."
    )
    
    observed_consequence: Optional[str] = Field(
        None, 
        description="Any outcome or effect of the constraint."
    )
    
    metric_or_statistic: Optional[str] = Field(
        None, 
        description="Quantitative detail if present (e.g., a funding gap, percentage)."
    )
    
    closest_sdg: Optional[str] = Field(
        None, 
        description=(
            "If directly relevant, mention the closest Sustainable Development Goal (SDG). "
            "Leave blank if nothing is directly relevant. If present and relevant then report this "
            "in the form in this example format 'SDG 16: Peace, Justice and Strong Institutions'"
        )
    )
    
    closest_sdg_target: Optional[str] = Field(
        None, 
        description=(
            "If directly relevant, mention the closest Sustainable Development Goal (SDG) target. "
            "Leave blank if nothing is directly relevant. If relevant use the format in the following example: "
            "'Eliminate all harmful practices, such as child, early and forced marriage and female genital mutilation'"
        )
    )


class StylizedSummary(BaseModel):
    """Final stylized summary for reports"""
    
    summary_text: str = Field(
        ..., 
        description="A short, stylized summary suitable for inclusion in a public finance report."
    )


class DateRangeExtraction(BaseModel):
    """Extract temporal context from evidence"""
    
    date_or_range: Optional[str] = Field(
        None,
        description=(
            "Return a specific and concrete date or date range (e.g., '2012', '2009–2014', 'FY2020/21', 'January 1, 2010') "
            "that is clearly relevant to the issue described in the extracted evidence. "
            "Do not return vague or generic expressions like 'recent years', 'early period', or 'in the past'. "
            "If no relevant date exists, return null."
        )
    )


class SummarizationService:
    """Service for creating structured summaries from validated evidence"""
    
    def __init__(self, llm_service, model: str = "gpt-4o"):
        """
        Initialize summarization service
        
        Args:
            llm_service: Azure OpenAI service instance
            model: LLM model to use
        """
        self.llm_service = llm_service
        self.model = model
    
    def get_context(self, df_chunks: pd.DataFrame, node_id: str, 
                   chunk_id: int, context_size: int = 2) -> str:
        """
        Get context chunks around the target chunk
        
        Args:
            df_chunks: DataFrame with all chunks
            node_id: Node ID of the target chunk
            chunk_id: Chunk ID of the target chunk
            context_size: Number of chunks before target to include
            
        Returns:
            Combined context text
        """
        node_id = str(node_id)
        context_chunk_ids = [chunk_id - i for i in range(context_size, 0, -1)]
        chunks = df_chunks[
            (df_chunks.node_id == node_id) & 
            (df_chunks.chunk_id.isin(context_chunk_ids))
        ].sort_values('chunk_id').text.values.tolist()
        return '\n\n'.join(chunks)
    
    def extract_structured_fields(self, context_text: str, extracted_evidence: str,
                                 bottleneck_name: str, bottleneck_description: str,
                                 metadata: Tuple, examples: List[str]) -> StructuredSummaryFields:
        """
        Extract structured fields from evidence
        
        Args:
            context_text: Full context from document
            extracted_evidence: Validated evidence excerpt
            bottleneck_name: Name of the bottleneck
            bottleneck_description: Description of the bottleneck
            metadata: Tuple of (country, doc_name, region, topic_text)
            examples: Example summaries for guidance
            
        Returns:
            Structured summary fields
        """
        prompt = self._make_structured_summary_prompt(
            context_text, extracted_evidence, bottleneck_name,
            bottleneck_description, metadata, examples
        )
        
        return self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=StructuredSummaryFields
        )
    
    def create_stylized_summary(self, extracted_evidence: str,
                               structured: StructuredSummaryFields,
                               bottleneck_name: str, examples: List[str]) -> str:
        """
        Create final stylized summary from structured fields
        
        Args:
            extracted_evidence: Original evidence text
            structured: Structured fields
            bottleneck_name: Name of the bottleneck
            examples: Example summaries for tone guidance
            
        Returns:
            Final summary text
        """
        prompt = self._make_summary_from_structure_prompt(
            extracted_evidence, structured, bottleneck_name, examples
        )
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=StylizedSummary
        )
        
        return result.summary_text
    
    def extract_date_range(self, extended_context: str, extracted_evidence: str,
                          bottleneck_name: str) -> Optional[str]:
        """
        Extract date or date range from evidence
        
        Args:
            extended_context: Full context
            extracted_evidence: Evidence excerpt
            bottleneck_name: Name of the bottleneck
            
        Returns:
            Date or date range if found
        """
        prompt = self._make_date_range_prompt(
            extended_context, extracted_evidence, bottleneck_name
        )
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=DateRangeExtraction
        )
        
        return result.date_or_range
    
    def _make_structured_summary_prompt(self, context_text: str, extracted_evidence: str,
                                       bottleneck_name: str, bottleneck_description: str,
                                       metadata_tuple: Tuple, examples: List[str]) -> str:
        """Create prompt for structured field extraction"""
        
        country, doc_name, region, topic_text = metadata_tuple
        example_block = "\n".join(f"- {ex}" for ex in examples)
        
        return f"""
        You are a public finance expert working at a multilateral development bank.

        Your task is to extract structured components that support stylized, policy-relevant summaries
        of public financial management (PFM) bottlenecks.

        You are given:
        - Context text from a fiscal diagnostic report
        - A validated excerpt from that context which supports a known PFM bottleneck referred to as the extracted evidence
        - Document metadata (e.g., country, region, topics)
        - A bottleneck definition (e.g., inadequate leadership commitment, funding fragmentation)

        ---

        Document:
        - Country: {country}
        - Title of document: {doc_name}
        - Region: {region}
        - Topics: {topic_text}

        Bottleneck:
        **{bottleneck_name}** → {bottleneck_description}

        ---

        Here is the full context from the document:
        {context_text}

        Here is the specific quote that was validated as evidence (extracted evidence) for the bottleneck titled {bottleneck_name}:
        \"\"\"{extracted_evidence}\"\"\"

        ---

        Your task is to extract the following structured fields:
        - Country
        - Issue Area (e.g., health, education, fiscal management, GBV, etc.)
        - Reference to policy or program (if applicable)
        - Key constraint (explain what's blocking implementation or delivery)
        - Observed consequence (if mentioned)
        - Metric or statistic (if present)

        Only extract what is clearly grounded in the text. Do not invent or infer missing details.

        ---

        To guide your understanding of the level of detail and relevance we expect, here are some example summaries that your structured fields will ultimately help produce:

        {example_block}
        """.strip()
    
    def _make_summary_from_structure_prompt(self, extracted_evidence: str,
                                           structured: StructuredSummaryFields,
                                           bottleneck_name: str, examples: List[str]) -> str:
        """Create prompt for final summary generation"""
        
        example_block = "\n".join(f"- {ex}" for ex in examples)
        
        return f"""
        You are writing a concise, report-style summary of a public finance implementation bottleneck. 
        The main content for this summary is the extracted evidence from document chunks: {extracted_evidence}

        In order to frame the summary -- you can refer to information in the structured input as well as some sample examples as shown below. 

        Match the tone following examples:

        {example_block}

        ---

        Use the structured information below to generate a clear, concise summary (1–5 sentences).
        The summary should:
        - Mention the **country**
        - Describe the **constraint** clearly
        - Refer to the **policy or program** (if relevant)
        - Include **consequence or impact**
        - Refer to the **outcome** (if relevant)
        - Mention **quantitative figures** if present
        - Do not remove any information that is already present. Keep all existing details but structure it in form and tone of the examples shown.
        - Do not add extra commentary unless this information is already present in the input information. 
        - Do not explicitly include SDGs unless mentioned in the extracted evidence. 

        Structured input:
        {structured.model_dump_json(indent=2)}
        """.strip()
    
    def _make_date_range_prompt(self, extended_context: str, extracted_evidence: str,
                               bottleneck_name: str) -> str:
        """Create prompt for date extraction"""
        
        return f"""
        You are analyzing text to identify a **year or year range** that helps contextualize a public finance bottleneck.
         
        Inputs:
        - The extended context (surrounding paragraph)
        - A highlighted excerpt from that context (the extracted evidence)
        - The name of the bottleneck being analyzed
         
        Your task:
        - Return the **most relevant year or year range** (e.g., "2012", "2015–2020") that refers to when the bottleneck occurred or was discussed.
        - The date or range can appear anywhere in the extended context — not just the extracted evidence — but must clearly relate to the **issue described** in the extracted evidence.
        - Prefer returning **years** or **year ranges**, not full dates (avoid things like "January 1, 2010" unless highly specific).
        - ❗ Do NOT return vague expressions like:
            - "recent years"
            - "early reform period"
            - "in the past"
        - If no relevant and specific year or year range can be found, return null.
        - The extracted year or range must be related to the extracted evidence and not just year or year range mentioned in the context but unrelated to the bottleneck
         
        ---
         
        **Bottleneck:**
        {bottleneck_name}
         
        **Extended context:**
        \"\"\"{extended_context}\"\"\"
         
        **Extracted evidence:**
        \"\"\"{extracted_evidence}\"\"\"
         
        ---
         
        Return format:
        - A single year: "2012"
        - Or a year range: "2015–2020"
        - Or null if not applicable
        """.strip()