# PFM Bottleneck Analysis System

## Overview

The PFM (Public Finance Management) Bottleneck Analysis System is a text processing pipeline designed to identify, classify, and validate bottlenecks in public finance documents. The system processes pre-chunked text through a multi-stage pipeline that balances recall in early stages with precision in final validation.

## System Architecture

### High-Level Pipeline Flow

```mermaid
flowchart TB
    Start([Input: Pre-chunked Text]) --> Stage1[Stage 1: Pre-filter]
    Stage1 --> Decision1{Relevant?}
    Decision1 -->|No| End1([Discard Chunk])
    Decision1 -->|Yes| Stage2[Stage 2: Multi-Challenge Classification]

    Stage2 --> Stage3[Stage 3: Evidence Extraction]
    Stage3 --> Stage4[Stage 4: Agentic Validation]

    Stage4 --> FinalOutput([Final Validated Bottlenecks])

    style Start fill:#2e7d32,color:#fff
    style FinalOutput fill:#1976d2,color:#fff
    style End1 fill:#d32f2f,color:#fff
    style Stage1 fill:#424242,color:#fff
    style Stage2 fill:#424242,color:#fff
    style Stage3 fill:#424242,color:#fff
    style Stage4 fill:#424242,color:#fff
    style Decision1 fill:#616161,color:#fff
```

## Detailed Stage Descriptions

### Stage 1: Pre-filter
**Purpose:** Remove clearly irrelevant chunks to reduce processing overhead
**Approach:** Dual-path acceptance using embeddings and keyword matching
**Output:** Boolean relevance flag + processing hints

```mermaid
flowchart LR
    Input[Chunk Text] --> Embed[Embedding Generation]
    Input --> Keywords[Keyword Extraction]

    Embed --> SimScore[Similarity Score]
    Keywords --> KeyCount[Keyword Count]

    SimScore --> Decision{Similarity > 0.35<br/>OR<br/>Keywords >= 3}
    KeyCount --> Decision

    Decision -->|Yes| Accept[Accept + Hints]
    Decision -->|No| Reject[Reject]

    style Input fill:#424242,color:#fff
    style Embed fill:#546e7a,color:#fff
    style Keywords fill:#546e7a,color:#fff
    style SimScore fill:#616161,color:#fff
    style KeyCount fill:#616161,color:#fff
    style Decision fill:#5d4037,color:#fff
    style Accept fill:#2e7d32,color:#fff
    style Reject fill:#d32f2f,color:#fff
```

**Key Features:**
- No LLM calls (cost-effective)
- Uses sentence-transformers (all-mpnet-base-v2)
- Optimized for high recall

### Stage 2: Multi-Challenge Classification
**Purpose:** Classify chunks into relevant PF Challenges (multi-label)
**Approach:** LLM-based multi-label classification
**Output:** List of relevant challenges with confidence scores

```mermaid
flowchart TD
    Chunk[Filtered Chunk] --> LLM[LLM Classifier]
    LLM --> ML[Multi-Label Output]

    ML --> C1[Challenge 1: Revenue<br/>Confidence: 0.85]
    ML --> C2[Challenge 3: Expenditure<br/>Confidence: 0.72]
    ML --> C3[Challenge 7: Coordination<br/>Confidence: 0.91]

    style Chunk fill:#424242,color:#fff
    style LLM fill:#1565c0,color:#fff
    style ML fill:#546e7a,color:#fff
    style C1 fill:#f57c00,color:#fff
    style C2 fill:#f57c00,color:#fff
    style C3 fill:#f57c00,color:#fff
```

**Classification Schema:**
```python
{
    "chunk_id": "unique_identifier",
    "challenges": [
        {
            "challenge_id": 1,
            "challenge_name": "Revenue Management",
            "confidence": 0.85,
            "reasoning": "References tax collection inefficiencies"
        },
        {
            "challenge_id": 7,
            "challenge_name": "Institutional Coordination",
            "confidence": 0.91,
            "reasoning": "Discusses inter-agency communication issues"
        }
    ]
}
```

### Stage 3: Evidence Extraction
**Purpose:** Extract specific evidence spans for each bottleneck under relevant challenges
**Approach:** Structured extraction using LLM with targeted prompts
**Output:** Evidence spans mapped to specific bottlenecks

```mermaid
flowchart TD
    Input[Chunk + Relevant Challenges] --> Loop[For Each Challenge]

    Loop --> B1[Bottleneck 1.1]
    Loop --> B2[Bottleneck 1.2]
    Loop --> B3[Bottleneck 1.3]

    B1 --> Extract1[Extract Evidence Span]
    B2 --> Extract2[Extract Evidence Span]
    B3 --> Extract3[Extract Evidence Span]

    Extract1 --> Compile[Compile Evidence Map]
    Extract2 --> Compile
    Extract3 --> Compile

    style Input fill:#424242,color:#fff
    style Loop fill:#5d4037,color:#fff
    style B1 fill:#616161,color:#fff
    style B2 fill:#616161,color:#fff
    style B3 fill:#616161,color:#fff
    style Extract1 fill:#1565c0,color:#fff
    style Extract2 fill:#1565c0,color:#fff
    style Extract3 fill:#1565c0,color:#fff
    style Compile fill:#2e7d32,color:#fff
```

**Evidence Schema:**
```python
{
    "chunk_id": "unique_identifier",
    "evidence_map": [
        {
            "bottleneck_id": "1.1",
            "bottleneck_name": "Weak revenue forecasting",
            "evidence_span": "Revenue projections consistently overestimate by 20-30%...",
            "span_start": 145,
            "span_end": 289,
            "relevance_score": 0.78
        }
    ]
}
```

### Stage 4: Agentic Validation
**Purpose:** High-precision validation using multi-agent debate
**Approach:** Three-agent system with advocate, skeptic, and judge
**Output:** Final validated bottlenecks with confidence scores

```mermaid
flowchart TB
    Input[Evidence + Bottleneck Pair] --> Parallel{Parallel Processing}

    Parallel --> Advocate[Advocate Agent]
    Parallel --> Skeptic[Skeptic Agent]

    Advocate --> AdvArg[Pro Arguments:<br/>- Strong correlation<br/>- Clear causality<br/>- Multiple indicators]
    Skeptic --> SkepArg[Con Arguments:<br/>- Ambiguous language<br/>- Lack of specificity<br/>- Alternative explanations]

    AdvArg --> Judge[Judge Agent]
    SkepArg --> Judge

    Judge --> Decision{Validation Decision}
    Decision -->|Accept| Final[Validated Bottleneck<br/>Confidence: 0.87]
    Decision -->|Reject| Discard[Discard]

    style Input fill:#424242,color:#fff
    style Parallel fill:#5d4037,color:#fff
    style Advocate fill:#2e7d32,color:#fff
    style Skeptic fill:#f57c00,color:#fff
    style Judge fill:#1565c0,color:#fff
    style AdvArg fill:#388e3c,color:#fff
    style SkepArg fill:#ff6f00,color:#fff
    style Decision fill:#616161,color:#fff
    style Final fill:#1976d2,color:#fff
    style Discard fill:#d32f2f,color:#fff
```

## Agent Specifications

### Advocate Agent
**Role:** Build the strongest case for bottleneck relevance
**Focus:** Identify supporting evidence and connections
**Output Structure:**
```python
{
    "agent": "advocate",
    "bottleneck_id": "1.1",
    "argument": {
        "main_points": [...],
        "supporting_evidence": [...],
        "confidence": 0.82
    }
}
```

### Skeptic Agent
**Role:** Challenge the bottleneck assignment
**Focus:** Find weaknesses and alternative interpretations
**Output Structure:**
```python
{
    "agent": "skeptic",
    "bottleneck_id": "1.1",
    "argument": {
        "challenges": [...],
        "alternative_interpretations": [...],
        "weakness_score": 0.65
    }
}
```

### Judge Agent
**Role:** Evaluate both arguments and make final decision
**Focus:** Balanced assessment with justification
**Output Structure:**
```python
{
    "agent": "judge",
    "bottleneck_id": "1.1",
    "decision": "accept",
    "confidence": 0.87,
    "reasoning": "Advocate's evidence outweighs skeptic's concerns...",
    "key_factors": [...]
}
```

## PF Challenge and Bottleneck Structure

### 9 PF Challenges with 28 Bottlenecks

```mermaid
mindmap
  root((PFM System))
    Revenue Management
      Weak revenue forecasting
      Tax administration inefficiencies
      Narrow tax base
    Budget Planning
      Unrealistic budgeting
      Poor budget credibility
      Weak MTEF
    Expenditure Control
      Overspending
      Weak commitment controls
      Payment arrears
    Treasury Management
      Cash flow problems
      Fragmented accounts
      Idle balances
    Procurement
      Non-competitive practices
      Weak contract management
      Procurement delays
    Financial Reporting
      Delayed reports
      Poor data quality
      Lack of transparency
    Institutional Coordination
      Fragmented systems
      Weak communication
      Unclear roles
    Capacity Constraints
      Staff shortages
      Limited technical skills
      High turnover
    Technology Infrastructure
      Outdated systems
      Poor integration
      Limited automation
```

## Data Flow and Processing

### Input Data Format
```csv
node_id,chunk_id,chunk_text
DOC001,CHUNK001,"The revenue forecasting model has consistently..."
DOC001,CHUNK002,"Budget execution reports show significant..."
```

### Processing Pipeline Data Flow
```mermaid
flowchart LR
    CSV[CSV Input] --> Parse[Parse Chunks]
    Parse --> S1[Stage 1:<br/>Filter]
    S1 --> S2[Stage 2:<br/>Classify]
    S2 --> S3[Stage 3:<br/>Extract]
    S3 --> S4[Stage 4:<br/>Validate]

    S4 --> JSON[JSON Output]

    style CSV fill:#2e7d32,color:#fff
    style Parse fill:#424242,color:#fff
    style S1 fill:#546e7a,color:#fff
    style S2 fill:#546e7a,color:#fff
    style S3 fill:#546e7a,color:#fff
    style S4 fill:#546e7a,color:#fff
    style JSON fill:#1976d2,color:#fff
```

## Performance Optimization Strategy

### Stage-wise Optimization Goals

| Stage | Primary Goal | Secondary Goal | Metrics |
|-------|-------------|----------------|---------|
| Pre-filter | High Recall (>95%) | Speed | False Negative Rate |
| Classification | Balanced (F1>0.8) | Coverage | Precision, Recall |
| Extraction | High Recall (>90%) | Relevance | Evidence Quality |
| Validation | High Precision (>95%) | Justification | False Positive Rate |


## System Components

### Core Architecture
- **Stage 1: Pre-filter** - Embeddings + keyword matching for initial filtering
- **Stage 2: Multi-Challenge Classification** - LLM-based multi-label classifier
- **Stage 3: Evidence Extraction** - Structured extraction system for evidence spans
- **Stage 4: Agentic Validation** - Three-agent debate system for final validation
- **Bottleneck Definitions** - Complete taxonomy of 28 bottlenecks across 9 challenges
- **Pipeline Orchestration** - Modular processing with stage-wise optimization


### Key Design Decisions
1. **Staged Recall-to-Precision Strategy**: Early stages optimize for recall to avoid missing potential bottlenecks, while later stages focus on precision to ensure quality
2. **Agentic Validation**: The three-agent system provides explainable AI decisions with clear reasoning trails
3. **Modular Architecture**: Each stage can be independently improved, tested, and deployed
4. **Evidence-Based Approach**: All bottleneck assignments are traceable to specific text evidence

### Performance Considerations
- Pre-filter dramatically reduces LLM costs by eliminating 60% of chunks
- Parallel processing in agentic stage for improved throughput
- Caching strategies for repeated document processing
- Batch processing optimizations for large document sets
