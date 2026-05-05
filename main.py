from fastapi import FastAPI, HTTPException
import requests
from mir_api import MirRestApi
import math
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MiR100 Control Center")

ROBOT_IP = "192.168.12.20" 
mir = MirRestApi(os.getenv("USERNAME"), os.getenv("PASSWORD"), ROBOT_IP)

@app.get("/")
def home():
    return {"message": "Welcome Ali! Robot Control is Ready"}

@app.get("/robot/status")
def get_status():
    code, data = mir.status_get()
    if code == 200:
        return {
            "battery": f"{data.get('battery_percentage')}%",
            "state": data.get('state_text'),
            "is_charging": data.get('is_charging')
        }
    return {"error": "Cannot reach robot", "details": data}

@app.post("/robot/pause")
def pause():
    code, data = mir.set_state(4)
    return {"status": "Paused" if code == 200 else "Error", "details": data}

@app.post("/robot/resume")
def resume():
    code, data = mir.set_state(3)
    return {"status": "Ready" if code == 200 else "Error", "details": data}


# תוסיף את אלו מתחת ל-resume() ב-app.py
#add move endpoints
@app.post("/robot/move/forward")
def move_forward():
    # נסיעה של 5 ס"מ קדימה
    code, data = mir.move_relative(distance_m=0.05)
    return {"status": "Moving Forward", "code": code, "details": data}

@app.post("/robot/move/backward")
def move_backward():
    # נסיעה של 5 ס"מ אחורה
    code, data = mir.move_relative(distance_m=-0.05)
    return {"status": "Moving Backward", "code": code, "details": data}

@app.post("/robot/move/turn_left")
def turn_left():
    # סיבוב של 45 מעלות שמאלה
    code, data = mir.move_relative(rotation_deg=45)
    return {"status": "Turning Left", "code": code, "details": data}

@app.post("/robot/move/turn_right")
def turn_right():
    # סיבוב של 45 מעלות ימינה
    code, data = mir.move_relative(rotation_deg=-45)
    return {"status": "Turning Right", "code": code, "details": data}