"""
models.py
---------
Object-oriented core of the Movie Recommendation System (MRS).

This module implements the classes shown in the UML class diagram:

    Movie                 - a single film in the catalogue
    User                  - a registered viewer with ratings + watch history
    RecommendationEngine  - content-based recommender + analytics
    Admin                 - privileged operations on the catalogue

Keeping the domain logic here (separate from the Streamlit UI in ``app.py``)
demonstrates a clean separation of concerns and makes the logic unit-testable.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


# ===========================================================================
# Movie
# ===========================================================================
class Movie:
    """Represents a single movie in the catalogue."""

    def __init__(self, movie_id: int, title: str, genres: List[str],
                 year: int, description: str = "") -> None:
        self.movie_id = movie_id            # attribute 1: unique identifier
        self.title = title                  # attribute 2: display title
        self.genres = genres                # attribute 3: list of genre tags
        self.year = year
        self.description = description
        self.ratings: Dict[str, int] = {}   # username -> rating (1..5)

    def add_rating(self, username: str, score: int) -> None:
        """Record/replace a single user's rating for this movie."""
        self.ratings[username] = int(score)

    def average_rating(self) -> float:
        """method: mean of all ratings (0.0 when the film has no ratings)."""
        if not self.ratings:
            return 0.0
        return round(sum(self.ratings.values()) / len(self.ratings), 2)

    def rating_count(self) -> int:
        return len(self.ratings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "genres": self.genres,
            "year": self.year,
            "description": self.description,
        }


# ===========================================================================
# User
# ===========================================================================
class User:
    """Represents a registered viewer of the platform."""

    def __init__(self, username: str, password: str,
                 ratings: Optional[Dict[str, int]] = None,
                 history: Optional[List[int]] = None) -> None:
        self.username = username                    # attribute 1
        self.password = password                    # attribute 2
        self.ratings: Dict[str, int] = ratings or {}  # movie_id(str) -> score
        self.history: List[int] = history or []       # watched movie ids

    def rate_movie(self, movie_id: int, score: int) -> None:
        """method: store a rating and log the movie as watched."""
        self.ratings[str(movie_id)] = int(score)
        self.add_to_history(movie_id)

    def add_to_history(self, movie_id: int) -> None:
        """Append to watch history, keeping the most recent occurrence last."""
        if movie_id in self.history:
            self.history.remove(movie_id)
        self.history.append(movie_id)

    def preferred_genres(self, movies: List[Movie], top_n: int = 3) -> List[str]:
        """Return the genres the user rates most highly (weighted by score)."""
        movie_by_id = {m.movie_id: m for m in movies}
        weights: Counter = Counter()
        for mid_str, score in self.ratings.items():
            movie = movie_by_id.get(int(mid_str))
            if movie:
                for genre in movie.genres:
                    weights[genre] += score
        return [g for g, _ in weights.most_common(top_n)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "ratings": self.ratings,
            "history": self.history,
        }


# ===========================================================================
# RecommendationEngine
# ===========================================================================
class RecommendationEngine:
    """Content-based recommender plus platform-level analytics.

    The engine builds a genre profile for the user from the movies they rated
    highly, then scores every unseen movie by cosine similarity between that
    profile and the movie's genre vector. A small popularity term breaks ties
    so well-loved titles surface ahead of obscure ones.
    """

    def __init__(self, movies: List[Movie], users: Dict[str, User]) -> None:
        self.movies = movies
        self.users = users
        self.all_genres = sorted({g for m in movies for g in m.genres})

    # -- vector helpers ----------------------------------------------------
    def _genre_vector(self, genres: List[str]) -> List[float]:
        return [1.0 if g in genres else 0.0 for g in self.all_genres]

    def _user_profile(self, user: User) -> List[float]:
        """Build a weighted genre-preference vector for a user."""
        profile = [0.0] * len(self.all_genres)
        movie_by_id = {m.movie_id: m for m in self.movies}
        for mid_str, score in user.ratings.items():
            movie = movie_by_id.get(int(mid_str))
            if not movie:
                continue
            # Centre ratings around 3 so disliked films pull the profile down.
            weight = score - 2.5
            vec = self._genre_vector(movie.genres)
            for i, v in enumerate(vec):
                profile[i] += weight * v
        return profile

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    # -- public API --------------------------------------------------------
    def recommend(self, user: User, top_n: int = 5) -> List[Tuple[Movie, float]]:
        """method: return the top-N recommended unseen movies with scores."""
        profile = self._user_profile(user)
        seen = set(int(mid) for mid in user.ratings.keys()) | set(user.history)

        # Cold-start: no useful profile yet -> fall back to trending.
        if not any(profile):
            return [(m, m.average_rating()) for m in self.trending(top_n)
                    if m.movie_id not in seen][:top_n]

        max_avg = max((m.average_rating() for m in self.movies), default=5) or 1
        scored: List[Tuple[Movie, float]] = []
        for movie in self.movies:
            if movie.movie_id in seen:
                continue
            similarity = self._cosine(profile, self._genre_vector(movie.genres))
            popularity = movie.average_rating() / max_avg  # 0..1
            score = 0.85 * similarity + 0.15 * popularity
            if score > 0:
                scored.append((movie, round(score, 4)))

        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_n]

    def trending(self, top_n: int = 5) -> List[Movie]:
        """Trending = highest rated, weighted by how many people rated it.

        Uses a Bayesian-style weighted score so a single 5-star rating does not
        outrank a film with many strong ratings.
        """
        global_avg = (sum(m.average_rating() for m in self.movies if m.rating_count())
                      / max(1, sum(1 for m in self.movies if m.rating_count())))
        minimum_votes = 2

        def weighted(m: Movie) -> float:
            v = m.rating_count()
            r = m.average_rating()
            if v == 0:
                return 0.0
            return (v / (v + minimum_votes)) * r + (minimum_votes / (v + minimum_votes)) * global_avg

        return sorted(self.movies, key=weighted, reverse=True)[:top_n]

    def popular_genres(self) -> List[Tuple[str, int]]:
        """Return genres ranked by total number of ratings received."""
        counter: Counter = Counter()
        for movie in self.movies:
            for genre in movie.genres:
                counter[genre] += movie.rating_count()
        return counter.most_common()

    def most_watched(self, top_n: int = 10) -> List[Tuple[Movie, int]]:
        """Engagement metric: how many users have a film in their history."""
        counter: Counter = Counter()
        for user in self.users.values():
            for mid in user.history:
                counter[mid] += 1
        movie_by_id = {m.movie_id: m for m in self.movies}
        ranked = []
        for mid, count in counter.most_common(top_n):
            if mid in movie_by_id:
                ranked.append((movie_by_id[mid], count))
        return ranked

    def search(self, query: str) -> List[Movie]:
        """Case-insensitive search across title and genres."""
        q = query.strip().lower()
        if not q:
            return []
        results = []
        for movie in self.movies:
            haystack = (movie.title + " " + " ".join(movie.genres)).lower()
            if q in haystack:
                results.append(movie)
        return results


# ===========================================================================
# Admin
# ===========================================================================
class Admin:
    """Privileged catalogue management, gated by a unique admin key."""

    def __init__(self, admin_key: str) -> None:
        self.admin_key = admin_key          # attribute 1: secret access key
        self.actions_log: List[str] = []    # attribute 2: audit trail

    def authenticate(self, key: str) -> bool:
        """method: verify the supplied key matches the admin key."""
        return key == self.admin_key

    def add_movie(self, movies: List[Movie], title: str, genres: List[str],
                  year: int, description: str = "") -> Movie:
        new_id = max((m.movie_id for m in movies), default=0) + 1
        movie = Movie(new_id, title, genres, year, description)
        movies.append(movie)
        self.actions_log.append(f"Added movie #{new_id}: {title}")
        return movie

    def edit_movie(self, movie: Movie, title: str, genres: List[str],
                   year: int, description: str = "") -> None:
        movie.title = title
        movie.genres = genres
        movie.year = year
        movie.description = description
        self.actions_log.append(f"Edited movie #{movie.movie_id}: {title}")

    def remove_movie(self, movies: List[Movie], movie_id: int) -> bool:
        for i, movie in enumerate(movies):
            if movie.movie_id == movie_id:
                movies.pop(i)
                self.actions_log.append(f"Removed movie #{movie_id}")
                return True
        return False
