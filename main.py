from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime, timedelta
import base64
import json
import time
from selenium.webdriver.common.by import By
from seleniumbase import SB
from dotenv import load_dotenv
import os
import time

def decode_payload(t):
    h, p, s = t.split(".")
    p += "=" * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p.encode()).decode())

def get_token():
    load_dotenv()

    signin_id = os.environ.get("ID")
    signin_pw = os.environ.get("PW")

    TARGET_SITE = "https://cbsh.edu-set.com"
    LOGIN_URL = "https://cbsh.edu-set.com/signin"
    TARGET_PATHS = {
        "페이지1": "https://cbsh.edu-set.com/std/selfstudy/manage"
    }

    with SB(uc=True, headless2=True, test=True) as sb:
        sb.uc_open_with_reconnect(TARGET_SITE, reconnect_time=10)

        sb.uc_open_with_reconnect(LOGIN_URL, reconnect_time=10)

        sb.type("input[name='id']", signin_id)
        sb.type("input[name='password']", signin_pw)
        sb.click("button[type='submit']")
        sb.sleep(10)

        token = sb.execute_script("return window.localStorage.getItem('accessToken');")
        return token

def valid_token(token):
    payload = decode_payload(token)
    exp = payload.get("exp")
    if exp is None:
        return None
    if exp < int(time.time()):
        return None
    return token

def get_valid_token(token):
    v = valid_token(token)
    if v is None:
        return get_token()
    return v

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI4OWEyZWIyNi0xMGM1LTQ5NWEtOTU5MC0xZjlkYTQ5OTg1YjkiLCJpYXQiOjE3NjI4NDgwNzksImV4cCI6MTc2MzEwNzI3OX0.RXs0OJ-uKVekquPbKabobp9xTChLHeQVtSLoAemDdjQ"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/selfstudy")
def get_selfstudy():
    global token
    token = get_valid_token(token)

    url = "https://api.cbsh.edu-set.com/selfstudy/search"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.49.0",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }

    kst = datetime.utcnow() + timedelta(hours=9)
    today_kst_iso = kst.strftime("%Y-%m-%dT00:00:00.000Z")
    data = {"date": today_kst_iso}

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
            "type": item.get("type", "selfstudy") or "selfstudy",
            "period": item.get("period", 0) or 0,
            "student_name": student.get("name", "이름없음") or "이름없음",
            "student_id": student_id,
            "room_name": item.get("room", {}).get("name", "방없음") or "방없음",
            "seat_name": item.get("seat", {}).get("name") if item.get("seat") else "없음"
        }

        if info["type"] == "outstay":
            info["reason"] = item.get("reason", "사유없음")

        results.append(info)

    results_sorted = sorted(results, key=lambda x: (
        x["period"],
        x["room_name"],
        x["seat_name"]
    ))

    return results_sorted
