# Demo Guide

## Purpose

This document explains how to present the project in a live demo or screen recording.

It focuses on:

- the demo problem statement
- the solution story
- what to click
- what to say
- how to structure a short recording

This guide is based on the current implementation in this repository.

---

## 1. Demo problem statement

The core problem this project solves is:

Operational teams receive many support or product incidents, but those tickets are:

- repetitive
- inconsistently worded
- hard to group manually
- difficult to prioritize quickly

As a result, teams struggle to answer:

- Which tickets are really the same issue?
- Which incident cluster is the highest risk?
- Is the issue increasing, stable, or resolved?
- What should be acted on first?

### Short version for presentations

“Teams are overwhelmed by raw support tickets, and they do not have an easy way to group duplicates, detect patterns, and prioritize the biggest operational risks.”

---

## 2. Solution statement

This project resolves that problem by turning raw ticket noise into grouped and prioritized operational insight.

It does this by:

- understanding ticket meaning using semantic embeddings
- enriching tickets with category and symptom signals
- clustering related incidents
- calculating confidence, trends, and impact
- showing the results in a dashboard for faster triage

### Short version for presentations

“We use AI-assisted clustering and analytics to convert unstructured support tickets into meaningful clusters, trends, and recommended actions.”

---

## 3. What the system is actually doing

In the backend:

1. Tickets are loaded from `backend/poc_tickets.json`
2. The AI pipeline enriches them with:
   - symptom
   - broad category
   - dynamic category
3. Ticket text is normalized
4. Semantic embeddings are generated with `SentenceTransformer`
5. Hybrid features are built using:
   - text
   - category
   - symptom
   - severity
6. Incidents are clustered using `DBSCAN` or `HDBSCAN`
7. The system computes:
   - confidence
   - trends
   - impact score
   - summaries
   - recommendations
8. The frontend visualizes the output

---

## 4. Demo story in simple language

Use this story:

“Today, operations teams often read tickets one by one and try to spot patterns manually. That is slow, repetitive, and easy to get wrong. This dashboard uses semantic AI and clustering to group similar incidents, identify the highest-risk patterns, and help teams respond faster.”

Then continue with:

“Instead of a flat backlog of tickets, the system gives us grouped incident clusters, duplicate detection, confidence signals, trend visibility, and suggested actions.”

---

## 5. Recommended demo format

Best format:

- 2 to 3 minute screen recording
- voiceover or live narration

Why this works well:

- the project is visual
- charts and clusters are easier to understand when shown
- you reduce live-demo risk
- the recording can be reused for presentations or review

---

## 6. Before recording

### Start the backend

From the project root:

```bash
cd backend
python3 main.py
```

### Start the frontend

From the project root:

```bash
npm run dev
```

### Open the dashboard

Frontend:
- `http://localhost:5173`

Backend:
- `http://localhost:8000`

### Best preparation tips

- keep one strong cluster ready to show
- keep one duplicate-check example ready
- avoid extra tabs during recording
- use a browser zoom that makes charts readable

---

## 7. Suggested demo flow

### Step 1: Open with the problem

What to show:
- dashboard landing page

What to say:

“Operations teams receive many support tickets, but those tickets are often repetitive, inconsistently worded, and difficult to prioritize quickly.”

“The problem is that raw ticket volume does not automatically translate into operational intelligence.”

“This project solves that by grouping related incidents, highlighting patterns, and surfacing what matters most.”

---

### Step 2: Show the overview dashboard

What to click:
- stay on the Overview tab

What to say:

“This is the Operational Intelligence Dashboard.”

“Instead of showing a flat list of incidents, it gives us a structured overview of risk, trends, and issue clusters.”

“At the top, we can immediately see total incidents, cluster count, trend, and overall risk score.”

What to point at:

- total incidents
- risk score
- trend
- cluster count

---

### Step 3: Show one cluster

What to click:
- click into one strong cluster

Good examples:

- file upload issues
- access errors
- partial review saved issues

What to say:

“Here the system has grouped multiple tickets into one underlying issue pattern.”

“These tickets may be worded differently, but semantically they are describing the same operational problem.”

“The backend uses text normalization, embeddings, and clustering to do that automatically.”

What to point at:

- summary
- incident count
- top keywords
- priority
- recommended action

---

### Step 4: Explain why this is useful

What to say:

“Without this, the team would manually inspect each ticket and try to guess whether it is new, duplicate, or part of a bigger pattern.”

“This reduces noise and helps the team focus on the real recurring issues instead of reading every incident in isolation.”

---

### Step 5: Show duplicate detection

What to click:
- open the Check Duplicate tab

Suggested examples to type:

- `File upload hangs at 99 percent`
- `Review still shows partial review saved after submit`

What to say:

“Now I’ll show duplicate detection.”

“A support agent can enter a new issue, and the system compares it semantically against existing incidents.”

“This is more than keyword matching. It uses embeddings, so differently worded tickets can still match.”

What to point at:

- confidence score
- matched cluster
- similar tickets

---

### Step 6: Show all tickets

What to click:
- open the All Tickets tab

What to say:

“This view shows the raw ticket inventory together with cluster assignments.”

“It helps validate that the AI grouping is reasonable and gives transparency into how the incidents are organized.”

What to point at:

- ticket IDs
- cluster assignment
- cluster confidence or priority if visible

---

### Step 7: Show trends or confidence

You can choose one based on what looks best.

#### Option A: Cluster Changes

What to say:

“This view shows whether a cluster is new, increasing, stable, or resolved.”

“That helps operations distinguish background noise from a fresh spike.”

#### Option B: Cluster Confidence

What to say:

“This gives an explainability signal for the clustering.”

“It helps us understand how strongly related the incidents are inside a cluster.”

---

### Step 8: Show actionability

What to click:
- open Jira draft if available

What to say:

“The system does not stop at grouping incidents.”

“It also turns the cluster into something actionable, including summary, impact, priority, and recommended next step.”

“That helps move from detection to response much faster.”

---

### Step 9: Close with business value

What to say:

“So the value of this project is that it turns raw ticket noise into prioritized operational insight.”

“Instead of manually reading everything, teams can focus on the biggest issue patterns, the fastest-rising risks, and the most important actions.”

“In short, it improves triage speed, prioritization quality, and operational visibility.”

---

## 8. Suggested recording timeline

### 2-minute version

- 20 sec: problem statement
- 35 sec: overview dashboard
- 25 sec: cluster example
- 20 sec: duplicate check
- 20 sec: all tickets or trends
- 20 sec: closing value

### 3-minute version

- 30 sec: problem statement
- 45 sec: overview
- 35 sec: cluster detail
- 30 sec: duplicate check
- 20 sec: all tickets
- 20 sec: trends or confidence
- 20 sec: close

---

## 9. Recommended spoken script

Use this concise version if you want a smoother talk track:

“Operations teams often deal with a large volume of support tickets, but those tickets are repetitive, inconsistently worded, and difficult to prioritize quickly. This project solves that by using AI-assisted clustering and analytics to group related incidents, detect patterns, and surface what matters most.”

“On the dashboard, we can immediately see overall risk, trend, and active issue clusters. If we drill into a cluster, we see the summary, volume, keywords, and recommended action. That means the system is not just grouping incidents, it is helping the team understand and act on them.”

“We can also check whether a new issue is likely a duplicate. This reduces repeated investigation and helps route incidents into existing clusters instead of creating more noise.”

“The result is faster triage, clearer prioritization, and better operational visibility.”

---

## 10. Notes for accuracy

When presenting this repository, keep the demo aligned with the current implementation:

- ticket data is currently file-based
- runtime state is currently in memory
- there is no persistent production database in this repo
- the AI layer is based on embeddings, clustering, and explainable metrics
- this is not a chatbot demo; it is an operational intelligence demo

This keeps the story accurate and credible.

