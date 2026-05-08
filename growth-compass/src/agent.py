"""Growth Compass Agent — the main orchestrator.

This is the agent that ties together all modules: journal, skill graph,
development plan, and growth report.

When an LLM API key is available, intelligence flows through the Claude API.
When unavailable, heuristics provide graceful fallback.
"""

from datetime import date
from typing import Optional

from .journal import GrowthJournal
from .skill_graph import SkillGraphEngine
from .dev_plan import DevPlanGenerator
from .report import ReportGenerator
from .knowledge import list_all_skills, get_role, get_resources
from .llm import LLMClient


class GrowthCompassAgent:
    """AI Growth Companion — makes growth visible, trackable, and personalized."""

    def __init__(
        self,
        user_name: str = "",
        provider: str = "anthropic",
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        use_llm: bool = True,
    ):
        self.user_name = user_name
        self.llm = LLMClient(
            provider=provider, api_key=api_key, model=model, base_url=base_url,
        ) if use_llm else None
        self.journal = GrowthJournal()
        self.graph_engine = SkillGraphEngine(self.journal, llm_client=self.llm)
        self.plan_generator = DevPlanGenerator(llm_client=self.llm)
        self.report_generator = ReportGenerator(
            self.journal, self.graph_engine, llm_client=self.llm
        )
        self.current_plan = None
        self.last_skill_map = None
        self._session_start = date.today()

    # ---- Journal Capture ----

    def capture(
        self,
        summary: str,
        primary_skill: str,
        category: str = "Project",
        secondary_skills: Optional[list[str]] = None,
        significance: str = "Practice",
        context: str = "",
        role: str = "",
        hard_part: str = "",
        outcome: str = "",
        key_insight: str = "",
        reflection: str = "",
    ) -> dict:
        """Capture a growth moment. Returns the structured entry."""
        entry = self.journal.capture(
            summary=summary,
            primary_skill=primary_skill,
            category=category,
            secondary_skills=secondary_skills,
            significance=significance,
            context=context,
            role=role,
            hard_part=hard_part,
            outcome=outcome,
            key_insight=key_insight,
            reflection=reflection,
        )

        return {
            "status": "captured",
            "entry_id": entry.id,
            "entry": {
                "summary": entry.summary,
                "date": entry.date.isoformat(),
                "category": entry.category.value,
                "primary_skill": entry.primary_skill,
                "secondary_skills": entry.secondary_skills,
                "significance": entry.significance.value,
                "context": entry.context,
                "role": entry.role,
                "hard_part": entry.hard_part,
                "outcome": entry.outcome,
                "key_insight": entry.key_insight,
                "reflection": entry.reflection,
            },
        }

    def capture_natural(self, user_input: str) -> dict:
        """Capture a growth moment from natural language via LLM.

        Returns {"status": "captured", ...} on success,
        {"status": "needs_more_info", "follow_up": "..."} if LLM wants clarification,
        {"status": "fallback"} if LLM unavailable or failed.
        """
        if not self.llm or not self.llm.available:
            return {"status": "fallback"}

        result = self.llm.extract_capture_entry(user_input)
        if result is None:
            return {"status": "fallback"}

        if not result.is_complete:
            return {
                "status": "needs_more_info",
                "follow_up": result.follow_up_question or "Could you tell me more about what happened?",
            }

        return self.capture(
            summary=result.summary or user_input[:100],
            primary_skill=result.primary_skill or "ai_building",
            category=result.category or "Project",
            secondary_skills=result.secondary_skills or [],
            significance=result.significance or "Practice",
            context=result.context or "",
            role=result.role or "",
            hard_part=result.hard_part or "",
            outcome=result.outcome or "",
            key_insight=result.key_insight or "",
            reflection=result.reflection or "",
        )

    # ---- Skill Mapping ----

    def map_skills(self) -> dict:
        """Generate the user's skill map."""
        skill_map = self.graph_engine.build_map(self.user_name)
        self.last_skill_map = skill_map

        skills_summary = {}
        for sid, ev in skill_map.skills.items():
            if ev.entry_count > 0:
                skills_summary[sid] = {
                    "label": ev.skill_label,
                    "level": ev.level.value,
                    "confidence": ev.confidence.value,
                    "entries": ev.entry_count,
                    "trend": ev.trend,
                }

        return {
            "status": "generated",
            "entries_analyzed": skill_map.entries_analyzed,
            "skills": skills_summary,
            "strengths": [
                skill_map.skills[s].skill_label for s in skill_map.strengths
                if s in skill_map.skills
            ],
            "growth_edges": [
                skill_map.skills[s].skill_label for s in skill_map.growth_edges
                if s in skill_map.skills
            ],
            "blind_spots": [
                skill_map.skills[s].skill_label for s in skill_map.blind_spots
                if s in skill_map.skills
            ],
            "plateaus": [
                skill_map.skills[s].skill_label for s in skill_map.plateaus
                if s in skill_map.skills
            ],
            "superpower": skill_map.superpower,
            "pattern_notes": skill_map.pattern_notes,
        }

    # ---- Development Plan ----

    def plan(self, target_role_id: str) -> dict:
        """Generate a development plan toward a target role."""
        if not self.last_skill_map:
            self.map_skills()

        dev_plan = self.plan_generator.generate(self.last_skill_map, target_role_id)
        self.current_plan = dev_plan

        return {
            "status": "generated",
            "target": dev_plan.target_role,
            "current_summary": dev_plan.current_summary,
            "gaps": [
                {
                    "skill": g.skill_label,
                    "current": g.current_level.value,
                    "target": g.target_level.value,
                    "gap_size": g.gap_size,
                    "priority": g.priority_label,
                    "learning_mode": g.learning_mode,
                }
                for g in dev_plan.gaps[:5]
            ],
            "sprint_30": dev_plan.sprint_30,
            "checkpoint_60": dev_plan.checkpoint_60,
            "target_90": dev_plan.target_90,
            "risks": dev_plan.risks,
            "learning_edge": dev_plan.learning_edge,
        }

    # ---- Growth Report ----

    def report(self, period: str = "Monthly") -> dict:
        """Generate a growth visibility report."""
        previous_map = self.last_skill_map
        self.map_skills()
        report = self.report_generator.generate(
            period, previous_map, dev_plan=self.current_plan
        )

        return {
            "status": "generated",
            "period": report.period,
            "entries_count": report.entries_count,
            "skills_demonstrated": report.skills_demonstrated,
            "skills_leveled_up": report.skills_leveled_up,
            "stretch_count": report.stretch_count,
            "new_skills": report.new_skills,
            "key_moments": report.key_moments,
            "patterns": report.patterns,
            "next_focus": report.next_focus,
            "next_priorities": report.next_priorities,
            "reflection_prompt": report.reflection_prompt,
            "shareable_summary": self.report_generator.shareable_summary(report),
        }

    # ---- Utilities ----

    def list_skills(self) -> list[dict]:
        """List all competencies in the taxonomy."""
        return list_all_skills()

    def list_roles(self) -> list[dict]:
        """List all available role profiles."""
        from .knowledge import get_roles
        roles_data = get_roles()
        return [
            {"id": rid, "label": rdata["label"], "description": rdata.get("key_differentiator", "")}
            for rid, rdata in roles_data.get("roles", {}).items()
        ]

    def stats(self) -> dict:
        """Return journal and agent statistics."""
        journal_stats = self.journal.stats()
        return {
            "session_start": self._session_start.isoformat(),
            "session_days": (date.today() - self._session_start).days,
            **journal_stats,
        }

    def status(self) -> dict:
        """Return current agent state overview."""
        return {
            "user": self.user_name,
            "entries": len(self.journal.entries),
            "has_plan": self.current_plan is not None,
            "target_role": self.current_plan.target_role if self.current_plan else None,
            "last_entry": self.journal.entries[-1].date.isoformat() if self.journal.entries else None,
            "journal_stats": self.journal.stats(),
            "llm_available": self.llm.available if self.llm else False,
        }
