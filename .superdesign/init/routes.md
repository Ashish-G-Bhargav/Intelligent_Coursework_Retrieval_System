# Page & Route Structure

EduRAG is structured as a high-performance single-page application with immediate client-side navigation.

## Routes Mapping

| Route ID | Label | View Description |
| :--- | :--- | :--- |
| `page-dashboard` | Dashboard | Hero section with interactive OmniSearch, Quick Revision chips, Telemetry Counters, and Tagline Reveal banner. |
| `page-workspace` | Study Workspace | Dual-pane comparative study interface with synchronized PDF slide viewer and grounded AI chat. |
| `page-assistant` | Ask AI Assistant | Dedicated conversational chatbot grounded in VTU syllabus with direct citations. |
| `page-subjects` | Course Catalog | Subject readiness cards for Semesters 3-6 (CSE, ISE, ECE) with cache and indexing telemetry. |
| `page-scrape` | Scrape & Index | Live crawler control center powered by Scrapling engine with real-time log terminal. |
| `page-upload` | Upload Materials | Document Ingestion Vault accepting official PDFs, question papers, and scheme syllabi into SQLite database. |
| `page-notes` | Notes Library | Searchable lecture notes archive with in-app PDF modal preview. |
