"""Unit tests for the Growth Compass comparison engine."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.comparison import ComparisonEngine
from src.models import SkillEvidence, SkillLevel, Confidence


@pytest.fixture
def engine():
    return ComparisonEngine()


# ── _tokenize ────────────────────────────────────────────────

def test_tokenize_lowercase(engine):
    assert "hello" in engine._tokenize("Hello World")


def test_tokenize_strips_punctuation(engine):
    tokens = engine._tokenize("hello, world!")
    assert "," not in tokens
    assert "!" not in tokens


def test_tokenize_filters_single_char(engine):
    tokens = engine._tokenize("a b c word")
    assert "a" not in tokens
    assert "b" not in tokens
    assert "word" in tokens


def test_tokenize_empty_string(engine):
    assert engine._tokenize("") == set()


def test_tokenize_only_punctuation(engine):
    tokens = engine._tokenize("!@#$%")
    assert tokens == set()


# ── _jaccard ─────────────────────────────────────────────────

def test_jaccard_identical_sets(engine):
    assert engine._jaccard({"a", "b", "c"}, {"a", "b", "c"}) == 1.0


def test_jaccard_disjoint_sets(engine):
    assert engine._jaccard({"a", "b"}, {"x", "y"}) == 0.0


def test_jaccard_partial_overlap(engine):
    score = engine._jaccard({"a", "b", "c"}, {"b", "c", "d"})
    assert score == pytest.approx(2 / 4)  # intersection=2, union=4


def test_jaccard_one_empty(engine):
    assert engine._jaccard(set(), {"a", "b"}) == 0.0


def test_jaccard_both_empty(engine):
    assert engine._jaccard(set(), set()) == 0.0


# ── _categorize ──────────────────────────────────────────────

def test_categorize_confirmed(engine):
    ev = SkillEvidence(
        skill_id="ai_building", skill_label="AI Building",
        level=SkillLevel.PRACTICING, confidence=Confidence.MEDIUM,
    )
    # Add mock entries to satisfy entry_count > 0
    from src.models import GrowthEntry, EntryCategory, Significance
    from datetime import date
    for i in range(3):
        ev.entries.append(GrowthEntry(
            id=f"e{i}", date=date.today(),
            category=EntryCategory.PROJECT, summary=f"Entry {i}",
            primary_skill="ai_building", significance=Significance.PRACTICE,
        ))

    ai_discovered = {"ai_building": ev}
    confirmed, revealed, aspirational = engine._categorize(
        matches=[("ai_building", 0, 0.8)],
        unmatched_ai=[],
        unmatched_self=[],
        ai_discovered=ai_discovered,
    )
    assert len(confirmed) == 1
    assert confirmed[0]["category"] == "Confirmed"
    assert confirmed[0]["skill_label"] == "AI Building"


def test_categorize_revealed(engine):
    ev = SkillEvidence(
        skill_id="ai_building", skill_label="AI Building",
        level=SkillLevel.PRACTICING, confidence=Confidence.MEDIUM,
    )
    from src.models import GrowthEntry, EntryCategory, Significance
    from datetime import date
    ev.entries.append(GrowthEntry(
        id="e0", date=date.today(),
        category=EntryCategory.PROJECT, summary="Built AI agent",
        primary_skill="ai_building", significance=Significance.STRETCH,
    ))

    ai_discovered = {"ai_building": ev}
    confirmed, revealed, aspirational = engine._categorize(
        matches=[],
        unmatched_ai=["ai_building"],
        unmatched_self=[],
        ai_discovered=ai_discovered,
    )
    assert len(revealed) == 1
    assert revealed[0]["category"] == "Revealed"
    assert revealed[0]["skill_label"] == "AI Building"


def test_categorize_aspirational(engine):
    confirmed, revealed, aspirational = engine._categorize(
        matches=[],
        unmatched_ai=[],
        unmatched_self=["public speaking"],
        ai_discovered={},
    )
    assert len(aspirational) == 1
    assert aspirational[0]["category"] == "Aspirational"
    assert aspirational[0]["skill_label"] == "public speaking"


def test_categorize_skips_empty_evidence(engine):
    ev = SkillEvidence(
        skill_id="system_design", skill_label="System Design",
        level=SkillLevel.AWARE, confidence=Confidence.LOW,
    )
    # No entries → entry_count == 0
    ai_discovered = {"system_design": ev}
    confirmed, revealed, aspirational = engine._categorize(
        matches=[],
        unmatched_ai=["system_design"],
        unmatched_self=[],
        ai_discovered=ai_discovered,
    )
    # Should skip because entry_count == 0
    assert len(revealed) == 0


def test_categorize_all_three(engine):
    from src.models import GrowthEntry, EntryCategory, Significance
    from datetime import date

    ev_confirmed = SkillEvidence(
        skill_id="mentoring", skill_label="Mentoring",
        level=SkillLevel.PRACTICING, confidence=Confidence.MEDIUM,
    )
    ev_confirmed.entries.append(GrowthEntry(
        id="e1", date=date.today(), category=EntryCategory.LEARNING,
        summary="Mentored junior", primary_skill="mentoring",
        significance=Significance.STRETCH,
    ))

    ev_revealed = SkillEvidence(
        skill_id="ai_building", skill_label="AI Building",
        level=SkillLevel.CAPABLE, confidence=Confidence.HIGH,
    )
    ev_revealed.entries.append(GrowthEntry(
        id="e2", date=date.today(), category=EntryCategory.PROJECT,
        summary="Built AI agent", primary_skill="ai_building",
        significance=Significance.STRETCH,
    ))

    ai_discovered = {"mentoring": ev_confirmed, "ai_building": ev_revealed}
    confirmed, revealed, aspirational = engine._categorize(
        matches=[("mentoring", 0, 0.7)],
        unmatched_ai=["ai_building"],
        unmatched_self=["public speaking"],
        ai_discovered=ai_discovered,
    )
    assert len(confirmed) == 1
    assert len(revealed) == 1
    assert len(aspirational) == 1


# ── _rank_insights ───────────────────────────────────────────

def test_rank_by_evidence_strength(engine):
    revealed = [
        {"entries": 1, "confidence": "low", "skill_label": "A"},
        {"entries": 5, "confidence": "high", "skill_label": "B"},
        {"entries": 3, "confidence": "medium", "skill_label": "C"},
    ]
    ranked = engine.rank_insights(revealed)
    # B: 5 × 3 = 15, C: 3 × 2 = 6, A: 1 × 1 = 1
    assert ranked[0]["skill_label"] == "B"
    assert ranked[1]["skill_label"] == "C"
    assert ranked[2]["skill_label"] == "A"


def test_rank_empty(engine):
    assert engine.rank_insights([]) == []


def test_rank_unknown_confidence_defaults_low(engine):
    revealed = [
        {"entries": 4, "confidence": "unknown", "skill_label": "X"},
        {"entries": 2, "confidence": "high", "skill_label": "Y"},
    ]
    ranked = engine.rank_insights(revealed)
    # Y: 2 × 3 = 6, X: 4 × 1 = 4
    assert ranked[0]["skill_label"] == "Y"


# ── _generate_summary ────────────────────────────────────────

def test_summary_with_revealed(engine):
    summary = engine._generate_summary(
        confirmed=[],
        revealed=[{"skill_label": "AI Building"}],
        aspirational=[],
    )
    assert "AI Building" in summary
    assert len(summary) > 0


def test_summary_with_all_three(engine):
    summary = engine._generate_summary(
        confirmed=[{"skill_label": "Mentoring"}],
        revealed=[{"skill_label": "AI Building"}],
        aspirational=[{"skill_label": "public speaking"}],
    )
    assert len(summary) > 0


def test_summary_empty(engine):
    summary = engine._generate_summary([], [], [])
    assert len(summary) > 0  # Should still return a message


# ── compare() integration ────────────────────────────────────

def test_compare_both_empty(engine):
    result = engine.compare([], {})
    assert len(result.summary) > 0  # Fallback message exists
    assert result.confirmed == []
    assert result.revealed == []


def test_compare_matches_mentoring(engine):
    from src.models import GrowthEntry, EntryCategory, Significance
    from datetime import date

    ev = SkillEvidence(
        skill_id="mentoring", skill_label="Mentoring & Developing Others",
        level=SkillLevel.PRACTICING, confidence=Confidence.MEDIUM,
    )
    ev.entries.append(GrowthEntry(
        id="e1", date=date.today(), category=EntryCategory.LEARNING,
        summary="Mentored junior through design review",
        primary_skill="mentoring", significance=Significance.STRETCH,
    ))

    result = engine.compare(
        self_claimed=["mentoring others", "public speaking"],
        ai_discovered={"mentoring": ev},
    )
    assert len(result.confirmed) == 1
    assert result.confirmed[0]["skill_id"] == "mentoring"
    assert any("public speaking" in a["skill_label"] for a in result.aspirational)


def test_compare_no_self_claimed_all_revealed(engine):
    from src.models import GrowthEntry, EntryCategory, Significance
    from datetime import date

    ev = SkillEvidence(
        skill_id="ai_building", skill_label="AI Building",
        level=SkillLevel.CAPABLE, confidence=Confidence.HIGH,
    )
    ev.entries.append(GrowthEntry(
        id="e1", date=date.today(), category=EntryCategory.PROJECT,
        summary="Built AI code review agent", primary_skill="ai_building",
        significance=Significance.STRETCH,
    ))

    result = engine.compare(
        self_claimed=["something completely different"],
        ai_discovered={"ai_building": ev},
    )
    assert len(result.revealed) >= 1
    revealed_ids = [r["skill_id"] for r in result.revealed]
    assert "ai_building" in revealed_ids
