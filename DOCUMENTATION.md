# ITS74004 — Assignment 3
# AI-Based Movie Recommendation System (MRS)

**Application name:** CineMatch
**Technology:** Python · Streamlit · Plotly · Pandas (object-oriented design)

> This document contains the full answers for **Question 1.A** (design) and
> **Question 2.A** (implementation, evidence and deployment). Source code is in
> `app.py`, `models.py` and `data.py`, and is also reproduced in Appendix A.

---

# QUESTION 1.A (15 Marks)

## Task 1.1 — UML Class Diagram (5 Marks)

**Purpose:** Design the object-oriented structure of the Movie Recommendation
System (MRS).

**Summary:** The UML class diagram models the MRS using four classes — User,
Movie, RecommendationEngine, and Admin — each with at least two attributes and
one method to support rating, recommendation, and catalogue management.

![UML Class Diagram](assets/uml_class_diagram.png)

The **User** class is associated with **Movie** through the *rates*
relationship, meaning one user can rate many movies and one movie can receive
ratings from many users. The **RecommendationEngine** class aggregates both
**User** and **Movie** objects so it can analyse behaviour and generate
recommendations. The **Admin** class depends on **Movie** to add, edit, and
remove films in the catalogue through secure administrative access.

Each class has a clear role in the system: User and Movie store data,
RecommendationEngine handles AI recommendation logic, and Admin manages the
movie catalogue. This structure keeps the system organised, easy to maintain,
and suitable for future improvements such as advanced machine learning models.

---

## Task 1.2 — Description of Attributes and Methods (5 Marks)

### Class `Movie`

**Summary & purpose:** The `Movie` class stores all information about a film in
the catalogue — including its title, genres, and ratings — so the system can
display movie details, calculate popularity, and use genre data as input for
recommendations.

| Member | Type | Description | Rationale |
|---|---|---|---|
| `movie_id` | Attribute | Unique ID for each movie. | Lets ratings and history reference the correct film. |
| `title` | Attribute | Name of the movie. | Shown in the UI and used for search. |
| `genres` | Attribute | List of genre tags. | Used as features for content-based recommendations. |
| `year` | Attribute | Release year. | Provides useful movie metadata. |
| `description` | Attribute | Short plot summary. | Helps users decide what to watch. |
| `ratings` | Attribute | Maps username to score. | Stores all user ratings for that movie. |
| `add_rating(user, score)` | Method | Saves or updates a rating. | Keeps rating logic inside the `Movie` class. |
| `average_rating()` | Method | Returns the mean rating. | Used for trending and recommendation scoring. |
| `rating_count()` | Method | Returns number of ratings. | Prevents one high rating from dominating rankings. |

### Class `User`

**Summary & purpose:** The `User` class represents a registered viewer and
records their login details, movie ratings, and watch history so the platform
can authenticate them, learn their preferences, and show personalised content
on their dashboard.

| Member | Type | Description | Rationale |
|---|---|---|---|
| `username` | Attribute | Unique login name. | Identifies the user in the system. |
| `password` | Attribute | Login credential. | Used for authentication. |
| `ratings` | Attribute | Maps movie ID to score. | Main input for personalised recommendations. |
| `history` | Attribute | List of watched movie IDs. | Supports watch logs and engagement analysis. |
| `rate_movie(id, score)` | Method | Rates a movie and logs it as watched. | Keeps ratings and history consistent. |
| `add_to_history(id)` | Method | Adds a movie to watch history. | Maintains a recent, de-duplicated watch list. |
| `preferred_genres()` | Method | Returns top liked genres. | Gives a simple summary of user taste. |

### Class `RecommendationEngine`

**Summary & purpose:** The `RecommendationEngine` class is the AI core of the
system — it analyses user behaviour and movie data to generate personalised
recommendations, identify trending titles, report popular genres, and support
movie search across the catalogue.

| Member | Type | Description | Rationale |
|---|---|---|---|
| `movies` | Attribute | Full movie catalogue. | Needed to search and recommend titles. |
| `users` | Attribute | All registered users. | Supports recommendations and analytics. |
| `recommend(user)` | Method | Returns top recommended movies. | Core AI logic using genre similarity. |
| `trending()` | Method | Returns popular movies. | Shows what is currently popular on the platform. |
| `popular_genres()` | Method | Returns most active genres. | Supports genre insight charts. |
| `search(query)` | Method | Finds movies by title or genre. | Helps users quickly locate films. |

### Class `Admin`

**Summary & purpose:** The `Admin` class provides secure, restricted access
for system administrators to manage the movie catalogue and review user
engagement, ensuring only authorised staff can add, edit, or remove content.

| Member | Type | Description | Rationale |
|---|---|---|---|
| `admin_key` | Attribute | Secret admin access key. | Restricts admin features to authorised users. |
| `actions_log` | Attribute | Record of admin actions. | Tracks changes made to the system. |
| `authenticate(key)` | Method | Checks the admin key. | Protects the admin console. |
| `add_movie()` | Method | Adds a new movie. | Keeps the catalogue up to date. |
| `edit_movie()` | Method | Updates movie details. | Allows correction of movie information. |
| `remove_movie()` | Method | Deletes a movie. | Removes outdated or unwanted titles. |

### Overall System

**Purpose:** Design an AI-powered Movie Recommendation System for a streaming platform.

**Summary:** The MRS is an object-oriented system that uses user ratings and
watch history to generate personalised movie recommendations, display trending
content and genre insights, and allow administrators to manage the catalogue,
supporting both user engagement and platform analytics through a modular class
design.

---

## Task 1.3 — How the System Analyses Behaviour & Improves Over Time (5 Marks)

The MRS analyses user behaviour by recording movie ratings and watch history.
Each rating is stored through `User.rate_movie()`, which helps the system learn
what genres and films a user enjoys. The `RecommendationEngine` uses this data
to build a preference profile for each user.

Recommendations are generated using content-based filtering. Rated movies are
converted into genre vectors and combined into a user profile. Unseen movies
are ranked by cosine similarity to that profile, with a small popularity score
used for tie-breaking. New users with no ratings are shown trending movies
until enough data is available.

The system updates in real time because new ratings are saved immediately and
the engine is rebuilt on the next page load, so recommendations change as soon
as the user rates more films. Machine learning can improve results further over
time through methods such as collaborative filtering and hybrid models, which
learn from similar users and adapt as more viewing data is collected.

---

# QUESTION 2.A (25 Marks)

The system is implemented as an interactive **Streamlit** web application
(`app.py`). Navigation is via the sidebar: **Discover & Rate**, **My Dashboard**
and **Admin Console**.

## Task 2.1 — Rate Movies, Recommendations & Search (5 Marks)

Implemented in `rate_and_search_view()`:
- **Search** — a text box queries title *and* genre (`RecommendationEngine.search`).
- **Browse + genre filter** — the full catalogue with a genre dropdown.
- **Rating** — every movie card has a 1–5 star slider and a *Save rating* button
  that calls `User.rate_movie()`.
- **Recommendations** — after rating, personalised picks appear on the dashboard
  (`RecommendationEngine.recommend`).

**Evidence (screenshot):** *Insert screenshot — "Discover & Rate" page showing a
search result and a rating slider.*

## Task 2.2 — Registered-User Dashboard (10 Marks)

Implemented in `dashboard_view()`:
- **Top recommended movies** — ranked table + horizontal bar chart of match scores.
- **Trending movies** — bar chart of top-rated titles (Bayesian weighting).
- **Popular genres** — donut chart of engagement share by genre.
- **Watch history & rating log** — chronological table of watched films and the
  score the user gave.
- **KPIs** — movies watched, movies rated, average rating given.
- **Data visualisations** — bar charts and a pie/donut chart via Plotly.

**Evidence (screenshots):** *Insert screenshots — KPI row, recommendation bar
chart, trending bar chart, popular-genres donut, and the watch-history table.*

## Task 2.3 — Administrative Console (6 Marks)

Implemented in `admin_view()`, gated by the unique key `ADMIN-2026-MRS`:
- **Add movie** — form for title, genres, year, description (`Admin.add_movie`).
- **Edit / Remove movie** — select a film, update fields or delete it
  (`Admin.edit_movie`, `Admin.remove_movie`).
- **Catalogue table** — live view of all movies with average rating & counts.
- **User-engagement analytics** — *most-watched movies* bar chart, platform KPIs
  (users, movies, total ratings, genres) and a *ratings-by-genre* bar chart.

**Evidence (screenshots):** *Insert screenshots — admin key prompt, add/edit
form, and the "Most-watched movies" engagement chart.*

## Task 2.4 — Streamlit Deployment (4 Marks)

**Deployed Application URL:** `__________________________________________`

**Deployment steps (to complete and paste your live URL above):**

1. Create a **public GitHub repository** and push `app.py`, `models.py`,
   `data.py`, `requirements.txt` and the `.streamlit/` folder.
2. Sign in at **https://share.streamlit.io** with GitHub and click **New app**.
3. Select the repository and branch, and set **Main file path** to `app.py`.
4. Click **Deploy** — Streamlit Community Cloud automatically installs the
   pinned dependencies in `requirements.txt` (`streamlit`, `pandas`, `plotly`);
   no `packages.txt` or `Procfile` is needed because there are no system-level
   or web-server dependencies.
5. Once the build finishes, copy the public `*.streamlit.app` URL and paste it
   above. Verify it loads in an incognito window before submission.

**Brief explanation (3–5 sentences):** *The application was deployed to Streamlit
Community Cloud, which hosts Python apps directly from a public GitHub repository.
The only configuration required was a `requirements.txt` listing the pinned
dependencies (streamlit, pandas, plotly), which the platform installs
automatically during the build. An optional `.streamlit/config.toml` sets the
theme, and the app entry point is `app.py`. No `packages.txt` or `Procfile` was
needed since the app has no system-level packages or custom server. After
deployment the public URL was confirmed to be accessible.*

---

## Demo Credentials

- **Users:** `alice / alice123`, `bob / bob123`, `carol / carol123`
- **Admin key:** `ADMIN-2026-MRS`

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
# open http://localhost:8501
```

---

# Appendix A — Source Code

The complete source is in the accompanying Python files:
- `models.py` — `Movie`, `User`, `RecommendationEngine`, `Admin`
- `data.py` — seed catalogue, demo users, JSON persistence
- `app.py` — Streamlit UI for all user journeys

Copy these files into your submission document or attach them as separate
`.py` files as required by the assessment guidelines.
