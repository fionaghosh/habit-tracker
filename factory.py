# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:10:55 2025

@author: Fiona
"""

# factory.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from models import db, User, Habit, Completion
from habits import calculate_streak
from datetime import datetime

# Prometheus metrics
SIGNUPS       = Counter("signup_requests_total", "Total signup calls")
LOGINS        = Counter("login_requests_total", "Total login calls")
HABIT_CREATES = Counter("habit_creations_total", "Total habits created")
COMPLETIONS   = Counter("completions_total", "Total completions recorded")

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    # Default config
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///instance/habits.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="replace-this-with-a-secure-random-key"
    )
    # Override from passed-in dict
    if config:
        app.config.update(config)

    db.init_app(app)
    jwt = JWTManager(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.route("/healthz")
    def healthz():
        return "OK", 200

    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    @app.route("/signup", methods=["POST"])
    def signup():
        SIGNUPS.inc()
        u = request.get_json() or {}
        if not u.get("username") or not u.get("password"):
            return jsonify(error="username & password required"), 400
        if User.query.filter_by(username=u["username"]).first():
            return jsonify(error="username taken"), 400
        user = User(username=u["username"], password=u["password"])
        db.session.add(user); db.session.commit()
        token = create_access_token(identity=str(user.id))
        return jsonify(token=token), 201

    # ... (rest of your routes, copying from your old app.py) ...

    return app
