# SBFO R&O Tracker

A risk and opportunity tracking system for Suntory's Sales Based Forecast Optimization (SBFO) process. Teams can log, manage, and snapshot risks and opportunities across business units, then export or compare snapshots for governance and reporting.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + TypeScript, Element Plus, Pinia, Vue Router, Vite |
| Backend | FastAPI, SQLAlchemy 2, Pydantic 2, Uvicorn |
| Database | Azure Databricks PostgreSQL (`sbfo_ro` schema) |
| Deployment | Databricks Apps |
| Config | `app.yaml` (both local dev and production) |

---

## Project Structure

```
sbfo-ro/
├── app.yaml              # Environment config (local + production)
├── requirements.txt      # Python dependencies
├── backend/
│   ├── main.py           # FastAPI app entry point, SPA serving
│   └── app/
│       ├── config.py     # Env loading from app.yaml or os.environ
│       ├── database.py   # SQLAlchemy engine + session
│       ├── models.py     # ORM models
│       ├── schemas.py    # Pydantic request/response schemas
│       ├── crud.py       # Database operations
│       └── api/
│           ├── auth.py       # Authentication
│           ├── entries.py    # Entry CRUD & versioning
│           ├── snapshots.py  # Snapshot management
│           ├── users.py      # User management
│           └── lookups.py    # Dropdown data
└── frontend/
    ├── src/
    │   ├── pages/        # Route-level views
    │   ├── components/   # Shared components (EntriesTable, EntryForm, …)
    │   ├── stores/       # Pinia state (entries, lookups, auth)
    │   ├── services/     # Axios API client
    │   ├── types/        # TypeScript interfaces
    │   └── utils/        # Formatters, export helpers
    └── vite.config.ts
```

---

## Features

### Entries
- Create, edit, duplicate, and delete risk/opportunity entries
- Multi-dimensional attributes: division, country, channel, brand, IBP step, R&O type, probability, categorisation, description
- Financial impact: NSV in AUD or NZD, volume in cases
- **Child impacts**: break a single entry into multiple period-level impacts (e.g. F05 2026, F07–F08 2026)
- Full version history — every edit creates a new version; originals are preserved
- Status workflow: Open → Approved / Dismissed / Included in Forecast

### Table Views
- **Column selector**: show/hide optional columns without affecting data
- **Split view**: group entries by any combination of Country, Division, IBP Step, R&O, Priority
- **Period view**: pivot child impacts into Month / Quarter / Half Year / Year columns
- **Impact Period display**: consecutive periods are merged into ranges (e.g. F07 2026 – F09 2026)
- **Quick filters**: Open Only, High Priority, Recently Modified, IBP Step shortcuts
- **Advanced filters**: Division, Country, Channel, Sub-Channel, Account, Brand, Brand Family, IBP Step, Owner, Status

### Snapshots
- Freeze the current state of entries into a named snapshot (Period + Year + IBP Step)
- View any snapshot's entries in a read-only table
- **Snapshot Comparison**: select two snapshots and see New / Deleted / Modified / Unchanged rows, with old → new values shown inline per changed cell
- Delete snapshots

### Export
- Export to **Excel (.xlsx)** with two sheets:
  - **Parents** — one row per entry, aggregated impact values
  - **Details** — one row per child impact (or parent if no children)
- Respects current column visibility settings
- Available per split group or for all filtered entries
- Also available on the Snapshot detail page

### Users & Roles

| Role | Permissions |
|------|------------|
| System Admin | Full access |
| User | Create and edit own Open entries |
| Department Approver | Approve/reject entries in their departments |
| Finance Approver | Mark entries as Included in Forecast |

---

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 18+
- Access to the Azure Databricks PostgreSQL instance

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run (reads DATABASE_URL and AUTH_MODE from app.yaml automatically)
uvicorn main:app --app-dir backend --reload
```

The backend starts on `http://localhost:8000`. In LOCAL mode it serves the built frontend from `frontend/dist/`.

### Frontend

```bash
cd frontend
npm install
npm run dev      # Dev server on http://localhost:5173 with proxy to :8000
npm run build    # Build to frontend/dist/
```

### Configuration

All configuration lives in `app.yaml`. No `.env` file is needed.

```yaml
env:
  - name: AUTH_MODE
    value: DBX          # LOCAL for local auth, DBX for Databricks auth
  - name: DATABASE_URL
    value: 'postgresql+psycopg2://...'
```

When `AUTH_MODE` is not set in the process environment (i.e. local dev), `config.py` reads `app.yaml` directly. On Databricks Apps the platform injects the variables into `os.environ`.

---

## Deployment

The app is deployed as a **Databricks App**:

1. Build the frontend: `cd frontend && npm run build`
2. Deploy via the Databricks Apps UI or CLI — it reads `app.yaml` for the start command and environment variables
3. The FastAPI backend serves the built Vue SPA from `frontend/dist/`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET/POST | `/api/entries` | List / create entries |
| GET/PUT/DELETE | `/api/entries/{id}` | Get / update / delete entry |
| GET | `/api/entries/{id}/history` | Version history |
| GET/POST | `/api/snapshots` | List / create snapshots |
| GET/DELETE | `/api/snapshots/{id}` | Get / delete snapshot |
| GET | `/api/snapshots/{id}/entries` | Entries in a snapshot |
| GET/POST | `/api/users` | List / create users |
| GET/PUT | `/api/users/{id}` | Get / update user |
| GET | `/api/lookups/{category}` | Dropdown options |
| POST | `/api/auth/login` | Authenticate user |
