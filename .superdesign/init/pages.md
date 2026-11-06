# Page Component Dependency Trees

## 1. Dashboard (`#page-dashboard`)
Entry: `frontend/index.html` (view: `page-dashboard`)
Dependencies:
- `.editorial-hero`
  - `.hero-tagline` (`.hero-red-dot`, `.zero-hallucination-pill`)
  - `.hero-heading` (`#heroHeadlineText`, `.headline-word-accent`)
  - `.hero-text`
  - `.omni-search-container` (`.omni-search-inner`, `.omni-search-input`, `.omni-search-btn`)
  - Quick Revision Chips (`.prompt-tag-btn`)
- `.stats-strip`
  - `.stat-tile` (`#statSubjects`, `#statIndexed`, `#statFiles`)
- `.tagline-section`
  - `#taglineWordsContainer` (`.reveal-word`)
- Core Study Workflows Grid
  - `.card.tilt-card`

## 2. Study Workspace (`#page-workspace`)
Entry: `frontend/index.html` (view: `page-workspace`)
Dependencies:
- `.workspace-bar`
  - `#wsSubjectSelect`, `#wsDocSelect`
  - `.ratio-switch-group` (`#ratioBtnSplit`, `#ratioBtnPdf`, `#ratioBtnChat`)
  - `#wsPageInput`
- `.workspace-panes-row`
  - `.ws-chat-column` (`.chat-header`, `.chat-stream`, `.chat-composer-box`)
  - `.ws-pdf-column` (`.pdf-header-bar`, `#wsPdfIframe`)

## 3. Upload Center (`#page-upload`)
Entry: `frontend/index.html` (view: `page-upload`)
Dependencies:
- Ingest Document Card
  - `.upload-dropzone` (`#pdfFileInput`)
  - Metadata Inputs (`#inputUploadScheme`, `#inputUploadSubjectCode`, `#inputUploadSem`, `#inputUploadType`)
  - `#btnSubmitUpload`
- Document Vault List Card
  - `#vaultSearchInput`, `#vaultTypeFilter`
  - `#vaultDocumentsList`
