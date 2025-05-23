# -*- coding: utf-8 -*-
"""
Created on Fri May 23 12:55:15 2025

@author: Fiona
"""

# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer,  primary_key=True)
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
