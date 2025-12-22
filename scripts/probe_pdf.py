from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if len(sys.argv) < 2:
        print("usage: probe_pdf.py <path-to-pdf>")
        return 2

    pdf_path = Path(sys.argv[1])
    print("path:", pdf_path)
    print("exists:", pdf_path.exists())
    if not pdf_path.exists():
        return 1

    try:
        from pypdf import PdfReader
    except Exception as e:
        print("ERROR: failed to import pypdf:", repr(e))
        return 3

    try:
        reader = PdfReader(str(pdf_path))
        print("pages:", len(reader.pages))
        for i in range(min(3, len(reader.pages))):
            text = (reader.pages[i].extract_text() or "")
            print(f"--- page {i} chars: {len(text)} ---")
            print(text[:2000])
    except Exception as e:
        print("ERROR: failed to read/extract:", repr(e))
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
