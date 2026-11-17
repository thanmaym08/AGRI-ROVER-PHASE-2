# System Architecture Document (ARCHITECTURE.md)
## Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring

**Document Version:** 2.0.0  
**Project Code:** MMCA34 (Project Work - Phase I & Phase II, 2025–2027 Batch)  
**Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru  
**Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)  

---

## 1. High-Level Cyber-Physical System Architecture

Agri Rover is architected as an event-driven, multi-tiered **Cyber-Physical Robotic System (CPS)**. The system couples physical edge robotics with a real-time browser-based **3D WebGL Digital Twin**.

```
+---------------------------------------------------------------------------------------------------------+
|                                        OPERATOR PRESENTATION TIER                                       |
|                                                                                                         |
|   +-------------------------------------------------------------------------------------------------+   |
|   |                        React.js + Three.js 3D WebGL Digital Twin Simulator                      |   |
|   |  - 3D Field Environment & Crop Rows (Three.js v0.128.0)    - OrbitControls Interactive Camera   |   |
|   |  - Kinematic Rover 3D Mesh & Rocker-Bogie Suspension      - Real-Time Dual Particle Spray Mists|   |
|   |  - Georeferenced NPK/pH Ground Heatmap Rings              - Telemetry HUD & Battery Gauge       |   |
|   |  - WASD Teleoperation & Lane Lock Steering Controls        - LocalStorage Operational Logger    |   |
|   +-------------------------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------------------------+
                                                     ▲
                                                     │ Bi-Directional Telemetry & Teleoperation
                                                     │ (WebSockets / HTTP REST / JSON Bridge)
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                      EDGE COMPUTING & CONTROL TIER                                      |
|                                      (Raspberry Pi 4 Model B - 4GB)                                     |
|                                                                                                         |
|   +--------------------------+  +--------------------------+  +-------------------------------------+   |
|   |  Vision Pipeline Daemon  |  |  Motion Kinematics Node  |  |      Sprayer Actuator Daemon        |   |
|   |  (camera_stream.py)      |  |  (motor_control_pi.py)   |  |      (pesticide_sprayer.py)         |   |
|   |                          |  |                          |  |                                     |   |
|   | - 1080p Video Acquisition|  | - 4WD Skid-Steer Mixer   |  | - Directional Solenoid Logic        |   |
|   | - BGR -> HSV Color Space |  | - PWM Speed Modulation   |  | - Calibrated 200ms Micro-bursts     |   |
|   | - Pest / Weed Thresholds |  | - Proportional Steering  |  | - 100Hz Diaphragm Pump MOSFET PWM|   |
|   | - Spatial Offset Calc    |  | - Zero-Radius Turn Exec  |  | - Flow & Pressure Control Loop     |   |
|   +--------------------------+  +--------------------------+  +-------------------------------------+   |
|                 │                             ▲                                   ▲                     |
|                 └─────────────────────────────┼───────────────────────────────────┘                     |
|                                               │ Inter-Process Coordination & Safety Bus                 |
|   +-------------------------------------------┴-----------------------------------------------------+   |
|   |                            Supervisory & Hardware Abstraction Layer                             |   |
|   |  - Power Management & Battery Supervisor (ADC Voltage Divider, Emergency Halt <= 12.0V)          |   |
|   |  - Soil Probe Deployment Controller (Stepper Linear Actuator Sequencer & Interlock)             |   |
|   |  - Low-Level RPi.GPIO Pin Manager (Pin mappings, Cleanups, State Lockouts)                      |   |
|   +-------------------------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------------------------+
                                                     ▲
                                                     │ Direct GPIO Lines & PWM Channels
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
|                                      PHYSICAL HARDWARE & ACTUATOR TIER                                  |
|                                                                                                         |
|   +---------------------+   +---------------------+   +---------------------+   +-------------------+   |
|   |  Drive Subsystem    |   |  Sprayer Subsystem  |   |  Soil Probe Subsys  |   |   Power Subsys    |   |
|   |                     |   |                     |   |                     |   |                   |   |
|   | - Dual BTS7960      |   | - 12V Left Solenoid |   | - NEMA Stepper      |   | - 12V 7Ah SLA /   |   |
|   |   43A H-Bridges     |   | - 12V Right Solenoid|   |   Linear Actuator   |   |   LiFePO4 Battery |   |
|   | - 4x DC Geared      |   | - 12V Diaphragm     |   | - NPK Electrochemical|  | - LM2596 Buck     |   |
|   |   Motors (High-     |   |   Chemical Pump     |   |   Sensor Array      |   |   5V 3A Converter |   |
|   |   Torque 12V)       |   | - Dual Brass Mist   |   | - pH Electrode      |   | - Optocouplers &  |   |
|   | - Mud-Tread Wheels  |   |   Nozzles           |   | - Capacitive Moist. |   |   Flyback Diodes  |   |
|   +---------------------+   +---------------------+   +---------------------+   +-------------------+   |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Subsystem Decomposition & Architectural Specifications

### 2.1 Subsystem 1: Edge Computing & Supervisory Control
- **Core Processor:** Raspberry Pi 4 Model B (Quad-core Cortex-A72 @ 1.5GHz, 4GB LPDDR4).
- **Operating Environment:** 64-bit Raspberry Pi OS (Debian Bullseye/Bookworm), Python 3.10+ runtime.
- **Architectural Pattern:** Modular, asynchronous daemon processes communicating via in-memory queues and shared state dictionaries.
- **Responsibilities:**
  - Video capture and real-time computer vision inference.
  - Calculation of differential motor speeds and PWM generation.
  - Safe firing of solenoid spray valves and motor driver relays.
  - Periodic reading and validation of battery voltage.
  - Serializing and transmitting telemetry frames to the 3D Digital Twin.

### 2.2 Subsystem 2: Drive & Motion Kinematics Subsystem
- **Actuation Topology:** 4-wheel independent drive with skid-steer differential steering.
- **Motor Drivers:** Dual BTS7960 43A High-Current H-Bridge Motor Driver ICs.
  - Left Driver controls Front-Left and Rear-Left geared DC motors.
  - Right Driver controls Front-Right and Rear-Right geared DC motors.
- **Speed Modulation:** Hardware-timed Pulse Width Modulation (PWM) operating at $1\text{ kHz}$ carrier frequency with selectable speed regimes:
  - **Creep (30% PWM):** Precision alignment and active soil probing maneuver.
  - **Cruise (60% PWM):** Standard autonomous crop-row tracking and AI spraying.
  - **Sprint (100% PWM):** Rapid transit between field headlands.
- **Kinematic Constraints:**
  - Skid-steer differential drive requires counter-rotating left and right motor banks for in-place zero-radius point turns ($\omega = 2v / L$, turning radius $R = 0$).

### 2.3 Subsystem 3: Computer Vision & AI Threat Detection Pipeline
- **Optics:** 1080p wide-angle camera mounted on rover front center looking downward along the crop row.
- **Algorithm Flow:**
  1. Capture raw BGR frame ($640 \times 480$ resized for edge efficiency).
  2. Convert frame to HSV (Hue-Saturation-Value) color space to achieve invariance against changing daylight conditions.
  3. Apply dual color segmentation masks:
     - **Purple Mask (`[130, 50, 50]` to `[160, 255, 255]`):** Detects biological pests such as foliar caterpillars and larvae.
     - **Red Mask (`[0, 70, 50]` to `[10, 255, 255]` and `[170, 70, 50]` to `[180, 255, 255]`):** Detects broadleaf weeds, blight spots, and foreign foliage.
  4. Perform morphological opening (erosion followed by dilation with a $3 \times 3$ kernel) to eliminate noise artifacts.
  5. Find external contours (`cv2.findContours`); reject contours with area $< 150\text{ pixels}^2$.
  6. Calculate bounding box centroid $(c_x, c_y)$. If $c_x < \text{width}/2$, flag target on **LEFT**; otherwise flag on **RIGHT**.
  7. Compute row centerline deviation via Hough Line Transform for autonomous lane centering.

### 2.4 Subsystem 4: Precision Chemical Spraying Subsystem
- **Fluidic Components:**
  - 12V DC High-Pressure Diaphragm Pump ($4.0\text{ L/min}$, $100\text{ PSI}$ max shutoff).
  - 2x Normally-Closed 12V Solenoid Valves (Brass body, fast-acting $<50\text{ ms}$ response).
  - Dual brass fan-mist spray nozzles mounted symmetrically on the left and right chassis booms.
- **Control Modes:**
  - **Option 1 (Blanket Coverage):** Continuous pump operation with both solenoid valves held open; spray rate modulated via pump PWM.
  - **Option 2 (Targeted AI Spraying):** Pump runs on continuous low-pressure standby ($40\text{–}60\text{ kPa}$). Solenoid valves fire independent, calibrated **200ms micro-bursts** directed solely at the detected threat coordinate, cutting fluid consumption by up to 80%.

### 2.5 Subsystem 5: In-Situ Soil Health & Probing Subsystem
- **Mechanism:** NEMA 17 stepper motor coupled to a $100\text{ mm}$ lead-screw linear actuator arm.
- **Sensor Array:**
  - Electrochemical NPK sensor probe (Nitrogen, Phosphorus, Potassium concentration in mg/kg).
  - Glass-electrode pH sensor ($0.0\text{–}14.0\text{ pH}$ range).
  - Capacitive soil moisture sensor ($0\text{–}100\%$).
- **Interlock Sequence:**
  1. Trigger event asserted -> Motor PWM command clamped to 0% -> Verification of zero vehicle velocity.
  2. Stepper motor steps downward, inserting the probe 100mm into the sub-canopy soil.
  3. Wait 500ms for electrochemical stabilization -> Sample analog/digital sensor lines.
  4. Stepper motor reverses, retracting probe to travel lock position.
  5. Motor interlock released; georeferenced reading packaged into JSON telemetry.

### 2.6 Subsystem 6: Hardware Safety & Power Management Subsystem
- **Main Power Source:** 12V 7Ah sealed lead-acid (SLA) or 4S LiFePO4 battery pack.
- **Power Distribution:**
  - Unregulated 12V rail supplies BTS7960 motor drivers, solenoid valves, and diaphragm pump.
  - Step-down LM2596 buck converter provides a clean, regulated 5.1V 3.0A rail for the Raspberry Pi 4.
  - Flyback clamping diodes (1N4007 / 1N5819) installed across all solenoid and pump inductive coils.
  - Optocoupler isolation between Raspberry Pi GPIO pins and relay coils.
- **Battery Fail-Safe:** Real-time hardware voltage sensing. If $V_{batt} \le 12.0\text{V}$ ($\le 12\%$ capacity), an automatic **Emergency Halt** is executed, disabling all motor PWM signals and shutting all chemical valves to prevent brownouts.

### 2.7 Subsystem 7: 3D WebGL Digital Twin Presentation Layer
- **Framework:** React 18+ with Three.js (v0.128.0) and OrbitControls.
- **Rendering Engine:** WebGL canvas rendering at native 60 FPS.
- **Simulation Models:**
  - Procedural farmland terrain with textured crop rows and furrow depressions.
  - Full 3D rover mesh featuring Rocker-Bogie rocker arms, mud-tread wheels, chemical tank, and articulated probe arm.
  - Particle mist systems (instanced sprite particles with velocity vectors) simulating chemical fluid discharge.
  - Interactive ground decals representing georeferenced NPK/pH soil test results.
- **Telemetry Bridge:** Bidirectional WebSocket/REST endpoint streaming rover pose $(x, y, \theta)$, motor PWM, battery voltage, active spray mode, and sensor readings.

---

## 3. Hardware Pinout & Wiring Specification

All pin assignments adhere to standard **Broadcom (BCM) GPIO numbering** on the Raspberry Pi 4:

| Subsystem | Function / Signal Name | BCM GPIO | Physical Header Pin | Electrical Interface | Operational Logic / Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Left BTS7960** | Left Forward PWM (`RPWM`) | **GPIO 12** | Pin 32 | Hardware PWM0 | Forward speed duty cycle (0–100%) |
| **Left BTS7960** | Left Reverse PWM (`LPWM`) | **GPIO 13** | Pin 33 | Hardware PWM1 | Reverse speed duty cycle (0–100%) |
| **Left BTS7960** | Left Forward Enable (`R_EN`) | **GPIO 27** | Pin 13 | 3.3V Digital Output | HIGH enables forward drive |
| **Left BTS7960** | Left Reverse Enable (`L_EN`) | **GPIO 17** | Pin 11 | 3.3V Digital Output | HIGH enables reverse drive |
| **Right BTS7960** | Right Forward PWM (`RPWM`) | **GPIO 18** | Pin 12 | Hardware PWM0 | Forward speed duty cycle (0–100%) |
| **Right BTS7960** | Right Reverse PWM (`LPWM`) | **GPIO 19** | Pin 35 | Hardware PWM1 | Reverse speed duty cycle (0–100%) |
| **Right BTS7960** | Right Forward Enable (`R_EN`) | **GPIO 23** | Pin 16 | 3.3V Digital Output | HIGH enables forward drive |
| **Right BTS7960** | Right Reverse Enable (`L_EN`) | **GPIO 22** | Pin 15 | 3.3V Digital Output | HIGH enables reverse drive |
| **Sprayer** | Left Solenoid Valve Control | **GPIO 24** | Pin 18 | Optocoupler Relay Out | HIGH = Valve Open (200ms pulse) |
| **Sprayer** | Right Solenoid Valve Control | **GPIO 25** | Pin 22 | Optocoupler Relay Out | HIGH = Valve Open (200ms pulse) |
| **Sprayer** | Diaphragm Pump Speed | **GPIO 26** | Pin 37 | MOSFET Gate PWM | 100Hz PWM for fluid flow control |
| **Soil Probe** | Stepper Step Pulse (`STEP`) | **GPIO 05** | Pin 29 | Digital Pulse Output | Linear actuator downward/upward feed |
| **Soil Probe** | Stepper Direction (`DIR`) | **GPIO 06** | Pin 31 | Digital Level Output | HIGH = Down, LOW = Up |
| **Soil Probe** | Stepper Enable (`EN`) | **GPIO 16** | Pin 36 | Digital Level Output | LOW = Driver Enabled, HIGH = Sleep |
| **Safety / Pwr** | Battery Voltage Sensing | **A0 (ADC)** | I2C (GPIO 2/3) | ADS1115 via I2C | Voltage divider ($12\text{V} \rightarrow 3.0\text{V}$) |

---

## 4. Detailed Data Flow Architecture

### 4.1 Level-0 Context Diagram (DFD Level 0)

```
                       +-----------------------------+
                       |        Farm Operator        |
                       +-----------------------------+
                           │                     ▲
       Teleop Commands,    │                     │ Live Telemetry HUD,
       Speed Preset, Mode  │                     │ Battery Status,
                           ▼                     │ Video Stream
                    +------------------------------------+
                    |                                    |
                    |         AGRI ROVER SYSTEM          |
                    |       (Cyber-Physical UGV)         |
                    |                                    |
                    +------------------------------------+
                           │                     ▲
       Chemical Sprays,    │                     │ Ground Soil Nutrients,
       Tire Traction       │                     │ Crop Row Video Frames,
                           ▼                     │ Ambient Light
                       +-----------------------------+
                       |    Crop Field Environment   |
                       +-----------------------------+
```

### 4.2 Level-1 Data Flow Diagram (DFD Level 1)

```
 +------------------+     [W,A,S,D, Keys]
 |  Farm Operator   | ─────────────────────┐
 +------------------+                      │
                                           ▼
                                 +────────────────----+
                                 | 1.0 Teleoperation  | ──── [Left/Right Motor Speeds] ───┐
                                 | & Mode Management  |                                   │
                                 +────────────────----+                                   │
                                           │                                              ▼
                                           │ Mode State                         +───────────────────+
                                           ▼                                    | 4.0 Steering      |
 +------------------+            +────────────────----+                         | Kinematics & PWM  |
 |  Camera Sensor   | ─────────> | 2.0 OpenCV Vision  |                         +───────────────────+
 +------------------+ [Raw BGR]  | & Threat Detection |                                   │
                                 +────────────────----+                                   │ [PWM Pulses]
                                           │                                              ▼
                                           │ [Target Side: Left/Right]          +-------------------+
                                           ▼                                    | BTS7960 Drivers   |
                                 +────────────────----+                         +-------------------+
                                 | 3.0 Solenoid &     | ── [Relay Trigger] ───> +-------------------+
                                 | Spray Control Node |                         | Solenoid Valves   |
                                 +────────────────----+                         +-------------------+
                                           ▲
                                           │ [Probe Trigger]
                                           ▼
                                 +────────────────----+                         +-------------------+
                                 | 5.0 Soil NPK Data  | ── [Analog / Modbus] ─> | Soil Probe Sensor |
                                 | Acquisition Node   | <── [NPK/pH Values] ─── +-------------------+
                                 +────────────────----+
                                           │
                                           ▼ [Structured Telemetry JSON]
                                 +────────────────----+
                                 | 6.0 3D Digital     | ──> [Visual Heatmap & HUD]
                                 | Twin Simulator     |
                                 +────────────────----+
```

---

## 5. Telemetry Frame Specification (JSON Schema)

Every telemetry packet emitted by the edge daemon or simulated by the digital twin complies with the following structured schema:

```json
{
  "timestamp": 1774281600000,
  "rover_id": "AGRI-ROVER-01",
  "system_state": "AUTONOMOUS_PATROL",
  "power": {
    "battery_voltage": 12.4,
    "battery_percentage": 78,
    "current_draw_amps": 3.2,
    "emergency_halt": false
  },
  "motion": {
    "left_speed_pwm": 60,
    "right_speed_pwm": 60,
    "steer_angle_rad": 0.05,
    "lane_lock_active": true,
    "point_turn_active": false,
    "pose": {
      "x": 12.45,
      "y": 0.0,
      "z": 45.20,
      "heading_deg": 180.2
    }
  },
  "threat_detection": {
    "active_mode": "OPTION_2_TARGETED_AI",
    "threats_detected": 1,
    "targets": [
      {
        "id": "T-102",
        "type": "CATERPILLAR",
        "side": "left",
        "confidence": 0.92,
        "bounding_box": [120, 180, 45, 60]
      }
    ]
  },
  "actuation": {
    "left_solenoid_open": true,
    "right_solenoid_open": false,
    "pump_duty_cycle_pct": 75,
    "spray_pulse_duration_ms": 200,
    "accumulated_chemical_saved_pct": 78.4
  },
  "soil_probe": {
    "probe_extended": false,
    "nitrogen_mg_kg": 42.1,
    "phosphorus_mg_kg": 18.5,
    "potassium_mg_kg": 165.2,
    "ph_level": 6.8,
    "moisture_pct": 34.2,
    "last_sampled_pose": { "x": 10.0, "z": 40.0 }
  }
}
```

---

## 6. Fault Tolerance & Reliability Architecture

| Potential Failure Mode | Detection Mechanism | Mitigation Strategy / Autonomous Recovery |
| :--- | :--- | :--- |
| **Battery Brownout ($V_{batt} \le 12.0\text{V}$)** | Dedicated ADC voltage polling loop every 50ms. | Instantaneous Emergency Halt: set motor PWM = 0%, disable `L_EN`/`R_EN`, close all solenoids, turn off pump. |
| **Camera Stream Dropout** | OpenCV `cap.read()` returns `False` or throws timeout. | Safe Stop: Halt forward motion, enter `STATIONARY_MANUAL` mode, display video loss warning on Dashboard. |
| **Inductive Spike / Voltage Kick** | High back-EMF from solenoid valve deactivation. | Hardware 1N4007 flyback diodes across coils + optocoupled relay inputs isolate Raspberry Pi 3.3V logic. |
| **Crop Row Boundary Loss** | Hough line transform fails to detect lines for $> 5$ frames. | Rover halts autonomous forward advance and requests manual operator intervention. |
| **Soil Probe Obstacle / Jam** | Stepper over-current or timeout on linear stroke. | Actuator auto-reverses to home position; logs mechanical alert and resumes travel mode without crashing probe. |
