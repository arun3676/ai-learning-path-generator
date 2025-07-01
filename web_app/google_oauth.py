import os
from flask import Blueprint, redirect, url_for, flash, current_app, session, request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from web_app.models import User
from web_app import db
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('google_oauth')

# Create a very basic blueprint for Google OAuth
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    # Use the flask_dance default configuration (no redirect_uri specified)
)

# Log all environment variables for debugging (without sensitive values)
for key in os.environ:
    if 'SECRET' not in key and 'KEY' not in key:
        logger.info(f"ENV: {key}={os.environ.get(key)}")


# Create a separate blueprint for our callback route
bp = Blueprint("google_auth", __name__)

# Add login route for those who prefer a dedicated endpoint
@bp.route("/login")
def login():
    return redirect(url_for("google.login"))

@bp.route("/google/authorized")
@bp.route("/callback/google")
@bp.route("/google-callback")
def google_callback():
    """Handle the callback from Google OAuth"""
    # Log important debug info
    logger.info(f"Google OAuth callback received at {request.path}")
    logger.info(f"Full request URL: {request.url}")
    logger.info(f"Request args: {request.args}")
    logger.info(f"Is Google authorized? {google.authorized}")
    
    # If this route is hit directly without going through OAuth flow
    if not google.authorized:
        logger.error("Not authorized. Redirecting to login.")
        return redirect(url_for("google.login"))

    # Get user info from Google
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            logger.error(f"Failed to fetch user info: {resp.text}")
            flash("Failed to fetch user info from Google.", "danger")
            return redirect(url_for("auth.login"))

        info = resp.json()
        logger.info(f"Successfully retrieved user info")
        
        email = info.get("email")
        if not email:
            logger.error("Google account does not have an email.")
            flash("Google account does not have an email.", "danger")
            return redirect(url_for("auth.login"))

        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            logger.info(f"Creating new user: {email}")
            user = User(username=info.get("name", email.split("@")[0]), email=email)
            db.session.add(user)
            db.session.commit()
        else:
            logger.info(f"Found existing user: {email}")

        login_user(user, remember=True)
        flash("Logged in with Google!", "success")
        return redirect(url_for("main.index"))
        
    except Exception as e:
        logger.exception(f"Error in Google callback: {str(e)}")
        flash(f"An error occurred during login: {str(e)}", "danger")
        return redirect(url_for("auth.login"))
