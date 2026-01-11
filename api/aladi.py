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


def _search_catalog(query: str, library_code: str, search_type: str = "keyword") -> BeautifulSoup | None:
    """Search the catalog and return parsed HTML. Returns None if no results.

    search_type can be:
    - 'keyword': bare search (default)
    - 'title': t:(query)
    - 'author': a:(query)
    """
    encoded_query = urllib.parse.quote(query)

    if search_type == "title":
        search_param = f"t:({encoded_query})"
    elif search_type == "author":
        search_param = f"a:({encoded_query})"
    else:
        search_param = f"({encoded_query})"

    search_url = f"{BASE_URL}/search~S1*cat/X?SEARCH={search_param}&searchscope=171&SORT=AX&b={library_code}"

    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check if there are any results
    links = soup.select('a[href*="frameset"]')
    if links:
        return soup
    return None


def search_author_at_library(author: str, library_name: str, library_code: str) -> list[dict]:
    """Search for an author's works at a specific library with fallback variations."""

    # Try multiple search strategies in order
    soup = None

    # 1. Try title search (user may have entered title/author that matches title)
    soup = _search_catalog(author, library_code, search_type="title")

    # 2. Try author field search
    if not soup:
        soup = _search_catalog(author, library_code, search_type="author")

    # 3. Try keyword search (original method)
    if not soup:
        soup = _search_catalog(author, library_code, search_type="keyword")

    # 4. Try inverted name order (e.g., "Laia Viñas" -> "Viñas Laia")
    if not soup:
        parts = author.strip().split()
        if len(parts) >= 2:
            inverted = f"{parts[-1]} {' '.join(parts[:-1])}"
            soup = _search_catalog(inverted, library_code, search_type="author")

    # 5. Try individual parts (last name first)
    if not soup:
        parts = author.strip().split()
        for part in reversed(parts):
            if len(part) > 2:  # Skip very short parts
                soup = _search_catalog(part, library_code, search_type="keyword")
                if soup:
                    break

    if not soup:
        return []

    results = []
    seen_titles = set()

    # Build a list of cover images from portadesbd.diba.cat
    # These appear in the same order as the book links
    cover_images = [img.get("src", "") for img in soup.select('img[src*="portadesbd.diba.cat"]')]

    # Try to find book links with titles (keyword search results)
    valid_link_index = 0
    for link in soup.select('a[href*="frameset"]'):
        title = link.get_text(strip=True)
        href = link.get("href", "")

        # Skip non-title links
        if not title or len(title) < 5 or title in seen_titles:
            continue
        if title in ("+ info", "Cliqueu el títol per veure tots els exemplars"):
            continue

        seen_titles.add(title)

        # Get cover URL by index (images and valid links should be in same order)
        cover_url = cover_images[valid_link_index] if valid_link_index < len(cover_images) else None
        valid_link_index += 1

        # Get holdings for this book
        holdings_url = BASE_URL + href.replace("/frameset", "/holdings")
        copies = get_holdings(holdings_url, library_name)

        if copies:  # Only include if there are copies at this library
            book_data = {
                "title": title,
                "copies": copies
            }
            if cover_url:
                book_data["cover_url"] = cover_url
            results.append(book_data)

    # If no results from link extraction, try extracting from detail page (single book result)
    if not results:
        # Check if this is a single book detail page (title search returns one result)
        # Only look at the first strong tag in the title field (Títol row)
        title_cell = soup.select_one('td.bibInfoData strong')

        if title_cell:
            text = title_cell.get_text(strip=True)

            if text and text not in seen_titles and len(text) >= 5:
                # This is a book title in a detail page
                # Check if there's a holdings table nearby
                title_table = title_cell.find_parent('table')
                if title_table:
                    # Look for the holdings table (usually comes after in document order)
                    holdings_table = None
                    sibling = title_table.find_next('table')
                    while sibling:
                        table_text = sibling.get_text()
                        if any(word in table_text.lower() for word in ['localització', 'signature', 'estat']):
                            holdings_table = sibling
                            break
                        sibling = sibling.find_next('table')

                    # Try to find the "Veure més exemplars" button to get all holdings
                    more_copies_form = soup.select_one('form input[type="submit"][value*="exemplar"]')
                    if more_copies_form:
                        more_copies_form = more_copies_form.find_parent('form')
                        if more_copies_form:
                            action = more_copies_form.get('action', '')
                            method = more_copies_form.get('method', 'get').lower()

                            if action:
                                holdings_url = BASE_URL + action
                                try:
                                    all_holdings_response = requests.post(holdings_url) if method == 'post' else requests.get(holdings_url)
                                    all_holdings_soup = BeautifulSoup(all_holdings_response.text, 'html.parser')
                                    # Find the main holdings table
                                    for tbl in all_holdings_soup.select('table'):
                                        if any(word in tbl.get_text().lower() for word in ['localització', 'signature', 'estat']):
                                            holdings_table = tbl
                                            break
                                except:
                                    pass  # Fallback to single holdings table

                    # Extract holdings from table
                    if holdings_table:
                        copies = []
                        for row in holdings_table.select('tr'):
                            cells = row.select('td')
                            if len(cells) < 3:
                                continue

                            location = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                            signature = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            status = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            notes = cells[3].get_text(strip=True) if len(cells) > 3 else ""

                            # Check if this is the library we want
                            match_name = library_name.split(".")[0].strip().lower()
                            if match_name in location.lower():
                                copies.append({
                                    "location": location,
                                    "signature": signature,
                                    "status": status,
                                    "notes": notes,
                                    "available": status.lower() == "disponible"
                                })

                        if copies:
                            # Extract clean title (remove author info)
                            title = text.split('/')[0].strip() if '/' in text else text
                            if title not in seen_titles and len(title) >= 5:
                                # Try to get cover image from detail page
                                cover_img = soup.select_one('img[src*="portadesbd.diba.cat"]')
                                cover_url = cover_img.get("src", "") if cover_img else None

                                book_data = {
                                    "title": title,
                                    "copies": copies
                                }
                                if cover_url:
                                    book_data["cover_url"] = cover_url
                                results.append(book_data)
                                seen_titles.add(title)

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
            "notes": notes,
            "available": status.lower() == "disponible"
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
