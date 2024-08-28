from flask import jsonify

from werkzeug.exceptions import BadRequest


def handle_bad_request(e: BadRequest):
    return (
        jsonify(
            {"error": "Bad Request", "message": e.description, "code": BadRequest.code}
        ),
        BadRequest.code,
    )
