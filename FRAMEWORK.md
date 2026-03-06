# GSD-Style Development Framework

This document describes how to reuse this spec-driven, phase-based development pipeline in a **new project**. The **phase structure** (how many phases, their names and goals) is defined **per project** in `.planning/phase-00-ROADMAP.md`, which you create at bootstrap from the TECHSPEC. The same prompt — **"GSD session start — Phase NN."** — works for any phase number; the agent reads the ROADMAP and TECHSPEC to know what Phase NN means. This keeps the framework general-purpose across different products and phase layouts.

---

## 1. Files to Take to a New Project

Copy these into the new repo **before** any implementation. They form the framework; you will adapt the TECHSPEC for the new product and keep the rest as-is.

### Must-have (framework core)


| File or folder                             | Purpose                                                                                                                                                                                                                                                                                            |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**TECHSPEC.md`**                          | Single source of truth. **Adapt §1 (Problem & Context)** and any product-specific parts of §3–§4 for the new app; keep §2 (constraints), §5–§8 (process, testing, GSD integration) as the pipeline.                                                                                                |
| `**FRAMEWORK.md`**                         | This file. Contains the STATE.md template, ROADMAP template, generic phase prompt pattern, bootstrap and audit prompts, and the full "how to use this pipeline" guide. Phase scope comes from each project's ROADMAP. Keep at root for reference; optionally remove after all phases are complete. |
| `**.cursor/rules/gsd-git-workflow.mdc**`   | Branch per phase, atomic commits, test+lint gate before every commit, SUMMARY required before merge, §1.3 verification for test phases, merge with `--no-ff`.                                                                                                                                      |
| `**.cursor/rules/gsd-state-tracking.mdc**` | STATE.md as session memory; per-phase SUMMARY.md; session-start routine, spec-first requirement, and DoD self-check against TECHSPEC §8.3 before closing a phase.                                                                                                                                  |
| `**STATE.md**` (template, see below)       | Create once at project root so the agent always has a place to read/write current phase and next task.                                                                                                                                                                                             |
| `**.planning/**`                           | Empty folder (add `.gitkeep`). Phase SPECs and SUMMARYs go here.                                                                                                                                                                                                                                   |


### Optional but recommended


| File or folder                              | Purpose                                                                                                                                                                                                                      |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**.gitattributes**`                        | `* text=auto eol=lf` — avoids Windows CRLF breaking lint (TECHSPEC §2.3).                                                                                                                                                    |
| `**.planning/phase-00-ROADMAP.md**`         | Phase index — maps phase numbers to goals, scope, and key TECHSPEC sections. Generated from the TECHSPEC during bootstrap (see §2).                                                                                          |
| `**.cursor/gsd/**`                          | Subagent definitions: generic phase runner (any Phase NN), bootstrap, audit. Phase scope comes from the project's ROADMAP + TECHSPEC. Optional; use with Cursor’s subagent (MCP task) to scale. See `.cursor/gsd/README.md`. |
| `**.cursor/rules/gsd-subagent-router.mdc**` | Rule that tells the agent when to delegate to a subagent; copy if you use `.cursor/gsd/`.                                                                                                                                    |


### Do not copy (project-specific)

- `package.json`, `app/`, `src/`, `store/`, `services/`, etc. — the new project will generate these from the TECHSPEC and phase specs.
- Existing `.planning/phase-*-SPEC.md` and `phase-*-SUMMARY.md` — those are for *this* product; the new project will write its own.
- Existing `.planning/phase-00-ROADMAP.md` — the new project will generate its own from the adapted TECHSPEC.

### phase-00-ROADMAP.md template

The roadmap is the **single source of phase structure** for the project. It breaks the TECHSPEC into implementable phases; the agent uses it to resolve "Phase NN" (name, goal, TECHSPEC sections). Each project can have a different number of phases and different names — e.g. 01–05, 01–08, or 01–06. Each phase should be completable in a single chat session. Template (example rows; adapt to your product):

```markdown
# Phase Roadmap

Derived from TECHSPEC.md on <date>.

| Phase | Name                 | Goal                                                 | Key TECHSPEC sections  | Depends on |
| ----- | -------------------- | ---------------------------------------------------- | ---------------------- | ---------- |
| 01    | Foundation           | Project scaffold, deps, tooling, directory structure | §2.1, §2.2, §2.3, §3.2 | —          |
| 02    | Data Model + Store   | Types, Zustand store, seed data with faker           | §4.1, §4.2, §3.3       | 01         |
| 03    | Services + Mocking   | API services, useApiCall, MSW handlers, dev mocks    | §3.3, §4.3, §6.4       | 02         |
| 04    | Orchestration + UI   | Qualification pipeline, screens, navigation, routes  | §1.2, §3.4, §3.3       | 03         |
| 05    | Manual Analysis      | Form screen, Zod validation, manual lead creation    | §3.4, §3.5             | 04         |
| 06    | Tests & Verification | Full test suite, coverage gate, README, DoD check    | §1.3, §6.1, §6.2, §8.3 | 01–05      |

## Phase sizing guidance

- Each phase targets **one chat session** worth of work.
- If a phase feels too large (>8 atomic commits), split it.
- If two phases are very small (<2 commits each), consider merging them.
- New features after initial build continue from Phase 07+ (see FRAMEWORK.md §6).
```

Adapt the table rows to match your product: add or remove phases, change names and goals. The column "Key TECHSPEC sections" ties each phase back to the spec so the agent knows which sections to reference. The framework does not assume a fixed set of phases — only that the ROADMAP exists and the agent reads it for "GSD session start — Phase NN."

### STATE.md template (create in new project root)

Use the **first phase name and goal from your ROADMAP** (not necessarily "Foundation"). Example:

```markdown
# Project State

## Current Phase

Phase 01 — <First phase name from ROADMAP> (in progress)

## Last Task Completed

None. Starting fresh.

## Next Task

<First phase goal from ROADMAP; e.g. Create branch feature/phase-01-<slug>. Install deps per TECHSPEC §2.2, set up tooling, scaffold per §3.2.>

## Key Decisions

- (Fill as decisions are made.)

## Blockers

None.
```

---

## 2. One-Time Bootstrap (New Project)

Before the first phase, the repo should have:

1. **TECHSPEC.md** — Adapted for the new product (at least §1 rewritten; §2–§8 can stay if stack is the same).
2. **FRAMEWORK.md** — This file, copied as-is.
3. `**.cursor/rules/`** — Both GSD rule files in place.
4. `**.gitattributes**` — `* text=auto eol=lf` for lint-safe line endings from day one.

Then run the bootstrap prompt below — the agent will create STATE.md, `.planning/`, and **phase-00-ROADMAP.md** by breaking the TECHSPEC into phases. The number and names of phases are determined by the TECHSPEC and the agent (e.g. 01–06, 01–05, 01–08).

- After the bootstrap commit lands on `main`, open a **new chat** and send **"GSD session start — Phase 01."** (or the first phase number in your ROADMAP). The agent will read the ROADMAP and TECHSPEC to know what Phase 01 is for this project.

**Bootstrap prompt:**

```
Read @TECHSPEC.md and @FRAMEWORK.md. This repo will use the GSD-style pipeline.

1. Create STATE.md at the root using the template in FRAMEWORK.md §1. Set current phase to "Phase 01 — <first phase name>" and next task to the first phase goal. Use the phase name and goal from the roadmap you are about to create in step 3 (or a placeholder "Phase 01 — (see ROADMAP)" and "First phase goal from .planning/phase-00-ROADMAP.md").
2. Create .planning/ with .gitkeep.
3. Create .planning/phase-00-ROADMAP.md using the template in FRAMEWORK.md §1 — read the TECHSPEC and break it into implementable phases (as many as needed: 01–06, 01–05, 01–08, etc.). Each phase should be completable in one chat session. Map each phase to the relevant TECHSPEC sections. This ROADMAP defines what "Phase NN" means for this project.
4. If you used placeholders in STATE.md, update them now from the ROADMAP. Commit everything to main. Do not write any app code yet.
```

This gives you a project-specific ROADMAP. From then on, **"GSD session start — Phase NN"** is resolved by reading the ROADMAP and TECHSPEC — no fixed phase list in the framework.

---

## 3. Phase-by-Phase Prompts (generic)

Use **one chat per phase** when possible. At the start of each new phase, **open a new chat** and send the same prompt pattern; the agent resolves what to do from **this project's ROADMAP and TECHSPEC**.

**Prompt (any phase):**

```
GSD session start — Phase NN.
```

(Replace NN with the phase number: 01, 02, 03, … Use the phase numbers defined in your `.planning/phase-00-ROADMAP.md`.)

**What the agent does (generic):**

1. Read **STATE.md** and **.planning/phase-00-ROADMAP.md**. Find the row for Phase NN to get the phase **Name**, **Goal**, and **Key TECHSPEC sections**.
2. Print the **pre-flight checklist** (branch `feature/phase-NN-<slug>`, spec `.planning/phase-NN-SPEC.md`, gate `npm test && npx biome check .`, no work on main). Use the slug from the ROADMAP or a short kebab-case name. **Wait for your "Confirm" or "Go"** before writing code.
3. After confirmation: create and commit `.planning/phase-NN-SPEC.md`, create the branch, implement everything required for Phase NN per the ROADMAP and the listed TECHSPEC sections. One commit per discrete task; run the gate before every commit.
4. When done: write `.planning/phase-NN-SUMMARY.md`, update STATE.md to "Phase NN complete", merge to `main` with `--no-ff`.

The framework does not assume Phase 01 = "Foundation" or Phase 06 = "Tests". Your ROADMAP defines the phases; the agent follows it. For a **test-heavy or audit-heavy final phase**, optionally attach `@TECHSPEC.md` and `@.planning/TECHSPEC-AUDIT.md` (if present) so the agent has full DoD and test-case context.

---

### Example: one possible phase structure (e.g. Addi-style project)

The table in §1 (ROADMAP template) shows one possible layout: 01 Foundation, 02 Data Model + Store, 03 Services + Mocking, 04 Orchestration + UI, 05 Manual Analysis, 06 Tests & Verification. If your project uses a similar ROADMAP, Phase 01 will be foundation-style work, Phase 03 services+MSW, etc. If your project has different phases (e.g. 01 Setup, 02 API, 03 Screens, 04 Tests), the same prompt "GSD session start — Phase 02" runs whatever Phase 02 is in your ROADMAP. No change to the framework is required.

---

## 4. When to Start a New Chat

- **Between phases:** Start a new chat for each new phase. STATE.md and the phase SUMMARYs carry context; the prompt is just "GSD session start — Phase NN."
- **Within a phase:** Stay in the same chat until the phase is merged. If the chat gets too long or context is lost, start a new chat and say: "Read STATE.md and resume. We are in the middle of Phase NN; last completed was . Continue from here."

---

## 5. Optional: Audit / Verification

To check that the project matches the TECHSPEC and all phases are truly complete:

**Prompt:**

```
Read @TECHSPEC.md and compare the project to it. Check: (1) All §1.3 test cases are covered by a test file — produce a mapping table. (2) §8.3 Definition of Done — for each bullet, state met or not and evidence. (3) All phases (from the project's ROADMAP): STATE.md phase status vs actual code and .planning/ SUMMARYs. (4) README per §1.5 and §8.3. (5) Coverage: run npm test -- --coverage and report vs §6.2 (80% min). Write the result to .planning/TECHSPEC-AUDIT.md.
```

---

## 6. Adding Features After Initial Phases Are Complete

The **initial phases** (as defined in your ROADMAP — e.g. 01–06, 01–05, or 01–08) build the project from zero. Once they're merged and the project is live, new work still follows the same GSD pipeline — the only difference is that you're extending rather than bootstrapping.

### 6.1 New feature = new phase

Continue the phase numbering from where you left off. If the last initial phase in your ROADMAP was 06, the next feature is Phase 07; if it was 05, the next is 06. Optionally add a row for the new phase to the ROADMAP or keep ROADMAP as "initial build" and use STATE.md for the new phase number.

**Step-by-step:**

1. **Update the TECHSPEC first.** Before any code, open a chat and ask the agent to add the new feature to the relevant TECHSPEC sections (§1.3 for test cases, §3.4 for screens/navigation, §4 for new data/APIs, etc.). Commit the TECHSPEC update to `main`. This keeps the spec as the single source of truth — the same spec-first principle from the initial build.
2. **Update STATE.md.** Set current phase to the new phase number and describe the next task.
3. **Start a new chat with the standard prompt:**

```
GSD session start — Phase 07.
```

The agent will read STATE.md, print the pre-flight checklist, create a branch (`feature/phase-07-<slug>`), write `.planning/phase-07-SPEC.md`, and proceed as usual. Same rules apply: spec committed before code, atomic commits, gate before every commit, SUMMARY before merge.

1. **Merge and audit.** After the phase is complete and merged, optionally run the audit prompt from §5 to verify the project still fully complies with the updated TECHSPEC.

### 6.2 Small changes vs. multi-phase features


| Size                                                       | Approach                                                                                                                                                    |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Small** (1–3 tasks, e.g. add a filter, tweak validation) | One phase. Single branch, a few commits, merge.                                                                                                             |
| **Medium** (new screen + API + tests)                      | One phase, but write a detailed phase-SPEC so nothing is missed.                                                                                            |
| **Large** (new module, multiple screens, new data model)   | Split into multiple phases (e.g. Phase 07 = data + services, Phase 08 = UI + orchestration, Phase 09 = tests). Each gets its own branch, spec, and summary. |


### 6.3 Bug fixes

Bug fixes follow a lighter version of the same workflow:

**Prompt:**

```
GSD session start — Phase NN (bugfix: <short description>).
```

The phase SPEC should describe the bug (observed vs expected behavior), the root cause if known, and the fix approach. Tests that reproduce the bug must be included before the fix is applied (red → green). Same gate, same SUMMARY, same merge.

For critical hotfixes that can't wait for a full phase cycle, use branch naming `hotfix/phase-NN-<slug>` instead of `feature/`, but still commit the SPEC first and write a SUMMARY before merging.

### 6.4 Evolving the TECHSPEC over time

As the project grows, the TECHSPEC should grow with it. Treat it as a living document:

- **New conventions discovered?** Add them to §3.3 (Key Boundaries & Conventions).
- **New test patterns?** Add to §6.1 or §6.4.
- **New constraints or dependencies?** Update §2.
- **Lessons learned from a painful phase?** Add to the changelog at the bottom and refine the relevant section so the next phase avoids the same issue.

Always commit TECHSPEC updates to `main` before starting the phase that relies on them. The agent should never be implementing against a spec that hasn't been committed.

### 6.5 Example: adding a "Lead Export" feature (Phase 07)

**Chat 1 — TECHSPEC update:**

```
Read @TECHSPEC.md. I need to add a "Lead Export" feature: the user can select multiple leads from the pipeline list and export them as a CSV file. Add the relevant test cases to §1.3, a new screen entry to §3.4, and any new API contracts to §4.3. Commit the updated TECHSPEC to main.
```

**Chat 2 — Implementation:**

```
GSD session start — Phase 07.
```

The agent picks up the updated TECHSPEC, reads STATE.md, creates the branch, writes the spec, and builds it out.

---

## 7. Summary: Checklist for a New Project

1. Copy **TECHSPEC.md** (adapt §1 and product-specific bits), **FRAMEWORK.md**, **.cursor/rules/** (both mdc files), **STATE.md** (template), **.planning/** (with .gitkeep), and optionally **.gitattributes** and **.planning/phase-00-ROADMAP.md**.
2. Commit them to `main` (no app code yet).
3. Run **bootstrap** (§2) so the agent creates STATE.md and **.planning/phase-00-ROADMAP.md** from the TECHSPEC. Your phase structure (number and names of phases) is defined there.
4. For **each phase in your ROADMAP** (e.g. 01, 02, … through your last initial phase), open a **new chat** and send: `**GSD session start — Phase NN.`** The agent reads the ROADMAP and TECHSPEC to know what Phase NN is. For the final phase (often tests/verification), optionally attach @TECHSPEC.md and @STATE.md and the audit file if you have one.
5. Confirm when the agent shows the pre-flight checklist; then let it implement, commit per task, and merge when DoD is met.
6. Optionally run the audit prompt (§5) after the last initial phase and fix any gaps before calling the project done.
7. For new features after the initial build, follow §6 — same pipeline, continue phase numbering from your last ROADMAP phase.

### 7.1 Scaling with Cursor subagents (optional)

If you use **Cursor** and copy `**.cursor/gsd/`** and `**gsd-subagent-router.mdc**`: the router delegates "GSD session start — Phase NN", "Run bootstrap", or "Run audit" to a subagent. Phase scope is **generic** — the subagent reads **this project's** `.planning/phase-00-ROADMAP.md` and TECHSPEC to know what Phase NN means, so the same setup works for any phase structure (e.g. 01–06, 01–05, 01–10). See **.cursor/gsd/README.md**.

---

## 8. Writing TECHSPEC §3.7 — UI/UX Design Guidelines

§3.7 is where you define the visual experience. It has two parts: a **style reference** (1–3 sentences you write) and a set of **general principles** (copy as-is). The agent reads both and derives the full visual implementation.

### 8.1 Style reference (you fill this in)

Write 1–3 sentences describing the look and feel you want. The agent uses this to pick colors, typography, spacing, shadows, and component styling. Be descriptive enough that someone who hasn't seen the app could visualize it.

**Template:**

```markdown
#### Style reference

> <describe the visual experience in 1–3 sentences — mood, color direction, shape language, reference apps or brands if helpful>
```

**Examples:**

- *"Clean, professional CRM feel — light backgrounds, soft card shadows, rounded corners, blue primary actions, green/red/amber for success/error/warning. Addi Sales Pipeline style."*
- *"Dark-mode fintech dashboard — near-black backgrounds, high-contrast text, neon-green accents, minimal shadows, sharp corners."*
- *"Playful consumer app — warm pastels, large rounded elements, friendly illustrations, bouncy press animations."*

### 8.2 General principles (copy into every TECHSPEC §3.7)

These principles tell the agent *how* to structure the visual layer regardless of style. Copy them as-is under the style reference.

---

**1. Centralized design tokens**

All colors, spacing values, radii, shadows, and typography sizes must live in a **single file** (e.g. `src/theme.ts` or a `COLORS` / `SPACING` object in `src/constants.ts`). Screens import from this file — never hardcode hex values or pixel sizes inline. This makes the visual language easy to audit and change globally.

Required token categories (names and values derived from the style reference):


| Category                        | Purpose                                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Background                      | Screen-level fill                                                                                                  |
| Card / Surface                  | Elevated containers (list items, forms, detail cards)                                                              |
| Primary                         | Main CTA color, links, active/focus states                                                                         |
| Success / Error / Warning       | Outcome indicators — each needs a **strong** variant (icon/text) and a **muted** variant (background fill, border) |
| Text primary / secondary        | Heading vs metadata contrast                                                                                       |
| Border                          | Dividers, input borders, separators                                                                                |
| Disabled                        | Inactive buttons, placeholder text                                                                                 |
| Status-specific (if applicable) | e.g. stage badges, category pills — distinct bg+text pair per status                                               |


**2. Spacing and layout system**

Define a small set of spacing values (e.g. 4, 8, 12, 16, 24, 40) and use them consistently:

- Screen horizontal padding.
- Card internal padding.
- Vertical gap between sections and between list items.
- Bottom padding on scrollable lists for thumb comfort.

Avoid arbitrary pixel values; pick from the spacing scale.

**3. Component patterns**

Every project reuses a common set of UI building blocks. The agent should implement these as reusable patterns (or extract as components when used in multiple screens):


| Pattern                        | What it solves                             | Key requirements                                                                                                                                                                                         |
| ------------------------------ | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **List card**                  | Tappable item in a list                    | Title + metadata on one side; status indicator + navigation affordance (e.g. chevron) on the other. Must have **press feedback** (opacity change, scale, or highlight).                                  |
| **Stats / summary row**        | At-a-glance metrics at top of a list       | Compact card with key numbers; distinct color per metric category.                                                                                                                                       |
| **Section header**             | Grouping within a list                     | Label (often uppercase, smaller, secondary color) + optional count badge.                                                                                                                                |
| **Detail row**                 | Key-value info on a profile/detail screen  | Icon + text value, aligned; secondary color.                                                                                                                                                             |
| **Status badge / pill**        | Category or state indicator                | Small pill with distinct bg+text color per status. Must be readable at small sizes.                                                                                                                      |
| **Primary action button**      | Main CTA                                   | Filled with primary color; icon + label. Disabled state uses muted color and prevents interaction.                                                                                                       |
| **Secondary / outline button** | Lower-emphasis action (e.g. reset, cancel) | Border in primary, transparent or card-colored fill. Same sizing as primary for visual consistency.                                                                                                      |
| **Progress step**              | Multi-step process visibility              | Row per step: status icon (spinner / checkmark / error / idle) + label + optional detail. Each step's background tints based on outcome (success muted, error muted). Steps separated by a thin divider. |
| **Result banner**              | Final outcome of a process                 | Full-width block with icon + title (bold) + subtitle. Background color matches the outcome (success / error / warning muted). Error banners must include a **retry CTA**.                                |
| **Form field**                 | User input                                 | Label above input; border changes on **focus** (primary) and **error** (error color); inline error message below field.                                                                                  |
| **Completed / locked state**   | Item that can't be actioned again          | Replace CTA with a short confirmation message (e.g. "Already completed") in a success-tinted container. No actionable button.                                                                            |


**4. Interaction and feedback**

- **Press states**: Use `Pressable` with visual feedback on `pressed` (opacity reduction, slight scale, or color shift). Never use a `TouchableOpacity` without visible feedback.
- **Loading states**: Show `ActivityIndicator` (or equivalent) in primary color for in-progress actions. Keep the button label visible (e.g. "Processing...") alongside the spinner so the user knows what's happening.
- **Keyboard handling**: Wrap form screens in `KeyboardAvoidingView` (behavior `padding` on iOS, `height` on Android). Use `keyboardShouldPersistTaps="handled"` on scroll containers so the user can tap submit without dismissing the keyboard first.
- **Error recovery**: Per §3.3, every error state must include an **actionable retry CTA** that calls `refetch` or re-invokes the mutation. Passive "try again later" without a button is not acceptable.
- **Transitions**: State changes (e.g. list item moving from one section to another) should feel smooth. Avoid janky re-renders; if a list re-sorts, the change should be visually obvious but not jarring.

**5. Icons**

- Use a **single icon library** consistently across all screens (e.g. `@expo/vector-icons` Ionicons, or Material Icons, or Lucide). Do not mix icon sets.
- Choose icons that are semantically clear: navigation chevrons, add/create, field-type indicators (ID card, calendar, email, phone), success check, error cross, warning alert, action triggers (e.g. analytics, refresh).
- The same icon set across all screens (list, detail, form) keeps the experience cohesive.

**6. Accessibility**

- Minimum touch target **44pt**.
- Screen reader labels on all interactive elements (list items, buttons, form fields).
- Ensure sufficient contrast ratio between text and background for all token pairings (WCAG AA minimum).
- Status should never be communicated by color alone — pair color with an icon or text label.

---

### 8.3 Example: how a filled-in §3.7 looks

See the current `TECHSPEC.md` §3.7 for a complete example of what a filled-in section looks like for the Addi Sales Pipeline app. It includes the style reference, the derived token palette, icon mapping, and component-specific notes.

---

## 9. Reference: TECHSPEC Section Map


| Section | Content                                                                                                                                                                                                                                                                         |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §1      | Problem, goals, success criteria, test cases, out of scope                                                                                                                                                                                                                      |
| §2      | Tech stack, constraints (exact deps, .gitattributes, peer deps), preferences                                                                                                                                                                                                    |
| §3      | Architecture, project structure (`src/`), conventions (routes, types, readonly props, retry CTA, URL paths, random mocks), **§3.7 UI/UX design guidelines** (filled-in per project — style reference + derived tokens; template and general principles live in FRAMEWORK.md §8) |
| §4      | Data model, storage, APIs (MSW scope, in-process dev mock), contracts                                                                                                                                                                                                           |
| §5      | Non-functionals (performance, security, a11y, observability)                                                                                                                                                                                                                    |
| §6      | Test pyramid, coverage gates, verification, **§6.4 Jest+Expo setup**                                                                                                                                                                                                            |
| §7      | Deployment, env, build                                                                                                                                                                                                                                                          |
| §8      | Phase↔TECHSPEC mapping, **plan constraints** (spec-first, pre-flight, MSW test-only), **Definition of Done** (lint per commit, §1.3 table, SUMMARY required)                                                                                                                    |


Keeping this map in mind helps when adapting TECHSPEC for a different product: change §1 and any domain sections; keep §2, §5–§8 and the structural parts of §3–§4 to preserve the pipeline.