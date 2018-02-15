from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm
from app.models import User
from email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/user/<username>')
@login_required
def user(username):
    usr = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=usr)


@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if username != current_user.username:
        return redirect(url_for('user', username=current_user.username))
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)


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
        # token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        # flash('A confirmation email has been sent to you by email.')
        # return redirect('index.html')
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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            send_password_reset_email(user)
        flash('CHeck your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    usr = User.verify_reset_password_token(token)
    if not usr:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        usr.set_pasword(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
