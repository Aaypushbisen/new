import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from app.service_ai import chat_gpt, extract_fields_with_gpt
from app.service_ocr import ocr_from_url


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

    api_key = os.getenv("API_KEY", "")

    def authenticate(req) -> bool:
        return bool(api_key) and req.headers.get("x-api-key") == api_key

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.post("/ocr")
    def ocr():
        if not authenticate(request):
            return jsonify({"error": "unauthorized"}), 401
        data = request.get_json(silent=True) or {}
        file_url = data.get("file_url")
        if not file_url:
            return jsonify({"error": "file_url required"}), 400
        text = ocr_from_url(file_url)
        return {"text": text}

    @app.post("/prefill")
    def prefill():
        if not authenticate(request):
            return jsonify({"error": "unauthorized"}), 401
        body = request.get_json(silent=True) or {}
        text = body.get("text") or ""
        schema = body.get("schema") or {"name": "", "dob": "", "address": "", "mobile": ""}
        fields = extract_fields_with_gpt(text, schema)
        return {"fields": fields}

    @app.post("/chat")
    def chat():
        if not authenticate(request):
            return jsonify({"error": "unauthorized"}), 401
        body = request.get_json(silent=True) or {}
        messages = body.get("messages") or []
        reply = chat_gpt(messages)
        return {"reply": reply}

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

