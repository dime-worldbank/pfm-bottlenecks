# challenge_classification.py
# Stage 1: MULTILABEL classifier → returns which challenges look relevant (scores only).
# Stage 2 (separate module) will extract verbatim evidence per accepted challenge.

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from service import Service
from bottleneck_definitions import load_bottlenecks
from models import (
    ChallengeID, ChallengeHit, ChallengeLabelSet,
    MultiLabelDecision, DecisionReason
)

SYSTEM_MESSAGE = """
You are a multilabel classifier for Public Finance challenges.

Rubric:
- Use ONLY the provided chunk; no outside knowledge.
- Include a challenge ONLY if you can provide ONE short verbatim quote copied exactly from the chunk that supports it.
- If you cannot find such a quote for a challenge, OMIT that challenge.
- Recommendations (“should”, “adopt”, “proposed”) count as implicit evidence of current constraints.
- Calibrate scores conservatively and sort by score descending.
- The calling tool enforces the exact response schema; ignore formatting concerns.
"""

def render_taxonomy_context() -> str:
    """Compact taxonomy: challenge name + bottleneck names as cues."""
    data = load_bottlenecks()
    lines: List[str] = []
    for i in range(1, 10):
        lines.append(data['challenges'][i]['description'])
    return "\n".join(lines)

def build_classification_prompt(chunk_text: str) -> str:
    """
    Ground the model with your taxonomy + task framing.
    No schema/JSON instructions—`instructor` handles shape.
    """
    example = (
        "Reasoning example (no output format): If a chunk mentions off-budget donor units and mid-year cash "
        "rationing, map to Challenge 6 (fragmented/uncoordinated resources). If it also mentions misaligned "
        "spending plans, Challenge 5 may apply."
    )
    return (
        "Classify the following chunk into the Public Finance challenges listed below.\n"
        "Challenge taxonomy (names + bottlenecks as cues):\n"
        f"{render_taxonomy_context()}\n\n"
        f"{example}\n\n"
        "Chunk:\n```\n"
        f"{chunk_text}\n"
        "```"
    )

@dataclass
class ChallengeClassifier:
    model: str = "openai/gpt-4o-mini"
    confidence_threshold: float = 0.60
    service: Optional[Service] = None

    def __post_init__(self):
        if self.service is None:
            self.service = Service()

    def classify(self, chunk_text: str) -> MultiLabelDecision:
        prompt = build_classification_prompt(chunk_text)

        result: ChallengeLabelSet = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ChallengeLabelSet,
            system_message=SYSTEM_MESSAGE,
        )

        # Abstain
        if not result.labels:
            return MultiLabelDecision(
                accepted=False,
                reason=DecisionReason.MODEL_ABSTAIN,
                accepted_labels=[],
                raw_result=result,
            )

        # Thresholding
        accepted = [lab for lab in result.labels if float(lab.score) >= float(self.confidence_threshold)]

        if accepted:
            return MultiLabelDecision(
                accepted=True,
                reason=DecisionReason.OK,
                accepted_labels=accepted,
                raw_result=result,
            )

        return MultiLabelDecision(
            accepted=False,
            reason=DecisionReason.LOW_CONFIDENCE,
            accepted_labels=[],
            raw_result=result,
        )





chunk = '''inistrations and non-State actors.

127. In order to remedy these imbalances and inefficiencies and revive the sector’s capacity to produce
     and sustain robust growth, the following areas of reform are proposed:

   i.     Improve technical efficiency. Different dimensions of the policy set for consideration are:
                - Rationalizing the allocation of sector expenditures envelope. Capital spending should
                  be increased, and the level at which it is incurred (public infrastructure,
                  infrastructure - such as irrigation schemes or storage facilities - handed over to
                  beneficiaries, Government or non-Government support services) should be
                  recorded through adequate budget coding.
                - Correcting current imbalances in agricultural public expenditures in favor of
                  agriculture commercialization and market development (including rural finance),
                  land and water sustainable management, technology research and development,
                  and dissemination and livestock development.
                - Adopting a new budget presentation allowing better accounting and thus better
                  planning and monitoring of both capital and recurrent spending and adequate
                  provisions for operation and maintenance costs.
                - As part of the overall PMF strengthening, ensuring full rolling out of IFMIS to
                  generate comprehensive and real-time budget execution data.
                - Streamlining procurement procedures, strengthening M&E at all levels.
                - Correcting the erosion of civil servants’ salaries combined with enhanced
                  performance assessment mechanisms, and discontinuing the use of travel
                  allowances as salary supplement.
                - Using the calendar year as the fiscal year could also be worth-considering.



                                                      53
   ii. Operationalize the ASWAp investment framework for which only the apex oversight bodies
       are in place at the moment, in order to increase ownership and accountability and establish
       a stronger linkage between policy framework and budget planning. In particular, MoAFS
       organizational chart and budget should be adjusted to become consistent with ASWAp
       architecture; all DP financed activities should be brought into MoAFS Budget in order to
       facilitate strategic planning and increase MoAFS fiscal space; as fiduciary capacities increase,
       DPs should make greater use of both Government systems and common financing mechanisms in
       order to further increase fiscal space and reduce aid transaction costs; finally, financial resources
       should be constantly reallocated from unsuccessful initiatives to more promising ones with the
       objective of spending better ke_user_promprather than spending more;
   iii. Re-design FISP in order to serve productive farmers in a market-smart way and
        concomitantly, strengthen pro-poor safety nets(cash transfer, rural pensions, public works,
        etc.). There is now some consensus that targeting has not been effective and has generated fraud
        and distortions. Attempts at tightening targeting would most probably merely exacerbate further
        these issues. This calls for a shift of paradigm in reforming FISP with less emphasis put on
        targeting and avoiding commercial sales displacement and more on eliminating fraud, corruption
        and distortions, and promoting private sector participation. The re-designed FISP would have to
        be accompanied by enhanced social safety nets as the most vulnerable may not get any longer the
        cash transfer they were getting through the reselling of their fertilizer allocation under the current
        system;
   iv. Foster the decentralization process that will be revived in 2014 with the election of the
       District Assemblies, through a greater involvement of District administration, local
       communities, farmers’ organizations, NGOs and private operators. Matching grants to
       finance demand-driven initiatives by local communities or local promoters with the technical
       support of the deconcentrated administration have proved powerful tools to support
       decentralization in other countries (e.g. Burkina Faso).

128. As a concluding remark, let us recall that to be a factor of change and progress, commitment
     by all stakeholders must go beyond intentions and translate into changes in processes and
     organizational arrangements. Most of the recommendations listed above are not new and were
     already formulated in previous studies and documents by the GoM itself (e.g. MPRS) more than 10
     years ago. One critical recommendation is therefore to start implementing and operationalizing the
     agreed recommendations. A number of Malawi strategies had ve'''

clf = ChallengeClassifier()
dec = clf.classify(chunk)
print(dec.raw_result.labels[0].evidence_span)
dec.raw_result

import pandas as pd
df = pd.read_csv('data/per_pfr_chunks_with_prefilter_results.csv')

ddf = df[df.prefilter_results]
ddf.sample(10).text.values.tolist
