import requests
import hashlib
import base64

class MirRestApi:
    def __init__(self, username, password, ip="192.168.12.20"):
        self.url = f"http://{ip}/api/v2.0.0"
        self.header = {
            'Content-Type': 'application/json',
            'Authorization': self.generate_auth_head(username, password)
        }

    def generate_auth_head(self, username, password):
        hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
        auth_str = f"{username}:{hashed_pass}"
        encoded = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        return f"Basic {encoded}"

    def handle_request(self, method, endpoint, data=None):
        url = f"{self.url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.header,
                json=data,
                timeout=5
            )
            
            if "image" in response.headers.get("Content-Type", ""):
                return response.status_code, response.content
                
            if "application/json" in response.headers.get("Content-Type", ""):
                return response.status_code, response.json()
                
            return response.status_code, {"text": response.text}
        except Exception as e:
            return 500, {"error": str(e)}

    def status_get(self):
        return self.handle_request("GET", "status")

    def set_state(self, state_id):
        return self.handle_request("PUT", "status", {"state_id": state_id})

    def missions_post(self, name, group_id):
        payload = {"name": name, "group_id": group_id}
        return self.handle_request("POST", "missions", payload)

    def mission_actions_post(self, mission_id, action_type, parameters):
        payload = {"action_type": action_type, "parameters": parameters, "priority": 1}
        return self.handle_request("POST", f"missions/{mission_id}/actions", payload)

    def mission_queue_post(self, mission_id):
        return self.handle_request("POST", "mission_queue", {"mission_id": mission_id})

    def maps_get(self):
        return self.handle_request("GET", "maps")

    def map_image_get(self, map_guid):
        code, data = self.handle_request("GET", f"maps/{map_guid}")
        if code != 200:
            return code, data
    
        map_b64 = data.get("map")
        if not map_b64:
            return 404, {"error": "map field not found in robot response"}

        image_bytes = base64.b64decode(map_b64)
        return 200, image_bytes