"""
Educational resource handling for the AI Learning Path Generator.
Manages resource recommendation and categorization.
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.ml.model_orchestrator import ModelOrchestrator
from src.utils.helpers import difficulty_to_score
from src.utils.config import RESOURCE_TYPES, LEARNING_STYLES

class ResourceManager:
    """
    Manages educational resources and recommendations.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the resource manager.
        
        Args:
            api_key: Optional OpenAI API key
        """
        self.model_orchestrator = ModelOrchestrator(api_key)
        self.cached_resources = {}
    
    def recommend_resources(
        self,
        topic: str,
        learning_style: str,
        expertise_level: str,
        count: int = 5,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend educational resources for a topic.
        
        Args:
            topic: The topic to find resources for
            learning_style: Preferred learning style
            expertise_level: User's expertise level
            count: Number of resources to recommend
            resource_type: Optional specific resource type
            
        Returns:
            List of resource recommendations
        """
        # Check cache first
        cache_key = f"{topic}_{learning_style}_{expertise_level}_{resource_type}"
        if cache_key in self.cached_resources:
            resources = self.cached_resources[cache_key]
            return resources[:count]
        
        # Generate resources using the model
        resources = self.model_orchestrator.generate_resource_recommendations(
            topic=topic,
            learning_style=learning_style,
            expertise_level=expertise_level,
            count=count
        )
        
        # Filter by resource type if specified
        if resource_type and resources:
            resources = [r for r in resources if r.get("type") == resource_type]
        
        # Cache the results
        self.cached_resources[cache_key] = resources
        
        return resources
    
    def categorize_by_learning_style(
        self,
        resources: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize resources by most suitable learning style.
        
        Args:
            resources: List of resource dictionaries
            
        Returns:
            Dictionary of resources grouped by learning style
        """
        result = {style: [] for style in LEARNING_STYLES}
        
        for resource in resources:
            resource_type = resource.get("type", "article")
            
            # Find the learning style with highest score for this resource type
            best_style = "reading"  # Default
            best_score = 0
            
            if resource_type in RESOURCE_TYPES:
                for style, score in RESOURCE_TYPES[resource_type].items():
                    if score > best_score:
                        best_score = score
                        best_style = style
            
            # Add resource to the appropriate category
            result[best_style].append(resource)
        
        return result
    
    def load_curated_resources(
        self,
        file_path: str = "data/curated_resources.json"
    ) -> List[Dict[str, Any]]:
        """
        Load curated resources from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of resource dictionaries
        """
        try:
            with open(file_path, "r") as f:
                resources = json.load(f)
                return resources
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_curated_resources(
        self,
        resources: List[Dict[str, Any]],
        file_path: str = "data/curated_resources.json"
    ) -> bool:
        """
        Save curated resources to a JSON file.
        
        Args:
            resources: List of resource dictionaries
            file_path: Path to save to
            
        Returns:
            Success status
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(exist_ok=True, parents=True)
            
            with open(file_path, "w") as f:
                json.dump(resources, f, indent=2)
            return True
        except Exception:
            return False
    
    def analyze_difficulty(self, resource: Dict[str, Any]) -> float:
        """
        Analyze the difficulty level of a resource.
        
        Args:
            resource: Resource dictionary with description
            
        Returns:
            Difficulty score between 0 and 1
        """
        # Try to extract difficulty from the resource directly
        if "difficulty" in resource:
            return difficulty_to_score(resource["difficulty"])
        
        # Analyze the description
        description = resource.get("description", "")
        if description:
            return self.model_orchestrator.analyze_difficulty(description)
        
        # Default to medium difficulty
        return 0.5
    
    def filter_by_difficulty(
        self,
        resources: List[Dict[str, Any]],
        max_difficulty: float = 1.0,
        min_difficulty: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Filter resources by difficulty level.
        
        Args:
            resources: List of resource dictionaries
            max_difficulty: Maximum difficulty score (0-1)
            min_difficulty: Minimum difficulty score (0-1)
            
        Returns:
            Filtered list of resources
        """
        result = []
        
        for resource in resources:
            # Get or calculate difficulty score
            if "difficulty_score" in resource:
                score = float(resource["difficulty_score"])
            else:
                difficulty = resource.get("difficulty", "intermediate")
                score = difficulty_to_score(difficulty)
            
            # Add to result if within range
            if min_difficulty <= score <= max_difficulty:
                result.append(resource)
        
        return result
