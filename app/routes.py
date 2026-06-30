import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Event, Message
from werkzeug.utils import secure_filename
from datetime import datetime


from flask import current_app as app

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth_login'))

@app.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signup':
            email = request.form.get('email')
            roll_number = request.form.get('roll_number')
            password = request.form.get('password')
            age = request.form.get('age')
            gender = request.form.get('gender')
            interests = request.form.getlist('interests') # returns list from checkboxes
            
            file = request.files.get('profile_pic')
            filename = 'default.jpg'
            if file and file.filename != '':
                filename = secure_filename(f"{roll_number}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            user = User(
                email=email, roll_number=roll_number, password=password, 
                age=age, gender=gender, profile_pic=filename, 
                interests=",".join(interests)
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
            
        elif action == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid credentials')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    all_events = Event.query.all()
    
    # Smart Sorting Algorithm based on matching interest items
    user_interest_list = current_user.interests.split(',')
    
    def calculate_score(event):
        # Filter based on gender preference right out of the feed
        if event.gender_preference != 'All' and event.gender_preference != current_user.gender:
            return -1 
        
        # Exact category match weights highest
        score = 0
        if event.category in user_interest_list or (event.category == 'other' and event.custom_details):
            score += 10
        return score

    # Filter out mismatching genders and sort descending by personalized score
    filtered_events = [e for e in all_events if calculate_score(e) >= 0]
    sorted_events = sorted(filtered_events, key=calculate_score, reverse=True)

    return render_template('dashboard.html', events=sorted_events)

@app.route('/create-event', methods=['POST'])
@login_required
def create_event():
    title = request.form.get('title')
    category = request.form.get('category')
    custom_details = request.form.get('custom_details')
    total_cost = float(request.form.get('total_cost', 0.0))
    member_limit = int(request.form.get('member_limit', 5))
    gender_preference = request.form.get('gender_preference', 'All')
    event_time = datetime.strptime(request.form.get('event_time'), '%Y-%m-%dT%H:%M')
    location = request.form.get('location')

    new_event = Event(
        title=title, category=category, custom_details=custom_details,
        total_cost=total_cost, member_limit=member_limit,
        gender_preference=gender_preference, event_time=event_time,
        location=location, host_id=current_user.id
    )
    # Host auto-joins their own group
    new_event.members.append(current_user)
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/join-event/<int:event_id>')
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.members.count() < event.member_limit and current_user not in event.members:
        event.members.append(current_user)
        db.session.commit()
    return redirect(url_for('chat_room', event_id=event.id))

@app.route('/chat/<int:event_id>')
@login_required
def chat_room(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user not in event.members:
        return redirect(url_for('dashboard'))
    
    # Fetch historical chat logs
    messages = Message.query.filter_by(event_id=event.id).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', event=event, messages=messages)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_login'))