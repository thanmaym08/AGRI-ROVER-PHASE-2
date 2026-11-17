# Product Requirements Document (PRD) — Prototype
## Agri Rover: ESP32-CAM Edge IoT Teleoperated & Autonomous Vision Testbed

**Document Version:** 1.0.0  
**Project Code:** MMCA34 — Agri Rover Phase II Prototype Work  
**Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru  
**Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)  
**Target Hardware:** AI-Thinker ESP32-CAM (ESP32-S + OV2640 + 4MB PSRAM)  
**Status:** Active Prototype Specification & Implementation  

---

## 1. Executive Summary & Prototype Vision

### 1.1 Problem Statement
Developing and field-testing full-scale autonomous agricultural robotics (such as the primary Agri Rover platform utilizing a Raspberry Pi 4, dual BTS7960 43A motor drivers, linear soil probing actuators, and high-pressure chemical plumbing) presents substantial operational friction:
1. **High Hardware Risk:** Direct field testing of heavy ($12\text{–}15\text{ kg}$) rover chassis risks physical impact, tipping, and costly mechanical damage during initial algorithm and teleoperation validation.
2. **Setup Overhead & Power Demands:** The primary rover requires a high-capacity 12V 18Ah lead-acid/LiFePO4 power plant, dual high-current motor drivers, and prolonged boot/configuration cycles.
3. **Need for a Rapid Testing Vehicle:** Rapid verification of Wi-Fi video streaming latency, mobile touch-teleoperation ergonomics, computer vision threat targeting (OpenCV HSV color thresholding), and real-time synchronization with the 3D WebGL Digital Twin demands a lightweight, low-cost, ultra-agile edge prototype.

### 1.2 System Vision
The **Agri Rover ESP32-CAM Prototype** is an agile, low-cost, cyber-physical edge robotics platform engineered to validate:
- **Low-Latency Wi-Fi Video Streaming:** Real-time MJPEG transmission over 802.11 b/g/n from the onboard OV2640 camera to mobile web clients and OpenCV vision workstations.
- **Mobile Phone Teleoperation:** An embedded, responsive Web-based User Interface (PWA/HTML5) hosted directly on the ESP32-CAM web server. Operators connect directly to the rover via smartphone Wi-Fi (SoftAP or Local LAN), steering the vehicle via an intuitive virtual touch joystick and inspecting the live video stream inside the app view without requiring native app installation.
- **Precision Skid-Steer Motor & Sprayer Actuation:** Core micro-controller control over a 4WD/2WD differential chassis via an H-Bridge motor driver (L298N / DRV8833) alongside optocoupled relay switching for chemical pump/valve micro-burst simulation and high-intensity LED flash illumination.
- **Companion OpenCV & Digital Twin Bridge:** Seamless stream routing from the ESP32-CAM to a host workstation running OpenCV pest/weed detection pipelines, with real-time pose and telemetry mirrored inside the React/Three.js 3D Digital Twin simulator.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AGRI ROVER ESP32-CAM ECOSYSTEM                  │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│    ESP32-CAM ROBOT  │    PHONE APPLICATION     │   COMPANION SYSTEM    │
│  - OV2640 Camera    │  - Connect to Wi-Fi      │  - OpenCV Detection   │
│  - MJPEG Webserver  │  - Live In-App Video     │  - Pest/Weed Masking  │
│  - Dual H-Bridge    │  - Touch Virtual Joystick│  - 3D Digital Twin    │
│  - Pump Relay / LED │  - Sprayer Micro-Burst   │  - Telemetry Mirror   │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## 2. Target Personas & Use Case Scenarios

### 2.1 User Personas

| Persona | Role | Key Needs | Pain Points Solved |
| :--- | :--- | :--- | :--- |
| **Field Operator / Scout** | Field pest scouting, spot-spraying, manual row navigation. | Zero-install phone control, instant video feedback, responsive vehicle maneuvering, quick spray micro-burst triggering. | Eliminates carrying bulky laptops or dedicated RC transmitters; operates directly via any smartphone browser. |
| **Robotics & Vision Researcher** | Tuning OpenCV segmentation algorithms, measuring streaming latency. | Stable HTTP MJPEG stream endpoint (`/stream`), predictable frame rate ($\ge 15\text{ FPS}$), REST/WebSocket control API. | Provides an instant real-world video feed for OpenCV pipelines without risking damage to the full-size agricultural rover. |
| **Digital Twin Engineer** | Validating cyber-physical synchronization between real robot and 3D simulation. | Bi-directional telemetry, state reflection (speed, heading, spray events) mirrored in Three.js WebGL dashboard. | Enables end-to-end hardware-in-the-loop (HIL) testing of Digital Twin controls. |

### 2.2 Operational User Scenarios

#### Scenario 1: Field Scouting & Phone Teleoperation (Standalone Mode)
1. Operator powers on the ESP32-CAM Prototype via physical toggle switch.
2. The prototype initializes in **Dual Wi-Fi Mode** (spawns SoftAP `AgriRover-CAM-AP` with fallback to farm Wi-Fi router).
3. Operator connects smartphone Wi-Fi to `AgriRover-CAM-AP` and navigates browser to `http://192.168.4.1`.
4. The mobile dashboard loads immediately:
   - High-contrast live video stream displays on the upper viewport.
   - A virtual analog joystick appears on the bottom-left; speed presets and spray/flash toggles appear on the bottom-right.
5. Operator steers the rover through crop rows while monitoring foliage on screen.
6. Upon spotting an infected leaf, operator presses **"Spray Burst"**:
   - ESP32-CAM energizes the spray pump relay for a calibrated $200\text{ ms}$ micro-pulse.
   - Status HUD confirms spray execution and logs event.

#### Scenario 2: Companion OpenCV Automated Threat Detection & Digital Twin Sync
1. ESP32-CAM connects to local lab/farm network at IP `192.168.1.150`.
2. Host PC launches `opencv_cam_bridge.py`:
   - Ingests `http://192.168.1.150:81/stream` via OpenCV `cv2.VideoCapture`.
   - Executes HSV color masking to identify caterpillars (purple mask) and weeds (red mask).
   - Generates bounding boxes and centroid coordinates.
3. Host PC transmits control feedback:
   - When a pest is centered in frame, script issues an HTTP POST to `http://192.168.1.150/spray?duration=200`.
4. Concurrently, rover motion commands and spray state are piped to the React Three.js Digital Twin via WebSocket, animating the 3D model in real time.

---

## 3. Product Scope & Functional Requirements (FR)

### 3.1 Traceability Matrix of Functional Requirements

| ID | Requirement Name | Description | Priority | Primary Actor | Target Metric |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **FR-P01** | Dual Wi-Fi Network Architecture | ESP32-CAM must support both SoftAP (`AgriRover-CAM-AP`) for standalone direct phone connection and Station Mode (`STA`) for campus/farm router connectivity. | High | System / Operator | AP DHCP assignment $\le 3\text{ s}$; auto-fallback if router is unreachable. |
| **FR-P02** | Real-Time MJPEG Video Streaming | Continuous HTTP multipart video streaming (`/stream`) utilizing OV2640 camera sensor with internal PSRAM buffer. | Critical | Operator / OpenCV | $\ge 15\text{–}20\text{ FPS}$ at VGA ($640\times 480$) or SVGA ($800\times 600$); latency $<120\text{ ms}$. |
| **FR-P03** | Differential Skid-Steer Motor Control | 4-channel PWM direction and speed control of 4WD/2WD geared motors via dual H-bridge driver. Forward, reverse, left pivot, right pivot, and stop. | Critical | Operator / Auto Controller | PWM resolution 8-bit ($0\text{–}255$); direction update latency $<30\text{ ms}$. |
| **FR-P04** | Responsive Mobile Phone Web Application | Responsive HTML5/PWA client served directly from ESP32-CAM flash memory containing live video view, touch joystick, speed preset buttons, and telemetry HUD. | Critical | Phone User | Zero app installation required; responsive on iOS Safari and Android Chrome; asset payload $<150\text{ KB}$. |
| **FR-P05** | Chemical Spray Actuation & Flash Illumination | GPIO control for a 5V/12V optocoupled relay driving the chemical spray pump (calibrated $200\text{ ms}$ pulse) and PWM dimming/toggle of the onboard Flash LED. | High | Operator / OpenCV Engine | Timed non-blocking relay closure ($200\text{ ms} \pm 10\text{ ms}$); flash toggle response $<50\text{ ms}$. |
| **FR-P06** | OpenCV Computer Vision Stream Ingestion | Python workstation bridge capable of capturing video stream over HTTP, executing color thresholding/pest detection, drawing bounding boxes, and issuing actuation triggers. | High | Vision Bridge | Frame ingestion rate $\ge 15\text{ FPS}$; automated threat detection accuracy matching Phase 1 baseline. |
| **FR-P07** | 3D WebGL Digital Twin Telemetry Synchronization | Bi-directional bridge synchronizing prototype velocity, turn rate, spray events, and camera HUD with the Three.js 3D Digital Twin simulation. | Medium | Digital Twin Dashboard | Telemetry state sync over WebSocket $<80\text{ ms}$ delay. |
| **FR-P08** | Communication Watchdog & Fail-Safe Auto-Stop | Automatic motor cutoff if no valid control packet is received from the mobile phone or host workstation within a configured timeout window. | Critical | Embedded Safety Daemon | All motor PWM forced to 0% within $500\text{ ms}$ of signal loss. |
| **FR-P09** | Strict 60/40 Mobile Console Cockpit Layout | Mobile teleoperation viewport strictly partitioned into 60% live video feed (upper) and 40% control cockpit (lower), with floating HUD metrics and touch-action suppression. | High | Mobile Web App / Firmware | Viewport locked to 60vh / 40vh without page scrolling or bounce. |
| **FR-P10** | Multi-Regime Speed Control (Presets & Slider) | Discrete speed buttons (Slow 35%, Medium 65%, Fast 100%) paired bidirectionally with an interactive continuous slider (25% to 100%). | High | Mobile Web App / Firmware | Instant PWM recalculation scaling motor duty cycles dynamically. |
| **FR-P11** | Turning Angle Sensitivity & Motor Drift Trim | Dynamic steering angle multiplier ($K_{\text{steer}}$: 0.3x–1.2x) and straight-line motor drift trim slider (-25% to +25%) with persistent browser storage. | High | Kinematics Engine | Allows fine-tuning of turn radius and straight-line drift elimination. |
| **FR-P12** | Real-Time Motion Vector & Telemetry HUD | Live tactical overlay reporting active motion state (▲ FWD, ▼ REV, ◄ PIVOT-L, ► PIVOT-R, ⮡ CURVE) and discrete left/right PWM duty cycles. | Medium | Mobile Web App HUD | Instantaneous visual feedback on motor assertion states. |
| **FR-P13** | Installable PWA & Android APK Distribution | Support for instant 1-tap Progressive Web App (PWA) installation to mobile home screen with custom icons and offline service worker, plus standalone native Android APK project template. | High | Android / Web Distribution | Fullscreen standalone operation without browser URL bars. |

---

## 4. Non-Functional Requirements (NFR)

| Category | Identifier | Metric / Requirement | Target Specification | Validation Method |
| :--- | :--- | :--- | :--- | :--- |
| **Performance** | NFR-P1 | End-to-End Video Latency | $\le 120\text{ ms}$ over 2.4GHz Wi-Fi (VGA resolution) | Optical timer screen-to-screen benchmark |
| **Performance** | NFR-P2 | Control Command Response Time | $\le 40\text{ ms}$ from screen touch to motor PWM assertion | Oscilloscope / Logic analyzer measurement |
| **Safety & Electrical** | NFR-S1 | Brownout Prevention | Zero MCU brownout resets during simultaneous camera capture, Wi-Fi transmit, and full motor stall | 5V rail voltage logging with digital storage oscilloscope |
| **Safety & Electrical** | NFR-S2 | Boot Pin Isolation | Safe startup without bootloader hangs or flash read corruption across power cycles | 50 consecutive cold-boot power cycle tests |
| **Reliability** | NFR-R1 | Fail-Safe Runaway Prevention | Motors must halt immediately upon phone Wi-Fi disconnection or app backgrounding | Range disconnect test / Airplane mode simulation |
| **Usability** | NFR-U1 | Cross-Platform Phone Compatibility | 100% functional on standard mobile browsers (Chrome on Android, Safari on iOS) without native app compilation | Multi-device browser verification matrix |
| **Maintainability** | NFR-M1 | Clean Firmware & Modular Architecture | Strict separation of FreeRTOS tasks (Core 0: Camera & HTTP Server; Core 1: Motor PWM & Relay Logic) | Static analysis & code architecture review |

---

## 5. System Constraints & Assumptions

1. **Hardware Constraints:**
   - ESP32-CAM AI-Thinker module has limited exposed GPIOs (most pins dedicated to OV2640 and PSRAM).
   - Boot strapping pins (GPIO 0, GPIO 2, GPIO 12, GPIO 15) must strictly adhere to voltage level constraints during power-on.
   - Onboard linear regulator (AMS1117-3.3) is sensitive to 5V input drops; motors must be powered from a dedicated high-current supply or high-amperage buck converter with common ground.
2. **Environmental Constraints:**
   - Wi-Fi range is limited to line-of-sight $30\text{–}50\text{ m}$ using onboard PCB trace antenna, expandable to $100\text{ m}+$ with an external 2.4GHz IPEX dipole antenna.
   - Outdoor sunlight illumination can cause camera auto-exposure oscillation; exposure and gain controls must be adjustable via web API.
3. **Software Assumptions:**
   - Arduino IDE / ESP-IDF / PlatformIO toolchain with ESP32 Arduino Core $\ge 2.0.11$.
   - Phone browser supports modern HTML5 Canvas, Touch Events, and WebSocket / Fetch APIs.
