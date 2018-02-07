from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user has already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # After the user posted login credential
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # If the credential is invalid, return to login page
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # Otherwise log in the user
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # If the login URL doesn't have a next argument, or  if the next is set
        # to a full URL that includes a domain name (for security issue),
        # redirects to the index page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
