from app.extensions import db  # Only import db from app.extensions
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    current_stage = db.Column(db.Integer, default=1)

    # Relationship with Watchlist
    watchlists = db.relationship('Watchlist', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="Question")
    question = db.Column(db.Text)
    filter = db.Column(db.String(32), default='filter')
    stage = db.Column(db.Integer, default=1)

    # Relationship with SurveyAnswer
    answers = db.relationship('SurveyAnswer', backref='question', lazy=True)

    def __repr__(self):
        return self.question


class SurveyAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_question.id'), nullable=False)

    def __repr__(self):
        return f"Answer for {self.question.title}"


class MoviePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    year_range = db.Column(db.String(50))
    region = db.Column(db.String(50))

    def __repr__(self):
        return f"{self.user_id} Preferences"


class Amenities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __repr__(self):
        return self.name


# Corrected Movie model (merged the definitions)
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, unique=True, default=-1)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    year = db.Column(db.String(4))
    image = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0)
    genre = db.Column(db.String(250))

    # Relationship with Watchlist and Review
    watchlists = db.relationship('Watchlist', backref='movie', lazy=True)
    reviews = db.relationship('Review', backref='movie', lazy=True)

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'name': self.name,
            'genre': self.genre,
            'year': self.year,
            'description': self.description,
            'image': self.image,
            'rating': self.rating
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    def __repr__(self):
        return f"Review for {self.movie.name} by {self.user.username}"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(128))
    score = db.Column(db.Integer)

    # Relationship with Answer
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return self.question


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.String(128))

    def __repr__(self):
        return self.answer


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __repr__(self):
        return f"{self.user.username}'s Watchlist"
