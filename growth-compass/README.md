# Growth Compass / 成长罗盘

**AI-Powered Personal Growth Tracker** — makes professional growth visible, trackable, and personalized.

**AI 驱动的个人成长追踪器** — 让职业成长可视化、可追踪、个性化。

---

## What It Does / 它能做什么

Growth Compass helps engineers and technical managers track professional growth through four AI skills:

成长罗盘通过四项 AI 技能帮助工程师和技术管理者追踪职业成长：

| Skill / 技能 | What It Does / 功能 | When / 频率 |
|-------|-------------|------|
| **Capture / 捕捉** | Structures reflections into growth data / 将反思结构化 | Weekly / 每周 |
| **Map / 图谱** | Builds skill graph with levels and patterns / 生成技能图谱 | Monthly / 每月 |
| **Plan / 规划** | Generates personalized 30/60/90 day plan / 生成个性化发展规划 | Per goal / 按需 |
| **Report / 报告** | Produces growth visibility reports / 产出成长可视化报告 | Quarterly / 每季度 |

---

## Quick Start / 快速开始

### Heuristic mode (no API key needed) / 启发式模式（无需 API key）

```bash
cd growth-compass
pip install -r requirements.txt
python demo/run_demo.py                 # 3-month demo / 三个月演示
python demo/interactive.py              # Interactive mode / 交互模式
```

### LLM mode (real AI intelligence) / LLM 模式（真实 AI 智能）

```powershell
# Set one key / 设置一个 key:
$env:DEEPSEEK_API_KEY="sk-..."          # DeepSeek
# or / 或:
$env:ANTHROPIC_API_KEY="sk-ant-..."     # Anthropic Claude
# or / 或:
$env:OPENAI_API_KEY="sk-..."            # OpenAI

$env:PYTHONUTF8=1
python demo/interactive.py              # Auto-detects provider / 自动检测供应商
python demo/run_demo.py --llm --provider deepseek
```

### Supported providers / 支持的供应商

| Provider | Env Var / 环境变量 | Default Model |
|----------|-------------------|---------------|
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-chat` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| Custom / 自定义 | `OPENAI_API_KEY` + `--base-url` | Any |

---

## Architecture / 架构

```
growth-compass/
├── agent/                          # Agent config (platform-agnostic) / 智能体配置
│   ├── system_prompt.md            # Agent persona, tone, rules / 角色、语调、规则
│   ├── skills/                     # 4 skill definitions / 四项技能定义
│   │   ├── capture_growth_moment.md
│   │   ├── map_skills.md
│   │   ├── create_dev_plan.md
│   │   └── generate_growth_report.md
│   └── knowledge_base/             # Structured knowledge / 结构化知识
│       ├── skills_taxonomy.json    # 16 competencies x 4 domains / 16项能力x4领域
│       ├── roles.json              # 6 role profiles / 6个角色画像
│       └── resources.json          # 14 curated learning resources / 14个学习资源
├── src/                            # Python engine / Python 引擎
│   ├── models.py                   # Data models + LLM response models / 数据模型
│   ├── knowledge.py                # Knowledge base loader / 知识库加载器
│   ├── journal.py                  # Growth journal — Capture / 成长日志
│   ├── skill_graph.py              # Skill mapping — Map / 技能图谱引擎
│   ├── dev_plan.py                 # Dev plan generator — Plan / 发展规划生成器
│   ├── report.py                   # Report generator — Report / 成长报告生成器
│   ├── llm.py                      # Multi-provider LLM client / 多供应商LLM客户端
│   └── agent.py                    # Main orchestrator / 主编排器
├── demo/
│   ├── run_demo.py                 # 3-month simulated demo / 三个月模拟演示
│   └── interactive.py              # Interactive CLI / 交互式命令行
├── requirements.txt
└── .env.example
```

---

## How AI Is Used / AI 如何使用

### When LLM is available / LLM 可用时

The `.md` skill files are loaded as **system prompts** and sent to the LLM. The knowledge base JSONs are injected as **context**. The LLM makes nuanced assessments — reading actual entry content to judge skill levels, identifying non-obvious patterns, and generating genuinely personalized plans.

`.md` 技能文件作为 **system prompts** 加载并发送给 LLM。知识库 JSON 作为 **上下文** 注入。LLM 做出细致判断——读取实际条目内容来评估技能水平、识别深层模式、生成真正个性化的计划。

### When LLM is unavailable / LLM 不可用时

Graceful fallback to heuristic rules. Everything works without an API key — just with hardcoded thresholds and templates instead of LLM judgment.

优雅降级到启发式规则。无需 API key 一切照常运行——只是用硬编码阈值和模板代替 LLM 判断。

### What calls the LLM / LLM 调用时机

| Action / 操作 | Skill file used / 使用的技能文件 | Type / 类型 |
|--------|------------------|------|
| Natural language capture / 自然语言捕捉 | `capture_growth_moment.md` | Structured extraction / 结构化提取 |
| View skill map / 查看技能图谱 | `map_skills.md` | Per-skill assessment + pattern detection |
| Generate dev plan / 生成发展规划 | `create_dev_plan.md` | Full plan generation / 完整计划生成 |
| View growth report / 查看成长报告 | `generate_growth_report.md` | Key moments + patterns + focus / 关键时刻+模式+重点 |

---

## Design Decisions / 设计决策

**Privacy-first / 隐私优先**: Growth data is personal awareness, not surveillance. Skill levels are grounded in evidence.

成长数据是自我认知，不是监控。技能等级基于证据而非臆断。

**Evidence over assertion / 证据重于断言**: "I'm good at system design" doesn't count — "I designed X, here's what happened" does.

"我擅长系统设计"不计数——"我设计了X，这是过程和结果"才计数。

**Graceful degradation / 优雅降级**: LLM is optional. The agent works with or without an API key. Heuristics are the safety net, not a separate code path.

LLM 是可选的。有 API key 用 AI，没有用启发式规则。两者共享同一代码路径。

**Multi-provider / 多供应商**: Anthropic, DeepSeek, OpenAI, or any compatible endpoint. One parameter switch.

支持 Anthropic、DeepSeek、OpenAI 及任何兼容接口，一个参数即可切换。

---

## Key Insight / 核心洞察

The hardest part of talent development isn't the training — it's making growth **visible** in the first place. This tool turns scattered work experiences into structured evidence. That's the foundation everything else builds on.

人才发展最难的不是培训——而是首先让成长变得**可见**。这个工具将零散的工作经历转化为结构化证据，这是其他一切的基础。
