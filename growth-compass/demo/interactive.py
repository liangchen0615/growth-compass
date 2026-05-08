"""
Growth Compass — Interactive Agent Demo

A terminal-based interactive session where you use the Growth Compass
as a real user would. Type commands, capture growth, see your data evolve.

Run: $env:PYTHONUTF8=1; python demo/interactive.py
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GrowthCompassAgent
from src.knowledge import list_all_skills, get_roles

DATA_FILE = Path(__file__).parent.parent / "demo" / "journal_data.json"

# ── Display helpers ────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def box(text: str):
    width = max(len(line) for line in text.split("\n")) + 4
    print("+" + "-" * (width - 2) + "+")
    for line in text.split("\n"):
        print(f"| {line:<{width - 4}} |")
    print("+" + "-" * (width - 2) + "+")


def wait():
    input("\n  Press Enter to continue...")


def heading(text: str):
    print(f"\n  {'=' * 56}")
    print(f"  {text}")
    print(f"  {'=' * 56}\n")


# ── Data persistence ───────────────────────────────────────

def save_agent(agent: GrowthCompassAgent):
    """Save journal entries to JSON."""
    data = {
        "user_name": agent.user_name,
        "entries": [
            {
                "id": e.id,
                "date": e.date.isoformat(),
                "category": e.category.value,
                "summary": e.summary,
                "primary_skill": e.primary_skill,
                "secondary_skills": e.secondary_skills,
                "significance": e.significance.value,
                "context": e.context,
                "role": e.role,
                "hard_part": e.hard_part,
                "outcome": e.outcome,
                "key_insight": e.key_insight,
                "reflection": e.reflection,
            }
            for e in agent.journal.entries
        ],
    }
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_agent(provider: str = "anthropic", model: str | None = None, base_url: str | None = None) -> GrowthCompassAgent:
    """Load journal entries from JSON, or return fresh agent."""
    if not DATA_FILE.exists():
        return GrowthCompassAgent(provider=provider, model=model, base_url=base_url)

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    agent = GrowthCompassAgent(
        user_name=data.get("user_name", ""),
        provider=provider,
        model=model,
        base_url=base_url,
    )

    from src.models import GrowthEntry, EntryCategory, Significance

    for e_data in data.get("entries", []):
        entry = GrowthEntry(
            id=e_data["id"],
            date=date.fromisoformat(e_data["date"]),
            category=EntryCategory(e_data["category"]),
            summary=e_data["summary"],
            primary_skill=e_data["primary_skill"],
            secondary_skills=e_data.get("secondary_skills", []),
            significance=Significance(e_data["significance"]),
            context=e_data.get("context", ""),
            role=e_data.get("role", ""),
            hard_part=e_data.get("hard_part", ""),
            outcome=e_data.get("outcome", ""),
            key_insight=e_data.get("key_insight", ""),
            reflection=e_data.get("reflection", ""),
        )
        agent.journal.add_entry(entry)

    return agent


# ── Interactive flows ──────────────────────────────────────

def flow_capture(agent: GrowthCompassAgent):
    """Walk the user through capturing a growth moment."""
    clear()
    heading("CAPTURE GROWTH MOMENT")

    print("  I'll ask you a few questions about something you did,")
    print("  learned, or struggled with. Be specific — the details")
    print("  are what make growth visible.\n")

    # 1. What happened
    print("  1. In one sentence, what happened?")
    summary = input("  > ").strip()
    if not summary:
        print("\n  (Capture cancelled)")
        wait()
        return None

    # 2. Category
    print("\n  2. What kind of experience was this?")
    print("     [1] Project/Delivery   [2] Learning/Study")
    print("     [3] Received Feedback   [4] Struggle/Difficulty")
    print("     [5] Milestone/Achievement")
    cat_choice = input("  Choose [1-5]: ").strip()
    cat_map = {"1": "Project", "2": "Learning", "3": "Feedback", "4": "Struggle", "5": "Milestone"}
    category = cat_map.get(cat_choice, "Project")

    # 3. Primary skill
    all_skills = list_all_skills()
    print("\n  3. What's the MAIN skill you exercised or developed?")
    for i, s in enumerate(all_skills, 1):
        print(f"     [{i:2d}] {s['label']} ({s['domain']})")
    skill_choice = input("  Choose number: ").strip()
    try:
        primary_skill = all_skills[int(skill_choice) - 1]["id"]
    except (ValueError, IndexError):
        print("  Invalid choice. Using 'ai_building' as default.")
        primary_skill = "ai_building"

    # 4. Significance
    print("\n  4. How much did this stretch you?")
    print("     [1] Stretch — first time or significantly harder than before")
    print("     [2] Practice — reinforcing an existing skill")
    print("     [3] Exposure — observed or learned about it, didn't do it yet")
    sig_choice = input("  Choose [1-3]: ").strip()
    sig_map = {"1": "Stretch", "2": "Practice", "3": "Exposure"}
    significance = sig_map.get(sig_choice, "Practice")

    # 5. Optional details
    print("\n  5. Quick context (optional) — What was the situation?")
    context = input("  > ").strip()

    print("\n  6. What was YOUR role in this? (optional)")
    role = input("  > ").strip()

    print("\n  7. What was genuinely HARD about it? (optional)")
    hard_part = input("  > ").strip()

    print("\n  8. What was the outcome? (optional)")
    outcome = input("  > ").strip()

    print("\n  9. What's one key insight you'll take forward? (optional)")
    key_insight = input("  > ").strip()

    # Capture
    result = agent.capture(
        summary=summary,
        primary_skill=primary_skill,
        category=category,
        significance=significance,
        context=context,
        role=role,
        hard_part=hard_part,
        outcome=outcome,
        key_insight=key_insight,
    )

    save_agent(agent)

    print(f"\n  [OK] Growth moment captured! (entry #{result['entry_id']})")
    print(f"  Skill: {primary_skill} | {significance} | {category}")
    wait()
    return result


def flow_capture_llm(agent: GrowthCompassAgent):
    """Natural language capture via LLM conversation."""
    clear()
    heading("CAPTURE GROWTH MOMENT (AI-POWERED)")

    if not agent.llm or not agent.llm.available:
        print("  LLM not available. Falling back to structured form.\n")
        wait()
        return flow_capture(agent)

    print("  Describe what you worked on, learned, or struggled with.")
    print("  Just tell me naturally — I'll figure out the structure.")
    print("  Press Enter on a blank line when you're done.\n")

    lines = []
    while True:
        line = input("  > ").strip()
        if not line:
            if lines:
                break
            print("\n  (Capture cancelled)")
            wait()
            return None
        lines.append(line)

    full_input = " ".join(lines)
    print("\n  Processing...")

    result = agent.capture_natural(full_input)

    if result.get("status") == "captured":
        e = result["entry"]
        print(f"\n  [OK] Growth moment captured!")
        print(f"  Summary: {e['summary']}")
        print(f"  Skill: {e['primary_skill']} | {e['significance']} | {e['category']}")
        save_agent(agent)
    elif result.get("status") == "needs_more_info":
        follow_up = result.get("follow_up", "")
        print(f"\n  {follow_up}")
        extra = input("  > ").strip()
        if extra:
            combined = f"{full_input}\n\nAdditional context: {extra}"
            result2 = agent.capture_natural(combined)
            if result2.get("status") == "captured":
                e = result2["entry"]
                print(f"\n  [OK] Growth moment captured!")
                print(f"  Summary: {e['summary']}")
                print(f"  Skill: {e['primary_skill']} | {e['significance']} | {e['category']}")
                save_agent(agent)
            else:
                print("\n  Let me use the structured form instead.\n")
                return flow_capture(agent)
    else:
        print("\n  Falling back to structured form.\n")
        return flow_capture(agent)

    wait()
    return result


def flow_skill_map(agent: GrowthCompassAgent):
    """Display the user's skill map."""
    clear()
    heading("YOUR SKILL MAP")

    if not agent.journal.entries:
        print("  No growth entries yet. Capture some moments first!\n")
        wait()
        return

    skill_map = agent.map_skills()

    print(f"  Entries analyzed: {skill_map['entries_analyzed']}")
    print(f"  Skills with evidence: {len(skill_map['skills'])}\n")

    # Skills with evidence
    if skill_map["skills"]:
        print("  SKILLS BY LEVEL:")
        print(f"  {'Skill':<30} {'Level':<15} {'Confidence':<12} {'Entries':<8}")
        print(f"  {'-'*30} {'-'*15} {'-'*12} {'-'*8}")
        for sid, s in sorted(skill_map["skills"].items(), key=lambda x: x[1]["level"]):
            bar = "=" * s["entries"] if s["entries"] < 8 else "=" * 8
            print(f"  {s['label']:<30} {s['level']:<15} {s['confidence']:<12} {bar}")

    # Strengths
    if skill_map["strengths"]:
        print(f"\n  STRENGTHS: {', '.join(skill_map['strengths'])}")

    # Growth edges
    if skill_map["growth_edges"]:
        print(f"  GROWING:   {', '.join(skill_map['growth_edges'])}")

    # Blind spots
    if skill_map["blind_spots"]:
        print(f"  BLINDSPOTS: {', '.join(skill_map['blind_spots'][:5])}")

    # Superpower
    if skill_map["superpower"]:
        print(f"\n  SUPERPOWER COMBINATION: {skill_map['superpower']}")

    # Pattern notes
    print(f"\n  {skill_map['pattern_notes']}\n")
    wait()


def flow_plan(agent: GrowthCompassAgent):
    """Generate a development plan."""
    clear()
    heading("DEVELOPMENT PLAN")

    if not agent.journal.entries:
        print("  Need at least a few growth entries before generating a plan.\n")
        wait()
        return

    # Show target roles
    roles_data = get_roles()
    role_list = list(roles_data.get("roles", {}).items())

    print("  Where do you want to go? Available target profiles:\n")
    for i, (rid, rdata) in enumerate(role_list, 1):
        print(f"  [{i}] {rdata['label']}")
        print(f"      {rdata.get('key_differentiator', '')}\n")

    choice = input("  Choose target role number: ").strip()
    try:
        target_id = role_list[int(choice) - 1][0]
    except (ValueError, IndexError):
        print("\n  Invalid choice. Targeting 'Senior Engineer' by default.")
        target_id = "senior_engineer"

    print(f"\n  Generating plan...")
    plan = agent.plan(target_id)

    print(f"\n  TARGET: {plan['target']}")
    print(f"  {plan['current_summary']}\n")

    print("  PRIORITY GAPS:")
    for g in plan["gaps"]:
        print(f"  [{g['priority']}] {g['skill']}: {g['current']} -> {g['target']} ({g['learning_mode']})")

    print(f"\n  30-DAY SPRINT:")
    for w in plan["sprint_30"]:
        print(f"  Week {w['week']}: {w['focus']}")
        print(f"    -> {w['action']}")

    print(f"\n  RISKS:")
    for r in plan["risks"]:
        print(f"  [!] {r['risk']}")
        print(f"      {r['mitigation']}")

    print(f"\n  LEARNING EDGE:")
    print(f"  {plan['learning_edge']}\n")
    wait()


def flow_report(agent: GrowthCompassAgent):
    """Generate a growth report."""
    clear()
    heading("GROWTH REPORT")

    if not agent.journal.entries:
        print("  No entries to report on yet. Capture some moments first!\n")
        wait()
        return

    print("  Choose report period:")
    print("  [1] Monthly   [2] Quarterly   [3] Custom")
    choice = input("  > ").strip()
    period_map = {"1": "Monthly", "2": "Quarterly", "3": "Custom Period"}
    period = period_map.get(choice, "Monthly")

    print("\n  Generating report...")
    report = agent.report(period)

    print(f"\n  {'='*20} GROWTH REPORT — {report['period']} {'='*20}")
    print(f"  Entries: {report['entries_count']} | Skills: {report['skills_demonstrated']}")
    print(f"  Leveled up: {report['skills_leveled_up']} | Stretch: {report['stretch_count']}")

    if report["key_moments"]:
        print(f"\n  KEY MOMENTS:")
        for m in report["key_moments"]:
            print(f"  * {m['title']}")
            print(f"    {m['why_it_mattered'][:100]}")

    if report["patterns"]:
        print(f"\n  PATTERNS:")
        for p in report["patterns"]:
            print(f"  * {p[:120]}")

    if report["next_priorities"]:
        print(f"\n  NEXT FOCUS: {report['next_focus']}")
        for p in report["next_priorities"]:
            print(f"  -> {p}")

    print(f"\n  REFLECTION: {report['reflection_prompt']}")
    print(f"\n  {'─' * 52}")
    print(f"\n  SHAREABLE SUMMARY:")
    print(f"\n{report['shareable_summary']}")
    print()
    wait()


def flow_intro(agent: GrowthCompassAgent):
    """First-time introduction."""
    clear()
    box("""Growth Compass v1.0
AI-Powered Personal Growth Tracker

I help you make your professional growth
visible, trackable, and personalized.""")

    if not agent.journal.entries:
        print("\n  Welcome! It looks like this is your first time here.\n")
        name = input("  What should I call you? ").strip()
        if name:
            agent.user_name = name
        print(f"\n  Hi {agent.user_name}! I'm your growth companion. Here's how I work:\n")
        print("  [Capture]  Tell me what you worked on, learned, or struggled with.")
        print("            I'll structure it into growth data.")
        print()
        print("  [Map]      I'll build a skill graph showing what you've demonstrated,")
        print("            at what level, with what evidence.")
        print()
        print("  [Plan]     Pick a target role, and I'll generate a personalized")
        print("            30/60/90 day development plan.")
        print()
        print("  [Report]   I'll produce a growth visibility report — patterns,")
        print("            key moments, and what to focus on next.")
        print()
        print("  Start by capturing a growth moment!")
    else:
        stats = agent.journal.stats()
        print(f"\n  Welcome back, {agent.user_name}!")
        print(f"  You have {stats['total_entries']} entries across {stats['unique_skills']} skills.")
        print(f"  Latest entry: {stats['latest_entry']}")

    wait()


def main_menu(agent: GrowthCompassAgent) -> bool:
    """Show main menu and handle choice. Returns False to exit."""
    clear()
    stats = agent.journal.stats()
    llm_status = agent.llm.available if agent.llm else False
    ai_tag = " [AI ON]" if llm_status else ""
    print()
    box(f"Growth Compass — {agent.user_name}   |   {stats['total_entries']} entries   |   {stats['unique_skills']} skills{ai_tag}")
    print()
    if llm_status:
        print("  [1] Capture a growth moment (natural language)")
        print("  [1f] Capture with structured form")
    else:
        print("  [1] Capture a growth moment")
    print("  [2] View my skill map")
    print("  [3] Generate a development plan")
    print("  [4] View growth report")
    print("  [5] About / Stats")
    print("  [6] Exit")
    print()
    choice = input("  What would you like to do? [1-6]: ").strip()

    if choice in ("1", "1f"):
        if choice == "1f":
            flow_capture(agent)
        elif llm_status:
            flow_capture_llm(agent)
        else:
            flow_capture(agent)
    elif choice == "2":
        flow_skill_map(agent)
    elif choice == "3":
        flow_plan(agent)
    elif choice == "4":
        flow_report(agent)
    elif choice == "5":
        flow_about(agent)
    elif choice == "6":
        clear()
        print("\n  See you next time. Keep growing!\n")
        return False
    return True


def flow_about(agent: GrowthCompassAgent):
    """Show agent stats and info."""
    clear()
    heading("ABOUT GROWTH COMPASS")

    stats = agent.stats()
    print(f"  User: {agent.user_name}")
    print(f"  Session started: {stats['session_start']}")
    print(f"  Days active: {stats['session_days']}")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Unique skills touched: {stats['unique_skills']}")
    print(f"  Stretch experiences: {stats['stretch_count']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  First entry: {stats['first_entry']}")
    print(f"  Latest entry: {stats['latest_entry']}")
    status = agent.status()
    print(f"  LLM available: {status.get('llm_available', False)}")
    print()
    print("  Growth Compass is an AI-native approach to talent development.")
    print("  It demonstrates: making growth visible, trackable, and personalized")
    print("  through structured data capture, skill mapping, and AI-powered")
    print("  development planning. An AI-native approach to making human")
    print("  growth visible, trackable, and personalized.")
    print()
    wait()


# ── Main ────────────────────────────────────────────────────

def main():
    # Auto-detect provider from available API keys
    provider = os.environ.get("GROWTH_COMPASS_PROVIDER", "")
    if not provider:
        if os.environ.get("DEEPSEEK_API_KEY"):
            provider = "deepseek"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "anthropic"

    model = os.environ.get("GROWTH_COMPASS_MODEL")
    base_url = os.environ.get("GROWTH_COMPASS_BASE_URL")

    agent = load_agent(provider=provider, model=model, base_url=base_url)
    flow_intro(agent)
    running = True
    while running:
        running = main_menu(agent)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  See you next time. Keep growing!\n")
