import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.model_orchestrator import ModelOrchestrator

def display_analysis(path: Dict, user_data: Dict):
    """Display detailed analysis of the learning path"""
    print("\n" + "="*50)
    print("AI Learning Path Analysis")
    print("="*50)

    # Topic Information
    print(f"\n🎯 Topic: {user_data['topic']}")
    print(f"📊 Level: {user_data['level']}")

    # Model Information
    print("\n🤖 Model Information:")
    print(f"├── Generation Model: {path['metadata']['generation_model']}")
    print(f"└── Model Versions:")
    print(f"    ├── Difficulty: v{path['metadata']['difficulty_model_version']}")
    print(f"    └── Progression: v{path['metadata']['progression_model_version']}")

    # Difficulty Analysis
    diff = path['difficulty_analysis']
    print("\n📈 Difficulty Analysis:")
    print(f"├── Technical Complexity: {diff['technical_density']:.2f}")
    print(f"├── Content Complexity: {diff['complexity_score']:.2f}")
    print(f"├── Overall Difficulty: {diff['overall_difficulty']:.2f}")
    print(f"└── Estimated Study Hours: {diff['estimated_hours']}")

    # Progress Timeline
    prog = path['progress_timeline']
    print("\n⏱️ Progress Prediction:")
    print(f"├── Estimated Completion: {prog['estimated_completion_days']} days")
    print(f"├── Confidence Score: {prog['confidence_score']:.2f}")
    print("└── Weekly Milestones:")
    for milestone in prog['weekly_milestones']:
        print(f"    ├── Week {milestone['week']}: {milestone['expected_progress']*100:.1f}% completion")
        print(f"    └── Hours: {milestone['hours_completed']}")

    # Create visualizations
    create_difficulty_visualization(diff)
    create_progress_visualization(prog)

def create_difficulty_visualization(difficulty_data: Dict):
    """Create visualization for difficulty analysis"""
    metrics = {
        'Technical Density': difficulty_data['technical_density'],
        'Content Complexity': difficulty_data['complexity_score'],
        'Overall Difficulty': difficulty_data['overall_difficulty']
    }
    
    plt.figure(figsize=(10, 6))
    plt.bar(metrics.keys(), metrics.values(), color=['#2ecc71', '#3498db', '#e74c3c'])
    plt.title('Learning Path Difficulty Analysis')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    plt.savefig('difficulty_analysis.png')
    plt.close()

def create_progress_visualization(progress_data: Dict):
    """Create visualization for progress timeline"""
    milestones = progress_data['weekly_milestones']
    weeks = [m['week'] for m in milestones]
    progress = [m['expected_progress'] * 100 for m in milestones]
    
    plt.figure(figsize=(10, 6))
    plt.plot(weeks, progress, marker='o', linestyle='-', color='#2ecc71')
    plt.fill_between(weeks, progress, alpha=0.2, color='#2ecc71')
    plt.title('Expected Learning Progress')
    plt.xlabel('Week')
    plt.ylabel('Progress (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig('progress_timeline.png')
    plt.close()

def test_models():
    # Load environment variables
    load_dotenv()
    
    # Test data
    user_data = {
        'topic': 'Machine Learning',
        'level': 'intermediate',
        'focus_areas': [
            'deep learning',
            'neural networks',
            'model optimization'
        ],
        'learning_style': 'practical',
        'available_hours_per_week': 10
    }
    
    # Initialize orchestrator
    print("🔄 Initializing AI Learning Path Generator...")
    orchestrator = ModelOrchestrator()
    
    # Generate enhanced path
    print("⚙️ Generating personalized learning path...")
    path = orchestrator.generate_enhanced_path(user_data)
    
    if path:
        # Display detailed analysis
        display_analysis(path, user_data)
        print("\n✅ Analysis complete! Visualizations saved as:")
        print("  └── difficulty_analysis.png")
        print("  └── progress_timeline.png")
    else:
        print("❌ Error: Failed to generate learning path")

if __name__ == "__main__":
    test_models()