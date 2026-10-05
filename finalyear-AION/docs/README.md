# AION

Adaptive Goal-Oriented AI Operating Layer with Autonomous Workflow Learning

## Project Overview
AION is a Windows desktop AI operating layer that runs on top of Windows, not a replacement operating system. It combines a compact conversational assistant UI, least-privilege permission controls, and real automation engines for file, application, and browser workflows.

Primary interaction model:

1. Small AION tray/icon presence
2. Compact floating assistant
3. Natural-language goal input
4. Plan explanation and approval
5. Controlled execution through allowlisted actions
6. Verification, history, and learning updates

## Problem Statement
Most desktop automation tools are either script-heavy for technical users or opaque/noisy for non-technical users. AION addresses this by providing:

- Goal-first natural language interaction
- Explicit user approvals
- Capability-scoped permissions
- Multi-agent orchestration
- Persistent memory and workflow learning

## Proposed Solution
AION uses a backend orchestration engine and a lightweight frontend assistant:

- GoalInterpreter converts user intent to structured tasks.
- TaskPlanner validates order and required capabilities.
- PermissionManager enforces least privilege.
- AutomationExecutor routes tasks to specialized agents.
- RecoveryEngine handles common failures.
- SQLite memory stores workflows, executions, preferences, and learning stats.

## Architecture

### Backend
- FastAPI API + WebSocket progress stream
- Pydantic structured models
- SQLAlchemy SQLite persistence
- Agent-based controlled execution

### Frontend
- React + Vite + TypeScript
- Tailwind compact floating assistant UI
- Real-time workflow updates
- First-time onboarding conversation

### Desktop Integration
- Tray launcher via pystray (backend/desktop/tray_app.py)

## Core Modules
- Goal Agent and Interpreter: parse natural language safely
- Planner Agent and TaskPlanner: generate executable workflow plans
- File Agent: real pathlib/shutil operations
- Browser Agent: Playwright-based public web automation
- Application Agent: safe app launch with installed-app checks
- Memory Agent and MemoryManager: workflow/prefs persistence
- Recovery Agent and RecoveryEngine: failure handling and retries
- LearningEngine: repeated successful workflow detection
- ActionRegistry + Validator + PermissionManager: security boundaries

## Technology Stack
- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- python-dotenv
- OpenAI API abstraction layer
- Playwright
- pathlib, shutil, psutil
- pywin32 and pystray for desktop integration
- React + Vite + TypeScript + Tailwind CSS
- pytest

## Security Architecture
AION uses a controlled automation layer:

- Allowlisted actions only
- Capability checks per task
- Scope-level permission checks
- Optional destructive-operation confirmation flags
- No arbitrary shell/code execution from LLM outputs
- Structured logging without secret exposure

## Permission Model
Permissions are capability-based and scope-aware.

Examples:

- file_access for Downloads directory
- browser_access for public URL actions
- application_access for app launch actions

Permissions are requested and granted through API endpoints and enforced before task execution.

## Multi-Agent Architecture
- GoalAgent
- PlannerAgent
- FileAgent
- BrowserAgent
- ApplicationAgent
- MemoryAgent
- RecoveryAgent
- AgentManager for routing

## Workflow Learning
LearningEngine evaluates workflow repetition and success/failure rates.
When a workflow crosses threshold and remains successful, it can be marked learned after user decision.

## Failure Recovery
RecoveryEngine currently handles common recoverable file-path scenarios and returns structured recovery payloads. Non-recoverable failures are preserved with explicit reasons.

## Installation

### 1) Clone / open workspace
Use this repository as the workspace root.

### 2) Backend setup
From repository root:

PowerShell:

python -m pip install -r backend/requirements.txt

### 3) Environment setup
Copy .env.example to .env and set values:

- OPENAI_API_KEY
- AION_HOST
- AION_PORT
- AION_FRONTEND_URL

### 4) Frontend setup
From frontend folder:

npm install

### 5) Playwright setup
From repository root:

python -m playwright install chromium

## Running AION

### Start backend
From repository root:

python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

### Start frontend
From frontend folder:

npm run dev

### Start tray icon
From repository root (after backend + frontend are running):

python -m backend.desktop.tray_app

## Testing
From repository root:

python -m pytest -q tests/unit

Manual live-API workflows are in `tests/manual/`. They are not collected by pytest because they can create, move, or delete files when run against a live backend.

## Demonstration Workflows

### Demo 1: PDF organization
Goal:
Create a folder called AION_Demo in my Downloads folder and move all PDF files from Downloads into it.

Expected:
- Goal interpreted into structured tasks
- Plan generated
- file_access permission requested/granted
- User approval recorded
- Files actually found/moved/verified
- Execution history persisted
- Learning stats updated

### Demo 2: Browser research
Goal:
Open Chrome and search for AION AI operating system research papers.

Expected:
- BrowserAgent workflow plan
- browser_access permission
- Approval and execution
- Browser opens/public search performed
- Execution history persisted

### Demo 3: Learning detection
Repeat Demo 1 several times. After threshold:
- Learning candidate appears
- User can save learned workflow
- Learned workflows are listed and reusable

## API Surface
- GET /api/health
- POST /api/goal/interpret
- POST /api/workflow/plan
- POST /api/workflow/approve
- POST /api/workflow/execute
- GET /api/workflow/history
- GET /api/workflow/{id}
- GET /api/memory
- POST /api/memory/preferences
- GET /api/learning/workflows
- POST /api/learning/{id}/run
- POST /api/learning/{id}/save
- GET /api/system/context
- GET /api/permissions
- POST /api/permissions/request
- POST /api/permissions/grant
- POST /api/permissions/revoke
- WS /ws/workflow/{workflow_id}

## Current Limitations
- Dependency installation and runtime verification are required on the target machine before full E2E execution.
- Browser automation currently focuses on public navigation/search patterns.
- Recovery strategy is implemented for common path issues and can be expanded.
- Tray integration opens the compact UI in browser; native embedded floating window behavior can be enhanced in next iteration.

## Future Scope
- Richer NLU and robust multi-step planning with strict schema correction loops
- Native always-on-top floating window anchored near tray icon
- Voice input/output pipeline
- Advanced policy engine for fine-grained risk levels
- Workflow optimization recommendations with user approval flow
- Expanded UI pages for detailed history, memory, and agent activity
