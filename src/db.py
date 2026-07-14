import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        if not self.mongo_uri:
            raise ValueError("MONGO_URI bulunamadı. Lütfen .env dosyasını kontrol edin.")
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client["youtube_shorts_bot"]
            
            # Koleksiyonlar
            self.videos = self.db["videos"]
            self.api_quotas = self.db["api_quotas"]
            self.system_logs = self.db["system_logs"]
            
            self._initialize_indexes()
            self.log_info("db.py", "Veritabanı bağlantısı ve indeksleme başarılı.")
            
        except ConnectionFailure as e:
            self.log_error("db.py", f"Veritabanı bağlantısı başarısız: {e}")
            raise e

    def _initialize_indexes(self):
        # Mükerrer yüklemeleri önlemek için source_url alanına unique index
        self.videos.create_index("source_url", unique=True)
        # Günlük API kota takibi için tarih bazlı unique index
        self.api_quotas.create_index("date", unique=True)

    def log_info(self, module: str, message: str):
        log_entry = {
            "level": "INFO",
            "module": module,
            "message": message,
            "timestamp": datetime.utcnow()
        }
        print(f"[INFO] {module}: {message}")
        self.system_logs.insert_one(log_entry)

    def log_error(self, module: str, message: str):
        log_entry = {
            "level": "ERROR",
            "module": module,
            "message": message,
            "timestamp": datetime.utcnow()
        }
        print(f"[ERROR] {module}: {message}")
        self.system_logs.insert_one(log_entry)

    def add_video(self, source_url: str, title: str = "", description: str = "") -> str:
        try:
            video_doc = {
                "source_url": source_url,
                "status": "PENDING",
                "title": title,
                "description": description,
                "youtube_video_id": None,
                "error_message": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.videos.insert_one(video_doc)
            self.log_info("db.py", f"Video veritabanına eklendi: {source_url}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            self.log_error("db.py", f"Spam/Mükerrer koruması: Video zaten mevcut: {source_url}")
            return None

    def update_video_status(self, source_url: str, status: str, error_message: str = None, youtube_video_id: str = None):
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if error_message is not None:
            update_data["error_message"] = error_message
        if youtube_video_id is not None:
            update_data["youtube_video_id"] = youtube_video_id
            
        self.videos.update_one({"source_url": source_url}, {"$set": update_data})
        self.log_info("db.py", f"Durum güncellendi: {source_url} -> {status}")

    def check_api_quota(self) -> bool:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        quota = self.api_quotas.find_one({"date": today})
        
        if not quota:
            self.api_quotas.insert_one({
                "date": today,
                "credits_used": 0,
                "is_exhausted": False,
                "updated_at": datetime.utcnow()
            })
            return True
            
        if quota.get("is_exhausted", False):
            self.log_error("db.py", f"GÜVENLİK: API kotası ({today}) için dolu durumda.")
            return False
            
        return True

    def increment_api_quota(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        quota = self.api_quotas.find_one({"date": today})
        
        if quota:
            new_credits = quota.get("credits_used", 0) + 1600
            is_exhausted = new_credits >= 10000
            
            self.api_quotas.update_one(
                {"date": today},
                {"$set": {
                    "credits_used": new_credits,
                    "is_exhausted": is_exhausted,
                    "updated_at": datetime.utcnow()
                }}
            )
            self.log_info("db.py", f"API Kotası güncellendi. Kullanılan: {new_credits}/10000")
            if is_exhausted:
                self.log_error("db.py", f"DİKKAT: API kotası bugün ({today}) için sınıra (10000) ulaştı.")

# Modül import edildiğinde bir instance oluşturulur (Singleton benzeri kullanım)
db = Database()
