import os
import sys

# Proje ana dizinini path'e ekliyoruz ki src modülleri doğru import edilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import db
from src.downloader import download_short
from src.uploader import upload_short

def extract_clips_from_long_video(source_url: str, output_dir: str):
    """
    [FAZ 2 PLACEHOLDER]
    Uzun YouTube videolarından moviepy kullanarak kısa klipler keser.
    """
    pass

def process_short(source_url: str, title: str, description: str, privacy_status: str = "private"):
    """
    Tek bir YouTube Shorts linkini alıp uçtan uca işlemleri (Veritabanı, İndirme, Yükleme) yönetir.
    """
    db.log_info("main.py", f"İşlem zinciri başlatıldı: {source_url}")
    
    # 1. Veritabanına Ekle (Mükerrer/Spam Kontrolü)
    video_id_mongo = db.add_video(source_url, title, description)
    if not video_id_mongo:
        db.log_info("main.py", f"Atlanıyor. Video zaten veritabanında mevcut: {source_url}")
        return
        
    try:
        # 2. Bandwidth tasarrufu için indirmeden önce API Kotası kontrolü
        if not db.check_api_quota():
            db.log_error("main.py", "İşlem iptal edildi: API Kotası limitlerde (10,000 kredi).")
            return

        # 3. Videoyu İndir
        file_path = download_short(source_url)
        
        # 4. Videoyu Yükle
        youtube_video_id = upload_short(
            file_path=file_path,
            source_url=source_url,
            title=title,
            description=description,
            privacy_status=privacy_status
        )
        
        db.log_info("main.py", f"Tüm işlemler başarıyla tamamlandı. Kaynak: {source_url} | Yeni YT ID: {youtube_video_id}")
        
    except Exception as e:
        db.log_error("main.py", f"İşlem sırasında kritik hata oluştu: {source_url} - {str(e)}")

if __name__ == "__main__":
    db.log_info("main.py", "YouTube Shorts Otomasyon Botu (Faz 1) başlatıldı.")
    
    # Test ve Örnek Kullanım (Kendi linkiniz ve credential'larınız ile test edebilirsiniz)
    process_short(
         source_url="https://youtu.be/2gg-OOLMP-8?si=4Sj15VslKkvaisrL",
         title="fireworks can break multiple blocks",
         description="dr donut",
         privacy_status="public" # public, private, unlisted
     )
