# CineMatch — AI-Based Movie Recommendation System (MRS)

Coursework: **ITS74004 A3** · An AI-powered movie recommendation platform built
with Python + Streamlit.

## Features

| Task | Feature |
|------|---------|
| 2.1  | Rate movies, content-based recommendations, search by title/genre |
| 2.2  | Registered-user dashboard: top picks, trending, popular genres, watch history + rating log, bar/pie visualisations |
| 2.3  | Admin console (unique key) for add/edit/remove movies + engagement analytics |
| 2.4  | Streamlit Community Cloud deployment |

## Project structure

```
ITS74004 A3/
├── app.py            # Streamlit UI (all user journeys)
├── models.py         # OOP core: Movie, User, RecommendationEngine, Admin
├── data.py           # Seed dataset + JSON persistence
├── requirements.txt  # Dependencies for deployment
├── .streamlit/
│   └── config.toml   # Theme + server config
└── DOCUMENTATION.md  # Full assignment answers (Q1 + Q2)
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501

## Demo credentials

- **Users:** `alice / alice123`, `bob / bob123`, `carol / carol123`
- **Admin key:** `ADMIN-2026-MRS`

## Deploy to Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. Go to https://share.streamlit.io → **New app**.
3. Select the repo/branch and set the main file path to `app.py`.
4. Click **Deploy**. The platform installs `requirements.txt` automatically.

## How recommendations work

The `RecommendationEngine` builds a weighted genre-preference vector from the
movies a user has rated, then ranks unseen movies by cosine similarity between
that profile and each movie's genre vector, with a small popularity term for
tie-breaking. New users (cold start) are shown trending titles until they have
rated enough movies.
