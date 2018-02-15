import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)


login.login_view = 'login'


# from app import routes
# The app package is defined by the app directory and the __init__.py script.
# The routes module needs to import the app variable just declared, so it is
# imported at bottom to avoid circular imports.
from . import routes, models, errors


if not app.debug:
    # Setting up the email logger is somewhat tedious due to having to handle
    # optional security options that are present in many email servers. But in
    # essence, the code below creates a SMTPHandler instance, sets its level so that
    # it only reports errors and not warnings, informational or debugging messages,
    # and finally attaches it to the app.logger object from Flask.
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=f'no-reply@{app.config["MAIL_SERVER"]}',
            toaddrs=app.config['ADMINS'],
            subject='ModernFlask Failure',
            credentials=auth,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # There are some failure conditions that do not end in a Python exception
    # and are not a major problem, but they may still be interesting enough to
    # save for debugging purposes. So we have a log file for the application.
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(filename='logs/modern_flask.log', maxBytes=10240, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # To make the logging more useful, we lower the logging level to the INFO
    # category, both in the application logger and the file logger handler.
    # Note: Debug, Info, Warning, Error, Critical in increasing order of severity.
    app.logger.setLevel(logging.INFO)

    # The server writes a line to the logs each time it starts.
    app.logger.info('ModernFlask startup')
