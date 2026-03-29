import os
import json
import re
import logging
from google import genai
from google.genai import types
from config.prompts import COORDINATOR_SYSTEM_PROMPT, SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Single ADK-style agent that:
      1. Classifies the user's intent (task / calendar / notes / email / summarize)
      2. For 'summarize' intent, calls Gemini a second time to produce the actual summary
      3. Returns a structured JSON-compatible dict
    """

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Set GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash"
        logger.info(f"CoordinatorAgent initialised with model={self.model}")

    # ── public ────────────────────────────────────────────────────────────────

    def run(self, user_input: str) -> dict:
        try:
            classified = self._classify(user_input)
            intent = classified.get("intent", "summarize")

            # For summarize intent, run a dedicated summarization pass
            if intent == "summarize":
                summary = self._summarize(user_input)
                classified["parameters"]["summary"] = summary
                classified["response"] = summary

            return {**classified, "status": "success"}

        except Exception as exc:
            logger.exception("Agent error")
            return {
                "intent": None,
                "agent": None,
                "confidence": None,
                "parameters": None,
                "response": str(exc),
                "status": "error",
            }

    # ── private ───────────────────────────────────────────────────────────────

    def _classify(self, text: str) -> dict:
        """Call Gemini with the coordinator system prompt and parse JSON response."""
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=COORDINATOR_SYSTEM_PROMPT,
                temperature=0.2,
            ),
            contents=text,
        )
        raw = response.text.strip()
        return self._parse_json(raw)

    def _summarize(self, transcript: str) -> str:
        """Run a dedicated summarization pass using the study-buddy prompt."""
        prompt = SUMMARIZE_PROMPT.format(transcript=transcript)
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(temperature=0.3),
            contents=prompt,
        )
        return response.text.strip()

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """Robustly extract JSON from the model response."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: extract first {...} block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        # Last-resort default
        return {
            "intent": "summarize",
            "agent": "summarize_agent",
            "confidence": "low",
            "parameters": {"raw_response": raw},
            "response": raw,
        }