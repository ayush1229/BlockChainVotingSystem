from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from flask import current_app
from sqlalchemy.orm import relationship
from itsdangerous import URLSafeTimedSerializer as Serializer
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    wallet_address = db.Column(db.String(42), nullable=True)

    # Relationship to store multiple emails
    emails = relationship('UserEmail', backref='user', lazy=True)
    session_verifications = relationship('UserSessionVerification', backref='user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class VotingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    results_released = db.Column(db.Boolean, nullable=False, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    candidates = db.relationship('Candidate', backref='session', lazy=True)

    def __repr__(self):
        return f"VotingSession('{self.title}', '{self.start_time}', '{self.end_time}')"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email_verification_method = db.Column(db.String(20), nullable=True)
    allowed_email_domain = db.Column(db.String(120), nullable=True)
    manual_verification_timelimit = db.Column(db.Integer, nullable=True)
    required_additional_info = db.Column(db.Text, nullable=True)
    voting_sessions = db.relationship('VotingSession', backref='creator', lazy=True)

    def __repr__(self):
        return f"Admin('{self.username}')"

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    session_id = db.Column(db.Integer, db.ForeignKey('voting_session.id'), nullable=False)


class ManualVerificationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voting_session_id = db.Column(db.Integer, db.ForeignKey('voting_session.id'), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class UserSessionVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voting_session_id = db.Column(db.Integer, db.ForeignKey('voting_session.id'), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    nft_token_id = db.Column(db.String(64), nullable=True) # Store NFT token ID if applicable

    db.UniqueConstraint('user_id', 'voting_session_id', name='_user_session_uc')



