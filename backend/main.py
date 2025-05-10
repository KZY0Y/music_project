from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import base64
import requests
import re
import json

app = FastAPI()

# 允许跨域，方便前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SILICONFLOW_API_KEY = "---"
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

SPOTIFY_CLIENT_ID = "---"
SPOTIFY_CLIENT_SECRET = "---"

def extract_json_from_markdown(text):
    match = re.search(r"```(?:json)?\\s*([\\s\\S]+?)\\s*```", text)
    if match:
        text = match.group(1)
    text = text.strip()
    if '{' in text and '}' in text:
        text = text[text.find('{'):text.rfind('}')+1]
    return text

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    resp = requests.post(url, data={
        "grant_type": "client_credentials"
    }, auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))
    resp.raise_for_status()
    return resp.json()["access_token"]

def search_spotify_track(song, artist):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    query = f"track:{song} artist:{artist}"
    url = f"https://api.spotify.com/v1/search?q={requests.utils.quote(query)}&type=track&limit=1"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print("Spotify搜索失败：", resp.text)
        return None
    items = resp.json().get("tracks", {}).get("items", [])
    if items:
        track_id = items[0]["id"]
        return f"https://open.spotify.com/embed/track/{track_id}"
    return None

@app.post("/upload_image")
def upload_image(file: UploadFile = File(...)):
    """图片上传接口"""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "file_path": file_path}

@app.post("/analyze_image")
def analyze_image(file_path: str = Form(...)):
    """图片分析接口，调用硅基流动多模态大模型API"""
    try:
        with open(file_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        print("图片读取失败：", e)
        return JSONResponse(status_code=500, content={"error": f"图片读取失败: {e}"})

    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请分析这张图片的内容、心情、季节、风景、时间，输出结构化JSON，字段为content, mood, season, scene, time。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    try:
        resp = requests.post(SILICONFLOW_API_URL, headers=headers, json=data)
        print("API状态码：", resp.status_code)
        print("API返回：", resp.text)
    except Exception as e:
        print("API请求失败：", e)
        return JSONResponse(status_code=500, content={"error": f"API请求失败: {e}"})

    try:
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        try:
            clean_content = extract_json_from_markdown(content)
            info = json.loads(clean_content)
        except Exception:
            info = {"content": content, "mood": "", "season": "", "scene": "", "time": ""}
        return info
    except Exception as e:
        print("响应解析失败：", e)
        return JSONResponse(status_code=500, content={"error": str(e), "raw": resp.text})

@app.post("/recommend_music")
def recommend_music(content: str = Form(...), mood: str = Form(...), season: str = Form(...), scene: str = Form(...), time: str = Form(...)):
    """音乐推荐接口，调用硅基流动文本大模型API"""
    prompt = f"请根据以下图片信息推荐一首最适合的音乐，输出JSON，字段为song和artist。\n内容: {content}\n心情: {mood}\n季节: {season}\n场景: {scene}\n时间: {time}"
    headers = {
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }
    resp = requests.post(SILICONFLOW_API_URL, headers=headers, json=data)
    try:
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        try:
            clean_content = extract_json_from_markdown(content)
            info = json.loads(clean_content)
        except Exception:
            info = {"song": content, "artist": ""}
        return info
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "raw": resp.text})

@app.post("/spotify_play")
def spotify_play(song: str = Form(...), artist: str = Form(...)):
    """Spotify播放接口，返回可嵌入的播放器链接"""
    url = search_spotify_track(song, artist)
    if url:
        return {"spotify_url": url}
    else:
        return {"spotify_url": f"https://open.spotify.com/search/{song} {artist}"} 