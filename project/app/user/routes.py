from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
import json
from app import db, bcrypt
from app.models import User, Admin
from app.user.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from app.user.utils import save_picture, send_reset_email

user = Blueprint('user', __name__)

@user.route('/voter_auth', methods=['GET', 'POST'])
def voter_auth():
    if current_user.is_authenticated:
        # If already logged in, redirect to vote page (need session_id)
        # Placeholder redirect for now
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index')) # Or a page that lists sessions

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        wallet_address = request.form.get('wallet_address') # Assume this comes from the form/JS

        user = User.query.filter_by(email=email).first()

        if user:
            # User exists, log them in
            # For a real app, you'd want a proper login flow, potentially with password verification
            # For this scenario, we'll assume email is enough for re-authentication after initial setup
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
        else:
            # New user, create account
            # We'll generate a dummy password as it's not used for login here based on the instruction
            hashed_password = bcrypt.generate_password_hash('dummy_password').decode('utf-8')
            new_user = User(username=name, email=email, password=hashed_password, wallet_address=wallet_address)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Your voter account has been created and you are logged in!', 'success')

        # TODO: Redirect to the vote_in_session page for a specific session_id.
        # Need to determine how the application knows which session the user wants to vote in.
        return redirect(url_for('main.index')) # Placeholder redirect

    return render_template('voter_auth.html', title='Voter Login/Register')

@user.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Assuming emails are submitted as a comma-separated string or similar
        email_list = [e.strip() for e in form.emails.data.split(',') if e.strip()]
        # Store emails as a JSON string
        emails_json = json.dumps(email_list)

        # The primary email field might still be useful, or you can remove it if emails list is sufficient
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, emails=emails_json)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('user.login'))
    return render_template('register.html', title='Register', form=form)

@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@user.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@user.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('user.login'))
    
@user.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@user.route('/link_wallet', methods=['GET', 'POST'])
@login_required
def link_wallet():
    # This route primarily serves the template for Metamask linking.
    return render_template('link_wallet.html', title='Link Wallet')
