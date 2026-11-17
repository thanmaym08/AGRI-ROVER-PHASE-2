#!/usr/bin/env python3
"""
Agri Rover — Master Companion PC Supervisor
File: Prototype/companion_pc/launch_all.py

Launches all prototype components simultaneously for complete hardware-in-the-loop
simulation or physical robot connection:
  [1] Mock ESP32-CAM Simulator  (Video stream: :8081, Control API: :8000)
  [2] Mobile App Web Server     (Phone UI: http://localhost:8080)
  [3] Companion OpenCV Bridge   (Pest/Weed detection + auto spray trigger)
  [4] 3D Digital Twin Dashboard (WebGL simulation with WebSocket telemetry)
"""

import subprocess
import sys
import time
import os
import webbrowser

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPANION_DIR = os.path.join(ROOT_DIR, "companion_pc")
MOBILE_DIR = os.path.join(ROOT_DIR, "mobile_app")
TWIN_DIR = os.path.join(ROOT_DIR, "digital_twin")

def main():
    print("=" * 70)
    print("        🌿 AGRI ROVER PHASE 2 — MASTER COMPANION SUITE        ")
    print("=" * 70)
    print("Mode Selection:")
    print("  [1] Full PC Simulation Mode (Mock ESP32 + Mobile App + OpenCV + Twin)")
    print("  [2] Physical Robot Mode (Connects to real ESP32-CAM on Wi-Fi)")
    print("  [3] Mobile App Web Server Only")
    print("  [4] Run Vision Automated Unit Tests")
    print("=" * 70)

    choice = input("Enter option [1-4] (default: 1): ").strip() or "1"
    processes = []

    if choice == "4":
        test_script = os.path.join(COMPANION_DIR, "test_companion.py")
        subprocess.run([sys.executable, test_script])
        return

    if choice == "3":
        app_script = os.path.join(MOBILE_DIR, "run_app_server.py")
        subprocess.run([sys.executable, app_script])
        return

    try:
        if choice == "1":
            print("\n>>> [1/4] Launching Mock ESP32-CAM Simulator...")
            mock_script = os.path.join(COMPANION_DIR, "mock_esp32_cam.py")
            p_mock = subprocess.Popen([sys.executable, mock_script])
            processes.append(p_mock)
            time.sleep(1.5)

            stream_url = "http://localhost:8081/stream"
            trigger_url = "http://localhost:8000/spray?ms=200"
        else:
            esp_ip = input("Enter physical ESP32-CAM IP (default: 192.168.4.1): ").strip() or "192.168.4.1"
            stream_url = f"http://{esp_ip}:81/stream"
            trigger_url = f"http://{esp_ip}/spray?ms=200"

        print(">>> [2/4] Starting Mobile App Web Server (:8080)...")
        app_script = os.path.join(MOBILE_DIR, "run_app_server.py")
        p_app = subprocess.Popen([sys.executable, app_script])
        processes.append(p_app)

        print(f">>> [3/4] Launching OpenCV Vision & Twin Bridge ({stream_url})...")
        bridge_script = os.path.join(COMPANION_DIR, "companion_bridge.py")
        p_bridge = subprocess.Popen([
            sys.executable, bridge_script,
            "--stream", stream_url,
            "--trigger", trigger_url
        ])
        processes.append(p_bridge)

        time.sleep(1.0)
        twin_path = os.path.join(TWIN_DIR, "index.html")
        print(f">>> [4/4] Opening 3D Digital Twin in default browser...")
        webbrowser.open(f"file://{twin_path}")

        print("\nAll systems active! Press Ctrl+C in this console to terminate all daemons.\n")
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nTerminating all prototype daemons...")
        for p in processes:
            p.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
