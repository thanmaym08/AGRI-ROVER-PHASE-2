# Agri Rover Phase 2 — Mobile & Web App Developer API Specification

**Target Audience:** Mobile App Developers (Flutter / Android / React Native / iOS / Web)  
**System Target:** Agri Rover Cyber-Physical Agricultural UGV (ESP32-CAM / ESP32-S3)  
**Author:** Technical Architecture Team | BMSITM MCA (Project Work MMCA34 / VTU)  

---

## 1. Network Topology & Wi-Fi Connection

The Agri Rover microcontroller hosts a dedicated, local 2.4GHz Wi-Fi Access Point (SoftAP). The mobile device running the application must connect to this network:

| Parameter | Configuration Value | Notes |
| :--- | :--- | :--- |
| **Hotspot SSID** | `AgriRover-CAM-AP` | Local broadcast name |
| **Hotspot Password** | `agrirover123` | WPA2-PSK security |
| **Rover IP Address** | `192.168.4.1` | Static Gateway & Server IP |
| **Subnet Mask** | `255.255.255.0` | Class C Subnet |
| **Control Server Port** | `80` (HTTP) | Dedicated to UI & REST commands |
| **Video Stream Port** | `81` (HTTP) | Dedicated to MJPEG video feed |

> [!NOTE]
> On Android and iOS, disable "Mobile Data / Cellular Data" or set "Stay connected to Wi-Fi without internet" so the OS does not route HTTP requests through 4G/5G.

---

## 2. Real-Time Video Streaming API (Port 81)

The camera stream runs on a completely independent HTTP server on Port 81 to prevent video chunking from delaying driving commands.

- **Endpoint:** `GET http://192.168.4.1:81/stream`
- **Content-Type:** `multipart/x-mixed-replace; boundary=123456789000000000000987654321`
- **Format:** MJPEG (Motion JPEG)
- **Resolution:** HVGA ($480 \times 320\text{ px}$)
- **Frame Rate:** $22\text{–}25\text{ FPS}$ (28ms frame pacing)
- **Bandwidth Consumption:** $\sim 2.1\text{ Mbps}$

### Client Implementation Tips:
- **Flutter:** Use the `flutter_mjpeg` package or a custom `Image.network` stream listener.
- **Android (Native Kotlin/Java):** Use a custom `MjpegView` surface or an embedded `WebView` pointing directly to the URL.
- **React Native:** Use `react-native-mjpeg` or a `<WebView source={{ uri: 'http://192.168.4.1:81/stream' }} />`.

---

## 3. Skid-Steer Drivetrain Teleoperation API (Port 80)

Differential skid-steer locomotion maps two independent channels: `left` and `right`.

- **Endpoint:** `GET http://192.168.4.1/drive?left=<L>&right=<R>`
- **HTTP Method:** `GET`

### Query Parameters:

| Parameter | Type | Valid Range | Function |
| :--- | :---: | :---: | :--- |
| **`left`** | `integer` | `-255` to `+255` | Left track PWM speed. Negative = Reverse, Positive = Forward, 0 = Halt |
| **`right`** | `integer` | `-255` to `+255` | Right track PWM speed. Negative = Reverse, Positive = Forward, 0 = Halt |

### Locomotion Examples:
- **Drive Forward (Sprint 100%):** `GET http://192.168.4.1/drive?left=255&right=255`
- **Drive Forward (Cruise 65%):** `GET http://192.168.4.1/drive?left=165&right=165`
- **Zero-Radius Pivot Left:** `GET http://192.168.4.1/drive?left=-180&right=180`
- **Zero-Radius Pivot Right:** `GET http://192.168.4.1/drive?left=180&right=-180`
- **Immediate Stop:** `GET http://192.168.4.1/drive?left=0&right=0`

### Safety Watchdog & Heartbeat Rule:
The rover has an embedded hardware watchdog set to **1200ms**. If the app fails to transmit a packet within 1200ms (e.g., connection lost or phone locked), the rover automatically cuts motor power to 0%.  
👉 **Implementation Rule:** Stream `/drive?left=...&right=...` on a **75ms to 100ms interval timer** while the user touches or drags the virtual joystick.

---

## 4. In-Situ Soil Moisture Probing & Automated Sprinkler API (Port 80)

This subsystem performs on-demand subsurface soil moisture testing and localized closed-loop watering.

```
[ App Taps Check ] ──> [ Drive Lockout ] ──> [ Servo Lowers 50mm ] ──> [ Read Sensor ]
                                                                             │
[ Resume Drive ] <── [ Release Lockout ] <── [ Water 2.5s if Dry ] <── [ Servo Retracts ]
```

### 4.1 Trigger Probing Sequence
Initiates the automated physical descent of the probe, measurement, retraction, and conditional watering.

- **Endpoint:** `GET http://192.168.4.1/probe`
- **HTTP Method:** `GET`
- **Response Format:** `application/json`
- **Sample Response:**
  ```json
  {
    "status": "probing_started"
  }
  ```

#### Hardware Sequence Executed:
1. **Drive Lockout:** Rover locks wheel motors to 0% PWM. Teleoperation is temporarily disabled.
2. **Servo Stroke:** MG996R servo drives the probe 50mm down into the soil ($160^\circ$).
3. **Stabilization:** 600ms pause for capacitive charge equilibrium.
4. **Sampling:** Samples capacitive sensor, converts to moisture percentage ($0\%\sim 100\%$).
5. **Servo Retraction:** MG996R retracts probe back to safe transport height ($10^\circ$).
6. **Sprinkling Decision:** If `moisture < threshold`, closes relay to fire direct 12V pump for 2.5s directly on the probed spot.
7. **Unlock:** Releases drive lockout; full teleoperation driving resumes.

---

### 4.2 Poll Probing Status & Moisture Readings
Poll this endpoint while probing is active (e.g. every 500ms) to update the app's UI, progress bars, and status text.

- **Endpoint:** `GET http://192.168.4.1/probe_status`
- **HTTP Method:** `GET`
- **Response Format:** `application/json`
- **Sample JSON Response:**
  ```json
  {
    "state": 0,
    "dry": true,
    "raw": 1,
    "percent": 24,
    "threshold": 35,
    "status": "WATERING COMPLETE - Spot Hydrated",
    "idle": true
  }
  ```

#### JSON Response Schema:

| Field | Type | Description | App Display Recommendation |
| :--- | :---: | :--- | :--- |
| **`percent`** | `integer` | Calibrated subsoil moisture ($0\%\sim 100\%$). | Display in a large circular gauge or text label (e.g., `24%`). |
| **`threshold`** | `integer` | Active user-set trigger limit ($10\%\sim 80\%$). | Display alongside moisture (e.g., `Dry Limit: 35%`). |
| **`dry`** | `boolean` | `true` if soil fell below threshold and needed water. | Show red warning badge if `true`, green badge if `false`. |
| **`status`** | `string` | Live human-readable status message from firmware. | Bind directly to a status banner or toast message. |
| **`idle`** | `boolean` | `true` if sequence is finished; `false` if active. | While `false`, disable driving buttons to prevent collision. |
| **`state`** | `integer` | FSM State ID: `0`: IDLE, `1`: EXTENDING, `2`: STABILIZING, `3`: READING, `4`: RETRACTING, `5`: WATERING. | Optional fine-grained state indicator. |

---

### 4.3 Set Dry Moisture Threshold (Slider)
Adjusts the boundary below which the pump automatically sprinkles water.

- **Endpoint:** `GET http://192.168.4.1/probe_threshold?val=<value>`
- **HTTP Method:** `GET`
- **Query Parameter:** `val` (integer from `10` to `80`, default `35`)
- **Example:** `GET http://192.168.4.1/probe_threshold?val=40`
- **Sample Response:**
  ```json
  {
    "status": "ok",
    "threshold": 40
  }
  ```

---

## 5. Auxiliary Control APIs (Port 80)

### 5.1 Manual Spray Trigger
Fires the 12V pump for a fixed micro-burst duration.

- **Endpoint:** `GET http://192.168.4.1/spray?ms=<duration>`
- **Parameter:** `ms` (duration in milliseconds, e.g. `1000` for 1 second, `2500` for 2.5 seconds)
- **Manual Toggle:** `GET http://192.168.4.1/spray?state=on` or `state=off`

### 5.2 Flashlight / Headlight Dimming
Controls the high-power onboard floodlight LED.

- **Endpoint:** `GET http://192.168.4.1/flash?val=<brightness>`
- **Parameter:** `val` (integer from `0` to `255`. `0` = OFF, `255` = Maximum brightness)

---

## 6. Recommended App UI Wireframe

```
+───────────────────────────────────────────────────────────+
| [⚡ ONLINE]  AGRI ROVER COCKPIT             Ping: 12ms    |
+───────────────────────────────────────────────────────────+
|                                                           |
|                 LIVE CAMERA MJPEG STREAM                  |
|               http://192.168.4.1:81/stream                |
|                                                           |
|   HUD BADGE: [ 🌱 MOISTURE: 24% | DRY LIMIT: 35% ]         |
+───────────────────────────────────────────────────────────+
| LEFT CONTROLS          | CENTER STATUS      | RIGHT CONTROLS
|                        |                    |
| [ ▲ FORWARD ]          | Measured Moisture: | [ ◄ STEER L ]
|                        |      [ 24% ]       |
| [ ▼ REVERSE ]          |                    | [ ► STEER R ]
|                        | [💧 Dry Limit: 35%]|
| Speed: 35% | 65% | 100%| [━━━●━━━━━━━━━━━━] | [ 💦 Manual 1s Spray ]
|                        |                    |
|                        |  [ 🌱 CHECK SOIL ] | [ 🛑 EMERGENCY STOP ]
+───────────────────────────────────────────────────────────+
```

---

## 7. Sample Implementation Code for App Developers

### 7.1 Flutter (Dart)

```dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AgriRoverController {
  final String baseUrl = 'http://192.168.4.1';
  Timer? _statusTimer;

  // 1. Send Continuous Driving Commands (Call every 75ms while joystick is held)
  Future<void> sendDrive(int left, int right) async {
    final url = Uri.parse('$baseUrl/drive?left=$left&right=$right');
    try {
      await http.get(url);
    } catch (e) {
      print('Drive error: $e');
    }
  }

  // 2. Trigger Soil Moisture Probing
  Future<void> checkSoilMoisture({
    required Function(int percent, String status, bool isIdle) onProgress,
  }) async {
    try {
      // Trigger probe extension
      await http.get(Uri.parse('$baseUrl/probe'));

      // Poll status every 500ms
      _statusTimer?.cancel();
      _statusTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) async {
        final res = await http.get(Uri.parse('$baseUrl/probe_status'));
        final data = jsonDecode(res.body);

        final int percent = data['percent'];
        final String status = data['status'];
        final bool isIdle = data['idle'];

        onProgress(percent, status, isIdle);

        if (isIdle) {
          timer.cancel(); // Stop polling when finished
        }
      });
    } catch (e) {
      print('Probe error: $e');
    }
  }

  // 3. Update Moisture Threshold Slider
  Future<void> setThreshold(int val) async {
    try {
      await http.get(Uri.parse('$baseUrl/probe_threshold?val=$val'));
    } catch (e) {
      print('Threshold update error: $e');
    }
  }
}
```

---

### 7.2 Native Android (Kotlin + OkHttp)

```kotlin
import android.os.Handler
import android.os.Looper
import okhttp3.*
import org.json.JSONObject
import java.io.IOException

class AgriRoverService {
    private val client = OkHttpClient()
    private val baseUrl = "http://192.168.4.1"
    private val mainHandler = Handler(Looper.getMainLooper())

    // 1. Trigger Soil Probe
    fun triggerSoilProbe(onStatusUpdate: (percent: Int, status: String, isIdle: Boolean) -> Unit) {
        val request = Request.Builder().url("$baseUrl/probe").build()
        client.newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {
                pollStatus(onStatusUpdate)
            }
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
            }
        })
    }

    // 2. Poll Probe Status
    private fun pollStatus(callback: (Int, String, Boolean) -> Unit) {
        val runnable = object : Runnable {
            override fun run() {
                val req = Request.Builder().url("$baseUrl/probe_status").build()
                client.newCall(req).enqueue(object : Callback {
                    override fun onResponse(call: Call, response: Response) {
                        val body = response.body?.string() ?: return
                        val json = JSONObject(body)
                        val percent = json.getInt("percent")
                        val status = json.getString("status")
                        val isIdle = json.getBoolean("idle")

                        mainHandler.post {
                            callback(percent, status, isIdle)
                        }

                        if (!isIdle) {
                            mainHandler.postDelayed(this@Runnable, 500)
                        }
                    }
                    override fun onFailure(call: Call, e: IOException) {}
                })
            }
        }
        mainHandler.post(runnable)
    }

    // 3. Set Dry Threshold Slider
    fun setThreshold(value: Int) {
        val req = Request.Builder().url("$baseUrl/probe_threshold?val=$value").build()
        client.newCall(req).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {}
            override fun onFailure(call: Call, e: IOException) {}
        })
    }
}
```

---

## 8. Reference Implementation in Codebase

For a complete working HTML/JavaScript reference that already interacts with all these endpoints, see:  
👉 [`Prototype/firmware/AgriRover_ESP32CAM/test_cockpit.html`](https://github.com/thanmaym08/AGRI-ROVER-PHASE-2/blob/main/Prototype/firmware/AgriRover_ESP32CAM/test_cockpit.html) (Lines 950–990).
