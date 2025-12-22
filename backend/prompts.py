"""Prompt library for helping users craft better questions.

This module intentionally supports a *local* prompt database generated from
user-provided assets (e.g. a PDF the user has rights to use).

We do not ship or embed third-party prompt corpora in the repository.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional


# Cache for loaded prompts
_prompts_cache: Optional[List[Dict[str, Any]]] = None


def _default_prompt_db_path() -> Path:
    # `data/` is gitignored in this repo.
    return Path(__file__).resolve().parent.parent / "data" / "prompt_library.json"


def load_prompt_db() -> List[Dict[str, Any]]:
    """Load prompts from a local JSON database if present."""
    global _prompts_cache
    env_path = os.getenv("PROMPT_LIBRARY_JSON_PATH")
    db_path = Path(env_path) if env_path else _default_prompt_db_path()

    # If we previously cached an empty list because the DB file didn't exist yet,
    # allow a reload once the file appears (common during dev).
    if _prompts_cache is not None:
        if _prompts_cache or not db_path.exists():
            return _prompts_cache

    if not db_path.exists():
        _prompts_cache = []
        return _prompts_cache

    try:
        data = json.loads(db_path.read_text(encoding="utf-8"))
        prompts = data.get("prompts")
        if not isinstance(prompts, list):
            _prompts_cache = []
            return _prompts_cache

        # Normalize to the UI's expected shape: title/text/category
        normalized: List[Dict[str, Any]] = []
        for item in prompts:
            if not isinstance(item, dict):
                continue
            template = str(item.get("template") or "").strip()
            name = str(item.get("name") or "").strip() or str(item.get("title") or "").strip()
            category = str(item.get("category") or "General").strip() or "General"
            if not template:
                continue
            normalized.append(
                {
                    "title": name or "Untitled",
                    "text": template,
                    "category": category,
                    "tags": item.get("tags") or [],
                    "placeholders": item.get("placeholders") or [],
                    "id": item.get("id"),
                }
            )

        _prompts_cache = normalized
        return _prompts_cache

    except Exception:
        _prompts_cache = []
        return _prompts_cache


def parse_prompt_library() -> List[Dict[str, Any]]:
    """Backward-compatible entrypoint.

    Historically this parsed a bundled PDF. We now load from a local JSON DB.
    """
    return load_prompt_db()


def _categorize_prompt(title: str) -> str:
    """Categorize a prompt based on its title."""
    title_lower = title.lower()
    
    categories = {
        "Writing": ["write", "writing", "compose", "draft", "essay", "article", "story"],
        "Analysis": ["analyze", "analysis", "evaluate", "assess", "compare", "review"],
        "Creative": ["create", "creative", "generate", "design", "brainstorm", "imagine"],
        "Code": ["code", "program", "debug", "function", "script", "develop"],
        "Research": ["research", "investigate", "explore", "study", "examine"],
        "Business": ["business", "marketing", "strategy", "sales", "customer"],
        "Education": ["learn", "teach", "explain", "tutorial", "lesson", "study"],
        "Problem Solving": ["solve", "solution", "problem", "fix", "troubleshoot"],
    }
    
    for category, keywords in categories.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    
    return "General"


def get_prompt_suggestions(
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get prompt suggestions, optionally filtered by query or category."""
    prompts = parse_prompt_library()
    
    if not prompts:
        return get_default_suggestions(limit)
    
    # Filter by category if specified
    if category:
        prompts = [p for p in prompts if p["category"] == category]
    
    # Filter/rank by query if specified
    if query:
        query_lower = query.lower().strip()

        def score(p: Dict[str, Any]) -> int:
            hay = f"{p.get('title','')} {p.get('text','')}".lower()
            return hay.count(query_lower)

        prompts = [
            p for p in prompts
            if query_lower in (p.get("title") or "").lower()
            or query_lower in (p.get("text") or "").lower()
        ]
        prompts.sort(key=score, reverse=True)
        return prompts[:limit]

    # No query: randomize for variety
    if len(prompts) > limit:
        prompts = random.sample(prompts, limit)
    return prompts[:limit]


def get_categories() -> List[str]:
    """Get all available prompt categories."""
    prompts = parse_prompt_library()
    if not prompts:
        return ["General", "Writing", "Analysis", "Creative", "Code"]
    
    categories = set(p["category"] for p in prompts)
    return sorted(list(categories))


def get_default_suggestions(limit: int = 10) -> List[Dict[str, Any]]:
    """Return default prompt suggestions if PDF parsing fails."""
    return [
        {
            "title": "Explain Like I'm 5",
            "text": "Explain [complex topic] in simple terms that a 5-year-old could understand.",
            "category": "Education"
        },
        {
            "title": "Pro/Con Analysis",
            "text": "List the pros and cons of [decision or topic] with detailed reasoning.",
            "category": "Analysis"
        },
        {
            "title": "Step-by-Step Guide",
            "text": "Create a detailed step-by-step guide on how to [achieve goal or complete task].",
            "category": "Education"
        },
        {
            "title": "Compare and Contrast",
            "text": "Compare and contrast [item A] and [item B], highlighting key differences and similarities.",
            "category": "Analysis"
        },
        {
            "title": "Creative Brainstorm",
            "text": "Generate 10 creative ideas for [project or problem].",
            "category": "Creative"
        },
        {
            "title": "Devil's Advocate",
            "text": "Play devil's advocate and challenge the following viewpoint: [statement or belief].",
            "category": "Analysis"
        },
        {
            "title": "Future Prediction",
            "text": "Based on current trends, predict how [industry or technology] will evolve in the next 5 years.",
            "category": "Research"
        },
        {
            "title": "Problem Solving Framework",
            "text": "Help me solve [problem] using a structured problem-solving framework.",
            "category": "Problem Solving"
        },
        {
            "title": "Code Review",
            "text": "Review this code and suggest improvements for readability, performance, and best practices: [code]",
            "category": "Code"
        },
        {
            "title": "Business Strategy",
            "text": "Develop a business strategy for [company or product] to achieve [specific goal].",
            "category": "Business"
        }
    ][:limit]
