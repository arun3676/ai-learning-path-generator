from typing import Dict, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class DifficultyModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.technical_terms = {
            'basic': [
                'algorithm', 'dataset', 'model', 'training',
                'testing', 'validation', 'accuracy'
            ],
            'intermediate': [
                'gradient descent', 'backpropagation', 'neural network',
                'cross-validation', 'regularization', 'hyperparameter'
            ],
            'advanced': [
                'transformer', 'attention mechanism', 'convolution',
                'lstm', 'bert', 'reinforcement learning'
            ]
        }

    def assess_path(self, path_data: Dict) -> Dict:
        try:
            content = path_data.get('content', '')
            
            term_frequency = self._analyze_technical_terms(content)
            complexity = self._calculate_complexity(content)
            
            return {
                'technical_density': self._calculate_technical_score(term_frequency),
                'complexity_score': complexity,
                'estimated_hours': self._estimate_study_time(content),
                'overall_difficulty': self._calculate_overall_difficulty(term_frequency, complexity)
            }
        except Exception as e:
            print(f"Error in difficulty assessment: {str(e)}")
            return None

    def _analyze_technical_terms(self, content: str) -> Dict[str, float]:
        content_lower = content.lower()
        return {
            level: sum(term in content_lower for term in terms) / len(terms)
            for level, terms in self.technical_terms.items()
        }

    def _calculate_complexity(self, content: str) -> float:
        return min(len(content.split()) / 1000, 1.0)

    def _estimate_study_time(self, content: str) -> int:
        return max(len(content.split()) // 200, 5)

    def _calculate_technical_score(self, term_frequency: Dict[str, float]) -> float:
        weights = {'basic': 0.3, 'intermediate': 0.5, 'advanced': 0.7}
        return sum(freq * weights[level] for level, freq in term_frequency.items())

    def _calculate_overall_difficulty(self, term_frequency: Dict[str, float], complexity: float) -> float:
        technical_score = self._calculate_technical_score(term_frequency)
        return (technical_score + complexity) / 2