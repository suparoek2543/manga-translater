import subprocess
import os

# ระบุที่อยู่ของตัวแปลภาษาในเครื่องคุณ (ปรับให้ตรงกับ Path จริง)
# ตัวอย่าง: r"C:\Users\Mario\...\manga-image-translator-beta-0.3"
TRANSLATOR_DIR = os.getenv("TRANSLATOR_PATH")
PYTHON_EXE = os.path.join(TRANSLATOR_DIR, "manga_env", "Scripts", "python.exe")

def translate_folder(input_path, output_path, mag_ratio=1.2):
    """
    ฟังก์ชันสำหรับสั่งแปลทั้ง Folder
    input_path: โฟลเดอร์รูป raw (เช่น storage/raw/Berserk/Ch_1)
    output_path: โฟลเดอร์ที่จะเก็บรูปแปล (เช่น storage/translated/Berserk/Ch_1)
    """
    
    # ตรวจสอบว่ามีโฟลเดอร์ output หรือยัง
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # เตรียมคำสั่ง (เหมือนที่คุณเคยรันใน PowerShell)
    # เราใช้ --mode batch เพื่อแปลทั้งโฟลเดอร์
    command = [
        PYTHON_EXE, 
        os.path.join(TRANSLATOR_DIR, "translate_demo.py"),
        "--mode", "batch",
        "--translator", "gemini",
        "--target-lang", "THA",
        "--use-cuda",                   # ใช้การ์ดจอ
        "--eng-font", "layiji.ttf",     # ใช้ฟอนต์ที่คุณแก้ไว้
        "--text-mag-ratio", str(mag_ratio),
        "--image", input_path,          # โฟลเดอร์ต้นทาง
        "--output", output_path         # โฟลเดอร์ปลายทาง
    ]

    print(f"🤖 AI Translator is starting for: {input_path}")
    
    try:
        # สั่งรันคำสั่งและรอจนกว่าจะเสร็จ
        result = subprocess.run(command, cwd=TRANSLATOR_DIR, check=True)
        if result.returncode == 0:
            print(f"✅ Translation completed! Results saved in: {output_path}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Translation failed: {e}")
        return False