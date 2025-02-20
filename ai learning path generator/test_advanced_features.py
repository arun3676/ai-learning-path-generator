# test_advanced_features.py

from src.advanced.multimodal_generator import AdvancedLearningPathGenerator
from src.advanced.skill_assessment import SkillAssessmentSystem
import os
from dotenv import load_dotenv

def test_advanced_path_generation():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Initialize advanced generator
    generator = AdvancedLearningPathGenerator(api_key)
    
    # Test topics
    test_topics = [
        ("Python Programming", "beginner"),
        ("Machine Learning", "intermediate")
    ]
    
    # Generate comprehensive paths
    for topic, level in test_topics:
        print(f"\nGenerating comprehensive path for {topic} ({level} level)...")
        path = generator.generate_comprehensive_path(topic, level)
        print("Generated path:", path)

def test_skill_assessment():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Initialize assessment system
    assessment_system = SkillAssessmentSystem(api_key)
    
    # Test assessment
    topic = "Python Programming"
    mock_responses = {
        "q1": "correct",
        "q2": "incorrect",
        "q3": "correct"
    }
    
    print(f"\nAssessing skills for {topic}...")
    assessment = assessment_system.assess_user_level(topic, mock_responses)
    print("Assessment results:", assessment)

if __name__ == "__main__":
    test_advanced_path_generation()
    test_skill_assessment()