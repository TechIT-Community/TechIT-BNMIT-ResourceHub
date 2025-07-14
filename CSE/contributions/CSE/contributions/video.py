import cv2
import easyocr
import os
from ultralytics import YOLO
import numpy as np
import sqlite3
from picamera2 import Picamera2
import time

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)  # No GPU on Pi

# Load YOLO model (use TFLite for better performance, or best.pt)
model_path = os.path.join("Main", "best.tflite")  # Change to "best.pt" if not using TFLite
if not os.path.exists(model_path):
    raise FileNotFoundError(f'Model file not found: {model_path}')
infer = YOLO(model_path)

# SQLite database setup
def init_db():
    conn = sqlite3.connect('Main/license_plates.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plates 
                 (plate_number TEXT PRIMARY KEY, timestamp TEXT, confidence REAL)''')
    conn.commit()
    conn.close()

def plate_exists(plate_text):
    conn = sqlite3.connect('Main/license_plates.db')
    c = conn.cursor()
    c.execute("SELECT plate_number FROM plates WHERE plate_number = ?", (plate_text,))
    result = c.fetchone()
    conn.close()
    return result is not None

def store_plate(plate_text, conf):
    conn = sqlite3.connect('Main/license_plates.db')
    c = conn.cursor()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    c.execute("INSERT OR IGNORE INTO plates (plate_number, timestamp, confidence) VALUES (?, ?, ?)",
              (plate_text, current_time, conf))
    conn.commit()
    conn.close()

# Initialize Pi Camera
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"size": (640, 480)}))
cam.start()

# Parameters
conf_threshold = 0.7
conf_drop_threshold = 0.3
save_duration = 2
timer_started = False
ocr_done = False
timer_start_time = 0

# Initialize database
init_db()

try:
    while True:
        # Capture frame from Pi Camera
        frame = cam.capture_array()

        # Run inference
        results = infer(frame, conf=conf_threshold)

        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()  # Bounding boxes
            scores = r.boxes.conf.cpu().numpy()  # Confidence scores

            for i, (box, conf) in enumerate(zip(boxes, scores)):
                x1, y1, x2, y2 = map(int, box)
                
                # Draw bounding box and confidence
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                label = f"Conf: {conf:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                label_y = y1 - 10 if y1 - 10 > label_size[1] else y1 + label_size[1]
                cv2.rectangle(frame, (x1, label_y - label_size[1] - 10), (x1 + label_size[0], label_y), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x1, label_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

                if conf >= conf_threshold and not ocr_done:
                    if not timer_started:
                        timer_started = True
                        timer_start_time = time.time()

                    if time.time() - timer_start_time >= save_duration:
                        license_plate = frame[y1:y2, x1:x2]
                        ocr_result = reader.readtext(license_plate)
                        ocr_text = ' '.join([text for _, text, _ in ocr_result]).replace(" ", "").upper() if ocr_result else 'No text detected'
                        
                        if ocr_text != 'No text detected' and not plate_exists(ocr_text):
                            print(f"Detected Plate: {ocr_text}, Confidence: {conf:.2f}")
                            store_plate(ocr_text, conf)
                        
                        ocr_done = True
                        timer_started = False

                elif conf < conf_drop_threshold:
                    timer_started = False
                    ocr_done = False

        # Display frame (optional, comment out to save CPU)
        cv2.imshow('License Plate Detection', frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    cam.stop()
    cv2.destroyAllWindows()