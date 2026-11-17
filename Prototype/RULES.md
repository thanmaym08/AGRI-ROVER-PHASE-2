# Development Rules & Engineering Standards (RULES.md) — Prototype
## Agri Rover: ESP32-CAM Edge IoT Teleoperated & Autonomous Vision Testbed

**Document Version:** 1.0.0  
**Project Code:** MMCA34 — Agri Rover Phase II Prototype Work  
**Hardware Target:** AI-Thinker ESP32-CAM Module  
**Status:** Mandatory Engineering Constraints  

---

## 1. Hardware, Power & Pin Protection Rules

### RULE-ESP-PWR-01: Dedicated 5.1V High-Amperage Power Supply
- **Constraint:** During Wi-Fi transmission bursts (up to $+20\text{ dBm}$ TX power) combined with active OV2640 camera capture, the ESP32-CAM draws instantaneous peak currents exceeding $450\text{–}500\text{ mA}$.
- **Rule:**
  1. The ESP32-CAM `5V` pin MUST be supplied by an active step-down buck converter (e.g., LM2596 or MP1584) tuned to **$5.10\text{V} \pm 0.05\text{V}$** with at least a **$2.0\text{A}$ continuous rating**.
  2. NEVER power the ESP32-CAM from an FTDI programmer's 3.3V rail. FTDI onboard 3.3V LDOs are rated for only $50\text{–}100\text{ mA}$ and will instantly trip the hardware brownout detector (`Brownout detector was triggered`).
  3. When flashing via FTDI, connect FTDI `VCC (5V)` to ESP32-CAM `5V` (or power the ESP32-CAM from an external 5V bench source with shared GND).

### RULE-ESP-PWR-02: Bulk Decoupling & Brownout Suppression
- **Constraint:** High inrush currents from 12V DC drive motors and the spray pump create severe ground bounce and $V_{CC}$ sag on shared battery rails.
- **Rule:**
  1. A low-ESR electrolytic capacitor of **$\ge 1000\mu\text{F} / 16\text{V}$** combined in parallel with a **$100\text{nF}$ ceramic capacitor** MUST be soldered as close as physically possible to the ESP32-CAM `5V` and `GND` header pins.
  2. The motor drive voltage (12V) and logic voltage (5.1V) must be electrically isolated via the buck converter.
  3. A single common **Star Ground Point** must tie Battery Negative, Buck Converter GND, Motor Driver GND, Relay GND, and ESP32-CAM GND together. Daisy-chaining high-current motor return paths through the microcontroller breadboard/PCB is strictly prohibited.

### RULE-ESP-PIN-01: Boot Strapping Pin Isolation & Voltage Levels
- **Constraint:** The ESP32-CAM exposes only 16 pins, most of which are multi-function or serve as boot configuration strapping pins during power-up.
- **Rule:**
  1. **GPIO 0 (Boot Mode):**
     - Pull to `GND` ONLY during firmware flashing.
     - Leave floating or pulled HIGH during normal boot. If GPIO 0 is grounded at power-on, the ESP32 enters UART download mode and firmware will not execute.
  2. **GPIO 12 (MTDI - Flash Voltage Select):**
     - **CRITICAL:** GPIO 12 MUST NOT be driven HIGH during power-on boot.
     - If GPIO 12 is HIGH at boot, the internal flash LDO switches from 3.3V to 1.8V, permanently corrupting or stalling SPI flash read operations (continuous crash loop: `rst:0x10 (RTCWDT_RTC_RESET)`).
     - When connecting to motor driver inputs (e.g., L298N `IN1`), ensure the driver board has a pull-down resistor or leaves GPIO 12 LOW at boot.
  3. **GPIO 2 (Boot / Blue Status LED):**
     - Connected to the onboard blue LED. Must be LOW or floating during bootloader entry.
     - Safe to use as an active-HIGH relay trigger or status indicator after boot.
  4. **GPIO 15 (MTDO - Boot Silence):**
     - Outputs high-frequency debug PWM clock pulses for $\approx 50\text{ ms}$ upon power-up.
     - Motor drivers connected to GPIO 15 must tolerate this brief startup jitter without uncommanded wheel motion.

### RULE-ESP-PIN-02: Strict Separation of Camera & PSRAM Buses
- **Constraint:** The AI-Thinker module internally allocates 15 GPIO lines to the OV2640 DVP parallel interface and 2 lines to the external 4MB PSRAM chip.
- **Rule:**
  1. **Internal Camera Bus (FORBIDDEN FOR EXTERNAL WIRING):**
     - Data lines: `GPIO 36 (D0)`, `GPIO 37 (D1)`, `GPIO 38 (D2)`, `GPIO 39 (D3)`, `GPIO 35 (D4)`, `GPIO 14 (D5)*` *(Note: Exposed on header; see conflict mitigation below)*, `GPIO 34 (D6)`, `GPIO 35 (D7)`.
     - Clock/Sync lines: `GPIO 25 (PCLK)`, `GPIO 23 (VSYNC)`, `GPIO 22 (HREF)`, `GPIO 0 (XCLK)`.
     - SCCB (I2C) control lines: `GPIO 26 (SIOD)`, `GPIO 27 (SIOC)`.
     - Power/Reset lines: `GPIO 32 (PWDN)`.
  2. **PSRAM Bus:** `GPIO 16 (CS)` and `GPIO 17 (CLK)` are hardwired to the external PSRAM IC on AI-Thinker boards. Connecting external sensors or actuators to GPIO 16 will crash camera frame capture.
  3. **Flash LED:** `GPIO 4` is hardwired to the ultra-bright SMD flash LED via an NPN transistor. Reserve GPIO 4 exclusively for workspace lighting and inspection.

---

## 2. Pin Mapping & Motor/Relay Allocation Standard

To eliminate pin collisions while retaining camera functionality, the prototype adopts the following standard pin allocation:

| ESP32-CAM Pin | Prototype Assignment | Peripheral Device | Electrical Configuration | Safety Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **GPIO 12** | Motor Left Direction A (`IN1`) | L298N / DRV8833 | Digital Output / PWM | MUST be LOW at boot (avoid flash voltage fault). |
| **GPIO 13** | Motor Left Direction B (`IN2`) | L298N / DRV8833 | Digital Output / PWM | Normal output. |
| **GPIO 14** | Motor Right Direction A (`IN3`) | L298N / DRV8833 | Digital Output / PWM | Shared with MicroSD card clock; ensure SD disabled. |
| **GPIO 15** | Motor Right Direction B (`IN4`) | L298N / DRV8833 | Digital Output / PWM | Startup jitter protected; pulled LOW at boot. |
| **GPIO 2** | Chemical Spray Relay Trigger | 5V Optocoupled Relay | Digital Output | Active HIGH ($200\text{ ms}$ micro-pulse). Safe at boot. |
| **GPIO 4** | High-Intensity Floodlight | Onboard Flash LED | LEDC Hardware PWM | Dedicated illumination channel ($0\text{–}255$). |
| **GPIO 1 (TX)**| Optional Serial Debug / Telemetry | Host PC / FTDI | UART0 TXD | Disconnected in field or used for telemetry stream. |
| **GPIO 3 (RX)**| Optional External Sensor Input | Auxiliary Input | UART0 RXD | Can be repurposed as digital input after boot. |

---

## 3. Motion Control & Actuation Rules

### RULE-ESP-ACT-01: Failsafe Wireless Watchdog
- **Constraint:** Mobile Wi-Fi connections can experience packet drops, interference, or browser backgrounding while the robot is moving.
- **Rule:**
  1. Every motion command (`/drive`, `/control`, or WebSocket frame) must update an internal unsigned 32-bit timestamp: `last_command_millis = millis()`.
  2. Core 1 must evaluate the watchdog condition every $50\text{ ms}$:
     $$\text{if } (\text{millis}() - \text{last\_command\_millis} > 500\text{ ms}) \implies \text{force\_stop\_motors}()$$
  3. All 4 motor PWM channels must be set to `0%` duty cycle immediately upon timeout.
  4. The rover must remain fully immobilized until a fresh, valid steering command is parsed.

### RULE-ESP-ACT-02: Directional Reversal Dead-Time
- **Constraint:** Switching an H-Bridge directly from full forward to full reverse without dead-time creates inductive shoot-through spikes and can burn out L298N bipolar transistors.
- **Rule:**
  1. Before toggling directional logic from Forward (`IN1=HIGH, IN2=LOW`) to Reverse (`IN1=LOW, IN2=HIGH`), the software must:
     - Set all motor inputs to `LOW` ($0\%$ PWM).
     - Enforce a minimum **$5\text{ ms}$ dead-time delay**.
     - Assert the new directional state.

### RULE-ESP-ACT-03: Non-Blocking Spray Actuation
- **Constraint:** The agricultural precision spraying mechanism delivers calibrated micro-bursts ($200\text{ ms}$).
- **Rule:**
  1. Actuation timing MUST be handled via asynchronous FreeRTOS software timers or non-blocking delta-time tracking in the Core 1 control loop.
  2. The use of blocking delay functions (e.g., `delay(200);`) in web request handlers or main loops is **STRICTLY PROHIBITED**.
  3. Blocking delays stall the network stack, drop Wi-Fi packets, cause camera frame buffer overflow, and freeze video rendering on the operator's phone.

---

## 4. Video Streaming & Memory Management Rules

### RULE-ESP-MEM-01: Mandatory PSRAM Frame Buffering
- **Constraint:** Raw RGB888 frames at VGA resolution ($640\times 480 \times 3$) require $921.6\text{ KB}$, far exceeding the ESP32's available internal SRAM ($520\text{ KB}$ shared).
- **Rule:**
  1. Always configure the camera driver to capture compressed JPEG format in external PSRAM:
     ```c
     config.pixel_format = PIXFORMAT_JPEG;
     config.frame_size = FRAMESIZE_VGA; // 640x480
     config.jpeg_quality = 12;          // 10-63 (lower = higher quality)
     config.fb_count = 2;               // Double buffering in PSRAM
     config.fb_location = CAMERA_FB_IN_PSRAM;
     ```
  2. If `psramFound()` returns `false` (defective board or PSRAM disabled in IDE), the firmware must automatically downscale to `FRAMESIZE_QVGA` ($320\times 240$) and set `fb_count = 1` to prevent immediate memory allocation crashes.

### RULE-ESP-MEM-02: Deterministic Frame Buffer Lifecycle
- **Constraint:** Failing to release camera frame buffers back to the driver causes DMA FIFO starvations and fatal kernel crashes within milliseconds.
- **Rule:**
  1. Every call to `esp_camera_fb_get()` MUST have a matching `esp_camera_fb_return(fb)` in all code execution paths (including error branches, client disconnects, and timeouts).
  2. Example canonical pattern:
     ```c
     camera_fb_t *fb = esp_camera_fb_get();
     if (!fb) {
         httpd_resp_send_500(req);
         return ESP_FAIL;
     }
     esp_err_t res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
     esp_camera_fb_return(fb); // MUST BE CALLED IMMEDIATELY
     return res;
     ```

---

## 5. Mobile Phone Application & UI Standards

### RULE-ESP-UI-01: Zero-Dependency Embedded Serving
- **Constraint:** The mobile application must run on any operator smartphone directly in the field without internet access or App Store installation.
- **Rule:**
  1. All HTML5, CSS3, and JavaScript assets must be embedded into the ESP32 firmware image (in `PROGMEM` or LittleFS/SPIFFS as compressed GZIP payloads).
  2. No external CDNs (Google Fonts, external JS libraries, unbundled scripts) are permitted. All touch joystick handlers, canvas renderers, and stream display tags must resolve from local flash memory.
  3. Asset payload size for the entire mobile web app must not exceed **$150\text{ KB}$** uncompressed ($<50\text{ KB}$ gzipped).

### RULE-ESP-UI-02: Touch Ergonomics & Multi-Touch Support
- **Constraint:** Farm operators operate the interface outdoors, often one-handed or wearing protective nitrile gloves.
- **Rule:**
  1. The virtual joystick touch boundary must occupy at least $35\%$ of the screen width on mobile viewports.
  2. The emergency STOP button and SPRAY BURST button must have minimum touch target dimensions of **$64\times 64\text{ px}$** with high-contrast visual states (idle, active, triggered).
  3. Browser default gestures (pinch-to-zoom, pull-to-refresh, double-tap zoom) must be strictly suppressed via viewport meta tags and touch-action CSS rules (`touch-action: none;`).

---

## 6. Assistant Workflow & Operational Guidelines

### RULE-WORKFLOW-01: Proactive Workspace & Media Inspection
- **Rule:**
  1. Whenever the user mentions adding, dropping, or placing files, photos, or hardware assets (or whenever files appear in `Prototype/`), proactively inspect and analyze them immediately on the very first turn without waiting for a reminder or prompt.
  2. Perform full technical evaluations (chip labels, pinout mapping, logic levels, schematic compatibility) and report findings directly.

### RULE-WORKFLOW-02: Global Living Specification & Prompt Ingestion Protocol
- **Rule:**
  1. For EVERY user prompt, conduct thorough end-to-end multi-disciplinary analysis (Hardware, Firmware, Kinematics, Electrical, HMI, Testing).
  2. Continuously synchronize all decisions, calibrations, user constraints, and code updates into the persistent living specifications: `PRD.md`, `DESIGN.md`, `TASKS.md`, and `MEMORY.md`.
  3. Ensure code, schematics, and documentation are never out of sync.


