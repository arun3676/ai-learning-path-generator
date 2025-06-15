"""
AI agent implementation for the Learning Path Generator.
Handles complex interactions and orchestrates the learning path generation process.
"""
print("--- src/agent.py execution started ---")
from typing import Dict, List, Any, Optional, Tuple
import json
import datetime
from pathlib import Path
print("--- src/agent.py initial imports done ---")
from src.learning_path import LearningPathGenerator, LearningPath
print("--- src/agent.py learning_path imported ---")
from src.ml.model_orchestrator import ModelOrchestrator
from src.data.vector_store import VectorStore
from src.data.document_store import DocumentStore
from src.utils.config import (
    LEARNING_STYLES,
    EXPERTISE_LEVELS,
    TIME_COMMITMENTS,
)
class LearningAgent:
    """
    AI agent that orchestrates the learning path generation process.
    """
    def __init__(self, api_key: Optional[str] = None):
        print("--- LearningAgent.__init__ started ---")
        """
        Initialize the learning agent with RAG capabilities.
        
        Args:
            api_key: Optional OpenAI API key
        """
        self.api_key = api_key
        self.path_generator = LearningPathGenerator(api_key)
        self.model_orchestrator = ModelOrchestrator(api_key)
        self.document_store = DocumentStore()
        self.vector_store = VectorStore(api_key)
        print("--- LearningAgent.__init__: All components initialized ---")
        
        # Track agent state
        self.current_path = None
        self.user_profile = {}
        self.session_history = []
        self.context = []
        self.goal = None
        self.planning_enabled = True
        
        # Load initial documents for RAG
        print("--- LearningAgent.__init__: Calling _load_initial_knowledge ---")
        self._load_initial_knowledge()
        print("--- LearningAgent.__init__ finished ---")

    def _load_initial_knowledge(self):
        print("--- LearningAgent._load_initial_knowledge started ---")
        """
        Load initial knowledge documents into the vector store.
        """
        # Create vector store directory if it doesn't exist
        vector_db_path = Path("vector_db")
        documents_dir = vector_db_path / "documents"
        
        if not vector_db_path.exists():
            vector_db_path.mkdir(parents=True)
            print(f"Created vector store directory at {vector_db_path}")
        
        if not documents_dir.exists():
            documents_dir.mkdir()
            print(f"Created documents directory at {documents_dir}")
        
        # Load documents if they exist
        if documents_dir.exists():
            try:
                print(f"Loading documents from {documents_dir}...")
                self.vector_store.load_documents(str(documents_dir))
                print(f"Documents loaded successfully from {documents_dir}.")
            except Exception as e:
                print(f"Warning: Failed to load documents: {str(e)}")
        else:
            print(f"Warning: Documents directory not found at {documents_dir}")
            
        # Initialize vector store if it doesn't exist
        if not (vector_db_path / "index.faiss").exists():
            try:
                # Create a dummy document to initialize the vector store
                with open(documents_dir / "dummy.txt", "w") as f:
                    f.write("This is a dummy document to initialize the vector store.")
                self.vector_store.load_documents(str(documents_dir))
                print("Vector store initialized successfully")
            except Exception as e:
                print(f"Warning: Failed to initialize vector store: {str(e)}")
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request and generate an appropriate response with RAG and agentic behavior.
        
        Args:
            request: Dictionary containing user request data
            
        Returns:
            Response dictionary with generated content
        """
        # Get the AI provider from the request (if specified)
        ai_provider = request.get("ai_provider")
        
        # Create provider-specific instances if provider is specified
        if ai_provider:
            provider_orchestrator = ModelOrchestrator(self.api_key, provider=ai_provider)
            provider_path_generator = LearningPathGenerator(self.api_key)
            provider_path_generator.model_orchestrator = provider_orchestrator
            
            use_orchestrator = provider_orchestrator
            use_path_generator = provider_path_generator
        else:
            use_orchestrator = self.model_orchestrator
            use_path_generator = self.path_generator
        
        # Get relevant context using RAG
        query = request.get("query", "")
        if query:
            relevant_docs = self.vector_store.search(query)
            context = [doc["content"] for doc in relevant_docs]
            self.context.extend(context)
            
            # Update user profile with preferences from context
            self._update_user_profile(context)
        
        # Plan if planning is enabled
        if self.planning_enabled:
            self._plan_next_steps(request)
        
        # Process the request based on its type
        request_type = request.get("type", "generate_path")
        
        # Add context to the request
        request["context"] = self.context
        
        if request_type == "generate_path":
            return self._handle_path_generation(request, use_path_generator)
        elif request_type == "modify_path":
            return self._handle_path_modification(request, use_path_generator)
        elif request_type == "ask_question":
            return self._handle_question(request, use_orchestrator)
        elif request_type == "get_resources":
            return self._handle_resource_request(request, use_orchestrator)
        else:
            return {
                "success": False,
                "message": f"Unknown request type: {request_type}",
                "data": None
            }
    
    def _handle_path_generation(self, request: Dict[str, Any], path_generator=None) -> Dict[str, Any]:
        """
        Handle a request to generate a new learning path with RAG and agentic behavior.
        
        Args:
            request: Dictionary with path generation parameters
            path_generator: Optional custom path generator
            
        Returns:
            Response with the generated path or error
        """
        try:
            # Extract request parameters
            topic = request.get("topic")
            expertise_level = request.get("expertise_level", "beginner")
            learning_style = request.get("learning_style", "visual")
            time_commitment = request.get("time_commitment", "moderate")
            goals = request.get("goals", [])
            additional_info = request.get("additional_info")
            
            # Validate required parameters
            if not topic:
                return {
                    "success": False,
                    "message": "Topic is required",
                    "data": None
                }
            
            # Use the provided path generator or fall back to the default
            current_generator = path_generator or self.path_generator
            
            # Get relevant context using RAG
            relevant_docs = self.vector_store.search(topic)
            context = [doc["content"] for doc in relevant_docs] if relevant_docs else []
            
            # Add any context from the request
            if request.get("context"):
                context.extend(request.get("context"))
            
            # Generate the learning path with context
            learning_path = current_generator.generate_path(
                topic=topic,
                expertise_level=expertise_level,
                learning_style=learning_style,
                time_commitment=time_commitment,
                goals=goals,
                additional_info=additional_info,
                context=context
            )
            
            # Save the generated path
            if request.get("save_path", True):
                path_file = current_generator.save_path(learning_path)
            
            # Update agent state
            self.current_path = learning_path
            self.user_profile.update({
                "last_topic": topic,
                "expertise_level": expertise_level,
                "learning_style": learning_style,
                "time_commitment": time_commitment
            })
            
            # Log the interaction
            self._log_interaction("generate_path", request, {"path_id": learning_path.id})
            
            return {
                "success": True,
                "message": f"Successfully generated learning path for {topic}",
                "data": learning_path.dict()
            }
            
        except ValueError as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating learning path: {str(e)}",
                "data": None
            }
    
    def _handle_path_modification(self, request: Dict[str, Any], path_generator=None) -> Dict[str, Any]:
        """
        Handle a request to modify an existing learning path.
        
        Args:
            request: Dictionary with modification parameters
            
        Returns:
            Response with the modified path or error
        """
        try:
            # Extract request parameters
            path_id = request.get("path_id")
            modifications = request.get("modifications", {})
            
            # Validate required parameters
            if not path_id:
                return {
                    "success": False,
                    "message": "Path ID is required",
                    "data": None
                }
            
            if not modifications:
                return {
                    "success": False,
                    "message": "No modifications specified",
                    "data": None
                }
            
            # Use the provided path generator or fall back to the default
            current_generator = path_generator or self.path_generator
            
            # Load the existing path
            learning_path = current_generator.load_path(path_id)
            if not learning_path:
                return {
                    "success": False,
                    "message": f"Learning path with ID {path_id} not found",
                    "data": None
                }
            
            # Apply modifications
            path_data = learning_path.dict()
            for key, value in modifications.items():
                if key in path_data and key not in ["id", "created_at"]:
                    path_data[key] = value
            
            # Create a new path with the modifications
            modified_path = LearningPath(**path_data)
            
            # Save the modified path
            if request.get("save_path", True):
                path_file = current_generator.save_path(modified_path)
            
            # Update agent state
            self.current_path = modified_path
            
            # Log the interaction
            self._log_interaction("modify_path", request, {"path_id": modified_path.id})
            
            return {
                "success": True,
                "message": f"Successfully modified learning path {path_id}",
                "data": modified_path.dict()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error modifying learning path: {str(e)}",
                "data": None
            }
    
    def _handle_question(self, request: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """
        Handle a question with RAG and agentic behavior.
        
        Args:
            request: Dictionary containing question data
            orchestrator: Optional custom model orchestrator
            
        Returns:
            Response with the answer or error
        """
        try:
            # Extract request parameters
            question = request.get("question")
            
            # Handle context properly (could be a list or dict)
            context = request.get("context", [])
            path_id = None
            
            # If context is a dictionary, extract path_id
            if isinstance(context, dict):
                path_id = context.get("path_id")
            # If it's a list or other type, just use it as context data
            
            # Validate required parameters
            if not question:
                return {
                    "success": False,
                    "message": "Question is required",
                    "data": None
                }
            
            # Prepare context for the model
            context_data = []
            
            # Add learning path context if available
            if path_id:
                learning_path = self.path_generator.load_path(path_id)
                if learning_path:
                    context_data.append(f"Learning Path: {learning_path.title}")
                    context_data.append(f"Description: {learning_path.description}")
                    context_data.append(f"Topic: {learning_path.topic}")
                    context_data.append(f"Expertise Level: {learning_path.expertise_level}")
                    
                    # Add milestone information
                    for i, milestone in enumerate(learning_path.milestones):
                        context_data.append(f"Milestone {i+1}: {milestone.title}")
                        context_data.append(f"  Description: {milestone.description}")
            
            # Search for relevant documents
            topic = None
            if isinstance(context, dict):
                topic = context.get("topic")
            elif 'learning_path' in locals() and learning_path:
                topic = learning_path.topic
            if topic:
                docs = self.document_store.search_documents(
                    query=question,
                    filters={"topic": topic} if topic else None,
                    top_k=3
                )
                for doc in docs:
                    context_data.append(doc.page_content)
            
            # Get relevant context using RAG
            try:
                relevant_docs = self.vector_store.search(question)
                if relevant_docs:
                    for doc in relevant_docs:
                        context_data.append(doc["content"])
            except Exception as e:
                print(f"Warning: Error searching vector store: {str(e)}")
            
            # Use the provided model orchestrator or fall back to the default
            current_orchestrator = orchestrator or self.model_orchestrator
            
            # Generate the answer with RAG context
            answer = current_orchestrator.generate_answer(
                question=question,
                context=context_data if context_data else None
            )
            
            # Log the interaction
            self._log_interaction("ask_question", request, {"answer_length": len(answer)})
            
            return {
                "success": True,
                "message": "Successfully answered question",
                "data": {
                    "question": question,
                    "answer": answer
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error answering question: {str(e)}",
                "data": None
            }
    
    def _plan_next_steps(self, request: Dict[str, Any]) -> None:
        """
        Plan the next steps based on the current request and agent state.
        
        Args:
            request: The current request being processed
        """
        request_type = request.get("type", "generate_path")
        topic = request.get("topic", "")
        
        # Set a goal if none exists
        if not self.goal:
            if request_type == "generate_path":
                self.goal = f"Create a comprehensive learning path for {topic}"
            elif request_type == "modify_path":
                self.goal = "Refine the learning path based on user feedback"
            elif request_type == "ask_question":
                self.goal = f"Answer the user's question about {topic}"
            else:
                self.goal = "Assist the user with their learning journey"
        
        # Update context with relevant information
        if topic and topic not in self.context:
            self.context.append(f"Current topic: {topic}")
            
        # Track user preferences
        expertise_level = request.get("expertise_level")
        if expertise_level:
            self.context.append(f"User expertise level: {expertise_level}")
            
        learning_style = request.get("learning_style")
        if learning_style:
            self.context.append(f"User learning style: {learning_style}")
    
    def _update_user_profile(self, context: List[str]) -> None:
        """
        Update the user profile based on context.
        
        Args:
            context: List of context strings
        """
        # Extract preferences from context
        for item in context:
            if "expertise level" in item.lower():
                parts = item.split(":", 1)
                if len(parts) > 1:
                    self.user_profile["expertise_level"] = parts[1].strip()
            elif "learning style" in item.lower():
                parts = item.split(":", 1)
                if len(parts) > 1:
                    self.user_profile["learning_style"] = parts[1].strip()
            elif "topic" in item.lower():
                parts = item.split(":", 1)
                if len(parts) > 1:
                    self.user_profile["interests"] = self.user_profile.get("interests", []) + [parts[1].strip()]
    
    def _handle_resource_request(self, request: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """
        Handle a request for learning resources.
        
        Args:
            request: Dictionary with resource request parameters
            
        Returns:
            Response with resources or error
        """
        try:
            # Extract request parameters
            topic = request.get("topic")
            learning_style = request.get("learning_style", "visual")
            expertise_level = request.get("expertise_level", "beginner")
            count = int(request.get("count", 5))
            
            # Validate required parameters
            if not topic:
                return {
                    "success": False,
                    "message": "Topic is required",
                    "data": None
                }
            
            # Use the provided model orchestrator or fall back to the default
            current_orchestrator = model_orchestrator or self.model_orchestrator
            
            # Generate recommendations using the model orchestrator
            resources = current_orchestrator.generate_resource_recommendations(
                topic=topic,
                learning_style=learning_style,
                expertise_level=expertise_level,
                count=count
            )
            
            # Log the interaction
            self._log_interaction("get_resources", request, {"resource_count": len(resources)})
            
            return {
                "success": True,
                "message": f"Successfully found {len(resources)} resources for {topic}",
                "data": {
                    "topic": topic,
                    "resources": resources
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error finding resources: {str(e)}",
                "data": None
            }
    
    def _log_interaction(
        self, 
        interaction_type: str, 
        request: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """
        Log an interaction with the agent.
        
        Args:
            interaction_type: Type of interaction
            request: The request data
            result: The result data
        """
        # Create an interaction log
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": interaction_type,
            "request": request,
            "result": result
        }
        
        # Add to session history
        self.session_history.append(log_entry)
        
        # Limit history size
        if len(self.session_history) > 100:
            self.session_history = self.session_history[-100:]
    
    def get_learning_styles(self) -> Dict[str, str]:
        """
        Get available learning styles.
        
        Returns:
            Dictionary of learning styles and descriptions
        """
        return LEARNING_STYLES
    
    def get_expertise_levels(self) -> Dict[str, str]:
        """
        Get available expertise levels.
        
        Returns:
            Dictionary of expertise levels and descriptions
        """
        return EXPERTISE_LEVELS
    
    def get_time_commitments(self) -> Dict[str, str]:
        """
        Get available time commitment options.
        
        Returns:
            Dictionary of time commitment options and descriptions
        """
        return TIME_COMMITMENTS
