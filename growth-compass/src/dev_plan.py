"""Development Plan Generator — builds personalized 30/60/90 day plans.

Uses LLM for creative plan content when available, falling back to templates.
"""

from datetime import date
from typing import TYPE_CHECKING

from .models import SkillMap, GapAnalysis, DevelopmentPlan, SkillLevel
from .knowledge import get_role, skill_level_order, find_resources

if TYPE_CHECKING:
    from .llm import LLMClient


PRIORITY_LABELS = {
    1: "Blocker",
    2: "Accelerator",
    3: "Differentiator",
    4: "Foundation",
}

LEARNING_MODE_MAP = {
    "system_design": "project_based",
    "coding_quality": "project_based",
    "debugging": "project_based",
    "ai_building": "project_based",
    "rapid_ai_prototyping": "project_based",
    "shipping": "project_based",
    "communication": "mentored",
    "mentoring": "teaching",
    "initiative": "project_based",
    "decision_making": "mentored",
    "data_thinking": "structured",
    "data_structuring": "structured",
    "user_insight": "observation",
    "problem_definition": "mentored",
    "ai_first_thinking": "structured",
}


def _priority(skill_id: str, gap_size: int) -> int:
    """Determine gap priority (heuristic fallback)."""
    blockers = ["ai_building", "problem_definition", "shipping"]
    accelerators = ["data_structuring", "communication", "initiative"]
    differentiators = ["user_insight", "ai_first_thinking", "system_design"]
    foundations = ["coding_quality", "debugging", "data_thinking"]

    if skill_id in blockers and gap_size >= 2:
        return 1
    elif skill_id in accelerators:
        return 2
    elif skill_id in differentiators:
        return 3
    else:
        return 4


def _learning_mode(skill_id: str) -> str:
    return LEARNING_MODE_MAP.get(skill_id, "project_based")


class DevPlanGenerator:
    """Generates personalized development plans."""

    def __init__(self, llm_client: "LLMClient | None" = None):
        self.llm = llm_client

    def _compute_gaps(self, skill_map: SkillMap, role: dict) -> list[GapAnalysis]:
        """Compute gaps between current skill map and target role expectations.

        This stays as pure data transformation — it's math, not creativity.
        """
        expectations = role.get("expectations", {})
        gaps: list[GapAnalysis] = []
        for skill_id, target_level_str in expectations.items():
            current_ev = skill_map.skills.get(skill_id)
            current_level_val = current_ev.level.value if current_ev else "aware"
            current_order = skill_level_order(current_level_val)
            target_order = skill_level_order(target_level_str)
            gap_size = target_order - current_order

            if gap_size > 0:
                prio = _priority(skill_id, gap_size)
                gaps.append(GapAnalysis(
                    skill_id=skill_id,
                    skill_label=current_ev.skill_label if current_ev else skill_id,
                    current_level=SkillLevel(current_level_val.title()),
                    target_level=SkillLevel(target_level_str.title()),
                    gap_size=gap_size,
                    priority=prio,
                    priority_label=PRIORITY_LABELS.get(prio, "Foundation"),
                    learning_mode=_learning_mode(skill_id),
                ))

        gaps.sort(key=lambda g: (g.priority, -g.gap_size))
        return gaps

    def _heuristic_generate(
        self, skill_map: SkillMap, role: dict, gaps: list[GapAnalysis],
    ) -> DevelopmentPlan:
        """Generate plan using heuristic templates (fallback)."""
        strengths = ", ".join(
            skill_map.skills[s].skill_label for s in skill_map.strengths[:3]
        ) if skill_map.strengths else "building foundations"

        current_summary = (
            f"You have {skill_map.entries_analyzed} growth entries across "
            f"{len([s for s in skill_map.skills.values() if s.entry_count > 0])} skills. "
            f"Key strengths: {strengths}. "
            f"Target: {role['label']} ({role.get('label', 'unknown')})."
        )

        sprint_30 = self._build_sprint(gaps[:3], 30)
        checkpoint_60 = self._build_checkpoint(gaps, 60)
        target_90 = self._build_target(gaps, role)
        risks = self._build_risks(gaps, skill_map)
        learning_edge = self._learning_edge(gaps, skill_map)

        return DevelopmentPlan(
            user_name=skill_map.user_name,
            target_role=role["label"],
            generated_date=date.today(),
            current_summary=current_summary,
            gaps=gaps,
            sprint_30=sprint_30,
            checkpoint_60=checkpoint_60,
            target_90=target_90,
            risks=risks,
            learning_edge=learning_edge,
        )

    def _llm_generate(
        self,
        skill_map: SkillMap,
        role: dict,
        gaps: list[GapAnalysis],
    ) -> DevelopmentPlan | None:
        """Use LLM to generate a personalized development plan."""
        if not self.llm or not self.llm.available:
            return None

        output = self.llm.generate_dev_plan(skill_map, role, gaps)
        if output is None:
            return None

        return DevelopmentPlan(
            user_name=skill_map.user_name,
            target_role=role["label"],
            generated_date=date.today(),
            current_summary=output.current_summary,
            gaps=gaps,
            sprint_30=output.sprint_30,
            checkpoint_60=output.checkpoint_60,
            target_90=output.target_90,
            risks=output.risks,
            learning_edge=output.learning_edge,
        )

    def generate(
        self, skill_map: SkillMap, target_role_id: str,
    ) -> DevelopmentPlan:
        """Generate a 30/60/90 day development plan from a skill map and target.

        Gap computation is always heuristic (it's math). Plan content
        tries LLM first, falls back to templates.
        """
        role = get_role(target_role_id)
        if not role:
            raise ValueError(f"Unknown role: {target_role_id}")

        # Gap analysis — always heuristic (pure data transformation)
        gaps = self._compute_gaps(skill_map, role)

        # Try LLM for creative plan content
        llm_plan = self._llm_generate(skill_map, role, gaps)
        if llm_plan is not None:
            return llm_plan

        # Fallback to heuristic
        return self._heuristic_generate(skill_map, role, gaps)

    def _build_sprint(self, top_gaps: list[GapAnalysis], days: int) -> list[dict]:
        """Build the 30-day sprint plan for highest-priority gaps (heuristic)."""
        weeks = []
        for i, gap in enumerate(top_gaps):
            resources = find_resources(gap.skill_id)
            resource_name = resources[0]["title"] if resources else "Find relevant learning materials"
            weeks.append({
                "week": i + 1,
                "focus": gap.skill_label,
                "action": f"Stretch assignment or project targeting {gap.skill_label}",
                "success": f"Can demonstrate {gap.current_level.value} -> {gap.target_level.value} with one concrete deliverable",
                "time": "4-6 hours/week",
                "resource": resource_name,
            })
        while len(weeks) < 3:
            weeks.append({
                "week": len(weeks) + 1,
                "focus": "Consolidate & capture",
                "action": "Deepen practice on Week 1-2 skills. Capture 3+ growth entries.",
                "success": "Journal has entries for each week with specific evidence",
                "time": "3-4 hours/week",
                "resource": None,
            })
        return weeks

    def _build_checkpoint(self, gaps: list[GapAnalysis], days: int) -> list[dict]:
        """Build the 60-day checkpoint (heuristic)."""
        checkpoint = []
        for gap in gaps[:5]:
            checkpoint.append({
                "focus": gap.skill_label,
                "action": f"Apply {gap.skill_label} in a new context to build confidence",
                "validation": f"External feedback or visible output demonstrating {gap.target_level.value} level",
            })
        return checkpoint

    def _build_target(
        self, gaps: list[GapAnalysis], role: dict,
    ) -> list[dict]:
        """Build the 90-day target outcomes (heuristic)."""
        target = []
        for gap in gaps[:5]:
            target.append({
                "competency": gap.skill_label,
                "target_level": gap.target_level.value,
                "proof": f"Can independently demonstrate {gap.skill_label} at {gap.target_level.value} level in real work",
            })
        target.append({
            "competency": "Overall readiness for " + role["label"],
            "target_level": role.get("key_differentiator", ""),
            "proof": "Skill map shows all expected competencies at or above target level",
        })
        return target

    def _build_risks(
        self, gaps: list[GapAnalysis], skill_map: SkillMap,
    ) -> list[dict]:
        """Identify risks and mitigations (heuristic)."""
        risks = []
        if len(gaps) > 5:
            risks.append({
                "risk": "Too many gaps — spreading thin",
                "mitigation": "Focus on top 3 priority gaps. Accept that not everything can close in 90 days.",
            })
        if skill_map.entries_analyzed < 5:
            risks.append({
                "risk": "Thin evidence base — current skill map may be incomplete",
                "mitigation": "Capture growth moments weekly. Fill in blind spots before committing to a target.",
            })
        if all(g.gap_size >= 2 for g in gaps):
            risks.append({
                "risk": "Target role is significantly ahead of current state",
                "mitigation": "Set an intermediate target first. Growth takes time and evidence.",
            })
        risks.append({
            "risk": "Not enough stretch opportunities in current work",
            "mitigation": "Proactively seek or create stretch projects. Side projects count if they produce evidence.",
        })
        return risks

    def _learning_edge(
        self, gaps: list[GapAnalysis], skill_map: SkillMap,
    ) -> str:
        """Describe what gives this person an edge in their learning plan (heuristic)."""
        if skill_map.superpower:
            return (
                f"Your superpower combination ({skill_map.superpower}) gives you a unique angle. "
                "Leverage it: learning new skills through the lens of your strongest combination "
                "will accelerate growth more than studying each skill in isolation."
            )
        return "Build your portfolio of growth entries to reveal your learning edge."
