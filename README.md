# SmartDesk Phase 1 — AI Study Buddy Agent

A single AI agent built with **Google ADK (Gemini)** and deployed on **Cloud Run**.  
It classifies a user's study-related message and, for transcript inputs, returns
structured bullet-point notes — all via a single HTTP endpoint.

## Architecture

```
POST /run-agent
      │
      ▼
CoordinatorAgent  (google-genai + Gemini 2.0 Flash)
      │
      ├── classify intent  →  task / calendar / notes / email / summarize
      │
      └── [if summarize]  →  generate bullet-point lecture notes
```

## Project Structure

```
smartdesk-phase1/
├── agents/
│   ├── __init__.py
│   └── coordinator.py      # ADK-style Gemini agent
├── config/
│   ├── __init__.py
│   ├── prompts.py          # System + task prompts
│   └── settings.py         # Env-based config
├── main.py                 # FastAPI app + endpoints
├── requirements.txt
├── Dockerfile
├── cloudbuild.yaml
├── .env.template
├── .gitignore
└── README.md
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/run-agent` | Run the agent on a single message |
| POST | `/batch` | Run up to 5 messages at once |

### Request body (`/run-agent`)
```json
{ "message": "Summarize this transcript: Newton's laws state..." }
```
Both `"message"` and `"query"` field names are accepted.

### Response
```json
{
  "intent": "summarize",
  "agent": "summarize_agent",
  "confidence": "high",
  "parameters": {
    "topic": "Newton's laws",
    "summary": "## Newton's Laws\n- **First law**: ..."
  },
  "response": "## Newton's Laws\n- **First law**: ...",
  "status": "success"
}
```

## Local Setup

```bash
# 1. Clone & enter directory
git clone <repo-url> && cd studybuddyagent

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
cp .env.template .env
# Edit .env and set GEMINI_API_KEY=your_key_here

# 5. Run locally
uvicorn main:app --reload --port 8080
```

## Test with curl

```bash
BASE=http://localhost:8080

# Health check
curl $BASE/health

# Intent classification
curl -X POST $BASE/run-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Remind me to submit the assignment by Thursday"}'

# Lecture summarization
curl -X POST $BASE/run-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize: Thermodynamics is the branch of physics that deals with heat and temperature and their relation to energy. The first law states energy cannot be created or destroyed."}'

# Calendar intent
curl -X POST $BASE/run-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Schedule a team standup tomorrow at 10am"}'

# Batch
curl -X POST $BASE/batch \
  -H "Content-Type: application/json" \
  -d '{"messages": ["What is on my plate today?", "Add task: review PR by Friday"]}'
```

## Deploy to Cloud Run

### Option A — Manual (quickest)
```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build & push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/smartdesk-phase1

# Deploy
gcloud run deploy smartdesk-phase1 \
  --image gcr.io/YOUR_PROJECT_ID/smartdesk-phase1 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 30 \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

### Option B — Cloud Build (CI/CD)
Store `GEMINI_API_KEY` in Secret Manager, then:
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | Your Google AI Studio API key |
| `GEMINI_MODEL` | ❌ | `gemini-2.0-flash` | Model override |

## Getting a Gemini API Key

1. Go to https://aistudio.google.com/
2. Click **Get API Key**
3. Copy the key into your `.env` file

## What Changed from the Original Project

| Original (AI Study Buddy) | Phase 1 (This project) |
|---|---|
| Streamlit UI | FastAPI REST API |
| Groq + LangChain | Google Gemini (google-genai) |
| Whisper audio transcription | Removed (out of scope) |
| FAISS vector store | Removed (stateless agent) |
| SQLite persistence | Removed (stateless agent) |
| PDF export | Removed (out of scope) |
| `@st.cache_resource` | Standard Python class |

The **summarization logic** from `utils/summarize.py` and **prompts** from
`config/prompts.py` have been directly ported and adapted.