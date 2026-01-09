#!/usr/bin/env python3
"""
Simple Aladí catalog searcher for Barcelona library network.
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

BASE_URL = "https://aladi.diba.cat"

# Cache for library codes
_library_cache: dict[str, str] | None = None


def get_all_libraries() -> dict[str, str]:
    """Fetch all library names and codes from the advanced search page."""
    global _library_cache
    if _library_cache is not None:
        return _library_cache

    response = requests.get(f"{BASE_URL}/search*cat/X")
    soup = BeautifulSoup(response.text, "html.parser")

    select = soup.select_one('select[name="b"]')
    if not select:
        return {}

    libraries = {}
    for option in select.select("option"):
        code = option.get("value", "")
        name = option.get_text(strip=True)
        if code and name and name != "Qualsevol":
            libraries[name] = code

    _library_cache = libraries
    return libraries


def find_library_code(query: str) -> tuple[str, str] | None:
    """Find library code by searching library names. Returns (name, code) or None."""
    libraries = get_all_libraries()
    query_lower = query.lower()

    # Try exact match first
    for name, code in libraries.items():
        if query_lower == name.lower():
            return (name, code)

    # Try substring match
    matches = []
    for name, code in libraries.items():
        if query_lower in name.lower():
            matches.append((name, code))

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Return best match (shortest name containing the query)
        matches.sort(key=lambda x: len(x[0]))
        return matches[0]

    # Try word-based match: all query words must be in the library name
    query_words = query_lower.split()
    if len(query_words) > 1:
        for name, code in libraries.items():
            name_lower = name.lower()
            if all(word in name_lower for word in query_words):
                matches.append((name, code))

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            matches.sort(key=lambda x: len(x[0]))
            return matches[0]

    return None


def search_author_at_library(author: str, library_name: str, library_code: str) -> list[dict]:
    """Search for an author's works at a specific library."""

    # Build search URL
    encoded_author = urllib.parse.quote(author)
    search_url = f"{BASE_URL}/search~S1*cat/X?SEARCH=({encoded_author})&searchscope=171&SORT=AX&b={library_code}"

    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    seen_titles = set()

    # Find book links - they contain 'frameset' in the href
    for link in soup.select('a[href*="frameset"]'):
        title = link.get_text(strip=True)
        href = link.get("href", "")

        # Skip non-title links
        if not title or len(title) < 5 or title in seen_titles:
            continue
        if title in ("+ info", "Cliqueu el títol per veure tots els exemplars"):
            continue

        seen_titles.add(title)

        # Get holdings for this book
        holdings_url = BASE_URL + href.replace("/frameset", "/holdings")
        copies = get_holdings(holdings_url, library_name)

        if copies:  # Only include if there are copies at this library
            results.append({
                "title": title,
                "copies": copies
            })

    return results


def get_holdings(holdings_url: str, library_name: str) -> list[dict]:
    """Get all copies at a specific library from the holdings page."""

    # Convert frameset URL to holdings URL if needed
    if "/frameset" in holdings_url:
        holdings_url = holdings_url.replace("/frameset", "/holdings")
    elif "/holdings" not in holdings_url:
        holdings_url = re.sub(r"\)$", ")/holdings", holdings_url)

    response = requests.get(holdings_url)
    soup = BeautifulSoup(response.text, "html.parser")

    copies = []

    # Extract the key part of the library name for matching (e.g., "Moià" from "Moià. Municipal 1 d'octubre")
    match_name = library_name.split(".")[0].strip().lower()

    # Find all rows in the holdings table
    for row in soup.select("tr"):
        cells = row.select("td")
        if len(cells) < 3:
            continue

        location = cells[0].get_text(strip=True)

        # Check if this is the library we want (case-insensitive partial match)
        if match_name not in location.lower():
            continue

        signature = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        status = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        notes = cells[3].get_text(strip=True) if len(cells) > 3 else ""

        copies.append({
            "location": location,
            "signature": signature,
            "status": status,
            "notes": notes
        })

    return copies


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python aladi_search.py <author> <library>")
        print("Example: python aladi_search.py 'Irene Solà' moià")
        print("Example: python aladi_search.py 'Irene Solà' \"Biblioteca Municipal 1 d'Octubre\"")
        sys.exit(1)

    author = sys.argv[1]
    library_query = sys.argv[2]

    result = find_library_code(library_query)
    if not result:
        print(f"Library not found: {library_query}")
        sys.exit(1)

    library_name, library_code = result
    print(f"Searching for '{author}' at {library_name} ({library_code})...\n")

    results = search_author_at_library(author, library_name, library_code)

    if not results:
        print("No results found.")
        return

    for book in results:
        print(f"📚 {book['title']}")
        for copy in book["copies"]:
            status = copy["status"]
            status_icon = "✓" if status.lower() == "disponible" else "✗"
            print(f"   {status_icon} {status}")
            if copy["notes"]:
                print(f"     ({copy['notes']})")
        print()


if __name__ == "__main__":
    main()
