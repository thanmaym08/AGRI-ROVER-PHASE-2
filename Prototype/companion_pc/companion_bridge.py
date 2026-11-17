#!/usr/bin/env python3
"""
Agri Rover — Companion PC Vision & Telemetry Bridge
File: Prototype/companion_pc/companion_bridge.py

Features:
 1. Low-latency threaded video frame capture from ESP32-CAM (or Mock Simulator).
 2. Real-time HSV color segmentation for foliar pests (purple) and weeds (red).
 3. Tactical targeting reticle with lock-on centroid calculation.
 4. Automated HTTP spray micro-burst triggering (/spray?ms=200).
 5. Embedded WebSocket server (port 8765) streaming telemetry to the 3D Digital Twin!
"""

import cv2
import numpy as np
import urllib.request
import time
import argparse
import threading
import json
import asyncio

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Default parameters
DEFAULT_STREAM_URL = "http://192.168.4.1:81/stream"
DEFAULT_TRIGGER_URL = "http://192.168.4.1/spray?ms=200"
WS_PORT = 8765

# HSV Color Ranges (Calibrated to Agri Rover Phase 1 Baseline)
PURPLE_LOWER = np.array([130, 50, 50])
PURPLE_UPPER = np.array([160, 255, 255])

RED_LOWER_1 = np.array([0, 70, 50])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 70, 50])
RED_UPPER_2 = np.array([180, 255, 255])

# Global state for WebSocket broadcasting
telemetry_data = {
    "fps": 0.0,
    "threats_detected": 0,
    "target_locked": False,
    "target_type": "NONE",
    "target_pos": [0, 0],
    "last_spray_event": 0
}

connected_ws_clients = set()

# Threaded video capture to eliminate OpenCV buffer lag
class FreshFrameReader:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret = False
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.02)
                continue
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def release(self):
        self.running = False
        self.cap.release()

async def ws_handler(websocket):
    connected_ws_clients.add(websocket)
    try:
        while True:
            await websocket.send(json.dumps(telemetry_data))
            await asyncio.sleep(0.05)  # 20Hz telemetry broadcast
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_ws_clients.remove(websocket)

def run_ws_server(port):
    async def main_ws():
        async with websockets.serve(ws_handler, "0.0.0.0", port):
            await asyncio.Future()  # run forever

    asyncio.run(main_ws())

def trigger_esp32_spray(trigger_url):
    """Sends non-blocking HTTP micro-burst request to ESP32."""
    def _req():
        try:
            req = urllib.request.Request(trigger_url, headers={'User-Agent': 'AgriRover-Companion/2.0'})
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                if resp.status == 200:
                    print("\n>>> [ACTUATION] 200ms Chemical Micro-Burst Triggered Successfully! <<<")
                    telemetry_data["last_spray_event"] = time.time()
        except Exception as e:
            print(f"\n[WARN] Actuation trigger failed: {e}")
    threading.Thread(target=_req, daemon=True).start()

def main():
    parser = argparse.ArgumentParser(description="Agri Rover Companion PC Perception Bridge")
    parser.add_argument("--stream", type=str, default=DEFAULT_STREAM_URL,
                        help="Video stream URL (e.g. http://192.168.4.1:81/stream or http://localhost:8081/stream)")
    parser.add_argument("--trigger", type=str, default=DEFAULT_TRIGGER_URL,
                        help="Actuation trigger URL (e.g. http://192.168.4.1/spray?ms=200 or http://localhost:8000/spray?ms=200)")
    parser.add_argument("--min-area", type=int, default=450, help="Minimum contour area in pixels")
    parser.add_argument("--cooldown", type=float, default=2.5, help="Cooldown between automatic sprays (seconds)")
    parser.add_argument("--ws-port", type=int, default=WS_PORT, help="WebSocket port for Digital Twin synchronization")
    parser.add_argument("--headless", action="store_true", help="Run without GUI window")
    args = parser.parse_args()

    print("=" * 65)
    print("      🌿 AGRI ROVER COMPANION PC PERCEPTION & TWIN BRIDGE     ")
    print("=" * 65)
    print(f"Camera Stream URL    : {args.stream}")
    print(f"Spray Trigger Target : {args.trigger}")
    print(f"Digital Twin WS Port : ws://0.0.0.0:{args.ws_port}")
    print("=" * 65)
    print("Commands:")
    print("  's' - Manually trigger 200ms chemical spray")
    print("  'q' - Quit")
    print("=" * 65)

    # Start background WebSocket server for 3D Digital Twin
    if HAS_WEBSOCKETS:
        threading.Thread(target=run_ws_server, args=(args.ws_port,), daemon=True).start()
        print(f"[OK] WebSocket bridge active on port {args.ws_port}")

    print("Connecting to camera stream...")
    reader = FreshFrameReader(args.stream)
    time.sleep(1.0)

    last_spray_time = 0
    frame_count = 0
    t0 = time.time()
    current_fps = 0.0

    try:
        while True:
            ret, frame = reader.read()
            if not ret or frame is None:
                time.sleep(0.04)
                continue

            frame_count += 1
            if time.time() - t0 >= 1.0:
                current_fps = frame_count / (time.time() - t0)
                frame_count = 0
                t0 = time.time()
                telemetry_data["fps"] = round(current_fps, 1)

            h, w, _ = frame.shape
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Segmentation
            mask_purple = cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER)
            mask_r1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
            mask_r2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
            mask_red = cv2.bitwise_or(mask_r1, mask_r2)
            threat_mask = cv2.bitwise_or(mask_purple, mask_red)
            threat_mask = cv2.GaussianBlur(threat_mask, (5, 5), 0)

            contours, _ = cv2.findContours(threat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Aiming reticle (center 30% width)
            ret_xmin, ret_xmax = int(w * 0.35), int(w * 0.65)
            ret_ymin, ret_ymax = int(h * 0.20), int(h * 0.80)

            target_locked = False
            active_threat_type = "NONE"
            active_threat_coords = [0, 0]
            threat_count = 0

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= args.min_area:
                    threat_count += 1
                    x, y, cw, ch = cv2.boundingRect(cnt)
                    cx = x + cw // 2
                    cy = y + ch // 2

                    roi_purple = mask_purple[y:y+ch, x:x+cw]
                    is_caterpillar = cv2.countNonZero(roi_purple) > (area * 0.35)
                    label = "CATERPILLAR" if is_caterpillar else "WEED"
                    color = (255, 0, 255) if is_caterpillar else (0, 0, 255)

                    cv2.rectangle(frame, (x, y), (x + cw, y + ch), color, 2)
                    cv2.putText(frame, f"{label} [{int(area)}px]", (x, y - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

                    # Check reticle lock
                    if ret_xmin <= cx <= ret_xmax and ret_ymin <= cy <= ret_ymax:
                        target_locked = True
                        active_threat_type = label
                        active_threat_coords = [cx, cy]

                        cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)
                        cv2.line(frame, (cx - 16, cy), (cx + 16, cy), (0, 0, 0), 2)
                        cv2.line(frame, (cx, cy - 16), (cx, cy + 16), (0, 0, 0), 2)

                        # Auto-spray trigger with cooldown
                        if time.time() - last_spray_time >= args.cooldown:
                            trigger_esp32_spray(args.trigger)
                            last_spray_time = time.time()

            # Update telemetry
            telemetry_data["threats_detected"] = threat_count
            telemetry_data["target_locked"] = target_locked
            telemetry_data["target_type"] = active_threat_type
            telemetry_data["target_pos"] = active_threat_coords

            # Reticle visualization
            reticle_color = (0, 0, 255) if target_locked else (0, 255, 0)
            cv2.rectangle(frame, (ret_xmin, ret_ymin), (ret_xmax, ret_ymax), reticle_color, 2)

            ret_status = "TARGET LOCKED — MICRO-BURST ACTIVE" if target_locked else "SEARCHING ROW..."
            cv2.putText(frame, ret_status, (ret_xmin, ret_ymin - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, reticle_color, 2)

            # HUD Telemetry
            cv2.putText(frame, f"FPS: {current_fps:.1f} | THREATS: {threat_count}", (16, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if not args.headless:
                cv2.imshow("Agri Rover Companion Perception Bridge", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    trigger_esp32_spray(args.trigger)

    except KeyboardInterrupt:
        pass
    finally:
        reader.release()
        cv2.destroyAllWindows()
        print("\nCompanion Perception Bridge closed.")

if __name__ == "__main__":
    main()
