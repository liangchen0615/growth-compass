"""Skill Graph Engine — aggregates entries into a skill map with levels and patterns.

Uses LLM for assessment and pattern detection when available, falling back to heuristics.
"""

from collections import defaultdict
from datetime import date
from typing import TYPE_CHECKING

from .models import (
    GrowthEntry, SkillEvidence, SkillMap, SkillLevel, Confidence, Significance,
)
from .journal import GrowthJournal
from .knowledge import list_all_skills, skill_level_order

if TYPE_CHECKING:
    from .llm import LLMClient


def _assess_level(evidence: SkillEvidence) -> SkillLevel:
    """Assess skill level based on evidence patterns (heuristic fallback)."""
    stretch = evidence.stretch_count
    total = evidence.entry_count

    if total == 0:
        return SkillLevel.AWARE

    contexts = set(e.context[:50] for e in evidence.entries if e.context)

    if stretch >= 5 and len(contexts) >= 3:
        return SkillLevel.PROFICIENT
    elif stretch >= 3 and len(contexts) >= 2:
        return SkillLevel.CAPABLE
    elif stretch >= 1:
        return SkillLevel.PRACTICING
    elif total >= 2:
        return SkillLevel.PRACTICING
    else:
        return SkillLevel.AWARE


def _assess_confidence(evidence: SkillEvidence) -> Confidence:
    """Assess confidence based on evidence density and variety (heuristic fallback)."""
    total = evidence.entry_count
    contexts = set(e.context[:50] for e in evidence.entries if e.context)
    has_feedback = any(
        e.category.value == "Feedback" for e in evidence.entries
    )

    if total >= 5 and len(contexts) >= 3 and has_feedback:
        return Confidence.HIGH
    elif total >= 3 and len(contexts) >= 2:
        return Confidence.MEDIUM
    else:
        return Confidence.LOW


def _detect_trend(entries: list[GrowthEntry]) -> str:
    """Detect trajectory trend from recent entries (heuristic fallback)."""
    if len(entries) < 2:
        return "stable"
    recent = sorted(entries, key=lambda e: e.date)
    recent_levels = []
    for e in recent:
        if e.significance == Significance.STRETCH:
            recent_levels.append(2)
        elif e.significance == Significance.PRACTICE:
            recent_levels.append(1)
        else:
            recent_levels.append(0)
    if len(recent_levels) < 2:
        return "stable"
    first_half = sum(recent_levels[:len(recent_levels)//2])
    second_half = sum(recent_levels[len(recent_levels)//2:])
    if second_half > first_half:
        return "rising"
    elif second_half < first_half:
        return "declining"
    return "stable"


class SkillGraphEngine:
    """Builds and queries skill maps from growth entries."""

    def __init__(self, journal: GrowthJournal, llm_client: "LLMClient | None" = None):
        self.journal = journal
        self.llm = llm_client

    def _cluster_entries(self) -> dict[str, list[GrowthEntry]]:
        """Cluster journal entries by skill (primary and secondary tags)."""
        skill_entries: dict[str, list[GrowthEntry]] = defaultdict(list)
        for entry in self.journal.entries:
            skill_entries[entry.primary_skill].append(entry)
            for sid in entry.secondary_skills:
                skill_entries[sid].append(entry)
        return skill_entries

    def _llm_assess_skill_evidence(
        self,
        skill_id: str,
        skill_info: dict,
        entries: list[GrowthEntry],
    ) -> SkillEvidence | None:
        """Use LLM to assess level, confidence, and trend for one skill."""
        if not self.llm or not self.llm.available:
            return None

        assessment = self.llm.assess_skill(
            {"id": skill_id, **skill_info},
            entries,
        )
        if assessment is None:
            return None

        try:
            level = SkillLevel(assessment.level.title())
        except (ValueError, KeyError):
            level = SkillLevel.AWARE
        try:
            confidence = Confidence(assessment.confidence.title())
        except (ValueError, KeyError):
            confidence = Confidence.LOW

        return SkillEvidence(
            skill_id=skill_id,
            skill_label=skill_info["label"],
            entries=entries,
            level=level,
            confidence=confidence,
            trend=assessment.trend if assessment.trend in ("rising", "stable", "declining") else "stable",
        )

    def _llm_identify_patterns_and_superpower(
        self,
        evidence_map: dict[str, SkillEvidence],
    ) -> tuple[list[str], list[str], list[str], list[str], str, str] | None:
        """Use LLM for cross-skill pattern analysis."""
        if not self.llm or not self.llm.available:
            return None

        all_skill_info = {s["id"]: s for s in list_all_skills()}
        analysis = self.llm.identify_patterns(
            evidence_map, all_skill_info, ""
        )
        if analysis is None:
            return None

        return (
            analysis.strengths,
            analysis.growth_edges,
            analysis.blind_spots,
            analysis.plateaus,
            analysis.superpower,
            analysis.pattern_notes,
        )

    def build_map(self, user_name: str = "") -> SkillMap:
        """Build a full skill map from all journal entries.

        Uses LLM for assessment and pattern detection when available,
        falling back to heuristics on failure or unavailability.
        """
        all_skills = {s["id"]: s for s in list_all_skills()}
        skill_entries = self._cluster_entries()

        # Phase 1: Per-skill assessment (LLM first, heuristic fallback)
        evidence_map: dict[str, SkillEvidence] = {}
        for skill_id, info in all_skills.items():
            entries = skill_entries.get(skill_id, [])

            # Try LLM assessment
            llm_evidence = self._llm_assess_skill_evidence(skill_id, info, entries)
            if llm_evidence is not None:
                evidence_map[skill_id] = llm_evidence
                continue

            # Heuristic fallback
            evidence = SkillEvidence(
                skill_id=skill_id,
                skill_label=info["label"],
                entries=entries,
                trend=_detect_trend(entries),
            )
            evidence.level = _assess_level(evidence)
            evidence.confidence = _assess_confidence(evidence)
            evidence_map[skill_id] = evidence

        # Phase 2: Cross-skill pattern detection (LLM first, heuristic fallback)
        llm_result = self._llm_identify_patterns_and_superpower(evidence_map)
        if llm_result:
            strengths, growth_edges, blind_spots, plateaus, superpower, pattern_notes = llm_result
        else:
            strengths, growth_edges, blind_spots, plateaus = self._find_patterns(evidence_map)
            superpower = self._detect_superpower(evidence_map)
            pattern_notes = self._generate_pattern_notes(evidence_map)

        return SkillMap(
            user_name=user_name,
            generated_date=date.today(),
            entries_analyzed=len(self.journal.entries),
            skills=evidence_map,
            strengths=strengths,
            growth_edges=growth_edges,
            blind_spots=blind_spots,
            plateaus=plateaus,
            superpower=superpower,
            pattern_notes=pattern_notes,
        )

    def _find_patterns(
        self, evidence_map: dict[str, SkillEvidence]
    ) -> tuple[list[str], list[str], list[str], list[str]]:
        """Identify strengths, growth edges, blind spots, and plateaus (heuristic)."""
        strengths = []
        growth_edges = []
        blind_spots = []
        plateaus = []

        for skill_id, ev in evidence_map.items():
            level_order = skill_level_order(ev.level.value)
            if level_order >= 2 and ev.confidence in (Confidence.MEDIUM, Confidence.HIGH):
                strengths.append(skill_id)
            elif ev.trend == "rising" and level_order >= 1:
                growth_edges.append(skill_id)
            elif ev.entry_count >= 3 and ev.trend in ("stable", "declining"):
                if level_order < 3:
                    plateaus.append(skill_id)
            elif ev.entry_count == 0:
                blind_spots.append(skill_id)

        return strengths, growth_edges, blind_spots, plateaus

    def _detect_superpower(self, evidence_map: dict[str, SkillEvidence]) -> str:
        """Find the strongest, most distinctive skill combination (heuristic)."""
        pairs = defaultdict(int)
        for entry in self.journal.entries:
            skills = [entry.primary_skill] + list(entry.secondary_skills)
            for i, s1 in enumerate(skills):
                for s2 in skills[i + 1:]:
                    key = tuple(sorted([s1, s2]))
                    pairs[key] += 1
        if not pairs:
            top_pair = ("unknown", "unknown")
        else:
            top_pair = max(pairs, key=pairs.get)

        s1 = evidence_map.get(top_pair[0], None)
        s2 = evidence_map.get(top_pair[1], None)
        label1 = s1.skill_label if s1 else top_pair[0]
        label2 = s2.skill_label if s2 else top_pair[1]
        return f"{label1} x {label2}"

    def _generate_pattern_notes(self, evidence_map: dict[str, SkillEvidence]) -> str:
        """Generate human-readable pattern observations (heuristic)."""
        if not self.journal.entries:
            return "No entries yet — start capturing growth moments to reveal patterns."

        stretch = sum(1 for e in self.journal.entries
                      if e.significance == Significance.STRETCH)
        total = len(self.journal.entries)

        stretch_ratio = stretch / total if total > 0 else 0
        if stretch_ratio > 0.5:
            rhythm = "You're regularly operating at your edge — high stretch ratio suggests rapid growth."
        elif stretch_ratio > 0.2:
            rhythm = "Steady mix of stretch and practice. Sustainable growth rhythm."
        else:
            rhythm = "Mostly practice and exposure. Consider seeking more stretch assignments."

        struggling = sum(1 for e in self.journal.entries
                        if e.category.value == "Struggle")
        if struggling > 0:
            rhythm += f" {struggling} entries frame difficulties as learning — that's a strong growth signal."

        return rhythm

    def compare(self, previous: SkillMap, current: SkillMap) -> list[dict]:
        """Compare two skill maps and return what changed."""
        changes = []
        for skill_id, current_ev in current.skills.items():
            prev_ev = previous.skills.get(skill_id)
            if prev_ev and prev_ev.level != current_ev.level:
                changes.append({
                    "skill_id": skill_id,
                    "skill_label": current_ev.skill_label,
                    "from_level": prev_ev.level.value,
                    "to_level": current_ev.level.value,
                    "change_desc": f"{current_ev.skill_label}: {prev_ev.level.value} -> {current_ev.level.value}",
                })
        return changes
