"""INEVITABLE Core Prompt Pack.

These are original prompt templates intended to be stable building blocks.
They are NOT sourced from any third-party PDF.
"""

from __future__ import annotations

from typing import Dict, List


def get_core_prompts() -> List[Dict[str, str]]:
    return [
        {
            "name": "Prompt Synthesizer",
            "purpose": "Generate a strong first-draft prompt from Goal/Context/Audience.",
            "template": (
                "Act as my Prompt Synthesizer.\n"
                "Goal: [GOAL]\n"
                "Context: [CONTEXT]\n"
                "Audience: [AUDIENCE]\n"
                "Constraints: [CONSTRAINTS]\n"
                "Output format: [OUTPUT FORMAT]\n\n"
                "Return: (1) A best-possible prompt, (2) 3 optional variations."
            ),
        },
        {
            "name": "Clarify First",
            "purpose": "Ask only the minimum questions needed before producing output.",
            "template": (
                "Before answering, ask up to [N] clarifying questions that materially change the result.\n"
                "Then wait for my answers.\n\n"
                "If you already have enough, say: 'No questions needed' and proceed."
            ),
        },
        {
            "name": "Critique & Improve",
            "purpose": "Take an existing prompt and rewrite it for quality and specificity.",
            "template": (
                "Improve this prompt for clarity, constraints, and output format.\n"
                "Original prompt: [PASTE PROMPT]\n\n"
                "Return:\n"
                "- Revised prompt\n"
                "- What changed (bullets)\n"
                "- 3 follow-up questions the prompt should answer"
            ),
        },
        {
            "name": "Role + Rubric",
            "purpose": "Make outputs consistent by defining role, rubric, and failure modes.",
            "template": (
                "Act as [ROLE].\n"
                "Task: [TASK].\n"
                "Rubric (score 0-2 each): [RUBRIC ITEMS].\n"
                "Hard constraints: [CONSTRAINTS].\n"
                "Output: [FORMAT].\n\n"
                "If any required info is missing, ask up to 3 questions first."
            ),
        },
        {
            "name": "Extract → Transform → Output",
            "purpose": "Reliable structured extraction and formatting.",
            "template": (
                "Extract the following fields from the input: [FIELDS].\n"
                "Then transform them by applying: [RULES].\n"
                "Then output strictly as: [JSON/CSV/MARKDOWN TABLE].\n\n"
                "Input: [PASTE INPUT]"
            ),
        },
    ]
