from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import markupsafe

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_events = db.Table('user_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Whitelist of avatars users are allowed to pick from.
# Files must live at app/static/uploads/<filename>
AVAILABLE_AVATARS = ['avatar1.png', 'avatar2.png', 'avatar3.png']
DEFAULT_AVATAR = 'avatar1.png'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(200), default=DEFAULT_AVATAR) # Stored purely as string key
    interests = db.Column(db.String(500), nullable=False)
    
    events_joined = db.relationship('Event', secondary=user_events, backref=db.backref('members', lazy='dynamic'))
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # Renders the user's chosen uploaded avatar image anywhere it's called in Jinja.
    # Falls back to the default avatar if profile_pic isn't in the whitelist
    # (e.g. old/bad data), so a bad value never breaks the page.
    def render_avatar(self, extra_classes="w-12 h-12"):
        from flask import url_for
        filename = self.profile_pic if self.profile_pic in AVAILABLE_AVATARS else DEFAULT_AVATAR
        src = url_for('static', filename=f'uploads/{filename}')
        return markupsafe.Markup(
            f'<img src="{src}" alt="avatar" class="{extra_classes} rounded-full object-cover">'
        )

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    custom_details = db.Column(db.String(200))
    total_cost = db.Column(db.Float, default=0.0)
    member_limit = db.Column(db.Integer, nullable=False)
    gender_preference = db.Column(db.String(20), default='All')
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