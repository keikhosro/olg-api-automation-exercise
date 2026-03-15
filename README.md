# API Automation Exercise

## Prerequisites

- Docker
- Python 3.10+

## Setup

```bash
# 1. Copy .env.example to .env
cp .env.example .env

# 2. Start WireMock
docker compose up -d

# 3. Create/activate a venv and install the dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Tests

```bash
pytest tests/ -v
```
