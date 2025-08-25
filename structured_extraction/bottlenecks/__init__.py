"""
Bottleneck module initialization
Provides easy access to all bottleneck definitions and models
"""
import importlib
from typing import Dict, Any


# List of available bottlenecks
AVAILABLE_BOTTLENECKS = ["1.1", "2.1", "3.1", "6.1"]


def load_bottleneck(bottleneck_id: str) -> Dict[str, Any]:
    """
    Dynamically load a bottleneck module by ID
    
    Args:
        bottleneck_id: ID of the bottleneck (e.g., "1.1")
        
    Returns:
        Dictionary containing all bottleneck components
    """
    # Convert ID to module name (1.1 -> bottleneck_1_1)
    module_name = f"bottleneck_{bottleneck_id.replace('.', '_')}"
    
    try:
        module = importlib.import_module(f".{module_name}", package="bottlenecks")
        
        # Extract all relevant components
        components = {
            "id": module.BOTTLENECK_ID,
            "name": module.BOTTLENECK_NAME,
            "description": module.BOTTLENECK_DESCRIPTION,
            "challenge_id": module.CHALLENGE_ID,
            "challenge_name": module.CHALLENGE_NAME,
            "challenge_description": module.CHALLENGE_DESCRIPTION,
            "role_of_public_finance": module.ROLE_OF_PUBLIC_FINANCE,
            "role_description": module.ROLE_DESCRIPTION,
            "extraction_model": getattr(module, f"Bottleneck_{bottleneck_id.replace('.', '_')}"),
            "validation_model": getattr(module, f"BottleneckValidation_{bottleneck_id.replace('.', '_')}"),
        }
        
        # Add optional components if they exist
        if hasattr(module, "BOTTLENECK_EXAMPLES"):
            components["examples"] = module.BOTTLENECK_EXAMPLES
        
        if hasattr(module, "post_validation_override"):
            components["post_validation_override"] = module.post_validation_override
        
        return components
        
    except ImportError as e:
        raise ValueError(f"Bottleneck {bottleneck_id} not found") from e