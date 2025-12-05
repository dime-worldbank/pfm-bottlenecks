# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

# MAGIC %run ./service

# COMMAND ----------

# MAGIC %run ./document_ingestion

# COMMAND ----------

# MAGIC %run ./prefilter

# COMMAND ----------

# MAGIC %run ./consts

# COMMAND ----------

# MAGIC %run ./evidence_extraction

# COMMAND ----------

# MAGIC %run ./service

# COMMAND ----------

# MAGIC %run ./evidence_validation
