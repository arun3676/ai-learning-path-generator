from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class GPT3Model:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
    def generate_path(self, user_data: Dict) -> Dict:
        """Generate learning path using GPT-3"""
        prompt = PromptTemplate(
            template="""Create a detailed learning path for {topic} at {level} level.
            Include:
            1. Prerequisites
            2. Core concepts
            3. Practical projects
            4. Advanced topics
            
            Format as a structured JSON with difficulty ratings.""",
            input_variables=["topic", "level"]
        )
        
        try:
            response = self.model.invoke(prompt.format(
                topic=user_data.get('topic'),
                level=user_data.get('level')
            ))
            
            return {
                'content': response.content,
                'model_info': {
                    'model': 'gpt-3.5-turbo',
                    'type': 'path_generation'
                }
            }
        except Exception as e:
            print(f"Error in GPT3Model: {str(e)}")
            return None