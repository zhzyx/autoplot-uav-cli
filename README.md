# Autoplot UAV

[中文](README.zh.md)

KML mission planner for DJI drones. Generates KMZ waypoint mission files from plot boundary definitions and survey configurations.

## Setup

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

**Linux / macOS**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install

```bash
git clone https://github.com/zhzyx/autoplot-uav-cli.git
cd autoplot-uav-cli
uv sync
```

For development (includes Jupyter and pytest):

```bash
uv sync --extra dev
```

### Run

```bash
uv run survey --config mission_cfg/your_config.yaml
```

Or activate the virtual environment first:

**Linux / macOS**
```bash
source .venv/bin/activate
python survey_gen.py --config mission_cfg/your_config.yaml
```

**Windows (PowerShell)**
```powershell
.venv\Scripts\activate
python survey_gen.py --config mission_cfg/your_config.yaml
```

### Tests

```bash
uv run pytest
```

## Mission Config

Mission YAML files go in `mission_cfg/`. See existing configs for reference.

## Project Structure

```
src/
  kml/            # KMZ/KML generation
  task_planner/   # Grid planning and plot surveying
  cmd_tools/      # Coordinate conversion utilities
tests/
mission_cfg/      # Mission configuration YAMLs
```
