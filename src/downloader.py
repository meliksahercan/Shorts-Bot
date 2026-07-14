import os
import yt_dlp
from src.db import db
from src.metadata_utils import randomize_and_clean_metadata

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_short(source_url: str) -> str:
    """
    YouTube Shorts videosunu yt-dlp ile en yüksek kalitede indirir.
    İndirilen videonun dosya yolunu döndürür.
    """
    db.update_video_status(source_url, "DOWNLOADING")
    db.log_info("downloader.py", f"İndirme başlatılıyor: {source_url}")
    
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Sadece bilgileri çekmek için (hata ayıklama vs.)
            info_dict = ydl.extract_info(source_url, download=True)
            video_id = info_dict.get("id", None)
            
            if not video_id:
                raise Exception("Video ID'si alınamadı.")
                
            file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
            
            if not os.path.exists(file_path):
                raise Exception("Dosya diske başarılı şekilde kaydedilemedi.")
                
            # --- YENİ: Metadata temizliği ve isimlendirme randomizasyonu ---
            final_path = randomize_and_clean_metadata(file_path, source_url)
            
            db.update_video_status(source_url, "DOWNLOADED")
            db.log_info("downloader.py", f"Video başarıyla indirildi ve hazır: {final_path}")
            return final_path
            
    except Exception as e:
        error_msg = str(e)
        db.update_video_status(source_url, "FAILED", error_message=error_msg)
        db.log_error("downloader.py", f"İndirme hatası {source_url}: {error_msg}")
        raise e
