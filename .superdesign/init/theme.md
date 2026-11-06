# Theme & Design System Tokens

## Part 1 — Compact Token Summary

### Color Tokens
- **Dark Mode (Cyber Red & Obsidian Black):**
  - `--bg-base`: `#000000`
  - `--bg-surface`: `#0a0a0d`
  - `--bg-card`: `rgba(16, 16, 22, 0.85)`
  - `--accent`: `#ef4444` (Cyber Crimson)
  - `--accent-hover`: `#f87171`
  - `--theme-rgb`: `239, 68, 68`
  - `--text-primary`: `#f4f4f5`
  - `--text-secondary`: `#a1a1aa`
  - `--text-muted`: `#71717a`

- **Light Mode (Editorial White, Pitch Black & VTU Crimson Red):**
  - `--bg-base`: `#f8fafc`
  - `--bg-surface`: `#ffffff`
  - `--bg-card`: `#ffffff`
  - `--bg-card-hover`: `#fef2f2`
  - `--accent`: `#dc2626` (VTU Crimson Red)
  - `--accent-hover`: `#b91c1c`
  - `--theme-rgb`: `220, 38, 38`
  - `--text-primary`: `#09090b` (Deep Pitch Black)
  - `--text-secondary`: `#334155`
  - `--text-muted`: `#64748b`

### Typography & Fonts
- **Primary Interface:** `Geist, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Monospace Code & Badges:** `JetBrains Mono, monospace`

### Radius & Spacing
- `--r-card`: `14px`
- `--r-inner-lg`: `10px`
- `--r-inner-sm`: `6px`
- `--r-pill`: `9999px`

---

## Part 2 — Raw Source Definitions

```css
:root, [data-theme="dark"] {
  --bg-base: #000000;
  --bg-surface: #0a0a0d;
  --bg-card: rgba(16, 16, 22, 0.85);
  --bg-card-hover: rgba(26, 26, 34, 0.95);
  --bg-input: #121217;
  --accent: #ef4444;
  --theme-rgb: 239, 68, 68;
  --text-primary: #f4f4f5;
  --text-secondary: #a1a1aa;
}

[data-theme="light"] {
  --bg-base: #f8fafc;
  --bg-surface: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #fef2f2;
  --bg-input: #ffffff;
  --accent: #dc2626;
  --theme-rgb: 220, 38, 38;
  --text-primary: #09090b;
  --text-secondary: #334155;
}
```
