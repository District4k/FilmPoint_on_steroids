from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import Watchlist, Movie, SurveyAnswer, SurveyQuestion, db
from .api import get_film_list_by_filter
from .forms import RegisterForm, AuthenticationForm  # Import forms


# Define the blueprint for 'main' routes
main = Blueprint('main', __name__)


# Index Route
@main.route('/')
def index():
    return render_template('index.html')


# Register Route
@main.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.save()
        login_user(user)
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.index'))
    flash('There was an error with your registration. Please try again.', 'error')
    return render_template('signup.html', form=form)


# Authentication function for login
def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


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
@main.route('/logout/', methods=['POST'])
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
    question_title = None
    user_survey_stage = current_user.current_stage
    questions = SurveyQuestion.query.filter_by(stage=user_survey_stage).all()
    if questions:
        question_title = questions[0].title
    stage_limit = 4
    if request.method == 'POST' and user_survey_stage < stage_limit:
        submitted_answer = request.form.get('answer')
        question_id = request.form.get('question')
        question = SurveyQuestion.query.get(int(question_id))
        answer = SurveyAnswer(user=current_user, question=question, answer=submitted_answer)
        db.session.add(answer)
        current_user.current_stage += 1
        db.session.commit()
        return redirect(url_for('main.intro_survey'))
    elif user_survey_stage == stage_limit:
        return redirect(url_for('main.get_recommendations'))
    return render_template('movie_survey.html', questions=questions, question_title=question_title)


# Get Recommendations Route
@main.route('/get_recommendations/', methods=['GET'])
@login_required
def get_recommendations():
    answers = SurveyAnswer.query.filter_by(user=current_user).all()
    answers_list = [answer.answer for answer in answers]
    recommended_movies = get_film_list_by_filter(answers_list, request)
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
