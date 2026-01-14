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

## AWS Setup

### AWS Credentials
The project uses AWS Network MCP server with the profile `diffffff-production` and region `eu-west-1`.

To get temporary credentials, run:

```bash
aws --profile diffffff-production sso login
```

This will authenticate your session with AWS SSO and provide temporary credentials for the `diffffff-production` profile.
