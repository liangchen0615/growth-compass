"""Data models for the Growth Compass system."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EntryCategory(Enum):
    PROJECT = "Project"
    LEARNING = "Learning"
    FEEDBACK = "Feedback"
    STRUGGLE = "Struggle"
    MILESTONE = "Milestone"


class Significance(Enum):
    STRETCH = "Stretch"
    PRACTICE = "Practice"
    EXPOSURE = "Exposure"


class SkillLevel(Enum):
    AWARE = "Aware"
    PRACTICING = "Practicing"
    CAPABLE = "Capable"
    PROFICIENT = "Proficient"
    MASTER = "Master"


class Confidence(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class GrowthEntry:
    """A single structured growth moment."""
    id: str
    date: date
    category: EntryCategory
    summary: str
    primary_skill: str
    secondary_skills: list[str] = field(default_factory=list)
    significance: Significance = Significance.PRACTICE
    context: str = ""
    role: str = ""
    hard_part: str = ""
    outcome: str = ""
    key_insight: str = ""
    reflection: str = ""


@dataclass
class SkillEvidence:
    """Aggregated evidence for a single skill."""
    skill_id: str
    skill_label: str
    entries: list[GrowthEntry] = field(default_factory=list)
    level: SkillLevel = SkillLevel.AWARE
    confidence: Confidence = Confidence.LOW
    trend: str = "stable"  # rising, stable, declining

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def stretch_count(self) -> int:
        return sum(1 for e in self.entries if e.significance == Significance.STRETCH)


@dataclass
class SkillMap:
    """A user's complete skill graph at a point in time."""
    user_name: str
    generated_date: date
    entries_analyzed: int
    skills: dict[str, SkillEvidence] = field(default_factory=dict)
    strengths: list[str] = field(default_factory=list)
    growth_edges: list[str] = field(default_factory=list)
    blind_spots: list[str] = field(default_factory=list)
    plateaus: list[str] = field(default_factory=list)
    superpower: str = ""
    pattern_notes: str = ""


@dataclass
class GapAnalysis:
    """One gap between current state and target role."""
    skill_id: str
    skill_label: str
    current_level: SkillLevel
    target_level: SkillLevel
    gap_size: int  # how many levels apart
    priority: int  # 1=blocker, 2=accelerator, 3=differentiator, 4=foundation
    priority_label: str
    learning_mode: str  # project_based, mentored, structured, teaching, observation


@dataclass
class DevelopmentPlan:
    """A personalized 30/60/90 day development plan."""
    user_name: str
    target_role: str
    generated_date: date
    current_summary: str
    gaps: list[GapAnalysis] = field(default_factory=list)
    sprint_30: list[dict] = field(default_factory=list)
    checkpoint_60: list[dict] = field(default_factory=list)
    target_90: list[dict] = field(default_factory=list)
    risks: list[dict] = field(default_factory=list)
    learning_edge: str = ""


@dataclass
class GrowthReport:
    """A periodic growth visibility report."""
    period: str
    generated_date: date
    entries_count: int
    skills_demonstrated: int
    skills_leveled_up: int
    stretch_count: int
    new_skills: int
    key_moments: list[dict] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    plan_progress: list[dict] = field(default_factory=list)
    skill_changes: list[dict] = field(default_factory=list)
    next_focus: str = ""
    next_priorities: list[str] = field(default_factory=list)
    reflection_prompt: str = ""


# ── LLM Response Models (Pydantic for structured output parsing) ──

class SkillAssessment(BaseModel):
    """Per-skill assessment returned by the LLM."""
    level: str = Field(description="One of: Aware, Practicing, Capable, Proficient, Master")
    confidence: str = Field(description="One of: Low, Medium, High")
    trend: str = Field(description="One of: rising, stable, declining")
    rationale: str = Field(description="Brief evidence-based reasoning for the assessment (1-2 sentences)")


class PatternAnalysis(BaseModel):
    """Cross-skill pattern analysis returned by the LLM."""
    strengths: list[str] = Field(description="Skill IDs where user shows high level and high confidence")
    growth_edges: list[str] = Field(description="Skill IDs with rapidly rising trajectory")
    blind_spots: list[str] = Field(description="Skill IDs expected but with zero or minimal evidence")
    plateaus: list[str] = Field(description="Skill IDs with entries but stagnant level progression")
    superpower: str = Field(description="Description of the user's strongest skill combination, e.g. 'System Design x Communication'")
    pattern_notes: str = Field(description="2-3 sentence narrative describing the most interesting growth patterns observed")


class DevPlanOutput(BaseModel):
    """Full development plan generated by the LLM."""
    current_summary: str = Field(description="1-2 sentence summary of current state relative to target role")
    sprint_30: list[dict] = Field(description="3-4 weekly sprint items, each with: week(int), focus(str), action(str), success(str), time(str), resource(str or null)")
    checkpoint_60: list[dict] = Field(description="Checkpoint items with: focus(str), action(str), validation(str)")
    target_90: list[dict] = Field(description="Target outcomes with: competency(str), target_level(str), proof(str)")
    risks: list[dict] = Field(description="Risk items with: risk(str), mitigation(str)")
    learning_edge: str = Field(description="One sentence describing what makes this plan particularly suited to this person")


class ReportOutput(BaseModel):
    """Growth report content generated by the LLM."""
    key_moments: list[dict] = Field(description="1-3 most significant growth entries with: title(str), date(str), context(str), why_it_mattered(str), category(str)")
    patterns: list[str] = Field(description="2-3 thematic observations about growth patterns this period")
    plan_progress: list[dict] = Field(description="Progress items with: priority_gap(str), plan(str), progress(str), status(str)")
    next_focus: str = Field(description="Primary theme to focus on in the next period (one phrase)")
    next_priorities: list[str] = Field(description="2-3 concrete priorities for the next period")
    reflection_prompt: str = Field(description="One forward-looking question to guide the next period")


class CaptureOutput(BaseModel):
    """Structured growth entry extracted from natural language by the LLM."""
    is_complete: bool = Field(description="True if enough information was extracted to create a full growth entry")
    follow_up_question: Optional[str] = Field(default=None, description="A clarifying question if is_complete is False. Keep it sharp and specific.")
    summary: Optional[str] = Field(default=None, description="One-line summary of what happened")
    category: Optional[str] = Field(default=None, description="One of: Project, Learning, Feedback, Struggle, Milestone")
    primary_skill: Optional[str] = Field(default=None, description="Skill ID of the main skill exercised, from the competency taxonomy")
    secondary_skills: Optional[list[str]] = Field(default=None, description="Additional skill IDs exercised")
    significance: Optional[str] = Field(default=None, description="One of: Stretch, Practice, Exposure")
    context: Optional[str] = Field(default=None, description="2-3 sentence description of the situation")
    role: Optional[str] = Field(default=None, description="What the user specifically did")
    hard_part: Optional[str] = Field(default=None, description="What was genuinely difficult")
    outcome: Optional[str] = Field(default=None, description="What happened, what feedback was received")
    key_insight: Optional[str] = Field(default=None, description="The one thing the user will take forward from this experience")
    reflection: Optional[str] = Field(default=None, description="A deeper insight or pattern the user noticed")
