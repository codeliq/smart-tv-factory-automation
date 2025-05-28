import requests
import json
import random
import time
from datetime import datetime

URL = "http://localhost:3001/update-status"

def generate_mock_data():
    angles = [random.randint(-180, 180) for _ in range(4)]

    position = {
        "x": random.randint(100, 300),
        "y": random.randint(100, 300),
        "z": random.randint(30, 100)
    }

    picked = random.choice(["blue", "white", "red"])
    color = random.choice(["blue", "white", "red"])
    defective = color == "red" and random.random() < 0.7
    signal = random.randint(1, 3)
    current_job = random.choice(["픽업", "이동", "분류"])

    return {
        "timestamp": datetime.now().isoformat(),
        "angles": angles,
        "position": position,
        "picked": picked,
        "recognized": {
            "color": color,
            "defective": defective
        },
        "signal": signal,
        "currentJob": current_job
    }

def send_loop():
    while True:
        data = generate_mock_data()
        try:
            res = requests.post(URL, json=data)
            print(f"[전송 완료] {res.status_code} | 각도: {data['angles']} | 작업: {data['currentJob']}")
        except Exception as e:
            print("[전송 실패]", e)

        time.sleep(4)

if __name__ == "__main__":
    send_loop()
