# Product Requirements Document (PRD)
## Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring

**Document Version:** 2.0.0  
**Project Code:** MMCA34 (Project Work - Phase I & Phase II, 2025–2027 Batch)  
**Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru  
**Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)  
**Last Updated:** September 2026  
**Status:** Phase 1 Complete / Phase 2 Active Development  

---

## 1. Executive Summary & Vision

### 1.1 Problem Statement
Modern agriculture is challenged by escalating chemical pesticide costs, acute rural labor shortages, environmental contamination, and systemic soil degradation. Traditional crop spraying relies on broad-area blanket broadcasting via tractor-mounted boom sprayers or manual knapsack systems. This distributes uniform chemical dosages across entire fields, resulting in:
1. **Severe Chemical Wastage:** Up to 70–80% of applied agrochemicals are wasted on uninfected plants or bare soil.
2. **Environmental & Soil Toxicity:** Chemical leaching pollutes groundwater aquifers, acidifies topsoil, and destroys beneficial subterranean microbial biomes.
3. **Severe Occupational Hazards:** Direct human inhalation and dermal contact with organophosphates and carcinogenic pesticides cause chronic occupational diseases among farm workers.
4. **Lack of Localized Soil Intelligence:** Conventional farms lack accessible, real-time ground-truth soil nutrient monitoring (NPK, pH, moisture), leading to indiscriminate over-fertilization.
5. **High Testing & Prototyping Barrier:** Testing autonomous agricultural robotics directly in real fields incurs heavy physical damage risks and prohibitive operational expenses for smallholder farmers and researchers.

### 1.2 System Vision
**Agri Rover** is an intelligent, cyber-physical Unmanned Ground Vehicle (UGV) engineered specifically for row-crop precision agriculture. The platform operates directly within crop rows, utilizing:
- **Edge Computer Vision:** Sub-second localized identification of weeds and foliar pests (e.g., caterpillars) via OpenCV.
- **Directional Micro-Burst Actuation:** High-speed 12V solenoid valves that target detected pests with millisecond-accuracy chemical pulses, cutting pesticide usage by up to 80%.
- **In-Situ Electrochemical Soil Probing:** Motorized linear actuator deploying NPK, pH, and soil moisture probes to build real-time georeferenced soil fertility heatmaps.
- **3D WebGL Digital Twin:** A zero-installation, browser-based 3D digital simulation running on React and Three.js with full kinematic skid-steer physics, zero-radius point turns, and telemetry streaming for safe, zero-cost virtual validation before physical deployment.

---

## 2. Target Personas & User Journeys

### 2.1 User Personas

| Persona | Role | Key Needs | Pain Points Solved |
| :--- | :--- | :--- | :--- |
| **Farm Operator / Field Manager** | Daily crop health monitoring, chemical spraying, soil sampling. | Simple WASD teleoperation, automated crop row tracking, minimal chemical exposure, clear status telemetry. | Eliminates manual toxic spraying; automates row navigation; provides instant visual confirmation of battery and tank levels. |
| **Agricultural Scientist / Agronomist** | Soil fertility evaluation, pest trend analysis, chemical dosage optimization. | Georeferenced NPK, pH, and moisture logs; localized spray logs; chemical dosage comparison data. | Replaces manual soil sample collection with automated mechanical probing; generates field fertility heatmaps. |
| **Robotics & AI Engineer / Student** | Hardware interfacing, computer vision tuning, navigation algorithm design. | Modular Python controllers, transparent GPIO maps, zero-risk virtual simulation environment. | 3D WebGL Digital Twin allows rapid testing of navigation and spray triggers without risking physical hardware collision or brownouts. |

### 2.2 Operational User Journeys

#### Journey 1: Autonomous Precision Patrol & AI Spraying
1. Operator places Agri Rover at the start of a crop row and selects **Autonomous Guidance** + **Lane Lock** mode on the dashboard.
2. The rover advances along the row centerline at calibrated cruise speed (60% PWM).
3. The forward camera stream is processed at $>15$ FPS on the Raspberry Pi 4.
4. Upon detecting a caterpillar or weed cluster in the left frame segment:
   - Rover calculates horizontal pixel offset.
   - Controller activates GPIO 24 (Left Solenoid Valve) for a 200ms calibrated micro-burst while running pump at 75% PWM.
   - Right valve remains closed; zero chemical is discharged on healthy foliage.
   - Threat event, bounding coordinates, and chemical dosage are logged to telemetry.
5. At the end of the crop row, the rover executes an automated zero-radius point turn to align with the adjacent row.

#### Journey 2: In-Situ Ground Soil Probing
1. Operator commands a soil test via UI button or keyboard trigger (`P` key).
2. Rover drive motors are instantly immobilized for mechanical stability.
3. The NEMA stepper-driven linear actuator drives the multi-parameter probe 100mm into the soil bed.
4. System pauses for sensor stabilization (500ms) and acquires NPK, pH, and capacitive moisture data.
5. Linear actuator retracts to transport position.
6. The georeferenced data point is rendered as a permanent color-coded heatmap ring on the 3D Digital Twin ground plane and stored in local telemetry logs.

---

## 3. Product Scope & Functional Requirements (FR)

### 3.1 Traceability Matrix of Functional Requirements

| ID | Requirement Name | Description | Priority | Primary Actor | Phase 1 Status | Phase 2 Scope |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **FR-1** | Manual Teleoperation & Speed Control | Full manual vehicle driving using WASD keys or mobile touch cockpits with selectable speed presets (30% Creep, 60% Cruise, 100% Sprint PWM). | High | Farm Operator | ✅ Completed & Tested | Multi-modal mobile cockpit with dual-port video/command isolation. |
| **FR-2** | Autonomous Guidance & Centerline Tracking | Proportional steering control that tracks crop row guidelines and maintains rover centering within 50–70cm row spacings. | High | Autonomous AI / Operator | ✅ Completed in Sim & Edge | Enhance with RTK-GPS waypoint navigation. |
| **FR-3** | Lane Lock & Zero-Radius Point Turning | Strict single-row corridor constraint with in-place zero-radius pivot turns ($0.0\text{ m}$ turning radius) at row boundaries. | High | Operator / System | ✅ Completed & Tested | Implement automated row-end headland U-turns. |
| **FR-4** | Option 1: Blanket Chemical Spraying | Continuous dual-nozzle spray coverage with adjustable diaphragm pump PWM duty cycle (0–100%). | Medium | Farm Operator | ✅ Completed & Tested | Implement pressure sensor feedback flow regulation. |
| **FR-5** | Option 2: Precision AI Targeted Spraying | Edge OpenCV segmentation identifying foliar weeds and caterpillars, triggering directional solenoid valves with 200ms pulses. | Critical | Edge AI Engine | ✅ Completed (HSV Masking) | Migrate to quantized YOLOv8n edge AI model. |
| **FR-6** | In-Situ Motorized Soil Probing | Drive motor lockout followed by linear actuator deployment to acquire and log NPK, pH, and soil moisture metrics. | High | Farm Operator / Autonomous | ✅ Completed & Tested | Integrate RS485 Modbus industrial NPK sensor probe. |
| **FR-7** | Hardware Safety & Battery Cutoff | Real-time voltage monitoring with automated emergency shutdown when battery drops $\le 12.0\text{V}$ ($\le 12\%$). | Critical | Safety Supervisor Node | ✅ Completed & Tested | Add automated return-to-dock on low battery. |
| **FR-8** | 3D WebGL Digital Twin Simulator | Interactive Three.js/WebGL scene with OrbitControls, Rocker-Bogie wheel suspension kinematics, particle mist, and live telemetry. | Critical | Operator / Developer | ✅ Completed & Hosted | Add dynamic shadow mapping and realistic crop physics. |
| **FR-9** | In-Situ Soil Moisture Probing & Localized Sprinkling | Motorized vertical probe deployment (touch-button triggered) measuring volumetric soil moisture followed by localized targeted water sprinkling on dry detection. | High | Farm Operator / Autonomous | Pending Implementation | Physical mechanism assembly, capacitive sensor integration, and pump sprinkler sequence. |

---

## 4. Non-Functional Requirements (NFR)

| Category | Identifier | Metric / Requirement | Target Specification | Validation Method |
| :--- | :--- | :--- | :--- | :--- |
| **Performance** | NFR-P1 | Vision Processing Latency | $\ge 15\text{ FPS}$ on Raspberry Pi 4 Model B (4GB) | Frame timer benchmarking |
| **Performance** | NFR-P2 | Solenoid Actuation Response | Actuation trigger within $\le 50\text{ ms}$ of threat bounding box detection | Logic analyzer / GPIO timestamps |
| **Performance** | NFR-P3 | Telemetry Transmission Latency | End-to-end telemetry update latency $< 100\text{ ms}$ | WebSocket ping/pong monitoring |
| **Safety & Reliability** | NFR-S1 | Low Battery Emergency Lockout | Motor PWM cutoff and valve closure within $10\text{ ms}$ of sensing $V_{batt} \le 12.0\text{V}$ | Unit Test UT-06 / Voltage bench test |
| **Safety & Reliability** | NFR-S2 | Soil Probing Drive Interlock | Motor drive PWM must be forced to 0% during linear actuator probe stroke | Interlock assertion verification |
| **Availability** | NFR-A1 | Offline Simulator Operation | 3D WebGL Digital Twin must run 100% offline in modern browser without cloud dependencies | Chrome/Firefox offline service worker test |
| **Usability** | NFR-U1 | Operator Interface Simplicity | Clear visual HUD displaying battery gauge, current mode, active nozzle status, and live console | User testing with non-technical operators |
| **Maintainability** | NFR-M1 | Code Modularization | Strict separation between motor control, vision processing, sprayer logic, and UI layer | Static code analysis & module independence |

---

## 5. UN Sustainable Development Goals (SDG) & ESG Alignment

### 5.1 SDG Alignment Summary
- **SDG 2: Zero Hunger (Target 2.4, Indicator 2.4.1):** Advances resilient and sustainable agricultural practices. Agri Rover optimizes crop health while preserving soil vitality through precision targeted chemical dispensing and real-time NPK monitoring.
- **SDG 12: Responsible Consumption and Production (Target 12.4):** Achieves environmentally sound management of agricultural chemicals, reducing chemical pesticide volume by up to **80%**, thereby preventing massive groundwater contamination.
- **SDG 15: Life on Land:** Halts soil degradation and protects beneficial soil microbial ecosystems by replacing broad-spectrum saturation with pinpoint micro-bursts and tracking soil pH/moisture.

### 5.2 ESG Impact Metrics
- **Environmental (E):** 80% reduction in chemical runoff; 100% electric zero-emission propulsion; prevention of soil salinization and acidification.
- **Social (S):** Eliminates toxic chemical inhalation and carcinogenic exposure for farm workers; democratizes agricultural robotics for small-to-medium scale farms.
- **Governance (G):** Open-source, transparent, reproducible Python/Three.js architecture; rigorous safety fail-safes (under-voltage cutoff $\le 12.0\text{V}$, inductive flyback isolation).

---

## 6. Success Metrics & Key Performance Indicators (KPIs)

| KPI | Baseline (Conventional Methods) | Agri Rover Phase 1 (Achieved) | Agri Rover Phase 2 (Target) |
| :--- | :---: | :---: | :---: |
| **Pesticide Consumption** | 100% (Uniform broadcast) | **20% (80% reduction via AI micro-bursts)** | **15% (85% reduction with YOLOv8)** |
| **Human Chemical Exposure** | High (Direct backpack/tractor exposure) | **Zero (Remote teleoperation)** | **Zero (Fully autonomous fleet)** |
| **Soil Sampling Turnaround** | 3–7 Days (Manual lab testing) | **$< 5\text{ seconds}$ (In-situ probe logging)** | **$< 3\text{ seconds}$ (Continuous autonomous logging)** |
| **Vision Inference Rate** | N/A (Manual human scouting) | **18–22 FPS (OpenCV HSV on Pi 4)** | **$\ge 30\text{ FPS}$ (YOLOv8 INT8 on NPU/Coral)** |
| **Testing Damage Risk** | High (Physical collision/damage in field) | **Zero (3D WebGL Digital Twin simulation)** | **Zero (Multi-rover swarm simulation)** |
| **Battery Brownout Rate** | Common in DIY robotics | **0% (Guaranteed by $\le 12.0\text{V}$ halt)** | **0% (Automated docking / recharge)** |

---

## 7. Assumptions, Dependencies & Constraints

### 7.1 Assumptions
1. Farmland crop rows are planted with relatively uniform inter-row spacing ($50\text{ to }70\text{ cm}$).
2. Ambient sunlight or rover-mounted LED auxiliary lighting provides sufficient illumination for color camera perception.
3. Operating terrain grade does not exceed 25 degrees of incline.

### 7.2 Dependencies
1. **Hardware Dependencies:** Raspberry Pi 4 Model B (4GB RAM), dual BTS7960 H-bridges, 12V 7Ah battery, 12V normally-closed solenoid valves, high-pressure 12V DC diaphragm pump, 100mm stepper linear actuator.
2. **Software Dependencies:** Python 3.10+, OpenCV 4.x, NumPy, RPi.GPIO, React 18+, Three.js v0.128.0.

### 7.3 Constraints
1. **Payload Capacity:** Total onboard payload (fluid tank, battery, chassis, actuators) must remain under $15\text{ kg}$ to prevent motor driver over-current.
2. **Onboard Compute:** Computer vision models must run within the 4-core Cortex-A72 thermal and memory envelope of the Raspberry Pi 4 without exceeding 70°C.
