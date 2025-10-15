# Project Repository

This is the initial README file for the project.

## Backend environment

Copy `.env.example` to `.env` in `events_backend` and adjust as needed:

- DATABASE_URL (default: sqlite:///./events.db)
- CORS_ORIGINS (default: http://localhost:3000)
- ENV (default: development)
- UVICORN_PORT (default: 3001)

To run the backend locally on port 3001:
1. cd events_backend
2. Create `.env` from `.env.example` and adjust if needed
3. Install deps: `pip install -r requirements.txt`
4. Start: `uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload`