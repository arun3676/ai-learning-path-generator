# src/core/learning_path.py
from ..ml.data_processor import LearningDataProcessor
from ..ml.model_orchestrator import ModelOrchestrator


from typing import List, Dict
from langchain_openai import ChatOpenAI  # Updated import
from langchain_core.prompts import PromptTemplate  # Updated import
from datetime import datetime
import json

class LearningPathGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            temperature=0.7,
            api_key=api_key,
            model="gpt-3.5-turbo"
        )
    
    def generate_structured_path(self, topic: str, user_level: str = "beginner") -> Dict:
        prompt = PromptTemplate(
            template="""Create a detailed, structured learning path in JSON format for {topic} at {user_level} level.
            
            The response must be a valid JSON object strictly following this structure:
            {{
                "topic": "{topic}",
                "level": "{user_level}",
                "prerequisites": [
                    {{
                        "skill": "prerequisite skill name",
                        "resource_link": "actual URL to learn this prerequisite",
                        "estimated_hours": 5
                    }}
                ],
                "modules": [
                    {{
                        "title": "specific module title",
                        "description": "clear module description",
                        "estimated_hours": 10,
                        "resources": [
                            {{
                                "type": "video",
                                "title": "specific resource title",
                                "link": "actual URL",
                                "duration": "2 hours"
                            }}
                        ],
                        "projects": [
                            {{
                                "title": "specific project title",
                                "description": "clear project description",
                                "difficulty": "intermediate",
                                "estimated_hours": 8
                            }}
                        ]
                    }}
                ],
                "certification_paths": [
                    {{
                        "name": "specific certification name",
                        "provider": "platform name",
                        "link": "actual URL",
                        "difficulty": "intermediate"
                    }}
                ],
                "total_estimated_hours": 40
            }}

            For {topic}, provide a detailed path including:
            1. Real online course links from Coursera, edX, or Udemy
            2. Actual YouTube tutorial links
            3. Hands-on projects with specific requirements
            4. Industry-relevant certifications
            
            Make the response strictly JSON-formatted and ensure all links are real.
            """,
            input_variables=["topic", "user_level"]
        )
        
        try:
            response = self.llm.invoke(prompt.format(
                topic=topic,
                user_level=user_level
            ))
            
            # Parse the response
            content = response.content if hasattr(response, 'content') else str(response)
            path_data = json.loads(content)
            
            # Add metadata
            path_data["metadata"] = {
                "generated_at": str(datetime.now()),
                "last_updated": str(datetime.now()),
                "version": "1.0"
            }
            
            return path_data
            
        except Exception as e:
            print(f"Error: {str(e)}")  # Add this for debugging
            return {
                "error": f"Failed to generate learning path: {str(e)}",
                "topic": topic,
                "level": user_level
            }

    def format_as_markdown(self, path_data: Dict) -> str:
        """Convert the learning path into a nicely formatted markdown document"""
        try:
            if "error" in path_data:
                return f"# Error Generating Learning Path\n{path_data['error']}"
                
            md = f"""# Learning Path: {path_data['topic']}

## Overview
- **Level:** {path_data['level']}
- **Total Estimated Time:** {path_data.get('total_estimated_hours', 0)} hours

## Prerequisites
"""
            for prereq in path_data.get('prerequisites', []):
                md += f"- {prereq['skill']}\n"
                md += f"  - Resource: [{prereq['skill']}]({prereq['resource_link']})\n"
                md += f"  - Estimated Time: {prereq['estimated_hours']} hours\n\n"

            md += "## Learning Modules\n"
            
            for i, module in enumerate(path_data.get('modules', []), 1):
                md += f"\n### Module {i}: {module['title']}\n"
                md += f"{module['description']}\n"
                md += f"**Estimated time:** {module['estimated_hours']} hours\n\n"
                
                md += "#### Learning Resources:\n"
                for resource in module.get('resources', []):
                    md += f"- [{resource['title']}]({resource['link']}) ({resource['type']})\n"
                    md += f"  - Duration: {resource['duration']}\n"
                
                if module.get('projects'):
                    md += "\n#### Projects:\n"
                    for project in module['projects']:
                        md += f"- **{project['title']}** ({project['difficulty']})\n"
                        md += f"  - {project['description']}\n"
                        md += f"  - Estimated time: {project['estimated_hours']} hours\n\n"
            
            if path_data.get('certification_paths'):
                md += "\n## Recommended Certifications\n"
                for cert in path_data['certification_paths']:
                    md += f"- [{cert['name']}]({cert['link']})\n"
                    md += f"  - Provider: {cert['provider']}\n"
                    md += f"  - Difficulty: {cert['difficulty']}\n\n"
            
            md += f"\n---\n*Generated on: {path_data['metadata']['generated_at']}*"
            
            return md
            
        except Exception as e:
            print(f"Formatting error: {str(e)}")  # Add this for debugging
            return f"# Error Formatting Learning Path\n{str(e)}"