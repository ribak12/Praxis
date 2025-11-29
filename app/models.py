from . import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    avatar = db.Column(db.String)
    timezone = db.Column(db.String)
    settings = db.Column(JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuestionPool(db.Model):
    __tablename__ = "question_pool"
    id = db.Column(db.Integer, primary_key=True)
    q_key = db.Column(db.String, unique=True)
    text = db.Column(db.Text, nullable=False)
    axes = db.Column(JSON, nullable=False)
    rarity = db.Column(db.Integer, default=1)
    difficulty = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdvicePool(db.Model):
    __tablename__ = "advice_pool"
    id = db.Column(db.Integer, primary_key=True)
    archetype = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)

class RitualPool(db.Model):
    __tablename__ = "ritual_pool"
    id = db.Column(db.Integer, primary_key=True)
    archetype = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    duration_sec = db.Column(db.Integer, default=30)

class DailySession(db.Model):
    __tablename__ = "daily_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date_local = db.Column(db.Date, nullable=False)
    question_ids = db.Column(JSON)
    answers = db.Column(JSON)
    archetype_dist = db.Column(JSON)
    dominant_archetype = db.Column(db.String)
    emoji = db.Column(db.String)
    completed_at = db.Column(db.DateTime)

class CalendarStamp(db.Model):
    __tablename__ = "calendar_stamps"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date_local = db.Column(db.Date, nullable=False)
    emoji = db.Column(db.String)
    session_id = db.Column(db.Integer, db.ForeignKey("daily_sessions.id"))
    ritual_done = db.Column(db.Boolean, default=False)

class Streak(db.Model):
    __tablename__ = "streaks"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    count = db.Column(db.Integer, default=0)
    last_completed = db.Column(db.Date)
    buffer_until = db.Column(db.Date)

class Friend(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
