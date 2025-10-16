# CORS and Base URL requirements for EventEase Frontend

To allow the React frontend on http://localhost:3000 to access the FastAPI backend:

- Install CORS middleware if not present:
  from fastapi.middleware.cors import CORSMiddleware

- Add middleware to the FastAPI app:
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=False,
      allow_methods=["*"],
      allow_headers=["*"],
  )

- Ensure health endpoint at GET /health returns 200 OK (JSON or text).

- Events routes should be mounted at /events (list/create) and /events/{event_id} (get/update/delete) to match frontend.

If deploying to a preview environment, set REACT_APP_API_BASE_URL in the frontend to the public backend host, and include that origin in allow_origins accordingly.
