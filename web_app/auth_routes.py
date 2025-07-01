from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from web_app import db, login_manager # Assuming db and login_manager are initialized in __init__.py
from web_app.models import User
from web_app.auth_forms import LoginForm, RegistrationForm
import json
import random
from datetime import datetime

# Define the blueprint
# If we later move this to an 'auth' subdirectory, the template_folder might change.
bp = Blueprint('auth', __name__, template_folder='templates/auth') 

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Assuming 'main.index' is your main page route
    
    form = RegistrationForm()
    
    # Handle form submission
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Add registration metadata
        user.registration_source = 'email_password'
        user.last_seen = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        
        # Personalized welcome message
        welcome_messages = [
            f"Welcome to the community, {user.username}!",
            f"Your learning journey begins now, {user.username}!",
            f"Congratulations on joining, {user.username}!",
            f"You're all set to start learning, {user.username}!"
        ]
        flash(random.choice(welcome_messages), 'success')
        
        # Auto-login after registration for seamless experience
        login_user(user)
        return redirect(url_for('main.index'))
        
    return render_template('register.html', title='Join the Community', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            # Helpful error message
            if user is None:
                flash('No account found with this email. Would you like to register?', 'warning')
                return redirect(url_for('auth.register', email=form.email.data))
            else:
                flash('Incorrect password. Please try again.', 'danger')
                return redirect(url_for('auth.login'))
        
        # Login successful
        login_user(user, remember=form.remember_me.data)
        
        # Update last seen
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Personalized welcome back message
        greeting = form.get_greeting()
        motivation = form.get_motivation()
        flash(f"{greeting} {motivation}", 'success')
        
        # Redirect handling
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'): # Basic security check
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    # Pre-fill email if coming from registration suggestion
    if request.args.get('email'):
        form.email.data = request.args.get('email')
        
    return render_template('login.html', title='Welcome Back', form=form)

@bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    
    # Friendly goodbye messages
    goodbye_messages = [
        f"See you soon, {username}!",
        f"Come back soon, {username}!",
        f"Your learning path will be waiting, {username}!",
        f"Taking a break? We'll be here when you return, {username}!"
    ]
    
    flash(random.choice(goodbye_messages), 'info')
    return redirect(url_for('main.index'))

# This is needed by Flask-Login to load a user from the session
@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

# AJAX routes for enhanced user experience

@bp.route('/check-username', methods=['POST'])
def check_username():
    """Check if a username is available and suggest alternatives if not"""
    data = request.get_json()
    username = data.get('username', '')
    
    if not username or len(username) < 3:
        return jsonify({
            'valid': False,
            'message': 'Username must be at least 3 characters long'
        })
    
    # Check if username exists
    user = User.query.filter_by(username=username).first()
    if user is not None:
        # Generate suggestions
        base = username
        suggestions = [
            f"{base}{random.randint(1, 999)}",
            f"awesome_{base}",
            f"{base}_learner"
        ]
        
        return jsonify({
            'valid': False,
            'message': 'This username is already taken',
            'suggestions': suggestions
        })
    
    return jsonify({
        'valid': True,
        'message': 'Username is available!'
    })

@bp.route('/check-password-strength', methods=['POST'])
def check_password_strength():
    """Check password strength and provide feedback"""
    data = request.get_json()
    password = data.get('password', '')
    
    # Create a form instance to use its method
    form = RegistrationForm()
    result = form.get_password_feedback(password)
    
    return jsonify(result)

@bp.route('/suggest-usernames', methods=['POST'])
def suggest_usernames():
    """Generate username suggestions based on email or name"""
    data = request.get_json()
    email = data.get('email', '')
    
    if not email or '@' not in email:
        return jsonify({
            'success': False,
            'message': 'Please provide a valid email'
        })
    
    # Create form instance to use its method
    form = RegistrationForm()
    username_base = email.split('@')[0]
    suggestions = form._generate_username_suggestions(username_base)
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })
