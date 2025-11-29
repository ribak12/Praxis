from .models import QuestionPool, DailySession
from datetime import date
import random

def sample_questions(user_id):
    """
    Adaptive sampler (simple version for now).
    Later we will add: rarity weighting, axis diversity, cooldown, and last-day influence.
    """

    # fetch all questions
    qs = QuestionPool.query.all()
    if not qs:
        return []

    # STEP 1 — pick 5 to 12 random (placeholder before adaptive logic)
    count = random.randint(5, 12)
    selected = random.sample(qs, min(count, len(qs)))

    return [q.id for q in selected]
