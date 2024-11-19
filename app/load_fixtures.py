import sys
import os
import json  # Add this import to fix the issue

# Add the parent directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import SurveyQuestion  # Add necessary imports here

app = create_app()

with app.app_context():
    with open('fixtures.json') as f:
        fixtures = json.load(f)

    for fixture in fixtures:
        if fixture['model'] == 'events.surveyquestion':
            fields = fixture['fields']
            survey_question = SurveyQuestion(
                title=fields['title'],
                question=fields['question'],
                filter=fields['filter'],
                stage=fields['stage']
            )
            db.session.add(survey_question)

    db.session.commit()
    print("Survey questions have been added.")
