# Google Photos MVP Prototype: Implementation Plan

## Phase 1: Problem Definition & Data Foundations
**Goal:** Establish the narrative and generate a dataset that supports the presentation.
* [x] Draft `problem-statement.md` analyzing the root causes of the #1 user issue ("Unexpected Photo Deletion" caused by semantic search failures).
* [x] Create `dummyData.js` generator.
* [x] Populate exactly 150 photos divided across 15 highly recognizable, real-world themes (Weddings, Receipts, Pets, Medicine, etc.).
* [x] Inject metadata for Timeline, People, and Location.

## Phase 2: MVP Scaffolding
**Goal:** Build the basic UI shell without interfering with the AI Discovery Engine.
* [x] Create `MVP.jsx` component.
* [x] Implement the dual-pane layout (Sidebar vs. Main Content).
* [x] Add Traditional Search filters (dropdowns) to the sidebar to serve as a foil to the AI search.
* [x] Build the basic AI chat interface and wire up hardcoded regex responses for the 15 themes.

## Phase 3: Routing & Isolation
**Goal:** Allow the user to present the Discovery Engine and the MVP as distinct products.
* [x] Replace `useState` toggling with native URL routing in `App.jsx`.
* [x] Assign `/` to the Discovery Engine and `/mvp` to the Prototype.
* [x] Deploy to Vercel and verify client-side routing works without 404 errors via `vercel.json` rewrites.

## Phase 4: The "Aha!" Moment (Recovery Flow)
**Goal:** Directly address the "Unexpected Photo Deletion" anxiety.
* [x] Inject hidden `syncStatus` flags into `dummyData.js` (tagging 30 photos as unsynced or trashed).
* [x] Update `MVP.jsx` search logic to intercept anxiety-driven keywords ("lost", "deleted", "missing").
* [x] Trigger an empathetic AI response ("Don't panic!").
* [x] Override traditional filters to immediately surface the missing photos.

## Phase 5: Storage Management (Auto-Cleanup)
**Goal:** Address user complaints regarding out-of-storage limitations.
* [x] Create `Cleanup.jsx` UI wizard.
* [x] Build Notification view (summarizing scheduled deletions).
* [x] Build Review view (showing duplicates and inactive photos).
* [x] Build Interactive Comparison view (Side-by-side comparison of duplicate photos with an "Undo" option).

## Phase 6: UI Polish & Feature Parity
**Goal:** Make the prototype look and feel exactly like native Google Photos.
* [x] Migrate `Cleanup.jsx` to be embedded inside the MVP sidebar for a seamless, single-page experience.
* [x] Add native Google Blue (`#174ea6`) typography for clear contrast.
* [x] Build a sticky Timeline Gallery that groups photos by Date.
* [x] Implement an interactive Date Scrubber on the right edge of the gallery.
* [x] Add Settings and Trash modules to the main navigation menu, completing the illusion of a fully featured app.
