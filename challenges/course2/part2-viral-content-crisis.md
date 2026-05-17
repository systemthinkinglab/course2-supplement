# Challenge 2 Part 2: Technical Design Document — Viral Content Crisis

**Student Name**: [Your Name]
**Submission Date**: [Date]
**Challenge**: News Aggregation Platform — Part 2 Viral Content Crisis

---

## Context — what happened

Your Part 1 platform launched six months ago. You grew from 10,000 to 500,000 daily users. Then a major world event broke. Traffic spiked **100x in 30 minutes**. Caches missed. The database buckled. Users saw error pages.

This document is your **evolution** of the Part 1 design — not a redesign. Part 2 should clearly build on the architecture you submitted for Part 1, adding components and modifying connections to address the new requirement.

## IMPORTANT: Technology-Agnostic Design Required

Use building block names, not technologies. See the Part 1 template for the full list. CDN, request coalescing, TTL jitter, and read replicas are all **techniques and patterns** — they describe what happens to building blocks, not new building block primitives.

---

## Part 1 Architecture Recap

[Briefly summarize your Part 1 architecture in 2-3 sentences. Name the major components and how they connect. This sets the baseline for what you're evolving.]

---

## Requirement 6: Handle 100x Traffic Spikes Without Degradation

*The system must handle 100x traffic surges during breaking news events without service degradation. Users should experience consistent performance whether traffic is normal or spiking. No error pages. Response times stay under 200ms. Search still works. Analytics still get recorded.*

### Failure mode analysis

**Where does the Part 1 design break under 100x load?**

- **Bottleneck 1**: [Which component falls over first, and why?]
- **Bottleneck 2**: [What fails second, and why?]
- **Bottleneck 3**: [Any other failure modes you anticipate?]

**The thundering herd problem (specifically)**: [Explain in your own words what happens when a popular cached article expires during a traffic spike, and why the Part 1 design can't survive it]

---

## Evolution Strategy

Address the 100x requirement using patterns from at least three of the four families below. For each pattern you apply, name the building blocks involved and explain how they slot into your Part 1 architecture.

### Family 1: CDN Distribution

**What you add**: [CDN in front of which component? What gets cached at the edge?]

**Why it helps**: [How does this address the bottleneck you identified?]

**Trade-off**: [What does this cost you? Stale content windows? Operational complexity? Vendor dependency?]

### Family 2: Advanced Cache Strategies

Apply at least two of the following:

- **TTL jitter**: [How does randomizing expirations prevent the synchronized-expiration problem?]
- **Request coalescing**: [How does electing a single fetcher prevent the herd?]
- **Stale-while-revalidate**: [How does serving stale-but-acceptable content while refreshing in the background help?]
- **Cache warming**: [How does pre-populating the cache before traffic arrives help for breaking news?]

**Your choices**: [Pick at least two, explain how they interact with your existing cache layer]

### Family 3: Read Replicas

**What you add**: [Read replicas of which database? How many?]

**Why it helps**: [How does this distribute load away from the primary?]

**Trade-off**: [Eventual consistency — when does staleness matter for news, and when doesn't it?]

### Family 4: Queue Buffering

**What you add**: [Which paths can be deferred behind a Queue during spikes?]

**Why it helps**: [How does buffering protect non-critical paths?]

**Trade-off**: [Acceptable lag in analytics or other deferred work]

---

## Traffic Flow Under Both Conditions

A strong submission shows how a request flows through the system in two scenarios.

### Normal traffic (500K users)

Walk through what happens when a user requests a popular article:

1. [Step 1]
2. [Step 2]
3. ...

### Spike traffic (50M users in 30 minutes)

Walk through what happens to that same request during the spike:

1. [Step 1]
2. [Step 2]
3. ...

**Key insight**: [What stays the same? What changes? Where does the spike load get absorbed before it reaches the database?]

---

## Failure Mode Analysis

Even with your evolution, name what would still break and how the system degrades:

- **If the CDN itself has an outage**: [What happens? What's the fallback?]
- **If a brand-new article goes viral before it can be cache-warmed**: [How does the system handle the cold-start herd?]
- **If the database primary fails during a write**: [Read replicas keep serving, but what about writes?]
- **[Add your own scenario]**: [What breaks and how does the architecture handle it?]

---

## Cost Analysis (Optional but Rewarded)

[How does your evolved architecture handle 100x traffic without provisioning 100x resources? Cite specific places where smart architecture multiplies effective capacity.]

---

## Trade-offs Explicitly Accepted

- **[Trade-off 1]**: [What you gave up to gain resilience]
- **[Trade-off 2]**: [What you gave up to gain resilience]
- **[Trade-off 3]**: [What you gave up to gain resilience]

---

## What This Evolution Intentionally Does NOT Address

[Anything you're deferring to Part 3 — explicitly. Examples: AI personalization, semantic search, recommendation systems. The grader rewards designs that know their boundaries.]

---

## Self-Graded Rubric (A / A- / B+)

**My grade**: [A / A- / B+]

**Why I assigned this grade**: [Apply the same rubric from Lesson 2. A means all requirements covered + optimal patterns + trade-offs named. A- means strong with one precision gap. B+ means solid but missing a domain-specific pattern. Be honest.]

---

## Submission

Save this document as markdown and paste the full content into the **Challenge Part 2** submission form at [systemthinkinglab.ai](https://systemthinkinglab.ai/protected/course2/challenge2.html). Part 1 must be graded before Part 2 can be submitted.
