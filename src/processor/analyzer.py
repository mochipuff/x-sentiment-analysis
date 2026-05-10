from src.utils.config import SARCASM_INDICATORS, CONTRADICTION_WORDS

class SentimentAnalyzer:
    """
    Lightweight rule-based analyser for Indonesian tweet sentiment signals.

    Detects:
    - Sarcasm: positive-sounding phrase + contradiction word
    - Firmness: strong emotional keywords present
    """

    FIRM_KEYWORDS = [
        "kecewa", "parah", "sampah", "puas", "mantap",
        "rekomendasi", "buruk", "marah", "kesal", "menyesal",
        "bangga", "senang", "takut", "sedih",
    ]

    def detect_sarcasm(self, text: str) -> bool:
        """
        Returns True if the text looks sarcastic.

        Logic: contains a positive-sounding indicator AND a contradiction word
        (cth: "keren banget tapi pelayanannya buruk").
        """
        text_lower = text.lower()
        has_positive = any(ind in text_lower for ind in SARCASM_INDICATORS)
        has_contradiction = any(word in text_lower for word in CONTRADICTION_WORDS)
        return has_positive and has_contradiction

    def check_is_firm(self, text: str) -> bool:
        """
        Returns True if the text contains strong emotional keywords,
        indicating a firm or emotionally charged opinion.
        """
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.FIRM_KEYWORDS)

    def analyze(self, clean_text: str) -> dict:
        """
        Run all analyses and return a results dict.

        Returns
        -------
        dict with keys:
            is_sarcasm : bool
            is_firm    : bool
        """
        return {
            "is_sarcasm": self.detect_sarcasm(clean_text),
            "is_firm": self.check_is_firm(clean_text),
        }
