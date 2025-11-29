from flask import Blueprint, render_template, request, jsonify, current_app as app
from .models import QuestionPool, DailySession, CalendarStamp, Streak
from . import db
from datetime import date, datetime
import random

from .sampler import sample_questions
from .scorer import score_archetype

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/session/today")
def session_today():
    return render_template("session_today.html")

@main.route("/api/session/start", methods=["POST"])
def api_session_start():
    payload = request.get_json() or {}
    user_id = payload.get("user_id")
    date_local = payload.get("date_local") or date.today().isoformat()

    # call adaptive sampler
    ids = sample_questions(user_id)

    # store session
    sess = DailySession(
        user_id=user_id,
        date_local=date.fromisoformat(date_local),
        question_ids=ids
    )
    db.session.add(sess)
    db.session.commit()

    return jsonify({"question_ids": ids, "session_id": sess.id})

@main.route("/api/_questions_bulk", methods=["POST"])
def api_questions_bulk():
    p = request.get_json() or {}
    ids = p.get("ids", [])
    qs = QuestionPool.query.filter(QuestionPool.id.in_(ids)).all()
    result = [{"id":q.id, "text":q.text, "axes": q.axes} for q in qs]
    return jsonify(result)

@main.route("/api/session/submit", methods=["POST"])
def api_session_submit():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    date_local = data.get("date_local") or date.today().isoformat()
    answers = data.get("answers") or []
    session_id = data.get("session_id")
    sess = DailySession.query.get(session_id)
    if not sess:
        return jsonify({"error":"session not found"}), 404

    sess.answers = answers
    sess.completed_at = datetime.utcnow()

    # use scorer to compute archetype distribution and dominant
    archetype_dist, dominant = score_archetype(answers)

    # debug log to terminal
    app.logger.info(f"[SCORER] user={user_id} session={session_id} dominant={dominant} dist={archetype_dist}")

    emoji_map = {
        "Seeker":"🧭","Analyst":"🧠","Empath":"💗","Builder":"🛠️","Anchor":"⚓",
        "Visionary":"🚀","Mystic":"🔮","Narrator":"📖","Guardian":"🛡️","Rebel":"🔥"
    }
    emoji = emoji_map.get(dominant, "✨")

    sess.archetype_dist = archetype_dist
    sess.dominant_archetype = dominant
    sess.emoji = emoji
    db.session.add(sess)

    # only stamp calendar / update streaks if we have a real user_id
    if user_id is not None:
        # upsert calendar stamp
        stamp = CalendarStamp.query.filter_by(user_id=user_id, date_local=sess.date_local).first()
        if not stamp:
            stamp = CalendarStamp(user_id=user_id, date_local=sess.date_local, emoji=emoji, session_id=sess.id)
            db.session.add(stamp)
        else:
            stamp.emoji = emoji
            stamp.session_id = sess.id
            db.session.add(stamp)

        # update streaks (buffer rule handled later)
        s = Streak.query.filter_by(user_id=user_id).first()
        today = sess.date_local
        if not s:
            s = Streak(user_id=user_id, count=1, last_completed=today)
            db.session.add(s)
        else:
            if s.last_completed:
                delta = (today - s.last_completed).days
                if delta == 1:
                    s.count += 1
                elif delta <= 2:
                    s.count += 1
                else:
                    s.count = 1
            else:
                s.count = 1
            s.last_completed = today
            db.session.add(s)
    else:
        app.logger.debug(f"anon session {sess.id} - skipping streak/calendar (no user_id)")

    db.session.commit()
    return jsonify({"archetype_dist": archetype_dist, "dominant": dominant, "emoji": emoji, "session_id": sess.id})
