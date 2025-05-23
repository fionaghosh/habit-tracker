# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:57:53 2025

@author: Fiona
"""

# tests/test_habits.py

import json
import pytest
from datetime import date

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

@pytest.fixture
def habit_client():
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

    # 3) Models
    class User(db.Model):
        id       = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(128), nullable=False)

    class Habit(db.Model):
        id          = db.Column(db.Integer, primary_key=True)
        user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        name        = db.Column(db.String(120), nullable=False)
        description = db.Column(db.Text)
        user        = db.relationship('User', backref='habits')

    class Completion(db.Model):
        id       = db.Column(db.Integer, primary_key=True)
        habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
        date     = db.Column(db.Date, nullable=False, default=date.today)
        habit    = db.relationship('Habit', backref='completions')

    # 4) Create schema
    with app.app_context():
        db.create_all()
        # seed one user
        u = User(username="u", password="p")
        db.session.add(u)
        db.session.commit()
        # get token
        token = create_access_token(identity=str(u.id))

    # 5) Define endpoints
    @app.route("/habits", methods=["POST"])
    @jwt_required()
    def create_habit():
        body = request.get_json() or {}
        name = body.get("name")
        if not name:
            return jsonify(error="name required"), 400
        user_id = get_jwt_identity()
        h = Habit(name=name, description=body.get("description",""), user_id=user_id)
        db.session.add(h); db.session.commit()
        return jsonify(id=h.id), 201

    @app.route("/habits", methods=["GET"])
    @jwt_required()
    def list_habits():
        user_id = get_jwt_identity()
        habits = Habit.query.filter_by(user_id=user_id).all()
        return jsonify([{"id":h.id,"name":h.name} for h in habits]), 200

    @app.route("/habits/<int:hid>/complete", methods=["POST"])
    @jwt_required()
    def mark_complete(hid):
        data = request.get_json() or {}
        comp_date = data.get("date")
        try:
            comp_date = date.fromisoformat(comp_date)
        except:
            return jsonify(error="invalid date"), 400
        c = Completion(habit_id=hid, date=comp_date)
        db.session.add(c); db.session.commit()
        return jsonify(status="ok"), 200

    @app.route("/streaks/<int:hid>", methods=["GET"])
    @jwt_required()
    def get_streak(hid):
        dates = [c.date for c in Completion.query.filter_by(habit_id=hid)]
        dates = sorted(set(dates))
        if not dates:
            return jsonify(current_streak=0), 200
        # compute simple streak back from today
        streak = 0
        today = date.today()
        for offset in range(len(dates)):
            if today.fromordinal(today.toordinal()-offset) in dates:
                streak += 1
            else:
                break
        return jsonify(current_streak=streak), 200

    # 6) Return a test client with Authorization header baked in
    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client

def test_create_and_list_habit(habit_client):
    # Create
    r = habit_client.post("/habits", json={"name":"Drink"})
    assert r.status_code == 201
    hid = r.get_json()["id"]

    # List
    lst = habit_client.get("/habits").get_json()
    assert any(h["id"] == hid for h in lst)

def test_mark_and_streak(habit_client):
    # Create X
    hid = habit_client.post("/habits", json={"name":"X"}).get_json()["id"]

    # Mark
    today = date.today().isoformat()
    r2 = habit_client.post(f"/habits/{hid}/complete", json={"date":today})
    assert r2.status_code == 200

    # Streak
    streak = habit_client.get(f"/streaks/{hid}").get_json()["current_streak"]
    assert isinstance(streak, int)
