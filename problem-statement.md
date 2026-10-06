# Google Photos Retrieval MVP: Problem Statement

## 1. Target User Segment
Users who have accumulated a massive library of photos (thousands of images over years) and rely on Google Photos as their primary "memory vault." Specifically, users trying to retrieve specific, older memories where they remember the *context* of the photo but not the *exact structural metadata* (date, location, or explicit object names).

## 2. The Retrieval Scenario
The user is trying to find a specific photo from the past. They know the photo exists, but they can only recall contextual or semantic clues. 
**Example Query:** *"The medicine I took when I was sick last winter"* or *"That small café we went to during our Goa trip."*
Instead of searching for exact objects (e.g., "Paracetamol"), they search using episodic memory (events, feelings, relative timeframes).

## 3. The Product Outcome
**Objective:** Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe.
**Key Metric:** Decrease the search abandonment rate (when a user types a query, gets 0 results or irrelevant results, and immediately exits the app or starts manually scrolling).

## 4. Root Cause of Retrieval Failure
Based on our Discovery Engine analysis (which analyzed public app store reviews and complaints):
The existing retrieval experience breaks down at the **system understanding stage**. Google Photos search is highly optimized for *Entity Recognition* (Faces, Dogs, Cars, Places) and *Structural Metadata* (Dates, GPS coordinates). It fails at *Semantic Context Recognition*. When a user types "when I was sick", the system looks for a visual representation of "sick" rather than understanding that a "thermometer" or "medicine bottle" implies sickness. 

Furthermore, when a query is vague, the system returns an overwhelming grid of loosely related images rather than initiating a dialogue to narrow down the search (e.g., "Do you remember what color the bottle was?").

## 5. Existing User Workarounds
When search fails, our data shows users resort to high-friction workarounds:
1. **The Endless Scroll:** Manually scrolling through the timeline to a vaguely remembered year/month (causing immense frustration).
2. **Cross-App Triangulation:** Opening WhatsApp or Calendar to find the exact date of a trip/event, then returning to Google Photos to jump to that date.
3. **The "Deletion" Assumption:** The user assumes the photo was lost or deleted by a bug (our #1 ranked issue in the Discovery Engine is "Unexpected Photo Deletion," which is often a false positive caused by severe retrieval failure).

## 6. Why solving this creates meaningful user value
Memory is inherently contextual, not structural. By aligning the retrieval engine with how human memory actually works (episodic and semantic), we remove the cognitive load of forcing users to translate their memories into rigid search terms. This transforms a frustrating, friction-heavy task into a delightful, "magical" experience.

## 7. Why solving this makes business sense for Google Photos
If users cannot retrieve their memories, the core value proposition of Google Photos ("a home for your memories") degrades. Frequent retrieval failures lead to users treating the app as cold storage rather than an active, engaging gallery. Improving this specific bottleneck increases user retention, builds extreme product loyalty, and mitigates the massive volume of negative App Store reviews mistakenly claiming that "Google Photos deleted my old photos."
