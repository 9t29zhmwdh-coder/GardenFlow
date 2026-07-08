# Contributing to GardenFlow

## Getting Started

### Prerequisites

- Python 3.12+
- [Docker](https://docker.com) (optional)

### Setup

1. Fork the repository
2. `git clone https://github.com/YOUR_USERNAME/GardenFlow`
3. `cd GardenFlow`
4. `python -m venv .venv && source .venv/bin/activate`
5. `pip install -r backend/requirements.txt`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/xyz`
2. Make your changes
3. Run the app locally and verify your change (there is currently no automated test suite, see ROADMAP.md)
4. Run linter: `ruff check .` (if configured for your editor; not currently enforced in CI)
5. Commit: `git commit -m "[feat] description"`
6. Push and open a Pull Request

## Code Style

- Python: `ruff format .` + `ruff check .`
- Follow PEP 8

## Commit Convention

`[type] description`, where type is:
- `[feat]`: new feature
- `[fix]`: bug fix
- `[docs]`: documentation only
- `[refactor]`: code cleanup
- `[test]`: tests only

## Questions?

Open an issue or discussion on GitHub.
