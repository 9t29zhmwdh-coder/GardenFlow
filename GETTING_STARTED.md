# Getting Started with GardenFlow

This guide is for people with **no coding experience**. It walks you through every step, from opening a terminal to seeing your GardenFlow dashboard in the browser.

GardenFlow runs inside [Docker](https://www.docker.com/), a small tool that packages the whole app (server, database, MQTT broker) so it runs the same way on every computer. You do not need to install Python, a database, or anything else by hand.

> The commands below are the same on every platform once your terminal is open. Skip to the section for your operating system.

---

## Windows

### 1. Open a terminal

Right-click the **Start** button and choose **Terminal** (or **Windows PowerShell** on older Windows versions).

### 2. Check whether Docker is installed

Type:

```powershell
docker --version
docker compose version
```

Press Enter after each line.

- If you see version numbers (e.g. `Docker version 27.0.3`), Docker is ready. Continue to step 3.
- If you see `'docker' is not recognized as the name of a cmdlet...`, Docker Desktop is not installed yet.

**Install Docker Desktop:**

1. Download it from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Run the installer and accept the defaults. It will ask to enable **WSL2**: accept this, Docker Desktop needs it on Windows.
3. Restart your computer if prompted.
4. Start **Docker Desktop** from the Start menu and wait until it says "Docker Desktop is running" (whale icon in the system tray, bottom right).
5. Go back to your terminal and re-run the two commands above.

### 3. Download GardenFlow

The easiest way, no Git required:

1. Go to [github.com/9t29zhmwdh-coder/GardenFlow](https://github.com/9t29zhmwdh-coder/GardenFlow).
2. Click the green **Code** button → **Download ZIP**.
3. Extract the ZIP (right-click → **Extract All...**) somewhere you'll find it again, e.g. `Documents\GardenFlow`.

Alternative, if you already have Git installed:

```powershell
git clone https://github.com/9t29zhmwdh-coder/GardenFlow
```

### 4. Move into the folder

In your terminal:

```powershell
cd Documents\GardenFlow
```

(Adjust the path if you extracted it somewhere else. Tip: type `cd ` with a trailing space, then drag the folder from File Explorer into the terminal window to auto-fill the path.)

### 5. Create your configuration file

GardenFlow reads its settings from a file called `.env`. A template is included:

```powershell
copy .env.example .env
```

The defaults work out of the box for trying GardenFlow locally; no editing required for a first run.

### 6. Start GardenFlow

```powershell
docker compose up -d
```

The first run downloads everything Docker needs, this can take a few minutes depending on your internet connection. Subsequent starts are much faster.

### 7. Open the dashboard

Open your browser and go to:

```
http://localhost:8000
```

You should see the GardenFlow dashboard. Since no real sensors are connected yet, charts will be empty; see "What you should see" below for how to simulate sensor data.

---

## Linux

### 1. Open a terminal

This depends on your desktop environment: usually `Ctrl+Alt+T`, or search for "Terminal" in your application menu.

### 2. Check whether Docker is installed

```bash
docker --version
docker compose version
```

- If you see version numbers, continue to step 3.
- If you see `command not found`, install Docker using your distribution's package manager. Follow the official guide for your distro at [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) (e.g. Ubuntu: `docs.docker.com/engine/install/ubuntu`). Debian/Ubuntu-based systems can typically use:

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in after the last command so your user can run Docker without `sudo`.

### 3. Download GardenFlow

No-Git route: download the ZIP from [github.com/9t29zhmwdh-coder/GardenFlow](https://github.com/9t29zhmwdh-coder/GardenFlow) (green **Code** button → **Download ZIP**) and extract it.

Or, with Git:

```bash
git clone https://github.com/9t29zhmwdh-coder/GardenFlow
cd GardenFlow
```

### 4. Create your configuration file

```bash
cp .env.example .env
```

### 5. Start GardenFlow

```bash
docker compose up -d
```

### 6. Open the dashboard

Go to `http://localhost:8000` in your browser.

---

## macOS

### 1. Open a terminal

Press `Cmd+Space` to open Spotlight, type `Terminal`, and press Enter.

### 2. Check whether Docker is installed

```bash
docker --version
docker compose version
```

- Version numbers shown → continue to step 3.
- `command not found` → install **Docker Desktop for Mac**:

1. Download it from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) (choose Apple Silicon or Intel, matching your Mac).
2. Drag Docker to Applications and launch it.
3. Wait for the whale icon in the menu bar to show Docker is running.
4. Re-run the commands above in your terminal.

### 3. Download GardenFlow

No-Git route: download the ZIP from [github.com/9t29zhmwdh-coder/GardenFlow](https://github.com/9t29zhmwdh-coder/GardenFlow) (green **Code** button → **Download ZIP**) and extract it (double-click the ZIP in Finder).

Or, with Git:

```bash
git clone https://github.com/9t29zhmwdh-coder/GardenFlow
cd GardenFlow
```

### 4. Create your configuration file

```bash
cp .env.example .env
```

### 5. Start GardenFlow

```bash
docker compose up -d
```

### 6. Open the dashboard

Go to `http://localhost:8000` in your browser.

<!-- TODO: Screenshot of the dashboard right after first start -->

---

## What you should see

After `docker compose up -d` finishes, three containers are running in the background (the app, the database, and an MQTT broker). The dashboard at `http://localhost:8000` loads with an empty set of charts, because no real sensors are connected yet.

To see live data without real hardware, run the included simulator (requires Python on your machine):

```bash
pip install aiomqtt
python tools/test_sensor.py
```

You'll then see simulated sensor readings appear on the dashboard in real time.

To stop GardenFlow later:

```bash
docker compose down
```

---

## A note for advanced users

If you already have Python 3.12+ installed and prefer to run GardenFlow without Docker for local development, see the "Local Development (no Docker)" section in the main [README.md](README.md). This is not recommended for a first try; Docker is the simpler path.

---

### Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `'docker' is not recognized...` (Windows) or `command not found: docker` (Linux/macOS) | Docker isn't installed, or your terminal was opened before installing it | Install Docker Desktop (Windows/macOS) or your distro's Docker package (Linux), then open a **new** terminal window |
| Docker commands hang or fail with "Cannot connect to the Docker daemon" | Docker Desktop / the Docker service isn't running | Windows/macOS: open Docker Desktop and wait for the whale icon to say "running". Linux: `sudo systemctl start docker` |
| Windows: WSL2-related error when starting Docker Desktop | WSL2 is not installed or outdated | Open PowerShell as Administrator and run `wsl --install`, then restart your computer |
| `docker compose up -d` fails with "port is already allocated" | Something else on your machine is already using port 8000 or 1883 | Stop the other program, or edit `APP_PORT` in your `.env` file and restart with `docker compose up -d` |
| Dashboard loads but shows no data | No sensors (real or simulated) are sending data yet | Run the simulator described in "What you should see" above |
