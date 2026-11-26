# Project Task Roadmap & Traceability Matrix (TASKS.md)
## Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring

**Document Version:** 2.0.0  
**Project Code:** MMCA34 (Project Work - Phase I & Phase II, 2025–2027 Batch)  
**Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru  
**Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)  

---

## 1. Phase 1: Completed Tasks & Verification Matrix

All tasks listed below have been completed, verified on physical hardware and/or the 3D WebGL Digital Twin, and documented in the official Phase 1 academic submissions.

### 1.1 Milestone 1: Requirements, System Architecture & Feasibility
- [x] **TASK-101: Literature Review & Gap Analysis**
  - Investigated conventional tractor boom sprayers, agricultural drones, and monolithic commercial UGVs.
  - Formulated the targeted AI micro-burst paradigm.
- [x] **TASK-102: Problem Statement, Aim & Measurable Objectives**
  - Formulated formal Problem Statement, overarching Project Aim, and 5 discrete engineering objectives.
- [x] **TASK-103: Software Requirements Specification (SRS)**
  - Authored Functional Requirements (FR-1 to FR-8) and Non-Functional Requirements (NFR-P1 to NFR-M1).
- [x] **TASK-104: UN SDG & ESG Compliance Definition**
  - Mapped project features to UN SDG 2 (Zero Hunger - Target 2.4), SDG 12 (Target 12.4), and SDG 15.
  - Documented Environmental, Social, and Governance (ESG) compliance matrix.

### 1.2 Milestone 2: 3D WebGL Digital Twin & Simulator Development
- [x] **TASK-105: 3D Farmland Environment & Crop Rows (Three.js)**
  - Implemented procedural farmland terrain, textured ground mesh, and row-crop layout ($50\text{–}70\text{ cm}$ spacing).
- [x] **TASK-106: Kinematic Rover 3D Mesh & Suspension Simulation**
  - Built 3D CAD rover model with Rocker-Bogie rocker arms, mud-tread wheels, chemical reservoir, and spray booms.
- [x] **TASK-107: Real-Time Particle Mist Spray Simulation**
  - Implemented instanced particle emitters simulating pressurized fluid cones matching solenoid triggers.
- [x] **TASK-108: Interactive HUD & Telemetry Dashboard**
  - Developed responsive React dashboard with battery gauge, speed presets (30%, 60%, 100%), and status badges.
- [x] **TASK-109: Skid-Steer Physics & Zero-Radius Point Turning**
  - Implemented in-place pivot turning ($R = 0$) and deadband lane-lock steering routines in Three.js.

### 1.3 Milestone 3: Embedded Hardware Interfacing & Motor Driver Integration
- [x] **TASK-110: 4WD Skid-Steer Chassis Assembly**
  - Built physical 4-wheel rover chassis with high-torque 12V DC geared motors and mud-tread all-terrain tires.
- [x] **TASK-111: Dual BTS7960 43A H-Bridge Driver Wiring**
  - Wired left and right motor banks to dual BTS7960 drivers on Raspberry Pi GPIO pins (BCM 12, 13, 17, 27 and BCM 18, 19, 22, 23).
- [x] **TASK-112: Python Motor Kinematics Daemon (`motor_control_pi.py`)**
  - Implemented software PWM speed modulation, speed clamping ($-100$ to $+100$), and smooth directional dead-time.

### 1.4 Milestone 4: Computer Vision Pipeline & Precision Actuation
- [x] **TASK-113: OpenCV Edge Vision Daemon (`camera_stream.py`)**
  - Configured 1080p camera feed processing at $>15\text{ FPS}$ on Raspberry Pi 4.
  - Implemented HSV color thresholding: Purple mask ($[130, 50, 50]$ to $[160, 255, 255]$) and Red weed mask.
- [x] **TASK-114: Directional Solenoid Valve & Pump Integration (`pesticide_sprayer.py`)**
  - Built optoisolated relay and MOSFET driver circuits for dual 12V solenoid valves (GPIO 24, GPIO 25) and pump (GPIO 26).
  - Implemented calibrated **200ms micro-burst actuation logic**, achieving up to **80% chemical pesticide volume reduction**.

### 1.5 Milestone 5: In-Situ Soil Health Probing & Safety Interlocks
- [x] **TASK-115: Motorized Linear Actuator Mechanism**
  - Installed NEMA 17 stepper linear slide ($100\text{ mm}$ stroke) carrying electrochemical NPK, pH, and soil moisture probes.
- [x] **TASK-116: Soil Probing Drive Interlock**
  - Implemented safety lockout: drive motor PWM forced to 0% during active soil probe extension.
- [x] **TASK-117: Georeferenced Ground Heatmap Ring Generation**
  - Serialized sampled NPK/pH readings and rendered color-coded concentric decals on the 3D WebGL ground plane.
- [x] **TASK-118: Hardware Under-Voltage Emergency Shutdown**
  - Implemented continuous ADC battery voltage supervisor: automated system halt when $V_{batt} \le 12.0\text{V}$ ($\le 12\%$).

---

## 2. Phase 1 Verification & Test Traceability Matrix

| Test Case ID | Requirement | Description / Input | Expected Result | Phase 1 Status |
| :---: | :---: | :--- | :--- | :---: |
| **TC-01** | FR-1 | Press 'W' key in Manual Mode | Rover accelerates forward smoothly, motor PWM set to selected preset (30%, 60%, 100%). | **PASS** |
| **TC-02** | FR-1 | Press 'A' key in Manual Mode | Left motor bank slows/reverses, right advances; rover turns left. | **PASS** |
| **TC-03** | FR-2, FR-3 | Enable Lane Lock & Autonomous Mode | Rover tracks row centerline via Hough guidelines; executes zero-radius point turn at end of row. | **PASS** |
| **TC-04** | FR-5 | Pest contour detected in Left camera frame | GPIO 24 (Left Solenoid) asserts HIGH for 200ms, Right Solenoid remains LOW, Pump runs at 75%. | **PASS** |
| **TC-05** | FR-6 | Press 'P' key / Click Probe UI button | Rover drive motors immediately lock (0% PWM), linear actuator extends 100mm, NPK/pH data logged. | **PASS** |
| **TC-06** | FR-7 | Battery voltage drops $\le 12.0\text{V}$ ($\le 12\%$) | Emergency shutdown triggers: motor PWM = 0%, direction enables LOW, all chemical valves closed. | **PASS** |
| **TC-07** | FR-1 | Virtual Joystick Continuous Hold | Drive packets stream continuously at 75ms; rover moves smoothly with zero stutter. | **PASS** |
| **TC-08** | FR-4 | Spray Burst Trigger (1s Actuation) | Relay fires Active-LOW for 1000ms; pump primes and delivers chemical micro-burst. | **PASS** |
| **TC-09** | FR-1 | Multi-Modal Split-Thumb Teleoperation | Simultaneous multi-touch tracking on Left (Throttle) and Right (Steering) sticks; mode switching with localStorage persistence. | **PASS** |
| **TC-10** | FR-1, FR-4 | Concurrent Video Stream & Drive Teleoperation | Port 81 isolated stream runs at ~22 FPS without starving Port 80 /drive packets; relay polarity toggle stops boot pump runs. | **PASS** |
| **TC-11** | FR-1 | Symmetrical Dual-Channel Skid-Steer Verification | Independent left (OUT1/2) and right (OUT3/4) bench motor diagnostics with isolated LEDC Timer 3 camera clocking. | **PASS** |
| **TC-12** | FR-1, FR-8 | Client-Side Hardware-Accelerated Camera Stream Rotation & Orientation Persistence | Instant 0°/90°/180°/270° CSS GPU transforms and mirror flip with scale(0.72) aspect preservation and localStorage recall. | **PASS** |
| **TC-13** | FR-1 | Post-Camera LEDC Peripheral Initialization & Actuator Drive Recovery | Calling ledcSetup/Attach after esp_camera_init preserves motor PWM channel mapping on GPIO 14, 15, 13, 12. | **PASS** |

---

## 2.1 Physical Prototype Bench Verification Matrix
- [x] **TASK-P01: 4-Motor TT Skid-Steer Polarity Alignment** (OUT1/2 Red/Black & OUT3/4 Red/Black verified forward)
- [x] **TASK-P02: Continuous Touch Heartbeat Stream** (75ms transmission loop preventing 500ms watchdog stall)
- [x] **TASK-P03: 1-Second Precision Spray Actuation & Active-LOW Relay Driver** (1000ms burst duration with manual bench override)
- [x] **TASK-P04: Multi-Modal Ergonomic Teleoperation Interface** (Dual-Thumb RC split-sticks + single 360° joystick + D-Pad + duration selector)
- [x] **TASK-P05: Dual-Port Socket Isolation & Dynamic Relay Polarity Diagnostics** (Port 80 control + Port 81 stream isolation, 28ms frame pacing, `isDriveInFlight` latch, live Active-HIGH/LOW toggle via `/spray?polarity=`)
- [x] **TASK-P06: Symmetrical 4-Motor Drive Bench Diagnostics & Timer Isolation** (LEDC Timer 3 / Channel 7 camera isolation, throttled `/drive` serial telemetry, web cockpit Left/Right motor test buttons)
- [ ] **TASK-P07: Power Rail Brownout & Left Motor Stall/Short Circuit Isolation** (Inspect OUT1/2 wiring for shorts, verify mechanical wheel free-spin, measure 3S battery voltage $\ge 11.1\text{V}$, verify LM2596 buck recovery)
- [x] **TASK-P08: SoftAP Modem Sleep & Micro-Disconnect Elimination** (Pure `WIFI_AP`, `WiFi.setSleep(false)`, `19.5dBm` TX power, 200ms `AbortController` latch release, `img.onerror` auto-reconnect)
- [x] **TASK-P09: Client-Side Hardware-Accelerated Camera Stream Rotation & Orientation Persistence** (One-touch on-screen quick-rotate button `[🔄 0°]`, 4-quadrant orientation grid in Settings modal, horizontal mirror flip, 0% CPU ESP32 load, and localStorage persistence)
- [x] **TASK-P10: Post-Camera LEDC Initialization & Motor Channel Integrity** (Moved motor PWM attachment after `esp_camera_init` to prevent peripheral driver reset, restoring motor drive signals on pins 14, 15, 13, 12)

---

## 3. Phase 2: Active Roadmap, Epics & Tasks

Phase 2 transitions Agri Rover from a single-rover prototype with color-thresholding vision into a fully autonomous, field-hardened, commercial-grade agricultural robotics platform.

```
+---------------------------------------------------------------------------------------------------------+
|                                    PHASE 2 IMPLEMENTATION TIMELINE                                      |
+---------------------------------------------------------------------------------------------------------+
| Milestone Activity                        | Month 1 | Month 2 | Month 3 | Month 4 | Month 5 | Month 6 |
+-------------------------------------------+---------+---------+---------+---------+---------+---------+
| Epic 1: Edge AI Quantized YOLOv8 Upgrade  | [█████] | [█████] |         |         |         |         |
| Epic 2: LoRaWAN Telemetry & IoT Mesh      |         | [█████] | [█████] |         |         |         |
| Epic 3: Centimeter RTK-GPS Navigation     |         |         | [█████] | [█████] |         |         |
| Epic 4: Autonomous Solar Docking Station  |         |         |         | [█████] | [█████] |         |
| Epic 5: Cloud Farm Analytics & Dashboard  |         |         |         |         | [█████] | [█████] |
+---------------------------------------------------------------------------------------------------------+
```

### Epic 1: Edge AI Deep Learning Model (YOLOv8 INT8 Edge Inference)
*Target: Replace basic HSV color segmentation with a deep learning object detection model running on the edge.*

- [ ] **TASK-201: Agricultural Pest & Crop Disease Dataset Assembly**
  - Collect and annotate $> 3,000$ high-resolution images of foliar pests (fall armyworm, caterpillars, aphids) and common weed species.
  - Perform domain-specific data augmentations (varying sunlight, partial occlusion, mud splash).
  - *Acceptance Criteria:* Annotated YOLO-format dataset split 70/20/10 with mAP50 benchmark $\ge 0.88$.
- [ ] **TASK-202: YOLOv8-nano (YOLOv8n) Model Training & Pruning**
  - Train custom YOLOv8n network; prune redundant convolutional weights to reduce model size to $< 6\text{ MB}$.
  - *Acceptance Criteria:* Validation mAP50:95 $\ge 0.75$ across target pest and weed classes.
- [ ] **TASK-203: INT8 Quantization & NPU Acceleration (TFLite / ONNX / Coral)**
  - Quantize model to 8-bit integer precision (INT8) using post-training quantization.
  - Deploy on Google Coral USB Accelerator or Raspberry Pi 4 CPU with edge runtime optimizations.
  - *Acceptance Criteria:* Inference latency $\le 30\text{ ms}$ per frame ($\ge 30\text{ FPS}$) with zero frame drops.
- [ ] **TASK-204: Multi-Class Targeted Spraying Logic**
  - Expand `pesticide_sprayer.py` to support dynamic spray recipes based on recognized threat type (insecticide for caterpillars vs herbicide for weeds).

---

### Epic 2: Long-Range Telemetry & Wireless Mesh (LoRaWAN)
*Target: Provide robust kilometers-range field telemetry across rural agricultural landscapes lacking cellular 4G/5G or WiFi.*

- [ ] **TASK-205: SX1262 LoRaWAN Transceiver Integration**
  - Interface SX1262 868MHz / 915MHz LoRa SPI module with Raspberry Pi 4.
  - *Acceptance Criteria:* Verified bidirectional packet transmission over line-of-sight distance $\ge 2.5\text{ km}$.
- [ ] **TASK-206: Compact Binary Telemetry Protocol**
  - Design a compact binary serialization schema (Protobuf / CBOR) encoding GPS pose, battery, NPK, and threat events into $\le 51\text{ bytes}$ per LoRaWAN packet.
- [ ] **TASK-207: Offline Store-and-Forward Telemetry Buffer**
  - Implement SQLite edge buffer that queues telemetry frames during RF link dropouts and synchronizes on reconnect.

---

### Epic 3: Centimeter-Level Navigation & Autonomous Headland U-Turns (RTK-GPS + IMU)
*Target: Enable centimeter-accuracy autonomous waypoint navigation and automated row transitions without human supervision.*

- [ ] **TASK-208: Dual-Frequency RTK GNSS Receiver Integration**
  - Mount an RTK GNSS module (u-blox ZED-F9P) on the rover with a stationary local base station.
  - *Acceptance Criteria:* Real-time kinematic fix with horizontal positioning accuracy $\le 2.5\text{ cm}$.
- [ ] **TASK-209: 9-DOF IMU Sensor Fusion (Extended Kalman Filter)**
  - Integrate BNO085 9-axis IMU with RTK GNSS using an Extended Kalman Filter (EKF) for drift-free heading estimation.
- [ ] **TASK-210: Autonomous Headland U-Turn & Row Transition Planner**
  - Implement Dubins path and Reeds-Shepp curve algorithms to plan smooth, collision-free $180^\circ$ transitions from Row $N$ to Row $N+1$ upon reaching row end markers.

---

### Epic 4: Autonomous Solar Docking & Recharging Station
*Target: Provide perpetual field energy autonomy with zero manual battery swapping.*

- [ ] **TASK-211: Mechanical Docking Guide & Contact Charging Plates**
  - Construct a weatherized docking station with spring-loaded copper contact pads and physical cone guide alignment.
- [ ] **TASK-212: Solar Photovoltaic & MPPT Charging Subsystem**
  - Install a 100W monocrystalline solar panel coupled with a 12V MPPT solar charge controller.
- [ ] **TASK-213: Autonomous Homing & Precision Docking Guidance**
  - Implement ArUco fiducial marker optical alignment on the docking station for millimetric homing accuracy.

---

### Epic 5: Cloud Farm Analytics & Web Agronomic Dashboard
*Target: Enterprise dashboard for regional agronomists and cooperative farming clusters.*

- [ ] **TASK-214: Time-Series Farm Database (TimescaleDB / InfluxDB)**
  - Deploy secure cloud backend storing georeferenced historical NPK, pH, and pesticide consumption logs.
- [ ] **TASK-215: Web GIS Heatmap Portal**
  - Build interactive Leaflet / Mapbox map visualization showing field-level nitrogen, phosphorus, and moisture spatial distributions.
- [ ] **TASK-216: Automated Variable Rate Application (VRA) Prescription Generator**
  - Generate automated agronomic prescription maps advising farmers on exact localized fertilizer quantities based on probe trends.

---

### Epic 6: In-Situ Soil Health Probing & Localized Closed-Loop Irrigation (FR-9)
*Target: On-demand mechanical soil penetration, real-time capacitive moisture feedback, and localized targeted water sprinkling.*

- [x] **TASK-217: In-Situ Soil Moisture Probing & Localized Sprinkler Delivery Subsystem**
  - Mechanical vertical deployment mechanism (MG996R servo rack-and-pinion or 12V linear actuator slide).
  - Integration of corrosion-resistant Capacitive Soil Moisture Sensor v1.2 with ADC1 / comparator input.
  - Non-blocking sequential interlock FSM: drive motor lockout $\to$ probe extension $\to$ stabilization pause $\to$ ADC sampling $\to$ retraction $\to$ conditional $2.5\text{s}$ localized sprinkler micro-burst.
  - Physical Assembly Work Package: Soldering (diode, DC jack, pump leads), mechanical mounting, direct 12V wiring, and DMM continuity verification (Est: 2.5–3.5 hours).
  - Cockpit UI integration with one-touch "🌱 Sample Moisture & Water" HUD button and real-time status feedback.
  - Remote Git synchronization: Published and tracked upstream on GitHub at `https://github.com/thanmaym08/AGRI-ROVER-PHASE-2.git`.

---

### Epic 7: State Sponsorship & Academic Grant Proposal (KSCST SPP 50th Series)
*Target: Official submission for Karnataka State Council for Science and Technology (KSCST) 50th Series Student Project Programme sponsorship.*

- [x] **TASK-218: KSCST 50th Series SPP Project Proposal & Submission Package**
  - Authored comprehensive KSCST SPP Project Proposal document based on Raspberry Pi 4 Model B, Dual BTS7960 43A motor drivers, 10–20 kg heavy-load torque derivation, smartphone app teleoperation, and precision solenoid chemical micro-spraying (`KSCST_SPP_AgriRover_Project_Proposal.docx` & `KSCST_SPP_AgriRover_Project_Proposal.pdf`).
  - Student Team updated to 2 members: Thanmay M (Team Leader, `1BY24MC095`) and Mohit S (`1BY24MC063`). Keerthana, Mohan, and Monica removed per user instruction.
  - Institutional Leadership synchronized: Project Guide Dr. Dwarakanath G V, HOD Dr. M. Sridevi (Dept. of MCA), College SPP Coordinator Dr. Manjunath (Dept. of Mechanical Engineering), and Principal Dr. Mohan Babu G N.
  - Generated standalone 1-page Declaration and Endorsement form strictly formatted for institutional signing today (`KSCST_Declaration_and_Endorsement_Form.pdf`).
  - Created complete Google Form submission guide with exact copy-paste fields and instructions for `https://forms.gle/VPPewZnbUhw1V8KdA` (`KSCST_GOOGLE_FORM_SUBMISSION_GUIDE.md`).
