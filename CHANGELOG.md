# Changelog: GardenFlow

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.6] - 2026-07-29

### Security

- The release workflow no longer grants `contents: write` for its whole run. The permission moves to the one job that publishes the release, and everything else runs with `contents: read`. OpenSSF Scorecard scores the Token-Permissions check 0 out of 10 whenever any workflow holds a top-level write permission, regardless of how little of the run needs it, so this single line was what held the check at zero.

---

## [1.0.5] - 2026-07-29

### Added

- `.github/workflows/release.yml`. Pushing a version tag produced nothing here: the tag landed in the repository and no release was ever created, which is how several versions ended up tagged but unreleased. The gap only showed when the tag list was compared against the release list. Release notes are taken from the matching `CHANGELOG.md` section, so they are not maintained separately from the file.

---

## [1.0.4] - 2026-07-29

### Changed

Dependency and workflow updates merged since 1.0.3:

- chore(ci): bump the actions group across 1 directory with 4 updates

---

## [1.0.3] - 2026-07-28

### Changed

- CodeQL moved from GitHub's default setup to an advanced setup with a committed `.github/workflows/codeql.yml`. The default setup skips pull requests that touch no code of a given language, so a dependency pull request changing only a lock file reported `skipping` on the required `Analyze (...)` checks forever and could never be merged. The workflow runs on every pull request regardless of what changed and uses the `security-extended` query suite, which the default setup does not allow choosing. Required checks are unchanged.
- The CodeQL job requests only `security-events: write` beyond the workflow-level `contents: read`. Repeating read grants at job level is what OpenSSF Scorecard counts as excessive token permissions, and it costs the full `Token-Permissions` score.
- Dependabot now groups only minor and patch updates per ecosystem; majors arrive as individual pull requests. The previous grouping bundled breaking changes with urgently needed security patches into one unreviewable diff. Actions stay grouped wholesale. Follows `engineering-standards` v0.11.0.

## [1.0.2] - 2026-07-28

### Added

- `.github/dependabot.yml`, with grouped weekly updates. The file was missing, and without it there are no version updates at all: repository security alerts only fire for disclosed vulnerabilities, which is how action pins across this portfolio quietly went stale. Follows `engineering-standards` v0.10.0.

### Fixed

- 3 action references used a mutable version tag rather than a commit SHA. A tag can be moved to point at different code after the fact without the workflow file changing; a SHA cannot. All are now pinned, with the version in the comment, per `standards/ci-cd.md` section 2. Pinned at the version that was actually running rather than upgraded, so any major bump arrives as its own reviewable Dependabot PR.
- `actions/checkout` pins now carry the full version in the comment instead of a bare major, and all workflows use the same SHA.

## [1.0.1] - 2026-07-20

### Changed

- OpenSSF Scorecard workflow and badge.
- `copilot-instructions.md` for consistent AI-assisted contributions.
- Initial pytest suite for the FastAPI backend (main/database/config, 24 tests) with coverage reporting in CI.
- Unified the EN/DE language-switch link format.
- Split the README's security/CI badges onto their own line, separate from the platform/tech/AI badges (they were rendering as a single merged line).

## [1.0.0] - 2026-07-17

First stable release: CI now actually builds and boots the full
`docker compose up` stack described in the README and verifies the
backend responds, turning "should work" into a tested guarantee. That
real, tested, installable distribution is the prerequisite for a 1.0
release per this portfolio's own SemVer discipline.

### Added
- CI job (`docker-smoke-test`) that runs `docker compose up --build` and confirms the backend responds, verifying the documented Quick Start actually works end to end.

## [0.1.11] - 2026-07-17

### Changed
- CI: added an explicit `permissions: contents: read` block to the workflow(s) that were missing one (CodeQL `actions/missing-workflow-permissions`), narrowing the default GITHUB_TOKEN scope.

## [0.1.10] (2026-07-12)

### Fixed

- Removed em-dashes/en-dashes from GETTING_STARTED.md (Swiss German orthography rule).

## [0.1.9] (2026-07-11)

### Added

- Documented Dual-Licensing assessment (Community-only) in ROADMAP.md.

## [0.1.8] (2026-07-11)

### Fixed

- Updated actions/setup-python to its latest major version in CI, since GitHub is deprecating the Node.js 20 runtime and the previous version was being forced onto Node 24 and crashing during post-run cleanup.

## [0.1.7] (2026-07-10)

### Fixed

- Removed a duplicate "New here? -> beginners guide" callout from README.md (was shown twice)

### Added

- Added the "New here?" beginner guide callout to README.de.md (was missing)

## [0.1.6] (2026-07-08)

### Fixed
- The WebSocket endpoint (`/ws`) returned HTTP 500 on every connection attempt: `app.mount("/", StaticFiles(...))` was registered before `@app.websocket("/ws")`, so the root-mounted static files catch-all intercepted the handshake before the dedicated route could match (`StaticFiles` only handles the ASGI `http` scope, not `websocket`, so it hit an `assert scope["type"] == "http"` and crashed). The dashboard always showed "Disconnected" and never received a single live push update; verified live with the fix, the badge now shows "Live" and charts update in real time
- Chart.js instances were stored in `charts: {}` inside Alpine.js's reactive `x-data`, so every sensor update triggered Alpine to deep-proxy-wrap a Chart.js object graph full of circular internal references, throwing `RangeError: Maximum call stack size exceeded` in the browser console on nearly every page interaction, including the language toggle appearing to silently do nothing. Moved the charts map outside Alpine's reactive state entirely
- CI's import check (`python -c "import main" 2>/dev/null || true`) could never fail regardless of the actual import result; removed the silencing so a broken import actually fails the build
- Corrected `ARCHITECTURE.md`'s file tree, MQTT topic convention, and mosquitto config path to match the real `backend/` package layout (it previously described flat files like `mqtt_client.py`/`rule_engine.py`/`db.py` and a bundled ESP32 firmware directory, none of which exist)
- Corrected `CONTRIBUTING.md`, which referenced a nonexistent `pyproject.toml`/`pip install -e ".[dev]"` and a `pytest` suite that doesn't exist
- Fixed em-dashes across documentation, `tools/test_sensor.py`, `backend/mqtt/client.py`, and `frontend/index.html`
- Removed stale `SKELETON.md`/`TEMPLATE_NOTES.md` scaffolding bookkeeping
- Fixed the FastAPI app's reported `version` claiming `1.0.0` while the repository's actual tags were at `v0.1.5`

## [0.1.1] (2026-07-07)

### Fixed
- MQTT subscriber never received messages on `aiomqtt>=2.3.0` (`client.messages()` was called as the old callable API instead of the current `client.messages` async iterator), so sensor data never reached the dashboard
- Every database call opened a connection twice (`async with await get_db()`), crashing with `RuntimeError: threads can only be started once` on rules/actuator endpoints
- Dashboard showed no sensor data after a page reload: the frontend only listened for live WebSocket events and never fetched current values via `/api/sensors` on load

## [0.1.0] (2026-06-15)

### Added
- MQTT broker integration (Mosquitto) for sensor/actuator communication
- Sensor data ingestion pipeline with SQLite storage
- Automation rule engine (condition-action rules)
- ESP32 and Zigbee sensor support
- Real-time web dashboard (FastAPI + WebSocket)
- Docker Compose deployment (Mosquitto + backend + frontend)
