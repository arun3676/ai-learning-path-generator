from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from web_app import db, login_manager # Assuming db and login_manager are initialized in __init__.py
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships for Feature 1: User Accounts & Progress Tracking
    # A user can have multiple learning paths they've generated or saved
    learning_paths = db.relationship('UserLearningPath', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserLearningPath(db.Model):
    __tablename__ = 'user_learning_paths'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Storing the original AI-generated path data as JSON for now
    # This can be normalized further if needed for Feature 2 (Enhanced Resource Management)
    path_data_json = db.Column(db.JSON, nullable=False) 
    title = db.Column(db.String(200), nullable=True) # Extracted from path_data for easier display
    topic = db.Column(db.String(100), nullable=True) # Extracted from path_data
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False)

    # Relationships for Feature 1: Progress Tracking
    # A learning path can have multiple progress entries (one per milestone)
    progress_entries = db.relationship('LearningProgress', backref='path', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<UserLearningPath {self.id} for User {self.user_id}>'

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_learning_path_id = db.Column(db.String(36), db.ForeignKey('user_learning_paths.id'), nullable=False)
    # Assuming milestones have a unique identifier within the path_data_json
    # For simplicity, let's say milestone_title or an index can serve as this ID for now.
    # This might need refinement based on how milestones are structured in path_data_json.
    milestone_identifier = db.Column(db.String(200), nullable=False) 
    status = db.Column(db.String(50), default='not_started')  # e.g., 'not_started', 'in_progress', 'completed'
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    # For Feature 3 (Interactive Learning - Quizzes), we might add quiz attempts here or in a separate table

    __table_args__ = (db.UniqueConstraint('user_learning_path_id', 'milestone_identifier', name='_user_path_milestone_uc'),)

    def __repr__(self):
        return f'<LearningProgress for Milestone {self.milestone_identifier} in Path {self.user_learning_path_id}>'

# Models for Feature 2: Enhanced Resource Management (Placeholders, to be detailed later)
# class CustomResource(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     # ... fields for URL, title, description, type, tags ...

# class ResourceRating(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     resource_id = db.Column(db.Integer, db.ForeignKey('some_global_resource_table_or_original_resource_id'))
#     rating = db.Column(db.Integer) # 1-5
#     review = db.Column(db.Text)

# Models for Feature 3: Interactive Learning (Placeholders, to be detailed later)
# class Quiz(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     milestone_identifier = db.Column(db.String(200)) # Links to a milestone
#     # ... fields for quiz title, description ...

# class Question(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
#     # ... fields for question text, type (MCQ, code), options, correct_answer, explanation ...

# class UserQuizAttempt(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
#     score = db.Column(db.Float)
#     # ... fields for answers given, completion_date ...
