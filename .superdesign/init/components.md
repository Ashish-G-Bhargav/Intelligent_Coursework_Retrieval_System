# Shared UI Primitives

This document contains the core UI primitives and component implementations for EduRAG.

## Button Primitives
File: `frontend/index.html`

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-main);
  font-weight: 600;
  border-radius: var(--r-inner-sm);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  text-decoration: none;
  border: 1px solid transparent;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent) 0%, rgba(var(--theme-rgb), 0.75) 100%);
  color: #ffffff;
  border: 1px solid rgba(var(--theme-rgb), 0.5);
  box-shadow: 0 4px 16px -2px rgba(var(--theme-rgb), 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 22px rgba(var(--theme-rgb), 0.55);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  border: 1px solid var(--border-default);
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(var(--theme-rgb), 0.35);
  color: #fff;
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 6px;
}
```

## Form Inputs & Selects
File: `frontend/index.html`

```css
.form-input, .input-text, .input-select {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: var(--r-inner-sm);
  color: var(--text-primary);
  font-family: var(--font-main);
  font-size: 13px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.form-input:focus, .input-text:focus, .input-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}
```

## Badges, Pills & Chips
File: `frontend/index.html`

```css
.code-pill {
  display: inline-flex;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 7px;
  border-radius: 5px;
  background: rgba(var(--theme-rgb), 0.1);
  color: var(--accent);
  border: 1px solid rgba(var(--theme-rgb), 0.25);
  letter-spacing: 0.3px;
}

.prompt-tag-btn {
  padding: 5px 11px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-default);
  border-radius: 7px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.prompt-tag-btn:hover {
  background: rgba(var(--theme-rgb), 0.1);
  border-color: rgba(var(--theme-rgb), 0.35);
  color: #ffffff;
  transform: translateY(-2px);
}
```

## Cards & 3D Tilt Wrapper
File: `frontend/index.html`

```css
.card {
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-default);
  border-radius: var(--r-card);
  position: relative;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.card:hover {
  border-color: var(--accent-border);
  box-shadow: 0 12px 36px -6px rgba(0, 0, 0, 0.7), 0 0 24px var(--accent-glow);
}
```
