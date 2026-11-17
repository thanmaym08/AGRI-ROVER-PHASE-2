# Agent Operating Guidelines & Rules (AGENTS.md)
# Location: Project Root / Applied automatically to all subdirectories and prompts

---

## 1. Proactive Workspace & Media Inspection (Zero-Prompt Directive)
- **Mandate:** Whenever the user mentions adding, dropping, or placing files, photos, or hardware assets—or whenever new images/files are detected in the workspace—the assistant must **proactively inspect, analyze, and diagnose them immediately on that very turn** without waiting for the user to ask or prompt.
- **Scope of Analysis:**
  - Read chip labels, part numbers, and markings.
  - Evaluate pinouts, voltage levels (3.3V vs 5V vs 12V), and logic compatibility.
  - Check physical form factors (e.g. Arduino shield headers vs standalone breakout modules).
  - Report findings directly with clear **Compatible / Incompatible** verdicts.

---

## 2. Hardware Safety & Electrical Protection Guardrails
- **Inductive Load Protection:** Never propose connecting inductive loads (motors, pumps, solenoids, relays) directly to microcontroller GPIO pins without flyback diodes (e.g., 1N4007) and optocoupled/MOSFET drivers.
- **Power Isolation & Brownout Prevention:**
  - Logic rails (3.3V / 5V) must always be electrically isolated from high-current motor rails via buck converters or dedicated supplies.
  - Always enforce bulk decoupling capacitors (e.g., $\ge 1000\mu\text{F}$) across MCU power rails when driving motors.
  - Require a single **Common Star Ground** across all voltage domains to prevent ground loops.
- **Pin Strapping & Boot Safety:**
  - For ESP32 / ESP32-S3 / ESP8266 / Raspberry Pi, always verify boot strapping pin restrictions (e.g. GPIO 0, 2, 12, 15 on ESP32) before assigning them to actuators.
  - Enforce software failsafe watchdogs (auto-braking motors if wireless communication drops $>500\text{ ms}$).

---

## 3. Code Generation & Implementation Standards
- **Complete, Non-Truncated Code:** Never output lazy placeholders like `// TODO: implement logic here` or `... rest of your code ...`. Always produce fully compilable, production-ready sketches and scripts.
- **Defensive Error Handling:** Hardware communication (I2C, SPI, UART, Wi-Fi, HTTP, WebSockets) must always include timeouts and try-catch/null checks to prevent silent device hangs.
- **Non-Blocking Execution:** For embedded microcontrollers, avoid blocking `delay()` calls in web servers or control loops. Use `millis()` delta-timing or FreeRTOS software timers.

---

## 4. Verification & Testing Discipline
- **Proactive Verification:** Whenever creating scripts or testable logic, run quick automated syntax checks or unit tests to verify they execute cleanly before handing them to the user.
- **Realistic Sourcing & Budgeting:** When suggesting electronic components, provide realistic market availability, exact search keywords, and verified prices for the user's region (e.g., Amazon India, Robu.in, ElectronicsComp).

---

## 5. Communication & Documentation Style
- **Lead with the Verdict:** Always give direct, clear answers first (e.g., "✅ Compatible" or "❌ Incompatible"), followed by the technical rationale, schematics, and actionable next steps.
- **Visuals & Tables:** Prefer structured markdown tables, ASCII schematics, and clickable links for complex technical data.

---

## 6. Global Living Specification & Deep Prompt Analysis Directive (Living-Doc Protocol)
- **Mandate:** For EVERY prompt the user submits, the assistant must:
  1. **Deep Architectural Analysis:** Thoroughly deconstruct and evaluate the prompt across all cyber-physical dimensions: Hardware Safety, Electrical Voltage/Current, Firmware & FreeRTOS Timing, Motor Kinematics, Mobile UI/UX, and System Integration—leaving zero ambiguity.
  2. **Living Specification Synchronization (PRD / DESIGN / TASKS / MEMORY):**
     - Treat `PRD.md`, `DESIGN.md`, `TASKS.md`, and `MEMORY.md` as live, continuous source-of-truth documents.
     - Systematically ingest new user requirements, decisions, calibrations, and hardware changes into these documents just as was done during initial project setup.
     - Check off completed milestones in `TASKS.md` and record all architectural trade-offs in `MEMORY.md` (ADRs).
  3. **Zero-Drift Code & Doc Alignment:** Never leave code, wiring schematics, and documentation out of sync. Any change in code or wiring must immediately be reflected in the living documentation.

