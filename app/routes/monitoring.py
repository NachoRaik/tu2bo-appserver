from flask import Blueprint, request, jsonify
from flask import current_app as app

bp_monitor = Blueprint("bp_monitor", __name__)

# -- Endpoints

@bp_monitor.route('/ping')
def ping():
    return "AppServer is ~app~ up!"


@bp_monitor.route('/stats')
def stats():
    return "This endpoint will return server stats in a future"

