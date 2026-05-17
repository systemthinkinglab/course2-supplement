# Challenge 2 Part 3: Technical Design Document — AI Personalization

**Student Name**: [Your Name]
**Submission Date**: [Date]
**Challenge**: News Aggregation Platform — Part 3 AI Personalization

---

## Context — what users are asking for

Your Part 2 platform handles viral traffic gracefully. But user feedback reveals the next frontier:

> *"Why do I keep seeing sports articles when I only care about tech?"*
> *"Why can't I just ask 'what happened with AI regulation this week?' instead of searching for keywords?"*
> *"Why does this platform show me the same content as everyone else?"*

This document is the **final evolution** — layering AI capabilities on top of your scaled Part 2 architecture. AI is added, not bolted on. The patterns from Parts 1 and 2 should remain intact and operational.

## IMPORTANT: Building Block Classification Matters Here

Cloud LLMs (like OpenAI, Anthropic, Gemini) are **External Services**, not File Stores. A locally-run model uses Service + File Store (for weights), but the cloud API call goes through External Service. The grader will check this classification — it's part of the grade.

Vector embeddings live in a **Vector Database**, not in a Key-Value Store or a Relational Database. The Vector DB is the one new building block this challenge requires.

---

## Part 1 + Part 2 Architecture Recap

[Briefly summarize the architecture you have after Part 2 (2-3 sentences). This sets the baseline for what you're extending.]

---

## Requirement 7: Personalized AI-Powered Content Experience

This requirement splits into two distinct capabilities. Address both.

### Capability A: Personalized Feeds

*Each user sees content tailored to their reading history and interests. New users start with sensible defaults; the personalization improves as the system learns from behavior.*

### Capability B: Natural Language Search

*Users ask questions like "What happened with the federal budget this week?" and get relevant articles — not just articles containing those exact keywords. Keyword search finds documents; semantic search finds meaning.*

---

## Personalized Feed Architecture

### User Flow Design

```
Example formats:
Pre-compute personalized feed: Time → Personalization Worker → Vector Database + Read Cache
Serve personalized feed:       User → Feed Service → Read Cache (pre-computed feed)
Update user profile:           User reads article → Analytics Queue → Profile Worker → User Profile Store
```

**Your personalization flows:**
[Write 2-4 specific flows showing how user behavior becomes recommendations]

### Building Blocks Added

- **[Vector Database]**: [Stores what? Used how?]
- **[User Profile Store]**: [What shape? Vector? Topic weights? Both?]
- **[Personalization Worker]**: [Triggered when? Does what?]
- **[Personalized Feed Cache]**: [Why pre-compute rather than compute at read time?]

### Architecture Decisions & Trade-offs

- **[Decision 1]**: [Why pre-compute personalized feeds offline rather than at read time?]
- **[Decision 2]**: [How fresh is "fresh enough" for a personalized news feed? What TTL or invalidation strategy?]
- **[Decision 3]**: [How does this scale to millions of users with unique profiles?]

---

## Natural Language Search Architecture

### User Flow Design

```
Example formats:
Article ingestion → embedding: New article published → Embedding Worker → External Service (embedding API) → Vector Database
Semantic search query:         User → Search Service → External Service (embedding API) → Vector Database → Ranking Service → Read Cache (response)
```

**Your semantic search flows:**
[Write 2-4 specific flows showing the RAG pattern applied to news]

### Building Blocks Added

- **[Embedding Worker]**: [Triggered when? Does what? Why a Worker rather than the upload Service doing it inline?]
- **[External Service — embedding API]**: [Used for what? At which stages?]
- **[External Service — LLM API]** (if applicable): [Used for what? Answer generation? Query understanding?]

### Architecture Decisions & Trade-offs

- **[Decision 1]**: [Why use a managed embedding API rather than running your own model?]
- **[Decision 2]**: [How do you avoid sending the same query to the embedding API repeatedly?]
- **[Decision 3]**: [What's the latency budget for semantic search vs traditional keyword search?]

---

## The Three Classic Trade-offs

A strong Part 3 submission names these explicitly.

### Freshness vs Cost

[News is time-sensitive — a personalized feed that's 8 hours old has missed a news cycle. But regenerating personalization for every user on every request is prohibitively expensive. How do you balance? Be specific about TTLs, refresh triggers, and cost estimates.]

### Cold Start

[A brand-new user has no behavior history. What does the feed look like for them on day one? Your options: editorial defaults, onboarding surveys, implicit cold start (observe and adapt). Pick one and justify.]

### Filter Bubbles vs Exploration

[A personalization system that only shows users what they already like creates filter bubbles. For a news platform, you may have an editorial responsibility to expose users to important stories outside their interest profile. How do you architect for that?]

---

## Graceful Degradation: Designing for AI Failure

AI services fail. The LLM API has an outage. The embedding service rate-limits you. The Vector Database needs reindexing. Your platform cannot go down when AI does.

For each AI capability, define the fallback:

| AI capability | Primary path | Fallback when AI is unavailable |
|---|---|---|
| Personalized feed | [Pre-computed feed from cache] | [Generic popular-articles feed?] |
| Semantic search | [Vector DB + embedding API] | [Keyword search from Part 1?] |
| Embedding new articles | [External Service embedding API] | [Queue with retry; articles still searchable by keyword in the meantime?] |
| [Add your own] | [Primary path] | [Fallback path] |

**Architectural principle**: [State explicitly — the platform should still work even if every AI service is down for an hour. AI enhances; AI is not load-bearing for the core product.]

---

## Complete End-to-End Architecture

Provide a complete architecture diagram (or detailed text description) showing:

1. All Part 1 components (still present)
2. All Part 2 additions (still present)
3. All Part 3 additions (new)
4. The connections between them

[Include diagram or detailed text walkthrough]

---

## Trade-offs Explicitly Accepted

- **[Trade-off 1]**: [What you gave up to add AI]
- **[Trade-off 2]**: [What you gave up to add AI]
- **[Trade-off 3]**: [What you gave up to add AI]

---

## What This Architecture Intentionally Does NOT Address

[Be honest about what's out of scope. Examples: real-time collaboration on articles, multi-language support, video personalization. The grader rewards designs that know their boundaries.]

---

## Self-Graded Rubric (A / A- / B+)

**My grade**: [A / A- / B+]

**Why I assigned this grade**: [Apply the rubric from Lesson 2. Specifically check: did you classify cloud LLM calls as External Service (not File Store)? Did you address all three classic trade-offs explicitly? Did you provide explicit fallbacks for AI failure?]

---

## Submission

Save this document as markdown and paste the full content into the **Challenge Part 3** submission form at [systemthinkinglab.ai](https://systemthinkinglab.ai/protected/course2/challenge3.html). Parts 1 and 2 must be graded before Part 3 can be submitted. This is the capstone of Course 2 — make it count.
