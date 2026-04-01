# DEMO VIDEO SCRIPT
## Operational Intelligence Dashboard - Elsevier Peer Review Platform

**Total Duration:** 5-7 minutes  
**Format:** Screen recording with voiceover  
**Audience:** Product managers, operations leads, engineering teams

---

## PART 1: THE PROBLEM (1:30 - 2:00)

*[SCENE: Dark background with text animation]*

### 1.1 Opening Hook (15 seconds)

**[NARRATOR]**
> "Every week, your support team drowns in a sea of tickets. Slack messages pile up. Jira backlogs grow. And somewhere in that noise, critical issues are slipping through the cracks."

**[VISUAL: Animated text showing growing ticket count]**

---

### 1.2 The Current Reality (45 seconds)

**[NARRATOR]**
> "Let's look at what your team actually deals with on a daily basis..."

**[VISUAL: Simulated Jira dashboard with scattered tickets, Slack channels with support threads]**

**[NARRATOR - Bullet Points with animations]**

1. **"Operational Chaos"**
   > "Your team manually reviews every support conversation. They try to spot patterns by eye - which is slow, error-prone, and exhausting."

2. **"Hidden Connections"**
   > "Three tickets come in about 'reviewer assignment failures' - but nobody realizes they're all the same root cause. Each gets investigated separately."

3. **"No Visibility into Trends"**
   > "Is the issue getting worse or better? Nobody knows. There's no trend analysis, no early warning system."

4. **"Gut-Feel Prioritization"**
   > "Teams guess what to fix first. High priority or low priority? It depends on who complained loudest."

**[VISUAL: Split screen - messy Jira/Slack on left, red arrows pointing to problems]**

---

### 1.3 The Cost (30 seconds)

**[NARRATOR]**
> "This isn't just annoying - it has real business impact."

| Metric | Impact |
|--------|--------|
| Time wasted on manual triage | 4+ hours/day |
| Redundant investigation | 20-30% duplicate work |
| Delayed resolution | Systemic issues hide in noise |
| Team burnout | Alert fatigue kills morale |

**[VISUAL: Clean infographic showing these metrics]**

**[TRANSITION: Hard cut to dark screen, then fade into PART 2]**

---

## PART 2: THE SOLUTION (2:30 - 3:30)

*[SCENE: Operational Intelligence Dashboard - Full Screen]*

### 2.1 Introducing the Dashboard (30 seconds)

**[NARRATOR]**
> "Introducing the Operational Intelligence Dashboard for Elsevier Peer Review."

**[VISUAL: First look at the dashboard - Executive Summary tab]**

> "Instead of drowning in raw tickets, you see a unified view of what's actually happening. Clear metrics. Actionable insights. No noise."

---

### 2.2 Key Features Walkthrough (1:30)

#### Feature 1: Executive Summary

**[VISUAL: Zoom into dashboard metrics]**

**[NARRATOR]**
> "The Executive Summary gives you instant situational awareness."

**[Show on screen]**
- **Risk Score** - Overall health indicator
- **Total Incidents** - This week's count
- **Stability Trend** - Up, down, or stable?
- **Active Clusters** - Grouped issues count

> "See at a glance: Is the platform healthy or on fire?"

---

#### Feature 2: AI-Clustered Issues

**[VISUAL: Click to Clusters tab, show the cluster cards]**

**[NARRATOR]**
> "Here's where the magic happens. The AI automatically groups related incidents into clusters."

**[VISUAL: Highlight a cluster card]**

> "Each cluster shows you:
> - What's happening (summary)
> - How many incidents are grouped together
> - Whether it's getting worse or better
> - Affected workflows"

**[Show cluster detail view]**

> "You can drill into any cluster to see:
> - Timeline of incidents
> - Top keywords
> - Contributing signals - volume, timing, affected areas
> - Confidence score - how sure the AI is about this grouping"

---

#### Feature 3: Trend Analysis

**[VISUAL: Switch to Overview tab, show trend chart]**

**[NARRATOR]**
> "Never wonder 'is this getting worse?' again."

> "The trend chart shows you incident volume over time. Is that issue spiking? Is another one stabilizing?"

**[VISUAL: Highlight trend line changes]**

> "Now you have data-driven answers, not gut feelings."

---

#### Feature 4: Real-Time Duplicate Detection

**[VISUAL: Show "Check Duplicate" tab]**

**[NARRATOR]**
> "When a new ticket comes in, the system instantly checks if it's a duplicate of an existing issue."

**[VISUAL: Type a ticket, show duplicate suggestions]**

> "No more investigating the same problem three times."

---

### 2.3 The AI Explainability (30 seconds)

**[NARRATOR]**
> "Now, let's talk about something important: trust."

**[VISUAL: Show a cluster with explanation panel expanded]**

> "Every AI insight comes with full transparency."

**[Show the contributing signals]**
- Incident volume contribution
- Timing patterns
- Affected workflows

> "You see exactly WHY the AI grouped these issues together. No black boxes. No mystery."

> "And importantly - the system does NOT make decisions for you. It supports human judgment. The AI says 'here's what I found, here's why' - but a human decides what to do about it."

---

### 2.4 Privacy & Compliance (15 seconds)

**[NARRATOR]**
> "One more thing: privacy."

**[VISUAL: Security/compliance iconography]**

> "The system analyzes operational metadata only. No manuscript content. No reviewer names. No editor data."

> "We're showing you patterns in system behavior - not sensitive academic content."

---

## PART 3: THE ARCHITECTURE (1:30 - 2:00)

*[SCENE: Clean architecture diagram]*

### 3.1 System Overview (30 seconds)

**[NARRATOR]**
> "Let me show you how this actually works under the hood."

**[VISUAL: Architecture diagram - 3 layers]**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │
│   │    Jira     │  │    Slack    │  │   Support Conversations     │  │
│   │   Tickets   │  │   Messages  │  │   & Other Sources           │  │
│   └─────────────┘  └─────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                                 │
│   ┌────────────────────────────────────────────────────────────────┐ │
│   │                    AI PROCESSOR                                │ │
│   │  ┌────────────────┐  ┌──────────────┐  ┌────────────────────┐  │ │
│   │  │  EMBEDDINGS    │  │  CLUSTERING  │  │  DUPLICATE CHECK   │  │ │
│   │  │  (768-dim)     │  │  (DBSCAN)    │  │  (Cosine Sim)      │  │ │
│   │  └────────────────┘  └──────────────┘  └────────────────────┘  │ │
│   │                                                                 │ │
│   │  ┌────────────────┐  ┌──────────────┐  ┌────────────────────┐  │ │
│   │  │  CATEGORY      │  │  CONFI-      │  │  TREND             │  │ │
│   │  │  CLASSIFIER    │  │  DENCE       │  │  ANALYSIS          │  │ │
│   │  └────────────────┘  └──────────────┘  └────────────────────┘  │ │
│   └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                                   │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────┐ │
│   │ EXECUTIVE    │  │  CLUSTER     │  │  DUPLICATE   │  │ TREND  │ │
│   │ SUMMARY      │  │  DETAILS     │  │  CHECKER     │  │ CHARTS │ │
│   └──────────────┘  └──────────────┘  └──────────────┘  └────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 The AI Pipeline (45 seconds)

**[NARRATOR]**
> "Here's what happens when a ticket arrives..."

**[VISUAL: Pipeline animation - step by step]**

**[STEP 1: Text Preprocessing]**
> "First, we clean the text - normalize, strip noise, prepare for analysis."

**[STEP 2: Semantic Embedding]**
> "Next, we convert the ticket text into a 768-dimensional vector using paraphrase-mpnet-base-v2."

**[VISUAL: Text → [0.2, -0.5, 0.8, ... 768 dims]]**

> "This captures the semantic meaning. 'Reviewer assignment failed' and 'workflow error' become mathematically similar."

**[STEP 3: Hybrid Clustering]**
> "Then we run DBSCAN clustering on combined features:
> - Semantic embeddings (768 dimensions)
> - Metadata features (workflow, severity, category)"

**[VISUAL: Show clusters forming]**

> "DBSCAN is density-based - it finds natural groupings without needing to specify cluster count upfront."

**[STEP 4: Confidence Scoring]**
> "Each cluster gets a confidence score based on:
> - Intra-cluster similarity (how tight are the issues?)
> - Inter-cluster separation (how distinct is this from other clusters?)"

**[VISUAL: Show confidence percentage]**

**[STEP 5: Trend & Change Tracking]**
> "Finally, we compare current vs. previous period to show trends. Is this cluster growing? Shrinking?"

---

### 3.3 Key Technical Decisions (30 seconds)

**[NARRATOR]**
> "Why did we build it this way?"

| Decision | Rationale |
|----------|-----------|
| **Sentence Transformers** | Pretrained model captures semantic meaning without training |
| **DBSCAN Clustering** | Density-based, finds natural clusters, no need to specify count |
| **Hybrid Features** | Semantic + metadata = better grouping than either alone |
| **REST API** | Easy integration with Jira, Slack, existing tools |
| **React Frontend** | Fast, interactive UI for real-time insights |

---

### 3.4 Closing (15 seconds)

**[VISUAL: Back to full dashboard]**

**[NARRATOR]**
> "The Operational Intelligence Dashboard turns operational noise into actionable insights."

> "Your team stops drowning in tickets and starts solving problems."

**[VISUAL: Clean end card]**

```
┌─────────────────────────────────────────┐
│                                         │
│   OPERATIONAL INTELLIGENCE DASHBOARD    │
│                                         │
│   AI-Powered. Human-Centered.            │
│   Evidence-Based.                       │
│                                         │
└─────────────────────────────────────────┘
```

> "Thanks for watching."

---

## APPENDIX: VISUAL ASSETS NEEDED

| Scene | Asset |
|-------|-------|
| Part 1 | Jira ticket grid mockup |
| Part 1 | Slack channel mockup |
| Part 1 | Metrics infographic template |
| Part 2 | Dashboard screenshots (all 5 tabs) |
| Part 2 | Cluster detail mockup |
| Part 2 | Duplicate check animation |
| Part 3 | Architecture diagram (SVG/PNG) |
| Part 3 | Pipeline animation frames |
| Closing | End card graphic |

---

## RECORDING NOTES

### Before Recording
- [ ] Record dashboard demo with realistic data
- [ ] Screen record each tab interaction
- [ ] Create pipeline animation sequence
- [ ] Prepare architecture diagram export

### Recording Tips
- Keep voice steady, speak clearly
- Pause 2 seconds between major points
- Use cursor highlights on important areas
- Keep mouse movements smooth

### Post-Production
- Add captions for accessibility
- Include background music (subtle, professional)
- Add transitions between sections
- Target 5-7 minute final cut
