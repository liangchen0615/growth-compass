"""LLM Client — multi-provider support for Growth Compass intelligence.

Supports: Anthropic, DeepSeek, OpenAI, and any OpenAI-compatible endpoint.

Usage:
  client = LLMClient(provider="deepseek")    # reads DEEPSEEK_API_KEY from env
  client = LLMClient(provider="anthropic")   # reads ANTHROPIC_API_KEY from env
  client = LLMClient(provider="openai")      # reads OPENAI_API_KEY from env
  client = LLMClient(provider="openai", base_url="https://custom.api/v1")  # custom

Every method returns None on failure so callers can fall back to heuristics.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Type

import anthropic
from openai import OpenAI
from pydantic import BaseModel

from .models import (
    SkillAssessment,
    PatternAnalysis,
    DevPlanOutput,
    ReportOutput,
    CaptureOutput,
)

AGENT_DIR = Path(__file__).parent.parent / "agent"
SKILLS_DIR = AGENT_DIR / "skills"
KB_DIR = AGENT_DIR / "knowledge_base"

# ── Provider config ─────────────────────────────────────────

PROVIDER_CONFIG = {
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "base_url": None,
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": None,
    },
}

# ── File readers ────────────────────────────────────────────

def _read_md(filename: str) -> str:
    path = AGENT_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def _read_skill_md(skill_name: str) -> str:
    path = SKILLS_DIR / f"{skill_name}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def _read_json(filename: str) -> dict:
    path = KB_DIR / filename
    if path.exists():
        return json.loads(path.read_bytes())
    return {}


# ── LLM Client ──────────────────────────────────────────────

class LLMClient:
    """Multi-provider LLM client for Growth Compass.

    Uses Anthropic SDK for 'anthropic' provider.
    Uses OpenAI SDK for 'deepseek', 'openai', or custom providers.
    """

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        config = PROVIDER_CONFIG.get(provider, {})
        self.provider = provider
        self.api_key = api_key or os.environ.get(config.get("env_key", ""))
        self.base_url = base_url or config.get("base_url")

        # Set default model based on provider
        if model:
            self.model = model
        elif provider == "deepseek":
            self.model = "deepseek-chat"
        elif provider == "openai":
            self.model = "gpt-4o"
        else:
            self.model = "claude-sonnet-4-20250514"

        self.client = None
        self.anthropic_client = None
        self.openai_client = None

        if not self.api_key:
            return

        if provider == "anthropic":
            self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
        else:
            # DeepSeek, OpenAI, or custom OpenAI-compatible
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.openai_client = OpenAI(**kwargs)

        self.client = self.anthropic_client or self.openai_client
        self._kb_cache_text: str | None = None

    @property
    def available(self) -> bool:
        return self.client is not None

    # ── Knowledge Base Context (lazy, cached) ────────────────

    def _get_kb_context(self) -> str:
        if self._kb_cache_text is not None:
            return self._kb_cache_text

        taxonomy = _read_json("skills_taxonomy.json")
        roles = _read_json("roles.json")

        lines = ["## Competency Taxonomy (Reference)"]
        for domain_id, domain in taxonomy.get("domains", {}).items():
            lines.append(f"\n### {domain['label']}")
            for comp_id, comp in domain.get("competencies", {}).items():
                levels_summary = ", ".join(
                    f"{lvl}: {desc[:60]}..."
                    for lvl, desc in comp.get("levels", {}).items()
                )
                lines.append(f"- **{comp_id}** ({comp['label']}): {comp['description']}")
                lines.append(f"  Levels: {levels_summary}")

        lines.append("\n## Role Profiles (Reference)")
        for role_id, role_data in roles.get("roles", {}).items():
            lines.append(f"\n### {role_data['label']} ({role_id})")
            lines.append(f"Key differentiator: {role_data.get('key_differentiator', '')}")
            expectations = role_data.get("expectations", {})
            if expectations:
                lines.append("Expected levels:")
                for skill_id, level in expectations.items():
                    lines.append(f"  - {skill_id}: {level}")

        self._kb_cache_text = "\n".join(lines)
        return self._kb_cache_text

    # ── Core API Call (provider dispatch) ────────────────────

    def _call_structured(
        self,
        response_model: Type[BaseModel],
        system: str,
        user_prompt: str,
        kb_context: bool = True,
        max_tokens: int = 4096,
    ) -> BaseModel | None:
        """Dispatch to the right API based on provider."""
        if not self.available:
            return None

        if self.anthropic_client:
            return self._call_anthropic(response_model, system, user_prompt, kb_context, max_tokens)
        elif self.openai_client:
            return self._call_openai_compatible(response_model, system, user_prompt, kb_context, max_tokens)
        return None

    def _call_anthropic(
        self,
        response_model: Type[BaseModel],
        system: str,
        user_prompt: str,
        kb_context: bool,
        max_tokens: int,
    ) -> BaseModel | None:
        """Call Anthropic Messages API with tool use."""
        content_blocks = []

        if kb_context:
            content_blocks.append({
                "type": "text",
                "text": self._get_kb_context(),
                "cache_control": {"type": "ephemeral"},
            })

        content_blocks.append({"type": "text", "text": user_prompt})
        tool_name = response_model.__name__

        for attempt in range(3):
            try:
                response = self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": content_blocks}],
                    tools=[{
                        "name": tool_name,
                        "description": f"Return a {tool_name} structured object",
                        "input_schema": response_model.model_json_schema(),
                    }],
                    tool_choice={"type": "tool", "name": tool_name},
                    extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
                )

                for block in response.content:
                    if block.type == "tool_use" and block.name == tool_name:
                        try:
                            return response_model.model_validate(block.input)
                        except Exception:
                            return None

                # Fallback: try text content as JSON
                for block in response.content:
                    if block.type == "text":
                        try:
                            return response_model.model_validate(json.loads(block.text))
                        except (json.JSONDecodeError, Exception):
                            continue
                return None

            except anthropic.RateLimitError:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except anthropic.APIStatusError as e:
                if e.status_code in (429, 500, 502, 503) and attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except (anthropic.APIConnectionError, Exception):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return None
        return None

    def _call_openai_compatible(
        self,
        response_model: Type[BaseModel],
        system: str,
        user_prompt: str,
        kb_context: bool,
        max_tokens: int,
    ) -> BaseModel | None:
        """Call OpenAI-compatible API (DeepSeek, OpenAI, custom) with function calling."""
        full_user_prompt = user_prompt
        if kb_context:
            full_user_prompt = self._get_kb_context() + "\n\n" + user_prompt

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": full_user_prompt},
        ]

        tool_name = response_model.__name__
        json_schema = response_model.model_json_schema()

        # Clean schema for OpenAI compatibility (remove $defs if present, simplify)
        def clean_schema(schema: dict) -> dict:
            """Remove fields that some OpenAI-compatible APIs reject."""
            cleaned = {}
            for k, v in schema.items():
                if k in ("$schema", "$defs", "additionalProperties"):
                    continue
                if k == "properties":
                    cleaned[k] = {
                        pk: {pk2: pv2 for pk2, pv2 in pv.items() if pk2 != "title"}
                        for pk, pv in v.items()
                    }
                elif isinstance(v, dict):
                    cleaned[k] = clean_schema(v)
                else:
                    cleaned[k] = v
            return cleaned

        tools = [{
            "type": "function",
            "function": {
                "name": tool_name,
                "description": f"Return a {tool_name} structured object",
                "parameters": clean_schema(json_schema),
            },
        }]

        for attempt in range(3):
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice={"type": "function", "function": {"name": tool_name}},
                    max_tokens=max_tokens,
                    temperature=0.2,
                )

                choice = response.choices[0]
                if choice.message.tool_calls:
                    args_str = choice.message.tool_calls[0].function.arguments
                    try:
                        return response_model.model_validate(json.loads(args_str))
                    except (json.JSONDecodeError, Exception):
                        return None

                # Fallback: try parsing message content as JSON
                if choice.message.content:
                    try:
                        return response_model.model_validate(json.loads(choice.message.content))
                    except (json.JSONDecodeError, Exception):
                        pass
                return None

            except Exception:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return None
        return None

    # ── Public Methods ───────────────────────────────────────

    def assess_skill(
        self,
        skill_info: dict,
        entries: list,
    ) -> SkillAssessment | None:
        """Assess level, confidence, and trend for a single skill."""
        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("map_skills.md")
        )

        entries_text = "No entries for this skill yet."
        if entries:
            entries_text = "\n\n".join(
                f"Entry {i+1}:\n"
                f"  Date: {e.date.isoformat()}\n"
                f"  Summary: {e.summary}\n"
                f"  Category: {e.category.value}\n"
                f"  Significance: {e.significance.value}\n"
                f"  Context: {e.context}\n"
                f"  Role: {e.role}\n"
                f"  Hard part: {e.hard_part}\n"
                f"  Outcome: {e.outcome}\n"
                f"  Key insight: {e.key_insight}"
                for i, e in enumerate(entries)
            )

        prompt = (
            f"## Skill to Assess\n\n"
            f"Skill ID: {skill_info['id']}\n"
            f"Skill Name: {skill_info['label']}\n"
            f"Description: {skill_info['description']}\n\n"
            f"Level definitions:\n"
        )
        for lvl_name, lvl_desc in skill_info.get("levels", {}).items():
            prompt += f"- **{lvl_name}**: {lvl_desc}\n"

        prompt += f"\n## User's Growth Entries for This Skill\n\n{entries_text}"
        prompt += "\n\nAssess the user's level, confidence, and trend for this skill. Base your assessment ONLY on the evidence provided."

        return self._call_structured(SkillAssessment, system=system, user_prompt=prompt, kb_context=False)

    def identify_patterns(
        self,
        evidence_map: dict,
        all_skill_info: dict,
        user_name: str,
    ) -> PatternAnalysis | None:
        """Identify cross-skill patterns, strengths, blind spots, superpower."""
        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("map_skills.md")
        )

        skill_summaries = []
        for skill_id, ev in evidence_map.items():
            info = all_skill_info.get(skill_id, {})
            skill_summaries.append(
                f"- **{skill_id}** ({info.get('label', skill_id)}): "
                f"Level={ev.level.value}, Confidence={ev.confidence.value}, "
                f"Trend={ev.trend}, Entries={ev.entry_count}"
            )

        prompt = (
            f"## User: {user_name}\n\n"
            f"## Full Skill Evidence Summary\n\n"
            + "\n".join(skill_summaries)
            + "\n\nIdentify strengths, growth edges, blind spots, plateaus, the superpower combination, "
            "and 2-3 sentences of pattern observations. Use skill IDs (not labels) for lists."
        )

        return self._call_structured(PatternAnalysis, system=system, user_prompt=prompt)

    def generate_dev_plan(
        self,
        skill_map,
        role: dict,
        gaps: list,
    ) -> DevPlanOutput | None:
        """Generate a personalized development plan."""
        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("create_dev_plan.md")
        )

        gap_text = "\n".join(
            f"- {g.skill_label} ({g.skill_id}): {g.current_level.value} -> {g.target_level.value} "
            f"(gap: {g.gap_size} levels, priority: {g.priority_label}, mode: {g.learning_mode})"
            for g in gaps
        )

        strengths_text = ", ".join(skill_map.strengths) if skill_map.strengths else "building foundations"

        prompt = (
            f"## User: {skill_map.user_name}\n\n"
            f"## Target Role: {role.get('label', '')}\n"
            f"Key differentiator: {role.get('key_differentiator', '')}\n\n"
            f"## Current State\n"
            f"Entries analyzed: {skill_map.entries_analyzed}\n"
            f"Key strengths: {strengths_text}\n"
            f"Superpower combination: {skill_map.superpower or 'not yet identified'}\n\n"
            f"## Priority Gaps (from gap analysis)\n\n{gap_text}\n\n"
            "Generate a complete development plan with specific, concrete actions tailored to this person."
        )

        return self._call_structured(DevPlanOutput, system=system, user_prompt=prompt)

    def generate_report(
        self,
        period: str,
        entries: list,
        current_map,
        previous_map,
        dev_plan,
    ) -> ReportOutput | None:
        """Generate a growth report with key moments and patterns."""
        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("generate_growth_report.md")
        )

        entries_text = "\n\n".join(
            f"Entry {i+1}: {e.date.isoformat()} | {e.category.value} | {e.significance.value}\n"
            f"  Skill: {e.primary_skill}\n  Summary: {e.summary}\n"
            f"  Context: {e.context}\n  Role: {e.role}\n"
            f"  Hard part: {e.hard_part}\n  Outcome: {e.outcome}\n  Insight: {e.key_insight}"
            for i, e in enumerate(entries)
        )

        skill_summary = "\n".join(
            f"- {sid}: {ev.level.value} ({ev.confidence.value}), trend={ev.trend}"
            for sid, ev in current_map.skills.items() if ev.entry_count > 0
        )

        dev_plan_text = ""
        if dev_plan:
            dev_plan_text = (
                f"Active development plan targeting: {dev_plan.target_role}\n"
                f"Current summary: {dev_plan.current_summary}"
            )

        prompt = (
            f"## Period: {period}\n## Entries: {len(entries)}\n\n"
            f"## Current Skill Map\n{skill_summary}\n\n"
            f"## Dev Plan Context\n{dev_plan_text}\n\n"
            f"## All Growth Entries\n\n{entries_text}\n\n"
            "Generate a growth report. Identify 1-3 truly significant key moments. "
            "Detect 2-3 thematic patterns. Recommend concrete next-period priorities. "
            "Craft a sharp, specific reflection prompt."
        )

        return self._call_structured(ReportOutput, system=system, user_prompt=prompt)

    def extract_capture_entry(
        self,
        user_input: str,
        conversation_history: list[dict] | None = None,
    ) -> CaptureOutput | None:
        """Extract a structured growth entry from natural language input."""
        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("capture_growth_moment.md")
        )

        history_text = ""
        if conversation_history:
            history_text = "\n\n".join(
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in conversation_history
            )

        prompt = (
            f"## Conversation History\n{history_text}\n\n"
            f"## User's Latest Input\n\n{user_input}\n\n"
            "Extract as much structured information as possible from the user's description. "
            "Map the described activity to the most appropriate skill ID. "
            "Set is_complete=True if you have summary + primary_skill + significance. "
            "If you need more info, set is_complete=False and ask ONE sharp follow-up question.\n\n"
            "Available skill IDs: ai_building, system_design, coding_quality, debugging, "
            "data_thinking, communication, mentoring, initiative, decision_making, "
            "user_insight, problem_definition, shipping, ai_first_thinking, "
            "data_structuring, rapid_ai_prototyping"
        )

        return self._call_structured(CaptureOutput, system=system, user_prompt=prompt, kb_context=False)

    def generate_reflection_prompt(
        self,
        entries: list,
        skill_map,
    ) -> str | None:
        """Generate a sharp, context-specific reflection question."""
        if not entries:
            return "What's one thing you did this week that stretched you?"

        system = (
            _read_md("system_prompt.md") + "\n\n"
            + _read_skill_md("capture_growth_moment.md")
        )

        entries_summary = "\n".join(
            f"- {e.date.isoformat()}: {e.summary[:80]}..."
            for e in entries[-5:]
        )

        strengths = ", ".join(
            skill_map.skills[s].skill_label for s in skill_map.strengths[:3]
            if s in skill_map.skills
        ) or "building foundations"

        prompt = (
            f"Recent entries:\n{entries_summary}\n\n"
            f"Key strengths: {strengths}\n"
            f"Blind spots: {', '.join(skill_map.blind_spots[:3]) if skill_map.blind_spots else 'none'}\n\n"
            "Generate ONE sharp, specific reflection question. Return ONLY the question, no other text."
        )

        if not self.available:
            return None

        try:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ]
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model=self.model, max_tokens=200, system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                if response.content and response.content[0].type == "text":
                    return response.content[0].text.strip().strip('"')
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.model, messages=messages, max_tokens=200, temperature=0.5,
                )
                if response.choices[0].message.content:
                    return response.choices[0].message.content.strip().strip('"')
        except Exception:
            pass
        return None
