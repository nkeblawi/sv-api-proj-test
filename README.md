# Teleconnection Forecast Plotter

[![Build status](https://img.shields.io/github/actions/workflow/status/nkeblawi/sv-api-proj-test/main.yml?branch=main)](https://github.com/nkeblawi/sv-api-proj-test/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/nkeblawi/sv-api-proj-test/branch/main/graph/badge.svg)](https://codecov.io/gh/nkeblawi/sv-api-proj-test)
[![Release](https://img.shields.io/github/v/release/nkeblawi/sv-api-proj-test)](https://github.com/nkeblawi/sv-api-proj-test/releases)
[![License](https://img.shields.io/github/license/nkeblawi/sv-api-proj-test)](LICENSE)

A web application for visualizing atmospheric **teleconnection index forecasts** (PNA, NAO, EPO) from major weather models (GFS, GEFS, ECMWF, EPS). The app fetches daily forecast CSV data from the StormVista API and renders it as a time-series plot.

The project ships **two interface implementations** backed by the same data-fetching logic:

| Interface | Entry point | Stack |
|---|---|---|
| Flask web app | `test_app.py` | Flask + Jinja2 templates + matplotlib (PNG embedded as base64) |
| Streamlit app | `app.py` | Streamlit + matplotlib (inline figure) |

---

## What Are Teleconnection Indices?

Teleconnections are large-scale atmospheric pressure patterns that influence weather across entire continents. The three indices supported here are:

- **PNA** (Pacific–North American) — represents ridge/trough patterns over North America
- **NAO** (North Atlantic Oscillation) — represents storminess and temperatures across Europe and eastern North America
- **EPO** (East Pacific Oscillation) — represents ridging/troughing over Alaska that influences temperature and precipitation on the US West Coast

Positive and negative phases of each index have distinct, well-documented downstream weather impacts.

---

## Project Structure

```
sv-api-proj-test/
├── app.py                  # Streamlit interface (imports pull_data from test_app.py)
├── test_app.py             # Flask interface + shared pull_data / plot_data functions
├── templates/
│   └── index.html          # Jinja2 form and plot display for Flask
├── static/
│   └── css/
│       └── styles.css      # Stylesheet for the Flask UI
├── requirements.txt        # Pinned runtime dependencies
├── pyproject.toml          # Project metadata, tool config (ruff, mypy, pytest)
├── tox.ini                 # Multi-Python test matrix (py3.8–3.12)
├── Makefile                # Developer workflow shortcuts
├── .pre-commit-config.yaml # Pre-commit hooks (ruff, prettier, standard checks)
└── CONTRIBUTING.md         # Contribution guide
```

---

## Prerequisites

- Python 3.8–3.12
- [`uv`](https://github.com/astral-sh/uv) package manager
- SV API credentials (key, base URL, API version)

---

## Setup

```bash
make install
```

This runs `uv sync` to create the virtual environment and install all dependencies, then installs the pre-commit hooks.

### Environment variables

Create a `.env` file (for Flask) or a Streamlit `secrets.toml` (for Streamlit) with:

```
SV_API_KEY=<your_api_key>
SV_URL=<api_base_url>          # e.g. api.synopticdata.com
SV_API_VERSION=<version>       # e.g. v2
```

The Flask app loads these via `python-dotenv`. The Streamlit app reads them from `st.secrets`.

---

## Running the App

### Flask

```bash
uv run python test_app.py
```

Open `http://localhost:5000` in a browser. Use the form to select model(s), model run, teleconnection index, and date, then click **Plot**.

### Streamlit

```bash
uv run streamlit run app.py
```

Open `http://localhost:8501`. The Streamlit UI exposes the same controls via native widgets.

---

## How It Works

1. The user selects one or more models (GFS, GEFS, ECMWF, EPS), a model run (00z / 06z / 12z / 18z), a teleconnection index, and a date.
2. `pull_data()` constructs a request URL per model and fetches a CSV from the SV API:
   ```
   /{version}/model-data/{model}/{date}/{run}/teleconnection/{index}-forecast.csv?apikey=...
   ```
3. The CSV rows are parsed into a DataFrame. For ensemble models (GEFS, EPS), ensemble member values are averaged by forecast hour to produce a single mean trace.
4. `plot_data()` (Flask) or inline matplotlib code (Streamlit) renders a line chart with hour on the x-axis and daily index value on the y-axis, with a dashed zero line for reference.
5. Flask encodes the figure as base64 and embeds it in the HTML response. Streamlit passes the `Figure` object directly to `st.pyplot()`.

---

## Development

### Code quality

```bash
make check        # lock-file validation + pre-commit linting + mypy
make test         # pytest with doctest support
```

### Pre-commit hooks (run automatically on `git commit`)

| Hook | Purpose |
|---|---|
| `pre-commit-hooks` | Conflict markers, TOML/YAML validation, trailing whitespace |
| `ruff` | Python linting (flake8-style rules + isort) |
| `ruff-format` | Python auto-formatting |
| `prettier` | HTML/CSS/YAML formatting |

### Multi-Python testing

```bash
tox               # runs pytest + mypy across Python 3.8–3.12
```

### Makefile targets

| Target | Description |
|---|---|
| `make install` | Set up venv and pre-commit hooks |
| `make check` | Lint and type-check |
| `make test` | Run test suite |
| `make build` | Build wheel distribution |
| `make clean-build` | Remove `dist/` artifacts |

---

## CI/CD

GitHub Actions runs on pull requests, merges to `main`, and new releases. The pipeline executes the full tox matrix (Python 3.8–3.12), uploads coverage to [Codecov](https://codecov.io/gh/nkeblawi/sv-api-proj-test), and can publish to PyPI on release.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. The short version: fork → branch → `make check` → `make test` → pull request.

---

Repository scaffolded with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
