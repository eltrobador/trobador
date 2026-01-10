# Trobador

Search the Aladí catalog - the library network of Diputació de Barcelona (XBM - Xarxa de Biblioteques Municipals).

## Features

- Search for books by author at any library in the network
- Dynamic library lookup (245+ libraries)
- Real-time availability status

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python aladi_search.py "<author>" "<library>"
```

### Examples

```bash
# Search by partial library name
python aladi_search.py "Irene Solà" "moià"

# Search with full library name
python aladi_search.py "Irene Solà" "1 d'Octubre Moià"

# Another library
python aladi_search.py "Maria Mercè Marçal" "Vic"
```

## Output

```
Searching for 'Irene Solà' at Moià. Municipal 1 d'octubre (gmo1)...

📚 Canto jo i la muntanya balla
   ✗ VENÇ EL 19-01-26
   ✗ VENÇ EL 22-01-26

📚 Et vaig donar ulls i vas mirar les tenebres
   ✓ Disponible
   ✓ Disponible
```

## Data Source

This tool queries the public [Aladí catalog](https://aladi.diba.cat/) of the Diputació de Barcelona library network.

### Attribution and Disclaimer

This project is not affiliated with or endorsed by the Diputació de Barcelona (DIBA). All bibliographic data is sourced from the public Aladí catalog and remains the property of the Diputació de Barcelona.

**Data source:** Catàleg Aladí - Diputació de Barcelona
**URL:** https://aladi.diba.cat

The bibliographic information provided through this tool is publicly available data from the municipal library network (Xarxa de Biblioteques Municipals - XBM). This project makes no claims of ownership over the data and provides it for informational purposes only.

## License

MIT (code only - does not apply to bibliographic data from DIBA)
