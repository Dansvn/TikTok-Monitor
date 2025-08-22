import json
import os
import subprocess
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import requests

last_followers = None
last_following = None
last_likes = None
last_profile_stats = None
first_check = True

with open("config.json") as f:
    config = json.load(f)

profile_url = config["profile_url"]
refresh_interval = config.get("refresh_interval", 10)
webhooks = config["webhooks"]


def load_cookies(
    driver, path_json="cookies/cookies.json", path_txt="cookies/cookies.txt"
):
    print("[INFO] Starting cookie loading process...")
    if not os.path.exists(path_json):
        print(f"[ERROR] JSON cookie file not found: {path_json}")
        return False
    if not os.path.exists(path_txt):
        print(f"[ERROR] TXT cookie file not found: {path_txt}")
        return False

    print(f"[INFO] JSON cookie file found: {path_json}")
    with open(path_json) as f:
        cookies = json.load(f)
    print(f"[INFO] Loaded {len(cookies)} cookies from JSON")

    for i, cookie in enumerate(cookies, start=1):
        cookie_dict = {
            k: cookie[k] for k in ("name", "value", "domain", "path") if k in cookie
        }
        driver.add_cookie(cookie_dict)
        print(f"[DEBUG] Injected cookie {i}/{len(cookies)}: {cookie_dict['name']}")

    print("[INFO] All cookies injected successfully.")
    return True


def get_video_links(driver, item_selector):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, item_selector + " a"))
        )
        items = driver.find_elements(By.CSS_SELECTOR, item_selector + " a")
        return [item.get_attribute("href") for item in items]
    except:
        return []


def download_video(url):
    try:
        subprocess.run(
            [
                "yt-dlp",
                "--cookies", "cookies/cookies.txt",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "-o", "downloads/%(id)s.%(ext)s",
                "-q",
                "--no-progress",
                url,
            ],
            check=True,
        )
        return True
    except:
        return False


def send_webhook(webhook_url, file_path=None, content=None):
    if not webhook_url:
        return

    data = {}
    files = None

    if content:
        data["content"] = content
    if file_path and os.path.exists(file_path):
        files = {"file": open(file_path, "rb")}

    try:
        requests.post(webhook_url, data=data, files=files)
    finally:
        if files:
            files["file"].close()


def click_tab(driver, tab_selector):
    try:
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, tab_selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        tab.click()
        time.sleep(2)
    except:
        pass


def load_seen(file):
    if os.path.exists(file):
        with open(file) as f:
            return set(line.strip() for line in f)
    return set()


def save_seen(file, links):
    with open(file, "w") as f:
        for link in links:
            f.write(link + "\n")


def monitor_tab(driver, tab_selector, item_selector, webhook_url, log_file):
    click_tab(driver, tab_selector)
    seen_links = load_seen(log_file)
    links = get_video_links(driver, item_selector)

    if not seen_links:
        save_seen(log_file, links)
        return

    new_links = [l for l in links if l not in seen_links]

    for link in new_links:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {link}")

        video_file = f"downloads/{link.split('/')[-1]}.mp4"

        if download_video(link):
            send_webhook(
                webhook_url, file_path=video_file, content=f"[{timestamp}] {link}"
            )
            if os.path.exists(video_file):
                os.remove(video_file)

        seen_links.add(link)

    save_seen(log_file, seen_links)


def monitor_profile_stats(driver, webhook_url):
    messages = []

    try:
        followers = int(
            driver.find_element(
                By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]'
            ).text.replace(",", "")
        )
        following = int(
            driver.find_element(
                By.CSS_SELECTOR, 'strong[data-e2e="following-count"]'
            ).text.replace(",", "")
        )
        likes = int(
            driver.find_element(
                By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]'
            ).text.replace(",", "")
        )
    except:
        return

    global last_profile_stats
    if last_profile_stats is None:
        last_profile_stats = {
            "followers": followers,
            "following": following,
            "likes": likes,
        }
        messages.append(f"Followers: {followers}")
        messages.append(f"Following: {following}")
        messages.append(f"Likes: {likes}")
    else:
        if followers != last_profile_stats["followers"]:
            messages.append(f"Followers changed: {followers}")
        if following != last_profile_stats["following"]:
            messages.append(f"Following changed: {following}")
        if likes != last_profile_stats["likes"]:
            messages.append(f"Likes changed: {likes}")
        last_profile_stats = {
            "followers": followers,
            "following": following,
            "likes": likes,
        }

    if messages:
        timestamp = time.strftime("%H:%M:%S")
        content = f"[{timestamp}] Profile stats:\n" + "\n".join(messages)
        print(content)
        send_webhook(webhook_url, content=content)


def main():
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    print("[INFO] Launching Chrome browser...")
    import undetected_chromedriver as uc
    import undetected_chromedriver as uc

    

    options = uc.ChromeOptions()  
    options.binary_location = "/usr/bin/chromium"  
    driver = uc.Chrome(options=options, use_subprocess=True)  
    driver.get("https://www.tiktok.com/")
    print(driver.title)




    print("[INFO] Navigating to TikTok homepage...")
    driver.get("https://www.tiktok.com/")
    time.sleep(2)

    print("[INFO] Loading cookies...")
    if load_cookies(driver):
        print("[INFO] Cookies loaded successfully")
        print("[INFO] Refreshing page to apply cookies...")
        driver.refresh()
        print("[INFO] Page refreshed, cookies should be applied")
    else:
        print(
            "[WARNING] Cookies not found or failed to load. TikTok may not load properly"
        )

    print(f"[INFO] Navigating to profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(5)

    selectors = {
        "reposts": {
            "tab": 'p[data-e2e="repost-tab"]',
            "items": 'div[data-e2e="user-repost-item-list"] div[data-e2e="user-repost-item"]',
            "webhook": webhooks.get("reposts"),
            "log": "logs/reposts.log",
        },
        "favorites": {
            "tab": 'p[data-e2e="favorites-tab"], p[class*="PFavorite"]',
            "items": 'div[data-e2e="favorites-item-list"] div[data-e2e="favorites-item"]',
            "webhook": webhooks.get("favorites"),
            "log": "logs/favorites.log",
        },
        "likes": {
            "tab": 'p[data-e2e="liked-tab"]',
            "items": 'div[data-e2e="user-liked-item-list"] div[data-e2e="user-liked-item"]',
            "webhook": webhooks.get("likes"),
            "log": "logs/likes.log",
        },
    }

    while True:
        monitor_tab(
            driver,
            selectors["reposts"]["tab"],
            selectors["reposts"]["items"],
            selectors["reposts"]["webhook"],
            selectors["reposts"]["log"],
        )
        monitor_tab(
            driver,
            selectors["favorites"]["tab"],
            selectors["favorites"]["items"],
            selectors["favorites"]["webhook"],
            selectors["favorites"]["log"],
        )
        monitor_tab(
            driver,
            selectors["likes"]["tab"],
            selectors["likes"]["items"],
            selectors["likes"]["webhook"],
            selectors["likes"]["log"],
        )
        monitor_profile_stats(driver, webhooks.get("followers"))
        time.sleep(refresh_interval)
        driver.refresh()


if __name__ == "__main__":
    main()
