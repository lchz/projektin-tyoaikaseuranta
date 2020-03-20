from flask import Flask

app = Flask(__name__)

# DB
import os
from flask_sqlalchemy import SQLAlchemy

if os.environ.get('HEROKU'):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Login, config
from os import urandom
app.config['SECRET_KEY'] = urandom(32)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'auth_login'
login_manager.login_message = 'Please login to use this functionality.'


# Login, ROLES
from functools import wraps

def login_required(_func=None, *, role="ANY"):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not (current_user and current_user.is_authenticated):
                return login_manager.unauthorized()

            accetable_roles = set(("ANY", current_user.get_roles()))
            if role not in accetable_roles:
                return login_manager.unauthorized()

            return func(*args, **kwargs)
        return decorated_view
    return wrapper if _func is None else wrapper(_func)


# UI
from application import views

from application.projects import models
from application.projects import views

from application.tasks import models
from application.tasks import views

from application.auth import models
from application.auth import views


# Logging in
from application.auth.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


try:
    db.create_all()
except:
    pass