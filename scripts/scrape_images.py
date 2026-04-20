import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

page_url = "https://nl.tommy.com/EN/mens-formal-shoes"

save_folder = r"D:\Fontys\Year 2\Semester 4\Challenge\dataset\raw\formal\shoes"

os.makedirs(save_folder, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_next_number(folder, prefix="formal_shoes_"):
    max_num = 0

    for filename in os.listdir(folder):
        match = re.match(rf"{re.escape(prefix)}(\d+)\.(jpg|jpeg|png|webp)$", filename, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    return max_num + 1

count = get_next_number(save_folder)
print(f"Starting from number: {count}")

chrome_options = Options()
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.get(page_url)

time.sleep(5)

images = driver.find_elements(By.TAG_NAME, "img")
print(f"Found {len(images)} total img tags")

seen = set()

for img in images:
    img_url = img.get_attribute("src")

    if not img_url:
        continue

    if "tommy-europe.scene7.com" not in img_url:
        continue

    if img_url in seen:
        continue
    seen.add(img_url)

    try:
        response = requests.get(img_url, headers=headers, timeout=15)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        else:
            ext = ".png"

        file_name = f"formal_shoes_{count:03d}{ext}"
        file_path = os.path.join(save_folder, file_name)

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"Saved: {file_path}")
        count += 1

    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

driver.quit()
print("Done.")