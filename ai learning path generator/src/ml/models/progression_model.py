from typing import Dict
import numpy as np
from datetime import datetime, timedelta

class ProgressionModel:
    def __init__(self):
        self.base_completion_rates = {
            'beginner': 0.8,
            'intermediate': 0.9,
            'advanced': 0.95
        }
        
    def predict_timeline(self, user_data: Dict, path_data: Dict) -> Dict:
        try:
            level = user_data.get('level', 'beginner')
            content = path_data.get('content', '')
            
            completion_rate = self.base_completion_rates.get(level, 0.8)
            total_hours = self._calculate_total_hours(content)
            
            timeline = self._generate_timeline(total_hours, completion_rate)
            
            return {
                'estimated_completion_days': timeline['total_days'],
                'weekly_milestones': timeline['weekly_progress'],
                'confidence_score': completion_rate
            }
        except Exception as e:
            print(f"Error in ProgressionModel: {str(e)}")
            return None
            
    def _calculate_total_hours(self, content: str) -> int:
        return max(len(content.split()) // 200, 5)
        
    def _generate_timeline(self, total_hours: int, completion_rate: float) -> Dict:
        hours_per_week = 10
        total_weeks = int(np.ceil(total_hours / hours_per_week))
        
        weekly_progress = []
        for week in range(total_weeks):
            progress = min((week + 1) * hours_per_week / total_hours, 1.0)
            weekly_progress.append({
                'week': week + 1,
                'expected_progress': progress * completion_rate,
                'hours_completed': min((week + 1) * hours_per_week, total_hours)
            })
            
        return {
            'total_days': total_weeks * 7,
            'weekly_progress': weekly_progress
        }