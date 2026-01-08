# uraha-m1

## Assumptions
- Python 3.10+ is available.
- Poetry is installed.

## Setup
```bash
poetry install
```

## Run
```bash
poetry run python wsgi.py
```

Open http://localhost:5000/ to see the home page.

## Project layout
```
app/
  __init__.py        # app factory
  config.py          # minimal config
  templates/
    base.html
    home.html
wsgi.py              # entrypoint
```
