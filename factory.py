# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:10:55 2025

@author: Fiona
"""

# factory.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
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

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    # Health check endpoint
    @app.route("/healthz")
    def healthz():
        # You could add deeper checks here (DB connectivity, etc.)
        return "", 200

    # Prometheus metrics endpoint
    @app.route("/metrics")
    def metrics():
        # Expose all defined Counters in Prometheus format
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
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
        return jsonify(token=token), 201

    @app.route("/login", methods=["POST"])
    def login():
        LOGINS.inc()
        u = request.get_json() or {}
        if not u.get("username") or not u.get("password"):
            return jsonify(error="username & password required"), 400
        user = User.query.filter_by(username=u["username"]).first()
        if not user or not user.check_password(u["password"]):
            return jsonify(error="invalid credentials"), 401
        token = create_access_token(identity=str(user.id))
        return jsonify(token=token), 200

    # ... your other habit and completion routes here ...
    # e.g. create habit, list habits, mark completion, streak, etc.

    return app

