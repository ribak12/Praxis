from .models import QuestionPool
import math

ARCHETYPES = [
    "Seeker","Analyst","Empath","Builder","Anchor",
    "Visionary","Mystic","Narrator","Guardian","Rebel"
]

# TEMP basic weight matrix (real one in Batch 3)
WEIGHTS = {
    "logic": {
        "Analyst": 1.0,
        "Narrator": 0.3
    },
    "emotion": {
        "Empath": 1.0,
        "Mystic": 0.4
    },
    "action": {
        "Builder": 1.0,
        "Rebel": 0.5
    },
    "reflection": {
        "Seeker": 1.0,
        "Mystic": 0.3
    },
    "social": {
        "Guardian": 1.0,
        "Anchor": 0.5
    }
}

def softmax(values):
    exp_vals = [math.exp(v) for v in values]
    total = sum(exp_vals)
    return [round(ev / total, 4) for ev in exp_vals]

def score_archetype(answers):
    """answers = [{q_id, value}]"""

    # aggregate axis scores
    axis_scores = {"logic":0, "emotion":0, "action":0, "reflection":0, "social":0}

    for a in answers:
        q = QuestionPool.query.get(a["q_id"])
        if not q:
            continue
        rating = a["value"] / 10.0
        for axis, weight in q.axes.items():
            axis_scores[axis] += rating * weight

    # map axis → archetype score
    arch_scores = {a:0 for a in ARCHETYPES}

    for axis, val in axis_scores.items():
        if axis in WEIGHTS:
            for arch, multiplier in WEIGHTS[axis].items():
                arch_scores[arch] += val * multiplier

    # convert to softmax
    score_list = [arch_scores[a] for a in ARCHETYPES]
    dist = softmax(score_list)

    final = {ARCHETYPES[i]: dist[i] for i in range(len(ARCHETYPES))}
    dominant = max(final, key=final.get)

    return final, dominant
