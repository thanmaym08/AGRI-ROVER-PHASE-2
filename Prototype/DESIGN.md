# Detailed System Design Document (DESIGN.md) — Prototype
## Agri Rover: ESP32-CAM Edge IoT Teleoperated & Autonomous Vision Testbed

**Document Version:** 1.0.0  
**Project Code:** MMCA34 — Agri Rover Phase II Prototype Work  
**Target Hardware:** AI-Thinker ESP32-CAM Module  
**Status:** Approved Detailed Design Specification  

---

## 1. Hardware Architecture & Component Specification

The Agri Rover ESP32-CAM prototype is engineered as a self-contained, high-performance edge IoT robotics platform.

### 1.1 Bill of Materials (BOM) & Electrical Ratings

| Component | Part / Model | Role in Prototype | Voltage / Rating | Key Specifications |
| :--- | :--- | :--- | :--- | :--- |
| **Microcontroller + Vision** | AI-Thinker ESP32-CAM | Core compute, camera sensor, Wi-Fi web server, motor/relay controller. | $5.0\text{V} \pm 0.1\text{V}$ input; $3.3\text{V}$ logic | Dual-core 240MHz Xtensa LX6, 520KB SRAM, 4MB PSRAM, OV2640 2MP DVP sensor. |
| **Step-Down Buck Converter** | LM2596 (or MP1584) | Regulates raw battery voltage down to clean logic power. | In: $7\text{–}35\text{V}$, Out: $5.10\text{V}$ DC | Max $3.0\text{A}$ output current, $>90\%$ efficiency, low ripple. |
| **Motor Driver** | L298N Dual H-Bridge (or DRV8833) | 4-channel DC motor power amplification and direction control. | Logic: $5\text{V}$, Motor: $12\text{V}$ | Dual H-bridge, max $2.0\text{A}$ continuous per channel, optical isolation. |
| **Drive Motors** | 4x TT Geared DC Motors (or 12V 100RPM Geared) | Skid-steer differential propulsion (2WD or 4WD). | $6\text{–}12\text{V}$ DC | Stall torque $\approx 1.5\text{–}3.0\text{ kg}\cdot\text{cm}$, rubber mud-tread wheels. |
| **Sprayer Actuator Relay** | 1-Channel 5V Optocoupled Relay Module | Switches high-current 12V power to chemical spray pump. | Coil: $5\text{V}$ DC, Contacts: $10\text{A} / 250\text{VAC}$ | Optoisolated input, active-HIGH or active-LOW jumper selectable. |
| **Chemical Spray Pump** | 12V Mini Diaphragm Pump (or 12V Solenoid Valve) | Delivers pressurized liquid chemical micro-bursts to spray nozzle. | $12\text{V}$ DC, $\approx 1.2\text{A}$ load | Flow rate $1.0\text{–}2.0\text{ L/min}$, operating pressure $\approx 0.2\text{–}0.4\text{ MPa}$. |
| **Power Source** | 3S Li-ion Battery (11.1V–12.6V) or 12V 7Ah SLA | Main mobile electrical reservoir. | Nominal $11.1\text{–}12.0\text{V}$, $>5\text{C}$ burst | Low internal resistance, powers motors, pump, and buck converter. |
| **Protection Components** | 1x $1000\mu\text{F} / 16\text{V}$ Cap, 1x 1N4007 Diode | Decoupling logic rail & flyback clamping across pump coil. | $16\text{V}$ cap, $1000\text{V} / 1\text{A}$ diode | Prevents brownouts and inductive voltage spikes. |
| **Flashing Programmer** | FT232RL or CP2102 USB-to-UART Adapter | Firmware flashing and serial console debugging. | USB $5\text{V}$ bus, $3.3\text{V}$ UART signals | Baud rates up to $921600\text{ bps}$. |

---

## 2. Complete Pin Mapping & Hardware Interfacing

### 2.1 AI-Thinker ESP32-CAM Physical Pin Allocation

The AI-Thinker module layout consists of two 8-pin dual-inline headers ($2.54\text{ mm}$ pitch).

```
                      AI-THINKER ESP32-CAM
                         ┌────────────┐
                         │   OV2640   │
                         │   CAMERA   │
                         │   LENS     │
                         └────────────┘
               [Flash LED]            [Reset Button]
               
     (Left Header)                     (Right Header)
  5V     [ 1]  ●                    ●  [16]   3V3
  GND    [ 2]  ●                    ●  [15]   GND
  IO12   [ 3]  ●  (Motor Left A)    ●  [14]   IO0   (Flash Jumper -> GND)
  IO13   [ 4]  ●  (Motor Left B)    ●  [13]   IO16  (PSRAM Internal CS)
  IO15   [ 5]  ●  (Motor Right B)   ●  [12]   IO1   (U0TXD - Serial Debug)
  IO14   [ 6]  ●  (Motor Right A)   ●  [11]   IO3   (U0RXD - Serial In)
  IO2    [ 7]  ●  (Spray Relay)     ●  [10]   VCC   (Unused / 3.3V)
  IO4    [ 8]  ●  (Flash LED PWM)   ●  [ 9]   GND
```

### 2.2 Functional Pinout Matrix

| Pin Label | Physical Header | Internal Wiring | Prototype Function | Electrical Description | Safety & Strapping Notes |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **5V** | Left Pin 1 | AMS1117-3.3 In | System 5V Power Input | Connect to LM2596 Output ($+5.10\text{V}$) | Add $1000\mu\text{F}$ cap directly to GND. |
| **GND** | Left Pin 2 | Ground Plane | System Star Ground | Common Star GND connection | Shared with battery, driver, and relay. |
| **GPIO 12** | Left Pin 3 | MTDI Strapping | **Motor Left A (`IN1`)** | Digital Output / LEDC PWM Channel 0 | **MUST BE LOW AT BOOT**. Avoid 1.8V flash bug. |
| **GPIO 13** | Left Pin 4 | HS2_DATA3 | **Motor Left B (`IN2`)** | Digital Output / LEDC PWM Channel 1 | High-speed digital output. |
| **GPIO 15** | Left Pin 5 | MTDO Strapping | **Motor Right B (`IN4`)** | Digital Output / LEDC PWM Channel 3 | Outputs PWM pulses during bootloader startup. |
| **GPIO 14** | Left Pin 6 | HS2_CLK / D5 | **Motor Right A (`IN3`)** | Digital Output / LEDC PWM Channel 2 | Shared with MicroSD CLK; MicroSD must be unused. |
| **GPIO 2** | Left Pin 7 | Blue Status LED | **Spray Pump Relay** | Digital Output ($200\text{ ms}$ pulse) | Must be LOW at bootloader download entry. |
| **GPIO 4** | Left Pin 8 | Onboard Flash LED | **Floodlight PWM** | LEDC PWM Channel 4 | Drives onboard SMD transistor for flash LED. |
| **GPIO 0** | Right Pin 14| Boot Strapping | **Flashing Mode Jumper** | Jumper to GND during flashing; open for run | Floating/HIGH in run mode; grounded to program. |
| **GPIO 16**| Right Pin 13| PSRAM Chip Select | **DO NOT CONNECT** | Hardwired to internal 4MB PSRAM IC | Connecting external circuits crashes camera. |
| **GPIO 1** | Right Pin 12| UART0 TXD | **Serial Debug / Telemetry** | 115200 baud UART TX output | Disconnected or routed to companion telemetry. |
| **GPIO 3** | Right Pin 11| UART0 RXD | **Serial Programming RX** | 115200 baud UART RX input | Connected to FTDI TX during flashing. |

---

## 3. Electrical Schematics & Circuit Wiring

### 3.1 Flashing Rig Wiring (USB-to-UART FTDI Programmer)

To flash firmware onto the ESP32-CAM, connect an FTDI adapter (CP2102 / FT232RL) configured for **5V VCC** and **3.3V Logic**:

```
 ┌──────────────────────┐                     ┌──────────────────────┐
 │     FTDI / CP2102    │                     │      ESP32-CAM       │
 │   USB-TO-SERIAL      │                     │                      │
 │                      │                     │                      │
 │  VCC (5V)       [5V] ├─────────────────────┤ [5V]   (Left Pin 1)  │
 │  GND           [GND] ├──────────┬──────────┤ [GND]  (Left Pin 2)  │
 │  TXD            [TX] ├──────────┼──────────┤ [IO3]  (U0RXD)       │
 │  RXD            [RX] ├──────────┼──────────┤ [IO1]  (U0TXD)       │
 └──────────────────────┘          │          │                      │
                                   │          │ [IO0]  (Boot Pin)    │
                                   │          │   │                  │
                                   └──────────┴───┴─ Jumper (GND)    │
                                                     [CLOSED = FLASH]
                                                     [OPEN   = RUN  ]
```

> **Flashing Sequence:**
> 1. Bridge `GPIO 0` to `GND`.
> 2. Plug FTDI into computer USB port.
> 3. Press the onboard **RST** button once on the ESP32-CAM to place it into download mode.
> 4. Click **Upload** in Arduino IDE / PlatformIO.
> 5. When upload completes (`Leaving... Hard resetting via RTS pin...`), disconnect the `GPIO 0` to `GND` jumper.
> 6. Press the **RST** button again to boot into the Agri Rover firmware!

---

### 3.2 Complete Prototype Electrical Schematic (Chassis & Actuators)

```
                       +12V HIGH-CURRENT BUS
 ┌────────────────────────────────────────────────────────────────────────┐
 │                                                                        │
 │   ┌──────────────┐     SPST Switch       ┌────────────────────────┐    │
 ├───┤ 12V Battery  ├─────────[ / ]─────────┤ +12V L298N VCC Power   │    │
 │   │ (Li-ion/SLA) │                       │                        │    │
 │   └──────┬───────┘                       │ Motor Driver Board     │    │
 │          │                               └───────────┬────────────┘    │
 │          │                                           │                 │
 │          │                               ┌───────────┴────────────┐    │
 │          │                               │ Relay COM Terminal     │    │
 │          │                               │ (5V Optocoupled Relay) │    │
 │          │                               └───────────┬────────────┘    │
 │          │                                           │ (NO Contact)    │
 │          │                                           ▼                 │
 │          │                               ┌────────────────────────┐    │
 │          │                               │ +12V Spray Pump (+)    │    │
 │          │                               │ [1N4007 Diode Across]  │    │
 │          │                               └───────────┬────────────┘    │
 │          │                                           │                 │
 │   ┌──────┴────────────────────────┐                  │                 │
 │   │ LM2596 Step-Down Buck Reg     │                  │                 │
 │   │ In: +12V  ──► Out: +5.10V DC  │                  │                 │
 │   └───┬──────────────────────┬────┘                  │                 │
 │       │ +5.1V Logic Rail     │ GND                   │                 │
 │       ▼                      │                       │                 │
 │   ┌──────────────────────┐   │                       │                 │
 │   │ ESP32-CAM Board      │   │                       │                 │
 │   │ [5V Pin]  ───┐       │   │                       │                 │
 │   │              ├───────┼───┼───────────────────────┼─────────────────┤
 │   │ [GND Pin] ───┘  │    │   │                       │                 │
 │   │ (1000uF Cap Across)  │   │                       │                 │
 │   │                      │   │                       │                 │
 │   │ GPIO 12 ─────────────┼───┼──────► L298N IN1      │                 │
 │   │ GPIO 13 ─────────────┼───┼──────► L298N IN2      │                 │
 │   │ GPIO 14 ─────────────┼───┼──────► L298N IN3      │                 │
 │   │ GPIO 15 ─────────────┼───┼──────► L298N IN4      │                 │
 │   │ GPIO 2  ─────────────┼───┼──────► Relay Signal IN│                 │
 │   │ 5V Out  ─────────────┼───┼──────► Relay VCC      │                 │
 │   └──────────────────────┘   │                       │                 │
 │                              │                       │                 │
 └──────────────────────────────┴───────────────────────┴─────────────────┘
                     COMMON STAR GROUND RETURN RAIL (0V)
```

---

### 3.3 4WD Motor Parallel Connection Topology (L298N Dual H-Bridge)

To drive a 4-wheel skid-steer chassis with a dual-channel L298N driver, the two left motors are wired in parallel to Channel A (`OUT1` / `OUT2`), and the two right motors are wired in parallel to Channel B (`OUT3` / `OUT4`):

```
       FRONT-LEFT MOTOR                             FRONT-RIGHT MOTOR
     ┌──────────────────┐                         ┌──────────────────┐
     │ (+) Red Wire     │────┐               ┌────│ (+) Red Wire     │
     │ (-) Black Wire   │──┐ │               │ ┌──│ (-) Black Wire   │
     └──────────────────┘  │ │               │ │  └──────────────────┘
                           │ │   L298N BOARD │ │
                           │ │  ┌─────────┐  │ │
                           │ └─►│ OUT1    │  │ │
                           └───►│ OUT2    │  │ │
                                │         │  │ │
                                │    OUT3 │◄─┘ │
                                │    OUT4 │◄───┘
                           ┌───►│         │
                           │ ┌─►│ 12V GND 5V│
                           │ │  └─────────┘
                           │ │    ▲   ▲   ▲ (POWER INPUT ONLY — NO MOTORS!)
     ┌──────────────────┐  │ │    │   │   │
     │ (-) Black Wire   │──┘ │    └───┼───┴─ From 12V Battery & Buck GND
     │ (+) Red Wire     │────┘        │
     └──────────────────┘             │
       REAR-LEFT MOTOR                │
     ┌──────────────────┐             │
     │ (-) Black Wire   │─────────────┘ (Twisted into OUT4)
     │ (+) Red Wire     │─────────────── (Twisted into OUT3)
     └──────────────────┘
       REAR-RIGHT MOTOR
```

| Terminal Block | Screw Position | Connected Wires | Function |
| :--- | :---: | :--- | :--- |
| **Left Blue Block (2 Screws)** | `OUT1` | **FL Red wire + RL Red wire** (twisted together) | Left Wheels Motor Forward (+) |
| **Left Blue Block (2 Screws)** | `OUT2` | **FL Black wire + RL Black wire** (twisted together) | Left Wheels Motor Reverse (-) |
| **Right Blue Block (2 Screws)**| `OUT3` | **FR Red wire + RR Red wire** (twisted together) | Right Wheels Motor Forward (+) |
| **Right Blue Block (2 Screws)**| `OUT4` | **FR Black wire + RR Black wire** (twisted together) | Right Wheels Motor Reverse (-) |
| **Bottom Block (3 Screws)**   | `12V`  | Battery Positive (+12V) through switch | Driver High-Current Motor Rail |
| **Bottom Block (3 Screws)**   | `GND`  | Common Star Ground (Battery -, Buck GND, ESP32 GND) | System Reference (0V) |
| **Bottom Block (3 Screws)**   | `5V`   | Logic 5V (keep 5V-EN jumper cap installed) | Internal Logic Supply |

---

### 3.4 Common Ground (Star Ground) Implementation Strategies & Topologies

Every component in the cyber-physical system must share a **Common Ground (0V)** so that digital logic signals from the ESP32 (3.3V/5V) have a closed return circuit to the L298N driver and relay. To prevent messy wiring or ground loops, operators can select one of four physical implementation methods:

```
                          COMMON STAR GROUND PHYSICAL OPTIONS
  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
  │  Option 1: WAGO Lever   │  │  Option 2: 2-Zone Buck  │  │  Option 3: L298N Hub    │
  ├─────────────────────────┤  ├─────────────────────────┤  ├─────────────────────────┤
  │ 5-port lever connector  │  │ LM2596 PCB naturally    │  │ L298N center screw      │
  │ clicks all black wires  │  │ joins high-power IN- to │  │ terminal receives       │
  │ with zero soldering.    │  │ clean logic OUT-.       │  │ main ground returns.    │
  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
```

#### Option 1: 5-Port WAGO 221 Lever Block (Cleanest & Easiest)
- Insert each ground wire into its own lever slot on a single WAGO 221-415 block:
  1. Slot 1: Battery (-) Negative
  2. Slot 2: LM2596 Buck `IN-`
  3. Slot 3: LM2596 Buck `OUT-`
  4. Slot 4: L298N Motor Driver `GND`
  5. Slot 5: 12V Diaphragm Pump (-) Black Wire
- From LM2596 `OUT-` / ESP32 header, jumper wires carry clean 0V to ESP32 `GND` and Relay `GND`.

#### Option 2: Two-Zone Natural Ground Hub via LM2596 PCB (Zero Extra Parts)
- The LM2596 non-isolated buck converter features a continuous internal ground copper plane connecting `IN-` and `OUT-` ($0\,\Omega$).
- **High-Current Power Zone (at `IN-`):** Battery (-) and L298N `GND` connect to LM2596 `IN-`.
- **Clean Logic Zone (at `OUT-`):** ESP32-CAM `GND` and Relay `GND` connect to LM2596 `OUT-`.
- High inductive motor noise is kept on the battery side, isolating sensitive Wi-Fi and camera circuitry.

---

## 4. Firmware Architecture & Software Design

### 4.1 Embedded Module Organization

```
Prototype/firmware/
├── AgriRover_ESP32CAM.ino     # Main entrypoint, setup(), loop(), task handles
├── camera_pins.h              # AI-Thinker OV2640 pin definitions
├── camera_server.h            # HTTP server, MJPEG streaming & REST handlers
├── motor_controller.h         # LEDC PWM hardware timers, skid-steer kinematics
├── spray_actuator.h           # Non-blocking relay pulse manager & flash LED
├── wifi_manager.h             # Dual SoftAP + Station network switcher
└── web_assets.h               # Embedded HTML5/CSS3/JS mobile phone interface
```

### 4.2 Skid-Steer Differential Kinematics & LEDC PWM Configuration

The firmware utilizes the ESP32's **LEDC hardware PWM peripheral** across 4 independent channels:

- **Timer Frequency:** $5000\text{ Hz}$ ($5\text{ kHz}$ eliminates audible motor coil whine).
- **Resolution:** 8-bit ($0\text{ to }255$).

| Function | ESP32 GPIO | LEDC Channel | Frequency | Resolution |
| :--- | :---: | :---: | :---: | :---: |
| Left Motor Forward (`IN1`) | GPIO 12 | Channel 0 | $5000\text{ Hz}$ | 8-bit ($0\text{–}255$) |
| Left Motor Reverse (`IN2`) | GPIO 13 | Channel 1 | $5000\text{ Hz}$ | 8-bit ($0\text{–}255$) |
| Right Motor Forward (`IN3`)| GPIO 14 | Channel 2 | $5000\text{ Hz}$ | 8-bit ($0\text{–}255$) |
| Right Motor Reverse (`IN4`)| GPIO 15 | Channel 3 | $5000\text{ Hz}$ | 8-bit ($0\text{–}255$) |
| Flash LED Dimming (`LED`)  | GPIO 4  | Channel 4 | $1000\text{ Hz}$ | 8-bit ($0\text{–}255$) |

#### Motion Kinematic Mapping Logic
```cpp
void set_motors(int left_speed, int right_speed) {
    // left_speed and right_speed range: -255 (full reverse) to +255 (full forward)
    left_speed = constrain(left_speed, -255, 255);
    right_speed = constrain(right_speed, -255, 255);

    // Left Motor Control
    if (left_speed > 0) {
        ledcWrite(0, left_speed); // IN1 PWM
        ledcWrite(1, 0);          // IN2 0
    } else if (left_speed < 0) {
        ledcWrite(0, 0);          // IN1 0
        ledcWrite(1, -left_speed);// IN2 PWM
    } else {
        ledcWrite(0, 0);
        ledcWrite(1, 0);
    }

    // Right Motor Control
    if (right_speed > 0) {
        ledcWrite(2, right_speed); // IN3 PWM
        ledcWrite(3, 0);           // IN4 0
    } else if (right_speed < 0) {
        ledcWrite(2, 0);           // IN3 0
        ledcWrite(3, -right_speed);// IN4 PWM
    } else {
        ledcWrite(2, 0);
        ledcWrite(3, 0);
    }
}
```

### 4.3 Chemical Spray Non-Blocking Timer Logic
```cpp
#define RELAY_PIN 2
unsigned long spray_start_time = 0;
bool spray_active = false;
unsigned long spray_duration_ms = 200; // Calibrated micro-burst

void trigger_spray(unsigned long duration_ms) {
    digitalWrite(RELAY_PIN, HIGH); // Energize relay
    spray_start_time = millis();
    spray_duration_ms = duration_ms;
    spray_active = true;
}

void process_spray_watchdog() {
    if (spray_active && (millis() - spray_start_time >= spray_duration_ms)) {
        digitalWrite(RELAY_PIN, LOW); // De-energize relay
        spray_active = false;
    }
}
```

---

## 5. Mobile Phone Web Application (In-App Video & Controls)

### 5.1 Architecture & UI Layout
The phone application is served directly from the ESP32-CAM when the user navigates to `http://192.168.4.1` (or local IP) on iOS Safari or Android Chrome.

```
┌─────────────────────────────────────────────────────────────┐
│ 🌿 AGRI ROVER | CAM       BAT: 12.4V   PING: 22ms   [ONLINE] ⚙️│ ◄── Floating HUD
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                LIVE VIDEO STREAM VIEWPORT                   │
│             <img src="/stream" id="video-feed">             │
│                                                             │
│       [ RETICLE: CENTERED FOR AI MICRO-BURST SPRAY ]        │
│                                                             │ ◄── 60% VIEWPORT
│                                                             │     (Video Stream & HUD)
│ [ ▲ FORWARD 65% ]  [ L: 165 | R: 165 ]                      │ ◄── Live Motion HUD
├──────────────────────────────┬──────────────────────────────┤
│      VIRTUAL JOYSTICK        │       TACTICAL CONTROLS      │
│                              │                              │
│             ▲                │   SPEED REGIME: [65% (MED)]  │
│             │                │   [ SLOW ]  [ MED ]  [ FAST ]│
│        ◄─── ┼ ───►           │   🐢 ───────●─────── 🐇      │ ◄── 40% CONTROLS
│             │                │   ┌──────────────────────┐   │     (Drive + Cockpit)
│             ▼                │   │ 💦 SPRAY BURST (200ms)│   │
│   (Multi-Touch Canvas Zone)  │   └──────────────────────┘   │
│                              │   [ 💡 FLASH ] [ 📐 CALIB ]  │
│   [ DRIVE & STEER ]          │   [ 🛑 EMERGENCY STOP ]      │
└──────────────────────────────┴──────────────────────────────┘
```

#### Skid-Steer Differential Kinematics with Turn Sensitivity & Drift Trim:

$$\text{throttle} = \frac{-dy}{R_{\max}} \in [-1.0, +1.0], \quad \text{steer} = \frac{dx}{R_{\max}} \in [-1.0, +1.0]$$

$$\text{left}_{\text{raw}} = \text{throttle} + (\text{steer} \cdot K_{\text{steer}})$$

$$\text{right}_{\text{raw}} = \text{throttle} - (\text{steer} \cdot K_{\text{steer}})$$

$$\text{if } (\text{Trim} > 0): \quad \text{right} = \text{right}_{\text{raw}} \cdot (1 - \text{Trim}), \quad \text{else}: \quad \text{left} = \text{left}_{\text{raw}} \cdot (1 + \text{Trim})$$

$$\text{left}_{\text{PWM}} = \text{clamp}\left(\text{left} \cdot V_{\max}, -255, 255\right), \quad \text{right}_{\text{PWM}} = \text{clamp}\left(\text{right} \cdot V_{\max}, -255, 255\right)$$


### 5.2 Embedded HTML/JS Mobile Application Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Agri Rover Controller</title>
<style>
  * { box-sizing: border-box; touch-action: none; user-select: none; margin: 0; padding: 0; }
  body { background: #121820; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
  header { background: #1a222d; padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2ecc71; }
  .badge { background: #27ae60; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
  #stream-box { position: relative; width: 100%; height: 48vh; background: #000; display: flex; justify-content: center; align-items: center; }
  #stream { max-width: 100%; max-height: 100%; object-fit: contain; }
  .reticle { position: absolute; border: 2px dashed rgba(46, 204, 113, 0.6); width: 140px; height: 140px; border-radius: 8px; pointer-events: none; }
  #controls { flex: 1; display: flex; padding: 12px; gap: 12px; }
  #joystick-zone { flex: 1; background: #1a222d; border-radius: 12px; position: relative; display: flex; justify-content: center; align-items: center; border: 1px solid #2c3e50; }
  #stick { width: 70px; height: 70px; background: radial-gradient(circle, #2ecc71, #27ae60); border-radius: 50%; position: absolute; transform: translate(0, 0); box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
  #action-panel { width: 160px; display: flex; flex-direction: column; gap: 8px; }
  .btn { background: #2c3e50; color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; text-align: center; }
  .btn:active { opacity: 0.7; }
  .btn-spray { background: linear-gradient(135deg, #2980b9, #3498db); color: #fff; font-size: 16px; padding: 16px; }
  .btn-stop { background: #e74c3c; }
  .speed-bar { display: flex; gap: 4px; }
  .btn-speed { flex: 1; padding: 8px 0; font-size: 11px; }
  .active-speed { background: #2ecc71; color: #121820; }
</style>
</head>
<body>

<header>
  <div><strong>🌿 AGRI ROVER</strong> | CAM</div>
  <div class="badge" id="status-badge">CONNECTED</div>
</header>

<div id="stream-box">
  <img id="stream" src="/stream" alt="Live Camera Stream">
  <div class="reticle"></div>
</div>

<div id="controls">
  <div id="joystick-zone">
    <div id="stick"></div>
  </div>

  <div id="action-panel">
    <div class="speed-bar">
      <button class="btn btn-speed" onclick="setSpeed(100)">30%</button>
      <button class="btn btn-speed active-speed" onclick="setSpeed(180)">60%</button>
      <button class="btn btn-speed" onclick="setSpeed(255)">100%</button>
    </div>
    <button class="btn btn-spray" onclick="triggerSpray()">💦 SPRAY (200ms)</button>
    <button class="btn" onclick="toggleFlash()">💡 FLASH LED</button>
    <button class="btn btn-stop" onclick="emergencyStop()">🛑 STOP</button>
  </div>
</div>

<script>
  let maxSpeed = 180;
  let flashState = 0;
  let stick = document.getElementById('stick');
  let zone = document.getElementById('joystick-zone');
  let activeTouch = null;
  let center = { x: 0, y: 0 };
  let maxRadius = 60;
  let lastSend = 0;

  function setSpeed(val) {
    maxSpeed = val;
    document.querySelectorAll('.btn-speed').forEach(b => b.classList.remove('active-speed'));
    event.target.classList.add('active-speed');
  }

  function triggerSpray() {
    fetch('/spray?ms=200').catch(err => console.error(err));
  }

  function toggleFlash() {
    flashState = flashState === 0 ? 200 : 0;
    fetch('/flash?val=' + flashState).catch(err => console.error(err));
  }

  function emergencyStop() {
    fetch('/drive?left=0&right=0').catch(err => console.error(err));
  }

  zone.addEventListener('touchstart', e => {
    let rect = zone.getBoundingClientRect();
    center = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    handleMove(e.touches[0]);
  });

  zone.addEventListener('touchmove', e => {
    e.preventDefault();
    handleMove(e.touches[0]);
  });

  zone.addEventListener('touchend', e => {
    stick.style.transform = `translate(0px, 0px)`;
    emergencyStop();
  });

  function handleMove(touch) {
    let dx = touch.clientX - center.x;
    let dy = touch.clientY - center.y;
    let dist = Math.hypot(dx, dy);
    if (dist > maxRadius) {
      dx = (dx / dist) * maxRadius;
      dy = (dy / dist) * maxRadius;
    }
    stick.style.transform = `translate(${dx}px, ${dy}px)`;

    // Convert dx, dy to differential skid-steer left & right motor speeds
    let throttle = (-dy / maxRadius); // -1.0 to +1.0
    let steer = (dx / maxRadius);     // -1.0 to +1.0

    let left = throttle + steer;
    let right = throttle - steer;

    let leftPWM = Math.round(left * maxSpeed);
    let rightPWM = Math.round(right * maxSpeed);

    let now = Date.now();
    if (now - lastSend > 60) { // Send packet every 60ms
      lastSend = now;
      fetch(`/drive?left=${leftPWM}&right=${rightPWM}`).catch(() => {});
    }
  }
</script>
</body>
</html>
```

---

## 6. Companion OpenCV Vision Bridge Specification

To replicate the Phase 1 automated pest and weed targeting on the ESP32-CAM stream, a Python bridge script (`opencv_cam_bridge.py`) runs on a companion PC/laptop:

```python
"""
opencv_cam_bridge.py
Captures ESP32-CAM MJPEG stream, performs HSV color segmentation for
caterpillars (purple) and weeds (red), renders targeting reticles,
and issues autonomous micro-burst spray triggers.
"""

import cv2
import numpy as np
import urllib.request
import time

STREAM_URL = "http://192.168.1.150:81/stream"  # Or http://192.168.4.1:81/stream
TRIGGER_URL = "http://192.168.1.150/spray?ms=200"

# HSV Color Ranges matching Phase 1 baseline
PURPLE_LOWER = np.array([130, 50, 50])
PURPLE_UPPER = np.array([160, 255, 255])

RED_LOWER_1 = np.array([0, 70, 50])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 70, 50])
RED_UPPER_2 = np.array([180, 255, 255])

last_spray_time = 0
SPRAY_COOLDOWN = 3.0  # seconds between auto-sprays

def trigger_esp32_spray():
    global last_spray_time
    if time.time() - last_spray_time > SPRAY_COOLDOWN:
        try:
            urllib.request.urlopen(TRIGGER_URL, timeout=0.5)
            print("[AUTO-SPRAY] Micro-burst triggered on ESP32-CAM!")
            last_spray_time = time.time()
        except Exception as e:
            print(f"[ERROR] Failed to trigger spray: {e}")

def main():
    print(f"Connecting to ESP32-CAM stream at: {STREAM_URL}")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Dropped frame / reconnecting...")
            time.sleep(0.1)
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Caterpillar Segmentation (Purple mask)
        mask_purple = cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER)

        # Weed Segmentation (Red mask)
        mask_red1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
        mask_red2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
        mask_weed = cv2.bitwise_or(mask_red1, mask_red2)

        combined_mask = cv2.bitwise_or(mask_purple, mask_weed)
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w, _ = frame.shape
        center_x_min, center_x_max = int(w * 0.35), int(w * 0.65)

        # Draw aiming reticle
        cv2.rectangle(frame, (center_x_min, int(h * 0.2)), (center_x_max, int(h * 0.8)), (0, 255, 0), 2)
        cv2.putText(frame, "TARGET RETICLE", (center_x_min, int(h * 0.18)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 450:  # Noise threshold
                x, y, cw, ch = cv2.boundingRect(cnt)
                cx = x + cw // 2
                cy = y + ch // 2

                cv2.rectangle(frame, (x, y), (x + cw, y + ch), (0, 0, 255), 2)
                cv2.putText(frame, f"THREAT: {int(area)}px", (x, y - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # If target is inside center reticle, trigger spray
                if center_x_min <= cx <= center_x_max:
                    cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)
                    trigger_esp32_spray()

        cv2.imshow("Agri Rover ESP32-CAM OpenCV Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

---

## 7. 3D WebGL Digital Twin Synchronization

The ESP32-CAM prototype integrates directly with the Phase 1 React Three.js Digital Twin:
1. **Camera HUD Overlay:** The React Digital Twin dashboard embeds the live stream (`<img src="http://192.168.1.150:81/stream">`) in the upper-right Picture-in-Picture (PiP) viewport.
2. **Kinematic Pose Mirroring:** When steering commands are dispatched from the phone or OpenCV bridge, the same normalized $(v, \omega)$ vectors are broadcast via WebSocket to the React Three.js simulation. The 3D rover model turns its wheels and drives across the virtual crop rows in real time.
3. **Spray Particle Sync:** When `/spray` is fired, the Digital Twin triggers its instanced Three.js particle mist emitter, simulating pressurized chemical discharge matching the physical rover.
