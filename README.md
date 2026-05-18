# Intelligent Recommended System

This repository is scaffolded for a hybrid recommendation platform with a FastAPI backend, ML pipelines, a React frontend, and deployment/monitoring assets.

Project layout

- `backend/`: API service for recommendations, user preferences, auth, and RAG explanations.
- `ml/`: collaborative filtering, content-based ranking, sentiment, and RAG utilities.
- Filtered sparse users/items and standardized interaction data to improve collaborative filtering performance and reduce noise.
- `frontend/`: React UI for browsing recommendations and requesting explanations.
- `infra/`: Kubernetes and monitoring manifests.
- `data/`: raw and processed datasets.
- `tests/`: backend, ML, and frontend test placeholders.

Getting started

1. Copy `.env.example` to `.env` and adjust the values for your local setup.
2. Start the local stack with Docker Compose:

```bash
docker compose up --build
```

3. Or work on the services individually:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

The Python environment files in the repository root are kept for local experimentation and package management. The older `src/main.py` verifier script is preserved as a simple dependency check.
