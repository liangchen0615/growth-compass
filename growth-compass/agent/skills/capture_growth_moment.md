# Skill: Capture Growth Moment

## Trigger
User shares an experience — something they did, learned, struggled with, or received feedback on. Can be invoked explicitly ("log a growth moment") or detected from natural conversation.

## Goal
Transform an unstructured, often rambling reflection into a **structured growth entry** that can feed the skill graph.

## Input Pattern Detection
Watch for signals like:
- "I worked on..." / "I just finished..."
- "Something frustrating happened..."
- "I learned that..."
- "I got feedback that..."
- "A milestone: ..."
- "I'm stuck on..."

## Process

### Step 1: Extract Core Facts
Ask clarifying questions if the initial share is vague:
- **What happened?** (The situation, task, or challenge)
- **What was your role?** (Led, contributed, observed, supported)
- **What was hard?** (The real difficulty, not the surface one)
- **What was the outcome?** (Result, feedback, what shipped, what broke)

### Step 2: Identify Skills Exercised
Map the experience to skills from the Competency Taxonomy (see knowledge base). Tag primary skill (the main one practiced) and secondary skills (supporting ones exercised).

### Step 3: Rate Growth Significance
Assign one of:
- **Stretch** — First time doing this, or significantly harder than before
- **Practice** — Reinforcing an existing skill, building fluency
- **Exposure** — Observed or learned about it, but didn't do it yet

### Step 4: Generate Reflection Prompt
Based on what was shared, ask ONE sharp follow-up question that deepens the reflection. Not "how did that feel?" — something that reveals a pattern.

Good examples:
- "You mentioned the requirements kept changing. What would you do differently next time you sense instability?"
- "You led this without formal authority. What specifically worked to get alignment?"

### Step 5: Structure the Entry
Output a structured growth entry:

```
## Growth Entry: [One-line summary]

**Date**: [date]
**Category**: [Project | Learning | Feedback | Struggle | Milestone]
**Primary Skill**: [skill from taxonomy]
**Secondary Skills**: [skills from taxonomy]
**Significance**: [Stretch | Practice | Exposure]
**Context**: [2-3 sentences describing the situation]
**My Role**: [what you did]
**The Hard Part**: [what was genuinely difficult]
**Outcome**: [what happened, what feedback you got]
**Key Insight**: [the one thing you'll take forward]
**Reflection**: [answer to the reflection prompt]
```

## Edge Cases
- If the user shares something too vague, push for specifics before tagging skills
- If multiple skills were exercised equally, tag up to 3 but designate one primary
- If the experience is a failure, treat it as high-value data — failures often reveal more than successes
- If the user seems to be journaling about the same skill repeatedly without progression, gently note the pattern
