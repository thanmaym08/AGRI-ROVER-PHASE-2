# Agri Rover Teleoperation Android App

An Android mobile teleoperation and telematics application for the **Agri Rover Phase 2 Agricultural Robot (UGV)**.

Built with a clean **Land Rover-inspired automotive card interface**, high-contrast typography, zero-latency skid-steer differential drive kinematics, live HVGA MJPEG camera streaming, and automated subsurface soil moisture testing with physical drive interlock.

---

## 🌟 Key Features

### 1. Dedicated Landing Page & 3 Control Architectures
Choose among three tailored control systems right from the launcher landing page or switch seamlessly on the fly from the cockpit dock:
- **Dual Thumbs (Split Axis):** Independent vertical throttle on the left thumb, horizontal steering on the right thumb. Direct, responsive teleoperation.
- **Single Stick (360° Omnidirectional):** Clean 60/40 cockpit layout with a 360° analog joystick, speed regime selector (`SLOW 35%`, `MED 65%`, `FAST 100%`), and chemical spray burst.
- **D-Pad Tactile (Step Drive):** Dedicated large press-and-hold buttons (`▲ FORWARD`, `▼ REVERSE` on the left; `◄ LEFT`, `RIGHT ►` on the right) designed for precision maneuvers along crop rows.

### 2. Physical Drivetrain Lockout Interlock
- When triggering the in-situ soil moisture probe (`/probe`), the mobile app and firmware enforce a strict physical drive lockout (`🔒 DRIVE LOCKED | SOIL PROBE ACTIVE`).
- All driving inputs (joystick, sliders, D-Pad) are blocked while the physical probe is lowered 50mm into the subsoil or while automatic watering is in progress.

### 3. In-Situ Soil Moisture & Sprinkler Control
- Live capacitive soil moisture percentage readout with active dry threshold limits.
- Interactive **Soil Dry Threshold (Auto-Sprinkle Limit)** slider (10% to 80%, default 35%) with immediate sync to the ESP32 microcontroller (`/probe_threshold?val=X`).
- Live firmware status notifications (`LOWERING PROBE 50mm...`, `SAMPLING SUBSOIL...`, `WATERING COMPLETE - Spot Hydrated`, `OPTIMAL`).

### 4. Precision Chemical Spray Micro-Burst
- Relay-actuated pump micro-bursts with dedicated duration selectors (`0.5s`, `1.0s`, `2.0s`) and custom duration configuration in settings.

### 5. High-Paced Real-Time Video Streaming
- Decodes multipart MJPEG video on Port 81 (`http://192.168.4.1:81/stream`) with rotation controls (`0°`, `90°`, `180°`, `270°`), automatic reconnection watchdog, and live FPS telemetry.

---

## 📡 Wi-Fi SoftAP Connection

1. Connect your Android phone to the rover's Wi-Fi hotspot:
   - **SSID:** `AgriRover-CAM-AP`
   - **Password:** `agrirover123`
   - **Rover Static IP:** `192.168.4.1`
2. Ensure mobile cellular data is temporarily toggled off or accept the prompt *"Stay connected to Wi-Fi without internet"*.
3. Launch the app to begin teleoperation.

---

## 🛠️ Build & Installation

### Requirements
- Android Studio Iguana / Jellyfish or newer
- Android SDK 34 (Compile & Target SDK), Min SDK 24 (Android 7.0+)
- JDK 17

### Command-Line Build
```bash
# Clone the repository
git clone https://github.com/mohitsarode/Rover-App.git
cd Rover-App

# Assemble debug APK
./gradlew assembleDebug

# Install on connected Android device via ADB
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## 📂 Project Architecture

```
Rover-App/
├── app/
│   ├── src/main/
│   │   ├── java/com/agrirover/teleop/
│   │   │   ├── AxisSliderView.java      # 1D pill-shaped vertical/horizontal slider
│   │   │   ├── JoystickView.java        # 360° omnidirectional analog joystick
│   │   │   ├── KinematicsHelper.java    # Skid-steer kinematics & differential solver
│   │   │   ├── LandingActivity.java     # Mode selection & diagnostics landing screen
│   │   │   ├── MainActivity.java        # Cockpit teleoperation Activity
│   │   │   ├── MjpegStreamer.java       # Native multipart MJPEG video stream decoder
│   │   │   ├── RoverApiClient.java      # Asynchronous OkHttp REST client
│   │   │   └── RoverConfig.java         # SharedPreferences & kinematics calibration
│   │   ├── res/
│   │   │   ├── drawable/                # Land Rover automotive card & button drawables
│   │   │   ├── layout/                  # activity_landing.xml, activity_main.xml, dialog_settings.xml
│   │   │   └── values/                  # colors.xml (Light theme), strings.xml, themes.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── gradle.properties
├── settings.gradle
└── README.md
```
