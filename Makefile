run:
	ALLOWED_ORIGINS='*' API_KEY='dev' PYTHONUNBUFFERED=1 python3 app/app.py

install:
	pip3 install --break-system-packages -r requirements.txt

health:
	curl -sS http://localhost:8080/health || true

