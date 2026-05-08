"""Growth Report Generator — produces periodic growth visibility reports.

Uses LLM for key moments, patterns, and focus recommendations when available,
falling back to heuristics.
"""

from datetime import date
from typing import TYPE_CHECKING

from .models import GrowthReport, Significance
from .journal import GrowthJournal
from .skill_graph import SkillGraphEngine

if TYPE_CHECKING:
    from .llm import LLMClient


class ReportGenerator:
    """Generates periodic growth visibility reports."""

    def __init__(
        self,
        journal: GrowthJournal,
        engine: SkillGraphEngine,
        llm_client: "LLMClient | None" = None,
    ):
        self.journal = journal
        self.engine = engine
        self.llm = llm_client

    def _llm_generate(
        self,
        period: str,
        current_map,
        previous_map,
        dev_plan,
    ) -> GrowthReport | None:
        """Use LLM to generate report content (key moments, patterns, focus)."""
        if not self.llm or not self.llm.available:
            return None

        output = self.llm.generate_report(
            period,
            self.journal.entries,
            current_map,
            previous_map,
            dev_plan,
        )
        if output is None:
            return None

        skill_changes = []
        if previous_map:
            skill_changes = self.engine.compare(previous_map, current_map)

        return GrowthReport(
            period=period,
            generated_date=date.today(),
            entries_count=len(self.journal.entries),
            skills_demonstrated=len(
                [s for s in current_map.skills.values() if s.entry_count > 0]
            ),
            skills_leveled_up=len(skill_changes),
            stretch_count=self.journal.stats().get("stretch_count", 0),
            new_skills=sum(
                1 for s in current_map.skills.values()
                if 0 < s.entry_count <= 1
            ),
            key_moments=output.key_moments,
            patterns=output.patterns,
            plan_progress=output.plan_progress,
            skill_changes=skill_changes,
            next_focus=output.next_focus,
            next_priorities=output.next_priorities,
            reflection_prompt=output.reflection_prompt,
        )

    def generate(
        self,
        period: str = "Monthly",
        previous_map=None,
        dev_plan=None,
    ) -> GrowthReport:
        """Generate a growth report for the current state.

        Tries LLM first for creative content, falls back to heuristics.
        """
        current_map = self.engine.build_map()

        # Try LLM
        llm_report = self._llm_generate(period, current_map, previous_map, dev_plan)
        if llm_report is not None:
            return llm_report

        # Heuristic fallback
        entries = self.journal.entries
        stats = self.journal.stats()

        skill_changes = []
        if previous_map:
            skill_changes = self.engine.compare(previous_map, current_map)

        key_moments = self._identify_key_moments(entries)
        patterns = self._detect_patterns(entries, current_map)
        next_focus, next_priorities = self._recommend_focus(current_map)

        return GrowthReport(
            period=period,
            generated_date=date.today(),
            entries_count=len(entries),
            skills_demonstrated=len(
                [s for s in current_map.skills.values() if s.entry_count > 0]
            ),
            skills_leveled_up=len(skill_changes),
            stretch_count=stats.get("stretch_count", 0),
            new_skills=sum(
                1 for s in current_map.skills.values()
                if 0 < s.entry_count <= 1
            ),
            key_moments=key_moments,
            patterns=patterns,
            plan_progress=[],
            skill_changes=skill_changes,
            next_focus=next_focus,
            next_priorities=next_priorities,
            reflection_prompt=self._reflection_prompt(entries, current_map),
        )

    def _identify_key_moments(self, entries: list) -> list[dict]:
        """Pick the 1-3 most significant growth moments (heuristic)."""
        stretch = [e for e in entries if e.significance == Significance.STRETCH]
        struggles = [e for e in entries if e.category.value == "Struggle"]

        moments = []
        candidates = sorted(
            stretch + struggles,
            key=lambda e: len(e.key_insight),
            reverse=True,
        )

        for entry in candidates[:3]:
            moments.append({
                "title": entry.summary,
                "date": entry.date.isoformat(),
                "context": entry.context,
                "why_it_mattered": entry.key_insight or entry.hard_part or entry.outcome,
                "category": entry.category.value,
            })
        return moments

    def _detect_patterns(self, entries: list, skill_map) -> list[str]:
        """Detect thematic patterns across entries (heuristic)."""
        patterns = []

        if not entries:
            return ["No entries yet — start capturing to reveal growth patterns."]

        stretch_ratio = (
            sum(1 for e in entries if e.significance == Significance.STRETCH)
            / len(entries)
        )

        if stretch_ratio > 0.4:
            patterns.append(
                "You're consistently operating at your learning edge. "
                f"{int(stretch_ratio * 100)}% of your entries are stretch experiences — "
                "this is a high-growth period."
            )
        elif stretch_ratio < 0.15:
            patterns.append(
                "Most activities are practice or exposure. Consider actively seeking "
                "a stretch assignment to push into new territory."
            )

        struggle_count = sum(1 for e in entries if e.category.value == "Struggle")
        if struggle_count >= 2:
            patterns.append(
                f"{struggle_count} entries frame difficulties as learning moments. "
                "Your relationship with struggle is a growth asset — you metabolize difficulty."
            )

        if skill_map.blind_spots:
            blind_labels = [
                skill_map.skills[s].skill_label
                for s in skill_map.blind_spots[:3]
                if s in skill_map.skills
            ]
            if blind_labels:
                patterns.append(
                    f"Blind spots detected in: {', '.join(blind_labels)}. "
                    "These competencies are expected but have zero evidence."
                )

        return patterns

    def _recommend_focus(self, skill_map) -> tuple[str, list[str]]:
        """Recommend focus areas for the next period (heuristic)."""
        priorities = []

        if skill_map.growth_edges:
            edge_label = skill_map.skills[skill_map.growth_edges[0]].skill_label
            priorities.append(
                f"Build on momentum in {edge_label} — your fastest-growing area"
            )

        for blind in skill_map.blind_spots[:2]:
            if blind in skill_map.skills:
                priorities.append(
                    f"Get first evidence in {skill_map.skills[blind].skill_label}"
                )

        for plateau in skill_map.plateaus[:1]:
            if plateau in skill_map.skills:
                priorities.append(
                    f"Break the plateau in {skill_map.skills[plateau].skill_label} "
                    f"by trying a different context or learning mode"
                )

        if not priorities:
            priorities = [
                "Continue building evidence across all skills",
                "Seek external feedback to validate self-assessment",
            ]

        if skill_map.superpower:
            focus = f"Deepen your {skill_map.superpower} combination"
        else:
            focus = "Build your evidence base and reveal your unique combination"

        return focus, priorities[:3]

    def _reflection_prompt(self, entries: list, skill_map) -> str:
        """Generate a forward-looking reflection prompt (heuristic)."""
        if not entries:
            return (
                "What's one thing you did this week that stretched you? "
                "Not necessarily a win — something that was harder than you expected."
            )

        if skill_map.blind_spots and skill_map.strengths:
            return (
                f"You're clearly strong in {skill_map.skills[skill_map.strengths[0]].skill_label}. "
                "What would it look like to apply that strength to a totally different domain?"
            )

        return (
            "If you could only develop ONE skill deeply over the next three months, "
            "which would create the most leverage for everything else you want to do?"
        )

    def shareable_summary(self, report: GrowthReport) -> str:
        """Produce a concise shareable summary for managers or mentors."""
        lines = [
            f"Growth Summary — {report.period}",
            f"Entries: {report.entries_count} | "
            f"Skills demonstrated: {report.skills_demonstrated} | "
            f"Leveled up: {report.skills_leveled_up}",
            "",
            "Key moments:",
        ]
        for m in report.key_moments:
            lines.append(f"  - {m['title']} — {m['why_it_mattered'][:100]}")
        lines.append("")
        lines.append("Focus for next period:")
        for p in report.next_priorities:
            lines.append(f"  - {p}")
        return "\n".join(lines)
