from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Junction table for many-to-many relationship: Users joining Event Groups
user_events = db.Table('user_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False) # <-- Add this explicit line
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    interests = db.Column(db.String(500), nullable=False)
    
    events_joined = db.relationship('Event', secondary=user_events, backref=db.backref('members', lazy='dynamic'))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # coding, sports, rides, custom, etc.
    custom_details = db.Column(db.String(200))
    total_cost = db.Column(db.Float, default=0.0)
    member_limit = db.Column(db.Integer, nullable=False)
    gender_preference = db.Column(db.String(20), default='All') # Male, Female, All
    event_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    host = db.relationship('User', backref=db.backref('hosted_events', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User')