#!/usr/bin/env python
"""Append new Google Scholar publications to _bibliography/papers.bib.

Unlike bin/update_scholar_citations.py (which only refreshes citation counts for
publications that are already listed), this script detects publications on Scholar
that are NOT yet in papers.bib and appends a generated BibTeX entry for each one.
Existing entries are never modified, so any manual curation (abbr, selected,
bibtex_show, etc.) on existing entries is preserved.
"""

import os
import re
import sys

import yaml
from scholarly import scholarly

BIB_FILE = "_bibliography/papers.bib"
SOCIALS_FILE = "_data/socials.yml"


def load_scholar_user_id() -> str:
    if not os.path.exists(SOCIALS_FILE):
        print(f"Configuration file {SOCIALS_FILE} not found.")
        sys.exit(1)
    with open(SOCIALS_FILE, "r") as f:
        config = yaml.safe_load(f)
    scholar_user_id = config.get("scholar_userid")
    if not scholar_user_id:
        print(f"No 'scholar_userid' found in {SOCIALS_FILE}.")
        sys.exit(1)
    return scholar_user_id


def normalize_title(title: str) -> str:
    """Lowercase and strip everything but letters/digits, so trivial formatting
    differences (LaTeX escapes, punctuation, accents) don't cause false negatives."""
    title = re.sub(r"[{}\\]", "", title)
    return re.sub(r"[^a-z0-9]", "", title.lower())


def existing_titles(bib_text: str) -> set:
    """Extract normalized titles already present in papers.bib.

    Handles single-level nested braces in title values (e.g. `{\"u}`), which a
    naive non-greedy regex would truncate on.
    """
    titles = set()
    for match in re.finditer(r"title\s*=\s*\{", bib_text):
        start = match.end()
        depth = 1
        i = start
        while i < len(bib_text) and depth > 0:
            if bib_text[i] == "{":
                depth += 1
            elif bib_text[i] == "}":
                depth -= 1
            i += 1
        raw_title = bib_text[start : i - 1]
        titles.add(normalize_title(raw_title))
    return titles


def existing_keys(bib_text: str) -> set:
    return set(re.findall(r"@\w+\{([^,]+),", bib_text))


def unique_key(base_key: str, taken: set) -> str:
    key = base_key
    suffix = ord("a")
    while key in taken:
        key = f"{base_key}{chr(suffix)}"
        suffix += 1
    return key


def main() -> None:
    scholar_user_id = load_scholar_user_id()

    if not os.path.exists(BIB_FILE):
        print(f"{BIB_FILE} not found.")
        sys.exit(1)

    with open(BIB_FILE, "r") as f:
        bib_text = f.read()

    known_titles = existing_titles(bib_text)
    taken_keys = existing_keys(bib_text)

    scholarly.set_timeout(20)
    scholarly.set_retries(3)

    print(f"Fetching publication list for Google Scholar ID: {scholar_user_id}")
    try:
        author = scholarly.search_author_id(scholar_user_id)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        print(f"Error fetching author data from Google Scholar: {e}")
        sys.exit(1)

    new_entries = []
    for pub in author.get("publications", []):
        title = pub.get("bib", {}).get("title", "")
        if not title or normalize_title(title) in known_titles:
            continue

        print(f"New publication found: {title!r} — fetching details...")
        try:
            pub = scholarly.fill(pub)
            bibtex = scholarly.bibtex(pub)
        except Exception as e:
            print(f"  Warning: could not fetch/convert {title!r}: {e}. Skipping.")
            continue

        match = re.match(r"@(\w+)\{([^,]+),", bibtex)
        if not match:
            print(f"  Warning: could not parse generated BibTeX for {title!r}. Skipping.")
            continue
        entry_type, base_key = match.groups()
        key = unique_key(base_key, taken_keys)
        taken_keys.add(key)
        bibtex = bibtex.replace(f"@{entry_type}{{{base_key},", f"@{entry_type}{{{key},", 1)

        new_entries.append(bibtex.strip())
        known_titles.add(normalize_title(title))

    if not new_entries:
        print("No new publications found. Nothing to do.")
        return

    addition = (
        "\n\n% --- Auto-added by bin/update_scholar_publications.py — please review"
        " (venue/abbr/selected fields) ---\n\n"
        + "\n\n".join(new_entries)
        + "\n"
    )
    with open(BIB_FILE, "a") as f:
        f.write(addition)

    print(f"Added {len(new_entries)} new publication(s) to {BIB_FILE}.")


if __name__ == "__main__":
    main()
