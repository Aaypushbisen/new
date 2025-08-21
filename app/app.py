import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from app.service_ai import chat_gpt, extract_fields_with_gpt
from app.service_ocr import ocr_from_url
from app.service_esign import start_esign
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    CORS(app, resources={r"/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

    api_key = os.getenv("API_KEY", "")
    upload_dir = os.getenv("UPLOAD_DIR") or str(Path(__file__).with_name("uploads"))
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_DIR"] = upload_dir
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

    def authenticate(req) -> bool:
        return bool(api_key) and req.headers.get("x-api-key") == api_key

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

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

    def _allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.post("/upload")
    def upload():
        if not authenticate(request):
            return jsonify({"error": "unauthorized"}), 401
        if "file" not in request.files:
            return jsonify({"error": "file is required (multipart form)"}), 400
        f = request.files["file"]
        if not f or not f.filename:
            return jsonify({"error": "empty filename"}), 400
        if not _allowed_file(f.filename):
            return jsonify({"error": "unsupported file type"}), 400
        filename = secure_filename(f.filename)
        new_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = Path(app.config["UPLOAD_DIR"]) / new_name
        f.save(str(save_path))
        public_url = request.host_url.rstrip("/") + f"/files/{new_name}"
        return {"file_url": public_url, "filename": new_name}

    @app.get("/files/<path:filename>")
    def files(filename: str):
        # In production, use a CDN or object storage; this is for development.
        return send_from_directory(app.config["UPLOAD_DIR"], filename, as_attachment=False)

    @app.post("/esign/start")
    def esign_start():
        if not authenticate(request):
            return jsonify({"error": "unauthorized"}), 401
        body = request.get_json(silent=True) or {}
        document_url = body.get("document_url") or ""
        fields = body.get("fields") or {}
        if not document_url:
            return jsonify({"error": "document_url required"}), 400
        result = start_esign(document_url, fields)
        return result

    @app.get("/esign/callback")
    def esign_callback():
        # Provider would redirect here with status; store and show receipt
        status = request.args.get("status", "unknown")
        return {"status": status}

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

