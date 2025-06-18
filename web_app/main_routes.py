import datetime
import os
import json
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import current_user, login_required
from web_app.models import db, UserLearningPath, LearningProgress
import uuid
from werkzeug.utils import secure_filename
from pydantic import ValidationError as PydanticValidationError

from src.learning_path import LearningPath, LearningPathGenerator
from src.data.resources import ResourceManager # Assuming this is the correct path
from src.utils.config import LEARNING_STYLES, EXPERTISE_LEVELS, TIME_COMMITMENTS
from src.ml.job_market import get_job_market_stats

# Define the blueprint
bp = Blueprint('main', __name__, template_folder='../templates') # Adjusted template_folder path

# Helper to get LearningPathGenerator, initializing if not present in app context
# This is a temporary setup for CLI compatibility. Proper setup involves app factory.
def get_path_generator():
    if not hasattr(current_app, 'path_generator'):
        current_app.logger.info("Initializing LearningPathGenerator for main_routes...")
        try:
            current_app.path_generator = LearningPathGenerator()
        except Exception as e:
            current_app.logger.error(f"Failed to initialize LearningPathGenerator in main_routes: {e}")
            current_app.path_generator = None # Avoid crashing if init fails
    return current_app.path_generator

# Helper for ResourceManager
def get_resource_manager():
    if not hasattr(current_app, 'resource_manager'):
        current_app.logger.info("Initializing ResourceManager for main_routes...")
        try:
            current_app.resource_manager = ResourceManager()
        except Exception as e:
            current_app.logger.error(f"Failed to initialize ResourceManager in main_routes: {e}")
            current_app.resource_manager = None
    return current_app.resource_manager

@bp.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

@bp.route('/')
def index():
    return render_template(
        'index.html',
        learning_styles=LEARNING_STYLES,
        expertise_levels=EXPERTISE_LEVELS,
        time_commitments=TIME_COMMITMENTS
    )

@bp.route('/generate', methods=['POST'])
def generate_path():
    current_app.logger.info('Generate path route called')
    current_app.logger.info(f'Form data: {request.form}')
    
    path_generator = get_path_generator()
    if not path_generator:
        current_app.logger.error('LearningPathGenerator not available')
        return jsonify({'success': False, 'error': 'LearningPathGenerator not available'}), 500

    try:
        data = request.form
        current_app.logger.info(f'Form data retrieved: {data}')
        
        topic = data.get('topic')
        expertise = data.get('expertise_level')
        style = data.get('learning_style')
        time_commitment = data.get('time_commitment')
        ai_provider = data.get('ai_provider', 'openai')  # Default to openai if not provided
        ai_model = data.get('ai_model')  # Model can be None if provider handles default

        current_app.logger.info(
            f'Extracted form fields - topic: {topic}, expertise: {expertise}, style: {style}, '
            f'time_commitment: {time_commitment}, ai_provider: {ai_provider}, ai_model: {ai_model}'
        )

        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required.'}), 400

        # Generate the learning path - this returns a LearningPath object, not a JSON string
        learning_path = path_generator.generate_path(
            topic=topic,
            expertise_level=expertise,
            learning_style=style,
            time_commitment=time_commitment,
            ai_provider=ai_provider,
            ai_model=ai_model
        )
        
        # No need to parse JSON or validate, as generate_path already returns a validated LearningPath object
        validated_path = learning_path
        path_data = validated_path.dict()
        
        # Generate a unique ID if not present
        path_id = path_data.get('id', str(uuid.uuid4()))
        path_data['id'] = path_id
        
        # Store in session for both logged-in and anonymous users
        session['current_path'] = path_data
        
        # For logged-in users, automatically save to database
        if current_user.is_authenticated:
            # Check if this path already exists for this user
            existing_path = UserLearningPath.query.filter_by(
                user_id=current_user.id,
                id=path_id
            ).first()
            
            if existing_path:
                # Update existing path
                existing_path.path_data_json = path_data
                existing_path.title = path_data.get('title', 'Untitled Path')
                existing_path.topic = path_data.get('topic', 'General')
                db.session.commit()
                current_app.logger.info(f"Updated existing path {path_id} for user {current_user.id}")
            else:
                # Create new path
                new_path = UserLearningPath(
                    id=path_id,
                    user_id=current_user.id,
                    path_data_json=path_data,
                    title=path_data.get('title', 'Untitled Path'),
                    topic=path_data.get('topic', 'General')
                )
                db.session.add(new_path)
                db.session.commit()
                current_app.logger.info(f"Created new path {path_id} for user {current_user.id}")
                
                # Create initial progress entries for each milestone
                milestones = path_data.get('milestones', [])
                for i, _ in enumerate(milestones):
                    progress = LearningProgress(
                        user_learning_path_id=path_id,
                        milestone_identifier=str(i),
                        status='not_started'
                    )
                    db.session.add(progress)
                
                db.session.commit()
        
        return redirect(url_for('main.result')) 

    except PydanticValidationError as e:
        current_app.logger.error(f"Pydantic Validation Error: {e.errors()}")
        error_details = e.errors()
        # Simplified error message for now
        error_message = f"AI response validation failed: {error_details[0]['msg']} for field {error_details[0]['loc'][0] if error_details[0]['loc'] else 'unknown'}. Please try again or refine your topic."
        if 'current_path' in session: del session['current_path'] 
        return render_template('index.html', error=error_message, learning_styles=LEARNING_STYLES, expertise_levels=EXPERTISE_LEVELS, time_commitments=TIME_COMMITMENTS)
    except Exception as e:
        current_app.logger.error(f"Error in /generate: {str(e)}")
        # import traceback; traceback.print_exc() # For detailed server-side debugging
        error_message = f"An unexpected error occurred: {str(e)}. Please try again."
        if 'current_path' in session: del session['current_path']
        return render_template('index.html', error=error_message, learning_styles=LEARNING_STYLES, expertise_levels=EXPERTISE_LEVELS, time_commitments=TIME_COMMITMENTS)

def save_learning_path():
    """Save the current learning path to the database for logged-in users or to session for anonymous users"""
    path_data = session.get('current_path')
    if not path_data:
        flash('No learning path to save.', 'error')
        return redirect(url_for('main.index'))
    
    path_id = path_data.get('id', str(uuid.uuid4()))
    path_data['id'] = path_id  # Ensure path has an ID
    
    # For logged-in users, save to database
    if current_user.is_authenticated:
        # Check if this path already exists for this user
        existing_path = UserLearningPath.query.filter_by(
            user_id=current_user.id,
            id=path_id
        ).first()
        
        if existing_path:
            # Update existing path
            existing_path.path_data_json = path_data  # Use path_data_json field name from the model
            existing_path.title = path_data.get('title', 'Untitled Path')
            existing_path.topic = path_data.get('topic', 'General')
            existing_path.last_accessed_at = datetime.datetime.utcnow()  # Use last_accessed_at instead of updated_at
            db.session.commit()
            flash('Learning path updated successfully!', 'success')
        else:
            # Create new path
            new_path = UserLearningPath(
                id=path_id,
                user_id=current_user.id,
                path_data_json=path_data,  # Use path_data_json field name from the model
                title=path_data.get('title', 'Untitled Path'),
                topic=path_data.get('topic', 'General')
                # Note: expertise_level is not a column in the model
            )
            db.session.add(new_path)
            db.session.commit()
            
            # Create initial progress entries for each milestone
            milestones = path_data.get('milestones', [])
            for i, milestone in enumerate(milestones):
                milestone_id = str(i)  # Using index as milestone identifier
                progress = LearningProgress(
                    user_learning_path_id=path_id,
                    milestone_identifier=milestone_id,
                    status='not_started'
                )
                db.session.add(progress)
            
            db.session.commit()
            flash('Learning path saved successfully!', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    # For anonymous users, save to session
    else:
        # Store in session
        if 'saved_paths' not in session:
            session['saved_paths'] = {}
        
        session['saved_paths'][path_id] = {
            'path_data': path_data,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        # Also save to file for persistence
        save_dir = Path(current_app.root_path) / 'anonymous_saved_paths'
        save_dir.mkdir(exist_ok=True)
        
        # Use session ID or a cookie to identify anonymous users
        session_id = session.get('anonymous_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['anonymous_id'] = session_id
        
        file_name = f"{session_id}_{path_id}.json"
        file_path = save_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump({
                'path_data': path_data,
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }, f, indent=4)
        
        flash('Learning path saved. Create an account to track your progress!', 'info')
        return redirect(url_for('main.result', id=path_id))

@bp.route('/save_path', methods=['GET', 'POST'])
def save_path():
    return save_learning_path()

def load_learning_path(path_id):
    """Load a learning path from database or file"""
    # If user is logged in, try to load from database first
    if current_user.is_authenticated:
        user_path = UserLearningPath.query.filter_by(
            user_id=current_user.id,
            id=path_id
        ).first()
        
        if user_path:
            return json.loads(user_path.content)
    
    # Fall back to file system for non-logged in users or if not found in database
    file_path = os.path.join(current_app.root_path, 'static', 'paths', f"{path_id}.json")
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            learning_path = json.load(f)
        return learning_path
    else:
        return None

@bp.route('/load_paths', methods=['GET'])
def load_paths():
    # This is a placeholder. Actual loading will involve database query.
    if current_user.is_authenticated:
        user_paths = UserLearningPath.query.filter_by(user_id=current_user.id).all()
        paths = []
        for path in user_paths:
            paths.append({
                'id': path.id,
                'title': path.title,
                'topic': path.topic,
                'expertise_level': path.expertise_level,
                'created_at': path.created_at.strftime('%Y-%m-%d')
            })
        return jsonify({'success': True, 'paths': paths})
    else:
        paths = session.get('saved_paths', [])
        return jsonify({'success': True, 'paths': paths})

@bp.route('/my-paths')
def my_paths():
    """Redirect to dashboard for logged in users or show session paths for others"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        paths = session.get('saved_paths', [])
        return render_template('login.html', paths=paths)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Display the user's dashboard with saved learning paths and progress"""
    # Get all non-archived learning paths for the current user
    user_paths = UserLearningPath.query.filter_by(
        user_id=current_user.id,
        is_archived=False
    ).order_by(UserLearningPath.created_at.desc()).all()
    
    # Get archived paths
    archived_paths = UserLearningPath.query.filter_by(
        user_id=current_user.id,
        is_archived=True
    ).order_by(UserLearningPath.created_at.desc()).all()
    
    # Get progress data for each path
    paths_with_progress = []
    total_milestones = 0
    completed_milestones = 0
    
    for path in user_paths:
        # Get progress for this path
        progress_entries = LearningProgress.query.filter_by(
            user_learning_path_id=path.id
        ).all()
        
        # Calculate progress percentage
        path_total = len(progress_entries)
        path_completed = sum(1 for entry in progress_entries if entry.status == 'completed')
        
        if path_total > 0:
            progress_percentage = int((path_completed / path_total) * 100)
        else:
            progress_percentage = 0
        
        # Add to overall counts
        total_milestones += path_total
        completed_milestones += path_completed
        
        # Add path with its progress data
        paths_with_progress.append({
            'id': path.id,
            'title': path.title,
            'topic': path.topic,
            'expertise_level': path.path_data_json.get('expertise_level', 'Beginner') if path.path_data_json else 'Beginner',
            'created_at': path.created_at.strftime('%Y-%m-%d') if path.created_at else datetime.datetime.now().strftime('%Y-%m-%d'),
            'progress_percentage': progress_percentage,
            'completed': path_completed,
            'total': path_total,
            'is_archived': path.is_archived
        })
    
    # Calculate overall progress
    overall_progress = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0
    
    # Prepare archived paths data
    archived_paths_data = [{
        'id': path.id,
        'title': path.title,
        'topic': path.topic,
        'expertise_level': path.path_data_json.get('expertise_level', 'Beginner'),
        'created_at': path.created_at.strftime('%Y-%m-%d')
    } for path in archived_paths]
    
    return render_template('dashboard.html', 
                          user_paths=paths_with_progress,
                          archived_paths=archived_paths_data,
                          stats={
                              'total_paths': len(user_paths),
                              'completed_milestones': completed_milestones,
                              'total_milestones': total_milestones,
                              'overall_progress': overall_progress
                          })

@bp.route('/upload_document', methods=['POST'])
def upload_document():
    resource_manager = get_resource_manager()
    if not resource_manager:
        return jsonify({'success': False, 'error': 'ResourceManager not available'}), 500
        
    if 'document' not in request.files:
        return jsonify({'success': False, 'error': 'No document part in the request'}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Ensure UPLOAD_FOLDER is configured on current_app by create_app
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads') 
        # Create absolute path for upload_folder if it's relative
        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(current_app.root_path, upload_folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            resource_manager.add_document(file_path)
            return jsonify({'success': True, 'message': f'Document "{filename}" uploaded and processed successfully.'})
        except Exception as e:
            current_app.logger.error(f"Error processing uploaded document {filename}: {str(e)}")
            return jsonify({'success': False, 'error': f'Failed to process document: {str(e)}'}), 500
    return jsonify({'success': False, 'error': 'File upload failed for an unknown reason.'}), 500

@bp.route('/result')
def result():
    path_data = session.get('current_path')
    if not path_data:
        # Try to load from query parameter
        path_id = request.args.get('id')
        if path_id:
            path_data = load_learning_path(path_id)
            if not path_data:
                flash('Learning path not found', 'error')
                return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.index'))
            
    # Get progress data if user is logged in
    progress_data = {}
    if current_user.is_authenticated and 'path_id' in request.args:
        path_id = request.args.get('id')
        progress_entries = LearningProgress.query.filter_by(
            user_learning_path_id=path_id
        ).all()
        
        for entry in progress_entries:
            progress_data[entry.milestone_identifier] = entry.is_completed
    
    return render_template('result.html', path=path_data, progress=progress_data)

@bp.route('/api/save_path', methods=['POST'])
def api_save_path():
    path_data = session.get('current_path')
    if not path_data:
        return jsonify({'success': False, 'error': 'No path in session to save.'}), 400
    
    # This is a placeholder. Actual saving will involve database operations with UserLearningPath model.
    # For now, let's simulate saving to a file or just acknowledge.
    # from flask_login import current_user
    # if not current_user.is_authenticated:
    #     return jsonify({'success': False, 'error': 'User must be logged in to save paths.'}), 401

    # path_title = path_data.get('title', 'Untitled Path')
    # file_name = f"{current_user.id}_{secure_filename(path_title)}.json"
    # save_dir = Path(current_app.root_path) / 'user_saved_paths'
    # save_dir.mkdir(exist_ok=True)
    # file_path = save_dir / file_name
    # with open(file_path, 'w') as f:
    #     json.dump(path_data, f, indent=4)

    # current_app.logger.info(f"Path '{path_title}' saved for user {current_user.id} to {file_path}")
    current_app.logger.info(f"Path save requested (placeholder): {path_data.get('title')}")
    return jsonify({'success': True, 'message': 'Path saved successfully (placeholder).'}) 

# Routes for progress tracking and path management
@bp.route('/update_progress', methods=['POST'])
@login_required
def update_progress():
    """Update the progress of a milestone in a learning path"""
    data = request.get_json()
    
    if not data or 'path_id' not in data or 'milestone_identifier' not in data or 'is_completed' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required data'}), 400
    
    path_id = data['path_id']
    milestone_identifier = data['milestone_identifier']
    is_completed = data['is_completed']
    
    # Find the progress entry
    progress = LearningProgress.query.filter_by(
        user_learning_path_id=path_id,
        milestone_identifier=milestone_identifier
    ).first()
    
    if not progress:
        # Create a new progress entry if it doesn't exist
        progress = LearningProgress(
            user_learning_path_id=path_id,
            milestone_identifier=milestone_identifier,
            is_completed=is_completed
        )
        db.session.add(progress)
    else:
        # Update existing progress entry
        progress.is_completed = is_completed
    
    db.session.commit()
    
    # Calculate new progress percentage
    all_progress = LearningProgress.query.filter_by(
        user_learning_path_id=path_id
    ).all()
    
    total = len(all_progress)
    completed = sum(1 for p in all_progress if p.is_completed)
    progress_percentage = int((completed / total) * 100) if total > 0 else 0
    
    return jsonify({
        'status': 'success', 
        'message': 'Progress updated',
        'progress_percentage': progress_percentage,
        'completed': completed,
        'total': total
    })

@bp.route('/archive_path', methods=['POST'])
@login_required
def archive_path():
    """Archive or unarchive a learning path"""
    data = request.get_json()
    
    if not data or 'path_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing path_id'}), 400
    
    path_id = data['path_id']
    archive_action = data.get('archive', True)  # Default to archive if not specified
    
    # Find the path
    path = UserLearningPath.query.filter_by(
        user_id=current_user.id,
        id=path_id
    ).first()
    
    if not path:
        return jsonify({'status': 'error', 'message': 'Path not found'}), 404
    
    # Update archive status
    path.is_archived = archive_action
    db.session.commit()
    
    action_text = "archived" if archive_action else "unarchived"
    return jsonify({
        'status': 'success',
        'message': f'Path {action_text} successfully',
        'is_archived': archive_action
    })

@bp.route('/delete_path', methods=['POST'])
@login_required
def delete_path():
    """Permanently delete a learning path for the current user."""
    data = request.get_json() or {}
    path_id = data.get('path_id')
    if not path_id:
        return jsonify({'status': 'error', 'message': 'Missing path_id'}), 400

    # Locate path
    path = UserLearningPath.query.filter_by(user_id=current_user.id, id=path_id).first()
    if not path:
        return jsonify({'status': 'error', 'message': 'Path not found'}), 404

    # Remove from DB
    db.session.delete(path)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Path deleted'})

@bp.route('/clear_session', methods=['POST'])
def clear_session_route(): # Renamed to avoid conflict with flask.session
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared.'})


import os
from openai import OpenAI

@bp.route('/chatbot_query', methods=['POST'])
def chatbot_query():
    if current_app.config.get('DEV_MODE'):
        # Return stub data in dev mode
        learning_path = f"# {request.json.get('topic', 'Untitled Topic')} Learning Path (Stub Data)\n\n"
        learning_path += "## Week 1: Getting Started\n"
        learning_path += "- Introduction to the topic\n"
        learning_path += "- Key concepts and terminology\n"
        learning_path += f"- Why {request.json.get('topic', 'Untitled Topic')} is important\n\n"
        learning_path += "## Week 2: Core Concepts\n"
        learning_path += "- Deep dive into fundamentals\n"
        learning_path += "- Practical examples\n"
        learning_path += "- Common challenges\n"
        return jsonify({
            'topic': request.json.get('topic', 'Untitled Topic'),
            'learning_path': learning_path,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'mode': 'dev'
        })
    else:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        data = request.get_json()
        user_message = data.get('message')
        learning_path_topic = data.get('learning_path_topic', 'a general topic') # Default if not provided
        learning_path_title = data.get('learning_path_title', 'your current learning path') # Default if not provided

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        try:
            system_prompt = (
                f"You are a helpful AI career assistant. The user is currently viewing a learning path titled "
                f"'{learning_path_title}' which is about '{learning_path_topic}'. "
                f"Your goal is to answer the user's questions in the context of this learning path. "
                f"Be concise and helpful."
            )

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            ai_response = completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}") # Log to server console
            ai_response = "Sorry, I encountered an error trying to connect to the AI service. Please try again later."

        return jsonify({'reply': ai_response})


@bp.route('/direct_chat', methods=['POST'])
def direct_chat():
    if current_app.config.get('DEV_MODE'):
        # Return stub data in dev mode
        learning_path = f"# {request.json.get('topic', 'Untitled Topic')} Learning Path (Stub Data)\n\n"
        learning_path += "## Week 1: Getting Started\n"
        learning_path += "- Introduction to the topic\n"
        learning_path += "- Key concepts and terminology\n"
        learning_path += f"- Why {request.json.get('topic', 'Untitled Topic')} is important\n\n"
        learning_path += "## Week 2: Core Concepts\n"
        learning_path += "- Deep dive into fundamentals\n"
        learning_path += "- Practical examples\n"
        learning_path += "- Common challenges\n"
        return jsonify({
            'topic': request.json.get('topic', 'Untitled Topic'),
            'learning_path': learning_path,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'mode': 'dev'
        })
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    data = request.get_json()
    user_message = data.get('message')
    mode = data.get('mode', 'Chat') # Default to 'Chat' if no mode is provided

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    system_prompt = ""
    if mode == 'Chat':
        system_prompt = (
            "You are a friendly and helpful AI Learning Assistant for a website that helps users generate personalized learning paths. "
            "Your goal is to have a general conversation, answer questions about the site, or guide users on how to create learning paths. "
            "Keep your responses concise and conversational."
        )
    elif mode == 'Research':
        system_prompt = (
            "You are an AI Research Assistant. The user wants help researching a topic. "
            "Provide comprehensive information, suggest resources, or help break down complex subjects. "
            "Encourage them to use the main form on the website to generate a full learning path if they want a structured plan. "
            "Be informative and thorough."
        )
    elif mode == 'Path':
        system_prompt = (
            "You are an AI assistant specialized in discussing and conceptualizing learning paths. "
            "The user might ask about what makes a good learning path, how to approach learning a new skill, or for ideas on topics. "
            "Guide them towards using the main form on the website to generate a detailed, personalized learning path if they are ready. "
            "Be insightful and encouraging."
        )
    else:
        # Fallback for any unknown mode, though frontend should prevent this
        system_prompt = "You are a general helpful assistant."

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Error calling OpenAI API in /direct_chat: {e}")
        ai_response = "Sorry, I encountered an error trying to connect to the AI service. Please try again later."

    return jsonify({'reply': ai_response})


@bp.route('/path/<path_id>')
@login_required
def view_path(path_id):
    """View a specific learning path"""
    # Find the path
    path = UserLearningPath.query.filter_by(
        id=path_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Get the path data from JSON
    path_data = path.path_data_json
    
    # Store in session for template rendering
    session['current_path'] = path_data
    
    # Redirect to result page
    return redirect(url_for('main.result'))

@bp.route('/job_market', methods=['GET'])
def job_market():
    """Return real-time job-market snapshot using Perplexity search."""
    topic = request.args.get('topic', 'Data Scientist')
    try:
        stats = get_job_market_stats(topic)
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Job market route failed: {e}")
        # fallback static numbers
        return jsonify({
            "open_positions": "5,000+",
            "salary_range": "$120,000 - $160,000",
            "employers": ["Big Tech Co", "Innovative Startup", "Data Insights Inc"],
            "error": str(e)
        }), 500
