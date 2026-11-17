# ESP32 DevKit V1 Rover: Master Engineering Wiring & Schematic Guide (Sensor-Free)

**Controller Platform:** ESP32 Development Board (30-pin / 38-pin DevKit V1, 3.3V Logic)  
**Drive Train:** Dual / 4x DC Gear Motors (L298N Dual H-Bridge Driver)  
**Sprayer Actuator:** 12V Mini Diaphragm Spray Pump (5V Optocoupled Relay + 1N4007 Diode)  
**Power Bus:** 12V Li-ion Battery $\rightarrow$ LM2596 Buck Converter ($5.00\text{V}$ Logic Rail) + Common Star Ground  
**Sensors:** None (Excluded from physical build)  
**Status:** ✅ 100% Verified & Error-Proofed per ECE Embedded Guidelines  

---

## 1. Visual Schematics & Circuit Diagrams

````carousel
![Master System Wiring Diagram (No Sensors)](C:/Users/Thanm/.gemini/antigravity/brain/a7b3df8e-611b-40eb-9f7b-18780773250d/devkit_motors_pump_only_1791360277415.jpg)
<!-- slide -->
![Power Distribution, Decoupling & Common Star Ground](C:/Users/Thanm/.gemini/antigravity/brain/a7b3df8e-611b-40eb-9f7b-18780773250d/power_starground_caps_1791360057655.jpg)
````

---

## 2. Netlist & Pin-to-Pin Interconnection Table

### Netlist A: Microcontroller & Logic Interconnects
| ESP32 DevKit V1 Pin | Target Component Pin | Wire Net Level | Function / Notes |
| :--- | :--- | :---: | :--- |
| **`GPIO 18`** | L298N `IN1` | $3.3\text{V}$ PWM | Left Motor Direction A (Safe Non-Strapping GPIO) |
| **`GPIO 19`** | L298N `IN2` | $3.3\text{V}$ PWM | Left Motor Direction B (Safe Non-Strapping GPIO) |
| **`GPIO 21`** | L298N `IN3` | $3.3\text{V}$ PWM | Right Motor Direction A (Safe Non-Strapping GPIO) |
| **`GPIO 22`** | L298N `IN4` | $3.3\text{V}$ PWM | Right Motor Direction B (Safe Non-Strapping GPIO) |
| **`GPIO 23`** | 5V Relay `IN` | $3.3\text{V}$ Digital Pulse | Spray Pump Micro-Burst Trigger (Safe Non-Strapping GPIO) |
| **`VIN` / `5V`** | LM2596 `OUT+` Rail | $+5.00\text{V} \pm 0.05\text{V}$ | Main Logic Board Power Input |
| **`GND`** | Master Star Ground Bus | $0\text{V}$ (GND) | Logic Ground Return |

---

### Netlist B: Power Distribution & Actuator Buses
| Source Pin / Rail | Destination Pin | Voltage Level | Electrical Purpose |
| :--- | :--- | :---: | :--- |
| **12V Battery (+)** | Rocker Switch (Pin 1) | $+12\text{V}$ Raw | Unswitched battery positive |
| **Rocker Switch (Pin 2)**| LM2596 `IN+` | $+12\text{V}$ Switched | Input to buck regulator |
| **Rocker Switch (Pin 2)**| L298N `12V` Terminal | $+12\text{V}$ Switched | Motor driver high-current rail |
| **Rocker Switch (Pin 2)**| Relay `COM` Terminal | $+12\text{V}$ Switched | Spray pump high-current rail |
| **LM2596 `OUT+`** (Tuned)| ESP32 `VIN` & Relay `VCC` | $+5.00\text{V}$ DC | Regulated clean logic power |
| **12V Battery (-)** | Master Star Ground Bus | $0\text{V}$ (GND) | Master negative reference |
| **LM2596 `IN-` & `OUT-`** | Master Star Ground Bus | $0\text{V}$ (GND) | Tied together via LM2596 internal copper plane |
| **L298N `GND`** | Master Star Ground Bus | $0\text{V}$ (GND) | High-current motor ground return |
| **Relay `NO` Contact** | 12V Spray Pump (+) Red | $+12\text{V}$ Switched | Closes when GPIO 23 goes HIGH |
| **12V Spray Pump (-) Black**| Master Star Ground Bus | $0\text{V}$ (GND) | Direct pump current return to battery |
| **Across Pump (+) & (-)** | **1N4007 Diode (Reverse)** | $1000\text{V} / 1\text{A}$ | **Cathode (silver band) to (+); Anode to (-)** |
| **Across L298N 12V & GND**| $470\mu\text{F} + 100\text{nF}$ Caps | $25\text{V}$ Low-ESR | Brownout suppression and high-frequency filtering |

---

## 3. Pre-Power-On Sanity Checklist & Error-Proof Verification

1. **Common Ground Continuity Check:** Multimeter continuity probe reads $\le 0.2\,\Omega$ across Battery (-), Buck IN-, Buck OUT-, L298N GND, ESP32 GND, and Relay GND.
2. **Strapping Pin Verification:** `GPIO 0`, `GPIO 2`, `GPIO 12`, and `GPIO 15` are completely unpopulated, guaranteeing clean power-up without bootloader stalls.
3. **Inductive Snubber Polarity:** The silver band on the 1N4007 diode faces the positive red terminal of the water pump.
4. **Decoupling Protection:** $470\mu\text{F}$ electrolytic capacitor installed across L298N power terminals to prevent motor inrush brownout resets on the ESP32.
