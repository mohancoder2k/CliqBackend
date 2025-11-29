# app.py -- Flask backend for Projects Risk Monitor
import os
import logging
import traceback
from flask import Flask, request, jsonify, abort

# import your logic from methods.py (single import)
from methods import process_tasks_and_notify, generate_daily_digest

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

from flask import request, abort
import os

def verify_token():
    secret = os.getenv("CLIQ_WEBHOOK_SECRET")
    token = request.headers.get("X-Webhook-Token", "")
    if secret and token != secret:
        abort(401)
# ---------- Flask endpoints ----------
@app.route("/webhook/cliq", methods=["POST"])
def webhook_cliq():
    verify_token()
    try:
        payload = request.get_json(silent=True) or {}

        msg = ""
        text_content = payload.get("text") or payload.get("content") or payload.get("message")
        if isinstance(text_content, dict):
            msg = text_content.get("content", "") or text_content.get("text", "")
        elif isinstance(text_content, str):
            msg = text_content

        msg = (msg or "").strip()

        if msg.upper() == "TEST":
            summary = process_tasks_and_notify()
            return jsonify({"status": "ok", "summary": summary}), 200

        return jsonify({"status": "ignored"}), 200

    except Exception:
        logger.error("webhook_cliq error:\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": "internal server error"}), 500


@app.route("/digest", methods=["POST"])
def digest():
    verify_token()
    try:
        res = generate_daily_digest()
        return jsonify({"status": "ok", "result": res}), 200
    except Exception:
        logger.error("digest error:\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": "internal server error"}), 500


@app.route("/monitor", methods=["POST"])
def monitor():
    verify_token()
    try:
        res = process_tasks_and_notify()
        return jsonify({"status": "ok", "result": res}), 200
    except Exception:
        logger.error("monitor error:\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": "internal server error"}), 500


@app.route("/debug/tasks", methods=["GET"])
def debug_tasks():
    try:
        summary = process_tasks_and_notify()
        return jsonify({"status": "ok", "summary": summary}), 200
    except Exception:
        logger.error("debug_tasks error:\n" + traceback.format_exc())
        return jsonify({"status": "error", "message": "internal server error"}), 500





@app.route("/health", methods=["GET"])
def health():
    # Keep health check minimal and fast
    return jsonify({"status": "ok", "message": "healthy"}), 200


@app.route("/__debug", methods=["GET"])
def debug_route():
    return jsonify({"status": "ok", "message": "DEPLOYED VERSION"}), 200


if __name__ == "__main__":
    # Use PORT env if provided by the platform (Railway/Heroku)
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
