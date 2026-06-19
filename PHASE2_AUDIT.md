# Architecture Audit - Intelligence Workbench Redesign

## 1. Current Architecture
- **Framework:** FastAPI with Jinja2 templates.
- **Styling:** Modular CSS (`tokens`, `layout`, `components`, `pages`).
- **Layout:** Floating top navigation with a centered single-column workspace.
- **Theme:** Supports Light/Dark/System modes using CSS variables and `data-theme` attribute.

## 2. Current Problems
- **Visual Depth:** The UI feels "flat." It lacks the lighting and layering effects found in premium apps like Linear or Vercel.
- **Visual Weight:** Light mode is dominant in screenshots, but the requested "Intelligence Workbench" vibe usually favors a high-contrast Dark mode with subtle glows.
- **In-line Styles:** Significant use of in-line `style` attributes in `dashboard.html`, which breaks the design system's maintainability.
- **Component Limitations:** Metric cards and panels are basic and don't provide enough information at a glance.

## 3. UI Weaknesses
- **Intelligence Funnel:** The visualization is text-heavy and uses basic arrows. It doesn't feel like a high-end "Intelligence" tool.
- **Empty States:** The dashboard metrics showing "0" lack a "ready for data" premium feel.
- **Active States:** Nav active states are a bit pale and don't stand out enough in light mode.

## 4. CSS Duplication
- Layout grid logic is repeated in in-line styles.
- `badge` and `system-pill` classes have overlapping properties.

## 5. Layout Problems
- Topbar and main content are separated by large gaps that break the visual flow.
- The floating nav's dropdown behavior is brittle (hover-based).

## 6. Navigation Problems
- Dropshadows on the nav pill are a bit heavy/standard.
- Dropdown content alignment is fixed to center, which might overflow on smaller screens.

## 7. Typography Problems
- Eyebrow text is uppercase and tracked out, which is good, but headings are a bit too "standard" in their weighting.
- Lack of a consistent typography scale.

## 8. Design System Inconsistencies
- Border colors and radii vary slightly between components.
- Saffron accent is underutilized (mostly limited to logo and one active state).

---

# Redesign Plan

## Phase 1: Tokens & Design System
- Update `tokens.css` with Clerk-inspired colors: Near-black (`#050505`), pure black (`#000000`).
- Implement a 90% Neutral / 10% Saffron accent split.
- Add lighting/glow tokens (radial gradients).
- Refine radii (standardize on `12px` for cards, `999px` for pills).

## Phase 2: Navigation (Clerk Style)
- Refine `nav.html` and `layout.css`.
- Ensure the floating nav has a "glass" appearance (blur + subtle border + transparency).
- Improve hover/active states for a premium feel.
- Add smooth transitions.

## Phase 3: Dashboard & Components
- Redesign `dashboard.html` to focus on "What happened? What changed?".
- Overhaul `card.html` macros for premium metric and panel cards.
- Redesign the "Intelligence Funnel" into a high-visibility workbench section.
- Move in-line styles to `components.css` or `pages.css`.

## Phase 4: Theme & Polish
- Ensure Dark/Light/System theme persistence works perfectly.
- Add subtle motion (transitions only, no decorative animation).
- Final cleanup of unused CSS and redundant code.

## Phase 5: Validation
- Verify all routes (`/candidates`, `/evidence`, `/runs`, etc.).
- Ensure no Jinja errors.
- Verify responsiveness.
