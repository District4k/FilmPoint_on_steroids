# from film_point import create_app
# from .models import SurveyQuestion
# from .extensions import db
# import json
#
#
# # Initialize the film_point and load the fixtures
# def load_fixtures():
#     with open('fixtures.json', 'r') as f:
#         data = json.load(f)
#
#     # Add the data to the database
#     for entry in data:
#         question_data = entry['fields']
#         question = SurveyQuestion(
#             title=question_data['title'],
#             question=question_data['question'],
#             filter=question_data['filter'],
#             stage=question_data['stage'],
#         )
#         db.session.add(question)
#
#     # Commit changes to the database
#     db.session.commit()
#     print("Fixtures loaded successfully.")
#
#
# # Create the Flask film_point
# app = create_app()
#
# # Run within the application context
# if __name__ == '__main__':
#     with app.app_context():
#         load_fixtures()
