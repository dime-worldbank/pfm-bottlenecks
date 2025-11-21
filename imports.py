# Databricks notebook source
# MAGIC %pip install -U openai azure-identity instructor sentence-transformers "pydantic>=2.4"

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
