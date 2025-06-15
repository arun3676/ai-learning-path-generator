import datetime
import json
import traceback
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_cors import cross_origin

# Use a unique name for the blueprint to prevent conflicts
agents_bp = Blueprint('agents_api', __name__)

# Initialize agents as None
research_agent = None
teaching_agent = None


def init_agents():
    """Initialize the agents with error handling and detailed logging"""
    global research_agent, teaching_agent
    from src.agents import ResearchAgent, TeachingAgent # Moved import here
    
    # Log start of initialization
    current_app.logger.info("Starting agents initialization...")
    
    try:
        # Initialize Research Agent
        current_app.logger.info("Initializing Research Agent...")
        research_agent = ResearchAgent()
        current_app.logger.info("Research Agent initialized successfully")
        
        # Initialize Teaching Agent
        current_app.logger.info("Initializing Teaching Agent...")
        teaching_agent = TeachingAgent()
        current_app.logger.info("Teaching Agent initialized successfully")
        
        # Log successful initialization
        current_app.logger.info("All agents initialized successfully")
        
        # Test agent functionality
        test_agent_functionality()
        
    except Exception as e:
        error_msg = f"Error initializing agents: {str(e)}"
        current_app.logger.error(error_msg)
        current_app.logger.error(traceback.format_exc())
        print(traceback.format_exc())  # ADDED for debugging
        # Log detailed error information
        current_app.logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'args') and e.args:
            current_app.logger.error(f"Error args: {e.args}")
        
        # Initialize with None to prevent app from crashing
        research_agent = None
        teaching_agent = None
        
        # Log initialization failure
        current_app.logger.error("Agents initialization failed")

def test_agent_functionality():
    """Test agent functionality with sample queries"""
    try:
        current_app.logger.info("Testing agent functionality...")
        
        # Test research agent with a simple query
        if research_agent:
            current_app.logger.info("Testing Research Agent with sample query...")
            test_research = research_agent.execute_task({
                'type': 'research',
                'topic': 'machine learning',
                'depth': 'quick'
            })
            current_app.logger.info(f"Research Agent test result: {test_research.get('success', False)}")
        
        # Test teaching agent with a simple query
        if teaching_agent:
            current_app.logger.info("Testing Teaching Agent with sample query...")
            test_teaching = teaching_agent.execute_task({
                'type': 'create_path',
                'topic': 'Python programming',
                'expertise_level': 'beginner'
            })
            current_app.logger.info(f"Teaching Agent test result: {test_teaching.get('success', False)}")
            
    except Exception as e:
        current_app.logger.error(f"Error testing agent functionality: {str(e)}")
        current_app.logger.error(traceback.format_exc())

@agents_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get available agents"""
    try:
        return jsonify({
            'success': True,
            'agents': {
                'research_agent': {
                    'name': 'Research Agent',
                    'description': 'Expert in knowledge acquisition and trend analysis',
                    'status': 'ready' if research_agent else 'error'
                },
                'teaching_agent': {
                    'name': 'Teaching Agent',
                    'description': 'Personalized learning path creator',
                    'status': 'ready' if teaching_agent else 'error'
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_agents: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve agent information',
            'details': str(e)
        }), 500

@agents_bp.route('/agent/chat', methods=['POST', 'OPTIONS'])
@agents_bp.route('/agents/chat', methods=['POST', 'OPTIONS'])  # Add alternate route
@cross_origin()
def agent_chat():
    """Handle chat messages with agents"""
    # Log the start of the request
    current_app.logger.info("=== New Agent Chat Request ===")
    current_app.logger.info(f"Request data: {request.data}")
    
    # Immediate response to show the request was received
    def immediate_response(message, status=200, success=True, **kwargs):
        response = jsonify({
            'success': success,
            'message': message,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            **kwargs
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, status
    
    try:
        # Handle preflight request
        if request.method == 'OPTIONS':
            return immediate_response("Preflight request successful")
            
        # Get and validate request data
        current_app.logger.info("Parsing request data...")
        try:
            data = request.get_json()
            current_app.logger.info(f"Parsed JSON data: {data}")
        except Exception as e:
            current_app.logger.error(f"Error parsing JSON: {str(e)}")
            return immediate_response("Invalid JSON in request", 400, False, type='invalid_json')
            
        if not data or 'message' not in data:
            current_app.logger.error("No message in request data")
            return immediate_response("Message is required", 400, False, type='validation_error')
            
        message = data.get('message', '').strip()
        if not message:
            current_app.logger.error("Empty message received")
            return immediate_response("Message cannot be empty", 400, False, type='validation_error')
            
        # Log the received message, conversation history, and mode parameters
        current_app.logger.info(f"Processing message: '{message}'")
        # Use query_type if provided, otherwise fall back to mode for backward compatibility
        mode = data.get('query_type', data.get('mode', 'chat')).lower()
        current_app.logger.info(f"Request mode: '{mode}' (from query_type: {data.get('query_type')}, mode: {data.get('mode')})")

        conversation_history = data.get('conversation_history', [])
        current_app.logger.info(f"Conversation history length: {len(conversation_history)}")

        # Log agent availability
        current_app.logger.info(f"Research agent available: {research_agent is not None}")
        current_app.logger.info(f"Teaching agent available: {teaching_agent is not None}")

        response_data = None
        try:
            if mode == 'research' and research_agent:
                current_app.logger.info("Routing to Research Agent based on mode.")
                task = {
                    'topic': message,
                    'depth': data.get('depth', 'comprehensive'),
                    'source_preferences': data.get('source_preferences', ['academic', 'web'])
                }
                current_app.logger.info(f"Research task for conduct_research: {task}")
                research_result = research_agent.conduct_research(task)
                current_app.logger.info(f"Research agent raw result: {research_result}")

                if research_result and research_result.get('success'):
                    curiosity_trails_html = ""
                    if research_result.get('curiosity_trails') and isinstance(research_result['curiosity_trails'], list):
                        curiosity_trails_html = "<br><br><strong>Curiosity Trails:</strong><ul>"
                        for trail in research_result['curiosity_trails']:
                            curiosity_trails_html += f"<li>{trail}</li>"
                        curiosity_trails_html += "</ul>"
                    
                    response_data = {
                        'message': research_result.get('summary', 'Research completed.') + curiosity_trails_html,
                        'raw_findings': research_result.get('findings'),
                        'curiosity_trails': research_result.get('curiosity_trails', [])
                    }
                    current_app.logger.info(f"Formatted research response: {response_data['message'][:200]}...") # Log snippet
                else:
                    error_message = research_result.get('error', "Failed to conduct research due to an unknown error.") if research_result else "Research agent did not return a result."
                    response_data = {'message': error_message}
                    current_app.logger.error(f"Research failed: {error_message}")

            elif mode == 'teach' and teaching_agent:
                current_app.logger.info("Routing to Teaching Agent based on mode.")
                task = {
                    'type': 'create_path', # Consistent with test_agent_functionality
                    'topic': message,
                    'expertise_level': data.get('expertise_level', 'beginner'), # Default, consider prompting later
                    'learning_style': data.get('learning_style', 'interactive'), # Default
                    'depth': data.get('depth', 'comprehensive') # Default
                }
                current_app.logger.info(f"Teaching task for execute_task: {task}")
                path_result = teaching_agent.execute_task(task)
                current_app.logger.info(f"Teaching agent raw result: {path_result}")

                if path_result and path_result.get('success'):
                    response_data = {
                        'message': path_result.get('path_description') or path_result.get('message') or "Learning path created successfully.",
                        'learning_path_details': path_result.get('path_data') # Or however the path is structured by the agent
                    }
                    current_app.logger.info(f"Formatted teaching response: {response_data['message'][:200]}...") # Log snippet
                else:
                    error_message = path_result.get('error', "Failed to create learning path due to an unknown error.") if path_result else "Teaching agent did not return a result."
                    response_data = {'message': error_message}
                    current_app.logger.error(f"Teaching failed: {error_message}")
            
            # If no specific agent handled the query or we want to ensure a response, provide one
            if not response_data:
                # Ensure we have a response no matter what
                current_app.logger.info("Providing direct response")
                response_data = {
                    'message': f"I'd be happy to help you learn about '{message}'. This is an important topic in {mode} mode. Let me provide some key information: Deep learning involves neural networks with multiple layers that can learn representations of data. Key skills include understanding backpropagation, activation functions, and frameworks like TensorFlow and PyTorch."
                }
                
                current_app.logger.info("No specific agent handled the query, defaulting to research agent.")
                try:
                    task = {
                        'type': 'research',
                        'topic': message,
                        'context': context
                    }
                    current_app.logger.info(f"Executing fallback research task: {task}")
                    result = research_agent.execute_task(task)
                    current_app.logger.info(f"Fallback research agent result: {result}")
                except Exception as e:
                    current_app.logger.error(f"Error in fallback research: {str(e)}")
                    print(traceback.format_exc())  # Print the full traceback
                    # Return a user-friendly error response
                    return jsonify({
                        'success': False,
                        'error': f"I'm sorry, I encountered an error while researching your topic: {str(e)}",
                        'type': 'processing_error'
                    }), 500
                findings = result.get('findings', {})
                # Extract the AI-generated summary
                summary = None
                if isinstance(findings, dict):
                    # First try to get the dedicated summary field
                    summary = findings.get('summary')
                    
                    # If no summary field, build one from available fields
                    if not summary and findings.get('key_concepts'):
                        # Join key concepts into a paragraph
                        key_concepts = findings.get('key_concepts')
                        if isinstance(key_concepts, list) and key_concepts:
                            summary = "Key concepts: " + ". ".join(key_concepts)
                    
                    # Check if this is a learning path request
                    learning_path = findings.get('learning_path')
                    if learning_path and isinstance(learning_path, list) and learning_path:
                        if summary:
                            summary += "\n\nLearning Path:\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(learning_path))
                        else:
                            summary = "Learning Path:\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(learning_path))
                
                # Fallback if no useful summary could be generated
                if not summary or summary == 'undefined':
                    summary = "No clear answer found. Please try rephrasing your question."
                
                # Create a more detailed response with better formatting
                main_title = f"Here's what I found about '{message}':"
                message_parts = [main_title]
                
                # Format summary with better spacing
                if summary:
                    message_parts.append(f"\n\n{summary}\n")
                
                # Format key concepts as bullet points
                if findings.get('key_concepts') and isinstance(findings.get('key_concepts'), list):
                    key_concepts = findings.get('key_concepts')
                    if key_concepts:
                        message_parts.append("\n**Key Concepts:**")
                        message_parts.append("\n" + "\n".join(f"• {concept}" for concept in key_concepts))
                
                # Format learning path as numbered steps
                if findings.get('learning_path') and isinstance(findings.get('learning_path'), list):
                    learning_path = findings.get('learning_path')
                    if learning_path:
                        message_parts.append("\n\n**Learning Path:**")
                        message_parts.append("\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(learning_path)))
                
                # Add code examples with proper code block formatting
                if findings.get('code_examples') and isinstance(findings.get('code_examples'), list):
                    code_examples = findings.get('code_examples')
                    if code_examples:
                        message_parts.append("\n\n**Code Examples:**")
                        for i, example in enumerate(code_examples):
                            message_parts.append(f"\n```python\n{example}\n```")
                
                # Add resources as bullet points
                if findings.get('resources') and isinstance(findings.get('resources'), list):
                    resources = findings.get('resources')
                    if resources:
                        message_parts.append("\n\n**Additional Resources:**")
                        message_parts.append("\n" + "\n".join(f"• {resource}" for resource in resources))
                
                # Add career applications as bullet points
                if findings.get('career_applications') and isinstance(findings.get('career_applications'), list):
                    career_apps = findings.get('career_applications')
                    if career_apps:
                        message_parts.append("\n\n**Career Applications:**")
                        message_parts.append("\n" + "\n".join(f"• {app}" for app in career_apps))
                        
                # Add advanced topics as bullet points
                if findings.get('advanced_topics') and isinstance(findings.get('advanced_topics'), list):
                    advanced_topics = findings.get('advanced_topics')
                    if advanced_topics:
                        message_parts.append("\n\n**Advanced Topics to Explore:**")
                        message_parts.append("\n" + "\n".join(f"• {topic}" for topic in advanced_topics))
                
                # Add Curiosity Trails if available
                curiosity_trails = findings.get('curiosity_trails')
                if curiosity_trails and isinstance(curiosity_trails, list):
                    trails_text = "\n\nCuriosity Trails to Explore:\n" + "\n".join([f"- {trail}" for trail in curiosity_trails])
                    message_parts.append(trails_text)
                
                response_message = "\n".join(message_parts).strip()
                
                response = {
                    'message': response_message,
                    'type': 'research_results',
                    'data': findings,
                    'suggested_actions': [
                        'Find more details',
                        'Search for related topics',
                        'Generate a learning path'
                    ]
                }
                
            # Ensure we have a valid response object
            if not response_data:
                response_data = {
                    'message': f"Here's what I found about '{message}': This is an important topic that involves understanding multiple concepts and approaches. Would you like a more specific aspect of this topic?"
                }
            
            # Format the response for the frontend
            final_response = {
                'success': True,
                'message': response_data.get('message'),  # This is what the frontend expects
                'response': response_data,  # Keep the full response data as well
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
            
            # Log the response for debugging
            current_app.logger.info(f"Sending response with message preview: {final_response.get('message', '')[:100]}...")
            
            return jsonify(final_response)
            
        except Exception as e:
            current_app.logger.error(f"Error in agent processing: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            print(traceback.format_exc())  # ADDED for debugging
            return jsonify({
                'success': False,
                'error': 'An error occurred while processing your message',
                'type': 'processing_error',
                'details': str(e) if current_app.debug else None
            }), 500
            
        # This block is now handled in the try-except above
        # The return statement is already included in the try block
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error: {str(e)}")
        return immediate_response("Invalid JSON in request body", 400, False, type='invalid_json')
        
    except Exception as e:
        current_app.logger.error(f"Error in agent_chat: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your message',
            'type': 'server_error',
            'details': str(e) if current_app.debug else None
        }), 500

@agents_bp.route('/agents/research', methods=['POST'])
def start_research():
    """Start a research task"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required for research',
                'type': 'validation_error'
            }), 400
        
        current_app.logger.info(f"Starting research on topic: {topic}")
        
        if not research_agent:
            current_app.logger.error("Research agent not initialized")
            return jsonify({
                'success': False,
                'error': 'Research agent is not available',
                'type': 'agent_error'
            }), 500
            
        # Execute the research task
        task = {
            'type': 'research',
            'topic': topic,
            'depth': 'moderate'  # Can be 'quick', 'moderate', or 'deep'
        }
        
        current_app.logger.info(f"Executing research task: {task}")
        result = research_agent.execute_task(task)
        
        if not result.get('success'):
            current_app.logger.error(f"Research failed: {result.get('message', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': result.get('message', 'Research failed'),
                'type': 'research_error'
            }), 500
            
        current_app.logger.info("Research completed successfully")
        
        return jsonify({
            'success': True,
            'message': f"Research completed on '{topic}'",
            'findings': result.get('findings', []),
            'sources': result.get('sources', []),
            'related_topics': result.get('related_topics', [])
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in start_research: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your research request',
            'type': 'server_error',
            'details': str(e) if current_app.debug else None
        }), 500

@agents_bp.route('/agents/research/history', methods=['GET'])
def get_research_history():
    """Get research history"""
    try:
        # In a real app, this would fetch from a database
        return jsonify({
            'success': True,
            'history': [
                'Research on Python Programming',
                'Research on Machine Learning'
            ]
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_research_history: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to fetch research history',
            'details': str(e)
        }), 500

@agents_bp.route('/agents/create-path', methods=['POST'])
def create_learning_path():
    """Create a learning path"""
    try:
        data = request.get_json()
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
            
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic cannot be empty'
            }), 400
            
        expertise_level = data.get('expertise_level', 'beginner')
        learning_style = data.get('learning_style', 'interactive')
        
        # In a real app, this would use the teaching agent
        # For now, return a mock response
        return jsonify({
            'success': True,
            'path': {
                'topic': topic,
                'level': expertise_level,
                'style': learning_style,
                'steps': [
                    f'Introduction to {topic}',
                    f'Basic concepts of {topic}',
                    f'Advanced topics in {topic}'
                ]
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in create_learning_path: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to create learning path',
            'details': str(e)
        }), 500

@agents_bp.route('/agents/paths', methods=['GET'])
def get_learning_paths():
    """Get all learning paths"""
    try:
        # In a real app, this would fetch from a database
        return jsonify({
            'success': True,
            'paths': [
                'Python Programming Path (Beginner)',
                'Machine Learning Path (Intermediate)'
            ]
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_learning_paths: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to fetch learning paths',
            'details': str(e)
        }), 500
