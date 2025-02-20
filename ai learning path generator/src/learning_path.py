from typing import List, Dict
from langchain_openai import ChatOpenAI     # Changed this line
from langchain_core.prompts import PromptTemplate  # Changed this line
from src.retriever import DocumentRetriever
from datetime import datetime
import re

class LearningPathGenerator:
    def __init__(self, api_key: str):
        self.retriever = DocumentRetriever()
        self.llm = ChatOpenAI(
            temperature=0.7,
            api_key=api_key,
            model="gpt-3.5-turbo"
        )
        
    def generate_learning_path(self, topic: str, user_level: str = "beginner") -> Dict:
        """
        Generate a personalized learning path for a given topic
        """
        # First, get relevant documents about the topic
        docs = self.retriever.retrieve_relevant_docs(topic)
        context = "\n".join(docs.get('documents', [[]])[0]) if docs else ""
        
        # Create prompt for learning path generation
        prompt = PromptTemplate(
            template="""Based on the following context and user level, create a structured learning path.
            
            Context: {context}
            Topic: {topic}
            User Level: {user_level}
            
            Create a learning path that includes:
            1. Prerequisites
            2. Learning objectives
            3. Subtopics in order of progression
            4. Estimated time for each subtopic
            5. Recommended resources
            
            Format the response as a structured dictionary.""",
            input_variables=["context", "topic", "user_level"]
        )
        
        # Generate learning path
        response = self.llm.invoke(prompt.format(
            context=context,
            topic=topic,
            user_level=user_level
        ))
        
        try:
            # Parse and structure the response
            learning_path = {
                "topic": topic,
                "user_level": user_level,
                "path": response.content,
                "metadata": {
                    "generated_at": str(datetime.now()),
                    "model": "gpt-3.5-turbo"
                }
            }
            return learning_path
        except Exception as e:
            return {"error": f"Failed to generate learning path: {str(e)}"}
    
    def estimate_completion_time(self, learning_path: Dict) -> int:
        """
        Estimate total completion time in hours
        """
        try:
            # Extract time estimates from the learning path
            content = learning_path.get("path", "")
            # Use regex to find time estimates
            time_estimates = re.findall(r'(\d+)\s*hours?', content, re.IGNORECASE)
            total_hours = sum(int(hours) for hours in time_estimates)
            return total_hours
        except Exception:
            return 0
    
    def get_prerequisites(self, learning_path: Dict) -> List[str]:
        """
        Extract prerequisites from the learning path
        """
        try:
            content = learning_path.get("path", "")
            # Look for prerequisites section
            prereq_match = re.search(r'Prerequisites:(.*?)(?=\n\n|\Z)', content, re.DOTALL)
            if prereq_match:
                prereqs = prereq_match.group(1).strip().split('\n')
                return [p.strip('- ') for p in prereqs if p.strip()]
            return []
        except Exception:
            return []