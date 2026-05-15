"""Internationalization for Growth Compass.

Language is determined by:
1. GROWTH_COMPASS_LANG env var (e.g. "zh", "en")
2. Defaults to "zh" (Chinese)

Usage:
    from .i18n import _
    print(_("capture_prompt"))  # "请描述..." in zh, "Describe..." in en
"""

import os

LANG = os.environ.get("GROWTH_COMPASS_LANG", "zh")

STRINGS = {
    "zh": {
        # ── General ──
        "welcome_title": "成长罗盘 v1.0",
        "welcome_subtitle": "AI 驱动的个人成长追踪器",
        "welcome_tagline": "让职业成长可视化、可追踪、个性化。",
        "press_enter": "按 Enter 继续...",

        # ── Main menu ──
        "menu_prompt": "你想做什么？",
        "menu_capture": "记录成长时刻",
        "menu_capture_llm": "记录成长时刻（AI 对话）",
        "menu_capture_form": "使用结构化表单记录",
        "menu_resume": "从简历导入 — 自动提取经历",
        "menu_skill_map": "查看我的技能图谱",
        "menu_compare": "对比 — 自我认知 vs. 实际证据",
        "menu_plan": "生成发展计划",
        "menu_report": "查看成长报告",
        "menu_stats": "关于 / 统计",
        "menu_switch_profile": "切换用户",
        "menu_exit": "退出",

        # ── Profile ──
        "profile_select_title": "成长罗盘 — 选择用户",
        "profile_no_profiles": "没有找到用户数据。来创建一个吧。",
        "profile_name_prompt": "用户名（例如你的名字）：",
        "profile_active": "当前用户",
        "profile_available": "可用用户",
        "profile_entries_count": "{name}（{user}，{count} 条记录）",
        "profile_create_new": "创建新用户",
        "profile_continue": "继续使用当前用户",
        "profile_choose": "选择：",
        "profile_new_name": "新用户名：",
        "profile_switched": "已切换到用户：",
        "profile_switch_title": "切换用户",
        "profile_cancel": "取消 — 留在",
        "profile_switch_to": "切换到：",

        # ── Capture ──
        "capture_title": "记录成长时刻",
        "capture_intro": "我会问你几个关于你做了什么、学到了什么或遇到了什么困难的问题。请具体描述——细节才能让成长变得可见。",
        "capture_q1": "1. 用一句话概括，发生了什么？",
        "capture_cancelled": "（记录已取消）",
        "capture_q2": "2. 这是哪种类型的经历？",
        "capture_q2_opt1": "[1] 项目/交付   [2] 学习/研究",
        "capture_q2_opt2": "[3] 收到反馈     [4] 困难/挫折",
        "capture_q2_opt3": "[5] 里程碑/成就",
        "capture_q3": "3. 你运用或发展了哪项主要技能？",
        "capture_q4": "4. 这次经历对你有多大挑战？",
        "capture_q4_opt1": "[1] 突破 — 第一次做或比之前难很多",
        "capture_q4_opt2": "[2] 练习 — 巩固已有技能",
        "capture_q4_opt3": "[3] 接触 — 观察或了解，尚未实践",
        "capture_q5": "5. 简要背景（可选）— 当时是什么情况？",
        "capture_q6": "6. 你在其中扮演什么角色？（可选）",
        "capture_q7": "7. 真正困难的地方是什么？（可选）",
        "capture_q8": "8. 结果如何？（可选）",
        "capture_q9": "9. 你会带走什么关键的认知？（可选）",
        "capture_success": "[OK] 成长时刻已记录！",
        "capture_default_skill": "ai_building",

        # ── Resume import ──
        "resume_title": "简历导入 — 从你的简历中提取成长记录",
        "resume_llm_required": "简历导入需要 AI 模型支持。",
        "resume_llm_hint": "设置 API key 后重新启动：",
        "resume_prompt": "请粘贴你的简历或履历。我会从中提取你的职业经历，并转化为成长记录。",
        "resume_tip": "提示：你可以粘贴 LinkedIn 个人资料、简历文本或任何职业总结。完成后按两次 Enter。",
        "resume_cancelled": "（导入已取消）",
        "resume_processing": "正在处理 {count} 字...",
        "resume_failed": "无法从简历中提取结构化记录。请尝试粘贴具体段落或手动记录。",
        "resume_success": "[OK] 从简历中导入了 {count} 条成长记录！",
        "resume_summary_label": "总结",
        "resume_extracted": "提取的记录：",
        "resume_added": "所有 {count} 条记录已加入你的日志。",
        "resume_next": "运行'查看技能图谱'或'对比'来看看它们揭示了什么。",

        # ── Skill map ──
        "skillmap_title": "你的技能图谱",
        "skillmap_no_entries": "还没有成长记录。先记录一些时刻吧！",
        "skillmap_entries_analyzed": "已分析记录",
        "skillmap_skills_with_evidence": "有证据的技能",
        "skillmap_strengths": "优势",
        "skillmap_growing": "成长中",
        "skillmap_blindspots": "盲区",
        "skillmap_superpower": "超能力组合",

        # ── Comparison ──
        "compare_title": "技能对比 — 你的自我认知 vs. 实际证据",
        "compare_intro": "我会对比你对自己的看法和你的日志实际显示的内容。",
        "compare_no_entries": "还没有成长记录。先记录一些时刻吧！",
        "compare_ask": "你觉得你有哪些技能或优势？用你自己的话描述就好。",
        "compare_hint": "用逗号分隔，例如\"系统设计、指导他人、调试\"",
        "compare_cancelled": "（对比已取消）",
        "compare_you_named": "你提到了 {count} 项技能。",
        "compare_analyzing": "正在分析你的日志...",
        "compare_comparing": "正在与你的证据对比...",
        "compare_revealed": "揭示 — 你没想到，但证据显示了这些：",
        "compare_confirmed": "确认 — 你说了，证据也支持：",
        "compare_aspirational": "期望中 — 你提到了这些，但日志中暂无证据：",
        "compare_no_data": "还没有成长记录。先记录一些时刻，然后我们可以对比。",

        # ── Development plan ──
        "plan_title": "发展计划",
        "plan_no_entries": "生成计划前需要至少几条成长记录。",
        "plan_choose_target": "你想去哪里？可用的目标角色：",
        "plan_choose_prompt": "选择目标角色编号：",
        "plan_generating": "正在生成计划...",
        "plan_target": "目标",
        "plan_priority_gaps": "优先级差距",
        "plan_sprint_30": "30 天冲刺",
        "plan_risks": "风险",
        "plan_learning_edge": "学习优势",

        # ── Growth report ──
        "report_title": "成长报告",
        "report_no_entries": "还没有可报告的内容。先记录一些时刻吧！",
        "report_choose_period": "选择报告周期：",
        "report_period_monthly": "[1] 月度   [2] 季度   [3] 自定义",
        "report_generating": "正在生成报告...",
        "report_entries": "记录",
        "report_skills": "技能",
        "report_leveled_up": "升级",
        "report_stretch": "突破",
        "report_key_moments": "关键时刻",
        "report_patterns": "模式",
        "report_next_focus": "下一阶段重点",
        "report_reflection": "反思",
        "report_shareable": "可分享摘要",

        # ── About / Stats ──
        "about_title": "关于成长罗盘",
        "about_user": "用户",
        "about_session_started": "会话开始",
        "about_days_active": "活跃天数",
        "about_total_entries": "总记录数",
        "about_unique_skills": "涉及技能数",
        "about_stretch_count": "突破经历",
        "about_categories": "类别",
        "about_first_entry": "首次记录",
        "about_latest_entry": "最新记录",
        "about_llm_available": "AI 模型可用",
        "about_description": "成长罗盘是一种 AI 原生的人才发展方式。通过结构化的数据捕捉、技能图谱和 AI 驱动的发展规划，让成长变得可见、可追踪、个性化。",

        # ── Intro ──
        "intro_welcome": "欢迎！看起来这是你第一次使用。",
        "intro_ask_name": "我该怎么称呼你？",
        "intro_greeting": "你好 {name}！我是你的成长伙伴。我是这样工作的：",
        "intro_capture_desc": "告诉我你做了什么、学到了什么或遇到了什么困难。我会把它整理成成长数据。",
        "intro_resume_desc": "粘贴你的简历或履历 — 我会自动提取你的经历作为成长记录。这是最快上手的方式。",
        "intro_compare_desc": "我会对比你对自己的描述和你的日志证据实际显示的内容。这是发现隐藏优势的地方。",
        "intro_map_desc": "我会构建一个技能图谱，展示你已经展示的能力、所处水平以及证据。",
        "intro_plan_desc": "选择一个目标角色，我会生成个性化的 30/60/90 天发展计划。",
        "intro_report_desc": "我会生成成长报告——模式、关键时刻以及下一步的重点。",
        "intro_start": "从记录一个成长时刻开始吧！",
        "intro_welcome_back": "欢迎回来，{name}！",
        "intro_stats": "你有 {total} 条记录，涉及 {skills} 项技能。",
        "intro_latest": "最新记录",

        # ── Generic ──
        "goodbye": "下次见。继续成长！",
        "invalid_choice": "无效选择。",
        "cancel": "取消",
        "back": "返回",
        "yes": "是",
        "no": "否",
        "processing": "处理中...",
        "ok": "[OK]",
        "entry_id": "记录 #{id}",
        "skill_label": "技能",
        "level": "水平",
        "confidence": "置信度",
        "entries_label": "记录数",
        "significance": "重要性",
        "category": "类别",
        "separator": "─" * 54,

        # ── Comparison engine insights ──
        "cmp_no_data": "还没有数据——记录一些成长时刻，然后告诉我你认为自己有哪些技能。",
        "cmp_confirmed_insight": "你提到了这项能力，而你的经历也支持这一点。{count} 条日志记录展示了 {level} 级别的能力。",
        "cmp_revealed_insight": "你没有把这项能力列为你自己的优势之一，但你的日志中有 {count} 条记录展示了 {level} 级别的 {skill} 能力。置信度：{confidence}。",
        "cmp_aspirational_insight": "你提到了 {skill}——但目前你的日志中还没有明确的证据。如果这对你很重要，试着记录一次你运用这项能力的经历。",
        "cmp_revealed_lead": "这里有一个有趣的发现：你的经历显示了 {skill} 方面的优势，而你并没有提到这一点。",
        "cmp_confirmed_summary": "{count} 项技能已确认——你的自我认知与证据相符。",
        "cmp_aspirational_summary": "你提到的 {count} 项技能在日志中暂无证据。",
        "cmp_no_patterns": "尚未发现模式——继续记录成长时刻。",
    },

    "en": {
        # ── General ──
        "welcome_title": "Growth Compass v1.0",
        "welcome_subtitle": "AI-Powered Personal Growth Tracker",
        "welcome_tagline": "Making professional growth visible, trackable, and personalized.",
        "press_enter": "Press Enter to continue...",

        # ── Main menu ──
        "menu_prompt": "What would you like to do?",
        "menu_capture": "Capture a growth moment",
        "menu_capture_llm": "Capture a growth moment (natural language)",
        "menu_capture_form": "Capture with structured form",
        "menu_resume": "Import resume — extract entries from your CV",
        "menu_skill_map": "View my skill map",
        "menu_compare": "Compare — what I say vs. what my evidence shows",
        "menu_plan": "Generate a development plan",
        "menu_report": "View growth report",
        "menu_stats": "About / Stats",
        "menu_switch_profile": "Switch profile",
        "menu_exit": "Exit",

        # ── Profile ──
        "profile_select_title": "Growth Compass — Profile Selection",
        "profile_no_profiles": "No profiles found. Let's create one.",
        "profile_name_prompt": "Profile name (e.g. your name):",
        "profile_active": "Active profile",
        "profile_available": "Available profiles",
        "profile_entries_count": "{name} ({user}, {count} entries)",
        "profile_create_new": "Create new profile",
        "profile_continue": "Continue with current profile",
        "profile_choose": "Choose:",
        "profile_new_name": "New profile name:",
        "profile_switched": "Switched to profile:",
        "profile_switch_title": "Switch Profile",
        "profile_cancel": "Cancel — stay on",
        "profile_switch_to": "Switch to:",

        # ── Capture ──
        "capture_title": "Capture Growth Moment",
        "capture_intro": "I'll ask you a few questions about something you did, learned, or struggled with. Be specific — the details are what make growth visible.",
        "capture_q1": "1. In one sentence, what happened?",
        "capture_cancelled": "(Capture cancelled)",
        "capture_q2": "2. What kind of experience was this?",
        "capture_q2_opt1": "[1] Project/Delivery   [2] Learning/Study",
        "capture_q2_opt2": "[3] Received Feedback   [4] Struggle/Difficulty",
        "capture_q2_opt3": "[5] Milestone/Achievement",
        "capture_q3": "3. What's the MAIN skill you exercised or developed?",
        "capture_q4": "4. How much did this stretch you?",
        "capture_q4_opt1": "[1] Stretch — first time or significantly harder than before",
        "capture_q4_opt2": "[2] Practice — reinforcing an existing skill",
        "capture_q4_opt3": "[3] Exposure — observed or learned about it, didn't do it yet",
        "capture_q5": "5. Quick context (optional) — What was the situation?",
        "capture_q6": "6. What was YOUR role in this? (optional)",
        "capture_q7": "7. What was genuinely HARD about it? (optional)",
        "capture_q8": "8. What was the outcome? (optional)",
        "capture_q9": "9. What's one key insight you'll take forward? (optional)",
        "capture_success": "[OK] Growth moment captured!",
        "capture_default_skill": "ai_building",

        # ── Resume import ──
        "resume_title": "Resume Import — Extract Growth Entries from Your Resume",
        "resume_llm_required": "Resume import requires an LLM.",
        "resume_llm_hint": "Set an API key and restart:",
        "resume_prompt": "Paste your resume or CV below. I'll extract your professional experiences as growth entries and add them to your journal.",
        "resume_tip": "Tip: You can paste LinkedIn profile text, a CV, or any career summary. Press Enter twice when you're done.",
        "resume_cancelled": "(Import cancelled)",
        "resume_processing": "Processing {count} words...",
        "resume_failed": "Could not extract structured entries from the resume. Try pasting specific sections or capturing moments manually.",
        "resume_success": "[OK] Imported {count} growth entries from your resume!",
        "resume_summary_label": "Summary",
        "resume_extracted": "Extracted entries:",
        "resume_added": "All {count} entries added to your journal.",
        "resume_next": "Run 'View Skill Map' or 'Compare' to see what they reveal.",

        # ── Skill map ──
        "skillmap_title": "Your Skill Map",
        "skillmap_no_entries": "No growth entries yet. Capture some moments first!",
        "skillmap_entries_analyzed": "Entries analyzed",
        "skillmap_skills_with_evidence": "Skills with evidence",
        "skillmap_strengths": "Strengths",
        "skillmap_growing": "Growing",
        "skillmap_blindspots": "Blind spots",
        "skillmap_superpower": "Superpower combination",

        # ── Comparison ──
        "compare_title": "Skill Comparison — What You Say vs. What Your Evidence Shows",
        "compare_intro": "I'll compare what you think about yourself against what your journal actually shows.",
        "compare_no_entries": "No growth entries yet. Capture some moments first!",
        "compare_ask": "What skills or strengths do you feel you have? Just name them in your own words.",
        "compare_hint": "Separate with commas, e.g. \"system design, mentoring, debugging\"",
        "compare_cancelled": "(Comparison cancelled)",
        "compare_you_named": "You named {count} skill(s).",
        "compare_analyzing": "Analyzing your journal entries...",
        "compare_comparing": "Comparing against your evidence...",
        "compare_revealed": "REVEALED — You didn't name these, but your evidence shows them:",
        "compare_confirmed": "CONFIRMED — You said it, and the evidence agrees:",
        "compare_aspirational": "ASPIRATIONAL — You mentioned these, but no journal evidence yet:",
        "compare_no_data": "No growth entries yet. Capture some moments first, then we can compare.",

        # ── Development plan ──
        "plan_title": "Development Plan",
        "plan_no_entries": "Need at least a few growth entries before generating a plan.",
        "plan_choose_target": "Where do you want to go? Available target profiles:",
        "plan_choose_prompt": "Choose target role number:",
        "plan_generating": "Generating plan...",
        "plan_target": "Target",
        "plan_priority_gaps": "Priority Gaps",
        "plan_sprint_30": "30-Day Sprint",
        "plan_risks": "Risks",
        "plan_learning_edge": "Learning Edge",

        # ── Growth report ──
        "report_title": "Growth Report",
        "report_no_entries": "No entries to report on yet. Capture some moments first!",
        "report_choose_period": "Choose report period:",
        "report_period_monthly": "[1] Monthly   [2] Quarterly   [3] Custom",
        "report_generating": "Generating report...",
        "report_entries": "Entries",
        "report_skills": "Skills",
        "report_leveled_up": "Leveled up",
        "report_stretch": "Stretch",
        "report_key_moments": "Key Moments",
        "report_patterns": "Patterns",
        "report_next_focus": "Next Focus",
        "report_reflection": "Reflection",
        "report_shareable": "Shareable Summary",

        # ── About / Stats ──
        "about_title": "About Growth Compass",
        "about_user": "User",
        "about_session_started": "Session started",
        "about_days_active": "Days active",
        "about_total_entries": "Total entries",
        "about_unique_skills": "Unique skills touched",
        "about_stretch_count": "Stretch experiences",
        "about_categories": "Categories",
        "about_first_entry": "First entry",
        "about_latest_entry": "Latest entry",
        "about_llm_available": "LLM available",
        "about_description": "Growth Compass is an AI-native approach to talent development. It makes growth visible, trackable, and personalized through structured data capture, skill mapping, and AI-powered development planning.",

        # ── Intro ──
        "intro_welcome": "Welcome! It looks like this is your first time here.",
        "intro_ask_name": "What should I call you?",
        "intro_greeting": "Hi {name}! I'm your growth companion. Here's how I work:",
        "intro_capture_desc": "Tell me what you worked on, learned, or struggled with. I'll structure it into growth data.",
        "intro_resume_desc": "Paste your resume or CV — I'll extract your experiences as growth entries automatically. Fastest way to start.",
        "intro_compare_desc": "I'll compare what you say about yourself against what your journal evidence actually shows. This is where hidden strengths get revealed.",
        "intro_map_desc": "I'll build a skill graph showing what you've demonstrated, at what level, with what evidence.",
        "intro_plan_desc": "Pick a target role, and I'll generate a personalized 30/60/90 day development plan.",
        "intro_report_desc": "I'll produce a growth visibility report — patterns, key moments, and what to focus on next.",
        "intro_start": "Start by capturing a growth moment!",
        "intro_welcome_back": "Welcome back, {name}!",
        "intro_stats": "You have {total} entries across {skills} skills.",
        "intro_latest": "Latest entry",

        # ── Generic ──
        "goodbye": "See you next time. Keep growing!",
        "invalid_choice": "Invalid choice.",
        "cancel": "Cancel",
        "back": "Back",
        "yes": "Yes",
        "no": "No",
        "processing": "Processing...",
        "ok": "[OK]",
        "entry_id": "entry #{id}",
        "skill_label": "Skill",
        "level": "Level",
        "confidence": "Confidence",
        "entries_label": "Entries",
        "significance": "Significance",
        "category": "Category",
        "separator": "─" * 54,

        # ── Comparison engine insights ──
        "cmp_no_data": "No data yet - capture some growth moments and tell me what skills you think you have.",
        "cmp_confirmed_insight": "You said you're good at this, and your experience backs it up. {count} journal entries demonstrate {level}-level ability.",
        "cmp_revealed_insight": "You didn't name this as one of your strengths, but your journal shows {count} entries demonstrating {level}-level ability in {skill}. Confidence: {confidence}.",
        "cmp_aspirational_insight": "You mentioned {skill} - but there's no clear evidence for it in your journal yet. If this matters to you, try capturing a growth moment where you exercised it.",
        "cmp_revealed_lead": "Here's something interesting: your experience shows strength in {skill}, which you didn't name yourself.",
        "cmp_confirmed_summary": "{count} skill(s) confirmed - your self-assessment matches your evidence.",
        "cmp_aspirational_summary": "{count} skill(s) you mentioned have no journal evidence yet.",
        "cmp_no_patterns": "No patterns detected yet - keep capturing growth moments.",
    },
}


def _(key: str, **kwargs) -> str:
    """Return the localized string for the given key.

    Args:
        key: String key from the STRINGS dict.
        **kwargs: Format arguments for the string template.

    Returns:
        Localized string in the current language, or the key itself if missing.
    """
    lang_dict = STRINGS.get(LANG, STRINGS["zh"])
    text = lang_dict.get(key)
    if text is None:
        # Fall back to English, then to the key itself
        text = STRINGS.get("en", {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
