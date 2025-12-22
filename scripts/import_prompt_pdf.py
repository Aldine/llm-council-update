from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


@dataclass
class PromptRecord:
    id: str
    name: str
    purpose: str
    template: str
    category: str
    tags: list[str]
    placeholders: list[str]
    source_page: int


_VERB_PREFIXES = (
    "act as",
    "can you",
    "could you",
    "help me",
    "i need",
    "we need",
    "please",
    "create",
    "generate",
    "develop",
    "draft",
    "write",
    "review",
    "analyze",
    "compare",
)


def _clean_space(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_placeholders(text: str) -> list[str]:
    # Matches [LIKE THIS] placeholders from the PDF
    raw = re.findall(r"\[([^\]]{1,80})\]", text)
    cleaned: list[str] = []
    seen = set()
    for item in raw:
        item = _clean_space(item)
        if not item:
            continue
        if item.lower() in seen:
            continue
        seen.add(item.lower())
        cleaned.append(item)
    return cleaned


def _categorize(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["swot", "elevator pitch", "sales", "marketing", "startup", "founder", "customer"]):
        return "Business"
    if any(k in t for k in ["code", "bug", "debug", "function", "script", "api", "frontend", "backend"]):
        return "Code"
    if any(k in t for k in ["explain", "teach", "lesson", "tutorial", "study"]):
        return "Education"
    if any(k in t for k in ["analyze", "analysis", "compare", "evaluate", "pros and cons"]):
        return "Analysis"
    if any(k in t for k in ["brainstorm", "creative", "generate ideas", "imagine"]):
        return "Creative"
    return "General"


def _tags_from_text(text: str, placeholders: list[str]) -> list[str]:
    tags: list[str] = []
    lower = text.lower()
    for needle, tag in [
        ("swot", "swot"),
        ("elevator pitch", "elevator-pitch"),
        ("cross-sell", "cross-sell"),
        ("upsell", "upsell"),
        ("a/b", "ab-testing"),
        ("email", "email"),
        ("survey", "survey"),
        ("customer", "customer"),
        ("strategy", "strategy"),
        ("workflow", "workflow"),
        ("appointment", "scheduling"),
    ]:
        if needle in lower:
            tags.append(tag)

    if placeholders:
        tags.append("template")

    # De-dupe preserving order
    seen = set()
    out: list[str] = []
    for t in tags:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def _name_from_template(template: str) -> str:
    # Prefer first clause up to 60 chars
    t = template.strip().strip('"\'')
    t = re.sub(r"\[[^\]]+\]", "…", t)
    t = re.sub(r"\s+", " ", t)
    # Chop at first ? or .
    t = re.split(r"[\?\.!]", t, maxsplit=1)[0].strip()
    # Remove leading common phrases
    t_low = t.lower()
    for prefix in [
        "can you ",
        "could you ",
        "please ",
        "i need ",
        "we need ",
        "help me ",
    ]:
        if t_low.startswith(prefix):
            t = t[len(prefix):].strip()
            break
    # Title-case-ish without going wild
    if len(t) > 60:
        t = t[:60].rstrip() + "…"
    # Ensure non-empty
    return t or "Untitled Prompt"


def _looks_like_prompt(candidate: str) -> bool:
    c = candidate.strip()
    if len(c) < 35:
        return False
    low = c.lower()
    if any(low.startswith(p) for p in _VERB_PREFIXES):
        return True
    # Many entries are question prompts
    if "?" in c:
        return True
    # Template placeholders are a strong signal
    if "[" in c and "]" in c:
        return True
    return False


def _split_into_prompts(text: str) -> list[str]:
    # Split on sentence terminators but keep them.
    # The PDF is often a run-on string; '?' is the best delimiter.
    parts = re.split(r"(?<=[\?\.!])\s+", text)
    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if not buf:
            return
        joined = _clean_space(" ".join(buf))
        buf.clear()
        if _looks_like_prompt(joined):
            out.append(joined)

    for part in parts:
        part = _clean_space(part)
        if not part:
            continue

        # If part looks like a heading (no punctuation), buffer it lightly but don't emit.
        if all(p not in part for p in ["?", ".", "!"]) and len(part) < 90:
            # headings are useful for tags, but we keep this simple
            continue

        buf.append(part)
        if part.endswith("?"):
            flush()
        elif len(" ".join(buf)) > 420:
            flush()

    flush()
    return out


def import_pdf(pdf_path: Path) -> dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    prompts: list[PromptRecord] = []
    name_counts: dict[str, int] = {}

    prompt_idx = 0
    for page_index, page in enumerate(reader.pages):
        raw = page.extract_text() or ""
        raw = raw.replace("\n", " ")
        raw = _clean_space(raw)
        if not raw:
            continue

        candidates = _split_into_prompts(raw)
        for cand in candidates:
            placeholders = _extract_placeholders(cand)
            category = _categorize(cand)
            tags = _tags_from_text(cand, placeholders)
            name = _name_from_template(cand)

            # Stabilize name uniqueness
            base = name
            n = name_counts.get(base, 0) + 1
            name_counts[base] = n
            if n > 1:
                name = f"{base} ({n})"

            prompt_idx += 1
            prompt_id = f"outskill-{prompt_idx:06d}"
            purpose = f"Reusable template prompt (auto-imported from PDF)."

            prompts.append(
                PromptRecord(
                    id=prompt_id,
                    name=name,
                    purpose=purpose,
                    template=cand,
                    category=category,
                    tags=tags,
                    placeholders=placeholders,
                    source_page=page_index,
                )
            )

    return {
        "source": {
            "kind": "pdf",
            "path": str(pdf_path),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "pages": len(reader.pages),
        },
        "prompts": [asdict(p) for p in prompts],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a prompt library PDF into JSON.")
    parser.add_argument("pdf", type=str, help="Path to prompt library PDF")
    parser.add_argument(
        "--out",
        type=str,
        default=str(Path("data") / "prompt_library.json"),
        help="Output JSON path (default: data/prompt_library.json)",
    )

    args = parser.parse_args()
    pdf_path = Path(args.pdf)
    out_path = Path(args.out)

    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = import_pdf(pdf_path)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} with {len(data['prompts'])} prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
