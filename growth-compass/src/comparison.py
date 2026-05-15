"""Comparison Engine - compares self-claimed skills against AI-discovered evidence.

Pipeline: normalize → bucket by domain → fuzzy match → categorize → rank insights.
Output: Confirmed (matched), Revealed (AI-found, not claimed), Aspirational (claimed, no evidence).
"""

import re
from dataclasses import dataclass, field

from .models import SkillEvidence, Confidence, SkillLevel
from .knowledge import list_all_skills
from .i18n import _


@dataclass
class ComparisonResult:
    confirmed: list[dict] = field(default_factory=list)
    revealed: list[dict] = field(default_factory=list)
    aspirational: list[dict] = field(default_factory=list)
    summary: str = ""


class ComparisonEngine:
    """Compares what a user says about themselves against what their journal shows."""

    def __init__(self, llm_client=None):
        self.llm = llm_client
        self._taxonomy_skills = {s["id"]: s for s in list_all_skills()}
        self._keyword_index = self._build_keyword_index()

    # ── Public API ────────────────────────────────────────────

    def compare(
        self,
        self_claimed: list[str],
        ai_discovered: dict[str, SkillEvidence],
    ) -> ComparisonResult:
        """Run the full comparison pipeline.

        Args:
            self_claimed: Free-text labels the user says they're good at.
            ai_discovered: SkillEvidence map from SkillGraphEngine.build_map().

        Returns:
            ComparisonResult with confirmed, revealed, aspirational lists.
        """
        if not self_claimed and not ai_discovered:
            return ComparisonResult(summary=_("cmp_no_data"))

        normalized_self = [self._normalize_label(label) for label in self_claimed]

        matches = []
        unmatched_ai = []

        for skill_id, evidence in ai_discovered.items():
            if evidence.entry_count == 0:
                continue

            ai_label = evidence.skill_label.lower()
            ai_tokens = self._tokenize(ai_label)
            best_score = 0.0
            best_self_idx = -1

            for i, self_tokens in enumerate(normalized_self):
                if self_tokens is None:
                    continue
                score = self._jaccard(ai_tokens, self_tokens)
                if score > best_score:
                    best_score = score
                    best_self_idx = i

            if best_score >= 0.4 and best_self_idx >= 0:
                matches.append((skill_id, best_self_idx, best_score))
                normalized_self[best_self_idx] = None  # Consume
            else:
                unmatched_ai.append(skill_id)

        unmatched_self = [
            self_claimed[i]
            for i, tokens in enumerate(normalized_self)
            if tokens is not None
        ]

        confirmed, revealed, aspirational = self._categorize(
            matches, unmatched_ai, unmatched_self, ai_discovered
        )

        return ComparisonResult(
            confirmed=confirmed,
            revealed=revealed,
            aspirational=aspirational,
            summary=self._generate_summary(confirmed, revealed, aspirational),
        )

    # ── Normalization ─────────────────────────────────────────

    def _normalize_label(self, label: str) -> set[str]:
        """Expand a free-text self-claimed label into an enriched token set."""
        base = self._tokenize(label)
        base.update(self._expand_keywords(label))
        return base

    def _tokenize(self, text: str) -> set[str]:
        """Tokenize text into normalized word tokens."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = set()
        for token in text.split():
            if len(token) > 1:
                tokens.add(token)
        return tokens

    def _jaccard(self, set1: set[str], set2: set[str]) -> float:
        """Jaccard similarity between two token sets."""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union

    # ── Keyword Index ─────────────────────────────────────────

    def _build_keyword_index(self) -> dict[str, set[str]]:
        """Build a keyword → domain mapping from the taxonomy for heuristic matching."""
        index: dict[str, set[str]] = {}
        for skill_id, skill_info in self._taxonomy_skills.items():
            label = skill_info.get("label", "")
            description = skill_info.get("description", "")
            domain = skill_info.get("domain", "")

            all_tokens = self._tokenize(f"{label} {description} {domain}")
            for token in all_tokens:
                if token not in index:
                    index[token] = set()
                index[token].add(skill_id)
        return index

    def _expand_keywords(self, text: str) -> set[str]:
        """Find taxonomy skill IDs whose keywords overlap with the given text."""
        tokens = self._tokenize(text)
        skill_hits: dict[str, int] = {}
        for token in tokens:
            if token in self._keyword_index:
                for skill_id in self._keyword_index[token]:
                    skill_hits[skill_id] = skill_hits.get(skill_id, 0) + 1

        expanded = set()
        for skill_id, count in skill_hits.items():
            if count >= 1:
                info = self._taxonomy_skills.get(skill_id, {})
                label = info.get("label", "")
                expanded.update(self._tokenize(label))
        return expanded

    # ── Categorization ────────────────────────────────────────

    def _categorize(
        self,
        matches: list[tuple[str, int, float]],
        unmatched_ai: list[str],
        unmatched_self: list[str],
        ai_discovered: dict[str, SkillEvidence],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """Assign skills to Confirmed, Revealed, or Aspirational."""

        confirmed = []
        for skill_id, self_idx, score in matches:
            evidence = ai_discovered.get(skill_id)
            confirmed.append({
                "skill_id": skill_id,
                "skill_label": evidence.skill_label if evidence else skill_id,
                "level": evidence.level.value if evidence else "unknown",
                "confidence": evidence.confidence.value if evidence else "unknown",
                "entries": evidence.entry_count if evidence else 0,
                "match_score": round(score, 2),
                "category": "Confirmed",
                "insight": (
                    _("cmp_confirmed_insight", count=evidence.entry_count,
                      level=evidence.level.value.lower())
                ) if evidence else "",
            })

        revealed = []
        for skill_id in unmatched_ai:
            evidence = ai_discovered.get(skill_id)
            if not evidence or evidence.entry_count == 0:
                continue
            revealed.append({
                "skill_id": skill_id,
                "skill_label": evidence.skill_label,
                "level": evidence.level.value,
                "confidence": evidence.confidence.value,
                "entries": evidence.entry_count,
                "category": "Revealed",
                "insight": _(
                    "cmp_revealed_insight",
                    count=evidence.entry_count,
                    level=evidence.level.value.lower(),
                    skill=evidence.skill_label,
                    confidence=evidence.confidence.value.lower(),
                ),
            })

        aspirational = []
        for label in unmatched_self:
            aspirational.append({
                "skill_label": label,
                "category": "Aspirational",
                "insight": _("cmp_aspirational_insight", skill=label),
            })

        return confirmed, revealed, aspirational

    # ── Ranking ───────────────────────────────────────────────

    def rank_insights(self, revealed: list[dict]) -> list[dict]:
        """Rank revealed skills by evidence strength (entries × confidence)."""
        confidence_weight = {"high": 3, "medium": 2, "low": 1}

        def rank_key(r: dict) -> int:
            entries = r.get("entries", 0)
            conf = r.get("confidence", "low").lower()
            return entries * confidence_weight.get(conf, 1)

        return sorted(revealed, key=rank_key, reverse=True)

    # ── Summary ───────────────────────────────────────────────

    def _generate_summary(
        self,
        confirmed: list[dict],
        revealed: list[dict],
        aspirational: list[dict],
    ) -> str:
        parts = []

        if revealed:
            top = revealed[0]
            parts.append(_("cmp_revealed_lead", skill=top['skill_label']))

        if confirmed:
            parts.append(_("cmp_confirmed_summary", count=len(confirmed)))

        if aspirational:
            parts.append(_("cmp_aspirational_summary", count=len(aspirational)))

        if not parts:
            return _("cmp_no_patterns")

        return " ".join(parts)
