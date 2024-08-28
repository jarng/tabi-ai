import requests
from flask import jsonify, request, current_app as app
from werkzeug.exceptions import BadRequest
from . import api


@api.route("/plan")
def plan():
    llm = app.config["LLM"]

    user_id = request.args.get("user_id")
    city = request.args.get("city")
    language = request.args.get("language")

    preferences = ""

    if not user_id or not city:
        raise BadRequest("Missing required parameters")

    # Get user survey from booking service
    booking_service_url = app.config["TABI_BOOKING_BASE_URL"]
    booking_service_url += f"/users/{user_id}/survey"
    try:
        user_survey = requests.get(booking_service_url, timeout=10).json()
        activities = user_survey["activities"] or ""
        place_type = user_survey["place_type"] or ""
        seasons = user_survey["seasons"] or ""
        preferences = (
            f"Activities: {activities}\nPlace type: {place_type}\nSeasons: {seasons}"
        )
    except requests.exceptions.HTTPError as e:
        app.logger.error(f"HTTP error: {e}")
    except requests.exceptions.ConnectionError as e:
        app.logger.error(f"Connection error: {e}")
    except requests.exceptions.Timeout as e:
        app.logger.error(f"Timeout error: {e}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error: {e}")
    except Exception as e:
        app.logger.error(f"Error getting user survey: {e}")

    msg = {
        "city": city,
        "language": language,
        "preferences": preferences,
        "user_id": user_id,
    }

    try:
        return jsonify({"message": llm.plan(msg)})
    except Exception as e:
        app.logger.error(f"Error in plan api: {e}")
