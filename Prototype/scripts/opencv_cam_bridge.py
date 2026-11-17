"""
Agri Rover Phase 2 — Prototype OpenCV Vision Bridge
File: Prototype/scripts/opencv_cam_bridge.py

Purpose:
  1. Ingests real-time MJPEG video stream from ESP32-CAM (SoftAP 192.168.4.1 or Station LAN IP).
  2. Applies HSV color segmentation to identify caterpillars (purple mask) and weeds (red mask).
  3. Computes contour areas, centroid coordinates, and draws tactical aiming reticles.
  4. Automatically triggers the calibrated 200ms chemical micro-burst on the ESP32-CAM
     when an agricultural pest/weed enters the center spray reticle.
  5. Displays live FPS and detection metadata.
"""

import cv2
import numpy as np
import urllib.request
import time
import argparse
import sys

# Default network endpoints
DEFAULT_STREAM_URL = "http://192.168.4.1:81/stream"  # ESP32-CAM SoftAP default
DEFAULT_TRIGGER_URL = "http://192.168.4.1/spray?ms=200"

# HSV Color Boundaries matching Agri Rover Phase 1 Baseline
# Purple Caterpillar Mask
PURPLE_LOWER = np.array([130, 50, 50])
PURPLE_UPPER = np.array([160, 255, 255])

# Red Foliar Weed Mask (wraps around 0/180 hue)
RED_LOWER_1 = np.array([0, 70, 50])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 70, 50])
RED_UPPER_2 = np.array([180, 255, 255])

def trigger_esp32_spray(trigger_url):
    """Dispatches asynchronous micro-burst command to ESP32-CAM."""
    try:
        req = urllib.request.Request(trigger_url, headers={'User-Agent': 'AgriRover-OpenCV/2.0'})
        with urllib.request.urlopen(req, timeout=0.5) as response:
            if response.status == 200:
                print("\n>>> [ACTUATION] 200ms Chemical Spray Micro-Burst Triggered Successfully! <<<")
    except Exception as e:
        print(f"\n[WARN] Failed to trigger ESP32 spray: {e}")

def main():
    parser = argparse.ArgumentParser(description="Agri Rover ESP32-CAM OpenCV Bridge")
    parser.add_argument("--stream", type=str, default=DEFAULT_STREAM_URL, help="ESP32-CAM MJPEG Stream URL")
    parser.add_argument("--trigger", type=str, default=DEFAULT_TRIGGER_URL, help="ESP32-CAM Spray Trigger URL")
    parser.add_argument("--min-area", type=int, default=450, help="Minimum contour area threshold in pixels")
    parser.add_argument("--cooldown", type=float, default=2.5, help="Cooldown time between automated spray bursts (seconds)")
    args = parser.parse_args()

    print("=" * 65)
    print("       AGRI ROVER PHASE 2 — ESP32-CAM OPENCV COMPANION BRIDGE       ")
    print("=" * 65)
    print(f"Connecting to Camera Stream : {args.stream}")
    print(f"Chemical Actuation Target   : {args.trigger}")
    print(f"Noise Filter Minimum Area   : {args.min_area} px")
    print("Press 'q' in the video window to exit.")
    print("=" * 65)

    cap = cv2.VideoCapture(args.stream)
    if not cap.isOpened():
        print(f"[FATAL] Unable to connect to video stream at {args.stream}")
        print("Tip: Ensure your PC is connected to 'AgriRover-CAM-AP' or the same LAN.")
        sys.exit(1)

    last_spray_time = 0
    fps_time = time.time()
    frame_count = 0
    fps_display = "FPS: --"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Dropped frame or connection stall. Retrying...")
            time.sleep(0.05)
            continue

        frame_count += 1
        if time.time() - fps_time >= 1.0:
            fps_display = f"FPS: {frame_count / (time.time() - fps_time):.1f}"
            frame_count = 0
            fps_time = time.time()

        h, w, _ = frame.shape
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 1. Mask caterpillars (Purple)
        mask_purple = cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER)

        # 2. Mask weeds (Red)
        mask_r1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
        mask_r2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
        mask_red = cv2.bitwise_or(mask_r1, mask_r2)

        # Combine threat masks
        threat_mask = cv2.bitwise_or(mask_purple, mask_red)
        threat_mask = cv2.GaussianBlur(threat_mask, (5, 5), 0)

        contours, _ = cv2.findContours(threat_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Tactical targeting reticle zone (central 30% of field of view)
        reticle_x_min = int(w * 0.35)
        reticle_x_max = int(w * 0.65)
        reticle_y_min = int(h * 0.20)
        reticle_y_max = int(h * 0.80)

        # Draw Targeting Reticle
        reticle_color = (0, 255, 0) # Green idle
        target_locked = False

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= args.min_area:
                x, y, cw, ch = cv2.boundingRect(cnt)
                cx = x + cw // 2
                cy = y + ch // 2

                # Determine threat type
                roi_purple = mask_purple[y:y+ch, x:x+cw]
                is_caterpillar = cv2.countNonZero(roi_purple) > (area * 0.4)
                threat_label = "CATERPILLAR" if is_caterpillar else "WEED"
                box_color = (255, 0, 255) if is_caterpillar else (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x + cw, y + ch), box_color, 2)
                cv2.putText(frame, f"{threat_label} ({int(area)}px)", (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

                # Check if target is inside aiming reticle
                if reticle_x_min <= cx <= reticle_x_max and reticle_y_min <= cy <= reticle_y_max:
                    target_locked = True
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)
                    cv2.line(frame, (cx - 15, cy), (cx + 15, cy), (0, 0, 0), 2)
                    cv2.line(frame, (cx, cy - 15), (cx, cy + 15), (0, 0, 0), 2)

                    # Autonomous Spray Trigger with Cooldown
                    if time.time() - last_spray_time > args.cooldown:
                        trigger_esp32_spray(args.trigger)
                        last_spray_time = time.time()

        if target_locked:
            reticle_color = (0, 0, 255) # Red on lock

        cv2.rectangle(frame, (reticle_x_min, reticle_y_min), (reticle_x_max, reticle_y_max), reticle_color, 2)
        status_text = "TARGET ACQUIRED — FIRING SPRAY" if target_locked else "SEARCHING ROW..."
        cv2.putText(frame, status_text, (reticle_x_min, reticle_y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, reticle_color, 2)

        # Draw HUD overlays
        cv2.putText(frame, f"AGRI ROVER CAM | {fps_display}", (16, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        cv2.putText(frame, "AI PRECISION SPRAY RETICLE", (16, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Agri Rover ESP32-CAM Perception Bridge", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nShutting down vision bridge.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
