import code

import requests
import hashlib
import base64
import math

class MirRestApi:
    def __init__(self, usrname, password, ip="192.168.12.20"):
        self.url = f"http://{ip}/api/v2.0.0"
        print(usrname)
        print(password)
        self.header = {
            'Content-Type': 'application/json',

            'Authorization': self.generate_auth_head(usrname, password)
        }

    def generate_auth_head(self, usrname, password):
        hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
        auth_str = f"{usrname}:{hashed_pass}"
        encoded = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        return f"Basic {encoded}"

    def status_get(self):
        try:
            response = requests.get(f"{self.url}/status", headers=self.header, timeout=5)
            return response.status_code, response.json()
        except Exception as e:
            return 500, {"error": str(e)}

    def set_state(self, state_id):
        # 3 = Ready, 4 = Pause
        try:
            response = requests.put(f"{self.url}/status", 
                                    json={"state_id": state_id}, 
                                    headers=self.header)
            return response.status_code, response.json()
        except Exception as e:
            return 500, {"error": str(e)}
#add move method
def move_relative(self, distance_m=0.0, rotation_deg=0.0):
    """
    פונקציה אחת לכל סוגי התנועה היחסית:
    :param distance_m: מרחק במטרים (חיובי לקדימה, שלילי לאחורה)
    :param rotation_deg: זווית סיבוב (חיובי לשמאל, שלילי לימין)
    """
    try:
        # 1. קבלת המיקום הנוכחי מהרובוט
        code, status_data = self.status_get()
        if code != 200:
            return code, {"error": "Could not get robot status"}

        curr_x = status_data['position']['x']
        curr_y = status_data['position']['y']
        curr_ori = status_data['position']['orientation'] # בדרגות

        # 2. חישוב היעד החדש
        # המרה של הזווית הנוכחית לרדיאנים לצורך חישוב סינוס וקוסינוס
        rad = math.radians(curr_ori)
        
        # נוסחת התנועה במישור:
        new_x = curr_x + distance_m * math.cos(rad)
        new_y = curr_y + distance_m * math.sin(rad)
        new_ori = curr_ori + rotation_deg

        # 3. הכנת גוף הבקשה (Payload) לפי ה-Schema בעמ' 368
        # שים לב: אתה חייב להשתמש ב-Mission ID שמוגדר עם Dynamic Parameters ברובוט
        payload = {
            "mission_id": "YOUR_MOVE_MISSION_GUID", 
            "parameters": [
                {"input_name": "x", "value": new_x},
                {"input_name": "y", "value": new_y},
                {"input_name": "orientation", "value": new_ori}
            ]
        }

        # 4. שליחה לתור המשימות
        url = f"{self.url}/mission_queue"
        response = requests.post(url, json=payload, headers=self.header, timeout=5)
        return response.status_code, response.json()

    except Exception as e:
        return 500, {"error": str(e)}