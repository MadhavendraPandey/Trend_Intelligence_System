# Design Extraction - Premium Workbench Patterns

## Navigation (Clerk inspired)
- **Position:** Floating centered top bar.
- **Visuals:**
  - Height: `44px` to `56px`.
  - Border: `1px solid var(--border)`.
  - Background: `var(--surface)` with `backdrop-filter: blur(20px)`.
  - Radius: `999px`.
  - Padding: `0 16px`.

## Typography (Linear/Vercel inspired)
- **Font:** Inter (already present).
- **Headings:** Bold, tight letter-spacing (`-0.03em`).
- **Eyebrows:** All-caps, tracked out (`0.05em`), smaller font size (`11px`).
- **Body:** Clean, legible, high line-height (`1.6`).

## Surfaces (Linear inspired)
- **Cards:**
  - Background: `#09090b`.
  - Border: `1px solid rgba(255,255,255,0.1)`.
  - Border Hover: `1px solid rgba(255,255,255,0.2)`.
  - Shadow: None or very subtle depth.

## Lighting (Vercel inspired)
- **Background Glow:** Subtle radial gradient starting from the top center:
  `radial-gradient(circle at 50% -20%, rgba(245, 158, 11, 0.1), transparent 50rem)`

## Color Strategy
- **Neutral (90%):** Grays and blacks (`#000000`, `#09090b`, `#a1a1aa`).
- **Accent (10%):** Saffron (`#f59e0b`). Used for active nav, primary buttons, and critical status indicators.
