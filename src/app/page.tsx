"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PREFERRED_LIBRARY_KEY = "preferredLibrary";

export default function Home() {
  const router = useRouter();
  const [author, setAuthor] = useState("");
  const [library, setLibrary] = useState("");
  const [saveAsPreferred, setSaveAsPreferred] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(PREFERRED_LIBRARY_KEY);
    if (saved) {
      setLibrary(saved);
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (author && library) {
      if (saveAsPreferred) {
        localStorage.setItem(PREFERRED_LIBRARY_KEY, library);
      }
      router.push(`/search?author=${encodeURIComponent(author)}&library=${encodeURIComponent(library)}`);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 p-4 dark:bg-zinc-950">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">Trobador</CardTitle>
          <p className="text-zinc-500 dark:text-zinc-400">
            Cerca al catàleg de biblioteques de Barcelona
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label htmlFor="author" className="text-sm font-medium">
                Autor
              </label>
              <Input
                id="author"
                type="text"
                placeholder="Irene Solà"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <label htmlFor="library" className="text-sm font-medium">
                Biblioteca
              </label>
              <Input
                id="library"
                type="text"
                placeholder="1 d'Octubre Moià"
                value={library}
                onChange={(e) => setLibrary(e.target.value)}
                required
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="saveAsPreferred"
                checked={saveAsPreferred}
                onChange={(e) => setSaveAsPreferred(e.target.checked)}
              />
              <label htmlFor="saveAsPreferred" className="text-sm">
                Desa com a biblioteca preferida
              </label>
            </div>
            <Button type="submit" className="mt-2">
              Cercar
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
