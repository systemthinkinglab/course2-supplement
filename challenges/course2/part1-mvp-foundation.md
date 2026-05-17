# Challenge 2 Part 1: Technical Design Document — MVP Foundation

**Student Name**: [Your Name]
**Submission Date**: [Date]
**Challenge**: News Aggregation Platform — Part 1 MVP Foundation

---

## IMPORTANT: Technology-Agnostic Design Required

This technical design document must focus on **building blocks and architectural patterns**, not specific technologies.

**Use:**
- Building block names: Service, Worker, Queue, Key-Value Store, File Store, Relational Database, Vector Database
- External entities: User, External Service, Time
- Technology-agnostic terms: cache, inverted index, full-text search, CDN, read replicas, async processing

**Do NOT use:**
- Specific technologies: PostgreSQL, Redis, Elasticsearch, RabbitMQ, Kafka, S3, MongoDB
- Vendor names: AWS, Google Cloud, Azure, Cloudflare, Bunny.net
- Programming languages or frameworks: Node.js, Python, React

The grader will look for pattern recognition and clear reasoning, not technology brand-recall. Senior engineers think in patterns that transcend specific technologies.

## Recommended approach

1. **Draw your architecture diagram** using the 7 building blocks + 3 external entities. Use [this Google Drawing template](https://docs.google.com/drawings/d/1hbx9r8NCBNjMDZv9tAXzfvLR3-XPsOgHm9zrX0h_cO8/edit?usp=sharing) to get started.
2. **Use your diagram as reference** while writing your user flows and technical explanations.
3. **Ensure consistency** between what you draw and what you write.

---

## Architecture Overview

**High-Level Description**:
[Provide a 2-3 sentence overview of your overall architecture approach for the MVP]

**Core Building Blocks Used** (check all that apply):
- [ ] Service (Blue Rectangle)
- [ ] Worker (Blue Trapezoid)
- [ ] Key-Value Store (Pink Diamond)
- [ ] File Store (Pink Pentagon)
- [ ] Queue (Pink Stacked Rectangles)
- [ ] Relational Database (Pink Cylinder)
- [ ] Vector Database (Pink Cube)
- [ ] User (Green Smiley)
- [ ] External Service (Green Cloud)
- [ ] Time (Green Hourglass)

---

## Requirement 1: Aggregate News from Multiple External Sources

*The platform must continuously ingest articles from news APIs, RSS feeds, and partner sites. New content should appear in the platform within minutes of publication.*

### User Flow Design

**Building block requirements:**
- Use EXACT building block names
- Use `+` for combinations (e.g., Queue + Worker)
- Identify the **external entity** that initiates this work (hint: it's not a User)

```
Example formats:
Scheduled news fetch: Time → Ingestion Worker → External Service (news API) → Relational Database
Article normalization: Queue → Normalization Worker → Relational Database
```

**Your news aggregation flows:**
[Write 2-4 specific flows for the ingestion path]

### Architecture Decisions & Trade-offs

**Key architectural decisions:**
- **[Decision 1]**: [Why Time + Worker rather than something else?]
- **[Decision 2]**: [How do you handle failures when an external source is down?]
- **[Decision 3]**: [How do you avoid ingesting duplicate articles?]

### Technical Implementation Details

**Source coordination**: [How does your system know when to fetch from each source?]

**Processing pipeline**: [How do raw API responses become normalized article records?]

**Failure handling**: [What happens when one source returns an error or rate-limits you?]

---

## Requirement 2: Store and Organize Articles by Topic

*Each article has structured attributes — headline, author, publication date, source, topic, body. Readers browse by topic and filter by date.*

### User Flow Design

```
Example formats:
Browse by topic: User → Article Service → Relational Database
View article: User → Article Service → Relational Database
```

**Your article storage flows:**
[Write 2-4 specific flows for browsing and metadata queries]

### Architecture Decisions & Trade-offs

**Key architectural decisions:**
- **[Decision 1]**: [Why Relational Database over another storage block?]
- **[Decision 2]**: [How do you handle articles that belong to multiple topics?]
- **[Decision 3]**: [Where does the article body live, and why?]

### Technical Implementation Details

**Data organization**: [How are articles, topics, and tags structured?]

**Query patterns**: [What does "show me all Tech articles from today" look like architecturally?]

---

## Requirement 3: Full-Text Search Across Articles

*Readers search by keyword. Results must be sub-second across millions of articles.*

### User Flow Design

```
Example formats:
Search query: User → Search Service → Inverted Index (Key-Value Store)
Index update: Article publish → Indexing Worker → Key-Value Store (inverted index)
```

**Your search flows:**
[Write 2-4 specific flows for both query path and indexing path]

### Architecture Decisions & Trade-offs

**Key architectural decisions:**
- **[Decision 1]**: [Why pre-processing rather than scanning at query time?]
- **[Decision 2]**: [Trade-off between index freshness and indexing latency]
- **[Decision 3]**: [How do you rank results within the index?]

### Technical Implementation Details

**Indexing pipeline**: [When and how do new articles get indexed?]

**Query execution**: [What does the system do between user typing a query and returning results?]

---

## Requirement 4: Cache Popular Articles for Fast Delivery

*Top articles get requested by thousands of readers simultaneously. Hitting the database for each request would immediately bottleneck.*

### User Flow Design

```
Example formats:
Hot article (cache hit):  User → Article Service → Key-Value Store
Cache miss:               User → Article Service → Key-Value Store → Relational Database → (populate cache) → respond
```

**Your caching flows:**
[Write 2-4 specific flows showing both cache hit and miss paths]

### Architecture Decisions & Trade-offs

**Key architectural decisions:**
- **[Decision 1]**: [Why a Key-Value Store specifically? What pattern (cache-aside, write-through, etc.)?]
- **[Decision 2]**: [TTL strategy or active invalidation? Why?]
- **[Decision 3]**: [What happens when an article is updated?]

### Technical Implementation Details

**Cache keys and values**: [What's the key? What's the value? How big is the value?]

**Invalidation strategy**: [How do you keep cache and database in sync?]

---

## Requirement 5: Track Basic Reading Analytics

*The platform needs to know which articles get read, how often, and from which topics. Recording must not slow down article delivery.*

### User Flow Design

```
Example formats:
Article read with analytics: User → Article Service → respond → emit to Analytics Queue → Analytics Worker → analytics store
```

**Your analytics flows:**
[Write 2-4 flows showing how analytics is captured without blocking the read path]

### Architecture Decisions & Trade-offs

**Key architectural decisions:**
- **[Decision 1]**: [Why fire-and-forget rather than synchronous logging?]
- **[Decision 2]**: [Where do analytics events accumulate before being processed?]
- **[Decision 3]**: [What storage shape suits the analytics queries you anticipate?]

### Technical Implementation Details

**Event shape**: [What fields does each analytics event carry?]

**Processing rate**: [How fast do Workers drain the analytics queue? What happens during traffic spikes?]

---

## Overall Architecture Analysis

### Key design decisions (whole-system level)

1. **[Decision 1]**: [Rationale]
2. **[Decision 2]**: [Rationale]
3. **[Decision 3]**: [Rationale]

### Building block combinations used

- **[Pattern 1]**: [Which building blocks combined, where, and why]
- **[Pattern 2]**: [Which building blocks combined, where, and why]
- **[Pattern 3]**: [Which building blocks combined, where, and why]

### Trade-offs explicitly accepted

- **[Trade-off 1]**: [What you gave up and what you gained]
- **[Trade-off 2]**: [What you gave up and what you gained]

### What this MVP intentionally does NOT address

[Anything you're deferring to Part 2 or Part 3 — be explicit about what's out of scope. The grader rewards designs that know their boundaries.]

### Self-graded rubric (A / A- / B+)

**My grade**: [A / A- / B+]

**Why I assigned this grade**: [One paragraph using the rubric from Lesson 2 — A means all requirements + optimal blocks + trade-offs acknowledged, A- means strong with one precision gap, B+ means solid with one domain-specific gap]

---

## Submission

Save this document as markdown and paste the full content into the **Challenge Part 1** submission form at [systemthinkinglab.ai](https://systemthinkinglab.ai/protected/course2/challenge1.html). You'll receive AI-graded feedback within 24 hours.
