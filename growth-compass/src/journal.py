"""Growth Journal — captures and structures growth moments."""

from datetime import date
from typing import Optional

from .models import GrowthEntry, EntryCategory, Significance


class GrowthJournal:
    """Manages the collection and structuring of growth entries."""

    def __init__(self):
        self.entries: list[GrowthEntry] = []
        self._id_counter = 0

    def add_entry(self, entry: GrowthEntry) -> GrowthEntry:
        """Add a growth entry to the journal."""
        self._id_counter += 1
        if not entry.id:
            entry.id = f"entry_{self._id_counter:04d}"
        if not entry.date:
            entry.date = date.today()
        self.entries.append(entry)
        return entry

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
    ) -> GrowthEntry:
        """Capture a growth moment and return the structured entry.

        This is the programmatic equivalent of the Capture Growth Moment skill.
        """
        entry = GrowthEntry(
            id="",
            date=date.today(),
            category=EntryCategory(category),
            summary=summary,
            primary_skill=primary_skill,
            secondary_skills=secondary_skills or [],
            significance=Significance(significance),
            context=context,
            role=role,
            hard_part=hard_part,
            outcome=outcome,
            key_insight=key_insight,
            reflection=reflection,
        )
        return self.add_entry(entry)

    def get_entries_by_skill(self, skill_id: str) -> list[GrowthEntry]:
        """Return all entries tagged with a given skill."""
        return [
            e for e in self.entries
            if e.primary_skill == skill_id or skill_id in e.secondary_skills
        ]

    def get_recent(self, count: int = 10) -> list[GrowthEntry]:
        """Return the most recent entries."""
        return sorted(self.entries, key=lambda e: e.date, reverse=True)[:count]

    def get_stretch_entries(self) -> list[GrowthEntry]:
        """Return only stretch experiences."""
        return [e for e in self.entries if e.significance == Significance.STRETCH]

    def stats(self) -> dict:
        """Return summary statistics about the journal."""
        skills = set()
        categories = {}
        for e in self.entries:
            skills.add(e.primary_skill)
            for s in e.secondary_skills:
                skills.add(s)
            cat_key = e.category.value
            categories[cat_key] = categories.get(cat_key, 0) + 1

        return {
            "total_entries": len(self.entries),
            "unique_skills": len(skills),
            "stretch_count": len(self.get_stretch_entries()),
            "categories": categories,
            "first_entry": self.entries[0].date.isoformat() if self.entries else None,
            "latest_entry": self.entries[-1].date.isoformat() if self.entries else None,
        }
