# CORS and Base URL requirements for EventEase Frontend

To allow the React frontend on http://localhost:3000 or a cloud preview origin to access the FastAPI backend:

- CORS middleware is enabled in the FastAPI app.
- In development/local ENV, the backend will automatically include http://localhost:3000 in allowed origins even if CORS_ORIGINS is not set.
- You can explicitly configure origins via the CORS_ORIGINS env variable (comma-separated).
- The default configuration also includes a wildcard for preview hosts: https://*.cloud.kavia.ai
  (Starlette CORS supports wildcard subdomains).

Example .env (copy from .env.example):
CORS_ORIGINS=http://localhost:3000

Verify endpoints and CORS:

- Health
  curl -i http://localhost:3001/health

- Events list
  curl -i http://localhost:3001/events

- CORS preflight (should be 204 from Starlette)
  curl -i -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" \
    http://localhost:3001/events

Troubleshooting:
- If preflight fails with "Disallowed CORS origin", ensure the frontend origin is in CORS_ORIGINS or that ENV is development/local.
- Frontend should point REACT_APP_API_BASE_URL (or equivalent) to the backend (e.g., http://localhost:3001).
