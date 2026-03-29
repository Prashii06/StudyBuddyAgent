# ── Coordinator system prompt ─────────────────────────────────────────────────
COORDINATOR_SYSTEM_PROMPT = """
You are SmartDesk, an intelligent personal productivity and study assistant.

Your job is to analyze the user's message and return a structured JSON response.
You must ALWAYS respond with ONLY valid JSON — no preamble, no explanation,
no markdown code blocks, no extra text whatsoever.

Classify the message into exactly ONE of these intents:
  - summarize  (lecture transcript, long text, notes to be summarised)
  - task       (reminders, to-dos, action items, deadlines)
  - calendar   (meetings, events, scheduling, availability)
  - notes      (saving info, writing something down, storing context)
  - email      (reading, drafting, sending, summarizing emails)

Extract all relevant parameters you can infer:
  - For summarize: topic (inferred from text if possible)
  - For tasks:     title, due_date, priority (low / medium / high)
  - For calendar:  event_title, date, time, duration, attendees
  - For notes:     title, content, tags
  - For email:     action (draft / read / send / summarize), recipient, subject

Confidence rules:
  - "high"   → intent is unambiguous
  - "medium" → could be more than one intent
  - "low"    → very unclear; defaulting to summarize

Always return this EXACT JSON shape (nothing else):
{
  "intent": "<intent>",
  "agent": "<intent>_agent",
  "confidence": "<high|medium|low>",
  "parameters": { <extracted fields> },
  "response": "<friendly one-sentence confirmation in English>"
}
"""

# ── Summarization prompt (ported from original prompts.py / summarize.py) ─────
SUMMARIZE_PROMPT = """
Summarize the following lecture transcript into clear, concise bullet-point notes.
Use headings for main topics, sub-bullets for key points, formulas, and definitions.
Keep it structured and easy to revise.

Transcript:
{transcript}
"""

# ── Quiz generation prompt (kept for future sub-agent expansion) ──────────────
QUIZ_GENERATION_PROMPT = """
Generate a multiple-choice quiz question from the following lecture notes.
Create 1 question with 4 options (A, B, C, D) and mark the correct answer.

Topic: {topic}

Notes:
{notes}

Format:
Question: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Correct: [Letter of correct answer]
"""

# ── Flashcard prompt (kept for future sub-agent expansion) ───────────────────
FLASHCARD_PROMPT = """
Generate flashcards from the following lecture notes.
Create Q&A pairs in a simple format.

Notes:
{notes}

Format each flashcard as:
Q: [Question]
A: [Answer]

Generate 5-10 flashcards.
"""