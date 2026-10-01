# Loan Application

This repository is organized as two independently deployable applications:

- `frontend/`: Vite and React single-page application.
- `backend/`: FastAPI API and Supabase PostgreSQL integration.

## Local development

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Copy `backend/.env.example` to `backend/.env` and configure its values before starting the API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:8000`. To override that URL, copy
`frontend/.env.example` to `frontend/.env.local` and set `VITE_API_BASE_URL`.

## Vercel deployment

Deploy two Vercel projects from this repository:

1. **Backend project:** set **Root Directory** to `backend`. Configure
   `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `FRONTEND_URL`.
   Set `FRONTEND_URL` to the complete deployed frontend URL, without a trailing slash.
2. **Frontend project:** set **Root Directory** to `frontend`. Configure
   `VITE_API_BASE_URL` to the complete deployed backend URL, without a trailing slash.

Redeploy the backend after setting `FRONTEND_URL`, then redeploy the frontend after
setting `VITE_API_BASE_URL`. Variables prefixed with `VITE_` are embedded in the
browser bundle, so never put private credentials in them.