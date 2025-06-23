"""
Model orchestrator for the AI Learning Path Generator.
Handles interactions with language models and embeddings.
"""
from typing import List, Dict, Any, Optional, Union, TypeVar, Type
import json
import os

# Ensure we're using Pydantic v1.x
import pydantic
from pydantic import BaseModel as PydanticBaseModel

# Import directly from langchain-openai instead
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI

# For type hints
T = TypeVar('T', bound='BaseModel')

class BaseModel(PydanticBaseModel):
    """Base model that uses Pydantic v1.x compatibility layer."""
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            # Add custom JSON encoders if needed
        }

    @classmethod
    def parse_obj(cls: Type[T], obj: Any) -> T:
        return super().model_validate(obj)

    def dict(self, **kwargs):
        return self.model_dump(**kwargs)

# We'll use only OpenAI for now to make the application work
# Both providers will default to using OpenAI

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains.llm import LLMChain

from src.utils.config import (
    OPENAI_API_KEY,
    DEEPSEEK_API_KEY,  # Kept for legacy compatibility
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    MAX_TOKENS,
    TEMPERATURE
)

class ModelOrchestrator:
    """
    Manages AI model interactions with RAG capabilities.
    """
    def __init__(self, api_key: Optional[str] = None, provider: Optional[str] = None):
        print("--- ModelOrchestrator.__init__ started ---")
        """
        Initialize the model orchestrator with RAG capabilities.
        
        Args:
            api_key: Optional API key (if not provided, will use from environment)
            provider: Optional provider name ('openai' or 'deepseek')
        """
        self.provider = provider.lower() if provider else DEFAULT_PROVIDER
        self.context = []
        self.goal = None
        self.planning_enabled = True
        self.memory = []
        
        # Set up API key based on selected provider
        if self.provider == 'openai':
            self.api_key = api_key or OPENAI_API_KEY
            if not self.api_key:
                raise ValueError("OpenAI API key is required. Please provide it or set the OPENAI_API_KEY environment variable.")
            
            print("--- ModelOrchestrator.__init__: Preparing to initialize ChatOpenAI ---")
            print(f"--- ModelOrchestrator.__init__: API Key: {str(self.api_key)[:15]}..., Model: {DEFAULT_MODEL}, Temp: {TEMPERATURE}, Max Tokens: {MAX_TOKENS} ---")
            # self.llm = ChatOpenAI(
            #     api_key=self.api_key,
            #     model_name=DEFAULT_MODEL,
            #     temperature=TEMPERATURE,
            #     max_tokens=MAX_TOKENS
            # )
            print("--- ModelOrchestrator.__init__: ChatOpenAI initialization SKIPPED ---")
            
            print("--- ModelOrchestrator.__init__: Preparing to initialize OpenAI (base_llm) ---")
            # self.base_llm = OpenAI(
            #     api_key=self.api_key,
            #     model_name=DEFAULT_MODEL,
            #     temperature=TEMPERATURE,
            #     max_tokens=MAX_TOKENS
            # )
            print("--- ModelOrchestrator.__init__: OpenAI (base_llm) initialization SKIPPED ---")
        elif self.provider == 'deepseek':
            self.api_key = api_key or DEEPSEEK_API_KEY
            if not self.api_key:
                raise ValueError("DeepSeek API key is required. Please provide it or set the DEEPSEEK_API_KEY environment variable.")
            print("--- ModelOrchestrator.__init__: DeepSeek provider selected, client initialization SKIPPED for now ---")
        # Only OpenAI and DeepSeek providers are supported now
        # (OpenAI is the primary and recommended provider)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'openai' or 'deepseek'.")
            
        # Track current model name
        self.model_name = DEFAULT_MODEL

        # Override default model if DeepSeek provider is selected
        if self.provider == 'deepseek':
            # Allow environment variable override but default to the official DeepSeek chat model
            self.model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            print(f"--- ModelOrchestrator.__init__: DeepSeek provider detected, using model: {self.model_name} ---")

        print("--- ModelOrchestrator.__init__: SKIPPING init_language_model call ---")
        # Initialize the language model based on provider
        # self.init_language_model()
        print("--- ModelOrchestrator.__init__ finished (LLM clients NOT initialized) ---")
    
    def init_language_model(self, model_name: Optional[str] = None, temperature: Optional[float] = None):
        print(f"--- ModelOrchestrator.init_language_model started (provider: {self.provider}, model: {model_name or self.model_name}) ---")
        """
        Initialize or switch the language model.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature setting for the model
        """
        # Update model name if provided
        if model_name:
            self.model_name = model_name
            
        temp = temperature if temperature is not None else TEMPERATURE
            
        # Initialize based on provider
        try:
            if self.provider == 'openai':
                print(f"--- ModelOrchestrator.init_language_model: Initializing ChatOpenAI for {self.provider} ---")
                # Initialize with explicit client for better compatibility
                from openai import OpenAI as OpenAIClient
                client = OpenAIClient(api_key=self.api_key)
                self.llm = ChatOpenAI(
                    client=client,
                    model=self.model_name,
                    temperature=temp,
                    max_tokens=MAX_TOKENS,
                )
                print(f"--- ModelOrchestrator.init_language_model: ChatOpenAI for {self.provider} initialized ---")
            elif self.provider == 'deepseek':
                print(f"--- ModelOrchestrator.init_language_model: Initializing ChatOpenAI for {self.provider} ---")
                # Fallback to OpenAI
                print("Using OpenAI as fallback for DeepSeek")
                from openai import OpenAI as OpenAIClient
                client = OpenAIClient(api_key=OPENAI_API_KEY)
                self.llm = ChatOpenAI(
                    client=client,
                    model=DEFAULT_MODEL,
                    temperature=temp,
                    max_tokens=MAX_TOKENS,
                )
            # OpenAI is the primary provider now
        except Exception as e:
            print(f"Error initializing language model: {str(e)}")
            raise
    
    def switch_provider(self, provider: str, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Switch between AI providers.
        
        Args:
            provider: The provider to switch to ('openai' or 'deepseek')
            api_key: Optional API key for the provider
            model_name: Optional model name to use
            
        Returns:
            str: Status message indicating the provider and model in use
        """
        try:
            self.provider = provider.lower()
            
            # Update API key if provided
            if api_key:
                self.api_key = api_key
            elif self.provider == 'openai':
                self.api_key = OPENAI_API_KEY
            elif self.provider == 'deepseek':
                self.api_key = DEEPSEEK_API_KEY
            # OpenAI is the primary provider now
            else:
                raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'deepseek'.")
                
            # Update model name if provided
            if model_name:
                self.model_name = model_name
                
            # Re-initialize the language model
            self.init_language_model()
            
            return f"Switched to {self.provider} provider with model {self.model_name}"
            
        except Exception as e:
            error_msg = f"Error switching to provider {provider}: {str(e)}"
            print(error_msg)
            # Try to fallback to a working provider
            if self.provider != 'openai':
                print("Falling back to OpenAI provider")
                return self.switch_provider('openai', OPENAI_API_KEY, model_name or DEFAULT_MODEL)
            raise ValueError(error_msg) from e
    
    def generate_response(
        self, 
        prompt: str, 
        relevant_documents: Optional[List[str]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a text response from the language model.
        
        Args:
            prompt: The prompt for the model
            relevant_documents: Optional list of relevant documents to add context
            temperature: Optional override for model temperature
            
        Returns:
            The generated response as a string
        """
        # Prepare context with relevant documents if available
        context = ""
        if relevant_documents and len(relevant_documents) > 0:
            context = "Relevant information:\n" + "\n\n".join(relevant_documents)
        
        # Create the full prompt with context
        full_prompt = f"{prompt}\n\n{context}" if context else prompt
        
        try:
            # Set up the temperature
            temp = temperature if temperature is not None else TEMPERATURE
            
            print("DEBUG: About to make OpenAI API call using direct implementation...")
            
            import time
            from src.direct_openai import generate_completion
            
            try:
                start_time = time.time()
                print(f"DEBUG: Using model: {self.model_name}")
                print(f"DEBUG: Prompt length: {len(full_prompt)} chars")
                
                # Use our direct implementation that bypasses the client library
                response_text = generate_completion(
                    prompt=full_prompt,
                    system_message="You are an expert educational AI assistant that specializes in creating personalized learning paths.",
                    model=self.model_name,
                    temperature=temp,
                    max_tokens=MAX_TOKENS,
                    timeout=120
                )
                
                print(f"DEBUG: API call completed in {time.time() - start_time:.2f} seconds")
                return response_text
                
            except Exception as e:
                print(f"DEBUG: API call failed: {str(e)}")
                raise
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            # Try to extract more detailed error information
            try:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"Error traceback:\n{error_traceback}")
                
                # Check if it's an OpenAI API error
                if hasattr(e, 'response') and hasattr(e.response, 'json'):
                    error_data = e.response.json()
                    print(f"OpenAI API Error: {error_data}")
                    error_msg += f"\nAPI Error: {error_data.get('error', {}).get('message', str(e))}"
                
            except Exception as inner_e:
                print(f"Error while processing error: {str(inner_e)}")
            
            raise ValueError(error_msg) from e
    
    def generate_structured_response(
        self,
        prompt: str,
        output_schema: str,
        relevant_documents: Optional[List[str]] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a structured response that follows a specific schema.
        
        Args:
            prompt: The prompt for the model
            output_schema: The schema instructions for the output
            relevant_documents: Optional list of relevant documents to add context
            temperature: Optional override for model temperature
            
        Returns:
            The generated response as a JSON string
        """
        # Determine if this is a learning path generation
        is_learning_path = 'LearningPath' in output_schema
        
        # Prepare the prompt with schema instructions and emphasize required fields
        required_fields_reminder = ""
        if is_learning_path:
            required_fields_reminder = """
            IMPORTANT: Your response MUST include ALL of these required fields:
            - title: String title of the learning path
            - description: Detailed description of the learning path
            - topic: Main topic of study
            - expertise_level: Starting expertise level
            - learning_style: Preferred learning style
            - time_commitment: Weekly time commitment
            - duration_weeks: Total duration in weeks (integer)
            - goals: List of learning goals and objectives
            - milestones: List of learning milestones
            - prerequisites: List of prerequisites for this path
            - total_hours: Total estimated hours (integer)
            
            For each milestone, you MUST include:
            - title: Short title for the milestone
            - description: Detailed description
            - estimated_hours: Estimated hours to complete (integer)
            - resources: List of recommended learning resources
            - skills_gained: List of skills gained after completion
            """
        
        schema_prompt = f"""
        {prompt}
        
        Your response should follow this schema format:
        {output_schema}
        
        {required_fields_reminder}
        
        Please provide a valid JSON response that strictly follows this schema.
        Do not include any explanatory text outside the JSON structure.
        """
        
        # Prepare context with relevant documents if available
        context = ""
        if relevant_documents and len(relevant_documents) > 0:
            context = "Relevant information:\n" + "\n\n".join(relevant_documents)
        
        # Create the full prompt with context
        full_prompt = f"{schema_prompt}\n\n{context}" if context else schema_prompt
        
        # Set up the temperature - lower for structured outputs
        temp = temperature if temperature is not None else 0.2
        
        # Use our direct implementation that bypasses the client library
        import time
        import requests
        import traceback
        response_text = None
        
        try:
            start_time = time.time()
            print(f"DEBUG: Generating structured response using provider: {self.provider}, model: {self.model_name}")
            print(f"DEBUG: Prompt length: {len(full_prompt)} chars")
            
            # Print the first 200 chars of the prompt for debugging
            print(f"DEBUG: Prompt preview: {full_prompt[:200]}...")
            
            # Print API key details for debugging (safely)
            if self.provider == 'openai':
                api_key = OPENAI_API_KEY
                if api_key:
                    print(f"DEBUG: Using OpenAI API key starting with: {api_key[:5]}{'*' * 10}")
                else:
                    print("DEBUG: WARNING - No OpenAI API key found!")
                    
            elif self.provider == 'deepseek':
                api_key = DEEPSEEK_API_KEY
                if api_key:
                    print(f"DEBUG: Using DeepSeek API key starting with: {api_key[:5]}{'*' * 10}")
                else:
                    print("DEBUG: WARNING - No DeepSeek API key found!")
                    
            # OpenAI is the primary provider now
            
            if self.provider == 'openai':
                from src.direct_openai import generate_completion
                print("Attempting to generate OpenAI completion...")
                response_text = generate_completion(
                    prompt=full_prompt,
                    system_message="You are an expert AI assistant that specializes in generating structured responses following specified schemas. Always include all required fields in your JSON response.",
                    model=self.model_name,
                    temperature=temp,
                    max_tokens=MAX_TOKENS,
                    timeout=300  # Increase timeout for reliability
                )
                print(f"Successfully generated completion with {len(response_text) if response_text else 0} characters")
            elif self.provider == 'deepseek':
                response_text = self._deepseek_completion(
                    full_prompt,
                    temp,
                    system_message="You are an expert AI assistant that specializes in generating structured responses following specified schemas. Always include all required fields in your JSON response."
                )
            # OpenAI is the primary provider now
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
                
            print(f"DEBUG: API call completed in {time.time() - start_time:.2f} seconds")
            if response_text:
                print(f"DEBUG: Received response with length: {len(response_text)} chars")
                print(f"DEBUG: Response preview: {response_text[:100]}...")
            else:
                print("DEBUG: WARNING - Received empty response from API")
                if is_learning_path:
                    # Return a fallback learning path
                    return self._create_fallback_learning_path()
                else:
                    # Return a fallback generic response
                    return json.dumps({
                        "summary": "Sorry, I encountered an error retrieving information.",
                        "key_concepts": ["Error occurred while processing your request"],
                        "learning_path": ["Please try again with a different query"],
                        "resources": [],
                        "code_examples": [],
                        "advanced_topics": []
                    })
                
        except Exception as e:
            print(f"DEBUG: Structured response generation failed: {str(e)}")
            print(traceback.format_exc())
            if is_learning_path:
                # Return a fallback learning path
                return self._create_fallback_learning_path()
            else:
                # Return a fallback generic response
                return json.dumps({
                    "summary": f"Sorry, I encountered an error: {str(e)}",
                    "key_concepts": ["Unable to extract structured information"],
                    "learning_path": ["Please try asking in a different way"],
                    "resources": [],
                    "code_examples": [],
                    "advanced_topics": [],
                    "career_applications": []
                })
        
        # Extract JSON from the response
        try:
            # Try to find JSON in the response (may be enclosed in ```json blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            # Validate JSON
            data = json.loads(json_str)

            # If expecting a learning path but received a list or wrong type, fallback
            if is_learning_path and not isinstance(data, dict):
                print("DEBUG: Expected learning path dict but received different type, returning fallback path.")
                return self._create_fallback_learning_path()

            # For learning paths, validate that all required fields are present
            if is_learning_path:
                required_fields = [
                    'title', 'description', 'topic', 'expertise_level', 
                    'learning_style', 'time_commitment', 'duration_weeks', 
                    'goals', 'milestones', 'prerequisites', 'total_hours'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"DEBUG: Missing required fields in learning path: {missing_fields}")
                    
                    # If any fields are missing, add them with default values
                    for field in missing_fields:
                        if field == 'title':
                            data['title'] = data.get('topic', 'Learning Path') + ' Learning Path'
                        elif field == 'description':
                            data['description'] = f"A comprehensive learning path for {data.get('topic', 'the requested topic')}."
                        elif field == 'topic':
                            data['topic'] = data.get('title', 'General Learning').replace(' Learning Path', '')
                        elif field == 'expertise_level':
                            data['expertise_level'] = 'beginner'
                        elif field == 'learning_style':
                            data['learning_style'] = 'visual'
                        elif field == 'time_commitment':
                            data['time_commitment'] = 'moderate'
                        elif field == 'duration_weeks':
                            data['duration_weeks'] = 8
                        elif field == 'goals':
                            data['goals'] = [f"Master {data.get('topic', 'the subject')}"]
                        elif field == 'milestones':
                            data['milestones'] = [{
                                'title': 'Getting Started',
                                'description': f"Introduction to {data.get('topic', 'the subject')}",
                                'estimated_hours': 10,
                                'resources': [{'name': 'Online Documentation', 'url': '', 'type': 'documentation'}],
                                'skills_gained': [f"Basic {data.get('topic', 'subject')} knowledge"]
                            }]
                        elif field == 'prerequisites':
                            data['prerequisites'] = ['None']
                        elif field == 'total_hours':
                            data['total_hours'] = 40
                            
                # Also check that each milestone has the required fields
                if 'milestones' in data and isinstance(data['milestones'], list):
                    milestone_required_fields = ['title', 'description', 'estimated_hours', 'resources', 'skills_gained']
                    for i, milestone in enumerate(data['milestones']):
                        milestone_missing_fields = [field for field in milestone_required_fields if field not in milestone]
                        
                        if milestone_missing_fields:
                            print(f"DEBUG: Missing required fields in milestone {i+1}: {milestone_missing_fields}")
                            
                            # Add missing fields with default values
                            for field in milestone_missing_fields:
                                if field == 'title':
                                    milestone['title'] = f"Milestone {i+1}"
                                elif field == 'description':
                                    milestone['description'] = f"A key learning milestone in this path."
                                elif field == 'estimated_hours':
                                    milestone['estimated_hours'] = 10
                                elif field == 'resources':
                                    milestone['resources'] = [{'name': 'Online Resource', 'url': '', 'type': 'article'}]
                                elif field == 'skills_gained':
                                    milestone['skills_gained'] = [f"Skills related to {data.get('topic', 'the subject')}"]
            
            return json.dumps(data)
        except Exception as e:
            print(f"DEBUG: Error parsing initial JSON: {str(e)}")
            
            # First cleanup attempt - remove common prefixes
            cleaned_response = response_text.strip()
            for prefix in ["+", "-", "*", "#", "Response:", "JSON:"]:
                if cleaned_response.startswith(prefix):
                    cleaned_response = cleaned_response[len(prefix):].strip()
            
            try:
                # Try to parse the cleaned response
                data = json.loads(cleaned_response)
                return json.dumps(data)
            except Exception as e2:
                print(f"DEBUG: Error parsing cleaned JSON: {str(e2)}")
                
                # Second attempt - try to find and extract JSON from markdown codeblock
                try:
                    import re
                    json_matches = re.findall(r'\{.*?\}', response_text, re.DOTALL)
                    if json_matches:
                        for potential_json in json_matches:
                            try:
                                data = json.loads(potential_json)
                                return json.dumps(data)
                            except:
                                continue
                except Exception as e3:
                    print(f"DEBUG: Error in regex extraction: {str(e3)}")
                
                # Return a fallback JSON as last resort instead of raising an exception
                print("DEBUG: Returning fallback JSON structure due to parsing failure")
                return json.dumps({
                    "summary": "Failed to parse the AI's response. The content might not be in the expected JSON format.",
                    "key_concepts": ["JSON parsing error"],
                    "learning_path": ["Please try a different query or check the AI provider's output directly if possible."],
                    "resources": [],
                    "code_examples": [],
                    "advanced_topics": [],
                    "error_details": "The AI's response could not be successfully parsed as JSON after multiple attempts."
                })
                return json.dumps({
                    "summary": f"I processed your request but encountered a formatting issue. Your question was about: {response_text[:100]}...",
                    "key_concepts": ["Unable to extract structured information"],
                    "learning_path": ["Please try asking in a different way"],
                    "resources": [],
                    "code_examples": [],
                    "advanced_topics": [],
                    "career_applications": []
                })
    
    def _deepseek_completion(self, prompt: str, temperature: float, system_message: str = None):
        """Call DeepSeek API for chat completion.
        
        The helper explicitly adds a **system** message reminding the model to comply with the
        schema and strictly return JSON. We have observed that without this guard-rail the
        DeepSeek model occasionally omits required fields which later causes Pydantic
        validation failures. Passing a clear system prompt greatly increases response
        reliability.
        """
        import requests, traceback, json, time
        
        api_key = DEEPSEEK_API_KEY
        url = "https://api.deepseek.com/v1/chat/completions"
        
        system_msg = (
            system_message
            or "You are an expert AI assistant that MUST output ONLY valid JSON strictly "
                "following the user's schema instructions. Do not add any commentary, markdown "
                "code fences or explanations."
        )
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload_base = {
            "model": self.model_name if hasattr(self, "model_name") else "deepseek-chat",
            "temperature": temperature or 0.2,
            "max_tokens": MAX_TOKENS,
        }
        
        def _post(messages):
            start = time.time()
            pl = {**payload_base, "messages": messages}
            print(
                f"DEBUG: DeepSeek request with {len(json.dumps(pl))} chars payload, "
                f"messages={len(messages)}"
            )
            resp = requests.post(url, headers=headers, json=pl, timeout=150)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            print(
                f"DEBUG: DeepSeek response in {time.time()-start:.2f}s with "
                f"{len(content)} chars"
            )
            return content
        
        try:
            # 1st attempt – full prompt
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ]
            response_text = _post(messages)
            
            # Quick JSON sanity check; if it fails we'll retry with a reduced prompt.
            try:
                json.loads(response_text.strip("`"))
                return response_text
            except Exception:
                print("DEBUG: DeepSeek response not valid JSON, retrying with simplified instructions...")
            
            # 2nd attempt – simplified prompt focusing on schema only
            simple_prompt = (
                "Provide ONLY the JSON that matches the schema. Do not wrap it in anything."\
            )
            messages_retry = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt + "\n\n" + simple_prompt},
            ]
            return _post(messages_retry)
        except Exception as e:
            print(f"DEBUG: DeepSeek API call failed: {str(e)}")
            print(traceback.format_exc())
            raise

    def _create_fallback_learning_path(self):
        """
        Create a fallback learning path with default values when generation fails.
        """
        import datetime
        import uuid
        fallback_path = {
            "id": str(uuid.uuid4()),
            "title": "General Learning Path",
            "description": "A default learning path created when specific generation failed.",
            "topic": "General Topic",
            "expertise_level": "beginner",
            "learning_style": "visual", 
            "time_commitment": "moderate",
            "duration_weeks": 8,
            "goals": ["Build foundational knowledge", "Develop practical skills"],
            "milestones": [
                {
                    "title": "Getting Started",
                    "description": "Introduction to the fundamentals.",
                    "estimated_hours": 10,
                    "resources": [
                        {"name": "Online Documentation", "url": "", "type": "documentation"}
                    ],
                    "skills_gained": ["Basic knowledge"]
                },
                {
                    "title": "Core Concepts",
                    "description": "Understanding core principles and practices.",
                    "estimated_hours": 15,
                    "resources": [
                        {"name": "Online Tutorial", "url": "", "type": "tutorial"}
                    ],
                    "skills_gained": ["Fundamental concepts"]
                }
            ],
            "prerequisites": ["None"],
            "total_hours": 25,
            "created_at": datetime.datetime.now().isoformat()
        }
        return json.dumps(fallback_path)
        
    def analyze_difficulty(self, content: str) -> float:
        """
        Analyze the difficulty level of educational content.
        
        Args:
            content: The content to analyze
            
        Returns:
            Difficulty score between 0 (easiest) and 1 (hardest)
        """
        prompt = f"""
        Analyze the following educational content and rate its difficulty level on a scale from 0 to 1,
        where 0 is very basic (elementary level) and 1 is extremely advanced (expert/PhD level).
        
        Content:
        {content[:1000]}...
        
        Consider factors like:
        - Technical vocabulary and jargon
        - Complexity of concepts
        - Prerequisites required to understand
        - Density of information
        
        Return only a numeric score between 0 and 1 with up to 2 decimal places.
        """
        
        response = self.generate_response(prompt, temperature=0.1)
        
        # Extract the numeric score
        try:
            # Look for patterns like "0.75" or "Difficulty: 0.75"
            import re
            matches = re.findall(r"([0-9]\.[0-9]{1,2})", response)
            if matches:
                score = float(matches[0])
                return max(0.0, min(1.0, score))  # Ensure between 0 and 1
            
            # If no decimal found, look for whole numbers
            matches = re.findall(r"^([0-9])$", response)
            if matches:
                score = float(matches[0])
                return max(0.0, min(1.0, score))  # Ensure between 0 and 1
                
            return 0.5  # Default to middle difficulty
        except Exception:
            return 0.5  # Default to middle difficulty
    
    def generate_resource_recommendations(
        self,
        topic: str,
        learning_style: str,
        expertise_level: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate tailored resource recommendations for a topic.
        
        Args:
            topic: The topic to find resources for
            learning_style: Preferred learning style
            expertise_level: User's expertise level
            count: Number of resources to recommend
            
        Returns:
            List of resource dictionaries
        """
        prompt = f"""
        Generate {count} learning resources for someone studying {topic}.
        
        Their learning style is {learning_style} and their expertise level is {expertise_level}.
        
        For each resource, include:
        1. Title
        2. Type (video, article, book, interactive, course, documentation, podcast, project)
        3. Description (1-2 sentences)
        4. Difficulty level (beginner, intermediate, advanced, expert)
        5. Estimated time to complete (in minutes or hours)
        6. URL (create a realistic but fictional URL if needed)
        
        Provide the response as a JSON array of resource objects.
        """
        
        response = self.generate_structured_response(
            prompt=prompt,
            output_schema="""
            [
              {
                "title": "string",
                "type": "string",
                "description": "string",
                "difficulty": "string",
                "time_estimate": "string", 
                "url": "string"
              }
            ]
            """,
            temperature=0.7
        )
        
        try:
            resources = json.loads(response)
            return resources
        except Exception:
            # Fallback to empty list on parsing error
            return []
    
    def generate_path(self, topic: str, expertise_level: str, learning_style: str, context: List[str] = None) -> str:
        """
        Generate a learning path based on user preferences and context using RAG.
        
        Args:
            topic: The learning topic
            expertise_level: User's expertise level
            learning_style: User's preferred learning style
            context: Optional context to consider
            
        Returns:
            Generated learning path
        """
        # Combine provided context with stored context
        full_context = self.context + (context or [])
        
        # Plan if planning is enabled
        if self.planning_enabled and hasattr(self, '_plan_path_generation'):
            self._plan_path_generation(topic, expertise_level, learning_style, full_context)
        
        # Generate path with context
        prompt = f"""Generate a learning path for the following topic:
        
        Topic: {topic}
        Expertise Level: {expertise_level}
        Learning Style: {learning_style}
        
        Context:
        {' '.join(full_context)}
        
        Previous answers:
        {' '.join(self.memory)}
        
        Generate a structured learning path with milestones and resources.
        """
        
        path = self._generate_text(prompt)
        
        # Store path in memory
        self.memory.append(f"Generated path for {topic} with {expertise_level} level and {learning_style} style")
        
        return path
    
    def generate_answer(self, question: str, context: Optional[List[str]] = None, temperature: Optional[float] = None) -> str:
        """
        Generate an answer to a question using RAG and agentic behavior.
        
        Args:
            question: The question to answer
            context: Optional context to consider
            temperature: Optional temperature for response generation
            
        Returns:
            Generated answer
        """
        # Combine provided context with stored context
        full_context = self.context + (context or [])
        
        # Plan if planning is enabled
        if self.planning_enabled and hasattr(self, '_plan_answer_generation'):
            self._plan_answer_generation(question, full_context)
        
        # Generate answer with context
        prompt = f"""Answer the following question based on the provided context:
        
        Context:
        {' '.join(full_context)}
        
        Question: {question}"""
        
        # Store question in memory
        self.memory.append(f"Question: {question}")
        
        # Generate and return the answer
        return self.generate_response(prompt, relevant_documents=full_context, temperature=temperature)
    
    def _plan_answer_generation(self, question: str, context: List[str]) -> None:
        """
        Plan the answer generation process.
        
        Args:
            question: The question to answer
            context: Context information
        """
        # Analyze the question to determine the best approach
        question_lower = question.lower()
        
        # Determine if we need more context
        if len(context) < 2 and not any(keyword in question_lower for keyword in ["what", "how", "why", "when", "where", "who"]):
            self.context.append("Need more context for this question")
            
        # Determine the type of question
        if "how" in question_lower:
            self.context.append("This is a procedural question")
        elif "why" in question_lower:
            self.context.append("This is an explanatory question")
        elif "what" in question_lower:
            self.context.append("This is a definitional question")
        elif "compare" in question_lower or "difference" in question_lower:
            self.context.append("This is a comparative question")
            
    def _plan_path_generation(self, topic: str, expertise_level: str, learning_style: str, context: List[str]) -> None:
        """
        Plan the learning path generation process.
        
        Args:
            topic: The learning topic
            expertise_level: User's expertise level
            learning_style: User's preferred learning style
            context: Context information
        """
        # Determine the appropriate depth and breadth based on expertise level
        if expertise_level == "beginner":
            self.context.append("Focus on fundamentals and basic concepts")
        elif expertise_level == "intermediate":
            self.context.append("Include practical applications and case studies")
        elif expertise_level == "advanced":
            self.context.append("Include advanced techniques and research papers")
            
        # Adjust for learning style
        if learning_style == "visual":
            self.context.append("Prioritize video resources and diagrams")
        elif learning_style == "auditory":
            self.context.append("Prioritize podcasts and audio lectures")
        elif learning_style == "reading":
            self.context.append("Prioritize books and articles")
        elif learning_style == "kinesthetic":
            self.context.append("Prioritize hands-on projects and exercises")
