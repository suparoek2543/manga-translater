import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    # หากรันบน Server ที่ไม่มีหน้าจอ ให้เปิดบรรทัดล่างนี้:
    # options.add_argument("--headless") 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def auto_set_long_strip(driver):
    """ฟังก์ชันเปลี่ยนโหมดที่ราคุยกันไว้ (แบบกด Toggle วน)"""
    wait = WebDriverWait(driver, 15)
    try:
        # เปิด Sidebar
        menu_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[local-name()='svg' and contains(@class, 'feather-chevron-left')]")))
        menu_btn.click()
        time.sleep(1.5)
        
        # กด Toggle 2 ทีเพื่อให้เป็น Long Strip (ปรับตามความต้องการหน้างาน)
        xpath_toggle = "//button[contains(@class, 'md-btn') and contains(@class, 'accent')]"
        for _ in range(2):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_toggle)))
            btn.click()
            time.sleep(1)
        
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception as e:
        print(f"Auto-mode error: {e}")

def get_blob_image(driver, img_url):
    js_script = "var uri = arguments[0]; var callback = arguments[1]; fetch(uri).then(res => res.blob()).then(blob => { var reader = new FileReader(); reader.onload = function() { callback(reader.result); }; reader.readAsDataURL(blob); }).catch(err => { callback(null); });"
    return driver.execute_async_script(js_script, img_url)

def scrape_mangadex_chapter(target_url, save_path):
    """ฟังก์ชันหลักที่ API จะเรียกใช้"""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    driver = setup_driver()
    try:
        driver.get(target_url)
        auto_set_long_strip(driver)
        
        # เลื่อนหน้าจอเพื่อโหลดรูป
        print(f"Downloading from: {target_url} to {save_path}")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

        # บันทึกรูป
        images = driver.find_elements(By.TAG_NAME, "img")
        count = 0
        for img in images:
            src = img.get_attribute('src')
            if src and "blob:" in src:
                width = int(img.get_attribute("naturalWidth") or 0)
                if width < 300: continue
                
                base64_data = get_blob_image(driver, src)
                if base64_data:
                    count += 1
                    with open(os.path.join(save_path, f"{count:03d}.jpg"), "wb") as f:
                        f.write(base64.b64decode(base64_data.split(",")[1]))
        return count
    finally:
        driver.quit()