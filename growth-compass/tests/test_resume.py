"""Unit tests for resume import functionality."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GrowthCompassAgent
from src.models import ResumeEntry, ResumeExtraction


# ── Pydantic model validation ─────────────────────────────────

def test_resume_entry_minimal():
    entry = ResumeEntry(
        summary="Built an AI code review system",
        category="Project",
        primary_skill="ai_building",
        significance="Stretch",
    )
    assert entry.summary == "Built an AI code review system"
    assert entry.category == "Project"
    assert entry.secondary_skills == []
    assert entry.context == ""
    assert entry.key_insight == ""


def test_resume_entry_full():
    entry = ResumeEntry(
        summary="Led migration to microservices",
        category="Project",
        primary_skill="system_design",
        secondary_skills=["shipping", "initiative"],
        significance="Stretch",
        context="Company scaling required breaking monolith into 12 services",
        role="Tech lead for the migration",
        hard_part="Zero-downtime requirement during business hours",
        outcome="Deploy frequency improved 4x, no production incidents during migration",
        key_insight="Strangler fig pattern works — migrate one endpoint at a time",
    )
    assert len(entry.secondary_skills) == 2


def test_resume_extraction_multiple_entries():
    extraction = ResumeExtraction(
        entries=[
            ResumeEntry(
                summary="Entry 1", category="Project",
                primary_skill="ai_building", significance="Stretch",
            ),
            ResumeEntry(
                summary="Entry 2", category="Learning",
                primary_skill="communication", significance="Practice",
            ),
            ResumeEntry(
                summary="Entry 3", category="Milestone",
                primary_skill="mentoring", significance="Stretch",
            ),
        ],
        summary="A strong candidate with diverse experience across AI and leadership.",
    )
    assert len(extraction.entries) == 3
    assert "diverse experience" in extraction.summary


# ── Agent fallback behavior ───────────────────────────────────

def test_import_resume_no_llm():
    agent = GrowthCompassAgent(user_name="Test", use_llm=False)
    result = agent.import_resume("Some resume text here")
    assert result["status"] == "fallback"
    assert "LLM" in result["summary"]


def test_import_resume_empty_journal_before():
    agent = GrowthCompassAgent(user_name="Test", use_llm=False)
    assert len(agent.journal.entries) == 0
    agent.import_resume("Fake resume")
    # Journal should still be empty since fallback didn't add entries
    assert len(agent.journal.entries) == 0


# ── Integration: resume + comparison ──────────────────────────

def test_resume_then_compare():
    """Verify imported entries flow into comparison engine."""
    agent = GrowthCompassAgent(user_name="Test", use_llm=False)

    # Simulate what import_resume does with an LLM — manually add entries
    agent.capture(
        summary="Built AI code review system",
        primary_skill="ai_building",
        category="Project",
        significance="Stretch",
        context="Team spending too much time on reviews",
        role="Built the agent and prompt chain",
        hard_part="Distinguishing real bugs from style nits",
        outcome="Reduced review time by 60%",
        key_insight="Good prompts define what 'good' looks like",
    )
    agent.capture(
        summary="Designed rate limiter for notification service",
        primary_skill="system_design",
        category="Project",
        significance="Stretch",
        context="Service hitting downstream limits under load",
        role="Led design, wrote design doc, got Staff review",
        hard_part="Token bucket vs sliding window tradeoffs",
        outcome="Design approved with escape hatch for future changes",
        key_insight="Good designs leave room to change your mind",
    )
    agent.capture(
        summary="Mentored junior through first system design review",
        primary_skill="mentoring",
        category="Learning",
        significance="Stretch",
        context="Junior was nervous, needed confidence",
        role="Ran mock reviews, taught design framework",
        hard_part="Not jumping in to answer for them",
        outcome="Both passed, one said 'I actually enjoyed it'",
        key_insight="Teaching thinking is the only thing that scales",
    )

    # Run comparison — user claims mentoring but not system design
    result = agent.compare(["mentoring others", "public speaking"])

    assert result["status"] == "generated"
    # System Design should be revealed (AI found it, user didn't claim it)
    revealed_ids = [r["skill_id"] for r in result["revealed"]]
    assert "system_design" in revealed_ids or "ai_building" in revealed_ids
    # Mentoring should be confirmed (user claimed it, evidence exists)
    confirmed_ids = [c["skill_id"] for c in result["confirmed"]]
    assert "mentoring" in confirmed_ids
