import os
from dotenv import load_dotenv

load_dotenv()

# OAuth 2.0 credentials
CLIENT_ID = os.getenv("X_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("X_CLIENT_SECRET", "")
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
REFRESH_TOKEN = os.getenv("X_REFRESH_TOKEN", "")

# OAuth 1.0a credentials
CONSUMER_KEY = os.getenv("X_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET", "")
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET", "")

# ─────────────
# Project Settings
# ─────────────

LABELS = ["Positive", "Negative", "Neutral", "Irrelevant"]

DEFAULT_QUERY = "layanan bank kecewa"
DEFAULT_LIMIT = 10
MAX_RESULTS_PER_PAGE = 100

# ────────────────────────
# Indonesian Slang Dictionary
# ────────────────────────

SLANG_DICT = {
    # Negasi
    "gak": "tidak", "ga": "tidak", "gk": "tidak", "nggak": "tidak",
    "ngga": "tidak", "enggak": "tidak",
    # Kata umum
    "bgt": "banget", "bngt": "banget",
    "mending": "lebih baik",
    "parah": "sangat buruk",
    "gila": "luar biasa",
    "satset": "cepat",
    "dahlah": "menyerah",
    "gercep": "gerak cepat",
    "ngab": "bang",
    "fomo": "takut tertinggal",
    "sdh": "sudah", "udh": "sudah", "udah": "sudah",
    "utk": "untuk", "tuk": "untuk",
    "yg": "yang", "dgn": "dengan", "dlm": "dalam",
    "org": "orang", "krn": "karena", "karna": "karena",
    "sm": "sama", "sama": "sama",
    "tp": "tapi", "ttg": "tentang",
    "hrs": "harus", "blm": "belum", "sdg": "sedang",
    "dr": "dari", "pd": "pada", "spy": "supaya",
    "jd": "jadi", "jgn": "jangan", "bs": "bisa",
    "lg": "lagi", "lsg": "langsung",
    "sy": "saya", "ak": "aku", "gw": "saya", "gue": "saya",
    "lo": "kamu", "lu": "kamu", "km": "kamu",
    "kpd": "kepada", "dpt": "dapat",
    "brp": "berapa", "gmn": "gimana", "gimana": "bagaimana",
    "anj": "umpatan", "anjir": "umpatan", "babi": "umpatan",
}

# ──────────────
# Sarcasm Detection
# ──────────────

SARCASM_INDICATORS = [
    "terserah", "keren banget ya", "makasih lho", "hebat bener",
    "pinter banget", "luar biasa ya", "top banget lah", "mantap sekali",
    "bagus banget sih", "wah keren", "amazing banget", "super sekali",
]

CONTRADICTION_WORDS = ["tapi", "kok", "padahal", "namun", "eh tapi", "tapi kok"]

# ───────────────────
# Web Scraper Selectors
# ───────────────────

TWEET_SELECTOR = 'article[data-testid="tweet"]'
TEXT_SELECTOR = '[data-testid="tweetText"]'
