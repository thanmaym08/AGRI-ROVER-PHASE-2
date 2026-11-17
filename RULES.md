# Development Rules & Engineering Standards (RULES.md)
## Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring

**Document Version:** 2.0.0  
**Project Code:** MMCA34 (Project Work - Phase I & Phase II, 2025–2027 Batch)  
**Institution:** Department of Master of Computer Applications, BMS Institute of Technology & Management (BMSITM), Bengaluru  
**Affiliation:** Autonomous Institution affiliated to Visvesvaraya Technological University (VTU)  

---

## 1. Hardware Safety & Electrical Protection Rules

### RULE-HW-01: Mandatory Under-Voltage Cutoff
- **Constraint:** The system battery supply voltage must be continuously sampled every $50\text{ ms}$.
- **Rule:** If the supply voltage drops to $\le 12.0\text{V}$ ($\le 12\%$ state-of-charge), an immediate **Emergency Shutdown** must be asserted:
  1. All motor PWM duty cycles set to `0%`.
  2. Direction enable pins (`L_EN` / `R_EN`) set to `LOW`.
  3. Both 12V solenoid valves immediately de-energized (`LOW`).
  4. Chemical pump MOSFET gate pulled `LOW`.
- **Rationale:** Deep discharge below 12.0V damages lead-acid/LiFePO4 cells, causes logic rail brownouts, and leads to erratic Raspberry Pi crashes.

### RULE-HW-02: Soil Probe Drive Interlock
- **Constraint:** The linear actuator probe must never deploy while the rover is in motion.
- **Rule:** Before issuing step pulses to the linear actuator stepper motor:
  1. Drive motor PWM commands must be set to `0%`.
  2. The software must assert and confirm zero wheel velocity for at least $200\text{ ms}$.
  3. Drive commands must be completely rejected by the motion controller until the probe is fully retracted to its physical home limit switch.
- **Rationale:** Moving the rover with the probe embedded in soil will snap the mechanical actuator and destroy sensor electrodes.

### RULE-HW-03: Inductive Load & Flyback Isolation
- **Constraint:** 12V solenoid valves and diaphragm pumps generate severe inductive voltage spikes ($> 100\text{V}$) on coil de-energization.
- **Rule:** 
  1. Every inductive coil MUST have an antiparallel flyback diode (1N4007 or 1N5819 Schottky) connected directly across its terminals.
  2. Relay coils and MOSFET gates must be driven through optocouplers. Direct connection from Raspberry Pi GPIO pins to inductive coils or unbuffered MOSFET gates is strictly prohibited.
- **Rationale:** Prevents catastrophic back-EMF destruction of Raspberry Pi GPIO silicon.

### RULE-HW-04: Motor Enable & Direction Sequencing
- **Constraint:** BTS7960 H-bridges require correct logic state sequencing.
- **Rule:**
  1. Always assert `L_EN` and `R_EN` to `HIGH` before applying non-zero PWM duty cycle.
  2. When reversing direction, set PWM to `0%`, wait a minimum dead-time of $5\text{ ms}$, then switch directional PWM channels (`RPWM` vs `LPWM`).
  3. Never toggle `RPWM` and `LPWM` simultaneously on the same BTS7960 driver.
- **Rationale:** Prevents shoot-through current spikes across high-side and low-side MOSFETs.

### RULE-HW-05: GPIO Safe Initialization & Mandatory Teardown
- **Constraint:** Leaving GPIO pins floating or driven HIGH on script exit can leave motors running or valves open.
- **Rule:**
  1. All Python hardware scripts must configure initial states explicitly:
     ```python
     GPIO.setmode(GPIO.BCM)
     GPIO.setwarnings(False)
     # Set safe defaults
     GPIO.setup(VALVE_PINS, GPIO.OUT, initial=GPIO.LOW)
     ```
  2. All hardware loops must be wrapped in `try ... finally:` blocks executing `GPIO.cleanup()`.
- **Rationale:** Guarantees that unhandled Python exceptions or `Ctrl+C` interrupts immediately safe the physical rover.

---

## 2. Software Development & Coding Standards

### RULE-SW-01: Python Code Standards (PEP 8 & Modularity)
- All Python scripts must adhere to **PEP 8** style guidelines.
- **Type Annotations:** All function signatures must include Python type hints:
  ```python
  def execute_sprayer_logic(rover_is_moving: bool, detected_targets: list[dict[str, str]]) -> bool:
  ```
- **Single Responsibility Principle:** Code must be segregated into single-purpose modular files:
  - `motor_control_pi.py`: Kinematics, PWM, and wheel motion.
  - `pesticide_sprayer.py`: Pump pressure, solenoid timing, dosage logging.
  - `camera_stream.py`: Frame acquisition, color thresholding, contour extraction.
  - `soil_probe_controller.py`: Stepper sequencing and sensor reading.
- **Structured Logging:** Use the standard Python `logging` module with standardized timestamps and log levels (`INFO`, `WARNING`, `ERROR`). `print()` statements in production hardware loops are prohibited.

### RULE-SW-02: JavaScript & 3D WebGL Best Practices
- **Resource Lifecycle & Memory Leaks:** WebGL geometries, materials, and textures do NOT get automatically garbage collected. When re-rendering or tearing down 3D objects, explicitly invoke:
  ```javascript
  geometry.dispose();
  material.dispose();
  texture.dispose();
  ```
- **Frame Rate Independence:** All physics integrations, rover rotations, and particle mist updates in Three.js must be multiplied by `clock.getDelta()` to maintain uniform behavior across displays ($60\text{Hz}$ vs $144\text{Hz}$).
- **Offline Self-Containment:** The 3D Digital Twin must import Three.js, OrbitControls, and assets locally or via pre-cached bundles. No runtime reliance on un-cached CDNs.

### RULE-SW-03: Simulation-Before-Hardware Verification Rule
- **Mandatory Workflow:** No autonomous navigation algorithm, computer vision color mask adjustment, or micro-burst timing profile may be flashed to the physical Raspberry Pi without first executing and passing in the **3D WebGL Digital Twin Simulator**.
- **Rationale:** Saves battery cycles, prevents field collisions, eliminates agrochemical spillage during testing, and adheres to academic verification standards.

---

## 3. Git, Version Control & Collaboration Rules

### RULE-VC-01: Branching Strategy
- **`main`**: Production-ready, fully tested releases (Phase 1 Final, Phase 2 Final). Protected branch.
- **`phase-1-release`**: Stable tag for Phase 1 submission and academic evaluation.
- **`phase-2-dev`**: Active integration branch for Phase 2 development (YOLOv8, RTK-GPS, LoRaWAN).
- **`feature/<name>`**: Topical feature branches branched from `phase-2-dev` (e.g., `feature/yolov8-nano-quant`, `feature/lorawan-telemetry`).

### RULE-VC-02: Conventional Commit Messages
All commit messages must follow the Conventional Commits specification:
- `feat: <description>`: A new feature (e.g., `feat: implement 200ms calibrated micro-burst pulse`).
- `fix: <description>`: A bug fix (e.g., `fix: prevent race condition in soil probe stepper enable`).
- `docs: <description>`: Documentation changes (e.g., `docs: update ARCHITECTURE.md with BCM pinout`).
- `test: <description>`: Adding or modifying unit/automation tests (e.g., `test: add UT-06 battery shutdown test`).
- `refactor: <description>`: Code changes that neither fix a bug nor add a feature.

---

## 4. Academic & Research Integrity Rules

### RULE-AC-01: Metric Reproducibility & Truthfulness
- All experimental numbers reported in documentation and presentations (e.g., *"up to 80% chemical pesticide volume reduction"*, *"18–22 FPS inference rate"*, *"sub-50ms solenoid actuation"*) must trace back to recorded empirical test logs or verified physical/simulation benchmarks.
- Estimations or projected Phase 2 targets must be clearly designated as **Target / Future Scope**.

### RULE-AC-02: University & Department Alignment
- All formal deliverables must strictly adhere to the formatting guidelines defined by the **Department of Master of Computer Applications, BMSITM**:
  - Course Code: **MMCA34 (Project Work - Phase I / Phase II)**
  - Heading font: 12–14 pt Times New Roman, Bold.
  - Body font: 12 pt Times New Roman, 1.5 line spacing, Justified.
  - Figures captioned below (`Fig. No: <Caption>`), Tables captioned above (`Table No: <Caption>`).

---

## 5. Living Specification & Continuous Prompt Analysis Protocol

### RULE-LIV-01: Universal Prompt Deconstruction Mandate
- Every user prompt must be evaluated across all system layers (Electrical, Microcontroller Strapping, Kinematics, Firmware, Web HMI, Safety Watchdogs).
- No requirement or feedback may remain solely in conversational dialogue. Every decision, calibration, or architecture refinement must be immediately codified in the living specification repository:
  1. `PRD.md`: Functional criteria, speed regimes, HMI layout requirements.
  2. `DESIGN.md`: Hardware schematics, motor kinematics, differential equations, pinout maps.
  3. `TASKS.md`: Task tracking, acceptance criteria verification, completed milestones.
  4. `MEMORY.md`: Architectural Decision Records (ADRs) and persistent user preferences.

