import re
from src.utils.config import SLANG_DICT

# Pre-compiled regex patterns for performance
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#(\w+)")       # keep the word, drop the #
_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")

# Emoji / non-ASCII range (optional strip)
_EMOJI_RE = re.compile(
    "[\U00010000-\U0010ffff]",
    flags=re.UNICODE,
)

class TextCleaner:
    """
    Cleans raw tweet text in a pipeline:
      1. basic_clean  — lowercase, remove URLs / mentions / punctuation
      2. replace_slang — normalise Indonesian slang words
    """

    @staticmethod
    def basic_clean(text: str, keep_hashtag_words: bool = True) -> str:
        """
        Lowercase and strip noise from a tweet.

        Parameters
        ----------
        text : str
            Raw tweet text.
        keep_hashtag_words : bool
            If True, '#kecewa' becomes 'kecewa'. If False, the whole token is removed.
        """
        if not text:
            return ""

        text = text.lower()
        text = _URL_RE.sub(" ", text)
        text = _MENTION_RE.sub(" ", text)

        if keep_hashtag_words:
            text = _HASHTAG_RE.sub(r"\1", text)   # '#kecewa' → 'kecewa'
        else:
            text = _HASHTAG_RE.sub(" ", text)

        text = _EMOJI_RE.sub(" ", text)
        text = _PUNCTUATION_RE.sub(" ", text)
        text = _WHITESPACE_RE.sub(" ", text)
        return text.strip()

    @staticmethod
    def replace_slang(text: str) -> str:
        """
        Replace Indonesian slang/abbreviations with their formal equivalents.

        Only replaces whole words (avoids partial matches).
        """
        if not text:
            return ""
        words = text.split()
        return " ".join(SLANG_DICT.get(w, w) for w in words)

    def clean(self, text: str) -> str:
        """Convenience: run the full pipeline (basic_clean → replace_slang)."""
        return self.replace_slang(self.basic_clean(text))

    def detect_slang(self, text: str) -> list[str]:
        """Return a list of slang words found in the raw text."""
        words = text.lower().split()
        return [w for w in words if w in SLANG_DICT]
