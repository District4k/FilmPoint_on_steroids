from sqlite3 import IntegrityError
from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Watchlist, Movie, SurveyAnswer, SurveyQuestion, User
from .api import get_film_list_by_filter
from film_point.extensions import db
from .forms import RegisterForm, AuthenticationForm, ForgotPasswordForm, generate_reset_token, send_reset_email, \
    verify_reset_token, SurveyForm

main = Blueprint('main', __name__)


# Index Route
@main.route('/')
def index():
    return render_template('index.html')


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


@main.route('/retake_survey', methods=['POST'])
@login_required
def retake_survey():
    if request.method == 'POST':
        stage_reset = request.form.get('stage_reset')

        if stage_reset:
            # Reset the current stage
            current_user.current_stage = 1

            # Commit the change to the user
            db.session.add(current_user)
            db.session.commit()

            # Delete the user's survey answers
            SurveyAnswer.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()

            # Redirect to the intro survey page
            return redirect(url_for('main.intro_survey'))

        # If no stage_reset, redirect to the main index
        return redirect(url_for('main.index'))


@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Get the password entered by the user
    password = request.form.get('password')

    if not password:
        flash("Please enter your password to confirm account deletion.", "danger")
        return redirect(url_for('main.index'))  # Redirect back to the profile page or a confirmation page

    try:
        # Check if the entered password matches the current user's password
        if check_password_hash(current_user.password, password):
            # Password matched, proceed with deletion
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted successfully.', 'success')
            logout_user()  # Log the user out
            return redirect(url_for('main.index'))  # Redirect to the homepage or login page
        else:
            flash("Incorrect password. Account deletion failed.", "danger")
            return redirect(url_for('main.index'))  # Redirect back to the profile page
    except Exception as e:
        db.session.rollback()
        flash('There was an error deleting your account. Please try again.', 'danger')
        return redirect(url_for('main.index'))


@main.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    user = verify_reset_token(token)
    if user is None:
        flash('The token is invalid or has expired', 'error')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        # Handle password reset form submission
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
            db.session.commit()  # Save changes to the database
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('main.login_view'))
        else:
            flash('Please provide a valid password.', 'error')

    return render_template('reset_password.html', token=token)


@main.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a password reset token
            token = generate_reset_token(user, current_app.config['SECRET_KEY'])
            # Send the reset link to the user’s email (pass 'current_app.mail' as argument)
            send_reset_email(user, token, current_app.mail)  # Ensure 'current_app.mail' is passed here
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found.', 'error')
        return redirect(url_for('main.login_view'))
    return render_template('forgot_password.html', form=form)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Ensure username and email are not empty
        if not username or not email:
            flash('Username and email are required.', 'danger')
            return redirect(url_for('main.edit_profile'))

        # Check if passwords match
        if password and password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('main.edit_profile'))

        # Update the user's details
        current_user.username = username
        current_user.email = email

        # If the user provided a new password, hash and update it
        if password:
            current_user.password = generate_password_hash(password)

        try:
            # Commit the changes to the database
            db.session.commit()
            flash('Your profile has been successfully updated!', 'success')
        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')
            print(e)  # For debugging purposes

        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html')


# Register Route
@main.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST':
        # Validate the form
        if form.validate():
            # Check if email or username already exists
            existing_user = User.query.filter(
                (User.email == form.email.data) | (User.username == form.username.data)
            ).first()

            if existing_user:
                if existing_user.email == form.email.data:
                    flash('The email is already registered. Please log in.', 'error')
                elif existing_user.username == form.username.data:
                    flash('The username is already taken. Please choose a different one.', 'error')
                return render_template('signup.html', form=form)

            # No duplicates, try to save the new user
            try:
                user = form.save()
                login_user(user)
                flash('Your account has been created!', 'success')
                return redirect(url_for('main.index'))
            except IntegrityError as e:
                db.session.rollback()
                flash('An error occurred during registration due to a database issue. Please try again later.', 'error')
                print(f"Database Integrity Error: {e}")
            except Exception as e:
                db.session.rollback()
                flash('An unexpected error occurred during registration. Please try again later.', 'error')
                print(f"Unexpected Error: {e}")
        else:
            flash('There was an error with your registration. Please check the form and try again.', 'error')

    return render_template('signup.html', form=form)


# Login Route
@main.route('/login/', methods=['GET', 'POST'])
def login_view():
    form = AuthenticationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = authenticate(username, password)
        if user:
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)


# Logout Route
@main.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout_view():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


# Profile Route
@main.route('/profile/', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)


# Watchlist Route
@main.route('/watchlist/', methods=['GET'])
@login_required
def watchlist():
    movie_ids_in_watchlist = [entry.movie_id for entry in Watchlist.query.filter_by(user=current_user).all()]
    movies_in_watchlist = Movie.query.filter(Movie.id.in_(movie_ids_in_watchlist)).all()
    return render_template('watchlist.html', movies=movies_in_watchlist, user=current_user)


# Survey intro route


@main.route('/survey/', methods=['GET', 'POST'])
@login_required
def intro_survey():
    form = SurveyForm()
    question_title = None
    user_survey_stage = current_user.current_stage
    questions = SurveyQuestion.query.filter_by(stage=user_survey_stage).all()
    if questions:
        question_title = questions[0].title
    stage_limit = 4
    if request.method == 'POST' and user_survey_stage < stage_limit:
        if form.validate_on_submit():  # Ensure CSRF token is validated
            submitted_answer = request.form.get('answer')
            question_id = request.form.get('question')
            question = SurveyQuestion.query.get(int(question_id))
            answer = SurveyAnswer(user_id=current_user.id, question=question, answer=submitted_answer)
            db.session.add(answer)
            current_user.current_stage += 1
            db.session.commit()
            return redirect(url_for('main.intro_survey'))
    elif user_survey_stage == stage_limit:
        return redirect(url_for('main.get_recommendations'))
    return render_template('movie_survey.html', questions=questions, question_title=question_title, form=form)


# Get Recommendations Route
@main.route('/get_recommendations/', methods=['GET'])
@login_required
def get_recommendations():
    answers = SurveyAnswer.query.filter_by(user_id=current_user.id).all()
    answers_list = [answer.answer for answer in answers]
    recommended_movies = get_film_list_by_filter(answers_list)
    return render_template('recommendation.html', recommended_movies=recommended_movies)


# Movie Detail Route
@main.route('/movie/<int:movie_id>/', methods=['GET'])
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('movie_detail.html', movie=movie)


# Add to Watchlist Route
@main.route('/add_to_watchlist/', methods=['POST'])
@login_required
def add_to_watchlist():
    movie_id = request.form.get('movie_id')
    movie_name = request.form.get('movie_name')
    movie_image = request.form.get('movie_image')
    movie_year = request.form.get('movie_year')
    movie_rating = request.form.get('movie_rating')
    movie_description = request.form.get('movie_description')
    movie_genre = request.form.get('movie_genre')

    movie_data = {
        'name': movie_name,
        'image': movie_image,
        'genre': movie_genre,
        'year': movie_year,
        'description': movie_description,
        'rating': movie_rating,
        'movie_id': movie_id
    }

    movie = Movie.query.filter_by(movie_id=movie_id).first()
    if not movie:
        movie = Movie(**movie_data)
        db.session.add(movie)
        db.session.commit()

    watchlist_entry = Watchlist(user=current_user, movie=movie)
    db.session.add(watchlist_entry)
    db.session.commit()

    return jsonify({'status': 'added'})


# Delete from Watchlist Route
@main.route('/delete_from_watchlist/', methods=['POST'])
@login_required
def delete_from_watchlist():
    movie_id = request.form.get('movie_id')
    movie = Movie.query.filter_by(movie_id=movie_id).first_or_404()

    watchlist_entry = Watchlist.query.filter_by(user=current_user, movie=movie).first()
    db.session.delete(watchlist_entry)
    db.session.commit()

    movie_ids_in_watchlist = [entry.movie_id for entry in Watchlist.query.filter_by(user=current_user).all()]
    movies_in_watchlist = Movie.query.filter(Movie.id.in_(movie_ids_in_watchlist)).all()
    return render_template('watchlist.html', movies=movies_in_watchlist, user=current_user)
