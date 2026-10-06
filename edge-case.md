# Edge Cases & Corner Scenarios: Google Photos Feedback Discovery Engine

This document outlines the potential edge cases, corner scenarios, and failure modes across the pipeline for the AI-powered user feedback discovery engine, along with recommended mitigation strategies.

---

## 1. Data Ingestion & Pre-Filtering Edge Cases

### 1.1 Non-Standard Terminology & False Negatives (Lexical Pre-Filter)
- **Scenario:** A user describes a retrieval failure without using standard keywords (e.g., `search`, `find`, `retrieve`, `remember`).
  - *Example:* "Where did the picture of my dog go? I typed it in the bar at the top and got nothing."
- **Impact:** The review is dropped by the Stage 2A Keyword Pre-Filter before it ever reaches the LLM.
- **Mitigation:** Maintain a robust, continuously updated synonym list (e.g., "typed in", "bar at the top", "looking for", "disappeared"). Periodically sample the discarded pile with the LLM to identify missing keywords.

### 1.2 False Positives in Heuristics
- **Scenario:** A review contains retrieval keywords but is entirely unrelated to photo search.
  - *Example:* "I lost my phone, but I remember I backed up my photos. Good app."
- **Impact:** Passes the pre-filter, consuming Groq LLM tokens in Stage 2B unnecessarily.
- **Mitigation:** This is an acceptable edge case. Stage 2B (Groq `llama-3.1-8b-instant`) is specifically designed to catch and discard these semantic false positives cheaply.

### 1.3 Multilingual & Mixed-Language Reviews
- **Scenario:** Users write reviews in languages other than English, or use "Hinglish" / mixed scripts.
  - *Example:* "Search kaam nahi kar raha, I can't find my old pics."
- **Impact:** The regex pre-filter misses them, or the LLM extractor misinterprets the memory clues.
- **Mitigation:** The ingestion script should filter by language metadata (e.g., Play Store `&hl=en` flag) to ensure the initial scope is English-only. Future iterations can add language detection (e.g., `langdetect`) before pre-filtering.

### 1.4 Unconventional PII Formatting
- **Scenario:** Users obfuscate their contact info, evading simple regex scrubbers.
  - *Example:* "Contact me at john dot doe at gmail dot com" or international phone formats like "+44 (0) 7911 123456".
- **Impact:** PII slips through into the database and dashboard.
- **Mitigation:** Use robust, battle-tested regex libraries for PII. If high sensitivity is required, utilize a fast, dedicated local NER (Named Entity Recognition) model (like Presidio) instead of just regex.

---

## 2. LLM Extraction & Journey Classification Edge Cases

### 2.1 The "Unknown" Gap (Lack of Detail)
- **Scenario:** A user states a clear failure but provides zero context on their search attempt or memory.
  - *Example:* "Can't find my photos anymore. Search is broken."
- **Impact:** The Cognitive Journey Classifier (Stage 4) cannot accurately determine if it was a Memory Expression, Interpretation, or Retrieval gap.
- **Mitigation:** The schema must include an `INSUFFICIENT_CONTEXT` enum value for the `failure_gap` field. The LLM should be instructed to default to this rather than hallucinating a specific gap.

### 2.2 Sarcasm and Irony
- **Scenario:** The user employs sarcasm, combining positive sentiment words with a retrieval failure.
  - *Example:* "Great job Google, I absolutely love searching for my medical records and getting pictures of my cat."
- **Impact:** Semantic classifiers or sentiment-based filters might mislabel this as a successful or positive interaction.
- **Mitigation:** Groq running `llama-3.3-70b-versatile` has high contextual reasoning and should correctly classify this as a `RETRIEVAL_GAP` failure, provided the prompt explicitly warns against sarcasm.

### 2.3 Multi-Intent Reviews (The "Kitchen Sink" Review)
- **Scenario:** A user writes a massive paragraph complaining about UI changes, battery life, pricing, AND a search failure.
- **Impact:** The LLM might truncate the extraction or get confused by the noise, diluting the focus on the search experience.
- **Mitigation:** Instruct the LLM in the system prompt to explicitly ignore all non-search-related complaints during the Stage 3 Cognitive Extraction phase.

### 2.4 Ambiguous Memory Clues
- **Scenario:** The user describes their memory in highly subjective or ambiguous terms.
  - *Example:* "I searched for the thing with the blue thing."
- **Impact:** The structured JSON extraction attempts to force this into `objects` or `visual_cues` but struggles with categorization.
- **Mitigation:** Keep Pydantic schemas flexible (e.g., `Optional[List[str]]`). Instruct the LLM to leave fields null if the clue is too vague to categorize definitively.

---

## 3. Clustering & Insight Generation Edge Cases

### 3.1 The "Everything Else" Mega-Cluster
- **Scenario:** HDBSCAN produces one massive cluster containing 60% of the data, grouping vaguely related failures because the embedding space isn't perfectly separated.
- **Impact:** The generated PM Insight is too generic to be actionable (e.g., "Users are having trouble finding things").
- **Mitigation:** Implement hierarchical clustering or sub-clustering. If a cluster exceeds a certain size threshold (e.g., >25% of data), recursively apply HDBSCAN on that cluster's embeddings to break it down into micro-themes.

### 3.2 Highly Specific Micro-Clusters (Orphaned Scenarios)
- **Scenario:** A small number of users have a highly unique but valid retrieval failure (e.g., searching for a specific rare breed of dog).
- **Impact:** HDBSCAN labels these as "noise" (Cluster -1), and they never reach the dashboard.
- **Mitigation:** Periodically sample the "noise" cluster and summarize it to see if emerging trends exist that aren't dense enough yet to form a formal HDBSCAN cluster.

### 3.3 Hallucinated Synthesis
- **Scenario:** The Stage 6 Insight Generator (`llama-3.3-70b-versatile`) writes a compelling root-cause hypothesis that sounds technically plausible but isn't actually supported by the raw reviews in that cluster.
- **Impact:** Product Managers might pursue a ghost problem.
- **Mitigation:** Implement the strict Citation Verifier (as defined in Architecture Section 6.2). Furthermore, force the LLM to structure its output so that every "Likely Underlying Problem" is directly tied to a specific "Representative Quote".

---

## 4. Operational & Infrastructure Edge Cases

### 4.1 Sudden Volume Spikes (The "Bad Update" Scenario)
- **Scenario:** A new Google Photos update breaks a core search feature, resulting in thousands of identical negative reviews in a single day.
- **Impact:** The ingestion pipeline pulls in a massive volume, immediately exhausting the Groq Free Tier TPM/RPM limits.
- **Mitigation:** 
  - The Ingestion Scheduler must implement a daily volume cap (e.g., max 500 reviews processed per day). 
  - The token-bucket rate limiter must gracefully queue excess reviews for processing on subsequent days.

### 4.2 API Format Changes
- **Scenario:** Reddit or Apple changes the structure of their public JSON feeds.
- **Impact:** The ingestion connectors crash with `KeyError` or parsing exceptions.
- **Mitigation:** Use defensive programming (`dict.get()`, `try/except` blocks) in the connectors. If parsing fails, log an alert and gracefully skip that connector for the current run rather than crashing the entire pipeline.
