import os
import sys
import threading
from flask import Flask, render_template, request, jsonify

# Proje ana dizinini path'e ekliyoruz ki src modülleri doğru import edilsin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import db
from src.main import process_short

# Şablonların aranacağı klasörü belirtiyoruz
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    data = request.json
    source_url = data.get("source_url")
    title = data.get("title", "")
    description = data.get("description", "")
    privacy_status = data.get("privacy_status", "private")
    
    if not source_url:
        return jsonify({"error": "Video URL zorunludur"}), 400
        
    # Veritabanında kontrol et, eğer işlemdeyse veya başarılı olduysa yeniden başlatma
    video = db.videos.find_one({"source_url": source_url})
    if video and video.get("status") not in ["FAILED"]:
        return jsonify({"error": f"Bu video zaten veritabanında {video.get('status')} durumunda."}), 400
        
    # main.py içindeki süreci arkaplanda asenkron çalıştırıyoruz (Thread)
    # Bu sayede arayüz (UI) kilitlenmeden anında cevap dönebiliriz.
    thread = threading.Thread(target=process_short, args=(source_url, title, description, privacy_status))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "İşlem başarıyla başlatıldı", "source_url": source_url})

@app.route('/api/status', methods=['GET'])
def get_status():
    source_url = request.args.get("source_url")
    if not source_url:
        return jsonify({"error": "source_url parametresi zorunludur"}), 400
        
    video = db.videos.find_one({"source_url": source_url})
    if not video:
        return jsonify({"status": "NOT_FOUND", "message": "Video veritabanında bulunamadı."})
        
    return jsonify({
        "status": video.get("status"),
        "error_message": video.get("error_message"),
        "youtube_video_id": video.get("youtube_video_id")
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Web Arayüzü Başlatıldı!")
    print("👉 Tarayıcınızda şu adresi açın: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
