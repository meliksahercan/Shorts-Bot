# 🚀 Shorts Automation Bot

This project is a powerful, local Python automation bot designed to automatically download YouTube Shorts videos at the highest quality, clear their metadata, and upload them to your own YouTube channel via the YouTube Data API v3. 

It comes with a **beautiful, modern Flask-based Web UI** so you can manage your uploads effortlessly without ever touching the code!

---

## ✨ Features

- **Modern Web Dashboard:** A sleek, dark-mode Glassmorphic UI to input video links, titles, descriptions, and privacy settings.
- **Idempotency & Spam Protection:** Uses MongoDB Atlas to track uploaded videos and prevent uploading the same video twice.
- **Metadata Cleansing:** Uses `ffmpeg` to completely strip all original metadata from downloaded videos without losing quality (re-encoding), making the file unique to the YouTube algorithm.
- **Auto-Randomized Filenames:** Downloads are assigned a completely random UUID before processing.
- **API Quota Management:** Automatically tracks Google Cloud API usage limits (10,000 queries/day) and stops safely to avoid suspension.
- **Background Processing:** Real-time upload status tracking (Pending -> Downloading -> Uploading -> Uploaded) on the Web UI.

---

## 🛠️ Requirements & Technologies

* **Python 3.8+**
* **FFmpeg:** Must be installed on your system (Required for merging high-quality audio and video streams).
* **MongoDB Atlas:** Free cloud database for logging and tracking.
* **Google Cloud Console:** YouTube Data API v3 OAuth 2.0 Credentials.

### Python Libraries Used:
* `Flask` (Web UI)
* `yt-dlp` (Video Downloading)
* `pymongo` (Database)
* `google-api-python-client` & `google-auth-oauthlib` (YouTube Uploads)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/youtube-shorts-bot.git
cd youtube-shorts-bot
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup (.env)
Create a `.env` file in the root directory (you can rename `.env.example`).
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
```

### 5. YouTube API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create an **OAuth Client ID** (Desktop Application).
4. Download the JSON file, rename it to `credentials.json`, and place it in the root folder of this project.

### 6. Install FFmpeg (Windows)
```powershell
winget install Gyan.FFmpeg
```

---

## 🚀 How to Run

Simply run the Flask web application:
```bash
python src/app.py
```
Then open your browser and go to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

*(Alternatively, Windows users can double-click the `Start_Shorts_Bot.bat` file).*

---

## 🔒 Security Notice
**NEVER** upload your `.env`, `credentials.json`, or `token.json` files to GitHub. Ensure the `.gitignore` file is active in your repository to keep your accounts completely safe.

---
*Developed as an independent automation tool.*
