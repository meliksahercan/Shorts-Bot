import os
import uuid
import subprocess
from src.db import db

def randomize_and_clean_metadata(input_path: str, source_url: str) -> str:
    """
    Takes an input video path, generates a random UUID name,
    clears all metadata using ffmpeg without re-encoding, and deletes the original file.
    Returns the new file path.
    """
    directory = os.path.dirname(input_path)
    # Generate completely random filename (UUID)
    random_filename = f"{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(directory, random_filename)
    
    db.log_info("metadata_utils.py", f"Metadata temizliği başlatılıyor: {input_path}")
    
    try:
        # ffmpeg ile yeniden kodlama yapmadan (copy) metadatayı sil (-map_metadata -1)
        command = [
            "ffmpeg",
            "-y", 
            "-i", input_path,
            "-map_metadata", "-1",
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ]
        
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if process.returncode != 0:
            db.log_error("metadata_utils.py", f"ffmpeg hatası: {process.stderr}")
            raise Exception("Metadata temizliği ffmpeg ile yapılamadı.")
            
        # Orijinal dosyayı sil (İz bırakmamak için)
        if os.path.exists(input_path):
            os.remove(input_path)
            
        db.log_info("metadata_utils.py", f"Metadata tamamen temizlendi. Yeni rastgele dosya: {random_filename}")
        return output_path
        
    except Exception as e:
        db.log_error("metadata_utils.py", f"Metadata temizleme hatası: {str(e)}")
        # Bir hata olursa akışı bozmamak için orijinal dosyayı döndür
        return input_path
