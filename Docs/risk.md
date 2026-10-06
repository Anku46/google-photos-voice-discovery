# Google Photos Discovery Engine: Risks & Rollout Strategy

This document outlines the potential failure modes of the AI Discovery Engine and our strategy for containing them, ensuring we meet the targets defined in `Success-Metrics.md`.

## ⚠️ Failure Modes & Mitigations

### 1. Hallucinated/Wrong Matches
* **Risk:** The AI suggests contextual refinement chips that don't actually exist in the user's personal library, leading them into a frustrating dead end (and violating our "Wrong-Confidence Results" guardrail).
* **Mitigation:** AI chip generation must be strictly bounded by the actual metadata present in the user's specific result set. We must avoid relying on global LLM assumptions and only suggest terms anchored to the user's real photos.

### 2. Privacy Discomfort
* **Risk:** Users feel unsettled or surveilled that the AI is "reading" the emotional or contextual subtext of their private, intimate photos.
* **Mitigation:** Keep the UI language mechanical, objective, and predictable rather than overly human or assuming (e.g., Use *"Narrow by setting"* rather than *"It looks like you were happy here"*).

### 3. Added Effort in a Slow Flow
* **Risk:** Forcing users to read and tap through multiple menus slows down a previously instant (even if failing) flow, potentially increasing the *Time to Retrieval*.
* **Mitigation:** Context chips are strictly additive and sit below the main search bar. Users who prefer to re-type or immediately scroll can completely ignore them.

### 4. Low Discoverability
* **Risk:** Users don't notice the refinement chips because they are conditioned to immediately start scrolling (The Scroll Fallback).
* **Mitigation:** Add a subtle pulsing animation to the refinement chips *only* after a user dwells on the zero-state or search results for >3 seconds, gently drawing their attention to the new tool.

---

## 🚀 Rollout Phases

To safely monitor our Leading Metrics and Guardrails, we will deploy the Discovery Engine progressively:

* **Phase 1 (Month 1):** `5% Rollout` — Targeted exclusively at English-locale, high-frequency searchers.
* **Phase 2 (Month 2):** `25% Rollout` — Primary focus on tuning chip generation latency to ensure it remains under the +200ms guardrail.
* **Phase 3 (Month 3):** `100% General Availability (GA)`

---

## 🏆 What Winning Looks Like at 3 Months
If our mitigations are successful and the rollout proceeds as planned, winning at the 3-month mark will be defined by:
1. A **20% reduction in search abandonment rates**.
2. A measurable shift in user behavior where **tapping a context chip replaces manual scrolling** as the default fallback behavior when an initial search fails.
