from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/selfstudy")
def get_selfstudy():
    url = "https://api.cbsh.edu-set.com/selfstudy/search"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI4OWEyZWIyNi0xMGM1LTQ5NWEtOTU5MC0xZjlkYTQ5OTg1YjkiLCJpYXQiOjE3NjA1OTU0NjksImV4cCI6MTc2MDg1NDY2OX0.3k9YjybvHyNxK_wQeM6Oa3ANso4CkxKms4Zoc2vWfr0",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.49.0",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    data = {"date": "2025-10-19T00:00:00.000Z"}

    response = requests.post(url, headers=headers, json=data)
    json_data = response.json()

    results = []
    for item in json_data:
        student = item.get("student", {})
        grade = student.get("grade", 0)
        class_no = student.get("classNo", 0)
        number = student.get("number", 0)

        student_id = f"{grade}{class_no}{number:02d}"

        info = {
            "period": item.get("period", 0) or 0,
            "student_name": student.get("name", "이름없음") or "이름없음",
            "student_id": student_id,
            "room_name": item.get("room", {}).get("name", "방없음") or "방없음",
            "seat_name": item.get("seat", {}).get("name") if item.get("seat") else "없음"
        }
        results.append(info)

    results_sorted = sorted(results, key=lambda x: (
        x["period"],
        x["room_name"],
        x["seat_name"]
    ))

    return results_sorted
