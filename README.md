# TikTok Monitor

A Python script that monitors TikTok profiles in real-time and sends notifications for new videos, followers, following, and likes.
Built using `selenium` with Chrome via `undetected-chromedriver` and integrates with Discord via webhooks.

---

## Features

* Automatically opens TikTok and applies cookies to bypass login.
* Monitors **followers**, **following**, **likes**, and new videos.
* Sends updates to Discord automatically via webhooks.
* Tracks already seen videos to avoid duplicate notifications.
* Works with **headless** or **non-headless** Chrome mode.

---

## Requirements

* **Python 3.10+** installed.
* **Google Chrome** or **Chromium** installed.
* **yt-dlp** installed for downloading videos.
* Internet connection.

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Dansvn/TikTok-Monitor
cd TikTok-Monitor
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare configuration

Create a `config.json` file:

```json
{
  "profile_url": "https://www.tiktok.com/@username",
  "refresh_interval": 10,
  "webhooks": {
    "followers": "DISCORD_WEBHOOK_URL",
    "reposts": "DISCORD_WEBHOOK_URL",
    "favorites": "DISCORD_WEBHOOK_URL",
    "likes": "DISCORD_WEBHOOK_URL"
  }
}
```
## Cookies

To make TikTok Monitor work properly, you need to provide your cookies:

- cookies/cookies.json → This file should contain your TikTok cookies in JSON format, which allows the script to log in automatically to your profile without entering username and password.
- cookies/cookies.txt → This file should contain the cookies in .txt format, which yt-dlp uses to download private or restricted videos correctly.

Both files are essential: the .json for Selenium navigation and the .txt for video downloads via yt-dlp.


---

## Running the Monitor

```bash
python main.py
```

If successful, you'll see:

```
[INFO] Launching Chrome browser...
[INFO] Navigating to TikTok homepage...
[INFO] Loading cookies...
[HH:MM:SS] Followers: ...
[HH:MM:SS] Following: ...
[HH:MM:SS] Likes: ...
```

---

## How It Works

1. Opens TikTok in a Selenium-controlled Chrome browser.
2. Loads cookies to bypass login.
3. Navigates to the target profile.
4. Monitors **reposts**, **favorites**, **likes**, and profile stats.
5. Sends Discord notifications only when new videos are posted or profile stats change.
6. Downloads new videos temporarily before sending to Discord, then deletes them locally.

---

Known Issues

- Captcha: TikTok may occasionally present a captcha when using the script. This can temporarily block automated actions.

- Photo Posts: The script only downloads videos. Posts that contain only photos will be skipped and not downloaded.


---

## Disclaimer

This project is for **educational purposes** only.
TikTok’s interface may change at any time, which could break the script.

---

## Contact

If you have any questions or need support, feel free to reach out!  
**My social links:** [ayo.so/dansvn](https://ayo.so/dansvn)
