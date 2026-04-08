import cv2
import face_recognition
import numpy as np
from ultralytics import YOLO
import math
import os
import time
from flask import Flask, Response
from flask_cors import CORS
import socketio

# 1. إعداد الخادم والربط بالسوكيت
app = Flask(__name__)
CORS(app)
sio = socketio.Client()

def connect_socket():
    try:
        if not sio.connected:
            sio.connect('http://localhost:4000')
    except:
        pass

# 2. تحميل موديل YOLO (PPE Detection)
model_path = 'runs/detect/train/weights/best.pt'
model = YOLO(model_path) if os.path.exists(model_path) else YOLO('yolov8n.pt')

# 3. إعداد التعرف على الوجوه من مجلد users
known_face_encodings = []
known_face_names = []
users_folder = "users"

if os.path.exists(users_folder):
    for file in os.listdir(users_folder):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            try:
                img = face_recognition.load_image_file(f"{users_folder}/{file}")
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(os.path.splitext(file)[0])
                    print(f"✅ Registered Worker: {os.path.splitext(file)[0]}")
            except Exception as e:
                print(f"⚠️ Error loading {file}: {e}")

# 4. متغيرات التقييم الاستباقي (MVP Logic)
safety_score = 100.0  # درجة الأمان الديناميكية
last_alert_time = 0   # للتحكم في توقيت التنبيهات

def generate_frames():
    global safety_score, last_alert_time
    cap = cv2.VideoCapture(1) # تأكد من رقم الكاميرا
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        connect_socket()

        # أ) التعرف على الهوية (Accountability)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        current_worker = "Unknown"
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                current_worker = known_face_names[matches.index(True)]

        # ب) كشف مخاطر السلامة (YOLO)
        results = model(frame, stream=True, verbose=False)
        helmet_detected = False
        person_detected = False
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = math.ceil(box.conf[0] * 100)
                label = model.names[int(box.cls[0])].lower()
                
                is_valid_helmet = ('helmet' in label and conf >= 60)
                if is_valid_helmet: helmet_detected = True
                if 'person' in label: person_detected = True
                
                detections.append((x1, y1, x2, y2, label, conf, is_valid_helmet))

        # ج) احتساب "درجة الأمان" الديناميكية ونظام التنبيهات
        if person_detected:
            if not helmet_detected:
                safety_score = max(0, safety_score - 1.0) # خصم نقاط عند الخطر
                status = "CRITICAL"
                status_color = (0, 0, 255) # أحمر
                
                # نظام تنبيه تلقائي (إرسال تنبيه كل 5 ثوانٍ عند المخالفة)
                if time.time() - last_alert_time > 5:
                    if sio.connected:
                        sio.emit('safety_alert', {'msg': f'ALERT: {current_worker} is not wearing a helmet!', 'score': int(safety_score)})
                    last_alert_time = time.time()
            else:
                safety_score = min(100, safety_score + 0.2) # استعادة النقاط عند الالتزام
                status = "SECURE"
                status_color = (173, 214, 71) # أخضر (Mint)
        else:
            status = "NO WORKER"
            status_color = (255, 255, 255)

        # د) رسم الواجهة (Dashboard Overlay)
        # شريط علوي بلون Mufakker الرسمي (#0B2A41)
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 70), (65, 42, 11), -1)
        cv2.putText(frame, f"SAFETY SCORE: {int(safety_score)}%", (20, 45), 1, 1.8, status_color, 2)
        cv2.putText(frame, f"WORKER: {current_worker}", (frame.shape[1]-300, 45), 1, 1.3, (255, 255, 255), 2)

        for x1, y1, x2, y2, label, conf, is_valid_helmet in detections:
            color = (173, 214, 71) if is_valid_helmet else (0, 0, 255) if 'person' in label and not helmet_detected else (200, 200, 200)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # هـ) إرسال البيانات للداشبورد
        if sio.connected:
            sio.emit('update_data', {
                "score": int(safety_score),
                "status": status,
                "operator": current_worker
            })

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 Starting Mufakker Proactive Safety Monitoring...")
    app.run(host='0.0.0.0', port=5000, threaded=True)