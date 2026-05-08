"""Knowledge base loader and query utilities."""

import json
from pathlib import Path
from typing import Optional

KB_DIR = Path(__file__).parent.parent / "agent" / "knowledge_base"


def _load_json(filename: str) -> dict:
    path = KB_DIR / filename
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_taxonomy() -> dict:
    """Return the full competency taxonomy."""
    return _load_json("skills_taxonomy.json")


def get_competency(skill_id: str) -> Optional[dict]:
    """Look up a single competency by its ID."""
    taxonomy = get_taxonomy()
    for domain in taxonomy.get("domains", {}).values():
        for comp_id, comp in domain.get("competencies", {}).items():
            if comp_id == skill_id:
                return comp
    return None


def list_all_skills() -> list[dict]:
    """Return all competency definitions with their domain context."""
    taxonomy = get_taxonomy()
    skills = []
    for domain_id, domain in taxonomy.get("domains", {}).items():
        for comp_id, comp in domain.get("competencies", {}).items():
            skills.append({
                "id": comp_id,
                "label": comp["label"],
                "description": comp["description"],
                "domain": domain["label"],
                "domain_id": domain_id,
            })
    return skills


def get_roles() -> dict:
    """Return all role profiles."""
    return _load_json("roles.json")


def get_role(role_id: str) -> Optional[dict]:
    """Look up a specific role profile."""
    roles = get_roles()
    return roles.get("roles", {}).get(role_id)


def get_resources() -> list[dict]:
    """Return all learning resources."""
    data = _load_json("resources.json")
    return data.get("resources", [])


def find_resources(skill_id: str, level: str = None) -> list[dict]:
    """Find learning resources for a given skill and optional level."""
    resources = get_resources()
    matching = [r for r in resources if r["competency"] == skill_id]
    if level:
        matching = [r for r in matching if level in r.get("best_for", [])]
    return matching


def skill_level_order(level: str) -> int:
    """Convert skill level string to numeric order for comparison."""
    order = {"aware": 0, "practicing": 1, "capable": 2, "proficient": 3, "master": 4}
    return order.get(level.lower(), 0)
