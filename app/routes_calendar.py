from flask import Blueprint, jsonify, render_template, request
from datetime import date
from .models import CalendarStamp
from . import db
from sqlalchemy import and_

calendar_bp = Blueprint("calendar", __name__)

@calendar_bp.route("/calendar")
def calendar_view():
    return render_template("calendar.html")

@calendar_bp.route("/api/calendar/get", methods=["POST"])
def api_calendar_get():
    data = request.get_json() or {}
    user_id = data.get("user_id", None)
    year = int(data.get("year", date.today().year))
    month = int(data.get("month", date.today().month))

    # if user_id is None -> query stamps with NULL user_id (anonymous) OR allow all if you prefer
    if user_id is None:
        stamps = CalendarStamp.query.filter(
            CalendarStamp.user_id.is_(None)
        ).all()
    else:
        stamps = CalendarStamp.query.filter_by(user_id=user_id).all()

    result = [
        {
            "date": s.date_local.isoformat(),
            "emoji": s.emoji,
            "session_id": s.session_id
        }
        for s in stamps
        if s.date_local.year == year and s.date_local.month == month
    ]

    return jsonify(result)
