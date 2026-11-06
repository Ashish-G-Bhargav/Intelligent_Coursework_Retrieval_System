# Shared Layout Components

This document contains the persistent shell, navigation, and workspace layout structures.

## Root Application Shell
File: `frontend/index.html`

```html
<div class="app-shell">
  <!-- Sidebar Navigation -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <div class="brand-mark">ER</div>
        <div class="brand-title">VTU Coursework AI</div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <!-- Nav items -->
    </nav>
    <div class="sidebar-footer">
      <!-- VTU Scheme Badge -->
    </div>
  </aside>

  <!-- Main View Container -->
  <div class="main">
    <header class="topbar">
      <!-- Topbar Title, Search Shortcut, Theme Toggle -->
    </header>
    <main class="page-container">
      <!-- Active Page Sections -->
    </main>
  </div>
</div>
```

## Top Navigation Bar
File: `frontend/index.html`

```css
.topbar {
  height: var(--topbar-h);
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(6, 8, 12, 0.85);
  backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 20;
}
```

## Sidebar Navigation
File: `frontend/index.html`

```css
.sidebar {
  width: var(--sidebar-w);
  background: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  z-index: 30;
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: var(--r-inner-sm);
  color: var(--text-secondary);
  background: transparent;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
  width: 100%;
  text-align: left;
}

.nav-item.active {
  color: #ffffff;
  background: linear-gradient(90deg, rgba(var(--theme-rgb), 0.2) 0%, rgba(var(--theme-rgb), 0.05) 100%);
  border-color: var(--accent-border);
}
```
