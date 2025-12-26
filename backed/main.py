from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from downloader import scrape_mangadex_chapter # เปลี่ยนชื่อให้ตรงกับไฟล์ของคุณ
from translator import translate_folder

app = FastAPI()

# เปิดให้หน้าเว็บเรียกใช้ API ได้ (CORS)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# เชื่อมต่อโฟลเดอร์เก็บรูปที่แปลแล้ว ให้เข้าถึงผ่าน URL ได้
# เช่น http://localhost:8000/images/Berserk/Ch_1/001.jpg
app.mount("/images", StaticFiles(directory="backed/storage/translated"), name="images")

def get_manga_metadata(url: str):
    """ดึงชื่อเรื่องและเลขตอนจาก MangaDex API"""
    chapter_id = url.split('/')[-1]
    api_url = f"https://api.mangadex.org/chapter/{chapter_id}?includes[]=manga"
    res = requests.get(api_url).json()
    
    chapter_num = res['data']['attributes']['chapter']
    manga_title = "Unknown"
    for rel in res['data']['relationships']:
        if rel['type'] == 'manga':
            manga_title = rel['attributes']['title'].get('en') or rel['attributes']['title'].get('ja-ro')
            break
    
    # ล้างชื่อเรื่องให้ใช้เป็นชื่อโฟลเดอร์ได้
    clean_title = "".join([c for c in manga_title if c.isalnum() or c in (' ', '_')]).strip()
    return clean_title, chapter_num

async def process_translation(url: str):
    """กระบวนการทำงานเบื้องหลัง: โหลด -> แปล"""
    title, ch = get_manga_metadata(url)
    raw_path = os.path.join("backed", "storage", "raw", title, f"Ch_{ch}")
    trans_path = os.path.join("backed", "storage", "translated", title, f"Ch_{ch}")
    
    # 1. ดาวน์โหลดไฟล์ RAW
    scrape_mangadex_chapter(url, raw_path)
    
    # 2. ส่งไปแปล
    translate_folder(raw_path, trans_path)

@app.post("/translate")
async def start_job(url: str, tasks: BackgroundTasks):
    tasks.add_task(process_translation, url)
    return {"status": "success", "message": "เริ่มกระบวนการแปลในพื้นหลังแล้ว"}

@app.get("/library")
async def get_library():
    """ดึงรายชื่อมังงะทั้งหมดในระบบเพื่อนำไปโชว์ในหน้าเว็บ"""
    library = []
    base_path = "backed/storage/translated"
    if os.path.exists(base_path):
        for title in os.listdir(base_path):
            ch_path = os.path.join(base_path, title)
            chapters = os.listdir(ch_path) if os.path.isdir(ch_path) else []
            library.append({"title": title, "chapters": chapters})
    return library

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)