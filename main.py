import cv2
import math
import time

# =========================================
# إعدادات
# =========================================
MAX_DISTANCE = 80      # أقصى مسافة لاعتبار نفس الشخص
TIMEOUT = 2.0          # حذف الشخص إذا اختفى (بالثواني)

# =========================================
# تحميل كاشف الوجوه (Haar Cascade)
# =========================================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# =========================================
# الكام (غيّر الرقم إذا لزم)
# =========================================
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# =========================================
# تخزين الأشخاص
# =========================================
workers = {}
next_id = 1

# workers:
# { id: {"center": (x,y), "last_seen": time} }

# =========================================
# دوال مساعدة
# =========================================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def assign_id(center):
    global next_id

    best_id = None
    best_dist = float("inf")

    for wid, data in workers.items():
        d = distance(center, data["center"])
        if d < best_dist and d < MAX_DISTANCE:
            best_dist = d
            best_id = wid

    if best_id is not None:
        workers[best_id]["center"] = center
        workers[best_id]["last_seen"] = time.time()
        return best_id

    # شخص جديد
    wid = next_id
    next_id += 1

    workers[wid] = {
        "center": center,
        "last_seen": time.time()
    }
    return wid

def cleanup():
    now = time.time()
    to_delete = []
    for wid, data in workers.items():
        if now - data["last_seen"] > TIMEOUT:
            to_delete.append(wid)

    for wid in to_delete:
        del workers[wid]

# =========================================
# التشغيل
# =========================================
print("Starting face tracking...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:
        cx = x + w // 2
        cy = y + h // 2

        wid = assign_id((cx, cy))

        # رسم
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(
            frame,
            f"Worker {wid}",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

    cleanup()

    cv2.imshow("Face Tracking - WorkerGuard", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()