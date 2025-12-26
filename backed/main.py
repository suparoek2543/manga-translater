import os
import requests
from scraper import scrape_mangadex_chapter
from translator import translate_folder


def get_manga_metadata(chapter_url):
    """ใช้ API ของ MangaDex เพื่อหาชื่อเรื่องและเลขตอน"""
    chapter_id = chapter_url.split('/')[-1]
    api_url = f"https://api.mangadex.org/chapter/{chapter_id}?includes[]=manga"
    
    response = requests.get(api_url).json()
    chapter_num = response['data']['attributes']['chapter']
    
    # หาชื่อเรื่องจาก relationships
    manga_title = "Unknown_Manga"
    for rel in response['data']['relationships']:
        if rel['type'] == 'manga':
            manga_title = rel['attributes']['title']['en'] # หรือ 'ja-ro'
            break
            
    # ล้างชื่อเรื่องให้ใช้เป็นชื่อโฟลเดอร์ได้ (ลบอักขระพิเศษ)
    clean_title = "".join([c for c in manga_title if c.isalnum() or c in (' ', '_')]).strip()
    return clean_title, chapter_num

def main():
    url = input("วางลิงก์ MangaDex: ")
    title, ch_num = get_manga_metadata(url)
    
    raw_path = os.path.abspath(os.path.join("storage", "raw", title, f"Ch_{ch_num}"))
    translated_path = os.path.abspath(os.path.join("storage", "translated", title, f"Ch_{ch_num}"))

    # 1. ดาวน์โหลด
    print("🚀 Downloading RAW images...")
    scrape_mangadex_chapter(url, raw_path)

    # 2. แปลภาษา (ส่งต่อเข้า Translator)
    print("🎨 Translating images...")
    success = translate_folder(raw_path, translated_path)
    
    if success:
        print(f"🎉 All Done! Read your manga here: {translated_path}")
    else:
        print("⚠️ Something went wrong during translation.")

if __name__ == "__main__":
    main()