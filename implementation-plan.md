# Phase-Wise Implementation Plan v2: Google Photos Discovery Engine

This document outlines the step-by-step, phased execution strategy to build the AI-Powered User Feedback Discovery Engine for Google Photos. It incorporates all v2 revisions from the design review. Changes relative to v1 are marked **[FIX]**.

This plan translates the requirements from `context.md` and `architecture.md` into actionable engineering phases.

---

## Decisions Locked Before Coding

| Topic | Decision |
|---|---|
| Structured output | Let `instructor` own the JSON mode. Do not also set `response_format` by hand. |
| Clustering library | Use `sklearn.cluster.HDBSCAN` (scikit-learn >= 1.3). Drop the standalone `hdbscan` package. **[FIX]** |
| Frontend | One stack: Vite + React + Recharts, built to static files and hosted on **Vercel**. No Next.js server. FastAPI does not serve the frontend. **[FIX]** |
| Backend hosting | **Railway**, deployed from a Dockerfile (CPU-only PyTorch, embedding model baked into the image). **[FIX]** |
| Secrets | All third-party keys (Groq, Supabase service key, API key) live only in Railway variables. The browser never receives a secret. **[FIX]** |
| Gap labels | Each review gets a `primary_gap` and an optional `secondary_gap`. **[FIX]** |
| "Funnel" | Rename to **Failure Distribution**. One label per review is a distribution, not stage-to-stage drop-off. **[FIX]** |
| Model IDs | Read from config/env, never hardcoded. Check Groq's current model list and limits (RPM, TPM and daily caps) before Phase 3. **[FIX]** |
| Stage numbering | Stage 1 Ingest, 2 Sanitize, 3 Filter, 4 Extract, 5 Classify, 6 Cluster, 7 Synthesize, 8 Top Issues. **[FIX]** |

---

## Phase 1: Foundation, Schemas, Golden Set (Week 1)
**Goal:** Repo, schemas, database, and a labeled evaluation set before any LLM work.

*   **Step 1.1: Environment Initialization:**
    *   Initialize a Python 3.11+ virtual environment (`venv`).
    *   Install core dependencies: `fastapi`, `pydantic`, `groq`, `instructor`, `supabase`, `sentence-transformers`, `scikit-learn`, `umap-learn`, `pytest`.
    *   **[FIX]** No standalone `hdbscan` — use `sklearn.cluster.HDBSCAN` (scikit-learn >= 1.3).
*   **Step 1.2: Define Pydantic Contracts:**
    *   Translate `architecture.md` schemas into strict Python Pydantic v2 models: `MemoryClues`, `RetrievalExperienceExtraction`, `JourneyClassification`.
    *   **[FIX]** `JourneyClassification` must include `primary_gap` and an optional `secondary_gap` field.
    *   Define a response model per API endpoint.
*   **Step 1.3: Database Setup (`db.py`):**
    *   Set up a Supabase project and connect via the official Python client.
    *   Create relational tables: `REVIEWS` (sanitized only), `FILTERED_REVIEWS`, `RETRIEVAL_EXPERIENCES`, `FAILURE_CLASSIFICATIONS`, `THEMATIC_CLUSTERS`, `PM_INSIGHTS`.
    *   **[FIX]** Add `PIPELINE_RUNS` table (run id, stage, status, timestamps, error) and `TOP_ISSUES` table. Review rows carry `source`, `rating`, `review_date`, `app_version`, `language`, `text_hash`.
*   **Step 1.4: [FIX] Golden Evaluation Set:**
    *   Hand-label ~100 reviews: relevant or not, extraction fields, primary and secondary gap. Store in `eval/golden.jsonl`.
    *   Include reviews the keyword pre-filter would reject, to measure its recall.
*   **Step 1.5: [FIX] Security Baseline:**
    *   Enable Supabase row-level security. Keep all keys in env vars.
    *   Confirm Supabase free-tier inactivity and pause policy.

**Exit criteria:** Schemas validate sample data. The golden set exists. `pytest` runs.

---

## Phase 2: Ingestion & Privacy (Week 2)
**Goal:** Collect data and sanitize it before anything is stored.

*   **Step 2.1: Implement Scrapers (`ingestion/`):**
    *   Write `play_store.py` utilizing the `google-play-scraper` library.
    *   Write `app_store.py` utilizing the `app-store-scraper` library.
    *   Write `reddit.py` using standard `httpx` calls to public `.json` endpoints.
    *   **[FIX]** Treat `app-store-scraper` as fragile: isolate it behind an interface so it can be swapped for Apple's RSS feed or dropped without breaking the pipeline.
*   **Step 2.2: Rate Limiting & Politeness:**
    *   Enforce a mandatory 1-second delay between all external scraping requests.
    *   Retry with exponential backoff on 429/5xx responses.
*   **Step 2.3: [FIX] Sanitize Before Persist (`pipeline/sanitize.py`):**
    *   Drop usernames and avatars **in memory**, assign synthetic IDs (e.g., `rev_001`), mask emails and phones, **then** store. Raw PII never reaches the database.
    *   **[FIX]** Extend regex scrubber to URLs and obvious `@handles`. State clearly in docs that regex does not catch names or addresses.
*   **Step 2.4: Deduplication:**
    *   Implement SHA-256 hash of normalized sanitized text to prevent duplicate ingestions.
*   **Step 2.5: [FIX] Incremental Ingestion:**
    *   Skip existing hashes on re-run; only new rows move downstream.
*   **Step 2.6: [FIX] Terms Check:**
    *   Review Play Store, App Store, and Reddit terms for scraping and ML use if this goes beyond personal or academic use.

**Exit criteria:** Seeded test PII (emails, phones, handles) is absent from the DB. A re-run inserts 0 duplicates.

---

## Phase 3: Groq LLM Processing Pipeline (Weeks 3–4)
**Goal:** Filter, extract, classify — with measurement at each stage.

*   **Step 3.1: Groq API Setup & Rate Limiting:**
    *   Configure Groq API keys and implement a token-bucket rate limiter with exponential backoff.
    *   **[FIX]** Add a daily request/token budget counter that pauses the run and resumes at the next quota window. Read model IDs from config/env — never hardcode them.
*   **Step 3.2: [FIX] Prompt-Injection Hygiene:**
    *   Wrap review text in delimiters and instruct the model to treat it as data only.
    *   Validate every output against the Pydantic schema; reject and log failures.
*   **Step 3.3: Stage 3 Filtering (`pipeline/filter.py`):**
    *   Build the Heuristic Lexical Pre-Filter (regex keyword matching).
    *   Implement Semantic Classifier using Groq `llama-3.1-8b-instant`.
    *   **[FIX]** Log every rejected review with its reason, and sample rejects weekly to estimate lost recall.
*   **Step 3.4: Stage 4 Cognitive Extraction (`pipeline/extract.py`):**
    *   Implement the extraction agent using Groq `llama-3.3-70b-versatile`.
    *   **[FIX]** Use `instructor` (not `response_format` manually) to map raw text to the `RetrievalExperienceExtraction` schema.
*   **Step 3.5: Stage 5 Journey Classification (`pipeline/classify.py`):**
    *   Use Groq `llama-3.3-70b-versatile` to map failures into the 5 Gaps (Memory Expression, Interpretation, Retrieval, Recognition, Refinement).
    *   **[FIX]** Assign `primary_gap` and an optional `secondary_gap` per review.
*   **Step 3.6: [FIX] Eval Harness (`eval/run_eval.py`):**
    *   Score each stage against the golden set. Proposed starting targets: filter recall >= 0.90, gap accuracy reported with a confusion matrix.
    *   Run on every prompt or model change.

**Exit criteria:** Eval report committed. Prompts tuned until targets are met or the shortfall is documented.

---

## Phase 4: Clustering & PM Insight Synthesis (Week 5)
**Goal:** Reproducible clusters and insights that can be verified.

*   **Step 4.1: [FIX] Local Embedding Generation (`pipeline/cluster.py`):**
    *   Combine Target, Clues, Search, and a trimmed excerpt of the user's own sanitized words into the embedding text.
    *   **[FIX]** Do **not** include the Gap label in the embedding string — clusters should not simply mirror the gap categories.
    *   Embed locally with `sentence-transformers` (`all-MiniLM-L6-v2`) on CPU, zero API cost.
    *   Flag non-English reviews via the `language` field; route them aside.
*   **Step 4.2: [FIX] UMAP + HDBSCAN Clustering:**
    *   Fix `random_state`; expose `min_cluster_size` and `min_samples` in config.
    *   Report the noise fraction (label -1). Try a few parameter settings and keep the one that is stable across seeds.
    *   **[FIX]** Show noise as an **"Unclustered"** bucket in the dashboard — do not hide it.
*   **Step 4.3: [FIX] Stage 7 PM Insight Synthesis:**
    *   Send 5–10 samples per cluster (nearest to medoid **plus** a few spread across the cluster) with cluster size and gap mix. Do not rely on a single medoid.
    *   Use Groq `llama-3.3-70b-versatile` to synthesize the PM-ready insight (User Situation, Behavior, Failure, Underlying Problem, Opportunity).
*   **Step 4.4: [FIX] Hallucination Guardrail / Verifier:**
    *   (a) Quotes must be exact substrings of the **sanitized** text (not raw).
    *   (b) All counts, percentages, and rankings are computed in code and injected; LLM output containing numbers is checked against them.
    *   (c) Failures trigger one retry, then the field is dropped.
*   **Step 4.5: [FIX] Recency Tracking:**
    *   Store `review_date` and `app_version` per review.
    *   Show per-cluster date range and recent-share so fixed problems are not reported as current.

**Exit criteria:** Same input and seed give the same clusters. Verifier passes on all stored insights.

---

## Phase 5: FastAPI Backend API (Week 6)
**Goal:** Safe, observable API.

*   **Step 5.1: FastAPI Application (`app.py`):**
    *   Initialize FastAPI with structured errors and automatic OpenAPI docs.
    *   Add `GET /health` endpoint for Railway health checks.
    *   **[FIX]** No static frontend mount. CORS reads `ALLOWED_ORIGINS` from env (the Vercel production URL). Do not allow all `*.vercel.app` origins.
*   **Step 5.2: API Endpoints:**
    *   `GET /api/metrics` — Totals, yield %, gap counts, cluster count, per-source counts.
    *   `GET /api/clusters` — All thematic clusters with labels, sizes, gap breakdown, medoid quotes, and an "Unclustered" entry.
    *   `GET /api/clusters/{cluster_id}` — Deep-dive: PM insight card, all member reviews, evidence quotes.
    *   `GET /api/distribution` — **[FIX]** (renamed from `/funnel`) Counts per primary gap and secondary-gap overlay.
    *   `GET /api/reviews` — Paginated, filterable (source, gap, cluster, rating, keyword).
    *   `GET /api/top-issues` — Read from `TOP_ISSUES` table.
    *   `POST /api/pipeline/run` — **[FIX]** Returns a run ID immediately; work runs as a background task (non-blocking).
    *   `GET /api/pipeline/status` — **[FIX]** Returns current stage, per-stage status, last run time, last error.
    *   `POST /api/chat` — RAG endpoint for the AI Copilot.
*   **Step 5.3: Response Models:**
    *   Define Pydantic response schemas for every endpoint.
*   **Step 5.4: [FIX] Auth & Abuse Control:**
    *   Read endpoints are public. `/api/pipeline/run` and `/api/chat` require credentials.
    *   Use a **Vercel serverless proxy** (`frontend/api/`) that injects the API key server-side — keeps secrets out of the browser.
    *   Add per-IP rate limits on `/chat`. Pipeline run lock lives in the `PIPELINE_RUNS` table (survives restarts).
*   **Step 5.5: [FIX] Copilot Design (`POST /api/chat`):**
    *   Route questions to (a) SQL aggregates for counts/rankings and (b) in-memory NumPy cosine-similarity search for quotes.
    *   LLM answers only from retrieved context, cites review IDs, verifier checks quotes and numbers before reply is returned.
    *   Refuse questions the data cannot answer.
*   **Step 5.6: [FIX] Stage 8, Top Issues (`pipeline/top_issues.py`):**
    *   Generate from clusters ranked by size, recency, and severity computed in code. Write to `TOP_ISSUES` table (replaces unowned `top5_issues_analysis.json`). Impact bars use real review counts.
*   **Step 5.7: Pipeline Orchestrator (`pipeline/orchestrator.py`):**
    *   Sequential stages with per-stage logging to `PIPELINE_RUNS`, **resumable from the last completed stage**.

**Exit criteria:** Pipeline run is non-blocking, status updates live, unauthenticated calls to `/pipeline/run` and `/chat` are rejected.

---

## Phase 6: Frontend Dashboard (Weeks 7–8)
**Goal:** Dashboard that surfaces insights honestly and stays fast.

Visual design tokens (dark slate palette `#0F172A`, card surfaces `#1E293B`, teal-to-violet accent `#06B6D4→#8B5CF6`, Inter font, 4px spacing, 12px card radius) are unchanged from v1.

### 6.1: Setup & Foundation

*   **Step 6.1.1: Project Setup:**
    *   Initialize a **Vite + React** frontend inside `frontend/`. **[FIX]** Not Next.js — static build deployed on Vercel.
    *   Install: `recharts`, `lucide-react`.
    *   **[FIX]** API base URL comes from `VITE_API_BASE_URL` (public value, baked in at build time; redeploy after changing it).
    *   Add `vercel.json` with a rewrite to `index.html` for client-side routing.
*   **Step 6.1.2: Design Tokens (`index.css`):**
    *   All tokens as `--color-*`, `--space-*`, `--radius-*`, `--shadow-*` CSS custom properties.
    *   Import `Inter` from Google Fonts (weights 400, 500, 600, 700). Base 16px, heading scale 1.25.
    *   **[FIX]** Use `backdrop-filter` sparingly — header and modal only; respect `prefers-reduced-motion`.
*   **Step 6.1.3: Layout Shell:**
    *   Full-viewport dark background, centered max-width ~1400px.
    *   Sticky header with app title, status dot driven by `/api/pipeline/status` (green = ready, amber = running).
    *   Source breakdown pill badges with exact review counts per source.
    *   Responsive CSS Grid: 2-column desktop (≥1280px), single-column below 768px.

### 6.2: Dashboard Components

*   **Step 6.2.1: Executive Metrics Bar:**
    *   4 glassmorphism stat cards: Total Reviews, Retrieval Yield %, Relevant Reviews, Thematic Clusters.
    *   Count-up animation (`requestAnimationFrame`, ~1.2s easeOutExpo). Staggered `fadeInUp` entrance.

*   **Step 6.2.2: [FIX] Failure Distribution Panel (was: Cognitive Journey Funnel):**
    *   Horizontal bars (Recharts) for the 5 gaps. Toggle % vs. Mentions. Click filters the VoC table.
    *   **[FIX]** Include secondary-gap counts as a lighter overlay on bars.
    *   **[FIX]** Label it clearly as a **distribution**, not a drop-off funnel.

*   **Step 6.2.3: Top 5 Issues Panel:**
    *   Vertically stacked cards from `/api/top-issues`. Rank badge, title, category tag, impact bar (uses real review counts), expandable root cause / quotes / recommendation.
    *   `hover:translateY(-2px)` lift effect.

*   **Step 6.2.4: Thematic Cluster Explorer:**
    *   Grid of cluster cards (2–3 per row desktop). **[FIX]** Include an **"Unclustered"** card for HDBSCAN noise.
    *   Each card: label, size badge, dominant gap tag, medoid quote preview.
    *   Click → PM Insight Drilldown Modal (User Situation, Behavior, Underlying Cause, Opportunity + scrollable evidence quotes). `scale(0.95→1)` entrance with backdrop blur.

*   **Step 6.2.5: VoC Evidence Table:**
    *   Sticky header, alternating rows, horizontal scroll on mobile (becomes card-list on mobile). **[FIX]**
    *   Columns: Review Quote, Memory Clues, Search Attempt, Failure Gap (color-coded badge **+ text label**), Source, Rating, Date.
    *   Filters: Source, Failure Gap, Cluster, Rating, debounced keyword search. Pagination.
    *   Empty state with friendly illustration.

*   **Step 6.2.6: Pipeline Control Panel:**
    *   "Run Pipeline" button → calls Vercel proxy → non-blocking POST. Spinner state.
    *   Stage progress driven by polling `/api/pipeline/status`. Per-stage status icons. Last run timestamp.

*   **Step 6.2.7: [FIX] AI Copilot (Chat Interface):**
    *   Floating or right-panel chat driven by `/api/chat` (via Vercel proxy).
    *   **[FIX]** Suggestion chips written for Google Photos retrieval: e.g., "Top search failures", "Can't find old photos", "Wrong results for a query". Remove fit/sizing or wishlist chips from any earlier project.
    *   Show citations (review IDs) and an "insufficient data" reply when the data cannot answer.

### 6.3: Animations & Micro-Interactions

*   **Entrance Animations:** Staggered `fadeInUp` via `IntersectionObserver`.
*   **[FIX]** Respect `prefers-reduced-motion` — disable transitions/animations if set.
*   **Chart Animations:** Recharts animation ~800ms `easeOutQuart`.
*   **Hover Effects:** Cards lift (`translateY(-2px)`), shadow expansion. Buttons `brightness(1.1)`. Table rows left-border highlight.
*   **Loading States:** Skeleton shimmer placeholders for all data sections.
*   **Transitions:** `transition: all 0.2s ease` for interactive state changes.

### 6.4: [FIX] Responsive Design & Accessibility

*   **Breakpoints:** ≥1280px (2-col desktop), ≥768px (adjusted grid), <768px (single-col stack).
*   **Mobile:** Distribution chart → vertical. Cluster grid → single column. VoC table → card list. Modal → full-screen sheet.
*   **Touch Targets:** All interactive elements ≥44px.
*   **[FIX] Accessibility:** Keyboard-navigable modal with focus trap. Gap badges paired with text labels — not color-only. Lighthouse Accessibility target ≥95.

### 6.5: Integration & Polish

*   **Step 6.5.1: API Integration:**
    *   `fetch()` calls to all `/api/*` endpoints with proper error handling and retry logic.
    *   Loading → Data → Error state management for every section.
*   **Step 6.5.2: [FIX] Performance:**
    *   Measure Lighthouse on a mid-range mobile profile early. If glassmorphism conflicts with Performance ≥90 target, drop the effect.
    *   Target: Lighthouse Performance ≥90, Accessibility ≥95.

---

## Phase 7: Integration, Hardening & Handoff (Week 9)

*   **7.1** End-to-end test on a fixture dataset; verify every dashboard card traces to a cluster, a review quote, and its source.
*   **7.2** Regression suite: eval harness and verifier tests run in CI on every prompt or model change.
*   **7.3** Cross-browser (Chrome, Firefox, Edge) and 3 breakpoints.
*   **7.4 [FIX] Limitations Page in Dashboard:** Reviews skew toward extreme experiences — counts are not user-base prevalence. Show golden-set accuracy numbers and the date range covered.
*   **7.5 [FIX] Runbook Docs:** Runbook for Groq quota exhaustion, scraper failures, and Supabase pausing.

---

## Phase 8: Deployment — Railway (Backend) + Vercel (Frontend) (Week 10)
**Goal:** Live, secure, and observable deployment. Deploy the backend first, then the frontend, then close the CORS loop.

### 8.1 Repo Layout
```
repo/
  backend/    # app.py, pipeline/, requirements.txt, Dockerfile
  frontend/   # Vite + React, vercel.json, api/ (optional proxy functions)
```

### 8.2 Backend on Railway
1.  **Dockerfile** (`backend/Dockerfile`): `python:3.11-slim`, install CPU-only PyTorch from the PyTorch CPU index, then `requirements.txt`, then **pre-download `all-MiniLM-L6-v2` in a build step** so it is not fetched on every restart. Start with `uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}`.
2.  Create a Railway project from the GitHub repo and set **Root Directory** to `backend`.
3.  **Variables:** `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `API_KEY`, `ALLOWED_ORIGINS`, plus model IDs and clustering parameters from config.
4.  Generate a public domain and set the health-check path to `/health`.
5.  Confirm `/docs` loads on the Railway URL.

### 8.3 Frontend on Vercel
1.  Import the repo, set **Root Directory** to `frontend`, framework Vite, build `npm run build`, output `dist`.
2.  Set `VITE_API_BASE_URL` to the Railway URL.
3.  If using the proxy option: add serverless functions in `frontend/api/` and store `API_KEY` as a **server-side** Vercel variable (no `VITE_` prefix — never exposed to browser).
4.  Deploy, then add the Vercel production URL to `ALLOWED_ORIGINS` on Railway and redeploy the backend.

### 8.4 Operational Rules
*   **Memory:** Embedding, UMAP, and HDBSCAN need real RAM. Watch Railway's memory graph on the first full run; size the plan up if the process is killed.
*   **Ephemeral Disk:** Nothing important is written to the container filesystem. All state is in Supabase.
*   **Redeploys interrupt running jobs.** The resumable orchestrator (Phase 5.7) picks up from the last completed stage. Avoid deploying mid-run.
*   **Status Polling:** The frontend polls `/api/pipeline/status` every few seconds. No websockets needed.
*   **Monitoring:** Use Railway logs for per-stage errors; track Groq quota usage and Supabase pause status in the runbook.

### 8.5 Deployment Checklist
1.  `GET /health` returns 200 on the Railway URL.
2.  The Vercel site loads data with no CORS errors in the browser console.
3.  Calls to `/api/pipeline/run` and `/api/chat` without credentials are rejected.
4.  No secret appears in the built frontend bundle or in browser network requests.
5.  A pipeline run keeps going after the page is refreshed, and the status dot updates.
6.  A redeploy mid-run resumes correctly from the last completed stage.

---

## Open Questions & Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Multilingual reviews | **Out of Scope (English Only).** Add a language filter; document as a constraint. |
| 2 | Use case scope | **Academic / Portfolio.** Scraping public sources is within fair use for research. |
| 3 | Chat retrieval: pgvector vs in-memory | **In-Memory.** At ~1,000–2,000 reviews, a NumPy cosine-similarity array uses <50MB and runs in milliseconds. |
| 4 | Protecting `/pipeline/run` & `/chat` | **Vercel Serverless Proxy.** A `frontend/api/run.js` function injects a hidden `process.env.API_SECRET` before forwarding. |
| 5 | Dashboard access | **100% Public (Read-Only).** Only execution endpoints are locked behind the proxy key. |
