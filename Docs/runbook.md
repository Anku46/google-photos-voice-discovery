# Google Photos Discovery Engine Runbook

This runbook outlines operational procedures and troubleshooting for the Google Photos Discovery Engine (v2) deployment on Railway and Vercel.

## 1. Groq Quota Exhaustion

**Symptom:** Pipeline run fails or Copilot chat returns errors containing `rate_limit_exceeded` or `budget exceeded`.
**Context:** Groq free tier imposes limits on RPM (Requests Per Minute), RPD (Requests Per Day), and TPM (Tokens Per Minute). Our local budget tracker (`groq_budget.json`) pauses the pipeline at 14,000 requests/day.

**Resolution:**
1. Wait for the daily reset (midnight UTC).
2. If this is a critical run, upgrade the Groq account to a paid tier to increase limits.
3. Once upgraded, manually edit `src/pipeline/groq_client.py` to increase `MAX_DAILY_REQUESTS`.
4. Run the pipeline again. The orchestrator is designed to resume from the last successful stage.

## 2. Scraper Failures

**Symptom:** Ingestion stage (Play Store, App Store, or Reddit) throws 5xx errors or 429 Too Many Requests, causing the pipeline to halt.
**Context:** Scrapers are fragile. We use exponential backoff, but prolonged blocks can still occur.

**Resolution:**
1. **Reddit / Play Store:** Wait 15-30 minutes and trigger the pipeline again. The backoff logic and duplicate tracking ensure no data is duplicated on retry.
2. **App Store:** `app-store-scraper` is highly volatile. If it breaks completely due to Apple DOM changes, the architecture supports swapping it. Go to `src/ingestion/app_store.py` and replace `AppStoreScraperLib` with an RSS-based scraper fallback.

## 3. Supabase Pausing (Free Tier)

**Symptom:** API requests return `500 Internal Server Error`, or the database connection times out (`psycopg2.OperationalError` or Supabase `AuthError`).
**Context:** Supabase pauses free-tier projects after 1 week of inactivity.

**Resolution:**
1. Log into the Supabase Dashboard.
2. Select the `discovery-engine` project.
3. Click **"Restore Project"**. This process takes ~2-5 minutes.
4. Once active, the FastAPI backend will automatically reconnect on the next request.

## 4. Pipeline Orchestrator Resumption

**Symptom:** A pipeline run fails midway through (e.g., during extraction).
**Context:** The orchestrator writes state to the `PIPELINE_RUNS` table.

**Resolution:**
1. Check the logs in the Railway dashboard or via `/api/pipeline/status` to identify the failing stage.
2. Fix the underlying issue (e.g., API key expiry).
3. Trigger a new run via the Dashboard. The pipeline relies on `text_hash` and `experience_id` uniqueness constraints to safely skip records it already processed in the previous run.

## 5. Deployment / Build Failures

**Symptom:** Vercel frontend build fails.
**Context:** The frontend is a static Vite + React app.
**Resolution:**
1. Ensure `VITE_API_BASE_URL` is set correctly in the Vercel project settings.
2. Check for missing dependencies in `package.json` (e.g., `recharts`, `lucide-react`).
