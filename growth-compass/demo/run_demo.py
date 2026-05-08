"""
Growth Compass — End-to-End Demo

Simulates 3 months of an engineer's growth journey, demonstrating all
four agent skills: Capture -> Map -> Plan -> Report.

Usage:
  python demo/run_demo.py             # Heuristic mode (no API key needed)
  python demo/run_demo.py --llm       # LLM-powered plan and report (needs ANTHROPIC_API_KEY)
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GrowthCompassAgent


def divider(title: str):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def section(title: str):
    print(f"\n--- {title} ---\n")


def print_entry(result: dict):
    e = result["entry"]
    print(f"  [OK] Captured: {e['summary']}")
    print(f"       Skill: {e['primary_skill']} | {e['significance']} | {e['category']}")
    if e["key_insight"]:
        print(f"       Insight: {e['key_insight']}")


def main():
    parser = argparse.ArgumentParser(description="Growth Compass 3-month demo")
    parser.add_argument("--llm", action="store_true", help="Use LLM for plan and report generation")
    parser.add_argument("--provider", type=str, default="anthropic", choices=["anthropic", "deepseek", "openai"], help="LLM provider (default: anthropic)")
    parser.add_argument("--api-key", type=str, help="API key (default: provider-specific env var)")
    parser.add_argument("--model", type=str, help="Model name (default: provider-specific default)")
    parser.add_argument("--base-url", type=str, help="Custom base URL for OpenAI-compatible providers")
    args = parser.parse_args()

    api_key = args.api_key
    use_llm = args.llm

    # ── Initialize ────────────────────────────────────────────
    if use_llm:
        mode_tag = f" [LLM MODE — {args.provider}]"
        agent = GrowthCompassAgent(
            user_name="Chen",
            provider=args.provider,
            api_key=api_key,
            model=args.model,
            base_url=args.base_url,
            use_llm=True,
        )
    else:
        mode_tag = " [Heuristic Mode]"
        agent = GrowthCompassAgent(user_name="Chen", use_llm=False)

    # ── Phase 1: Data Foundation (Week 1-4) ──────────────────
    divider("PHASE 1 — Building the Evidence Base (Weeks 1-4)")

    print("\n  Capturing growth moments from daily work...\n")

    # Week 1 — System Design
    r = agent.capture(
        summary="Designed rate limiter for notification service",
        primary_skill="system_design",
        category="Project",
        significance="Stretch",
        context="Notification service hitting downstream limits under load",
        role="Led the design, wrote the design doc, got review from Staff Engineer",
        hard_part="Choosing between token bucket and sliding window — tradeoffs were subtle",
        outcome="Design approved. Token bucket chosen for simplicity, with escape hatch for sliding window later.",
        key_insight="Good designs leave room to change your mind. The escape hatch cost almost nothing but buys a lot of optionality.",
    )
    print_entry(r)

    # Week 2 — AI Building
    r = agent.capture(
        summary="Built an AI-powered code review assistant for the team",
        primary_skill="ai_building",
        category="Project",
        significance="Stretch",
        context="Team spending too much time on mechanical review comments. Wanted to free up brain cycles for design discussion.",
        role="Built the AI agent, wrote the prompt chain, set up the knowledge base with our coding standards",
        hard_part="Getting the agent to distinguish between style nits vs. real bugs. Had to iterate the prompt 15+ times.",
        outcome="Agent now catches 80% of mechanical issues. Team reviews are more focused on architecture and design.",
        key_insight="Prompt engineering is 90% defining what 'good' looks like and 10% writing the words.",
    )
    print_entry(r)

    # Week 3 — Initiative + Problem Definition
    r = agent.capture(
        summary="Spotted and fixed a silent data corruption bug in payment pipeline",
        primary_skill="debugging",
        secondary_skills=["initiative", "problem_definition"],
        category="Project",
        significance="Stretch",
        context="Noticed payment reconciliation was off by 0.3% for 2 weeks. Nobody had flagged it.",
        role="Investigated independently, traced through 5 services, found the race condition",
        hard_part="The bug only manifested under specific concurrency patterns. Took 3 days to reproduce reliably.",
        outcome="Fix deployed. Root cause was a missing idempotency key in the retry path. Also added monitoring to catch this class of issue.",
        key_insight="The hardest bugs aren't the ones that fail loudly — they're the ones that almost succeed.",
    )
    print_entry(r)

    # Week 4 — Mentoring
    r = agent.capture(
        summary="Onboarded a new team member and created a 2-week ramp-up plan",
        primary_skill="mentoring",
        category="Learning",
        significance="Practice",
        context="Junior engineer joined the team. Existing onboarding docs were outdated.",
        role="Created structured onboarding with bite-sized tasks, each building on the last",
        hard_part="Resisting the urge to just do things myself. Letting them struggle productively.",
        outcome="New hire shipped their first PR in week 2. Onboarding doc is now the team standard.",
        key_insight="Good onboarding isn't about transferring information — it's about building confidence through small wins.",
    )
    print_entry(r)

    # Week 4 bonus — Struggle entry
    r = agent.capture(
        summary="Sprint planning went badly — I over-promised and the team missed commitments",
        primary_skill="decision_making",
        secondary_skills=["communication"],
        category="Struggle",
        significance="Stretch",
        context="Under pressure to show velocity. Committed to 3 features. Team only delivered 1.",
        role="I was the lead for this sprint. The estimates were mine.",
        hard_part="Admitting to the team and my manager that I'd misjudged. The silence in the retro was brutal.",
        outcome="Changed estimation approach. Now we do a 'pre-mortem' before committing. Next sprint hit all targets.",
        key_insight="Over-promising isn't ambition — it's avoiding a hard conversation. The hard conversation is cheaper.",
    )
    print_entry(r)

    # ── Phase 2: Map Skills ──────────────────────────────────
    divider("PHASE 2 — Skill Map (End of Month 1)")

    skill_map = agent.map_skills()

    section("Strengths")
    for s in skill_map["strengths"]:
        print(f"  * {s}")
    if not skill_map["strengths"]:
        print("  (Building foundations — keep capturing)")

    section("Growth Edges (Rising)")
    for s in skill_map["growth_edges"]:
        print(f"  -> {s}")

    section("Blind Spots")
    for s in skill_map["blind_spots"]:
        print(f"  !! {s}")
    if not skill_map["blind_spots"]:
        print("  (None detected)")

    section("Superpower")
    print(f"  !! {skill_map['superpower']}")

    print(f"\n  Pattern Notes: {skill_map['pattern_notes']}")

    # ── Phase 3: More Growth Data (Week 5-8) ──────────────────
    divider("PHASE 3 — Deepening Evidence (Weeks 5-8)")

    print("\n  Capturing more diverse growth moments...\n")

    agent.capture(
        summary="Ran user interviews to understand why onboarding drop-off was high",
        primary_skill="user_insight",
        category="Learning",
        significance="Stretch",
        context="Our onboarding flow had 40% drop-off. Nobody had talked to actual users about why.",
        role="Conducted 8 user interviews, synthesized findings, presented to product",
        hard_part="First interview was terrible — I led the witness. Had to unlearn and re-learn how to listen.",
        outcome="Found 3 root causes. Product team prioritized 2 fixes. Drop-off improved to 18%.",
        key_insight="What users say and what they need are different things. The skill is hearing the need behind the complaint.",
    )

    agent.capture(
        summary="Ship an AI workflow for automated regression test analysis",
        primary_skill="ai_building",
        secondary_skills=["rapid_ai_prototyping", "shipping"],
        category="Project",
        significance="Stretch",
        context="Regression test failures were piling up. Engineers spent hours triaging flaky tests.",
        role="Built and shipped an AI agent that analyzes test failures, identifies root causes, and suggests fixes",
        hard_part="Getting the agent to understand our test framework's idiosyncrasies. Required building a test-specific knowledge base.",
        outcome="Agent handling 60% of triage. Mean time to resolution dropped from 4 hours to 1.5 hours. 2 other teams adopting it.",
        key_insight="The best AI use cases aren't new problems — they're existing pain points where AI can take first pass and humans do the judgment.",
    )

    agent.capture(
        summary="Mentored 2 junior engineers through their first system design reviews",
        primary_skill="mentoring",
        secondary_skills=["communication"],
        category="Learning",
        significance="Stretch",
        context="Juniors were nervous about design reviews. Needed to build their confidence and framework.",
        role="Ran 3 mock review sessions, taught them a 5-question design framework, attended their real reviews",
        hard_part="Not jumping in to answer for them during the real review. Letting the silence happen.",
        outcome="Both passed their reviews. One said 'I actually enjoyed it' — biggest win.",
        key_insight="Teaching someone to think is harder than teaching them to do. But it's the only thing that scales.",
    )

    agent.capture(
        summary="Defined and shipped metrics dashboard for AI code review agent",
        primary_skill="data_thinking",
        secondary_skills=["shipping"],
        category="Project",
        significance="Practice",
        context="Needed to prove the AI code review agent was actually helping, not just generating noise",
        role="Defined metrics (false positive rate, issue severity distribution, reviewer time saved), built dashboard",
        hard_part="Defining 'time saved' credibly. Had to instrument before/after comparison.",
        outcome="Dashboard live. Data shows 3.5 hours/week saved per engineer. Used the data to get buy-in for expanding the agent.",
        key_insight="AI adoption lives or dies on measurement. Without numbers, it's an opinion. With numbers, it's a decision.",
    )

    print("  +4 more entries captured.\n")

    # ── Phase 4: Generate Development Plan ────────────────────
    divider("PHASE 4 — Development Plan: Senior Engineer Track")

    plan = agent.plan("senior_engineer")

    print(f"\n  Target: {plan['target']}")
    print(f"  {plan['current_summary']}")

    section("Priority Gaps")
    for g in plan["gaps"]:
        bar = "█" * g["gap_size"] + "░" * (4 - g["gap_size"])
        print(f"  [{g['priority']}] {g['skill']}: {g['current']} {bar} {g['target']} ({g['learning_mode']})")

    section("30-Day Sprint")
    for w in plan["sprint_30"]:
        print(f"  Week {w['week']} | {w['focus']}")
        print(f"          → {w['action']}")
        print(f"          ✓ {w['success']}")

    section("Risks")
    for r in plan["risks"]:
        print(f"  ⚠ {r['risk']}")
        print(f"    → {r['mitigation']}")

    section("Learning Edge")
    print(f"  {plan['learning_edge']}")

    # ── Phase 5: Final Growth Data (Week 9-12) ───────────────
    divider("PHASE 5 — Closing Gaps (Weeks 9-12)")

    print("\n  Working on priority gaps from the plan...\n")

    agent.capture(
        summary="Redesigned team's CI/CD pipeline — cut build time by 60%",
        primary_skill="system_design",
        secondary_skills=["shipping", "initiative"],
        category="Project",
        significance="Stretch",
        context="Build times creeping up, slowing down the entire team. My 30-day sprint target.",
        role="Analyzed bottlenecks, proposed new architecture, led migration",
        hard_part="Had to keep old pipeline running during migration. Zero-downtime requirement meant careful orchestration.",
        outcome="Build time from 22 min → 9 min. Estimated 40 engineer-hours saved per month across the team.",
        key_insight="Infrastructure improvements are the highest-leverage work — they compound across the entire team.",
    )

    agent.capture(
        summary="Gave a tech talk on 'AI-Native Development' at company engineering forum",
        primary_skill="communication",
        secondary_skills=["ai_first_thinking", "mentoring"],
        category="Milestone",
        significance="Stretch",
        context="Engineering org doesn't have a shared vocabulary for AI-native development. Wanted to change that.",
        role="Researched, wrote, and delivered a 30-minute talk with live demos",
        hard_part="Making it concrete. Talks without demos are just opinions. Built 3 live demos to ground the concepts.",
        outcome="120 attendees. Talk spawned 4 follow-up discussions. VP of Eng asked for a version for the leadership team.",
        key_insight="Teaching forces you to confront what you don't actually understand. Preparing this talk deepened my own thinking.",
    )

    agent.capture(
        summary="Led postmortem for a production incident and drove the follow-up actions",
        primary_skill="decision_making",
        secondary_skills=["communication", "initiative", "problem_definition"],
        category="Project",
        significance="Stretch",
        context="Major outage in payment service. I wasn't on call but stepped in to lead the postmortem process.",
        role="Facilitated the postmortem, wrote the timeline, drove action items to completion",
        hard_part="Keeping the postmortem blameless when the root cause was clearly a specific commit. Reframing from 'who' to 'how did our process allow this.'",
        outcome="5 action items all completed. New pre-commit check would have caught this. Mentored 2 others on running postmortems.",
        key_insight="The best postmortems change the system, not the person. If you're naming individuals, you're doing it wrong.",
    )

    print("  +3 more entries captured.\n")

    # ── Phase 6: Final Growth Report ─────────────────────────
    divider("PHASE 6 — Quarterly Growth Report (Mar 2026)")

    report = agent.report("Q1 2026")

    print(f"\n  📊 Period: {report['period']}")
    print(f"  📝 Total entries: {report['entries_count']}")
    print(f"  🎯 Skills demonstrated: {report['skills_demonstrated']}")
    print(f"  📈 Skills leveled up: {report['skills_leveled_up']}")
    print(f"  💪 Stretch experiences: {report['stretch_count']}")

    section("Key Moments")
    for i, m in enumerate(report["key_moments"], 1):
        print(f"  {i}. {m['title']}")
        print(f"     Why it mattered: {m['why_it_mattered'][:120]}")

    section("Patterns & Themes")
    for p in report["patterns"]:
        print(f"  • {p[:120]}")

    section("Focus for Next Quarter")
    print(f"  Theme: {report['next_focus']}")
    for p in report["next_priorities"]:
        print(f"  → {p}")

    section("Reflection Prompt")
    print(f"  ❓ {report['reflection_prompt']}")

    # ── Shareable Summary ────────────────────────────────────
    divider("SHAREABLE SUMMARY (for Manager Review)")
    print(f"\n{report['shareable_summary']}")

    # ── Agent Stats ──────────────────────────────────────────
    divider("AGENT STATS")
    stats = agent.stats()
    print(f"\n  Session: {stats['session_start']}")
    print(f"  Total entries in journal: {stats['total_entries']}")
    print(f"  Unique skills touched: {stats['unique_skills']}")
    print(f"  Stretch experiences: {stats['stretch_count']}")
    print(f"  Entry categories: {stats['categories']}")

    divider("DEMO COMPLETE")
    print(f"\n  Growth Compass transformed {agent.user_name}'s growth from")
    print(f"  invisible → visible, anecdotal → evidence-based, generic → personalized.")
    print(f"\n  This is what 'rebuilding talent development with AI' looks like.")
    print()


if __name__ == "__main__":
    main()
