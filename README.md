# Growth Compass / 成长罗盘

**AI-Powered Personal Growth Tracker** — makes professional growth visible, trackable, and personalized.

**AI 驱动的个人成长追踪器** — 让职业成长可视化、可追踪、个性化。

---

Growth Compass helps engineers and technical managers track their professional growth through four AI-powered skills: **Capture** growth moments from daily work, **Map** skills into an evidence-based graph, **Plan** personalized 30/60/90 day development paths, and **Report** with visibility reports that surface patterns and blind spots.

成长罗盘通过四项 AI 技能帮助工程师和技术管理者追踪职业成长：**捕捉**工作中的成长时刻、**生成**基于证据的技能图谱、**规划**个性化 30/60/90 天发展路径、**生成**揭示模式和盲区的成长报告。

---

## Quick Start / 快速开始

```bash
cd growth-compass
pip install -r requirements.txt
python demo/run_demo.py                 # 3-month simulated demo
python demo/interactive.py              # Interactive mode
```

With LLM / 接入 AI 模型:
```powershell
$env:DEEPSEEK_API_KEY="sk-..."          # or ANTHROPIC_API_KEY / OPENAI_API_KEY
$env:PYTHONUTF8=1
python demo/interactive.py
```

Supports **Anthropic**, **DeepSeek**, **OpenAI**, and any OpenAI-compatible endpoint. Works without an API key too (heuristic fallback).

支持 **Anthropic**、**DeepSeek**、**OpenAI** 及任何兼容接口。无 API key 亦可运行（启发式降级）。

---

## Architecture / 架构

```
growth-compass/
├── agent/                  # Agent prompts + knowledge base
│   ├── system_prompt.md
│   ├── skills/             # 4 skill definitions
│   └── knowledge_base/     # Taxonomy, roles, resources
├── src/                    # Python engine
│   ├── llm.py              # Multi-provider LLM client
│   ├── agent.py            # Main orchestrator
│   ├── models.py           # Data + Pydantic response models
│   ├── skill_graph.py      # Skill mapping engine
│   ├── dev_plan.py         # Development plan generator
│   ├── report.py           # Growth report generator
│   └── journal.py          # Growth journal
└── demo/
    ├── interactive.py      # Interactive CLI
    └── run_demo.py         # 3-month demo script
```

---

## Key Design / 设计理念

- **Evidence over assertion / 证据重于断言** — skill levels require observable proof
- **Graceful degradation / 优雅降级** — works with or without LLM
- **Multi-provider / 多供应商** — one parameter to switch AI backends
- **Privacy-first / 隐私优先** — growth data is self-awareness, not surveillance

[Full documentation / 完整文档 →](growth-compass/README.md)
