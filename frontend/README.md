# AISAF frontend

## Run locally

1. Start the API from `backend/`:
   `uvicorn main:app --reload --port 8000`
2. In this folder, install dependencies with `npm install`.
3. Run `npm run dev` and open the shown Vite URL.

Set `VITE_API_BASE_URL` in `.env` when the API is not running at `http://127.0.0.1:8000`.
