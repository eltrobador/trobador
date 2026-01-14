"use client";

import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Copy {
  location: string;
  status: string;
  available: boolean;
}

interface Book {
  title: string;
  copies: Copy[];
  cover_url?: string;
}

interface SearchResult {
  author: string;
  library: {
    name: string;
    code: string;
  };
  books: Book[];
  error?: string;
}

function SearchContent() {
  const searchParams = useSearchParams();
  const author = searchParams.get("author");
  const library = searchParams.get("library");

  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!author || !library) {
      setError("Falten paràmetres de cerca");
      setLoading(false);
      return;
    }

    const fetchResults = async () => {
      try {
        const response = await fetch(
          `/api/search?author=${encodeURIComponent(author)}&library=${encodeURIComponent(library)}`
        );
        const data = await response.json();

        if (data.error) {
          setError(data.error);
        } else {
          setResult(data);
        }
      } catch {
        setError("Error en la connexió");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [author, library]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <p className="text-lg text-zinc-500">Cercant...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-zinc-50 p-4 dark:bg-zinc-950">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Link href="/">
            <Button variant="outline">← Nova cerca</Button>
          </Link>
        </div>

        {error ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-red-500">{error}</p>
            </CardContent>
          </Card>
        ) : result && result.books.length === 0 ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Cap resultat</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-zinc-500">
                No s&apos;han trobat llibres de <strong>{result.author}</strong> a{" "}
                <strong>{result.library.name}</strong>
              </p>
            </CardContent>
          </Card>
        ) : result ? (
          <>
            <div className="mb-6">
              <h1 className="text-2xl font-bold">{result.author}</h1>
              <p className="text-zinc-500">{result.library.name}</p>
            </div>

            <div className="flex flex-col gap-4">
              {result.books.map((book, index) => (
                <Card key={index}>
                  <CardContent className="flex gap-4 p-4">
                    {book.cover_url && (
                      <div className="shrink-0">
                        <Image
                          src={book.cover_url}
                          alt={`Portada de ${book.title}`}
                          width={80}
                          height={120}
                          className="rounded object-cover"
                          unoptimized
                        />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="mb-3 text-lg font-semibold">
                        {book.title}
                      </h3>
                      <p className="mb-2 text-sm font-medium text-zinc-500">
                        Còpies:
                      </p>
                      <ul className="flex flex-col gap-2">
                        {book.copies.map((copy, copyIndex) => (
                          <li
                            key={copyIndex}
                            className="flex items-center gap-2"
                          >
                            <span
                              className={`inline-block h-3 w-3 shrink-0 rounded-full ${
                                copy.available
                                  ? "bg-green-500"
                                  : "bg-red-500"
                              }`}
                            />
                            <span
                              className={
                                copy.available
                                  ? "text-green-700 dark:text-green-400"
                                  : "text-red-700 dark:text-red-400"
                              }
                            >
                              {copy.status}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-1 items-center justify-center bg-zinc-50 dark:bg-zinc-950">
          <p className="text-lg text-zinc-500">Carregant...</p>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
