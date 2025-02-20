from typing import Dict, List
from src.ml.models.gpt3_model import GPT3Model
from src.ml.models.difficulty_model import DifficultyModel
from src.ml.models.progression_model import ProgressionModel

class ModelOrchestrator:
    def __init__(self):
        self.models = {
            'path_generation': GPT3Model(),
            'difficulty_assessment': DifficultyModel(),
            'progress_prediction': ProgressionModel()
        }
        
    def generate_enhanced_path(self, user_data: Dict) -> Dict:
        """Generate learning path using multiple models"""
        try:
            # Generate base path
            base_path = self.models['path_generation'].generate_path(user_data)
            
            if not base_path:
                raise Exception("Failed to generate base path")
            
            # Assess difficulty
            difficulty_scores = self.models['difficulty_assessment'].assess_path(base_path)
            
            # Predict progress
            progress_predictions = self.models['progress_prediction'].predict_timeline(
                user_data, base_path
            )
            
            # Combine results
            enhanced_path = self._combine_model_outputs(
                base_path=base_path,
                difficulty_scores=difficulty_scores,
                progress_predictions=progress_predictions
            )
            
            return enhanced_path
            
        except Exception as e:
            print(f"Error in path generation: {str(e)}")
            return None
    
    def _combine_model_outputs(
        self, 
        base_path: Dict, 
        difficulty_scores: Dict, 
        progress_predictions: Dict
    ) -> Dict:
        """Combine outputs from different models"""
        return {
            **base_path,
            'difficulty_analysis': difficulty_scores,
            'progress_timeline': progress_predictions,
            'metadata': {
                'generation_model': 'GPT-3',
                'difficulty_model_version': '1.0',
                'progression_model_version': '1.0'
            }
        }