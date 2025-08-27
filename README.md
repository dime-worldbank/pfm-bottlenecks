# PFM Bottleneck Analysis System

This repository contains two complementary approaches for identifying and analyzing bottlenecks in Public Financial Management (PFM) systems using AI-powered document analysis.

## Two Approaches

### 1. Structured Extraction Pipeline (`/structured_pipeline`)
A systematic three-stage pipeline that processes documents sequentially:
- **Stage 1: Extraction** - Identifies potential evidence from document chunks
- **Stage 2: Validation** - Validates evidence using structured sub-questions and criteria
- **Stage 3: Formatting** - Creates report-ready summaries with structured fields

**Key Features:**
- Uses Instructor library with Pydantic models for guaranteed structured outputs
- Hierarchical validation with multiple specific criteria per bottleneck
- Expert-in-the-loop design for iterative improvement
- Processes each chunk against one bottleneck at a time

### 2. Agentic Pipeline (`/agentic_pipeline`)
An agent-based approach using specialized agents working in coordination:
- **Pre-Filter Agent** - Reduces document chunks to find relevant spans
- **Multi-Bottleneck Classifier** - Simultaneously evaluates evidence against ALL bottlenecks
- **Causality Validator** - Explicitly validates causal claims within the text
- **Evidence Arbitrator** - Makes final decisions and resolves conflicts

**Key Features:**
- Competitive evaluation where evidence must "win" against all bottleneck types
- Explicit causation checking to reduce false positives
- Parallel bottleneck evaluation prevents misclassification
- Higher evidence thresholds with cross-validation

## Core Difference

**Structured Pipeline**: Sequential, methodical approach processing each chunk through defined stages for one bottleneck at a time. Best for systematic coverage and detailed validation trails.

**Agentic Pipeline**: Parallel, competitive approach where multiple agents evaluate evidence against all bottlenecks simultaneously. Best for reducing false positives and ensuring correct bottleneck assignment.

Both approaches use Azure OpenAI (GPT-4o) and are designed for Databricks environments processing World Bank PFM documents.

For detailed information about each approach, see the README files in their respective directories.