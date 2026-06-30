from flask import request
from flask_socketio import emit, join_room, leave_room
from . import socketio, db
from .models import Message, User
from flask_login import current_user

@socketio.on('join')
def handle_join(data):
    room = str(data['event_id'])
    join_room(room)
    # Modern Feature: System notifies room when a classmate hops on
    emit('status', {'msg': f"{current_user.name} joined the plan."}, room=room)
@socketio.on('text')
def handle_message(data):
    room = str(data['event_id'])
    msg_content = data['msg'].strip()
    
    if msg_content:
        new_msg = Message(event_id=int(room), user_id=current_user.id, content=msg_content)
        db.session.add(new_msg)
        db.session.commit()
        
        emit('message', {
            'user_id': current_user.id,    # <-- Pass ID for layout matching
            'user_name': current_user.name, # <-- Pass Name for display
            'msg': msg_content,
            'pic': current_user.profile_pic
        }, room=room)