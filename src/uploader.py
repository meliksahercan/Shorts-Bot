import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.db import db

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def get_authenticated_service():
    credentials = None
    # Token dosyası varsa credentials yüklenir
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
    # Geçerli token yoksa (veya süresi dolmuşsa)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                db.log_info("uploader.py", "Token süresi dolmuş, yenileniyor...")
                credentials.refresh(Request())
            except Exception as e:
                db.log_error("uploader.py", f"Token yenileme başarısız: {e}")
                credentials = None
                
        if not credentials:
            db.log_info("uploader.py", "Yeni yetkilendirme işlemi başlatılıyor...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # Alınan/Yenilenen token kaydedilir
        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())
            db.log_info("uploader.py", "Yeni token token.json dosyasına kaydedildi.")
            
    return build("youtube", "v3", credentials=credentials)

def upload_short(file_path: str, source_url: str, title: str, description: str, privacy_status: str = "private") -> str:
    """
    Parametrik verilerle (başlık, açıklama, gizlilik) videoyu YouTube'a yükler.
    Başarılı olursa YouTube Video ID'sini döndürür.
    """
    if not db.check_api_quota():
        raise Exception("API Kotası dolu olduğu için yükleme yapılamıyor.")
        
    db.update_video_status(source_url, "UPLOADING")
    db.log_info("uploader.py", f"Yükleme başlatılıyor: {source_url}")
    
    try:
        youtube = get_authenticated_service()
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "22" # People & Blogs (İsteğe göre değiştirilebilir)
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                db.log_info("uploader.py", f"Yükleme yüzdesi: {int(status.progress() * 100)}%")
                
        video_id = response.get("id")
        
        if video_id:
            db.update_video_status(source_url, "UPLOADED", youtube_video_id=video_id)
            db.increment_api_quota()
            db.log_info("uploader.py", f"Video başarıyla yüklendi. YouTube ID: {video_id}")
            return video_id
        else:
            raise Exception("Yükleme tamamlandı fakat video ID dönmedi.")
            
    except Exception as e:
        error_msg = str(e)
        db.update_video_status(source_url, "FAILED", error_message=error_msg)
        db.log_error("uploader.py", f"Yükleme hatası {source_url}: {error_msg}")
        raise e
