from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS
import cv2
import face_recognition
import numpy as np
import os
import threading
import time
from datetime import datetime, date
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
import requests

# --- Load environment variables ---
load_dotenv(dotenv_path=Path('.') / '.env')
SUPABASE_URL = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '').strip()

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

# --- Supabase Init ---
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected.")
    except Exception as e:
        print("❌ Supabase error:", e)
else:
    print("⚠️ Missing Supabase credentials.")

# --- Global Variables ---
recognition_active = False
recognition_thread = None
known_face_encodings = []
known_face_names = []
known_face_ids = []
known_face_image_urls = []

current_recognized = {
    'name': '',
    'image_url': '',
    'status': 'Waiting for recognition...'
}

# --- Face Recognition System ---
class FaceRecognitionSystem:
    def __init__(self):
        self.video_capture = None
        self.last_recognition = {}
        self.tolerance = 0.6  # Increased for faster matching
        self.model = 'hog'  # 'cnn' if GPU
        self.num_jitters = 0  # Reduced from 1 to 0 for speed
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.frame_counter = 0
        self.process_every_n_frames = 10  # Process every 10th frame only

    def load_faces(self):
        global known_face_encodings, known_face_names, known_face_ids, known_face_image_urls
        try:
            result = supabase.table('students').select('*').not_.is_('image_url', 'null').execute()
            students = result.data

            if not students:
                print("⚠️ No student images found.")
                return False

            known_face_encodings.clear()
            known_face_names.clear()
            known_face_ids.clear()
            known_face_image_urls.clear()

            for student in students:
                try:
                    image = requests.get(student['image_url'], timeout=5).content
                    nparr = np.frombuffer(image, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    # Resize image for faster processing
                    rgb_img = cv2.resize(rgb_img, (0, 0), fx=0.5, fy=0.5)
                    locs = face_recognition.face_locations(rgb_img, model=self.model, number_of_times_to_upsample=0)
                    encs = face_recognition.face_encodings(rgb_img, locs, num_jitters=0)
                    if encs:
                        known_face_encodings.append(encs[0])
                        known_face_names.append(student['name'])
                        known_face_ids.append(student['id'])
                        known_face_image_urls.append(student['image_url'])
                except Exception as e:
                    print(f"⚠️ Error loading {student['name']}: {e}")

            print(f"✅ Loaded {len(known_face_encodings)} faces.")
            return True
        except Exception as e:
            print("❌ Supabase fetch error:", e)
            return False

    def mark_attendance(self, student_id, name):
        try:
            now = datetime.now()
            today = date.today().isoformat()
            session = "before_break" if now.hour < 12 else "end_of_day"

            exists = supabase.table("attendance").select("id") \
                .eq("student_id", student_id).eq("date", today).eq("session_type", session).execute()

            if exists.data:
                print(f"ℹ️ Already marked: {name}")
                return False

            supabase.table("attendance").insert({
                "student_id": student_id,
                "session_type": session,
                "date": today,
                "timestamp": now.isoformat()
            }).execute()

            print(f"✅ Attendance marked: {name}")
            return True
        except Exception as e:
            print(f"❌ Attendance error for {name}: {e}")
            return False

    def start_camera(self):
        """Initialize and start camera capture"""
        try:
            # Try camera 0 first (most common)
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                # Try camera 1 if 0 fails
                self.video_capture.release()
                self.video_capture = cv2.VideoCapture(1)
            
            if self.video_capture.isOpened():
                # Set lower resolution for better performance
                self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                self.video_capture.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS
                self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                print("✅ Camera initialized")
                return True
            
            print("❌ No camera found")
            return False
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return False

    def recognize(self):
        global recognition_active
        
        if not self.start_camera():
            current_recognized["status"] = "❌ Camera not accessible"
            return

        print("🎥 Recognition started.")
        
        while recognition_active:
            try:
                ret, frame = self.video_capture.read()
                if not ret:
                    continue

                # Store current frame for video feed
                with self.frame_lock:
                    self.current_frame = frame.copy()

                # Only process face recognition every Nth frame
                self.frame_counter += 1
                if self.frame_counter % self.process_every_n_frames != 0:
                    continue

                # Use much smaller frame for face recognition
                small_frame = cv2.resize(frame, (160, 120))  # Very small for speed
                rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Faster face detection with fewer locations
                locs = face_recognition.face_locations(rgb, model=self.model, number_of_times_to_upsample=0)
                
                if locs:  # Only compute encodings if faces found
                    encs = face_recognition.face_encodings(rgb, locs, num_jitters=self.num_jitters)

                    for enc in encs:
                        # Use faster distance calculation
                        distances = face_recognition.face_distance(known_face_encodings, enc)
                        
                        if distances.size > 0:
                            best_match_idx = np.argmin(distances)
                            if distances[best_match_idx] < self.tolerance:
                                sid = known_face_ids[best_match_idx]
                                name = known_face_names[best_match_idx]
                                img_url = known_face_image_urls[best_match_idx]
                                now = time.time()

                                if sid not in self.last_recognition or now - self.last_recognition[sid] > 5:
                                    marked = self.mark_attendance(sid, name)
                                    current_recognized.update({
                                        'name': name,
                                        'image_url': img_url,
                                        'status': '✅ Marked!' if marked else 'ℹ️ Already marked'
                                    })
                                    self.last_recognition[sid] = now
                                break  # Stop after first match

            except Exception as e:
                print(f"⚠️ Recognition error: {e}")
            
            time.sleep(0.1)  # Small delay

        if self.video_capture:
            self.video_capture.release()
        print("🛑 Recognition stopped.")

    def get_frame(self):
        """Get current frame for video streaming"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

face_system = FaceRecognitionSystem()

# --- Routes ---

@app.route('/toggle-recognition', methods=['POST'])
def toggle_recognition():
    global recognition_active, recognition_thread
    if not recognition_active:
        if not face_system.load_faces():
            return jsonify({'error': 'Failed to load student faces from database.'}), 500
        
        recognition_active = True
        recognition_thread = threading.Thread(target=face_system.recognize)
        recognition_thread.daemon = True
        recognition_thread.start()
        return jsonify({'active': True, 'message': 'Face recognition started successfully!'})
    else:
        recognition_active = False
        if recognition_thread:
            recognition_thread.join(timeout=5)
        return jsonify({'active': False, 'message': 'Face recognition stopped.'})

@app.route('/video_feed')
def video_feed():
    def generate():
        while recognition_active:
            frame = face_system.get_frame()
            if frame is not None:
                try:
                    # Resize for web display and compress more
                    display_frame = cv2.resize(frame, (480, 360))
                    ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                except:
                    pass
            time.sleep(0.1)  # 10 FPS for web display
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current')
def current_status():
    return jsonify(current_recognized)

@app.route('/reset')
def reset_status():
    current_recognized.update({
        'name': '',
        'image_url': '',
        'status': 'Waiting for recognition...'
    })
    return jsonify({'message': 'Status reset successfully'})

@app.route('/camera')
def serve_camera_ui():
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Recognition Attendance System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 1s ease-out;
        }

        .header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }

        .header p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            font-weight: 300;
        }

        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            align-items: start;
        }

        .video-section {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            animation: fadeInLeft 1s ease-out;
        }

        .video-container {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            background: #000;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }

        #video-feed {
            width: 100%;
            height: auto;
            display: block;
            min-height: 400px;
            object-fit: cover;
        }

        .video-overlay {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            backdrop-filter: blur(5px);
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }

        .btn-start {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        }

        .btn-stop {
            background: linear-gradient(45deg, #f44336, #da190b);
            color: white;
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
        }

        .btn-reset {
            background: linear-gradient(45deg, #2196F3, #0b7dda);
            color: white;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }

        .btn:active {
            transform: translateY(0);
        }

        .status-section {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            animation: fadeInRight 1s ease-out;
            text-align: center;
        }

        .status-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 20px;
        }

        .status-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }

        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        #student-photo {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #667eea;
            margin: 0 auto 15px;
            display: none;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }

        #student-photo.show {
            display: block;
            animation: zoomIn 0.5s ease-out;
        }

        #student-name {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }

        #recognition-status {
            font-size: 1.1rem;
            font-weight: 500;
            padding: 10px 15px;
            border-radius: 10px;
            margin-top: 10px;
            transition: all 0.3s ease;
        }

        .status-waiting {
            background: linear-gradient(45deg, #ffc107, #ff8f00);
            color: white;
        }

        .status-success {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }

        .status-info {
            background: linear-gradient(45deg, #2196F3, #0b7dda);
            color: white;
        }

        .status-error {
            background: linear-gradient(45deg, #f44336, #da190b);
            color: white;
        }

        .health-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.6);
            animation: pulse 2s infinite;
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes fadeInRight {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes zoomIn {
            from { opacity: 0; transform: scale(0.5); }
            to { opacity: 1; transform: scale(1); }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 15px;
            }
            
            .video-section, .status-section {
                padding: 20px;
            }
            
            .controls {
                gap: 10px;
            }
            
            .btn {
                padding: 10px 20px;
                font-size: 0.9rem;
            }
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="health-indicator" id="health-indicator"></div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 Smart Attendance System</h1>
            <p>Advanced Face Recognition Technology</p>
        </div>

        <div class="main-content">
            <div class="video-section">
                <div class="video-container">
                    <img id="video-feed" src="/video_feed" alt="Camera Feed" onerror="handleVideoError()">
                    <div class="video-overlay">
                        <span id="camera-status">📹 Camera Ready</span>
                    </div>
                </div>
                
                <div class="controls">
                    <button class="btn btn-start" onclick="startRecognition()" id="start-btn">
                        ▶️ Start Recognition
                    </button>
                    <button class="btn btn-stop" onclick="stopRecognition()" id="stop-btn">
                        ⏹️ Stop Recognition
                    </button>
                    <button class="btn btn-reset" onclick="resetStatus()" id="reset-btn">
                        🔄 Reset Status
                    </button>
                </div>
            </div>

            <div class="status-section">
                <h2 class="status-title">Recognition Status</h2>
                
                <div class="status-card">
                    <img id="student-photo" alt="Student Photo">
                    <div id="student-name">No student detected</div>
                    <div id="recognition-status" class="status-waiting">
                        Waiting for recognition...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isRecognitionActive = false;
        let updateInterval;

        function handleVideoError() {
            document.getElementById('camera-status').innerHTML = '❌ Camera Error';
            document.getElementById('video-feed').style.display = 'none';
        }

        async function startRecognition() {
            const btn = document.getElementById('start-btn');
            const originalText = btn.innerHTML;
            
            try {
                btn.innerHTML = '<span class="loading"></span> Starting...';
                btn.disabled = true;
                
                const response = await fetch('/toggle-recognition', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (data.active) {
                    isRecognitionActive = true;
                    document.getElementById('camera-status').innerHTML = '🔴 Recording';
                    showNotification('Recognition started successfully!', 'success');
                    startStatusUpdates();
                }
                
            } catch (error) {
                console.error('Start error:', error);
                showNotification('Failed to start recognition: ' + error.message, 'error');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }

        async function stopRecognition() {
            const btn = document.getElementById('stop-btn');
            const originalText = btn.innerHTML;
            
            try {
                btn.innerHTML = '<span class="loading"></span> Stopping...';
                btn.disabled = true;
                
                await fetch('/toggle-recognition', { method: 'POST' });
                
                isRecognitionActive = false;
                document.getElementById('camera-status').innerHTML = '⏸️ Paused';
                showNotification('Recognition stopped', 'info');
                stopStatusUpdates();
                
            } catch (error) {
                console.error('Stop error:', error);
                showNotification('Failed to stop recognition', 'error');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }

        async function resetStatus() {
            try {
                await fetch('/reset');
                document.getElementById('student-name').textContent = 'No student detected';
                document.getElementById('student-photo').classList.remove('show');
                updateStatusDisplay('Waiting for recognition...', 'waiting');
                showNotification('Status reset successfully', 'info');
            } catch (error) {
                console.error('Reset error:', error);
                showNotification('Failed to reset status', 'error');
            }
        }

        async function updateStatus() {
            try {
                const response = await fetch('/current');
                const data = await response.json();

                document.getElementById('student-name').textContent = 
                    data.name || 'No student detected';

                const photo = document.getElementById('student-photo');
                if (data.image_url) {
                    photo.src = data.image_url;
                    photo.classList.add('show');
                } else {
                    photo.classList.remove('show');
                }

                updateStatusDisplay(data.status || 'Waiting...', getStatusType(data.status));

            } catch (error) {
                console.error('Status update error:', error);
            }
        }

        function updateStatusDisplay(status, type) {
            const statusElement = document.getElementById('recognition-status');
            statusElement.textContent = status;
            statusElement.className = `status-${type}`;
        }

        function getStatusType(status) {
            if (!status) return 'waiting';
            if (status.includes('✅')) return 'success';
            if (status.includes('ℹ️')) return 'info';
            if (status.includes('❌')) return 'error';
            return 'waiting';
        }

        function startStatusUpdates() {
            updateInterval = setInterval(updateStatus, 3000);  // Every 3 seconds instead of 1.5
        }

        function stopStatusUpdates() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        }

        function showNotification(message, type) {
            // Create notification element
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 1000;
                font-weight: 500;
                animation: slideDown 0.3s ease-out;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideUp 0.3s ease-in forwards';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        // Add CSS animations for notifications
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        // Initialize with faster updates
        startStatusUpdates();
        
        // Faster health check
        setTimeout(() => {
            setInterval(async () => {
                try {
                    const response = await fetch('/health');
                    const health = await response.json();
                    const indicator = document.getElementById('health-indicator');
                    
                    if (health.status === 'running') {
                        indicator.style.background = '#4CAF50';
                    } else {
                        indicator.style.background = '#f44336';
                    }
                } catch (error) {
                    document.getElementById('health-indicator').style.background = '#f44336';
                }
            }, 10000);  // Check every 10 seconds instead of 5
        }, 2000);
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/health')
def health():
    return jsonify({
        'status': 'running',
        'supabase_connected': supabase is not None,
        'faces_loaded': len(known_face_encodings),
        'recognition_active': recognition_active
    })

# --- Run App ---
if __name__ == '__main__':
    print("🚀 Server running at http://localhost:5000/camera")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)