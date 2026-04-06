from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np

app = Flask(__name__)

# Global variable to store the current detected color
current_color = "None"

def detect_colors(frame):
    global current_color
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Red color range
    # Red has two ranges in HSV
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2
    
    # Green color range
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)
    
    # Yellow color range
    lower_yellow = np.array([15, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv_frame, lower_yellow, upper_yellow)
    
    # Analyze masks
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    detected = "None"
    max_area = 500 # Minimum area threshold to avoid noise
    best_cnt = None
    color_box = (0, 0, 0)
    
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            detected = "Red"
            best_cnt = cnt
            color_box = (0, 0, 255)
            
    for cnt in contours_green:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            detected = "Green"
            best_cnt = cnt
            color_box = (0, 255, 0)
            
    for cnt in contours_yellow:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            detected = "Yellow"
            best_cnt = cnt
            color_box = (0, 255, 255)
            
    if best_cnt is not None:
        x, y, w, h = cv2.boundingRect(best_cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color_box, 2)
        cv2.putText(frame, detected, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color_box, 2)
        
    current_color = detected
    return frame

def generate_frames():
    camera = cv2.VideoCapture(0) # Use 0 for default webcam, or replace with URL for mobile cam
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = detect_colors(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_color')
def get_color():
    return jsonify({"color": current_color})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
