from typing import Dict, List, Optional
import sys
import os
from structured_pipeline.bottlenecks import load_bottleneck as load_structured_bottleneck


class BottleneckRegistry:
    """
    Central registry for all bottleneck definitions
    Loads from structured pipeline definitions for consistency
    """
    
    def __init__(self):
        self.bottlenecks = {}
        self._load_default_bottlenecks()
    
    def _load_default_bottlenecks(self):
        """Load default bottlenecks from structured pipeline"""
        default_ids = ["1.1", "2.1", "3.1", "6.1"]
        
        for bottleneck_id in default_ids:
            try:
                # Load from structured pipeline
                bottleneck_data = load_structured_bottleneck(bottleneck_id)
                
                # Convert to simpler format for agentic pipeline
                self.bottlenecks[bottleneck_id] = {
                    "id": bottleneck_id,
                    "name": bottleneck_data["name"],
                    "description": bottleneck_data["description"],
                    "challenge_name": bottleneck_data["challenge_name"],
                    "examples": bottleneck_data.get("examples", []),
                    "role": bottleneck_data["role_of_public_finance"]
                }
            except Exception as e:
                print(f"Warning: Could not load bottleneck {bottleneck_id}: {e}")
    
    def get_bottleneck(self, bottleneck_id: str) -> Optional[Dict]:
        """Get a specific bottleneck definition"""
        return self.bottlenecks.get(bottleneck_id)
    
    def get_all_bottlenecks(self) -> List[Dict]:
        """Get all bottleneck definitions"""
        return list(self.bottlenecks.values())
    
    def get_active_bottlenecks(self, active_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Get active bottlenecks based on configuration
        
        Args:
            active_ids: List of bottleneck IDs to include (None = all)
            
        Returns:
            List of active bottleneck definitions
        """
        if active_ids is None:
            return self.get_all_bottlenecks()
        
        return [self.bottlenecks[bid] for bid in active_ids if bid in self.bottlenecks]
    
    def add_bottleneck(self, bottleneck_id: str, name: str, 
                      description: str, examples: List[str] = None, **kwargs):
        """Add a custom bottleneck definition"""
        self.bottlenecks[bottleneck_id] = {
            "id": bottleneck_id,
            "name": name,
            "description": description,
            "examples": examples or [],
            **kwargs
        }
    
    def get_bottleneck_summary(self) -> str:
        """Get a summary of all registered bottlenecks"""
        summary = "Registered Bottlenecks:\n"
        for bid, bottleneck in self.bottlenecks.items():
            summary += f"\n{bid}: {bottleneck['name']}\n"
            summary += f"  Challenge: {bottleneck.get('challenge_name', 'N/A')}\n"
            summary += f"  Examples: {len(bottleneck.get('examples', []))} provided\n"
        return summary