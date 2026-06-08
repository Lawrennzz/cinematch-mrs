"""
app.py
------
Streamlit user interface for the AI-powered Movie Recommendation System (MRS).

Covers Question 2.A of the assignment:
    Task 2.1 - rate movies, receive recommendations, search movies
    Task 2.2 - registered-user dashboard (top picks, trending, history,
               popular genres) with data visualisations
    Task 2.3 - admin console behind a unique login key (CRUD + engagement)
    Task 2.4 - packaged for Streamlit Community Cloud deployment

Run locally with:  streamlit run app.py
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st

from data import ADMIN_KEY, load_store, save_store
from models import Admin, Movie, RecommendationEngine, User

st.set_page_config(
    page_title="CineMatch | AI Movie Recommendations",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# State <-> domain object bridge
# ---------------------------------------------------------------------------
def build_objects(store: dict):
    """Convert the raw JSON store into domain objects."""
    movies: List[Movie] = []
    for m in store["movies"]:
        movies.append(Movie(m["movie_id"], m["title"], m["genres"],
                            m["year"], m.get("description", "")))

    users: Dict[str, User] = {}
    for uname, u in store["users"].items():
        users[uname] = User(u["username"], u["password"],
                            dict(u.get("ratings", {})), list(u.get("history", [])))

    # Project per-user ratings down onto each Movie so averages are correct.
    movie_by_id = {m.movie_id: m for m in movies}
    for user in users.values():
        for mid_str, score in user.ratings.items():
            movie = movie_by_id.get(int(mid_str))
            if movie:
                movie.add_rating(user.username, score)

    return movies, users


def persist(movies: List[Movie], users: Dict[str, User]) -> None:
    """Write domain objects back to the JSON store."""
    store = {
        "movies": [m.to_dict() for m in movies],
        "users": {name: u.to_dict() for name, u in users.items()},
    }
    save_store(store)
    st.session_state.store = store


def get_state():
    """Load/refresh domain objects held in session state."""
    if "store" not in st.session_state:
        st.session_state.store = load_store()
    movies, users = build_objects(st.session_state.store)
    engine = RecommendationEngine(movies, users)
    return movies, users, engine


# ---------------------------------------------------------------------------
# Chart helpers (native Streamlit — no extra dependencies)
# ---------------------------------------------------------------------------
def show_h_bar(df: pd.DataFrame, value_col: str, label_col: str,
               title: str) -> None:
    st.caption(title)
    chart_df = df.set_index(label_col)[[value_col]].sort_values(value_col)
    st.bar_chart(chart_df, width="stretch")


def show_v_bar(df: pd.DataFrame, label_col: str, value_col: str,
               title: str) -> None:
    st.caption(title)
    chart_df = df.set_index(label_col)[[value_col]]
    st.bar_chart(chart_df, width="stretch")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def auth_view(users: Dict[str, User]):
    st.title("🎬 CineMatch")
    st.caption("Your AI-powered movie recommendation companion")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", width="stretch")
        if submitted:
            username = username.strip().lower()
            user = users.get(username)
            if user and user.password == password:
                st.session_state.current_user = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.info("Demo accounts: **alice / alice123**, **bob / bob123**, "
                "**carol / carol123**")

    with register_tab:
        with st.form("register_form"):
            new_user = st.text_input("Choose a username")
            new_pass = st.text_input("Choose a password", type="password")
            submitted = st.form_submit_button("Create account", width="stretch")
        if submitted:
            new_user = new_user.strip().lower()
            if not new_user or not new_pass:
                st.error("Username and password are required.")
            elif new_user in users:
                st.error("That username is already taken.")
            else:
                movies, users_obj, _ = get_state()
                users_obj[new_user] = User(new_user, new_pass)
                persist(movies, users_obj)
                st.session_state.current_user = new_user
                st.success("Account created! Logging you in...")
                st.rerun()


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------
def movie_card(movie: Movie, user: User, key_prefix: str):
    """Render a movie with its rating control."""
    with st.container(border=True):
        st.markdown(f"**{movie.title}** ({movie.year})")
        st.caption(" · ".join(movie.genres))
        if movie.description:
            st.write(movie.description)
        avg = movie.average_rating()
        st.write(f"⭐ {avg if avg else '—'}  ·  {movie.rating_count()} ratings")

        current = user.ratings.get(str(movie.movie_id), 0)
        rating = st.slider(
            "Your rating",
            min_value=0, max_value=5,
            value=int(current),
            key=f"{key_prefix}_rate_{movie.movie_id}",
            help="0 = not rated",
        )
        if st.button("Save rating", key=f"{key_prefix}_save_{movie.movie_id}",
                     width="stretch"):
            if rating == 0:
                st.warning("Pick a rating between 1 and 5.")
            else:
                movies, users, _ = get_state()
                users[user.username].rate_movie(movie.movie_id, rating)
                persist(movies, users)
                st.success(f"Saved {rating}★ for {movie.title}")
                st.rerun()


# ---------------------------------------------------------------------------
# Task 2.1 - Rate & search
# ---------------------------------------------------------------------------
def rate_and_search_view(movies, users, engine, user):
    st.header("🔍 Discover & Rate Movies")

    query = st.text_input("Search by title or genre",
                          placeholder="e.g. Inception, Sci-Fi, Horror...")
    if query:
        results = engine.search(query)
        st.write(f"Found **{len(results)}** result(s) for '{query}'")
        cols = st.columns(3)
        for i, movie in enumerate(results):
            with cols[i % 3]:
                movie_card(movie, user, key_prefix="search")
    else:
        st.subheader("Browse the catalogue")
        genres = ["All"] + sorted({g for m in movies for g in m.genres})
        chosen = st.selectbox("Filter by genre", genres)
        shown = [m for m in movies if chosen == "All" or chosen in m.genres]
        cols = st.columns(3)
        for i, movie in enumerate(shown):
            with cols[i % 3]:
                movie_card(movie, user, key_prefix="browse")


# ---------------------------------------------------------------------------
# Task 2.2 - User dashboard
# ---------------------------------------------------------------------------
def dashboard_view(movies, users, engine, user):
    st.header(f"📊 {user.username.title()}'s Dashboard")

    movie_by_id = {m.movie_id: m for m in movies}

    # -- KPI row -----------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Movies watched", len(user.history))
    c2.metric("Movies rated", len(user.ratings))
    avg_given = (round(sum(user.ratings.values()) / len(user.ratings), 2)
                 if user.ratings else 0)
    c3.metric("Avg rating given", avg_given)

    st.divider()

    # -- Top recommendations ----------------------------------------------
    st.subheader("🎯 Top Recommended For You")
    recs = engine.recommend(user, top_n=5)
    if recs:
        rec_df = pd.DataFrame([
            {"Movie": m.title, "Genres": ", ".join(m.genres),
             "Match score": round(score, 3), "Avg rating": m.average_rating()}
            for m, score in recs
        ])
        st.dataframe(rec_df, width="stretch", hide_index=True)
        show_h_bar(rec_df, "Match score", "Movie", "Personalised match scores")
    else:
        st.info("Rate a few movies to unlock personalised recommendations.")

    st.divider()

    # -- Trending + popular genres ----------------------------------------
    left, right = st.columns(2)
    with left:
        st.subheader("🔥 Trending Now")
        trending = engine.trending(top_n=8)
        trend_df = pd.DataFrame([
            {"Movie": m.title, "Avg rating": m.average_rating(),
             "Ratings": m.rating_count()} for m in trending
        ])
        show_h_bar(trend_df, "Avg rating", "Movie", "Top-rated movies")

    with right:
        st.subheader("🎭 Popular Genres")
        pop = engine.popular_genres()
        if pop:
            genre_df = pd.DataFrame(pop, columns=["Genre", "Total ratings"])
            show_v_bar(genre_df, "Genre", "Total ratings",
                       "Popular genres by rating activity")

    st.divider()

    # -- Watch history + rating log ---------------------------------------
    st.subheader("🕓 Your Watch History & Rating Log")
    if user.history:
        log_rows = []
        for mid in reversed(user.history):
            movie = movie_by_id.get(mid)
            if movie:
                log_rows.append({
                    "Movie": movie.title,
                    "Genres": ", ".join(movie.genres),
                    "Year": movie.year,
                    "Your rating": user.ratings.get(str(mid), "—"),
                })
        st.dataframe(pd.DataFrame(log_rows), width="stretch",
                     hide_index=True)
    else:
        st.info("You haven't watched anything yet. Rate a movie to get started.")


# ---------------------------------------------------------------------------
# Task 2.3 - Admin console
# ---------------------------------------------------------------------------
def admin_view():
    st.header("🛠️ Administrative Console")

    if not st.session_state.get("admin_ok"):
        st.warning("Restricted area. Enter the admin access key to continue.")
        with st.form("admin_login"):
            key = st.text_input("Admin access key", type="password")
            submitted = st.form_submit_button("Unlock")
        if submitted:
            admin = Admin(ADMIN_KEY)
            if admin.authenticate(key):
                st.session_state.admin_ok = True
                st.success("Admin access granted.")
                st.rerun()
            else:
                st.error("Incorrect admin key.")
        st.caption(f"(Demo key for grading: `{ADMIN_KEY}`)")
        return

    movies, users, engine = get_state()
    admin = Admin(ADMIN_KEY)

    tab_manage, tab_analytics = st.tabs(
        ["Manage Catalogue", "User Engagement"])

    # -- CRUD --------------------------------------------------------------
    with tab_manage:
        st.subheader("Add a new movie")
        with st.form("add_movie"):
            title = st.text_input("Title")
            genres = st.text_input("Genres (comma separated)",
                                   placeholder="Action, Drama")
            year = st.number_input("Year", min_value=1900, max_value=2100,
                                   value=2024)
            desc = st.text_area("Description")
            if st.form_submit_button("Add movie"):
                if title and genres:
                    glist = [g.strip() for g in genres.split(",") if g.strip()]
                    admin.add_movie(movies, title, glist, int(year), desc)
                    persist(movies, users)
                    st.success(f"Added '{title}'.")
                    st.rerun()
                else:
                    st.error("Title and at least one genre are required.")

        st.divider()
        st.subheader("Edit or remove an existing movie")
        if movies:
            options = {f"#{m.movie_id} - {m.title}": m.movie_id for m in movies}
            selected = st.selectbox("Select a movie", list(options.keys()))
            mid = options[selected]
            movie = next(m for m in movies if m.movie_id == mid)

            with st.form("edit_movie"):
                e_title = st.text_input("Title", value=movie.title)
                e_genres = st.text_input("Genres (comma separated)",
                                         value=", ".join(movie.genres))
                e_year = st.number_input("Year", min_value=1900, max_value=2100,
                                         value=int(movie.year))
                e_desc = st.text_area("Description", value=movie.description)
                col_a, col_b = st.columns(2)
                save_clicked = col_a.form_submit_button("Save changes",
                                                        width="stretch")
                del_clicked = col_b.form_submit_button("Remove movie",
                                                       width="stretch",
                                                       type="secondary")
            if save_clicked:
                glist = [g.strip() for g in e_genres.split(",") if g.strip()]
                admin.edit_movie(movie, e_title, glist, int(e_year), e_desc)
                persist(movies, users)
                st.success("Movie updated.")
                st.rerun()
            if del_clicked:
                admin.remove_movie(movies, mid)
                persist(movies, users)
                st.success("Movie removed.")
                st.rerun()

        st.divider()
        st.subheader("Current catalogue")
        cat_df = pd.DataFrame([
            {"ID": m.movie_id, "Title": m.title, "Genres": ", ".join(m.genres),
             "Year": m.year, "Avg rating": m.average_rating(),
             "Ratings": m.rating_count()} for m in movies
        ])
        st.dataframe(cat_df, width="stretch", hide_index=True)

    # -- Analytics ---------------------------------------------------------
    with tab_analytics:
        st.subheader("Most-watched movies")
        watched = engine.most_watched(top_n=10)
        if watched:
            w_df = pd.DataFrame([
                {"Movie": m.title, "Unique viewers": c} for m, c in watched
            ])
            show_h_bar(w_df, "Unique viewers", "Movie",
                       "Most-watched movies (by unique viewers)")
        else:
            st.info("No engagement data yet.")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Registered users", len(users))
            st.metric("Movies in catalogue", len(movies))
        with c2:
            total_ratings = sum(m.rating_count() for m in movies)
            st.metric("Total ratings recorded", total_ratings)
            st.metric("Genres tracked", len(engine.all_genres))

        st.divider()
        st.subheader("Ratings volume by genre")
        pop = engine.popular_genres()
        if pop:
            g_df = pd.DataFrame(pop, columns=["Genre", "Ratings"])
            show_v_bar(g_df, "Genre", "Ratings", "Ratings volume by genre")


# ---------------------------------------------------------------------------
# Main router
# ---------------------------------------------------------------------------
def main():
    movies, users, engine = get_state()

    st.sidebar.title("🎬 CineMatch")

    current = st.session_state.get("current_user")
    if current and current in users:
        user = users[current]
        st.sidebar.success(f"Logged in as **{current}**")
        page = st.sidebar.radio(
            "Navigate",
            ["Discover & Rate", "My Dashboard", "Admin Console"],
        )
        if st.sidebar.button("Log out", width="stretch"):
            st.session_state.pop("current_user", None)
            st.session_state.pop("admin_ok", None)
            st.rerun()

        if page == "Discover & Rate":
            rate_and_search_view(movies, users, engine, user)
        elif page == "My Dashboard":
            dashboard_view(movies, users, engine, user)
        elif page == "Admin Console":
            admin_view()
    else:
        # Allow reaching the admin console without a normal user account too.
        page = st.sidebar.radio("Navigate", ["Login / Register", "Admin Console"])
        if page == "Admin Console":
            admin_view()
        else:
            auth_view(users)

    st.sidebar.divider()
    st.sidebar.caption("ITS74004 A3 · AI Movie Recommendation System")


try:
    main()
except Exception as exc:
    st.error("CineMatch failed to start.")
    st.exception(exc)
