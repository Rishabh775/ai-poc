# OPERATIONAL INTELLIGENCE PLATFORM
## Product Specification Document

---

## 1. EXECUTIVE SUMMARY

**Product Name:** OpsIntel (placeholder)  
**Tagline:** AI-Powered Operational Triage Engine  
**Mission:** Automatically analyze, cluster, and prioritize operational incidents to reduce MTTR (Mean Time To Resolution) and eliminate alert fatigue.

**Core Value Proposition:**
- Automatically group similar incidents into clusters
- Detect duplicates before they create redundant work
- Recommend actions and assign ownership
- Notify teams via Slack when attention is needed

---

## 2. TARGET MARKET

| Segment | Description |
|---------|-------------|
| **Primary** | Mid-market tech companies (100-2000 employees) with dedicated ops/dev teams |
| **Secondary** | SaaS companies with 24/7 on-call rotations |
| **Tertiary** | Enterprise engineering teams with high incident volume |

**Ideal Customer Profile:**
- Uses Jira for incident tracking
- Has Slack for team communication
- Deals with 50+ incidents/month
- Currently uses manual triage or no systematic approach

---

## 3. PROBLEM STATEMENT

| Pain Point | Current Reality | Cost |
|------------|-----------------|------|
| **Alert Fatigue** | Teams receive 100s of alerts, can't prioritize | 4+ hrs/day wasted |
| **Duplicate Work** | Same issue reported multiple times | 20-30% redundant investigation |
| **Slow Triage** | Manual categorization takes hours | Delayed resolution |
| **No Pattern Recognition** | Systemic issues hidden in noise | Recurring outages |

---

## 4. PRODUCT VISION

### 4.1 Core Features (MVP)

| Feature | Description |
|---------|-------------|
| **AI Clustering** | Automatically group similar incidents using semantic embeddings + ML clustering |
| **Duplicate Detection** | Real-time check if new ticket is a duplicate of existing cluster |
| **Priority Scoring** | Auto-assign P1-P4 based on frequency, severity, recurrence |
| **Action Recommendations** | Suggest root cause investigation, escalation, or workaround |
| **Jira Integration** | Read tickets, write back clusters/priority/assignee |
| **Slack Notifications** | Alert channels when new clusters detected or risk spikes |
| **Dashboard** | Visual overview of incidents, clusters, trends, team workload |

### 4.2 Future Features (Post-MVP)

| Feature | Description |
|---------|-------------|
| **Auto-Create Subtasks** | Generate investigation tasks automatically |
| **SLA Tracking** | Monitor time-to-resolution per cluster |
| **Root Cause Hints** | LLM-powered hypothesis generation |
| **Release Correlation** | Link incidents to recent deployments |
| **Multi-Project** | Aggregate across multiple Jira projects |
| **Custom Workflows** | User-defined routing and automation rules |
| **API First** | Full REST API for CI/CD integrations |
| **Self-Hosted** | On-prem deployment for security-sensitive orgs |

---

## 5. ARCHITECTURE

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OPSINTEL PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                  │
│  │   JIRA     │      │   SLACK    │      │   DASHBOARD │                  │
│  │   CLOUD    │      │   WORKSPACE│      │   (React)   │                  │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘                  │
│         │                    │                    │                         │
│         └────────────────────┼────────────────────┘                         │
│                              │                                              │
│                      ┌───────▼───────┐                                      │
│                      │  API GATEWAY  │                                      │
│                      │   (FastAPI)   │                                      │
│                      └───────┬───────┘                                      │
│                              │                                              │
│         ┌────────────────────┼────────────────────┐                         │
│         │                    │                    │                         │
│  ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐                 │
│  │   JIRA      │     │     AI      │     │   SLACK     │                 │
│  │  CONNECTOR  │     │   PIPELINE  │     │  NOTIFIER   │                 │
│  │  Service    │     │  (ML/ML)    │     │   Service   │                 │
│  └─────────────┘     └─────────────┘     └─────────────┘                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     BACKGROUND WORKERS                               │   │
│  │   • Ticket Polling (configurable interval)                          │   │
│  │   • Cluster Re-processing (daily/weekly)                          │   │
│  │   • Trend Analysis                                                  │   │
│  │   • Notification Dispatcher                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DATA STORAGE                                     │   │
│  │   • PostgreSQL: Tickets, Clusters, Config, Users                     │   │
│  │   • Redis: Cached embeddings, session data                          │   │
│  │   • Vector DB (optional): Embedding storage                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | FastAPI (Python) | High perf, async, great ML ecosystem |
| **AI/ML** | Sentence Transformers + DBSCAN | Proven semantic similarity + clustering |
| **Database** | PostgreSQL | Relational data, ACID, mature |
| **Cache** | Redis | Embedding cache, session store |
| **Frontend** | React + Vite + Tailwind | Current stack, fast dev |
| **Charts** | Recharts | Good balance of features/weight |
| **Queue** | Celery + Redis | Background job processing |
| **Container** | Docker + Docker Compose | Easy deployment |

---

## 6. INTEGRATION SPECIFICATIONS

### 6.1 Jira Integration

**Authentication:**
- OAuth 2.0 (recommended for multi-tenant)
- API Token + Basic Auth (for single-tenant/self-hosted)
- Scopes: `read:jira-work`, `write:jira-work`, `read:jira-users`

**API Endpoints Used:**

| Endpoint | Purpose |
|----------|---------|
| `GET /rest/api/3/search` | Fetch tickets via JQL |
| `GET /rest/api/3/issue/{id}` | Get ticket details |
| `PUT /rest/api/3/issue/{id}` | Update priority, labels, assignee |
| `POST /rest/api/3/issue` | Create new tickets |
| `GET /rest/api/3/project` | List available projects |

**JQL Query Pattern:**
```jql
project = "OPS" AND created >= -30d ORDER BY created DESC
```

**Rate Limits:**
- Jira Cloud: 10 requests/second (paid), 3 requests/second (free)
- Implement exponential backoff + request queuing
- Cache frequently-accessed data

**Data Sync Strategy:**

| Mode | Trigger | Latency |
|------|---------|---------|
| **Polling** | Every 5/15/30/60 min | Low |
| **Webhook** | On ticket create/update | Near real-time |

### 6.2 Slack Integration

**Authentication:**
- OAuth 2.0 for workspace installation
- Incoming Webhooks for notifications

**Features:**

| Feature | Implementation |
|---------|---------------|
| **Notifications** | Incoming Webhooks → Channel |
| **Commands** | Slack Slash Command `/ops check <ticket-id>` |
| **Interactive** | Slack Buttons (acknowledge, escalate) |

**Notification Types:**

| Trigger | Message Format |
|---------|----------------|
| New cluster detected | Block Kit with cluster summary + top tickets |
| Risk score spike | Alert with severity + affected tickets |
| Duplicate found | Thread reply with similar tickets |
| Daily digest | Summary of clusters, trends, recommendations |

**Message Template Example:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "🚨 New Incident Cluster Detected"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Type:*\nSubmission failures"},
        {"type": "mrkdwn", "text": "*Incidents:*\n12 in last 7 days"},
        {"type": "mrkdwn", "text": "*Priority:*\nP2"},
        {"type": "mrkdwn", "text": "*Owner:*\nBackend Team"}
      ]
    },
    {
      "type": "actions",
      "elements": [
        {"type": "button", "text": {"type": "plain_text", "text": "View Dashboard"}, "url": "..."},
        {"type": "button", "text": {"type": "plain_text", "text": "Create Jira Ticket"}}
      ]
    }
  ]
}
```

---

## 7. DATA MODEL

### 7.1 Core Entities

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Tenant     │     │     User       │     │    JiraConfig  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)        │     │ id (PK)        │     │ id (PK)        │
│ name           │────<│ tenant_id (FK) │     │ tenant_id (FK) │
│ plan           │     │ email          │     │ jira_domain    │
│ created_at     │     │ role           │     │ access_token   │
│ updated_at     │     │ slack_user_id  │     │ refresh_token  │
└─────────────────┘     └─────────────────┘     │ webhook_url    │
                                                └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Ticket     │     │    Cluster      │     │   Notification  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)        │     │ id (PK)        │     │ id (PK)        │
│ tenant_id (FK) │     │ tenant_id (FK) │     │ tenant_id (FK) │
│ jira_id        │     │ name           │     │ cluster_id (FK)│
│ title          │     │ summary        │     │ type           │
│ description    │     │ priority       │     │ sent_at        │
│ severity       │     │ owner_team     │     │ status         │
│ workflow_type  │     │ impact_score   │────<│ message        │
│ jira_status    │     │ risk_score     │     └─────────────────┘
│ created_at     │     │ confidence     │
│ cluster_id (FK)│────<│ created_at     │
└─────────────────┘     └─────────────────┘
```

---

## 8. API SPECIFICATION

### 8.1 REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Auth** | | |
| POST | `/api/v1/auth/login` | OAuth/JWT login |
| POST | `/api/v1/auth/jira/callback` | Jira OAuth callback |
| POST | `/api/v1/auth/slack/callback` | Slack OAuth callback |
| **Tickets** | | |
| GET | `/api/v1/tickets` | List tickets (paginated) |
| GET | `/api/v1/tickets/{id}` | Get ticket detail |
| POST | `/api/v1/tickets/import` | Manual import (paste JSON) |
| **Clusters** | | |
| GET | `/api/v1/clusters` | List clusters |
| GET | `/api/v1/clusters/{id}` | Get cluster detail |
| POST | `/api/v1/clusters/{id}/merge` | Merge two clusters |
| POST | `/api/v1/clusters/{id}/dismiss` | Dismiss cluster |
| **Insights** | | |
| GET | `/api/v1/insights` | Get AI insights + metrics |
| GET | `/api/v1/insights/trends` | Get trend data |
| **Duplicates** | | |
| POST | `/api/v1/duplicate/check` | Check if ticket is duplicate |
| **Webhooks** | | |
| POST | `/api/v1/webhooks/jira` | Receive Jira webhooks |
| **Settings** | | |
| GET | `/api/v1/settings` | Get tenant settings |
| PUT | `/api/v1/settings` | Update settings |

### 8.2 Webhook Events (Outbound)

| Event | Payload |
|-------|---------|
| `cluster.created` | `{cluster_id, summary, priority, ticket_count}` |
| `cluster.updated` | `{cluster_id, changes}` |
| `duplicate.detected` | `{ticket_id, similar_cluster_id, similarity}` |
| `risk.spike` | `{old_score, new_score, cluster_id}` |

---

## 9. PRICING MODEL

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 100 tickets/month, 1 project, dashboard only |
| **Starter** | $49/mo | 1,000 tickets/mo, Jira integration, Slack notifs |
| **Pro** | $149/mo | 10,000 tickets/mo, multiple projects, API access |
| **Enterprise** | Custom | Unlimited, self-hosted, SLA, dedicated support |

---

## 10. IMPLEMENTATION ROADMAP

### Phase 1: MVP (Weeks 1-4)
- [ ] Jira connector with OAuth
- [ ] Basic ticket import (paste JSON)
- [ ] AI pipeline (embeddings + clustering)
- [ ] Dashboard with cluster visualization
- [ ] Manual duplicate check UI

### Phase 2: Integration (Weeks 5-8)
- [ ] Slack webhook notifications
- [ ] Auto-sync (polling + webhooks)
- [ ] Auto-update Jira (priority, labels)
- [ ] Real-time duplicate detection

### Phase 3: Scale (Weeks 9-12)
- [ ] Multi-tenant architecture
- [ ] API keys for external integrations
- [ ] Advanced analytics
- [ ] User management + RBAC

### Phase 4: Enterprise (Weeks 13-16)
- [ ] Self-hosted deployment
- [ ] SSO/SAML
- [ ] Audit logs
- [ ] Advanced automation rules

---

## 11. COMPETITIVE LANDSCAPE

| Competitor | Strength | Weakness |
|------------|----------|----------|
| **PagerDuty** | Incident management | No AI clustering, expensive |
| **OpsGenie** | Alert routing | No intelligent triage |
| **Jira** | Native | Basic automation only |
| **Custom Scripts** | Free | No AI, maintenance burden |

**Differentiation:** AI-powered clustering + action recommendations + Jira/Slack native integration in one platform

---

## 12. SUCCESS METRICS

| Metric | Target (Year 1) |
|--------|-----------------|
| Customers | 50 paid customers |
| MRR | $25,000 |
| NRR | >100% |
| Churn | <5% monthly |
| MTTR Improvement | 30% reduction |
| Duplicate Detection | 40% of duplicates caught |

---

## 13. RISKS & MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Jira API changes | Medium | High | Abstract connector, version pinning |
| ML accuracy issues | High | Medium | Human feedback loop, tunable thresholds |
| Low adoption | Medium | High | Strong onboarding, templates |
| Data privacy concerns | Medium | High | Local processing option, GDPR compliance |
| Competition | Medium | Medium | Focus on AI differentiation |

---

## 14. APPENDIX

### A. AI Model Details
- **Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Clustering:** DBSCAN with configurable eps/min_samples
- **Similarity Threshold:** Default 0.85 (configurable 0.80-0.90)
- **Update Frequency:** Re-cluster on new tickets or daily batch

### B. Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/opsintel

# Redis
REDIS_URL=redis://localhost:6379

# Jira
JIRA_CLIENT_ID=xxx
JIRA_CLIENT_SECRET=xxx
JIRA_REDIRECT_URI=http://localhost:8000/auth/jira/callback

# Slack
SLACK_CLIENT_ID=xxx
SLACK_CLIENT_SECRET=xxx
SLACK_REDIRECT_URI=http://localhost:8000/auth/slack/callback

# App
SECRET_KEY=xxx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### C. Sample JQL Queries
```jql
# All recent incidents
project = "INC" AND created >= -7d ORDER BY created DESC

# Unassigned high priority
project = "INC" AND priority IN (High, Critical) AND assignee IS EMPTY

# Same summary pattern
project = "INC" AND summary ~ "timeout" AND created >= -30d
```

---

**Document Version:** 1.0  
**Last Updated:** March 2026  
**Author:** Optimus  
**Status:** Draft for Internal Review
