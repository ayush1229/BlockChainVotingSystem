from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.admin'
login_manager.login_message_category = 'info'

from app.models import Admin
@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))

mail = Mail()

def create_app(class_config=Config):
    app = Flask(__name__)
    app.config.from_object(class_config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.main.routes import main
    from app.user.routes import user

    from app.vote.routes import vote
    app.register_blueprint(main)
    app.register_blueprint(vote)
    app.register_blueprint(user)

    return app


