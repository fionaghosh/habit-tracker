# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:57:31 2025

@author: Fiona
"""
# tests/test_auth.py

import json
import pytest

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token

# ----------------------------
# Minimal app‐in‐test definition
# ----------------------------

@pytest.fixture
def auth_client():
    # 1) Create a fresh Flask app
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test-secret-key"
    })

    # 2) Init extensions
    db = SQLAlchemy(app)
    jwt = JWTManager(app)

    # 3) Define a simple User model
    class User(db.Model):
        id       = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(128), nullable=False)

    # 4) Create all tables
    with app.app_context():
        db.create_all()

    # 5) Define endpoints
    @app.route("/signup", methods=["POST"])
    def signup():
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
        u = request.get_json() or {}
        user = User.query.filter_by(username=u.get("username")).first()
        if not user or user.password != u.get("password"):
            return jsonify(error="bad credentials"), 401
        token = create_access_token(identity=str(user.id))
        return jsonify(token=token), 200

    # 6) Return a test client
    return app.test_client()

def test_signup_and_login(auth_client):
    creds = {"username": "u", "password": "p"}

    # SIGNUP
    r1 = auth_client.post(
        "/signup",
        data=json.dumps(creds),
        content_type="application/json"
    )
    assert r1.status_code == 201, r1.get_data(as_text=True)
    body1 = r1.get_json()
    assert "token" in body1 and isinstance(body1["token"], str)

    # LOGIN
    r2 = auth_client.post(
        "/login",
        data=json.dumps(creds),
        content_type="application/json"
    )
    assert r2.status_code == 200, r2.get_data(as_text=True)
    body2 = r2.get_json()
    assert "token" in body2 and isinstance(body2["token"], str)
