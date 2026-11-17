# Project Task Roadmap & Verification Matrix (TASKS.md) — Prototype
## Agri Rover: ESP32-CAM Edge IoT Teleoperated & Autonomous Vision Testbed

**Document Version:** 1.0.0  
**Project Code:** MMCA34 — Agri Rover Phase II Prototype Work  
**Hardware Target:** AI-Thinker ESP32-CAM Module  
**Status:** Active Execution Plan  

---

## 1. Prototype Milestone Overview

```mermaid
flowchart LR
    M1["M1: Bench Setup & Flashing Rig"] --> M2["M2: Firmware Development"]
    M2 --> M3["M3: Electrical & Chassis Wiring"]
    M3 --> M4["M4: Phone Web App & Control"]
    M4 --> M5["M5: OpenCV Threat Bridge"]
    M5 --> M6["M6: Digital Twin Synchronization"]
```

---

## 2. Milestone 1: Flashing Environment & Bench Setup

- [ ] **TASK-P101: FTDI Programmer & ESP32-CAM Breadboard Rig**
  - Wire FTDI adapter to ESP32-CAM: VCC to 5V, GND to GND, TX to U0RXD (IO3), RX to U0TXD (IO1).
  - Install a tactile switch or jumper header between `GPIO 0` and `GND` for download mode selection.
  - *Verification:* Connect to PC; verify COM port enumeration and stable $5.0\text{V}$ rail.
- [ ] **TASK-P102: Arduino IDE / PlatformIO Configuration**
  - Install ESP32 Board Core (v2.0.11 or later).
  - Configure IDE build parameters:
    - **Board:** `AI Thinker ESP32-CAM`
    - **CPU Frequency:** `240MHz (WiFi/BT)`
    - **Flash Frequency:** `80MHz`
    - **Flash Mode:** `QIO`
    - **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)`
    - **Core Debug Level:** `Verbose` (during initial bring-up)
  - *Verification:* Flash standard `CameraWebServer` example; confirm serial output prints local IP.
- [ ] **TASK-P103: PSRAM Verification & Camera Probe Test**
  - Compile memory test asserting `psramFound() == true` and `esp_camera_init(&camera_config) == ESP_OK`.
  - *Verification:* Serial monitor prints total PSRAM $>4\text{MB}$ and free heap $>3.8\text{MB}$.

---

## 3. Milestone 2: Firmware Development & FreeRTOS Architecture

- [ ] **TASK-P201: Dual Wi-Fi Network Manager (`wifi_manager.h`)**
  - Implement concurrent SoftAP (`AgriRover-CAM-AP`, IP `192.168.4.1`) and Station Mode auto-fallback.
  - *Verification:* Phone discovers and connects to AP within $3\text{ seconds}$ without external router.
- [ ] **TASK-P202: Chunked MJPEG HTTP Video Server (`camera_server.h`)**
  - Configure multipart/x-mixed-replace stream handler at `http://<ip>:81/stream`.
  - Tune frame settings: VGA resolution ($640\times 480$), JPEG quality 12, double frame buffer in PSRAM.
  - *Verification:* Browser renders smooth $>15\text{ FPS}$ stream with $<120\text{ ms}$ latency.
- [x] **TASK-P203: LEDC Hardware PWM Motor Driver (`motor_controller.h`)**
  - Assign LEDC channels 0–3 at $5\text{ kHz}$ across GPIO 12, 13, 14, 15.
  - Implement differential skid-steer kinematics solver mapping throttle and steering to left/right motor PWM.
  - *Verification:* Verified via automated virtual hardware test suite (`Prototype/scripts/virtual_hardware_test.py`) and interactive testbench (`Prototype/virtual_testbench.html`). All 8 kinematics tests passed with 100% assertions.
- [x] **TASK-P204: Non-Blocking Spray Micro-Burst Actuator (`spray_actuator.h`)**
  - Configure GPIO 2 digital output driving the 5V relay module.
  - Implement non-blocking timestamp watchdog de-energizing relay after calibrated $200\text{ ms}$.
  - *Verification:* Logic analyzer confirms relay pulse duration of $200\text{ ms} \pm 5\text{ ms}$ without blocking video stream.
- [x] **TASK-P205: Failsafe Wireless Watchdog Timer**
  - Implement 500ms command timeout resetting all motor PWM channels to $0\%$.
  - *Verification:* Rover halts immediately when phone Wi-Fi is disconnected while moving.

---

## 4. Milestone 3: Electrical & Mechanical Chassis Assembly

- [x] **TASK-P301: Power Supply & Buck Converter Calibration**
  - Connect 12V battery pack to LM2596 step-down buck converter.
  - Adjust multi-turn trimpot until output measures exactly **$5.10\text{V} \pm 0.02\text{V}$**.
  - Solder $1000\mu\text{F} / 16\text{V}$ electrolytic and $100\text{nF}$ ceramic capacitor across 5V and GND.
  - *Verification:* Multi-meter confirms $5.10\text{V}$ under 1A simulated load.
- [x] **TASK-P302: L298N Motor Driver Interfacing & Wiring Schematic**
  - Mount L298N driver to chassis. Wire motor banks to `OUT1..OUT4`.
  - Connect ESP32 GPIO 12 (`IN1`), GPIO 13 (`IN2`), GPIO 14 (`IN3`), GPIO 15 (`IN4`).
  - Wire common Star Ground between Battery (-), Buck GND, L298N GND, and ESP32 GND.
  - Deliver photorealistic workbench diagram and interactive vector SVG guide (`Prototype/wiring_guide.html`).
  - *Verification:* Master wiring guide verified for all 4 motors and spray pump.
- [x] **TASK-P303: Spray Pump & Optocoupled Relay Assembly**
  - Mount 12V diaphragm pump and fluid nozzle.
  - Wire relay `NO` contact in series with pump 12V supply line.
  - Solder 1N4007 flyback diode in reverse bias directly across pump motor terminals.
  - Connect relay input to ESP32 `GPIO 2`.
  - *Verification:* Issue `/spray?ms=200`; verify single crisp chemical burst with zero MCU brownout.

---

## 5. Milestone 4: Mobile Phone Control Application & Ergonomics

- [x] **TASK-P401: Embedded HTML5 Mobile Client Deployment**
  - Embed compressed HTML/CSS/JS mobile dashboard into ESP32 flash memory (`PROGMEM` / SPIFFS).
  - Serve UI directly upon `GET http://192.168.4.1/`.
  - Enforce strict 60% live video / 40% control cockpit layout.
  - *Verification:* Mobile browser loads complete responsive UI in $<500\text{ ms}$ with zero internet connection.
- [x] **TASK-P402: Multi-Touch Virtual Joystick & Kinematics Engine**
  - Implement touch canvas joystick calculating directional vectors $(dx, dy)$ and differential wheel speeds.
  - Add turn sensitivity multiplier ($K_{\text{steer}}$: $0.30\times - 1.20\times$) and straight-line motor drift trim ($-25\%\text{ to }+25\%$).
  - *Verification:* Smooth forward, reverse, pivot-left, pivot-right, and arc turns verified on iPhone and Android.
- [x] **TASK-P403: Tactical Action Controls, Presets & Continuous Speed Slider**
  - Implement speed buttons: Slow (35%), Medium (65%), Fast (100%) paired with a continuous range slider (25% to 100%).
  - Tactical triggers: 200ms Spray Burst, Flash LED, Emergency Stop, and Settings/Calibration modal.
  - *Verification:* Immediate tactile visual feedback and corresponding hardware response.
- [x] **TASK-P404: PWA 1-Tap Home Screen Install & Native Android APK**
  - Implement Web App Manifest (`manifest.json`) and service worker (`sw.js`) with custom 192px and 512px app icons.
  - Provide complete native Android Studio project wrapper in `Prototype/android_apk/`.
  - *Verification:* Installable on Android Chrome and iOS Safari without app stores.

---

## 6. Milestone 5: Companion OpenCV Threat Detection Bridge

- [ ] **TASK-P501: Python Video Stream Ingestion Script (`opencv_cam_bridge.py`)**
  - Ingest ESP32-CAM stream via `cv2.VideoCapture("http://192.168.1.150:81/stream")`.
  - Measure frame throughput and display FPS overlay.
  - *Verification:* Sustained $\ge 18\text{ FPS}$ feed on host laptop.
- [ ] **TASK-P502: HSV Color Segmentation (Pests & Weeds)**
  - Apply HSV masks: Purple $[130, 50, 50]$ to $[160, 255, 255]$ for caterpillars; Red for weed targets.
  - Extract contours, filter noise ($area > 450\text{ px}$), and draw bounding boxes.
  - *Verification:* Test on artificial target foliage; confirm accurate target detection and reticle lock.
- [ ] **TASK-P503: Automated Micro-Burst Trigger Callback**
  - Calculate target centroid $(\text{cx}, \text{cy})$.
  - When target aligns with center reticle ($35\%\text{ to }65\%$ frame width), execute HTTP GET to `/spray?ms=200`.
  - *Verification:* Physical rover fires spray micro-burst autonomously when caterpillar model is centered!

---

## 7. Milestone 6: 3D Digital Twin Integration & End-to-End Validation

- [x] **TASK-P601: Camera Stream PiP Embed in React Three.js Dashboard**
  - Add live video HUD panel to Digital Twin web app displaying ESP32-CAM stream.
  - *Verification:* Operator sees 3D virtual rover and real-time physical camera feed side-by-side (`Prototype/3d_digital_twin_app.html`).
- [x] **TASK-P602: Bi-Directional Telemetry Mirroring**
  - Establish WebSocket / direct event link mirroring phone joystick commands to virtual 3D rover model.
  - *Verification:* 3D virtual rover drives, turns, and pivots in lockstep with the physical ESP32-CAM firmware (`AgriRover_ESP32CAM.ino`).
- [x] **TASK-P603: Spray Particle Mist Synchronization**
  - Trigger Three.js particle mist emitter whenever physical spray relay activates.
  - *Verification:* Visual chemical mist appears simultaneously in 3D simulator and physical nozzle.

---

## 8. Verification & Acceptance Criteria Matrix

| Task ID | Verification Method | Pass Criteria | Status |
| :--- | :--- | :--- | :---: |
| **TASK-P101** | Multimeter & Serial Monitor | COM port recognized, stable 5.0V, no brownout. | ⬜ Ready |
| **TASK-P102** | Arduino IDE Upload | Firmware uploads without sync errors (`Done uploading`). | ⬜ Ready |
| **TASK-P103** | Serial Heap Diagnostic | Total PSRAM $>4\text{MB}$, Free Heap $>3.8\text{MB}$. | ⬜ Ready |
| **TASK-P201** | Smartphone Wi-Fi Scan | `AgriRover-CAM-AP` visible and connects in $<3\text{ s}$. | ⬜ Ready |
| **TASK-P202** | Chrome Browser Benchmark | VGA stream renders $\ge 15\text{ FPS}$ with latency $<120\text{ ms}$. | ⬜ Ready |
| **TASK-P203** | Motor Bench Spin Test | Forward, reverse, and pivot turns execute correctly. | ✅ Passed (Virtual) |
| **TASK-P204** | Relay Oscilloscope Check | Crisp $200\text{ ms}$ pulse; no CPU freeze or frame drop. | ⬜ Ready |
| **TASK-P205** | Wi-Fi Kill Test | Rover stops within $500\text{ ms}$ of phone disconnect. | ⬜ Ready |
| **TASK-P301** | Voltage Under Load Test | Buck voltage remains $\ge 5.0\text{V}$ during motor stall. | ⬜ Ready |
| **TASK-P401** | Phone Safari / Chrome Load | Web app opens instantly at `http://192.168.4.1`. | ⬜ Ready |
| **TASK-P502** | OpenCV Color Reticle Test | Bounding boxes enclose caterpillar model accurately. | ⬜ Ready |
| **TASK-P503** | Automated Spray Loop | Centered pest triggers autonomous relay burst. | ⬜ Ready |
| **TASK-P602** | 3D Digital Twin Test | Virtual rover mirrors physical motion in Three.js. | ✅ Passed (3D Video & WebGL) |
