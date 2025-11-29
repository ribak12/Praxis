import json
from .models import QuestionPool
from . import db
from flask import current_app

def seed_questions_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    created = 0
    for q in data:
        if QuestionPool.query.filter_by(q_key=q.get("id")).first():
            continue
        qp = QuestionPool(q_key=q.get("id"), text=q.get("text"), axes=q.get("axes", {}), rarity=q.get("rarity",1), difficulty=q.get("difficulty",1))
        db.session.add(qp)
        created += 1
    db.session.commit()
    return created
