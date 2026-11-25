"""Avatar conversacional local: catálogo + OpenAI Responses API opcional."""

import os
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
from time import monotonic

from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

from knowledge import instructions, is_fair_project_query, load_catalog, offline_reply


ROOT = Path(__file__).parent
app = Flask(__name__, static_folder="web", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 10_000
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def output_token_limit() -> int:
    try:
        requested = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1200"))
    except ValueError:
        return 1200
    return max(256, min(requested, 4000))


MAX_OUTPUT_TOKENS = output_token_limit()
client = OpenAI(api_key=API_KEY, timeout=20.0, max_retries=1) if API_KEY else None
visits: dict[str, deque[float]] = defaultdict(deque)
visits_lock = Lock()


def limited(ip: str) -> bool:
    now = monotonic()
    with visits_lock:
        queue = visits[ip]
        while queue and now - queue[0] > 60:
            queue.popleft()
        if len(queue) >= 20:
            return True
        queue.append(now)
    return False


@app.get("/")
def home():
    return send_from_directory("web", "index.html")


@app.get("/api/status")
def status():
    catalog = load_catalog()
    return jsonify(ai_enabled=bool(client), model=MODEL if client else None,
                   career=catalog["carrera"]["nombre"])


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
        return jsonify(error="Envía un mensaje de texto"), 400
    message = payload["message"].strip()
    if not message or len(message) > 500:
        return jsonify(error="El mensaje debe tener entre 1 y 500 caracteres"), 400
    if limited(request.remote_addr or "local"):
        return jsonify(error="Demasiadas preguntas. Espera un momento."), 429
    if is_fair_project_query(message):
        return jsonify(reply="Ahora solo respondo preguntas sobre la carrera de Computación y sus docentes.", mode="restricted")
    catalog = load_catalog()
    if not client:
        return jsonify(reply=offline_reply(message, catalog), mode="demo")
    history = payload.get("history", [])
    clean_history = []
    if isinstance(history, list):
        for item in history[-6:]:
            if isinstance(item, dict) and item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
                if not is_fair_project_query(item["content"]):
                    clean_history.append({"role": item["role"], "content": item["content"][:500]})
    try:
        response = client.responses.create(
            model=MODEL,
            instructions=instructions(catalog),
            input=[*clean_history, {"role": "user", "content": message}],
            max_output_tokens=MAX_OUTPUT_TOKENS,
            store=False,
        )
        return jsonify(reply=response.output_text.strip() or "No pude responder. Intenta de nuevo.", mode="ai")
    except Exception:
        app.logger.exception("Error de OpenAI API")
        return jsonify(error="No pude conectar con la IA. Consulta al organizador o intenta más tarde."), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, threaded=True, use_reloader=False)
