"""
Prompt generation functions for the bottleneck analysis pipeline
"""
from typing import Optional, List, Type


def make_bottleneck_prompt(
    text: str,
    role_of_public_finance: str,
    role_description: str,
    challenge_name: str,
    challenge_description: str,
    bottleneck_name: str,
    bottleneck_description: str,
    bottleneck_examples: Optional[List[str]] = None
) -> str:
    """
    Create prompt for bottleneck extraction
    
    Args:
        text: Chunk text to analyze
        role_of_public_finance: Role category
        role_description: Description of the role
        challenge_name: Name of the PFM challenge
        challenge_description: Description of the challenge
        bottleneck_name: Name of the specific bottleneck
        bottleneck_description: Description of the bottleneck
        bottleneck_examples: Optional examples of valid evidence
        
    Returns:
        Formatted prompt string
    """
    example_section = ""
    if bottleneck_examples:
        formatted = "\n".join(f"- {ex}" for ex in bottleneck_examples)
        example_section = f"""
        Examples of valid evidence for this bottleneck include:
        {formatted}
        """.strip()

    return f"""
        You are analyzing a public finance document to identify specific bottlenecks affecting development outcomes.
        
        The context for your analysis is as follows:
        
        Role of Public Finance: {role_of_public_finance}
        → {role_description}
        
        PFM Challenge: {challenge_name}
        → {challenge_description}
        
        Specific Bottleneck: {bottleneck_name}
        → {bottleneck_description}
        
        {example_section}
        
        ---
        
        Your task:
        
        - Carefully read the excerpt below.
        - Extract direct evidence from the text that clearly supports the presence of the specific bottleneck listed above.
        - Only extract text that is explicitly present in the excerpt.
        - Do not infer, assume, or include information that is not stated.
        - If you find no clear evidence, return null.
        
        For each piece of extracted evidence, briefly explain your reasoning (i.e., why this excerpt indicates the bottleneck), and indicate if the match is ambiguous.
        
        Text to analyze:
        
        {text}
        """.strip()


def make_validation_prompt(
    extracted_evidence: str,
    reasoning: str,
    role_of_public_finance: str,
    role_description: str,
    challenge_name: str,
    challenge_description: str,
    bottleneck_name: str,
    bottleneck_description: str,
    validation_model_cls: Optional[Type] = None,
    bottleneck_examples: Optional[List[str]] = None
) -> str:
    """
    Create prompt for evidence validation
    
    Args:
        extracted_evidence: Previously extracted evidence text
        reasoning: Reasoning for the extraction
        role_of_public_finance: Role category
        role_description: Description of the role
        challenge_name: Name of the PFM challenge
        challenge_description: Description of the challenge
        bottleneck_name: Name of the specific bottleneck
        bottleneck_description: Description of the bottleneck
        validation_model_cls: Validation model class with guidance method
        bottleneck_examples: Optional examples of valid evidence
        
    Returns:
        Formatted validation prompt string
    """
    # Get bottleneck-specific guidance if available
    bottleneck_specific_criteria = ""
    if validation_model_cls and hasattr(validation_model_cls, "validation_guidance"):
        bottleneck_specific_criteria = validation_model_cls.validation_guidance()

    # Format examples, if provided
    example_text_block = ""
    if bottleneck_examples:
        formatted_examples = "\n".join(f"- {ex}" for ex in bottleneck_examples)
        example_text_block = (
            "Here are some representative examples of valid evidence for this bottleneck:\n"
            f"{formatted_examples}"
        )

    # Compose the full prompt
    return f"""
        You are validating whether a previously extracted piece of text is strong evidence of a specific bottleneck in public finance.

        Here is the context:

        Role of Public Finance: {role_of_public_finance}
        → {role_description}

        PFM Challenge: {challenge_name}
        → {challenge_description}

        Specific Bottleneck: {bottleneck_name}
        → {bottleneck_description}

        {("Additional evaluation criteria:" + bottleneck_specific_criteria) if bottleneck_specific_criteria else ""}
        {f"{example_text_block}" if example_text_block else ""}

        ---

        Extracted Evidence:
        {extracted_evidence}

        Reasoning for Extraction:
        {reasoning}

        ---

        Your task:

        - First, evaluate whether the evidence is general, misplaced, insufficient, or misclassified using the bottleneck-specific criteria above.
        - Then, reflect on those evaluations to decide:
            - Does this evidence clearly and directly support the bottleneck?
            - Is the reasoning plausible and grounded in the evidence?
        - If the evidence is vague, general, or fits another bottleneck better, mark `is_valid` as False.
        - Ensure the `is_valid` field reflects your judgment based on the flags you select.
        - Your validation reasoning must explain how the intermediate evaluations informed your final decision.
        """.strip()


def make_validation_prompt_with_chunk(
    extracted_evidence: str,
    chunk: str,
    role_of_public_finance: str,
    role_description: str,
    challenge_name: str,
    challenge_description: str,
    bottleneck_name: str,
    bottleneck_description: str,
    validation_model_cls: Optional[Type] = None,
    bottleneck_examples: Optional[List[str]] = None
) -> str:
    """
    Create prompt for evidence validation including original chunk
    
    Args:
        extracted_evidence: Previously extracted evidence text
        chunk: Original chunk text
        role_of_public_finance: Role category
        role_description: Description of the role
        challenge_name: Name of the PFM challenge
        challenge_description: Description of the challenge
        bottleneck_name: Name of the specific bottleneck
        bottleneck_description: Description of the bottleneck
        validation_model_cls: Validation model class with guidance method
        bottleneck_examples: Optional examples of valid evidence
        
    Returns:
        Formatted validation prompt string
    """
    # Get bottleneck-specific guidance if available
    bottleneck_specific_criteria = ""
    if validation_model_cls and hasattr(validation_model_cls, "validation_guidance"):
        bottleneck_specific_criteria = validation_model_cls.validation_guidance()

    # Format examples, if provided
    example_text_block = ""
    if bottleneck_examples:
        formatted_examples = "\n".join(f"- {ex}" for ex in bottleneck_examples)
        example_text_block = (
            "Here are some representative examples of valid evidence for this bottleneck:\n"
            f"{formatted_examples}"
        )

    # Compose the full prompt
    return f"""
        You are validating whether a previously extracted piece of text is strong evidence of a specific bottleneck in public finance.

        Here is the context:

        Role of Public Finance: {role_of_public_finance}
        → {role_description}

        PFM Challenge: {challenge_name}
        → {challenge_description}

        Specific Bottleneck: {bottleneck_name}
        → {bottleneck_description}

        {("Additional evaluation criteria:" + bottleneck_specific_criteria) if bottleneck_specific_criteria else ""}
        {f"{example_text_block}" if example_text_block else ""}

        ---

        Extracted Evidence:
        {extracted_evidence}

        Chunk of original text from which the potential evidence is extracted:
        {chunk}

        ---

        Your task:

        - First, evaluate whether the evidence is general, misplaced, insufficient, or misclassified using the bottleneck-specific criteria above.
        - Then, reflect on those evaluations to decide:
            - Does this evidence clearly and directly support the bottleneck?
            - Is the reasoning plausible and grounded in the evidence provided within the chunk?
        - If the evidence is vague, general, or fits another bottleneck better, mark `is_valid` as False.
        - Ensure the `is_valid` field reflects your judgment based on the flags you select.
        - Your validation reasoning must explain how the intermediate evaluations informed your final decision.
        """.strip()