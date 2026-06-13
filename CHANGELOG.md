# Changelog

## v4.0.0 — Neon Dark Edition

### Visual
- **Dark canvas** — `(22, 20, 32)` deep navy-charcoal replaces the bright white background. Much easier on eyes.
- **Neon glow stroke system** — every free-draw stroke is rendered in two passes:
    1. Wide soft halo (extra radius, low alpha blended layer) → gives luminous glow
    2. Sharp core line (full brightness, LINE_AA) → crisp edge
- **Neon glow swatches** — active color swatch shows an animated outer glow ring
- **Neon trail** — the finger trail uses additive-style brightness so it glows vividly

### Colors — 16 Neon / Glitter palette (black removed)
Neon Green, Neon Cyan, Neon Blue, Neon Pink, Neon Purple, Neon Red, Neon Yellow, Neon Orange,
Gold, Rose Gold, Silver, Aqua, Lavender, Coral, Mint, UV White

### Smoothing — maximum upgrade (triple-exponential)
- Added **acceleration EMA** (3rd layer of exponential smoothing) — smooths changes in velocity itself
- Alpha ceiling lowered: `0.65 → 0.55` — noticeably silkier even at medium speed
- Jitter gate raised: `2.5px → 3.0px`
- Catmull-Rom buffer enlarged: `4 → 6` points — curves are rounder and more continuous
- Interpolation steps: `5 → 8` — zero visible gaps even at fast strokes
- Predictive assist: `0.35 → 0.45` velocity + `0.10` acceleration — hand motion is anticipated better

### Bug Fixes
- Black color removed (was invisible on dark canvas)
- Camera blend darkened (`0.40/0.88 → 0.30/0.92`) so canvas artwork dominates

---

## v3.0.0
- White canvas, black color fix, pinch removed, 18 colors, 8 shapes, Catmull-Rom spline

## v2.0.0
- Double-exponential smoothing, undo/redo, shape modes, opacity, particle trail

## v1.0.0
- Basic MediaPipe drawing app
