# Extractable Components Catalog

Reusable Superdesign `DraftComponent` candidates from the EduRAG application.

## Layout Components
### SidebarNavigation
- Source: `frontend/index.html` (selector: `.sidebar`)
- Category: layout
- Description: Fixed-width left navigation bar with brand badge, page items, and VTU scheme status.
- Extractable props: `activePage` (string), `isCollapsed` (boolean)
- Hardcoded: Navigation item icons, labels, brand initials "ER"

### TopBarHeader
- Source: `frontend/index.html` (selector: `.topbar`)
- Category: layout
- Description: Sticky header with command palette trigger and dark/light dual theme toggle.
- Extractable props: `currentTheme` ("dark" | "light")
- Hardcoded: Brand title, keyboard shortcut badge

## Basic Components
### OmniSearchBar
- Source: `frontend/index.html` (selector: `.omni-search-container`)
- Category: basic
- Description: Centered search bar with animated gradient focus halo, search icon, and Ask AI CTA button.
- Extractable props: `query` (string), `placeholder` (string)
- Hardcoded: SVG icon, Enter key badge

### StatTileCard
- Source: `frontend/index.html` (selector: `.stat-tile`)
- Category: basic
- Description: Interactive 3D tilt telemetry card with icon wrapper, animated counter digit, and label.
- Extractable props: `value` (number | string), `label` (string), `icon` (svg)
- Hardcoded: Tilt perspective styling

### PromptRevisionChip
- Source: `frontend/index.html` (selector: `.prompt-tag-btn`)
- Category: basic
- Description: Interactive quick exam question prompt chip with micro-elevation and crimson hover wash.
- Extractable props: `queryText` (string)
- Hardcoded: Pill shape, transition curves

### UploadDropzone
- Source: `frontend/index.html` (selector: `.upload-dropzone`)
- Category: basic
- Description: Drag-and-drop PDF ingestion container with file picker and active drag states.
- Extractable props: `acceptedFormats` (string)
- Hardcoded: Cloud upload SVG, instructional typography
