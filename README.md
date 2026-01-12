# Trobador

Cerca al catàleg Aladí - la xarxa de biblioteques de la Diputació de Barcelona (XBM - Xarxa de Biblioteques Municipals).

## Característiques

- Cercar llibres per autor a qualsevol biblioteca de la xarxa
- Cerca dinàmica de biblioteques (245+ biblioteques)
- Estat de disponibilitat en temps real

## Instal·lació

```bash
pip install -r requirements.txt
```

## Ús

```bash
python aladi_search.py "<autor>" "<biblioteca>"
```

### Exemples

```bash
# Cercar per nom parcial de biblioteca
python aladi_search.py "Irene Solà" "moià"

# Cercar amb nom complet de biblioteca
python aladi_search.py "Irene Solà" "1 d'Octubre Moià"

# Una altra biblioteca
python aladi_search.py "Maria Mercè Marçal" "Vic"
```

## Sortida

```
Searching for 'Irene Solà' at Moià. Municipal 1 d'octubre (gmo1)...

📚 Canto jo i la muntanya balla
   ✗ VENÇ EL 19-01-26
   ✗ VENÇ EL 22-01-26

📚 Et vaig donar ulls i vas mirar les tenebres
   ✓ Disponible
   ✓ Disponible
```

## Font de dades

Aquesta eina consulta el catàleg públic [Aladí](https://aladi.diba.cat/) de la xarxa de biblioteques de la Diputació de Barcelona.

### Atribució i Avís Legal

Aquest projecte no està afiliat ni és endossat per la Diputació de Barcelona (DIBA). Totes les dades bibliogràfiques provenen del catàleg públic d'Aladí i són propietat de la Diputació de Barcelona.

**Font de dades:** Catàleg Aladí - Diputació de Barcelona
**URL:** https://aladi.diba.cat

La informació bibliogràfica proporcionada mitjançant aquesta eina és dada pública de la xarxa de biblioteques municipals (Xarxa de Biblioteques Municipals - XBM). Aquest projecte no fa reclamacions sobre la propietat de les dades i les proporciona només amb fins informatius.
