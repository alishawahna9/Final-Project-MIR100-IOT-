# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project with two independent components:
1. A **FastAPI server** (`main.py` + `mir_api.py`) that acts as a REST control layer for a MiR100 autonomous mobile robot.
2. A **standalone IoT visualization script** (`iot.py`) that reads MQTT message dumps and plots sensor data using matplotlib.

## Running the Server

```powershell
# Activate the virtual environment first
.\venv\Scripts\activate

# Start the FastAPI server
uvicorn main:app --reload
```

The server starts at `http://127.0.0.1:8000`. Interactive Swagger UI is at `/docs` (served from local `static/` files — no internet required).

## Architecture

### FastAPI Layer (`main.py`)
Thin HTTP API that maps REST endpoints to `MirRestApi` calls. Robot IP and credentials are hardcoded at the top of the file:
- `ROBOT_IP = "192.168.12.20"`
- Credentials: `MirRestApi("Distributor", "distributor", ROBOT_IP)`

A `.env` file (gitignored) exists at the project root with `USERNAME` and `PASSWORD` keys, and `python-dotenv` is installed in the venv — but `load_dotenv()` is not currently called.

The Swagger UI is served from local static files to avoid CDN dependency on the robot's network:
```python
app = FastAPI(title="MiR100 Control Center", docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
# /docs returns get_swagger_ui_html(...) pointing to /static/swagger-ui-bundle.js and /static/swagger-ui.css
```

Every directional move command goes through the shared `_move(x, y, orientation)` helper: create mission → add `relative_move` action → post to queue. The `/robot/move/step` endpoint does the same three steps inline with `x=0.5` and mission name `API_Move_Task` (vs `move_cmd` used by `_move`).

The mission group ID used in **all** move operations (both `_move` and `/robot/move/step`) is:
```
mirconst-guid-0000-0011-missiongroup
```

### MiR REST Client (`mir_api.py`)
`MirRestApi` wraps the robot's REST API at `http://{ip}/api/v2.0.0`. Auth is constructed in `generate_auth_head`: the password is SHA-256 hashed, combined with the username as `user:hash`, then Base64-encoded as a Basic auth header.

`handle_request` is the central dispatcher — it detects the response `Content-Type` and returns either raw bytes (for images) or parsed JSON. All requests use a 5-second timeout.

Key constants:
- Robot state IDs: `3` = Ready, `4` = Paused
- Movement action type: `relative_move` (params: `x`, `y`, `orientation`, `max_linear_speed`, `max_angular_speed`, `collision_detection`)

Map images are stored base64-encoded in the `"map"` field of the map object (not `"base_map"`); `map_image_get` decodes them to raw PNG bytes.

### MiR Robot — Valid Action Types
The robot only understands these exact `action_type` string values (used in `mission_actions_post`):

```
prompt_user, move, wait_for_plc_register, connect_bluetooth, sound_stop,
set_reset_plc, adjust_localization, switch_map, if, pause, docking,
reduce_protective_fields, create_autolog, relative_move, pickup_cart,
wait_for_fleet, place_cart, planner_settings, charging, set_io, return,
check_pose, set_reset_io, set_plc_register, throw_error, wait, sound,
break, move_to_position, disconnect_bluetooth, run_ur_program, light,
try_catch, email, while, continue, wait_for_io, set_footprint, loop
```

Currently the codebase only uses `relative_move`. Any new movement or automation feature must use one of the names above — the robot will reject any other value.

### IoT Script (`iot.py`)
Standalone script — not part of the server. Reads a JSON export of MQTT messages from a hardcoded path (`C:\Users\alish\Downloads\All connections (1).json`) and renders three matplotlib subplots (temperature, humidity, pressure). Topics: `braude/team1/temperature`, `braude/team1/temp`, `braude/team1/humidity`, `braude/team1/pressure`.

## Dependencies

All dependencies are installed in `venv/`. Key packages:
- `fastapi`, `uvicorn` — web server
- `requests` — HTTP client for robot communication
- `python-dotenv` — available for credential externalization (not yet wired)
- `matplotlib` — IoT data plotting
