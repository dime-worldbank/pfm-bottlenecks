# Databricks notebook source
from __future__ import annotations

from typing import Optional, Type
from pydantic import BaseModel
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential, get_bearer_token_provider
import instructor


class Service:

    DEFAULT_SYSTEM_PROMPT = """You are a public finance expert working at a multilateral development bank. 
    Your job is to identify and evaluate evidence of bottlenecks in Public Financial Management (PFM) systems, 
    based on diagnostic reports, budget support documents, and public expenditure reviews.

    You are especially trained to distinguish between:
    - vague or aspirational language vs. concrete implementation gaps,
    - general governance issues vs. specific failures of leadership commitment,
    - PFM system reform vs. follow-through on approved policy actions.

    Only validate a chunk as evidence for a bottleneck if it meets the precise criteria described.
    """

    def __init__(self, dbutils, system_prompt: Optional[str] = None):
        """
        Initializes the Service with a Databricks dbutils secrets client.
        """
        credential = ClientSecretCredential(
            tenant_id=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Tenant-ID"),
            client_id=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Client-ID"),
            client_secret=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Client-Secret"),
        )

        token_provider = get_bearer_token_provider(
            credential,
            dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Token-Cred"),
        )

        client = AzureOpenAI(
            azure_endpoint="https://azapim.worldbank.org/conversationalai/v2/",
            azure_ad_token_provider=token_provider,
            api_version="2024-08-01-preview",
        )

        self.client = instructor.from_openai(
            client,
            mode=instructor.Mode.JSON,
        )
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT

    def execute(
        self,
        *,
        prompt: str,
        model: str,
        response_model: Type[BaseModel],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
    ) -> BaseModel:
        """
        Executes a structured chat completion against Azure OpenAI.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")

        messages = [
            {"role": "system", "content": system_message or self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=response_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


# COMMAND ----------


