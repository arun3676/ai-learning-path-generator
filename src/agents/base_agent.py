"""
Base class for all autonomous learning agents
"""
from typing import List, Dict, Any, Optional
import abc
from datetime import datetime
import json

from src.utils.config import OPENAI_API_KEY
from src.ml.model_orchestrator import ModelOrchestrator
from src.data.vector_store import VectorStore

class BaseAgent(abc.ABC):
    """
    Base class for all autonomous learning agents
    Provides common functionality for all agents
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the base agent
        
        Args:
            api_key: Optional API key for language models
        """
        try:
            self.api_key = api_key or OPENAI_API_KEY
            if not self.api_key:
                print("Warning: No API key provided. Some features may not work correctly.")
                
            # Initialize model orchestrator
            self.model_orchestrator = ModelOrchestrator(api_key=self.api_key)
            
            # Initialize vector store with error handling
            self.vector_store = VectorStore(api_key=self.api_key)
            try:
                # Try to load documents from the default directory
                docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vector_db', 'documents')
                self.vector_store.load_documents(docs_dir)
            except Exception as e:
                print(f"Warning: Could not load documents: {str(e)}")
                # Fall back to minimal vector store
                self.vector_store._create_minimal_vector_store()
                
            self.memory = []
            self.goals = []
            self.current_task = None
            self.last_action = None
            
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            # Try to continue with minimal functionality
            self.api_key = api_key or OPENAI_API_KEY
            self.memory = []
            self.goals = []
            self.current_task = None
            self.last_action = None
            
            # Try to create a minimal vector store
            try:
                self.vector_store = VectorStore(api_key=self.api_key)
                self.vector_store._create_minimal_vector_store()
            except:
                print("Warning: Could not initialize vector store. Some features may not work.")
                self.vector_store = None
        
    @abc.abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task
        
        Args:
            task: Task description and parameters
            
        Returns:
            Task execution results
        """
        pass
    
    def add_to_memory(self, content: str) -> None:
        """
        Add content to agent's memory
        
        Args:
            content: Content to remember
        """
        timestamp = datetime.now().isoformat()
        memory_item = {
            "timestamp": timestamp,
            "content": content
        }
        self.memory.append(memory_item)
        
        # Keep memory size manageable
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
    
    def get_relevant_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        Get relevant memories based on a query
        
        Args:
            query: Query to find relevant memories
            
        Returns:
            List of relevant memory items
        """
        if not self.memory:
            return []
            
        try:
            # Convert memory to text format
            memory_texts = [f"{item['timestamp']}: {item['content']}" for item in self.memory]
            
            # If vector store is not available, do a simple text search
            if not hasattr(self, 'vector_store') or self.vector_store is None:
                # Simple text-based search as fallback
                query = query.lower()
                return [
                    item for item in self.memory
                    if query in item['content'].lower()
                ][:5]  # Limit to top 5 matches
                
            # Use vector store to find most relevant memories
            relevant_memories = self.vector_store.search(query, documents=memory_texts)
            
            # Convert back to memory format
            relevant_items = []
            for memory in self.memory:
                memory_text = f"{memory['timestamp']}: {memory['content']}"
                if any(memory_text in item for item in relevant_memories):
                    relevant_items.append(memory)
            
            return relevant_items
            
        except Exception as e:
            print(f"Error in get_relevant_memory: {str(e)}")
            # Fallback to simple text search
            query = query.lower()
            return [
                item for item in self.memory
                if query in item['content'].lower()
            ][:5]  # Limit to top 5 matches
    
    def plan_next_action(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the next action based on current state
        
        Args:
            current_state: Current state information
            
        Returns:
            Planned action
        """
        # Get relevant memories
        relevant_memories = self.get_relevant_memory("next action plan")
        
        # Create planning prompt
        memory_summary = "\n".join(item["content"] for item in relevant_memories)
        prompt = f"""
        You are a specialized learning agent. Plan your next action based on:
        
        Current State:
        {json.dumps(current_state, indent=2)}
        
        Relevant Past Actions:
        {memory_summary}
        
        Goals:
        {json.dumps(self.goals, indent=2)}
        
        Propose a specific, actionable next step.
        Format your response as JSON with these fields:
        - action: string (what to do)
        - parameters: object (any parameters needed)
        - reason: string (why this action)
        """
        
        # Generate plan
        plan = json.loads(self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "action": "string",
                "parameters": "object",
                "reason": "string"
            }
            """
        ))
        
        # Store the plan
        self.last_action = plan
        self.add_to_memory(f"Planned action: {json.dumps(plan)}")
        
        return plan
    
    def self_improve(self) -> None:
        """
        Analyze past performance and improve agent's capabilities
        """
        # Analyze recent actions
        recent_actions = self.memory[-10:]
        
        # Get feedback on performance
        prompt = f"""
        Analyze these recent actions and suggest improvements:
        {json.dumps(recent_actions, indent=2)}
        
        Suggest specific improvements for:
        1. Task execution efficiency
        2. Memory management
        3. Goal achievement
        4. Resource utilization
        
        Format your response as JSON with specific suggestions.
        """
        
        # Get improvement suggestions
        improvements = json.loads(self.model_orchestrator.generate_structured_response(
            prompt=prompt,
            output_schema="""
            {
                "improvements": [
                    {
                        "area": "string",
                        "suggestion": "string",
                        "implementation": "string"
                    }
                ]
            }
            """
        ))
        
        # Store improvements for future reference
        self.add_to_memory(f"Self-improvement suggestions: {json.dumps(improvements)}")
