### Backend (FastAPI)

- Create and fill `.env` based on `.env.example`.
- Create a Python venv and install deps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- Initialize DB and run API:

```bash
python -c "from app.main import init_db; init_db()"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API docs: `http://localhost:8000/docs`

Security notes:
- JWT for auth. Use HTTPS in production and secure storage for tokens on device.
- Field-level AES-GCM encryption for sensitive content.
- Access grants allow patients to authorize providers with scopes and expiry.
- All access is audited in `audit_logs`.