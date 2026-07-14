import os
import sys

# Proje ana dizinini path'e ekliyoruz ki src modülleri doğru import edilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import db

def reset_videos_collection():
    print("Mükerrer video (spam) veritabanı temizleniyor...")
    # Veritabanındaki 'videos' koleksiyonunda yer alan tüm kayıtları siler
    result = db.videos.delete_many({})
    print(f"\n✅ Toplam {result.deleted_count} adet eski video kaydı silindi!")
    print("✅ Artık daha önce hata alan veya denediğiniz test linklerini arayüzden tekrar yükleyebilirsiniz.\n")

if __name__ == "__main__":
    reset_videos_collection()
