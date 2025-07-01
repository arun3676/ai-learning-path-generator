from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from web_app.models import User # Assuming models.py is in web_app
import random
import string
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    login_method = HiddenField(default='password')
    login_time = HiddenField(default=lambda: datetime.utcnow().strftime('%H:%M'))
    submit = SubmitField('Sign In')
    
    def get_greeting(self):
        """Returns a time-appropriate greeting"""
        hour = datetime.utcnow().hour
        if hour < 12:
            return "Good morning!"
        elif hour < 18:
            return "Good afternoon!"
        else:
            return "Good evening!"
            
    def get_motivation(self):
        """Returns a random motivational message"""
        messages = [
            "Ready to continue your learning journey?",
            "Your AI learning path awaits!",
            "Welcome back, knowledge seeker!",
            "Let's build your skills today!",
            "Time to level up your expertise!"
        ]
        return random.choice(messages)

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                         validators=[DataRequired(), 
                                    Length(min=3, max=64),
                                    Regexp('^[A-Za-z0-9_.-]+$', 
                                          message='Username can only contain letters, numbers, dots, underscores and dashes')])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', 
                            validators=[DataRequired(), 
                                       EqualTo('password', message='Passwords must match.')])
    password_strength = HiddenField(default='0')
    suggested_username = HiddenField()
    submit = SubmitField('Join the Learning Community')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Generate username suggestions based on email if provided
        if 'email' in kwargs.get('data', {}) and kwargs['data']['email']:
            email = kwargs['data']['email']
            username_base = email.split('@')[0]
            self.suggested_username.data = self._generate_username_suggestions(username_base)
    
    def _generate_username_suggestions(self, base):
        """Generate creative username suggestions"""
        suggestions = []
        # Basic username from email
        suggestions.append(base)
        
        # Add a learning-related suffix
        learning_suffixes = ['learner', 'student', 'scholar', 'genius', 'explorer']
        suggestions.append(f"{base}_{random.choice(learning_suffixes)}")
        
        # Add year
        current_year = datetime.utcnow().year
        suggestions.append(f"{base}{current_year}")
        
        # Random suffix
        random_suffix = ''.join(random.choices(string.digits, k=3))
        suggestions.append(f"{base}{random_suffix}")
        
        return suggestions
        
    def get_password_feedback(self, password):
        """Returns helpful feedback about password strength"""
        strength = 0
        feedback = []
        
        if len(password) >= 12:
            strength += 2
            feedback.append("Good length!")
        elif len(password) >= 8:
            strength += 1
            
        if any(c.isupper() for c in password):
            strength += 1
            feedback.append("Has uppercase")
            
        if any(c.islower() for c in password):
            strength += 1
            
        if any(c.isdigit() for c in password):
            strength += 1
            feedback.append("Has numbers")
            
        if any(c in string.punctuation for c in password):
            strength += 1
            feedback.append("Has special characters")
            
        strength_labels = {
            0: "Very weak",
            1: "Weak",
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very strong",
            6: "Excellent!"
        }
        
        return {
            "score": strength,
            "label": strength_labels.get(strength, "Unknown"),
            "feedback": feedback
        }

    def validate_username(self, username):
        # Check if username exists
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            # Generate alternative suggestions
            base = username.data
            suggestions = []
            
            # Add random numbers
            suggestions.append(f"{base}{random.randint(1, 999)}")
            
            # Add learning-related prefix
            prefixes = ['awesome', 'brilliant', 'clever', 'eager']
            suggestions.append(f"{random.choice(prefixes)}_{base}")
            
            # Add random suffix
            suffixes = ['learner', 'mind', 'thinker', 'pro']
            suggestions.append(f"{base}_{random.choice(suffixes)}")
            
            # Format suggestions as a string
            suggestion_text = ", ".join(suggestions)
            raise ValidationError(f'This username is already taken. How about: {suggestion_text}?')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is already registered. Did you mean to log in instead?')
        
        # Email domain validation with friendly messages
        domain = email.data.split('@')[-1].lower()
        disposable_domains = ['mailinator.com', 'tempmail.com', 'fakeinbox.com', 'guerrillamail.com']
        
        if domain in disposable_domains:
            raise ValidationError('Please use your regular email instead of a temporary one. We promise not to spam you!')
            
        # Generate username suggestions based on email
        username_base = email.data.split('@')[0]
        self.suggested_username.data = self._generate_username_suggestions(username_base)
