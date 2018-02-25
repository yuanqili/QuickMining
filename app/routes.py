from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, \
    SubmitTicketForm
from app.models import User, Level
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


###
# Admin pages
###


@app.route('/')
@app.route('/home')
@login_required
def index():
    return render_template('production/home.html', title='Home')


@app.route('/history')
@login_required
def history():
    return render_template('production/history.html', title='History')


@app.route('/profile')
@login_required
def profile():
    return render_template('production/user.html', title='Profile')


@app.route('/contact-us', methods=['GET', 'POST'])
@login_required
def contact_us():
    form = SubmitTicketForm()
    return render_template('production/contact-us.html', title='Contact Us', form=form)


@app.route('/pricing')
@login_required
def pricing():
    return render_template('production/pricing.html', title='Pricing')


@app.route('/show-page')
def show_page():
    return render_template('production/show-page.html', title='Show Page')


@app.route('/test')
def test():
    return render_template('production/sign-in-up-form.html', title='Sign in')


@app.route('/admin')
def admin():
    users = User.query.all()
    contracts = Level.query.all()
    return render_template('production/admin.html', title='Admin', users=users, contracts=contracts)


@app.route('/signin', methods=['GET', 'POST'])
def signin2():
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
            return redirect(url_for('signin2'))
        # Otherwise log in the user
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # If the login URL doesn't have a next argument, or  if the next is set
        # to a full URL that includes a domain name (for security issue),
        # redirects to the index page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('production/signin.html', title='Sign In', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup2():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        usr = User(username=form.username.data, email=form.email.data)
        usr.set_password(form.password.data)
        db.session.add(usr)
        db.session.commit()
        # token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        # flash('A confirmation email has been sent to you by email.')
        # return redirect('index.html')
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('signin2'))
    return render_template('production/signup.html', title='Sign Up', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


###
# Tests
###


# @app.route('/user/<username>/edit', methods=['GET', 'POST'])
# @login_required
# def edit_profile(username):
#     if username != current_user.username:
#         return redirect(url_for('user', username=current_user.username))
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         db.session.commit()
#         flash('Your changes have been saved')
#         return redirect(url_for('user', username=current_user.username))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#     return render_template('edit_profile.html', title='Edit Profile', form=form)
#
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         # token = user.generate_confirmation_token()
#         # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
#         # flash('A confirmation email has been sent to you by email.')
#         # return redirect('index.html')
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Sign Up', form=form)
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # If the user has already logged in
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     # After the user posted login credential
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         # If the credential is invalid, return to login page
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         # Otherwise log in the user
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         # If the login URL doesn't have a next argument, or  if the next is set
#         # to a full URL that includes a domain name (for security issue),
#         # redirects to the index page
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)
#
#
# @app.route('/reset_password_request', methods=['GET', 'POST'])
# def reset_password_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = ResetPasswordRequestForm()
#     if form.validate_on_submit():
#         if User.query.filter_by(email=form.email.data).first():
#             send_password_reset_email(user)
#         flash('CHeck your email for the instructions to reset your password')
#         return redirect(url_for('login'))
#     return render_template('reset_password_request.html', title='Reset password', form=form)
#
#
# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     usr = User.verify_reset_password_token(token)
#     if not usr:
#         return redirect(url_for('index'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         usr.set_pasword(form.password.data)
#         db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('login'))
#     return render_template('reset_password.html', form=form)
