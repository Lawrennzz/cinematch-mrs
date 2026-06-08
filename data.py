"""
data.py
-------
Seed dataset and persistence helpers for the Movie Recommendation System (MRS).

The dataset is intentionally lightweight (no external database) so the
application runs out-of-the-box on Streamlit Community Cloud. All runtime state
is persisted to a JSON file so that ratings/history survive page reloads during
a single deployment session.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# File locations
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORE_PATH = os.path.join(BASE_DIR, "mrs_store.json")

# Unique key required to access the administrative console (Task 2.3).
ADMIN_KEY = "ADMIN-2026-MRS"


# ---------------------------------------------------------------------------
# Seed catalogue of movies
# ---------------------------------------------------------------------------
SEED_MOVIES: List[Dict[str, Any]] = [
    {"movie_id": 1,  "title": "Inception",                 "genres": ["Sci-Fi", "Thriller"],      "year": 2010, "description": "A thief who steals corporate secrets through dream-sharing technology."},
    {"movie_id": 2,  "title": "The Dark Knight",           "genres": ["Action", "Crime", "Drama"], "year": 2008, "description": "Batman faces the Joker, a criminal mastermind plunging Gotham into chaos."},
    {"movie_id": 3,  "title": "Interstellar",              "genres": ["Sci-Fi", "Adventure", "Drama"], "year": 2014, "description": "Explorers travel through a wormhole in space to ensure humanity's survival."},
    {"movie_id": 4,  "title": "The Shawshank Redemption",  "genres": ["Drama"],                    "year": 1994, "description": "Two imprisoned men bond over years, finding solace and redemption."},
    {"movie_id": 5,  "title": "Pulp Fiction",              "genres": ["Crime", "Drama"],           "year": 1994, "description": "The lives of two mob hitmen, a boxer and others intertwine in violence."},
    {"movie_id": 6,  "title": "The Matrix",                "genres": ["Sci-Fi", "Action"],         "year": 1999, "description": "A hacker discovers reality is a simulation controlled by machines."},
    {"movie_id": 7,  "title": "Forrest Gump",              "genres": ["Drama", "Romance"],         "year": 1994, "description": "The decades-long story of a slow-witted but kind-hearted man."},
    {"movie_id": 8,  "title": "The Godfather",             "genres": ["Crime", "Drama"],           "year": 1972, "description": "The aging patriarch of a crime dynasty transfers control to his son."},
    {"movie_id": 9,  "title": "Toy Story",                 "genres": ["Animation", "Family", "Comedy"], "year": 1995, "description": "A cowboy doll is threatened by a new spaceman figure."},
    {"movie_id": 10, "title": "Finding Nemo",              "genres": ["Animation", "Family", "Adventure"], "year": 2003, "description": "A clownfish searches the ocean for his abducted son."},
    {"movie_id": 11, "title": "The Avengers",              "genres": ["Action", "Sci-Fi", "Adventure"], "year": 2012, "description": "Earth's mightiest heroes unite to stop Loki and his alien army."},
    {"movie_id": 12, "title": "Gladiator",                 "genres": ["Action", "Drama", "Adventure"], "year": 2000, "description": "A betrayed Roman general seeks revenge as a gladiator."},
    {"movie_id": 13, "title": "Titanic",                   "genres": ["Romance", "Drama"],         "year": 1997, "description": "A romance blossoms aboard the ill-fated maiden voyage of the Titanic."},
    {"movie_id": 14, "title": "The Lion King",             "genres": ["Animation", "Family", "Drama"], "year": 1994, "description": "A lion cub flees after his father's death and later reclaims his kingdom."},
    {"movie_id": 15, "title": "Joker",                     "genres": ["Crime", "Drama", "Thriller"], "year": 2019, "description": "A failed comedian descends into madness and becomes a criminal icon."},
    {"movie_id": 16, "title": "Parasite",                  "genres": ["Thriller", "Drama", "Comedy"], "year": 2019, "description": "A poor family schemes to become employed by a wealthy household."},
    {"movie_id": 17, "title": "Avatar",                    "genres": ["Sci-Fi", "Adventure", "Action"], "year": 2009, "description": "A marine on an alien planet becomes torn between orders and a new world."},
    {"movie_id": 18, "title": "The Conjuring",             "genres": ["Horror", "Thriller"],       "year": 2013, "description": "Paranormal investigators help a family terrorised by a dark presence."},
    {"movie_id": 19, "title": "Get Out",                   "genres": ["Horror", "Thriller", "Mystery"], "year": 2017, "description": "A young man uncovers a disturbing secret on a visit to his girlfriend's family."},
    {"movie_id": 20, "title": "La La Land",                "genres": ["Romance", "Musical", "Drama"], "year": 2016, "description": "A jazz musician and an aspiring actress fall in love in Los Angeles."},
    {"movie_id": 21, "title": "Whiplash",                  "genres": ["Drama", "Musical"],         "year": 2014, "description": "A young drummer is pushed to his limits by an abusive instructor."},
    {"movie_id": 22, "title": "Mad Max: Fury Road",        "genres": ["Action", "Adventure", "Sci-Fi"], "year": 2015, "description": "On a post-apocalyptic Earth, a woman rebels against a tyrannical ruler."},
    {"movie_id": 23, "title": "The Grand Budapest Hotel",  "genres": ["Comedy", "Drama"],          "year": 2014, "description": "A concierge and his protege become embroiled in a theft and family fortune."},
    {"movie_id": 24, "title": "Spirited Away",             "genres": ["Animation", "Adventure", "Family"], "year": 2001, "description": "A girl wanders into a world of spirits and must free her parents."},
    {"movie_id": 25, "title": "Django Unchained",          "genres": ["Western", "Drama", "Action"], "year": 2012, "description": "A freed slave sets out to rescue his wife from a brutal plantation owner."},
    {"movie_id": 26, "title": "The Notebook",              "genres": ["Romance", "Drama"],         "year": 2004, "description": "A poor man and a rich woman fall in love in the 1940s."},
    {"movie_id": 27, "title": "It",                        "genres": ["Horror", "Thriller"],       "year": 2017, "description": "Children confront a shape-shifting entity that preys on their fears."},
    {"movie_id": 28, "title": "Frozen",                    "genres": ["Animation", "Family", "Musical"], "year": 2013, "description": "A fearless princess sets off to find her estranged, ice-powered sister."},
    {"movie_id": 29, "title": "Dune",                      "genres": ["Sci-Fi", "Adventure", "Drama"], "year": 2021, "description": "A noble family becomes embroiled in a war over a desert planet's resource."},
    {"movie_id": 30, "title": "Knives Out",                "genres": ["Mystery", "Comedy", "Crime"], "year": 2019, "description": "A detective investigates the death of a wealthy crime novelist."},
]


# ---------------------------------------------------------------------------
# Demo users + some seed ratings so recommendations work on first launch
# ---------------------------------------------------------------------------
SEED_USERS: Dict[str, Dict[str, Any]] = {
    "alice": {
        "username": "alice",
        "password": "alice123",
        "ratings": {"1": 5, "3": 5, "6": 4, "11": 4, "17": 5},
        "history": [1, 3, 6, 11, 17],
    },
    "bob": {
        "username": "bob",
        "password": "bob123",
        "ratings": {"4": 5, "8": 5, "5": 4, "15": 4, "16": 5},
        "history": [4, 8, 5, 15, 16],
    },
    "carol": {
        "username": "carol",
        "password": "carol123",
        "ratings": {"9": 5, "10": 5, "14": 4, "24": 5, "28": 4},
        "history": [9, 10, 14, 24, 28],
    },
}


def default_store() -> Dict[str, Any]:
    """Return a fresh data store seeded with movies and demo users."""
    return {
        "movies": [dict(m) for m in SEED_MOVIES],
        "users": {k: dict(v) for k, v in SEED_USERS.items()},
    }


def load_store() -> Dict[str, Any]:
    """Load the JSON store from disk, creating it from seed data if missing."""
    if not os.path.exists(STORE_PATH):
        store = default_store()
        save_store(store)
        return store
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        # Corrupted file -> reset to defaults.
        store = default_store()
        save_store(store)
        return store


def save_store(store: Dict[str, Any]) -> None:
    """Persist the data store to disk."""
    with open(STORE_PATH, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)
