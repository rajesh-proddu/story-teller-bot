"""
Content-safety guardrail for Story Teller Bot (kids aged 5-8).
Layer 1: fast keyword/regex blocklist. Layer 2: optional toxic-bert classifier.
"""
from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

from config.settings import settings  # noqa: F401  (kept for project-convention parity)


# ---------------------------------------------------------------------------
# Keyword blocklists. Module-level so they're easy to audit / extend.
# Keep each list to roughly 10-20 terms. Multi-word phrases are matched as
# literal phrases (case-insensitive); single tokens use \b...\b boundaries.
# ---------------------------------------------------------------------------

VIOLENCE_TERMS: list[str] = [
    "kill",
    "killed",
    "killing",
    "murder",
    "murdered",
    "blood",
    "bloody",
    "gun",
    "guns",
    "weapon",
    "stab",
    "stabbed",
    "shoot",
    "shot dead",
    "torture",
    "dead body",
    "corpse",
    "behead",
    "slaughter",
    "massacre",
]

SEXUAL_TERMS: list[str] = [
    "sex",
    "sexual",
    "porn",
    "pornography",
    "nude",
    "naked",
    "rape",
    "raped",
    "molest",
    "molested",
    "penis",
    "vagina",
    "boobs",
    "breasts",
    "erotic",
    "horny",
    "orgasm",
]

SUBSTANCE_TERMS: list[str] = [
    "drug",
    "drugs",
    "cocaine",
    "heroin",
    "meth",
    "methamphetamine",
    "weed",
    "marijuana",
    "crack",
    "ecstasy",
    "lsd",
    "alcohol abuse",
    "drunk",
    "drunken",
    "overdose",
    "smoking crack",
    "shoot up",
]

HATE_TERMS: list[str] = [
    # Project-approved slur/hate terms. Extend with care.
    "nigger",
    "nigga",
    "faggot",
    "retard",
    "retarded",
    "chink",
    "spic",
    "kike",
    "tranny",
    "dyke",
    "white power",
    "kill all",
    "hate jews",
    "hate blacks",
    "hate muslims",
    "hate gays",
]

SELF_HARM_TERMS: list[str] = [
    "suicide",
    "kill myself",
    "kill yourself",
    "self-harm",
    "self harm",
    "cutting myself",
    "cut myself",
    "hang myself",
    "end my life",
    "want to die",
    "wanna die",
    "slit my wrist",
    "slit my wrists",
]


CATEGORIES: dict[str, list[str]] = {
    "violence": VIOLENCE_TERMS,
    "sexual": SEXUAL_TERMS,
    "substances": SUBSTANCE_TERMS,
    "hate": HATE_TERMS,
    "self_harm": SELF_HARM_TERMS,
}


def _compile_patterns(terms: list[str]) -> list[re.Pattern[str]]:
    """Compile each term as a case-insensitive word-boundary regex."""
    patterns: list[re.Pattern[str]] = []
    for term in terms:
        if " " in term or "-" in term:
            # Multi-word/hyphenated phrase: allow flexible whitespace/hyphenation.
            escaped = re.escape(term).replace(r"\ ", r"\s+").replace(r"\-", r"[-\s]")
            patterns.append(re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE))
        else:
            patterns.append(re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE))
    return patterns


_COMPILED: dict[str, list[re.Pattern[str]]] = {
    cat: _compile_patterns(terms) for cat, terms in CATEGORIES.items()
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class SafetyResult:
    """Outcome of a safety check."""

    is_safe: bool
    categories: list[str] = field(default_factory=list)
    reason: str = ""
    classifier_score: Optional[float] = None


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


_PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation})


def sanitize_for_kids(text: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace for keyword matching."""
    if not text:
        return ""
    lowered = text.lower().translate(_PUNCT_TABLE)
    return re.sub(r"\s+", " ", lowered).strip()


def _scan_keywords(text: str) -> list[str]:
    """Return the categories whose patterns match the given text."""
    hits: list[str] = []
    for category, patterns in _COMPILED.items():
        for pattern in patterns:
            if pattern.search(text):
                hits.append(category)
                break  # one hit per category is sufficient
    return hits


# ---------------------------------------------------------------------------
# SafetyFilter
# ---------------------------------------------------------------------------


class SafetyFilter:
    """Two-layer content safety filter for kids' story bot."""

    def __init__(
        self,
        enable_classifier: bool = False,
        toxicity_threshold: float = 0.7,
    ) -> None:
        """Configure the filter; classifier model is lazy-loaded on first use."""
        self.enable_classifier = enable_classifier
        self.toxicity_threshold = toxicity_threshold
        self._classifier = None  # transformers pipeline, lazy
        self._classifier_failed = False
        logger.info(
            f"SafetyFilter initialized (classifier={'on' if enable_classifier else 'off'}, "
            f"threshold={toxicity_threshold})"
        )

    # -- classifier plumbing ------------------------------------------------

    def _get_classifier(self):
        """Lazily build the toxic-bert pipeline; cache failures so we don't retry."""
        if self._classifier is not None or self._classifier_failed:
            return self._classifier
        try:
            from transformers import pipeline  # local import keeps cold-path cheap

            logger.info("Loading toxic-bert classifier (unitary/toxic-bert)...")
            self._classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                top_k=None,
            )
            logger.info("toxic-bert classifier loaded.")
        except Exception as e:  # pragma: no cover - depends on env
            logger.warning(f"Could not load toxic-bert; falling back to keyword-only: {e}")
            self._classifier = None
            self._classifier_failed = True
        return self._classifier

    def _classifier_score(self, text: str) -> Optional[float]:
        """Run toxic-bert and return the max toxicity score across labels, or None."""
        if not self.enable_classifier:
            return None
        clf = self._get_classifier()
        if clf is None:
            return None
        try:
            raw = clf(text[:512])  # truncate to BERT's 512-token window
            scores: list[float] = []
            # Output may be [[{label,score},...]] or [{label,score},...].
            if raw and isinstance(raw[0], list):
                for entry in raw[0]:
                    scores.append(float(entry.get("score", 0.0)))
            else:
                for entry in raw:
                    scores.append(float(entry.get("score", 0.0)))
            return max(scores) if scores else None
        except Exception as e:
            logger.warning(f"Classifier inference failed: {e}")
            return None

    # -- public API ---------------------------------------------------------

    def check_input(self, text: str) -> SafetyResult:
        """Strict check for user input; any keyword hit fails."""
        if not text or not text.strip():
            return SafetyResult(is_safe=True, reason="empty input")

        normalized = sanitize_for_kids(text)
        categories = _scan_keywords(normalized)

        if categories:
            reason = f"Input blocked: matched categories {categories}"
            logger.warning(reason)
            return SafetyResult(is_safe=False, categories=categories, reason=reason)

        score = self._classifier_score(text)
        if score is not None and score >= self.toxicity_threshold:
            reason = f"Input blocked by classifier (score={score:.2f})"
            logger.warning(reason)
            return SafetyResult(
                is_safe=False,
                categories=["classifier"],
                reason=reason,
                classifier_score=score,
            )

        return SafetyResult(is_safe=True, reason="input passed", classifier_score=score)

    def check_output(self, text: str) -> SafetyResult:
        """Check for generated stories; case-insensitive but non-destructive on text."""
        # Slightly more permissive than check_input: we do NOT strip/normalize the
        # story text (so it stays readable for TTS). Keyword patterns are already
        # case-insensitive, and classifier-on-raw-text handles natural prose well.
        if not text or not text.strip():
            return SafetyResult(is_safe=True, reason="empty output")

        categories = _scan_keywords(text)

        if categories:
            reason = f"Output blocked: matched categories {categories}"
            logger.warning(reason)
            return SafetyResult(is_safe=False, categories=categories, reason=reason)

        score = self._classifier_score(text)
        if score is not None and score >= self.toxicity_threshold:
            reason = f"Output blocked by classifier (score={score:.2f})"
            logger.warning(reason)
            return SafetyResult(
                is_safe=False,
                categories=["classifier"],
                reason=reason,
                classifier_score=score,
            )

        return SafetyResult(is_safe=True, reason="output passed", classifier_score=score)
