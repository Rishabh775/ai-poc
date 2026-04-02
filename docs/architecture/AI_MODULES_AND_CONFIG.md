# AI Modules and Configuration Guide

## Purpose

This document explains the main AI and ML modules used in the project, how the text normalization and semantic pipeline work, and what the important configuration values control.

It is intended to help reviewers and future contributors understand the backend intelligence layer before making changes.

---

## 1. High-level pipeline

The backend AI flow is:

1. Load tickets
2. Add symptom labels
3. Add broad taxonomy category labels
4. Optionally build dynamic categories
5. Normalize ticket text
6. Generate semantic embeddings
7. Build hybrid features from text + metadata
8. Cluster similar incidents
9. Compute confidence, metrics, summaries, and trends
10. Return processed insights to the UI

Main implementation: [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py)

---

## 2. Main modules

### 2.1 SentenceTransformer

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L17)
- [backend/config.py](/Users/induraghav/gitrepo/ai-poc/backend/config.py#L24)

What it does:
- Converts normalized ticket text into dense numeric vectors called embeddings
- Captures semantic meaning rather than exact wording

Why it matters:
- Tickets that describe the same problem in different words can still be grouped together
- This is the main semantic understanding layer in the system

Current default model:
- `paraphrase-mpnet-base-v2`

Example:
- "upload hangs at 99%"
- "file never completes uploading"

These may end up close in vector space even if the wording differs.

---

### 2.2 DBSCAN

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L647)

What it does:
- Groups incidents into clusters based on density
- Marks outliers as noise instead of forcing everything into a cluster

Why it matters:
- Good for issue clustering where we do not know the number of clusters in advance
- Helpful when some tickets do not belong to any recurring pattern

Main parameters:
- `DBSCAN_EPS`
- `MIN_SAMPLES`

Config source:
- [backend/config.py](/Users/induraghav/gitrepo/ai-poc/backend/config.py#L11)

---

### 2.3 HDBSCAN

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L633)

What it does:
- Alternative clustering algorithm to DBSCAN
- Handles variable-density clusters better

Why it matters:
- More flexible when some issue groups are very dense and others are sparse
- Often better for real operational datasets where clusters are uneven

Main parameters:
- `USE_HDBSCAN`
- `HDBSCAN_MIN_CLUSTER_SIZE`
- `HDBSCAN_MIN_SAMPLES`
- `HDBSCAN_CLUSTER_SELECTION_EPSILON`

Config source:
- [backend/config.py](/Users/induraghav/gitrepo/ai-poc/backend/config.py#L14)

Note:
- HDBSCAN is optional
- If it is disabled or unavailable, the processor falls back to DBSCAN

---

### 2.4 PCA

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L548)

What it does:
- Reduces dimensionality of embeddings before clustering

Why it matters:
- Removes some noise
- Makes clusters tighter
- Improves clustering stability and speed

Main parameters:
- `USE_PCA`
- `PCA_COMPONENTS`

Config source:
- [backend/config.py](/Users/induraghav/gitrepo/ai-poc/backend/config.py#L30)

---

### 2.5 OneHotEncoder

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L566)
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L613)

What it does:
- Converts categorical values into machine-readable numeric vectors

Used for:
- `category`
- `symptom`

Why it matters:
- Lets the clustering algorithm use structured metadata along with text embeddings

---

### 2.6 StandardScaler

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L602)

What it does:
- Scales severity values into a normalized numeric range

Why it matters:
- Prevents severity from dominating or being drowned out when combined with text features

---

### 2.7 silhouette_samples

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L656)

What it does:
- Measures how well each ticket fits inside its assigned cluster compared with other clusters

Why it matters:
- Used as part of cluster quality assessment
- Helps estimate whether clusters are meaningful or weak

---

## 3. Classification and enrichment modules

### 3.1 Broad category classification

Location:
- [backend/category_classifier.py](/Users/induraghav/gitrepo/ai-poc/backend/category_classifier.py)

Purpose:
- Assigns a stable taxonomy category such as:
  - `File handling`
  - `Access control`
  - `Status tracking`

How it works:
- Either semantic similarity against category descriptions
- Or optional LLM-assisted classification if enabled

Why it exists:
- Gives a business-friendly broad grouping
- Adds metadata to clustering

---

### 3.2 Symptom classification

Location:
- [backend/symptom_classifier.py](/Users/induraghav/gitrepo/ai-poc/backend/symptom_classifier.py)

Purpose:
- Captures the actual failure mode

Examples:
- `Timeout`
- `Stuck progress`
- `Data corruption`
- `Download failure`
- `Access error`

Why it exists:
- Broad category alone is often too coarse
- Helps distinguish similar workflows with different failure patterns

---

### 3.3 Dynamic category generation

Location:
- [backend/dynamic_category.py](/Users/induraghav/gitrepo/ai-poc/backend/dynamic_category.py)

Purpose:
- Creates smarter labels by combining topic and symptom

Examples:
- `Upload - Timeout`
- `Upload - Data corruption`
- `Review Workflow - Missing UI action`

Why it exists:
- Makes labels more useful for humans
- Helps prevent many tickets from collapsing into one very broad category

---

## 4. How normalization works

Main normalization logic:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L186)

### 4.1 Standard normalization

Default mode:
- Lowercase text
- Replace known wording variants using synonym rules
- Remove domain noise words
- Remove emails
- Remove ticket/manuscript IDs
- Collapse extra whitespace

Examples of synonym cleanup:
- `does not` -> `doesn't`
- `not loading` -> `broken`
- `failing` -> `broken`

Why this helps:
- Reduces wording noise before generating embeddings
- Makes semantically similar tickets even closer

### 4.2 LLM normalization

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L257)

Purpose:
- Rewrites tickets into short canonical problem statements using Gemini

Why it helps:
- Better at collapsing different phrasings of the same issue into the same semantic form

Requirements:
- `USE_LLM_NORMALIZATION=true`
- valid `GEMINI_API_KEY`

### 4.3 Local normalization

Location:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L346)

Purpose:
- Uses a local FLAN-T5 model instead of a hosted LLM

Why it helps:
- Keeps the pipeline usable without an API key

Tradeoff:
- Heavier local runtime

---

## 5. How semantics work

The semantic layer is based on:

1. text normalization
2. embedding generation
3. cosine similarity
4. density-based clustering

### Duplicate detection

Duplicate detection uses:
- normalized title or title+description
- embedding generation
- cosine similarity against existing tickets

This allows the system to find likely duplicates even when wording differs.

### Clustering semantics

Cluster formation is mainly driven by:
- semantic text embeddings

Then adjusted by:
- category metadata
- symptom metadata
- severity metadata

This creates a hybrid clustering system rather than a pure keyword system.

---

## 6. Hybrid feature construction

Main implementation:
- [backend/ai_processor.py](/Users/induraghav/gitrepo/ai-poc/backend/ai_processor.py#L526)

The hybrid feature vector combines:
- text embeddings
- category one-hot encoding
- symptom one-hot encoding
- scaled severity value

This is controlled by weights in config:
- `HYBRID_WEIGHT_TEXT`
- `HYBRID_WEIGHT_CATEGORY`
- `HYBRID_WEIGHT_SEVERITY`
- `HYBRID_WEIGHT_SYMPTOM`

Design intent:
- text remains the strongest signal
- metadata lightly nudges the clustering in smarter directions

---

## 7. Configuration reference

Main config file:
- [backend/config.py](/Users/induraghav/gitrepo/ai-poc/backend/config.py)

### Similarity and clustering

`SIMILARITY_THRESHOLD`
- Used for duplicate detection cutoff

`DBSCAN_EPS`
- Neighborhood distance threshold for DBSCAN

`MIN_SAMPLES`
- Minimum nearby tickets needed to form a DBSCAN cluster

`USE_HDBSCAN`
- Enables HDBSCAN instead of DBSCAN

`HDBSCAN_MIN_CLUSTER_SIZE`
- Minimum size of an HDBSCAN cluster

`HDBSCAN_MIN_SAMPLES`
- Density sensitivity for HDBSCAN

`HDBSCAN_CLUSTER_SELECTION_EPSILON`
- Controls cluster splitting/merging behavior in HDBSCAN

### Embeddings and hybrid weighting

`EMBEDDING_MODEL`
- SentenceTransformer model name

`HYBRID_WEIGHT_TEXT`
- Weight assigned to text embeddings

`HYBRID_WEIGHT_CATEGORY`
- Weight assigned to broad/dynamic category metadata

`HYBRID_WEIGHT_SEVERITY`
- Weight assigned to severity metadata

`HYBRID_WEIGHT_SYMPTOM`
- Weight assigned to symptom metadata

### Dimensionality reduction

`USE_PCA`
- Enables PCA before clustering

`PCA_COMPONENTS`
- Number of PCA dimensions to retain

### Severity and impact

`SEVERITY_WEIGHTS`
- Used when calculating impact score
- Higher severity contributes more to overall cluster impact

### Classification

`CLASSIFIER_ENABLED`
- Enables LLM-based category classification
- If disabled, semantic classifier fallback is used

`CATEGORY_MODE`
- Controls whether categories remain broad or become dynamic

### LLM and local normalization

`GEMINI_API_KEY`
- API key for Gemini-based features

`LLM_MODEL`
- Gemini model name

`USE_LLM_NORMALIZATION`
- Enables hosted LLM normalization

`LLM_NORMALIZATION_BATCH_SIZE`
- Batch size for LLM rewriting

`USE_LOCAL_NORMALIZATION`
- Enables local FLAN-T5 normalization

`LOCAL_NORMALIZATION_MODEL`
- Name of the local normalization model

### Taxonomy

`CATEGORY_LIST`
- Broad category vocabulary used by the classifier

---

## 8. Runtime behavior summary

At startup:
- FastAPI loads tickets
- The AI processor runs the full pipeline
- The result is stored in memory as `insights_cache`

During API use:
- the frontend reads cached insights for fast rendering
- duplicate checks use semantic similarity
- cluster mutations trigger reprocessing

This means the current system behaves like a lightweight POC intelligence engine with in-memory runtime state rather than a persistent production platform.

---

## 9. Main dependencies used

Backend dependencies:
- `sentence-transformers` for semantic embeddings
- `scikit-learn` for PCA, encoders, scaling, clustering, and quality metrics
- `hdbscan` for optional advanced clustering
- `pandas` and `numpy` for data handling and numeric operations
- `fastapi` and `pydantic` for API serving and request models
- `google-genai` for optional Gemini-based normalization and classification

Dependency list:
- [backend/requirements.txt](/Users/induraghav/gitrepo/ai-poc/backend/requirements.txt)

---

## 10. Short explanation for demos

If you need to explain the backend quickly:

“The system cleans ticket text, understands meaning through embeddings, adds structured signals like category and symptom, clusters similar incidents with DBSCAN or HDBSCAN, and then computes confidence, trends, and impact so the dashboard can prioritize what matters most.”

