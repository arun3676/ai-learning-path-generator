import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Load .env file only if not on Render
if not os.environ.get('RENDER'):
    load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess-this-is-not-secure'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ensure cookies work with OAuth redirects in production
    if os.environ.get('RENDER'):
        SESSION_COOKIE_SECURE = True       # Cookie only over HTTPS
        SESSION_COOKIE_SAMESITE = 'None'   # Allow cross-site OAuth redirect
        REMEMBER_COOKIE_SECURE = True
        REMEMBER_COOKIE_SAMESITE = 'None'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
