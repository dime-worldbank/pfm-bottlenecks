## Methodology References

**Staged Decision-Making Architecture**

Self-Verification Improves Few-Shot Clinical Information Extraction (Gero et al., 2023)
https://arxiv.org/abs/2306.00024
- Supports using separate extraction and verification steps. Shows LLMs can effectively verify their own outputs by grounding them in evidence spans.

Self-Reflection in LLM Agents: Effects on Problem-Solving Performance (Renze & Guven, 2024)
https://arxiv.org/abs/2405.06682
- Demonstrates self-reflection significantly improves performance (p < 0.001). Validates having a separate reflection step to review validation outputs.The basic idea predates this paper, and the principle being that a complex task split into multiple steps increases accuracy of the output.

**Multi-Agent Validation**

Improving Factuality and Reasoning in Language Models through Multiagent Debate (Du et al., 2023)
https://arxiv.org/abs/2305.14325
- Shows multi-agent debate reduces hallucinations and improves factual accuracy.

Can LLM Agents Really Debate? A Controlled Study (2024)
https://arxiv.org/abs/2511.07784
- Debate achieves >90% correction rates vs <55% without debate. Quantifies value of multi-agent validation.

We tried an alternate multi-agent archecture involving an advocate, skeptic and judge agents in a debate set-up as shown in the references above. This was discarded since the output was harder to control as we needed to incorporate expert feedback. This architecture was harder to maintain and didn't give any significant adfvantages over the sequential architecture that we currently have.

**Pipeline Architecture**

Understanding and Optimizing Multi-Stage AI Inference Pipelines (2025)
https://arxiv.org/abs/2504.09775
- Validates cascading multi-stage approaches for complex LLM tasks.
