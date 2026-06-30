import eventlet
eventlet.monkey_patch()  # <-- Add this to fix the RLock greening warning

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

# ... rest of your existing app/__init__.py code remains exactly the same

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth_login'
# Inside app/__init__.py

# Update this line to include async_mode explicitly
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from . import routes, models
        db.create_all() # Automatically creates MySQL tables if they don't exist in Railway

    return app