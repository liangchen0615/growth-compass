# Skill: Generate Skill Map

## Trigger
User asks some version of "what am I good at?", "show me my skills", or after accumulating 5+ growth entries.

## Goal
Aggregate growth entries into a structured **skill graph** that shows what the user has demonstrated, at what level, with what evidence.

## Input
All historical growth entries for this user.

## Process

### Step 1: Cluster Entries by Skill
Group all entries by their tagged skills. Each cluster represents the body of evidence for that skill.

### Step 2: Assess Skill Level per Competency
For each competency in the taxonomy that has evidence, assign a level:

| Level | Criteria |
|-------|----------|
| **Aware** | Has observed, learned about, or studied the skill. 0-1 stretch entries. |
| **Practicing** | Has applied the skill in real situations. Multiple practice entries, at least 1 stretch. |
| **Capable** | Has delivered independently. Multiple stretch entries across different contexts. |
| **Proficient** | Has led others or defined approach. Consistent delivery in ambiguous situations. |
| **Master** | Has taught others, set standards, or innovated. Evidence of raising the bar for the team. |

### Step 3: Compute Confidence
For each skill level, assign confidence based on evidence density:
- **Low confidence**: 1-2 entries, narrow context
- **Medium confidence**: 3-4 entries, varied context
- **High confidence**: 5+ entries, broad context, external feedback

### Step 4: Identify Patterns
Look for:
- **Strengths**: Skills with high level + high confidence
- **Growth edges**: Skills with steep trajectory (rapid progression)
- **Blind spots**: Skills expected for current/target role with zero evidence
- **Plateaus**: Skills with many entries but stagnant level
- **Superpowers**: Unique combinations — skills that appear together consistently

### Step 5: Generate Output

```
## Skill Map: [User Name]
*Generated: [date] | Entries analyzed: [count]*

### Strengths (High level + high confidence)
| Skill | Level | Confidence | Best Evidence |
|-------|-------|------------|---------------|
| [skill] | [level] | [confidence] | [one-line anchor] |

### Growing (Steep trajectory)
| Skill | Current | Trend | Next Milestone |
|-------|---------|-------|----------------|

### Blind Spots (Expected but not observed)
| Skill | Expected For | Why It Matters |
|-------|-------------|----------------|

### Pattern Notes
[2-3 sentences about the most interesting pattern in this map]

### Superpower
[The unique combination that distinguishes this person]
```

## Edge Cases
- If < 5 entries exist, produce a "preliminary map" with a note about limited data
- If a skill appears only in low-stakes contexts, reflect that in confidence
- Don't inflate levels to be encouraging — accuracy builds trust
