import os
from dotenv import load_dotenv
from src.agents.research_agent import ResearchAgent

def test_research_agent():
    # Load environment variables
    load_dotenv()
    
    # Initialize the research agent
    print("Initializing Research Agent...")
    agent = ResearchAgent()
    
    # Test a simple research task
    print("\nTesting research task...")
    task = {
        "type": "research",
        "topic": "Artificial Intelligence in Healthcare",
        "depth": "moderate"
    }
    
    try:
        result = agent.execute_task(task)
        print("\nResearch Results:")
        print("Success:", result.get('success', False))
        print("Message:", result.get('message', 'No message'))
        
        if 'findings' in result:
            print("\nFindings:")
            for key, value in result['findings'].items():
                print(f"\n{key.replace('_', ' ').title()}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"- {item}")
                else:
                    print(value)
        
        if 'sources' in result and result['sources']:
            print("\nSources:")
            for source in result['sources']:
                print(f"- {source}")
    
    except Exception as e:
        print("\nError during research:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nPlease check your API key and internet connection.")

if __name__ == "__main__":
    test_research_agent()
