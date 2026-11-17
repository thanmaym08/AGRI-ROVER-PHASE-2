# AGRI-ROVER-PHASE-2
## Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring

[![VTU Affiliation](https://img.shields.io/badge/Affiliation-VTU%20%2F%20BMSITM-green.svg)](https://bmsit.ac.in)
[![Project Phase](https://img.shields.io/badge/Phase-Phase%20II%20Active-blue.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-ESP32--CAM%20%7C%20L298N%20%7C%20MG996R-orange.svg)]()
[![Simulation](https://img.shields.io/badge/Digital%20Twin-Three.js%20WebGL-purple.svg)]()

Agri Rover is an intelligent, cyber-physical Unmanned Ground Vehicle (UGV) engineered specifically for row-crop precision agriculture. Developed as a Master of Computer Applications (MCA) Project Work (MMCA34) at **BMS Institute of Technology & Management (BMSITM), Bengaluru**, affiliated to **Visvesvaraya Technological University (VTU)**.

---

## 🌟 Key Capabilities & System Features

1. **Precision Micro-Burst Actuation (Option 2 Targeted AI Mode):**
   - Direct 12V high-pressure mini diaphragm pump switched via an optocoupled relay with reverse 1N4007 flyback protection.
   - Slashes chemical pesticide volume by **up to 80%** compared to traditional continuous blanket spraying.

2. **In-Situ Automated Soil Moisture Probing (FR-9):**
   - 1-DOF vertical deployment slide driven by an **MG996R metal-gear high-torque servo** ($15\text{ kg}\cdot\text{cm}$).
   - Lowers a corrosion-resistant **Capacitive Soil Moisture Sensor v1.2** 50mm into the subsoil on demand.
   - Retracts to a safe transport clearance ($10^\circ$) before any vehicle motion resumes.

3. **Closed-Loop Localized Sprinkling with Dynamic Web Cockpit Slider:**
   - Real-time moisture threshold slider ($10\%\sim 80\%$, default $35\%$) embedded directly in the mobile web cockpit.
   - If subsoil moisture is **below** the threshold, the rover fires a calibrated 2.5-second targeted water burst directly onto the dry root zone.
   - If moisture is sufficient, spraying is bypassed, saving water and preventing root rot.

4. **Drive Lockout Safety Interlock:**
   - Wheel drive motors are strictly locked at **0% PWM** whenever the probe is extended or localized watering is active, preventing probe snapping or mechanical derailment.

5. **Concurrent Dual-Port Video Streaming & Teleoperation:**
   - **Port 80 (`camera_httpd`):** Dedicated exclusively to low-latency teleoperation REST endpoints (`/drive`, `/spray`, `/probe`, `/probe_threshold`, `/flash`).
   - **Port 81 (`stream_httpd`):** Dedicated exclusively to high-throughput MJPEG video streaming at 22–25 FPS.
   - Complete thread isolation eliminates video lag and control starvation.

6. **3D WebGL Digital Twin Simulation:**
   - Browser-based Three.js digital twin simulator featuring Rocker-Bogie wheel kinematics, zero-radius point turns, realistic mist cone particle systems, and georeferenced soil fertility heatmap rings.

---

## 🛠️ Hardware Architecture & Sourcing (BOM)

| Component | Specification | Function / Role | Sourcing |
| :--- | :--- | :--- | :--- |
| **Microcontroller** | AI-Thinker ESP32-CAM (OV2640, 4MB PSRAM) | Wi-Fi SoftAP server, camera streaming, PWM motor control | Robu.in |
| **Motor Driver** | L298N Dual H-Bridge Driver | Drives 4x TT DC geared motors with 12V high-current bus | Robu.in |
| **Drive Motors** | 4x TT Geared DC Motors (Skid-steer 4WD) | Locomotion across row crops; zero-radius in-place turns | ElectronicsComp |
| **Buck Converter** | LM2596 DC-DC Step-Down Regulator | Steps 12.6V down to clean 5.05V logic rail for ESP32 and Servo | Robu.in |
| **Battery Bus** | 12V 3S Li-ion Battery Pack (3x 18650, 12.6V peak) | Master power bus (10A–20A BMS discharge capability) | Local / Robu |
| **Battery Charger** | Dedicated 12.6V 2A CC/CV Smart Charger | Balanced cell charging to 4.2V/cell; resets tripped BMS | Robu.in / Amazon |
| **Charging Port** | DC-022B 5.5×2.1mm Panel Mount Female Jack | External chassis charge port; charge with main switch OFF | ElectronicsComp |
| **Soil Probe Actuator**| MG996R Metal-Gear High-Torque Servo | 1-DOF vertical probe extension and retraction mechanism | Robu.in |
| **Moisture Sensor** | Capacitive Soil Moisture Sensor v1.2 | Solder-resist insulated corrosion-free subsoil moisture reading | ElectronicsComp |
| **Water Pump** | 12V Mini Diaphragm Pump (R385) | High-pressure localized fluid dispensing directly from 12V bus | Robu.in |
| **Relay Driver** | 1-Channel 5V Optocoupled Relay Module | Isolates ESP32 GPIO from high-current 12V pump motor inrush | ElectronicsComp |
| **Flyback Diode** | 1N4007 Rectifier Diode (1000V / 1A) | Suppresses 150V back-EMF inductive kickback across pump | Local electronics |

---

## ⚡ Master Pinout & Netlist

| Microcontroller Pin | Peripheral / Target Terminal | Signal / Level | Role / Protection Rule |
| :--- | :--- | :---: | :--- |
| **GPIO 14** | L298N `IN1` | 3.3V LEDC PWM | Left Motors Forward Speed |
| **GPIO 15** | L298N `IN2` | 3.3V LEDC PWM | Left Motors Reverse Speed |
| **GPIO 13** | L298N `IN3` | 3.3V LEDC PWM | Right Motors Forward Speed |
| **GPIO 12** | L298N `IN4` | 3.3V LEDC PWM | Right Motors Reverse Speed (Must be LOW at boot) |
| **GPIO 2** | 5V Relay `IN` | 3.3V Digital Pulse | Direct 12V Water Pump Trigger |
| **GPIO 4** | MG996R Servo Signal (Orange) | 3.3V 50Hz PWM | Vertical Probe Stroke ($10^\circ \to 160^\circ$) |
| **GPIO 3 (`U0RXD`)** | Capacitive Soil Sensor Signal | Digital / Analog | Moisture status input (HIGH = Dry soil) |
| **Relay `COM`** | Switched +12.6V Battery Rail | +12.6V Direct Bus | **DIRECT 12V PUMP POWER** (Raw un-stepped battery) |
| **Relay `NO`** | 12V Pump (+) Red Lead | +12.6V Switched | Delivers 12V power when relay energizes |
| **Across Pump (+)/(-)**| 1N4007 Diode (Reverse) | Snubber Clamp | **Cathode (silver band) to (+); Anode to (-)** |
| **Master Star Ground**| Common 0V Reference | 0V Ground | Battery (-), LM2596 (-), L298N GND, ESP32 GND, Pump (-) |

---

## 💻 Firmware & Quick Start

1. Open [`Prototype/firmware/AgriRover_ESP32CAM/AgriRover_ESP32CAM.ino`](Prototype/firmware/AgriRover_ESP32CAM/AgriRover_ESP32CAM.ino) in Arduino IDE.
2. Select Board: **AI Thinker ESP32-CAM** (or ESP32-S3 Cam).
3. Set Upload Speed: **`115200`** baud.
4. Flash the board.
5. Power on the rover, connect your phone/laptop to Wi-Fi SoftAP:
   - **SSID:** `AgriRover-CAM-AP`
   - **Password:** `agrirover123`
6. Open your browser and navigate to: **`http://192.168.4.1`**
7. Use the responsive mobile cockpit to drive, view live 22 FPS video, adjust the **`💧 DRY LIMIT`** slider, and tap **`[ 🌱 PROBE & WATER ]`**!

---

## 📁 Repository Directory Structure

```
agrirover-phase-2/
├── PRD.md                         # Product Requirements Document (FRs, NFRs, Personas, SDGs)
├── ARCHITECTURE.md                # Cyber-Physical Architecture, Pinouts, Schematics
├── RULES.md                       # Hardware Safety, Code Quality, Git Conventions
├── DESIGN.md                      # Kinematics, CV Pipeline, Spraying Design, FSM, UI/UX
├── TASKS.md                       # Task Roadmap, Verification Matrix & Phase 2 Epics
├── MEMORY.md                      # Persistent Context, ADRs (ADR-001 to ADR-012)
├── Prototype/
│   ├── firmware/AgriRover_ESP32CAM/
│   │   ├── AgriRover_ESP32CAM.ino # Master Production ESP32 Firmware
│   │   └── test_cockpit.html      # Standalone Interactive Mobile Web Cockpit
│   ├── Agri_Rover_Moisture_Sprinkler_BOM_and_Wiring_Guide.pdf # Engineering PDF Guide
│   ├── Agri_Rover_Prototype_Hardware_BOM.pdf
│   ├── 3d_digital_twin_app.html   # Browser-based 3D Digital Twin Simulator
│   ├── digital_twin/              # WebGL Three.js Simulation Assets
│   └── mobile_app/                # Progressive Web App (PWA) Assets
└── assets/                        # Diagrams, Cad mockups, Schematics
```

---

## 👥 Project Team & Academic Credentials

- **Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru
- **Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)
- **Course Code:** MMCA34 (Project Work - Phase I & Phase II, 2025–2027 Batch)
- **UN SDG Alignment:** SDG 2 (Zero Hunger - Target 2.4), SDG 12 (Target 12.4), SDG 15 (Target 15.3)
