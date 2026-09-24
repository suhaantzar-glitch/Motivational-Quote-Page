"""Shared helpers: loading quotes and naming output files consistently."""
import json
import re

import config


def load_quotes(path=config.QUOTES_FILE):
    with open(path, encoding="utf-8") as f:
        quotes = json.load(f)
    for q in quotes:
        q.setdefault("author", "Unknown")
    return quotes


def quote_id(index, quote):
    """Stable file stem like '01_comfort-is-a-quiet' (1-based index + first words)."""
    words = re.sub(r"[^a-z0-9 ]", "", quote["quote"].lower()).split()[:4]
    return f"{index + 1:02d}_{'-'.join(words)}"
