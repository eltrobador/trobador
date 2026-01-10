export default function Footer() {
  return (
    <footer className="mt-auto border-t border-zinc-200 bg-white py-6 dark:border-zinc-800 dark:bg-zinc-950">
      <div className="container mx-auto px-4">
        <div className="flex flex-col items-center gap-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
          <div>
            <p className="font-medium">Dades proporcionades pel Catàleg Aladí</p>
            <p className="mt-1">
              <a
                href="https://aladi.diba.cat"
                target="_blank"
                rel="noopener noreferrer"
                className="text-zinc-900 underline hover:text-zinc-700 dark:text-zinc-100 dark:hover:text-zinc-300"
              >
                Diputació de Barcelona
              </a>
            </p>
          </div>
          <div className="max-w-2xl">
            <p className="text-xs leading-relaxed">
              Aquest projecte no està afiliat amb ni aprovat per la Diputació de Barcelona (DIBA).
              Totes les dades bibliogràfiques provenen del catàleg públic Aladí i són propietat de la
              Diputació de Barcelona. La informació es proporciona únicament amb finalitats informatives.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
