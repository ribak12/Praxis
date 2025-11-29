from app import create_app
from app.seed import seed_questions_from_file

app = create_app()
with app.app_context():
    created = seed_questions_from_file("seed/questions.json")
    print("created:", created)
