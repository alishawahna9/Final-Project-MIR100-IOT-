from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import requests
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# ייבוא המחלקה מהקובץ השני!
from mir_api import MirRestApi

app = FastAPI(title="MiR100 Control Center", docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="MiR100 Control Center",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROBOT_IP = "192.168.12.20"
mir = MirRestApi(os.getenv("ROBOT_USERNAME"), os.getenv("ROBOT_PASSWORD"), ROBOT_IP)

@app.get("/")
def home():
    return {"message": "MiR100 API is Online", "robot_ip": ROBOT_IP}

@app.get("/robot/status")
def get_status():
    code, data = mir.status_get()
    if code == 200:
        return {
            "battery": f"{data.get('battery_percentage')}%",
            "state": data.get('state_text'),
            "is_charging": data.get('is_charging'),
            "mode": data.get('mode_text')
        }
    raise HTTPException(status_code=code, detail=data)

@app.post("/robot/pause")
def pause():
    code, data = mir.set_state(4)
    return {"status": "Paused", "code": code}

@app.post("/robot/resume")
def resume():
    code, data = mir.set_state(3)
    return {"status": "Ready", "code": code}

@app.get("/robot/missions")
def list_missions():
    code, data = mir.handle_request("GET", "missions")
    if code == 200:
        return data
    raise HTTPException(status_code=code, detail=data)

@app.get("/robot/queue")
def get_queue():
    code, data = mir.handle_request("GET", "mission_queue")
    if code == 200:
        return data
    raise HTTPException(status_code=code, detail=data)

@app.post("/robot/move/step")
def move_robot_step():
    GROUP_ID = "mirconst-guid-0000-0011-missiongroup"
    
    code, mission = mir.missions_post("API_Move_Task", GROUP_ID)
    if code != 201:
        raise HTTPException(status_code=code, detail=mission)
    
    m_guid = mission.get("guid")
    
    params = [
        {"id": "x", "value": 0.5},
        {"id": "y", "value": 0.0},
        {"id": "orientation", "value": 0.0},
        {"id": "max_linear_speed", "value": 0.1},
        {"id": "max_angular_speed", "value": 0.2},
        {"id": "collision_detection", "value": True}
    ]
    
    code_act, action = mir.mission_actions_post(m_guid, "relative_move", params)
    if code_act != 201:
        return {"error": "Step 2 failed", "robot_response": action}
    
    code_q, queue = mir.mission_queue_post(m_guid)
    if code_q != 201:
        return {"error": "Step 3 failed", "robot_response": queue}
        
    return {"status": "Success", "guid": m_guid}

@app.post("/robot/move/forward")
def move_forward(): return _move(x=0.3, y=0.0, orientation=0.0)

@app.post("/robot/move/backward")
def move_backward(): return _move(x=-0.3, y=0.0, orientation=0.0)

@app.post("/robot/move/turn-left")
def turn_left(): return _move(x=0.0, y=0.0, orientation=45.0)

@app.post("/robot/move/turn-right")
def turn_right(): return _move(x=0.0, y=0.0, orientation=-45.0)

def _move(x, y, orientation):
    GROUP_ID = "mirconst-guid-0000-0011-missiongroup"
    code, mission = mir.missions_post("move_cmd", GROUP_ID)
    if code != 201:
        raise HTTPException(status_code=code, detail=mission)
    guid = mission.get("guid")
    params = [
        {"id": "x", "value": x},
        {"id": "y", "value": y},
        {"id": "orientation", "value": orientation},
        {"id": "max_linear_speed", "value": 0.1},
        {"id": "max_angular_speed", "value": 0.2},
        {"id": "collision_detection", "value": True}
    ]
    mir.mission_actions_post(guid, "relative_move", params)
    mir.mission_queue_post(guid)
    return {"status": "ok"}

@app.get("/robot/maps")
def list_maps():
    code, data = mir.maps_get()
    if code == 200:
        return data
    raise HTTPException(status_code=code, detail=data)

@app.get("/robot/maps/{map_guid}/image")
def get_map_image(map_guid: str):
    status_code, response_data = mir.map_image_get(map_guid)
    if status_code == 200:
        return Response(content=response_data, media_type="image/png")
    raise HTTPException(status_code=status_code, detail="Failed to fetch map image from robot")