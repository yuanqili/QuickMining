from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


#  +---------------+     +---------------+
#  | users         |     | posts         |
#  +---------------+     +---------------+
#  | id            |--.  | id            |
#  | username      |  |  | body          |
#  | email         |  |  | timestamp     |
#  | password_hash |  `--| user_id       |
#  +---------------+     +---------------+


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login required items
    # is_authenticated
    #   : a property that is True if the user has valid credentials
    # is_active
    #   : a property that is True if the user's account is active
    # is_anonymous
    #   : a property that is False for regular users
    # get_id() -> string
    #   : a method that returns a unique id for the user as a string

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    """
    Loads user for Flask-Login.

    Flask-Login keeps track of the logged in user by storing its unique id in
    Flask's user session, a storage space assigned to each user who connects to
    the application. Each time the logged-in user navigates to a new page,
    Flask-Login retrieves the ID of the user from the session, and then loads
    that user into the memory.

    :param id: unicode user id
    :return: the corresponding user object
    """
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
