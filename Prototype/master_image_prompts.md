# 🌿 Agri Rover Phase 2 — Master Image Generation Prompts for Claude

**Purpose:** Copy-paste these prompts into Claude to generate accurate, professional wiring diagrams for the Agri Rover ESP32-CAM Prototype.  
**Total Prompts:** 6 (covering every single wire in the entire system)  
**Usage:** Copy everything inside a `PROMPT START` / `PROMPT END` block and paste directly into Claude.

---

## Prompt 1 of 6: Complete Master System Wiring Diagram (All Components)

> **What this generates:** One single unified diagram showing ALL 7 components and EVERY wire in the entire rover.

<!-- PROMPT START -->

Generate a highly detailed, professional electronics wiring schematic diagram on a pure white background. This is for a 4WD agricultural robot rover prototype. Arrange all components clearly with generous spacing, bold color-coded wires, and large legible labels.

COMPONENTS TO DRAW (exact count and position):
1. TOP-LEFT: A blue 3S 12V Li-ion battery pack (labeled "12V 3S Li-ion Battery"). A red wire exits the (+) terminal and passes through a black SPST rocker switch before continuing.
2. CENTER-LEFT: A blue LM2596 DC-DC step-down buck converter module with 4 screw terminals clearly labeled "IN+", "IN-", "OUT+", "OUT-" and a brass adjustment trimpot on top.
3. BOTTOM-LEFT: A black AI-Thinker ESP32-CAM board (with the silver camera module and gold antenna visible). A cylindrical black 1000uF 16V electrolytic capacitor is soldered across the 5V and GND header pins (long lead to 5V, short lead to GND).
4. CENTER: A red L298N dual H-bridge motor driver board with a large black aluminum heatsink on top. It has THREE distinct blue screw terminal blocks: LEFT side = 2 screws labeled OUT1 (top) and OUT2 (bottom); RIGHT side = 2 screws labeled OUT3 (top) and OUT4 (bottom); BOTTOM center = 3 screws labeled "+12V" (left), "GND" (center), "+5V" (right). Below the heatsink is a row of black pin headers labeled ENA, IN1, IN2, IN3, IN4, ENB with small black jumper caps on ENA and ENB.
5. FOUR CORNERS around the L298N: Four identical yellow TT DC geared motors with white plastic gear housings. Label them "Front-Left (FL)", "Rear-Left (RL)", "Front-Right (FR)", "Rear-Right (RR)". Each motor has exactly 2 brass solder tabs with a red wire on (+) and a black wire on (-).
6. BOTTOM-RIGHT: A blue/black 5V single-channel optocoupled relay module with 3 low-voltage pins (VCC, GND, IN) and 3 high-voltage screw terminals (COM, NO, NC).
7. FAR RIGHT: A black 12V mini diaphragm water pump with barbed hose fittings. A small black cylindrical 1N4007 diode is soldered directly across the pump's red and black wires (the silver cathode band faces the red positive wire).

WIRE CONNECTIONS (draw each wire as a bold, clearly colored line):
POWER WIRES (RED = +12V or +5V, BLACK = GND):
- Battery (+) RED wire → Rocker Switch Pin 1 → Switch Pin 2 branches into THREE red lines:
  • Red Line A → LM2596 "IN+"
  • Red Line B → L298N bottom terminal "+12V"
  • Red Line C → Relay high-voltage terminal "COM"
- LM2596 "OUT+" → RED wire splits to: ESP32-CAM "5V" pin AND Relay "VCC" pin (label this wire "+5.10V")
- Battery (-) BLACK wire → LM2596 "IN-"
- LM2596 "OUT-" → ESP32-CAM "GND" pin AND Relay "GND" pin

LOGIC SIGNAL WIRES (use distinct colors):
- ESP32 GPIO 12 → L298N header pin IN1 (BLUE wire)
- ESP32 GPIO 13 → L298N header pin IN2 (YELLOW wire)
- ESP32 GPIO 14 → L298N header pin IN3 (GREEN wire)
- ESP32 GPIO 15 → L298N header pin IN4 (ORANGE wire)
- ESP32 GPIO 2 → Relay pin "IN" (PURPLE wire)

MOTOR WIRES (RED and BLACK pairs):
- FL motor RED + RL motor RED twisted together → L298N "OUT1"
- FL motor BLACK + RL motor BLACK twisted together → L298N "OUT2"
- FR motor RED + RR motor RED twisted together → L298N "OUT3"
- FR motor BLACK + RR motor BLACK twisted together → L298N "OUT4"

PUMP & RELAY WIRES:
- Relay "NO" terminal → RED wire → Pump (+) red wire
- Pump (-) black wire → BLACK wire → LM2596 "IN-" (common ground)
- 1N4007 diode soldered across pump terminals (silver band toward red +)

GROUND CONNECTIONS (show clearly with a bold label "COMMON STAR GROUND"):
- All these BLACK ground wires connect to the LM2596 "IN-" terminal: Battery (-), L298N bottom "GND" terminal, Pump (-) black wire
- These BLACK ground wires connect to the LM2596 "OUT-" terminal: ESP32-CAM "GND", Relay "GND"
- Add a bold annotation: "LM2596 internally bridges IN- and OUT- on PCB (0Ω)"

STYLE: Clean technical diagram, no 3D effects, flat 2D top-down schematic view, white background, sharp bold wire lines (3px thickness), large readable sans-serif font labels, professional electronics educational poster quality.

<!-- PROMPT END -->

---

## Prompt 2 of 6: Ground Wire "Common Star Ground" via Mini Breadboard

> **What this generates:** Zoomed-in diagram showing how all 6 ground wires plug into a mini breadboard's blue negative rail as a clean, solder-free star ground bus.

<!-- PROMPT START -->

Generate a clear, zoomed-in educational electronics diagram on a pure white background showing ONLY the ground (GND / 0V) wire connections in a robot rover project. Show how 6 separate black ground wires from different components all connect together using a white mini breadboard as the central junction point.

COMPONENTS (draw only the ground-relevant portions, arranged in a circle around the central breadboard):
1. TOP-LEFT: A blue 12V battery pack showing only its BLACK negative (-) wire labeled "Battery GND (-)"
2. TOP-CENTER: A blue LM2596 buck converter module showing its "IN-" screw terminal with a black wire going to the breadboard, labeled "Buck IN- (Power GND)"
3. TOP-RIGHT: A blue LM2596 buck converter module showing its "OUT-" screw terminal with a black wire going to the breadboard, labeled "Buck OUT- (Logic GND)"
4. BOTTOM-LEFT: A red L298N motor driver board showing only the center screw of the bottom 3-pin blue terminal block labeled "L298N GND"
5. BOTTOM-CENTER: A black ESP32-CAM board showing only its "GND" header pin, labeled "ESP32 GND"
6. BOTTOM-RIGHT: A blue 5V relay module showing only its "GND" pin, labeled "Relay GND"
7. FAR RIGHT: A black 12V water pump showing only its BLACK (-) wire, labeled "Pump GND (-)"

CENTRAL ELEMENT — MINI BREADBOARD:
- In the exact CENTER of the diagram, draw a white 170-point mini breadboard (the small rectangular ones, approximately 4.5cm x 3.5cm, that come with Arduino starter kits).
- The breadboard has a BLUE NEGATIVE RAIL running along one long edge — a horizontal row of holes marked with a blue line and a large minus sign (-).
- Each of the 6-7 black ground wires from the surrounding components plugs into a separate hole along this BLUE NEGATIVE RAIL:
  • Hole 1: Battery (-) black wire
  • Hole 2: LM2596 "IN-" black wire
  • Hole 3: LM2596 "OUT-" black wire
  • Hole 4: L298N "GND" black wire
  • Hole 5: ESP32-CAM "GND" black jumper wire
  • Hole 6: Relay "GND" black jumper wire
  • Hole 7: Pump (-) black wire

LABELS AND ANNOTATIONS:
- Place a large bold title above the breadboard: "⭐ COMMON STAR GROUND BUS (0V)"
- Draw annotation arrows from each wire to its component with clear text labels
- Add a note below the breadboard: "All holes on this blue (−) rail are internally connected by a metal strip — plugging wires here links ALL grounds together with zero soldering!"
- Add a second note: "You can also use a 5-port WAGO 221 lever connector or a screw terminal strip instead of a breadboard."

STYLE: Ultra-clean, white background, large bold labels, color-coded annotations (all ground wires in BLACK, annotations in dark blue), educational infographic quality, top-down flat view, no shadows or 3D effects.

<!-- PROMPT END -->

---

## Prompt 3 of 6: ESP32-CAM to L298N & Relay Logic Pin Header Connections

> **What this generates:** Clear diagram showing only the 5 color-coded signal/logic jumper wires from ESP32-CAM GPIO pins to L298N header pins and relay IN pin.

<!-- PROMPT START -->

Generate a precise electronics wiring diagram on a pure white background showing ONLY the signal/logic jumper wire connections between an AI-Thinker ESP32-CAM board, an L298N motor driver board, and a 5V relay module.

LEFT SIDE — ESP32-CAM:
Draw the AI-Thinker ESP32-CAM board as a black rectangular PCB (approximately 27mm x 40mm) viewed from above with the camera module at the top and the antenna trace visible. Show both rows of gold header pins along the left and right long edges. Label EVERY pin in small but readable text:
- RIGHT column (top to bottom): 5V, GND, GPIO 12, GPIO 13, GPIO 15, GPIO 14, GPIO 2, GPIO 4, GPIO 0, GND
- LEFT column (top to bottom): 3V3, GND, GPIO 16, GPIO 0, GND
Highlight GPIO 12, 13, 14, 15, and 2 with colored circles matching the wire colors below.

RIGHT SIDE — L298N:
Draw the L298N motor driver board as a red rectangular PCB. Focus on the black pin header row at the bottom center of the board. Show these header pins in order left to right: ENA, IN1, IN2, IN3, IN4, ENB. Draw small black plastic jumper caps sitting on ENA and ENB pins. Add a label: "Keep jumper caps on ENA & ENB!"

BELOW RIGHT — 5V RELAY MODULE:
Draw a small blue/black 5V relay module with 3 header pins on its low-voltage side labeled left to right: VCC, GND, IN.

JUMPER WIRE CONNECTIONS (draw each as a bold, distinctly colored line with small black rectangular female Dupont connectors drawn on both ends of each wire):
1. ESP32 GPIO 12 → L298N IN1 = BLUE colored wire (label: "Left Motor Forward")
2. ESP32 GPIO 13 → L298N IN2 = YELLOW colored wire (label: "Left Motor Reverse")
3. ESP32 GPIO 14 → L298N IN3 = GREEN colored wire (label: "Right Motor Forward")
4. ESP32 GPIO 15 → L298N IN4 = ORANGE colored wire (label: "Right Motor Reverse")
5. ESP32 GPIO 2 → Relay IN = PURPLE colored wire (label: "Spray Pump Trigger")

LEGEND TABLE (draw in the bottom-left corner):
| Wire Color | ESP32 Pin | Target Pin | Motor Function |
| Blue | GPIO 12 | L298N IN1 | Left Forward PWM |
| Yellow | GPIO 13 | L298N IN2 | Left Reverse PWM |
| Green | GPIO 14 | L298N IN3 | Right Forward PWM |
| Orange | GPIO 15 | L298N IN4 | Right Reverse PWM |
| Purple | GPIO 2 | Relay IN | Spray Pump 200ms Pulse |

STYLE: Clean flat 2D diagram, white background, bold colored wire lines (each a different vivid color), large legible labels on every pin, no 3D rendering, professional electronics teaching poster quality.

<!-- PROMPT END -->

---

## Prompt 4 of 6: 4 Motors Parallel Wiring to L298N Screw Terminals

> **What this generates:** Clear diagram showing how 4 TT motors connect in parallel pairs (left bank & right bank) to the L298N's 2-screw terminal blocks, with a close-up of wire twisting.

<!-- PROMPT START -->

Generate a clear, educational electronics wiring diagram on a pure white background showing exactly how 4 yellow TT DC geared motors connect in parallel pairs to an L298N motor driver board's screw terminals.

CENTER: Draw the L298N motor driver board (red PCB, large black aluminum heatsink on top, blue capacitors). Clearly show THREE separate blue screw terminal blocks:
- LEFT SIDE blue block: exactly 2 screw terminals labeled "OUT1" (top screw) and "OUT2" (bottom screw)
- RIGHT SIDE blue block: exactly 2 screw terminals labeled "OUT3" (top screw) and "OUT4" (bottom screw)
- BOTTOM CENTER blue block: exactly 3 screw terminals labeled "+12V" (left), "GND" (center), "+5V" (right). Draw a large RED X over this bottom block with bold text: "⚠ NO MOTORS HERE — POWER INPUT ONLY!"

FOUR MOTORS (arranged at the four corners around the L298N):
- TOP-LEFT: Yellow TT gear motor labeled "Front-Left (FL)" — show a RED wire and a BLACK wire soldered to its two brass tabs
- BOTTOM-LEFT: Yellow TT gear motor labeled "Rear-Left (RL)" — show a RED wire and a BLACK wire
- TOP-RIGHT: Yellow TT gear motor labeled "Front-Right (FR)" — show a RED wire and a BLACK wire
- BOTTOM-RIGHT: Yellow TT gear motor labeled "Rear-Right (RR)" — show a RED wire and a BLACK wire

WIRING (show twisted wire pairs CLEARLY with visible twisting pattern):
LEFT BANK (parallel pair):
- FL RED wire + RL RED wire → show both wires converging and visibly twisting together into a single thick braided strand → this twisted pair enters the OUT1 screw terminal. Add label: "2 Red wires twisted together → OUT1"
- FL BLACK wire + RL BLACK wire → twisted together → enters OUT2 screw terminal. Add label: "2 Black wires twisted together → OUT2"

RIGHT BANK (parallel pair):
- FR RED wire + RR RED wire → twisted together → enters OUT3 screw terminal. Add label: "2 Red wires twisted together → OUT3"
- FR BLACK wire + RR BLACK wire → twisted together → enters OUT4 screw terminal. Add label: "2 Black wires twisted together → OUT4"

INSET DETAIL PANELS (draw two small zoomed-in panels in the bottom corners):
Panel A (bottom-left): Close-up of a soldering iron tip touching a brass motor tab with a red wire being soldered to it. Label: "Step 1: Solder 1 Red + 1 Black wire to each motor tab"
Panel B (bottom-right): Close-up of a precision flat-head screwdriver tightening a blue screw terminal clamp onto two twisted copper wire strands. Label: "Step 2: Twist pairs and screw into terminal"

STYLE: Clean technical diagram, white background, bold color-coded wires (bright vivid red and solid black), large readable sans-serif labels, top-down 2D flat view, educational infographic quality, no 3D effects.

<!-- PROMPT END -->

---

## Prompt 5 of 6: 12V Spray Pump + Relay + Flyback Diode Protection Circuit

> **What this generates:** Detailed diagram of the spray pump actuation circuit with the relay switching mechanism and critical 1N4007 flyback diode orientation.

<!-- PROMPT START -->

Generate a clear electronics wiring diagram on a pure white background showing the spray pump protection circuit for an agricultural robot rover. Arrange components left to right.

COMPONENTS:

1. FAR LEFT (signal source): Show a small black ESP32-CAM board with only GPIO 2 pin highlighted. A PURPLE wire exits GPIO 2 heading right toward the relay.

2. LEFT-CENTER (relay module): Draw a blue/black 5V optocoupled relay module. Show clearly TWO sides:
   - LOW-VOLTAGE SIDE (left edge): 3 header pins in a vertical column labeled top-to-bottom: "VCC" (with a red wire going up, labeled "+5.10V from Buck"), "GND" (with a black wire going down, labeled "Common Star Ground"), "IN" (with the purple wire coming from ESP32 GPIO 2)
   - HIGH-VOLTAGE SIDE (right edge): 3 large screw terminals in a vertical column labeled top-to-bottom: "NC" (empty, no wire, label: "Not Connected"), "COM" (center screw, label: "Common"), "NO" (bottom screw, label: "Normally Open")
   
3. Inside the relay module, draw a simplified internal switch diagram: a dashed box containing a hinged arm connecting COM to NO when the coil is energized. Add label: "When GPIO 2 = HIGH → coil pulls arm → COM touches NO → circuit closes → pump runs"

4. RIGHT-CENTER (power feed): A RED wire labeled "+12V from Battery Switch" enters the relay's "COM" terminal. Another RED wire exits the relay's "NO" terminal heading right toward the pump.

5. FAR RIGHT (pump + diode): Draw a black 12V mini diaphragm water pump with two barbed hose connectors visible. Two wires exit the pump:
   - RED wire (+) connects back to the relay "NO" terminal
   - BLACK wire (-) connects down to Common Star Ground
   
6. DIODE (critical protection): Draw a small black cylindrical component (the 1N4007 rectifier diode) soldered DIRECTLY across the pump's RED and BLACK wires, bridging them. The diode has a visible SILVER/WHITE stripe band on one end.
   - The SILVER BAND (cathode) MUST point toward the RED (+) wire
   - The plain BLACK end (anode) connects to the BLACK (-) wire
   - Add a LARGE bold annotation with an arrow: "⚠ 1N4007 FLYBACK DIODE — Silver cathode band MUST face the RED (+) wire! Protects relay from voltage spikes when pump turns off."

7. Add a SEQUENCE ANNOTATION across the bottom:
   "ESP32 GPIO 2 HIGH (200ms) → Relay coil energizes → COM-NO closes → 12V flows → Pump sprays → GPIO 2 LOW → Relay opens → Pump stops → 1N4007 absorbs back-EMF spike safely"

STYLE: Clean flat 2D schematic, white background, large bold labels, color-coded wires (red for +12V, black for GND, purple for signal), professional electronics educational quality, no 3D effects, clear annotations with arrows.

<!-- PROMPT END -->

---

## Prompt 6 of 6: Power Distribution: Battery → Switch → Buck → All Loads

> **What this generates:** Focused power-only diagram showing the 12V and 5.10V rails, the buck converter calibration, and the two-zone ground architecture.

<!-- PROMPT START -->

Generate a clear electronics power distribution wiring diagram on a pure white background for a 12V robot rover. This diagram shows ONLY the power wires (no motor signal wires, no logic jumpers). Focus entirely on how 12V battery power flows through the switch, splits into a 12V motor bus and a 5.10V logic bus, and how all grounds return through a two-zone common star ground.

COMPONENTS (arrange in a logical flow from left to right, top to bottom):

1. TOP-LEFT: Blue 12V 3S Li-ion battery pack with a RED wire from (+) terminal and a BLACK wire from (-) terminal. Label the red wire "+12V" and the black wire "0V GND".

2. TOP-CENTER: Black SPST rocker switch with two terminals. The RED battery wire enters Terminal 1. A switched RED wire exits Terminal 2. Label: "Main Power ON/OFF Switch".

3. CENTER: From Switch Terminal 2, the RED wire branches into THREE separate red lines using a solder splice or WAGO connector (show the branch point clearly with a bold dot):
   - Branch A goes DOWN-LEFT to LM2596 buck converter "IN+" terminal. Label: "+12V to Buck Input"
   - Branch B goes RIGHT to L298N motor driver "+12V" screw terminal. Label: "+12V Motor Power Rail"
   - Branch C goes DOWN-RIGHT to Relay "COM" screw terminal. Label: "+12V Pump Power Rail"

4. LEFT-CENTER: Blue LM2596 DC-DC step-down buck converter module. Show all 4 screw terminals clearly: "IN+" and "IN-" on the input side, "OUT+" and "OUT-" on the output side. Show the brass trimpot on top. Below the module, draw a red digital multimeter with its LCD showing "5.10" volts, with red probe touching OUT+ and black probe touching OUT-. Label: "Adjust trimpot until multimeter reads exactly 5.10V BEFORE connecting to ESP32!"

5. BOTTOM-LEFT: Black ESP32-CAM board showing "5V" and "GND" pins. A black cylindrical 1000uF/16V electrolytic capacitor bridges these two pins (long lead to 5V, short lead to GND). Label the capacitor: "1000µF Brownout Prevention Cap".

6. BOTTOM-RIGHT: Blue 5V relay module showing "VCC" and "GND" pins.

7. CENTER-RIGHT: Red L298N motor driver showing the bottom 3-pin terminal block: "+12V", "GND", "+5V". Show a small black jumper cap on the 5V-EN pins. Label: "Keep 5V-EN jumper cap ON".

POWER WIRE CONNECTIONS:

+12V HIGH-CURRENT BUS (all RED wires, thick bold lines):
- Battery (+) → Switch T1 → Switch T2 → branches to: LM2596 IN+, L298N +12V, Relay COM

+5.10V REGULATED LOGIC BUS (RED wires, slightly thinner, labeled "+5.10V"):
- LM2596 "OUT+" → branches to: ESP32-CAM "5V" pin, Relay "VCC" pin

GROUND / 0V RETURN (all BLACK wires):
ZONE 1 — HIGH-POWER GROUND (connect to LM2596 "IN-"):
- Battery (-) BLACK wire → LM2596 "IN-"
- L298N "GND" terminal → LM2596 "IN-"
- (Pump BLACK wire also connects here)
Label this zone: "ZONE 1: Noisy Motor Ground"

ZONE 2 — CLEAN LOGIC GROUND (connect to LM2596 "OUT-"):
- LM2596 "OUT-" → ESP32-CAM "GND"
- LM2596 "OUT-" → Relay "GND"
Label this zone: "ZONE 2: Clean Logic Ground"

Add a bold annotation on the LM2596 module: "IN- and OUT- are connected internally on the LM2596 PCB copper ground plane (0Ω). This naturally bridges Zone 1 and Zone 2 without extra wires!"

VOLTAGE LABELS: Add voltage labels on each wire segment showing: "+12V", "+5.10V", or "0V GND"

STYLE: Clean flat 2D schematic, white background, bold color-coded wires (thick red for +12V, medium red for +5.10V, thick black for GND), large readable labels with voltage values, professional power distribution diagram quality, no 3D effects.

<!-- PROMPT END -->

---

## Quick Reference: Which Prompt Generates What

| # | Prompt Name | What It Shows |
|:---:|:---|:---|
| **1** | Complete Master System | ALL components, ALL wires, entire rover in one diagram |
| **2** | Common Star Ground Bus | How to plug all 6 ground wires into a mini breadboard |
| **3** | ESP32 → L298N Logic Pins | 5 colored jumper wires: GPIO 12-15 → IN1-IN4, GPIO 2 → Relay |
| **4** | 4 Motors → L298N Terminals | Parallel pair twisting into OUT1-OUT4 with soldering close-up |
| **5** | Pump + Relay + Diode | Spray circuit with 1N4007 flyback diode orientation |
| **6** | Power Distribution | Battery → Switch → Buck → 12V bus + 5.10V bus + two-zone ground |
