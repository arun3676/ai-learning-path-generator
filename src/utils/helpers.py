"""
Helper functions for the AI Learning Path Generator.
"""
import re
import json
import datetime
from typing import List, Dict, Any, Optional

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent any security issues.
    
    Args:
        text: The input text to sanitize
        
    Returns:
        Sanitized text string
    """
    # Remove any HTML or script tags
    text = re.sub(r'<[^>]*>', '', text)
    # Limit length
    return text.strip()[:1000]

def format_duration(minutes: int) -> str:
    """
    Format a duration in minutes to a human-readable string.
    
    Args:
        minutes: Number of minutes
        
    Returns:
        Formatted string (e.g., "2 hours 30 minutes")
    """
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours} hour{'s' if hours > 1 else ''} {mins} minute{'s' if mins > 1 else ''}"
    elif hours:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        return f"{mins} minute{'s' if mins > 1 else ''}"

def calculate_study_schedule(
    weeks: int, 
    hours_per_week: int, 
    topic_weights: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate a recommended study schedule based on topic weights.
    
    Args:
        weeks: Total duration in weeks
        hours_per_week: Hours available per week
        topic_weights: Dictionary of topics with their importance weights
        
    Returns:
        Dictionary with schedule information
    """
    total_hours = weeks * hours_per_week
    total_weight = sum(topic_weights.values())
    
    # Normalize weights to sum to 1
    normalized_weights = {
        topic: weight / total_weight for topic, weight in topic_weights.items()
    }
    
    # Calculate hours per topic
    hours_per_topic = {
        topic: round(weight * total_hours) for topic, weight in normalized_weights.items()
    }
    
    # Ensure minimum hours and adjust to match total
    min_hours = 1
    for topic in hours_per_topic:
        if hours_per_topic[topic] < min_hours:
            hours_per_topic[topic] = min_hours
    
    # Create schedule with start/end dates
    start_date = datetime.datetime.now()
    current_date = start_date
    
    schedule = {
        "total_hours": total_hours,
        "hours_per_week": hours_per_week,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + datetime.timedelta(weeks=weeks)).strftime("%Y-%m-%d"),
        "topics": {}
    }
    
    for topic, hours in hours_per_topic.items():
        topic_days = hours / (hours_per_week / 7)  # Distribute across available days
        topic_end = current_date + datetime.timedelta(days=topic_days)
        
        schedule["topics"][topic] = {
            "hours": hours,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": topic_end.strftime("%Y-%m-%d"),
            "percentage": round(hours / total_hours * 100, 1)
        }
        
        current_date = topic_end
    
    return schedule

def difficulty_to_score(difficulty: str) -> float:
    """
    Convert difficulty description to numeric score (0-1).
    
    Args:
        difficulty: String description of difficulty
        
    Returns:
        Numeric score between 0 and 1
    """
    difficulty = difficulty.lower()
    if "beginner" in difficulty or "easy" in difficulty:
        return 0.25
    elif "intermediate" in difficulty:
        return 0.5
    elif "advanced" in difficulty:
        return 0.75
    elif "expert" in difficulty:
        return 1.0
    else:
        return 0.5  # Default to intermediate

def match_resources_to_learning_style(
    resources: List[Any], 
    learning_style: str,
    resource_type_weights: Optional[Dict[str, Dict[str, int]]] = None
) -> List[Any]:
    """
    Sort resources based on learning style preference.
    
    Args:
        resources: List of resources (either dictionaries or Pydantic models)
        learning_style: User's learning style
        resource_type_weights: Optional custom weights for resource types
        
    Returns:
        Sorted list of resources
    """
    from src.utils.config import RESOURCE_TYPES
    
    weights = resource_type_weights or RESOURCE_TYPES
    
    # Create a copy of resources to avoid modifying the original objects
    resources_with_scores = []
    
    for resource in resources:
        # Handle both dictionary and Pydantic model (ResourceItem) objects
        if hasattr(resource, 'dict'):
            # It's a Pydantic model
            resource_dict = resource.dict()
            resource_type = resource.type if hasattr(resource, 'type') else 'article'
        else:
            # It's a dictionary
            resource_dict = resource
            resource_type = resource.get("type", "article")
        
        # Calculate style score
        style_score = 1  # Default score
        if resource_type in weights and learning_style in weights[resource_type]:
            style_score = weights[resource_type][learning_style]
        
        # Store the original resource and its score
        resources_with_scores.append((resource, style_score))
    
    # Sort by style score (higher is better)
    sorted_resources = [r[0] for r in sorted(resources_with_scores, key=lambda x: x[1], reverse=True)]
    return sorted_resources
