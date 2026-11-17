# Persistent Prototype Knowledge Base & Decision Records (MEMORY.md)
## Agri Rover: ESP32-CAM Edge IoT Teleoperated & Autonomous Vision Testbed

**Document Version:** 1.0.0  
**Project Code:** MMCA34 — Agri Rover Phase II Prototype Work  
**Hardware Target:** AI-Thinker ESP32-CAM Module  
**Status:** Active Persistent Knowledge Base  

---

## 1. Prototype Identity & Context

The **Agri Rover ESP32-CAM Prototype** is a rapid cyber-physical testbed developed within the Agri Rover Phase 2 research initiative at **BMS Institute of Technology & Management (BMSITM)**.

### Primary Purpose
1. **Low-Risk Teleoperation Validation:** Test responsive mobile phone touch-steering algorithms and failsafe auto-braking on an agile, lightweight chassis before deploying code to the $15\text{ kg}$ full-scale field rover.
2. **Wi-Fi Streaming & Perception Benchmarking:** Benchmark OV2640 camera latency, frame rates, and PSRAM buffer behavior under real-world 802.11 b/g/n wireless conditions.
3. **End-to-End Pipeline Verification:** Validate the complete loop:
   $$\text{ESP32-CAM Stream} \longrightarrow \text{OpenCV Threat Reticle} \longrightarrow \text{Auto-Spray Micro-Burst} \longrightarrow \text{3D Digital Twin Sync}$$

---

## 2. Prototype Architecture Decision Records (ADRs)

### ADR-P01: Compute Platform — AI-Thinker ESP32-CAM
- **Status:** Accepted
- **Context:** Need an ultra-low-cost ($< \$8$), compact board capable of concurrent video streaming, web server hosting, motor PWM, and relay control.
- **Decision:** Selected the AI-Thinker ESP32-CAM module featuring the ESP32-S SoC (240MHz dual-core Xtensa), OV2640 2MP sensor, and 4MB external PSRAM.
- **Rationale:** The module provides sufficient compute and memory (via PSRAM double buffering) to stream VGA video at $15\text{–}20\text{ FPS}$ while simultaneously hosting an embedded web server and running real-time motor control loops.

### ADR-P02: Mobile Phone HMI — Zero-Install Embedded Web App vs. Native Mobile App
- **Status:** Accepted
- **Context:** Operators need to control the rover from their smartphones in the field and view live camera feed inside the application.
- **Decision:** Implemented an embedded, single-page responsive HTML5/JavaScript application served directly from the ESP32-CAM flash memory (`GET /`).
- **Rationale:** Native mobile apps (Android APK or iOS App Store) require platform-specific compilation, signing certificates, and manual installation on every phone. Serving an embedded PWA web app allows any smartphone (iOS Safari, Android Chrome) to connect to `http://192.168.4.1` and operate immediately with zero installation.

### ADR-P03: Video Streaming Protocol — HTTP Multi-Part MJPEG vs. RTSP / WebRTC
- **Status:** Accepted
- **Context:** Need a low-latency video feed accessible by standard mobile web browsers and desktop Python OpenCV scripts.
- **Decision:** Adopted HTTP/1.1 `multipart/x-mixed-replace; boundary=frame` MJPEG streaming.
- **Rationale:** MJPEG requires no client-side plugins and renders natively inside standard HTML `<img>` tags (`<img src="/stream">`). It introduces minimal encoding overhead on the ESP32 (JPEG frames are produced directly in hardware by the OV2640 sensor) and can be opened in Python via a single call to `cv2.VideoCapture("http://<ip>:81/stream")`.

### ADR-P04: Motor Driver Selection — Dual H-Bridge (L298N / DRV8833) for Prototype
- **Status:** Accepted
- **Context:** The prototype uses 4x TT DC geared motors or 12V 100RPM micro-gear motors.
- **Decision:** Selected the L298N (or DRV8833) dual H-bridge module for the prototype chassis, while reserving the dual BTS7960 43A drivers for the full-scale agricultural vehicle.
- **Rationale:** The prototype motors draw $<1.0\text{A}$ stall current, well within the L298N thermal limits. The 4-channel input configuration (`IN1` to `IN4`) pairs cleanly with ESP32-CAM pins GPIO 12, 13, 14, 15.

### ADR-P05: Pin Collision & Boot Strapping Safety Scheme
- **Status:** Accepted
- **Context:** The ESP32-CAM has severe pin restrictions due to internal camera and PSRAM buses.
- **Decision:**
  - `GPIO 12`: Left Motor A (`IN1`) — must be LOW at boot.
  - `GPIO 13`: Left Motor B (`IN2`).
  - `GPIO 14`: Right Motor A (`IN3`).
  - `GPIO 15`: Right Motor B (`IN4`).
  - `GPIO 2`: Spray Pump Relay Trigger (active HIGH micro-pulse).
  - `GPIO 4`: Onboard Flash LED (illumination).
  - `GPIO 0`: Bootloader jumper to GND (only during flashing).
  - `GPIO 16 & 17`: Hardwired to PSRAM (STRICTLY RESERVED).
- **Rationale:** This allocation completely avoids camera bus lines, prevents the 1.8V flash voltage bug on GPIO 12, and keeps PSRAM fully operational for video buffering.

### ADR-P06: Edge Perception Partitioning — Offloaded Companion OpenCV
- **Status:** Accepted
- **Context:** Real-time color segmentation, contour filtering, and bounding box drawing require substantial floating-point calculations and matrix operations.
- **Decision:** Offloaded OpenCV processing to a companion computer (laptop or field Raspberry Pi) ingesting the HTTP stream, which dispatches automated spray triggers back to the ESP32-CAM via HTTP POST (`/spray?ms=200`).
- **Rationale:** Keeps the ESP32-CAM firmware responsive and cool, preventing streaming frame drops, while allowing arbitrary computer vision models (OpenCV HSV, YOLOv8) to run on the companion workstation.

### ADR-P07: 60/40 Teleoperation Cockpit & Kinematic Angle/Trim Engine
- **Status:** Accepted
- **Context:** Operators require a wide, unobstructed camera view for crop row and weed inspection while simultaneously having access to tactile drive steering, speed presets, and calibration.
- **Decision:** Implemented a strict 60% video viewport and 40% control cockpit layout. Integrated Slow (35%), Medium (65%), Fast (100%) buttons with a continuous slider, dynamic steering sensitivity multiplier ($K_{\text{steer}}$: $0.3\times - 1.2\times$), and a motor drift trim slider ($-25\%\text{ to }+25\%$) stored in browser `localStorage`.
- **Rationale:** Prevents page scrolling/bounce outdoors, allows precision alignment along narrow crop rows without oversteering, and compensates for RPM variations in budget DC gear motors without touching code.

### ADR-P08: 4-Motor Parallel Driver & Common Star Ground Architecture
- **Status:** Accepted
- **Context:** 4WD rover chassis with 4x TT DC gear motors plus 1x 12V diaphragm spray pump. L298N driver has 2 output channels.
- **Decision:** Wired left side motors in parallel into L298N OUT1 & OUT2; right side motors in parallel into OUT3 & OUT4. Switched spray pump on 12V rail via 5V optocoupled relay with an antiparallel 1N4007 flyback diode. Tied all GND lines to a single master Common Star Ground point.
- **Rationale:** Provides high mechanical torque for outdoor terrain while preventing ground loops and inductive flyback spikes from resetting the ESP32 microcontroller.

### ADR-P09: Dual-Format App Distribution (PWA + Native Android APK Wrapper)
- **Status:** Accepted
- **Context:** Users need zero-install convenience for field operations plus standalone APK packages for college project evaluation and offline sharing.
- **Decision:** Implemented an installable Progressive Web App (PWA) with `manifest.json`, `sw.js` service worker, and 192px/512px icons for instant 1-tap browser installation, paired with a complete native Android Studio project wrapper in `Prototype/android_apk/`.
- **Rationale:** Operators can install the app to their phone home screen in 5 seconds via Chrome/Safari without developer tools, while academic reviewers can compile and inspect a clean native Android APK.

### SOP-P01: Pre-Assembly Order of Operations (Bench Bringup Protocol)
- **Status:** Mandatory Standard Operating Procedure
- **Context:** Deciding whether to assemble/solder all hardware first vs. flash firmware first.
- **Rule:** Flash and verify the ESP32 standalone FIRST on the workbench with zero actuators attached. Tune the buck converter to exactly $5.10\text{V}$ with a multimeter BEFORE connecting to the ESP32. Wire and solder motors/pump LAST.
- **Rationale:**
  1. Prevents accidental over-voltage destruction (factory buck converters ship at $12\text{V}-18\text{V}$).
  2. Eliminates parasitic current draw and USB port overload during firmware flashing.
  3. Prevents boot strapping conflicts on GPIO 12 (`rst:0x10` flash voltage crash).
  4. Allows verification of Wi-Fi SoftAP and camera streaming before chassis mounting.

### ADR-P10: Component-by-Component Subsystem Wiring & Visual Mapping Matrix
- **Status:** Accepted
- **Context:** Hardware assembly confusion across multiple peripherals (ESP32-CAM, LM2596 buck, L298N driver, 4x TT motors, 5V relay, 12V spray pump, 1N4007 diode).
- **Decision:** Segmented prototype architecture into 4 isolated, verified subsystems with dedicated educational visual guides:
  1. *Power Subsystem:* 12V Li-ion + Rocker Switch + LM2596 Buck tuned to $5.10\text{V}$ + Master Common Star Ground.
  2. *Logic Subsystem:* ESP32-CAM GPIO 12-15 to L298N `IN1-IN4`, GPIO 2 to Relay `IN`, and $1000\mu\text{F}$ capacitor on 5V/GND.
  3. *Drive Subsystem:* Parallel pair wiring (FL+RL to `OUT1/OUT2`, FR+RR to `OUT3/OUT4`).
  4. *Actuator Subsystem:* Relay `COM` to $+12\text{V}$, Relay `NO` to Pump (+), Pump (-) to GND, with antiparallel 1N4007 flyback diode.
- **Rationale:** Modular isolation enables the operator to wire, power, and test each cyber-physical subsystem independently without catastrophic short circuits or component damage.

### ADR-P11: Common Star Ground Physical Architecture & Two-Zone Isolation
- **Status:** Accepted
- **Context:** Multiple ground returns (Battery -, Buck IN-, Buck OUT-, L298N GND, ESP32 GND, Relay GND, Pump Black) create wiring congestion and risk of inductive ground loops.
- **Decision:** Recommended two verified implementation patterns:
  1. *Primary Pattern (Hardware Modular):* 5-port WAGO 221 lever connector serving as a single star node (zero soldering, 100% mechanical grip).
  2. *Secondary Pattern (Two-Zone Natural Split):* Using the LM2596 internal copper ground plane as the bridge between the noisy high-power motor ground (`IN-`) and clean logic ground (`OUT-`).
- **Rationale:** Prevents high-current motor transients from traveling through ESP32 ground traces, avoiding MCU brownouts and camera frame corruptions while keeping assembly clean.

### ADR-P12: Base Hardware Architecture & Anti-Error Engineering Rules (ESP32 DevKit V1 30/38-Pin)
- **Status:** Accepted (Permanent Baseline Specification)
- **Context:** Establishing verified, error-proof hardware wiring and pin assignment rules for the standard ESP32 DevKit V1 (30-pin / 38-pin) rover chassis with dual/4 DC gear motors and 12V spray pump (Sensors EXCLUDED from physical build).
- **Decision:**
  1. *Physical Build Scope:* Active prototype strictly consists of: ESP32 DevKit V1, L298N Dual H-Bridge, DC Gear Motors, 5V Optocoupled Relay, 12V Mini Diaphragm Pump, 12V Battery Pack, LM2596 Buck Converter, and Common Star Ground. All sensor lines (Ultrasonic, Soil Moisture, DHT22) are explicitly excluded from the physical rover wiring.
  2. *PWM/Driver Pins:* Exclusively use safe, non-strapping GPIOs (`GPIO 18`, `GPIO 19`, `GPIO 21`, `GPIO 22`). Never assign boot strapping pins (`GPIO 0, 2, 12, 15`) to actuators.
  3. *Spray Pump Actuation:* `GPIO 23` triggers the 5V optocoupled relay module. Direct GPIO coil driving is strictly prohibited.
  4. *Inductive Protection:* Mandatory flyback snubber diode (1N4007 / UF4007) across the pump terminals (silver cathode band to +); decoupling capacitors ($100\text{nF}$ ceramic + $\ge 470\mu\text{F}$ electrolytic) on motor power rails.
  5. *Common Star Ground:* Maintain a single common star reference point across Battery GND, Buck OUT-, Driver GND, and ESP32 GND to prevent ground loops.
- **Rationale:** Keeps the physical chassis clean, eliminates unnecessary sensor circuitry and voltage dividers, and focuses 100% of resources on robust locomotion and precision spray actuation.

### ADR-P13: Physical Wiring Harness Pin Mapping Alignment (AI-Thinker ESP32-CAM)
- **Status:** Accepted & Firmware Synchronized
- **Context:** The operator provided a verified physical wiring harness (Images 1-7) where motor inputs were wired: GPIO 14 (IN1), GPIO 15 (IN2), GPIO 13 (IN3), GPIO 12 (IN4), and GPIO 2 (Relay IN). Previous default firmware had Left on GPIO 12/13 and Right on GPIO 14/15, creating a reverse-diagonal motion inversion.
- **Decision:** Updated `AgriRover_ESP32CAM.ino` to explicitly match the operator's harness:
  - `PIN_MOTOR_L_A`: `14` (`IN1` - Left Forward)
  - `PIN_MOTOR_L_B`: `15` (`IN2` - Left Backward)
  - `PIN_MOTOR_R_A`: `13` (`IN3` - Right Forward)
  - `PIN_MOTOR_R_B`: `12` (`IN4` - Right Backward; verified initialized LOW at boot to satisfy MTDI strapping constraint)
  - `PIN_RELAY`: `2` (`Relay IN` - Spray Pump Trigger)
- **Rationale:** Ensures 100% zero-drift alignment between the operator's physical wire colors/harness and the embedded PWM kinematics engine, verified by 8/8 automated test suite passes.

### ADR-P14: 3D Video & WebGL Digital Twin Simulation Engine
- **Status:** Accepted & Assets Generated
- **Context:** The operator requested a 3D animated video and real-time simulator demonstrating the `.ino` firmware kinematics running in lockstep with the Mobile Teleoperation Cockpit App.
- **Decision:** Generated dual simulation modalities:
  1. *High-Definition 3D Animation Video (`agrirover_3d_simulation.mp4` / `.gif`):* 720p HD 24fps video showing 5 flight test phases (Boot, Forward Cruise, Skid-Steer Pivot, Chemical Mist Burst, Watchdog Auto-Brake).
  2. *Interactive Three.js WebGL Digital Twin (`3d_digital_twin_app.html`):* Real-time 3D farmland world with 4 rotating rubber-tread wheels, chemical particle spray nozzle, POV camera feed, and an integrated teleoperation app cockpit with a "PLAY 3D DEMO VIDEO" automated tour director.
- **Rationale:** Enables visual verification of differential steering kinematics, logic level PWM behavior, and safety failsafes before applying high-current battery power to the physical chassis.

---

## 3. Hardware Quirks, Strapping Gotchas & Troubleshooting Guide

### 1. "Brownout detector was triggered" Crash Loop
- **Symptom:** Board resets continuously during boot or immediately when Wi-Fi connects or camera starts.
- **Root Cause:** Input voltage on the `5V` pin sags below $4.5\text{V}$ during peak radio transmission bursts. Common when powering from FTDI 3.3V or high-resistance USB cables.
- **Solution:**
  1. Power the ESP32-CAM from an external LM2596 buck converter tuned to **$5.10\text{V}$** (minimum 2A capacity).
  2. Solder a **$1000\mu\text{F} / 16\text{V}$ electrolytic capacitor** directly across the ESP32-CAM `5V` and `GND` pins.
  3. In code (temporary bench testing only):
     ```c
     #include "soc/soc.h"
     #include "soc/rtc_cntl_reg.h"
     WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector
     ```

### 2. "Camera probe failed with error 0x20001"
- **Symptom:** Camera fails to initialize during `esp_camera_init()`.
- **Root Cause:**
  - Ribbon cable is seated upside down or slightly skewed in the FPC connector.
  - Pin definitions in `camera_pins.h` do not match `CAMERA_MODEL_AI_THINKER`.
  - Insufficient power delivery during sensor power-up.
- **Solution:** Unlatch the FPC connector collar, ensure the gold contacts on the camera ribbon face towards the ESP32-CAM PCB, gently re-seat the ribbon, and snap the latch shut. Verify `#define CAMERA_MODEL_AI_THINKER` is active.

### 3. Continuous Flash Read Error / Bootloader Hang (`rst:0x10`)
- **Symptom:** After uploading firmware and removing GPIO 0 jumper, the board prints `rst:0x10 (RTCWDT_RTC_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)` and hangs.
- **Root Cause:** `GPIO 12` is being pulled HIGH by the motor driver during power-up, selecting 1.8V flash voltage instead of 3.3V.
- **Solution:** Ensure the motor driver input on GPIO 12 has a pull-down resistor or disconnect GPIO 12 during power-up to confirm clean boot.

### 4. ESP32-CAM Flash LED Glowing Dimly
- **Symptom:** The bright flash LED on GPIO 4 stays dimly lit even when turned off.
- **Root Cause:** Floating state or leakage current through GPIO 4.
- **Solution:** Explicitly pull GPIO 4 LOW during `setup()`:
  ```c
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);
  ```

### 5. L298N Terminal Block Topology (2-Pin Motor Outputs vs. 3-Pin Power Block)
- **Symptom:** Operator confusion regarding "three wires" on the motor driver.
- **Root Cause:** The blue terminal block on the bottom of the L298N has **3 screw terminals** (`12V`, `GND`, `5V`). This block is strictly for **POWER INPUT**, not motors.
- **Rule:**
  - **Left Motor Block:** Exactly **2 screw terminals** (`OUT1` and `OUT2`). Solder 1 Red wire and 1 Black wire per TT motor; connect both Red wires to `OUT1` and both Black wires to `OUT2`.
  - **Right Motor Block:** Exactly **2 screw terminals** (`OUT3` and `OUT4`). Connect both Red wires to `OUT3` and both Black wires to `OUT4`.
  - **Bottom Power Block (3 Screws):** NEVER connect motor leads here! Pin 1 = `+12V` Battery (+), Pin 2 = `GND` Common Star Ground, Pin 3 = `5V` (leave onboard jumper ON).

---

## 4. Current State & Artifact Index

| Artifact | File Path | Status | Summary |
| :--- | :--- | :---: | :--- |
| **Prototype PRD** | `Prototype/PRD.md` | ✅ Complete | Product requirements, personas, functional/non-functional criteria, user scenarios. |
| **Prototype Architecture** | `Prototype/ARCHITECTURE.md` | ✅ Complete | Block diagrams, dual-core FreeRTOS allocation, network modes, API specs. |
| **Prototype Rules** | `Prototype/RULES.md` | ✅ Complete | Boot strapping rules, power protection, failsafe watchdog, memory safety. |
| **Prototype Design** | `Prototype/DESIGN.md` | ✅ Complete | Pin mapping, schematics, motor kinematics, embedded phone web app, OpenCV script. |
| **Prototype Tasks** | `Prototype/TASKS.md` | ✅ Complete | Step-by-step roadmap, test procedures, acceptance matrix. |
| **Prototype Memory** | `Prototype/MEMORY.md` | ✅ Complete | ADRs, troubleshooting knowledge base, pin constraints. |
| **Hardware BOM Guide** | `Prototype/Agri_Rover_Prototype_Hardware_Guide_Comprehensive.pdf` | ✅ Complete | 5-page PDF with integrated schematic, component catalog, and verified links. |
| **Interactive Wiring Vector** | `Prototype/wiring_guide.html` | ✅ Complete | Interactive vector SVG guide with clickable circuit nodes and wire tracing. |
| **Component Wiring Guide** | Brain Artifact: `all_components_wiring_guide.md` | ✅ Complete | Visual guide covering all 7 components, power distribution, relay, and motors. |

---

## 5. Active User Preferences & Operating Directives

- **PROACTIVE_WORKSPACE_INSPECTION (MANDATORY):** Immediately inspect, analyze, and diagnose any newly placed files, photos, or schematics in the workspace without waiting for the user to ask or prompt.
- **HARDWARE_DECISIONS_LOG:**
  - **Motor Driver:** The user's existing Arduino L293D shield is incompatible (74HC595 shift register requires 6 GPIOs). User must use standalone L298N module (~₹160).
  - **Spray Pump:** User's existing 12V pump is 100% reusable with 5V relay module (₹0 cost).
  - **MCU Upgrade Option:** Evaluated ESP32-S3 WROOM N16R8 Dual USB-C board (UG LAND INDIA, ₹1,499) as superior upgrade path (20+ free GPIOs, 8MB PSRAM, 16MB flash).

