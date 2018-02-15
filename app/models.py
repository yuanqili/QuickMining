from datetime import datetime
from hashlib import md5
from time import time
from urllib.parse import urlencode

import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app


#  Current Database Schema
#  Feb 7, 2017
#
#  +------------------+     +---------------+     +------------+
#  | levels           |     | users         |     | activities |
#  +------------------+     +---------------+     +------------+
#  | id               |--.  | id            |--.  | id         |
#  | title            |  |  | username      |  `--| user_id    |
#  | hash-rate        |  |  | email         |     | datetime   |
#  | earning-rate     |  |  | password_hash |     | notes      |
#  | profit-rate      |  `--| level_id      |     +------------+
#  | affiliate-bonus  |     | credit        |
#  | price            |     +---------------+
#  | credit           |
#  +------------------+

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), default=1)
    credit = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)

    activities = db.relationship('Activity', backref='user', lazy='dynamic')

    def modify_credits(self, delta):
        self.credit += delta
        db.session.add(self)
        db.session.commit()

    def modify_level(self, level):
        self.level_id = level
        db.session.add(self)
        db.session.commit()

    def avatar(self, size=128):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        base = 'https://www.gravatar.com/avatar'
        params = urlencode({'d': 'identicon', 's': size})
        return f'{base}/{digest}?{params}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        # Note that jwt.encode() returns a byte string
        token = jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
        return token.decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """
        This method takes a token and attempts to decode it by invoking PyJWT's
        jwt.decode() function. If the token cannot be validated or is expired,
        an exception will be raised, and in that case it catches it to prevent
        the error, and then return None to the caller. If the token is valid,
        then the value of the reset_password key from the token's payload is the
        ID of the user, so it can load the user and return it.
        :param token: A JWT token of the format {'reset_password': ..., 'exp': ...}
        :return:
        """
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

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
        return f'<User {self.username}>'


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


class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    hash_rate = db.Column(db.Float)
    earning_rate = db.Column(db.Integer)
    profit_rate = db.Column(db.Integer)
    affiliate_bonus = db.Column(db.Float)
    price = db.Column(db.Integer)
    credit = db.Column(db.Integer)

    users = db.relationship('User', backref='level', lazy='dynamic')

    def __repr__(self):
        return f'<UserClass {self.title}>'


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Activity {self.user_id}[{self.timestamp}]: {notes}>'


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post {}>'.format(self.body)
