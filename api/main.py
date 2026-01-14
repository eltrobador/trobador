#!/usr/bin/env python3
"""
FastAPI backend for Trobador library search.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aladi import find_library_code, search_author_at_library, get_all_libraries

app = FastAPI(
    title="Trobador API",
    description="API for searching the Barcelona library network catalog",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Library(BaseModel):
    name: str
    code: str


class Copy(BaseModel):
    location: str
    signature: str
    status: str
    notes: str
    available: bool


class Book(BaseModel):
    title: str
    copies: list[Copy]
    cover_url: str | None = None


class SearchResponse(BaseModel):
    author: str
    library: Library
    books: list[Book]


class LibrariesResponse(BaseModel):
    count: int
    libraries: list[Library]


@app.get("/api/search", response_model=SearchResponse)
async def search(
    author: str = Query(..., description="Author name to search for"),
    library: str = Query(..., description="Library name or partial name"),
):
    """Search for books by an author at a specific library."""
    result = find_library_code(library)
    if not result:
        raise HTTPException(status_code=404, detail=f"Library not found: {library}")

    library_name, library_code = result
    books = search_author_at_library(author, library_name, library_code)

    return SearchResponse(
        author=author,
        library=Library(name=library_name, code=library_code),
        books=[
            Book(
                title=book["title"],
                copies=[Copy(**copy) for copy in book["copies"]],
                cover_url=book.get("cover_url"),
            )
            for book in books
        ],
    )


@app.get("/api/libraries", response_model=LibrariesResponse)
async def list_libraries():
    """Get all available libraries."""
    libraries = get_all_libraries()
    result = [Library(name=name, code=code) for name, code in libraries.items()]
    return LibrariesResponse(count=len(result), libraries=result)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
