#!/usr/bin/env python3
"""
Agri Rover — Mock ESP32-CAM Simulator
File: Prototype/companion_pc/mock_esp32_cam.py

Simulates the physical AI-Thinker ESP32-CAM board:
 1. Serves synthetic animated crop row video with moving caterpillar & weed targets
    as an MJPEG stream on http://0.0.0.0:81/stream and http://0.0.0.0:80/stream.
 2. Handles HTTP REST control API:
    - GET /drive?left=...&right=...
    - GET /spray?ms=200
    - GET /flash?val=...
    - GET /status
 3. Enables complete end-to-end testing of the Mobile App and OpenCV Vision Bridge
    on your PC without needing physical hardware!
"""

import http.server
import socketserver
import threading
import time
import math
import numpy as np
import cv2
import urllib.parse

HTTP_PORT = 8000     # Simulated ESP32 Port 80 (or 8000 for non-root execution)
STREAM_PORT = 8081   # Simulated ESP32 Port 81 (or 8081 for non-root execution)

# State
rover_state = {
    "left_speed": 0,
    "right_speed": 0,
    "flash": 0,
    "spraying": False,
    "spray_until": 0,
    "last_command": time.time()
}

def generate_synthetic_frame(t):
    """Draws a synthetic agricultural scene with crop rows, caterpillars, and weeds."""
    w, h = 640, 480
    frame = np.zeros((h, w, 3), dtype=np.uint8)

    # 1. Dirt Ground (Brown)
    frame[:] = (35, 45, 60)

    # 2. Crop Rows (Perspective green bands)
    cv2.line(frame, (100, h), (260, 200), (30, 100, 30), 18)
    cv2.line(frame, (w - 100, h), (w - 260, 200), (30, 100, 30), 18)
    cv2.line(frame, (0, 200), (w, 200), (50, 70, 90), 2)  # Horizon

    # 3. Animated Caterpillar Target (Purple: BGR ~ (180, 50, 150), HSV ~ [140, 180, 180])
    cat_x = int(w * 0.5 + 120 * math.sin(t * 0.8))
    cat_y = int(320 + 30 * math.cos(t * 1.2))
    cv2.ellipse(frame, (cat_x, cat_y), (35, 18), int(math.sin(t) * 15), 0, 360, (180, 50, 160), -1)
    cv2.circle(frame, (cat_x + 25, cat_y - 5), 10, (140, 30, 120), -1)  # Head

    # 4. Foliar Weed Target (Red: BGR ~ (30, 30, 210), HSV ~ [0, 220, 210])
    weed_x = int(w * 0.35 + 40 * math.sin(t * 0.5 + 2))
    weed_y = int(270 + 20 * math.cos(t * 0.5))
    pts = np.array([
        [weed_x, weed_y - 20],
        [weed_x + 18, weed_y + 10],
        [weed_x - 18, weed_y + 10]
    ], np.int32)
    cv2.fillPoly(frame, [pts], (30, 40, 220))

    # 5. Visual spray actuation indicator if active
    if rover_state["spraying"] and time.time() < rover_state["spray_until"]:
        cv2.putText(frame, ">>> SPRAYING MICRO-BURST (200ms) <<<", (80, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        # Draw spray particles
        for i in range(20):
            px = int(w * 0.5 + math.sin(t * 20 + i) * 60)
            py = int(h * 0.75 + math.cos(t * 20 + i) * 50)
            cv2.circle(frame, (px, py), 4, (255, 220, 100), -1)
    elif rover_state["spraying"]:
        rover_state["spraying"] = False

    # 6. Motor Telemetry HUD overlay
    cv2.putText(frame, f"SIM ESP32-CAM | L:{rover_state['left_speed']} R:{rover_state['right_speed']}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    return jpeg.tobytes()

class StreamHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/stream'):
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            t0 = time.time()
            try:
                while True:
                    t = time.time() - t0
                    frame_bytes = generate_synthetic_frame(t)
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(frame_bytes)}\r\n\r\n'.encode())
                    self.wfile.write(frame_bytes)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.04)  # ~25 FPS
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress streaming access logs

class ControlHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if parsed.path == '/drive':
            left = int(params.get('left', [0])[0])
            right = int(params.get('right', [0])[0])
            rover_state['left_speed'] = left
            rover_state['right_speed'] = right
            rover_state['last_command'] = time.time()
            if left != 0 or right != 0:
                print(f"[DRIVE] Left: {left:4d} | Right: {right:4d}")
            self.wfile.write(b'{"status":"ok"}')

        elif parsed.path == '/spray':
            ms = int(params.get('ms', [200])[0])
            rover_state['spraying'] = True
            rover_state['spray_until'] = time.time() + (ms / 1000.0)
            print(f"\n[ACTUATION] >>> Calibrated Micro-Burst Spray Triggered! ({ms}ms) <<<\n")
            self.wfile.write(f'{{"status":"spraying","ms":{ms}}}'.encode())

        elif parsed.path == '/flash':
            val = int(params.get('val', [0])[0])
            rover_state['flash'] = val
            print(f"[FLASH] LED Brightness: {val}")
            self.wfile.write(b'{"status":"ok"}')

        elif parsed.path == '/status':
            self.wfile.write(b'{"battery":12.4,"rssi":-52,"status":"MOCK_ONLINE"}')

        else:
            self.wfile.write(b'{"status":"unknown_route"}')

    def log_message(self, format, *args):
        return

def main():
    print("=" * 65)
    print("        🌿 AGRI ROVER — MOCK ESP32-CAM SIMULATOR           ")
    print("=" * 65)
    print(f"Control API Server  : http://localhost:{HTTP_PORT} (Endpoints: /drive, /spray, /flash)")
    print(f"Video Stream Server : http://localhost:{STREAM_PORT}/stream")
    print("=" * 65)
    print("Simulating animated caterpillars and weeds for OpenCV detection!")
    print("Press Ctrl+C to exit.\n")

    # Start MJPEG Stream Server
    stream_server = socketserver.ThreadingTCPServer(("", STREAM_PORT), StreamHandler)
    t_stream = threading.Thread(target=stream_server.serve_forever, daemon=True)
    t_stream.start()

    # Start Control API Server
    ctrl_server = socketserver.ThreadingTCPServer(("", HTTP_PORT), ControlHandler)
    try:
        ctrl_server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock ESP32-CAM simulator.")
        stream_server.shutdown()
        ctrl_server.shutdown()

if __name__ == "__main__":
    main()
