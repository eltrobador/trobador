# Development Setup

## Create venv (if it doesn't exist)

```bash
uv venv --python 3.13 ./venv
```

## Activate venv and install dependencies

```bash
source venv/bin/activate
uv pip install -r requirements.txt
```

## Run CLI

```bash
python api/aladi.py "Irene Solà" "1 d'Octubre Moià"
```
