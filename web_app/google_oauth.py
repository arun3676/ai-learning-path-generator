import os
from flask import Blueprint, redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user
from web_app.models import User
from web_app import db

# Create Google OAuth blueprint
# Client credentials must be set in environment variables

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_url="/login/google/authorized",
)

bp = Blueprint("google_auth", __name__)


@bp.route("/login/google/authorized")
def google_authorized():
    """Handle the callback from Google OAuth"""
    if not google.authorized:
        flash("Authorization failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "danger")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = info.get("email")
    if not email:
        flash("Google account does not have an email.", "danger")
        return redirect(url_for("auth.login"))

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=info.get("name", email.split("@")[0]), email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Logged in with Google!", "success")
    return redirect(url_for("main.index"))
