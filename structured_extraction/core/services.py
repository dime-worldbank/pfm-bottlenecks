"""
Azure OpenAI Service Integration for PFM Bottleneck Analysis
"""
import instructor
from abc import ABC
from typing import Optional, Type
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential, get_bearer_token_provider


class BaseService(ABC):
    """
    Base class for all services. Automatically registers subclasses with the ServiceRegistry.
    """

    def __init_subclass__(cls, **kwargs):
        """
        Automatically registers subclasses with the ServiceRegistry when they are defined.
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "service_name") or not isinstance(cls.service_name, str):
            raise AttributeError(
                f"Service class '{cls.__name__}' must define a string 'service_name'."
            )


class AzureOpenAIService(BaseService):
    """
    A service for interacting with Azure OpenAI using Instructor.
    """

    service_name = "azureopenai"
    
    DEFAULT_SYSTEM_PROMPT = """You are a public finance expert working at a multilateral development bank. 
Your job is to identify and evaluate evidence of bottlenecks in Public Financial Management (PFM) systems, 
based on diagnostic reports, budget support documents, and public expenditure reviews.

You are especially trained to distinguish between:
- vague or aspirational language vs. concrete implementation gaps,
- general governance issues vs. specific failures of leadership commitment,
- PFM system reform vs. follow-through on approved policy actions.

Only validate a chunk as evidence for a bottleneck if it meets the precise criteria described."""

    def __init__(
        self,
        client: AzureOpenAI,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the AzureOpenAIService with an existing AzureOpenAI client.
        """
        self.SYSTEM_PROMPT = system_prompt or self.DEFAULT_SYSTEM_PROMPT

        # Wrap your AzureOpenAI client using instructor
        self.client = instructor.from_openai(
            client,
            mode=instructor.Mode.JSON,
        )

    def execute(
        self,
        prompt: str,
        model: str,
        response_model: Type,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs,
    ):
        """
        Executes a structured chat completion.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("The 'prompt' must be a non-empty string.")
        if not isinstance(model, str):
            raise ValueError("The 'model' must be a string.")

        system_message = system_message or self.SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=model,
                response_model=response_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response

        except Exception as e:
            raise Exception(f"Error in AzureOpenAI API call: {e}")


def create_azure_client(dbutils):
    """
    Create and configure Azure OpenAI client for Databricks environment
    """
    credential = ClientSecretCredential(
        tenant_id=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Tenant-ID"),
        client_id=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Client-ID"),
        client_secret=dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Client-Secret")
    )
    
    token_provider = get_bearer_token_provider(
        credential, 
        dbutils.secrets.get(scope="DAPGPTKEYVAULT", key="GPT-APIM-Token-Cred")
    )
    
    client = AzureOpenAI(
        azure_endpoint="https://azapim.worldbank.org/conversationalai/v2/",
        azure_ad_token_provider=token_provider,
        api_version="2024-08-01-preview"
    )
    
    return client