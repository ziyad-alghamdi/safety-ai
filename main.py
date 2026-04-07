import cv2
from ultralytics import YOLO
import math
from flask import Flask, Response
from flask_cors import CORS
import socketio

# 1. إعداد الخادم والاتصال
app = Flask(__name__)
CORS(app)
sio = socketio.Client()

def connect_socket():
    try:
        if not sio.connected:
            sio.connect('http://localhost:4000')
            print("✅ Connected to Mufakker Dashboard")
    except:
        pass

# 2. تحميل الموديل
model_path = 'runs/detect/train/weights/best.pt'
try:
    model = YOLO(model_path)
except:
    model = YOLO('yolov8n.pt')

current_score = 100
worker_name = "Ziyad"

def generate_frames():
    global current_score
    # تأكد من رقم الكاميرا (0 للأصلية، 1 للخارجية)
    cap = cv2.VideoCapture(1) 
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        connect_socket()
        results = model(frame, stream=True, verbose=False)
        
        helmet_detected_high_conf = False
        person_detected = False
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = math.ceil(box.conf[0] * 100)
                label = model.names[cls].lower()
                
                # منطق النسبة الجديد: نعتبر الخوذة موجودة فقط إذا كانت فوق 60%
                is_valid_helmet = ('helmet' in label and conf >= 60)
                
                if is_valid_helmet:
                    helmet_detected_high_conf = True
                if 'person' in label:
                    person_detected = True

                detections.append((x1, y1, x2, y2, label, conf, is_valid_helmet))

        # منطق التقييم بناءً على شرط الـ 60%
        if person_detected and not helmet_detected_high_conf:
            current_score = max(0, current_score - 0.2)
            status = "NO HELMET"
            status_color = (0, 0, 255) # أحمر
        else:
            current_score = min(100, current_score + 0.05)
            status = "SAFE"
            status_color = (173, 214, 71) # لون مينت (#47D6AD)

        # رسم المربعات بناءً على النتائج والنسبة
        for x1, y1, x2, y2, label, conf, is_valid_helmet in detections:
            if 'person' in label:
                color = status_color
                display_label = f"Worker: {status}"
            elif 'helmet' in label:
                # إذا كانت الخوذة محققة للشرط تظهر بالأخضر، وإلا تظهر بالأحمر
                color = (173, 214, 71) if conf >= 60 else (0, 0, 255)
                display_label = f"Helmet: {conf}%"
            else:
                color = (255, 255, 255)
                display_label = f"{label} {conf}%"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            t_size = cv2.getTextSize(display_label, 1, 1, 1)[0]
            cv2.rectangle(frame, (x1, y1 - t_size[1] - 10), (x1 + t_size[0] + 10, y1), color, -1)
            cv2.putText(frame, display_label, (x1 + 5, y1 - 5), 1, 1, (255, 255, 255) if color == (0,0,255) else (0,0,0), 1)

        if sio.connected:
            sio.emit('update_data', { "score": math.ceil(current_score), "status": status })
            
        # لوحة معلومات Mufakker بالألوان الاحترافية (#0B2A41)
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 60), (65, 42, 11), -1) 
        cv2.putText(frame, f"LIVE FEED | OPERATOR: {worker_name}", (20, 38), 1, 1.5, (255, 255, 255), 2)
        cv2.circle(frame, (frame.shape[1] - 30, 32), 10, status_color, -1)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret: continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)