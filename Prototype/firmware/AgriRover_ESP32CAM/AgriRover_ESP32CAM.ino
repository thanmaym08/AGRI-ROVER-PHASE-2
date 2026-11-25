/*
 * Agri Rover Phase 2 — ESP32-CAM Prototype Firmware
 * Hardware Target: AI-Thinker ESP32-CAM or ESP32-S3 WROOM CAM
 * 
 * Features:
 *  1. Dual Wi-Fi (SoftAP "AgriRover-CAM-AP" @ 192.168.4.1 + Station Mode fallback)
 *  2. Real-time MJPEG Video Streaming (/stream on Port 81)
 *  3. Embedded 56% Center Video Responsive Mobile Phone Web App with Multi-Modal Cockpit
 *  4. 4-Channel LEDC Hardware PWM Differential Skid-Steer Motor Control (L298N)
 *     (Fully compatible with both ESP32 Arduino Core v2.x and v3.x)
 *  5. Timed Non-Blocking Chemical Spray Relay Micro-Burst (/spray?ms=1000)
 *  6. Flash LED Dimming / Toggle (/flash?val=128)
 *  7. Communication Failsafe Watchdog (auto-halts motors after 1200ms signal loss)
 *  8. Steering Angle (K_steer) & Straight-Line Motor Drift Trim Calibration
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_http_server.h"

// Compatibility detection for ESP32 Arduino Core v2 vs v3
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
#define CORE_V3 1
#else
#define CORE_V3 0
#endif

// ======================== CAMERA MODEL SELECTION ========================
// Select your camera module (uncomment ONE):
#define CAMERA_MODEL_AI_THINKER  // Classic AI-Thinker ESP32-CAM (OV2640)
//#define CAMERA_MODEL_ESP32S3_CAM  // UG LAND INDIA / Freenove ESP32-S3 WROOM CAM (OV2640 / OV3660)

#if defined(CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

// ==================== ACTUATOR & MOTOR PIN CONFIGURATION ====================
// 1. Drivetrain Motors (L298N Dual H-Bridge)
#define PIN_MOTOR_L_A 14  // IN1 -- Left Motors Forward
#define PIN_MOTOR_L_B 15  // IN2 -- Left Motors Backward
#define PIN_MOTOR_R_A 13  // IN3 -- Right Motors Forward
#define PIN_MOTOR_R_B 12  // IN4 -- Right Motors Backward (MUST BE LOW AT BOOT)

// 2. DIRECT 12V WATER PUMP SPRINKLER (5V Optocoupled Relay Trigger)
// WIRING DIRECT 12V POWER:
//  - Battery (+) 12.6V -> Main Switch -> Relay COM Terminal (Direct un-stepped raw 12V bus)
//  - Relay NO Terminal -> 12V Diaphragm Pump (+) Red lead (Receives full 12.6V when triggered)
//  - Pump (-) Black lead -> Common Star Ground Bus
//  - 1N4007 Diode soldered directly across pump terminals (Cathode silver band to +, Anode to -)
#define PIN_RELAY 2       // Relay IN -- Direct 12V Pump Trigger (Active-HIGH/LOW configurable)

// 3. IN-SITU SOIL MOISTURE PROBE MECHANISM (MG996R Servo + Capacitive Sensor)
#define PIN_SERVO 4       // MG996R 50Hz PWM (Header Pin 4; moves probe 10° stowed to 160° ground)
#define PIN_MOISTURE_IN 3 // Soil Moisture Sensor Digital DO / Analog input (Header Pin 3 / U0RXD)
#define PIN_FLASH 4       // High-power SMD LED

#elif defined(CAMERA_MODEL_ESP32S3_CAM)
#define PWDN_GPIO_NUM -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 15
#define SIOD_GPIO_NUM 4
#define SIOC_GPIO_NUM 5
#define Y2_GPIO_NUM 11
#define Y3_GPIO_NUM 9
#define Y4_GPIO_NUM 8
#define Y5_GPIO_NUM 10
#define Y6_GPIO_NUM 12
#define Y7_GPIO_NUM 18
#define Y8_GPIO_NUM 17
#define Y9_GPIO_NUM 16
#define VSYNC_GPIO_NUM 6
#define HREF_GPIO_NUM 7
#define PCLK_GPIO_NUM 13

// Actuator & Motor Pins for ESP32-S3 Dev Module
#define PIN_MOTOR_L_A 1   // IN1
#define PIN_MOTOR_L_B 2   // IN2
#define PIN_MOTOR_R_A 41  // IN3
#define PIN_MOTOR_R_B 42  // IN4
#define PIN_RELAY 40      // Direct 12V Spray Pump / Solenoid
#define PIN_SERVO 38      // MG996R Servo
#define PIN_MOISTURE_IN 39// Soil Moisture Sensor
#define PIN_FLASH 48      // Board Indicator LED
#endif

// LEDC PWM Configuration for Motors
#define PWM_FREQ 5000  // 5 kHz
#define PWM_RES 8      // 8-bit resolution (0-255)
#define LEDC_CH_L_A 0
#define LEDC_CH_L_B 1
#define LEDC_CH_R_A 2
#define LEDC_CH_R_B 3
#define LEDC_CH_FLASH 4

// Servo 50Hz PWM Configuration (Timer 2 / Channel 5)
#define SERVO_PWM_FREQ 50   // 50 Hz Servo Frequency (20ms period)
#define SERVO_PWM_RES 14    // 14-bit resolution (0-16383)
#define LEDC_CH_SERVO 5

// Helper to support both Core 2.x and Core 3.x
void pwm_write(int pin, int channel, int val) {
#if CORE_V3
  ledcWrite(pin, val);
#else
  ledcWrite(channel, val);
#endif
}

// Wi-Fi Credentials
const char *AP_SSID = "AgriRover-CAM-AP";
const char *AP_PASS = "agrirover123";

// Optional Station Mode Router Credentials (leave empty or set to your Wi-Fi)
const char *STA_SSID = "";
const char *STA_PASS = "";

// State Variables
unsigned long last_command_time = 0;
const unsigned long WATCHDOG_TIMEOUT_MS = 1200;  // Increased to 1200ms to absorb Wi-Fi frame latency while heartbeat streams
unsigned long spray_start_time = 0;
unsigned long spray_duration_ms = 1000;  // Calibrated 1-second (1000ms) spray burst
bool spray_active = false;
bool drive_lockout = false;  // Rover strictly immobilized during soil probe & sprinkling

// ======================== RELAY POLARITY CONFIGURATION ========================
// Dynamic Active-HIGH / Active-LOW selection (toggleable via UI /spray?polarity=high or low)
// Default to Active-HIGH (0V/LOW = OFF at boot, 3.3V/HIGH = ON) to prevent pump running on boot.
bool relay_active_low = false;

inline int get_relay_on() {
  return relay_active_low ? LOW : HIGH;
}

inline int get_relay_off() {
  return relay_active_low ? HIGH : LOW;
}

httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

// ======================== MOTOR MOTION CONTROLLER ========================
void set_motors(int left_speed, int right_speed) {
  if (drive_lockout) {
    // SAFETY INTERLOCK: Rover strictly immobilized during soil probe & sprinkling!
    pwm_write(PIN_MOTOR_L_A, LEDC_CH_L_A, 0);
    pwm_write(PIN_MOTOR_L_B, LEDC_CH_L_B, 0);
    pwm_write(PIN_MOTOR_R_A, LEDC_CH_R_A, 0);
    pwm_write(PIN_MOTOR_R_B, LEDC_CH_R_B, 0);
    return;
  }
  left_speed = constrain(left_speed, -255, 255);
  right_speed = constrain(right_speed, -255, 255);

  // Left Motor (Skid-Steer Track A)
  if (left_speed > 0) {
    pwm_write(PIN_MOTOR_L_A, LEDC_CH_L_A, left_speed);
    pwm_write(PIN_MOTOR_L_B, LEDC_CH_L_B, 0);
  } else if (left_speed < 0) {
    pwm_write(PIN_MOTOR_L_A, LEDC_CH_L_A, 0);
    pwm_write(PIN_MOTOR_L_B, LEDC_CH_L_B, -left_speed);
  } else {
    pwm_write(PIN_MOTOR_L_A, LEDC_CH_L_A, 0);
    pwm_write(PIN_MOTOR_L_B, LEDC_CH_L_B, 0);
  }

  // Right Motor (Skid-Steer Track B)
  if (right_speed > 0) {
    pwm_write(PIN_MOTOR_R_A, LEDC_CH_R_A, right_speed);
    pwm_write(PIN_MOTOR_R_B, LEDC_CH_R_B, 0);
  } else if (right_speed < 0) {
    pwm_write(PIN_MOTOR_R_A, LEDC_CH_R_A, 0);
    pwm_write(PIN_MOTOR_R_B, LEDC_CH_R_B, -right_speed);
  } else {
    pwm_write(PIN_MOTOR_R_A, LEDC_CH_R_A, 0);
    pwm_write(PIN_MOTOR_R_B, LEDC_CH_R_B, 0);
  }
}

void stop_motors() {
  set_motors(0, 0);
}

// ======================== SPRAY ACTUATION LOGIC ========================
void trigger_spray(unsigned long duration_ms) {
  digitalWrite(PIN_RELAY, get_relay_on());
  spray_start_time = millis();
  spray_duration_ms = duration_ms;
  spray_active = true;
  Serial.printf("[DIRECT 12V PUMP] Spray burst triggered for %lu ms (PIN %d -> %s)\n",
                duration_ms, PIN_RELAY, (get_relay_on() == LOW ? "LOW" : "HIGH"));
}

void process_spray_watchdog() {
  if (spray_active && (millis() - spray_start_time >= spray_duration_ms)) {
    digitalWrite(PIN_RELAY, get_relay_off());
    spray_active = false;
    Serial.printf("[DIRECT 12V PUMP] Spray burst ended. (PIN %d -> %s)\n",
                  PIN_RELAY, (get_relay_off() == LOW ? "LOW" : "HIGH"));
  }
}

// ======================== MG996R SERVO PWM CONTROL ========================
void set_servo_angle(int angle) {
  angle = constrain(angle, 0, 180);
  // 50Hz = 20ms period. 14-bit resolution = 16383 full scale (819.15 ticks/ms)
  // 0.6ms (0°) -> ~492 ticks; 2.4ms (180°) -> ~1966 ticks
  int duty = map(angle, 0, 180, 492, 1966);
  pwm_write(PIN_SERVO, LEDC_CH_SERVO, duty);
}

// ======================== SOIL PROBE & LOCALIZED SPRINKLER FSM ========================
enum ProbeState {
  PROBE_IDLE,
  PROBE_EXTENDING,
  PROBE_STABILIZING,
  PROBE_READING,
  PROBE_RETRACTING,
  PROBE_WATERING
};

ProbeState current_probe_state = PROBE_IDLE;
unsigned long probe_state_timer = 0;
bool last_probe_dry = false;
int last_moisture_raw = 0;
int last_moisture_percent = 50;   // Dynamic 0-100% moisture reading
int moisture_threshold = 35;      // Water trigger threshold (User adjustable via web slider)
String probe_telemetry_status = "IDLE - Ready";

void trigger_soil_probe() {
  if (current_probe_state == PROBE_IDLE) {
    stop_motors();
    drive_lockout = true;          // 1. Lock drive motors immediately
    set_servo_angle(160);          // 2. Drive probe 50mm downward into ground
    probe_state_timer = millis();
    current_probe_state = PROBE_EXTENDING;
    probe_telemetry_status = "PROBING: Lowering into ground...";
    Serial.println("[PROBE] Sequence started. Drive lockout ACTIVE. Extending probe...");
  }
}

void process_soil_probe_fsm() {
  unsigned long now = millis();

  switch (current_probe_state) {
    case PROBE_IDLE:
      drive_lockout = false;
      break;

    case PROBE_EXTENDING:
      // Allow 900ms for MG996R servo to drive the probe carriage down
      if (now - probe_state_timer >= 900) {
        probe_state_timer = now;
        current_probe_state = PROBE_STABILIZING;
        probe_telemetry_status = "PROBING: In subsoil. Stabilizing...";
        Serial.println("[PROBE] Probe fully extended. Stabilizing capacitive charge...");
      }
      break;

    case PROBE_STABILIZING:
      // Allow 600ms for capacitive charge equilibration
      if (now - probe_state_timer >= 600) {
        current_probe_state = PROBE_READING;
      }
      break;

    case PROBE_READING: {
      // 3. Read soil moisture sensor on PIN_MOISTURE_IN (GPIO 3 / RX)
      int sensor_val = digitalRead(PIN_MOISTURE_IN);
      last_moisture_raw = sensor_val;

      // Map sensor signal to intuitive moisture percentage:
      // Standard LM393 comparator DO pin: HIGH = Dry soil, LOW = Moist soil.
      if (sensor_val == HIGH) {
        last_moisture_percent = 20; // Dry indicator
      } else {
        last_moisture_percent = 75; // Moist/wet indicator
      }

      // Check if soil moisture falls below user-configured slider threshold:
      last_probe_dry = (last_moisture_percent < moisture_threshold);

      // 4. Retract probe back to transport position immediately
      set_servo_angle(10); // Retract to stowed position
      probe_state_timer = now;
      current_probe_state = PROBE_RETRACTING;
      if (last_probe_dry) {
        probe_telemetry_status = "DRY (" + String(last_moisture_percent) + "% < " + String(moisture_threshold) + "%) - Retracting to water!";
      } else {
        probe_telemetry_status = "MOIST (" + String(last_moisture_percent) + "% >= " + String(moisture_threshold) + "%) - Retracting (Optimal)";
      }
      Serial.printf("[PROBE] Moisture: %d%% vs Threshold: %d%% -> %s. Retracting probe...\n",
                    last_moisture_percent, moisture_threshold, (last_probe_dry ? "DRY (WATER)" : "OPTIMAL (PASS)"));
      break;
    }

    case PROBE_RETRACTING:
      // Allow 900ms for servo to return to stowed position
      if (now - probe_state_timer >= 900) {
        if (last_probe_dry) {
          // 5. DIRECT 12V WATER SPRINKLING: Firing 12V pump for 2500ms directly on probed spot!
          Serial.printf("[SPRINKLE] Firing DIRECT 12V pump for 2500ms! (Moisture: %d%% < Thresh: %d%%)\n",
                        last_moisture_percent, moisture_threshold);
          trigger_spray(2500); // 2.5s localized micro-burst
          probe_state_timer = now;
          current_probe_state = PROBE_WATERING;
          probe_telemetry_status = "DIRECT 12V SPRINKLING (" + String(last_moisture_percent) + "% < " + String(moisture_threshold) + "%)...";
        } else {
          current_probe_state = PROBE_IDLE;
          drive_lockout = false; // Release drive lockout
          probe_telemetry_status = "OPTIMAL MOISTURE (" + String(last_moisture_percent) + "%) - No water needed";
          Serial.printf("[PROBE] Soil moisture optimal (%d%% >= %d%%). Drive lockout RELEASED.\n",
                        last_moisture_percent, moisture_threshold);
        }
      }
      break;

    case PROBE_WATERING:
      if (!spray_active) {
        current_probe_state = PROBE_IDLE;
        drive_lockout = false;   // 6. Release drive lockout; rover ready to move
        probe_telemetry_status = "WATERING COMPLETE - Spot Hydrated";
        Serial.println("[SPRINKLE] Localized watering complete. Drive lockout RELEASED.");
      }
      break;
  }
}

// ======================== EMBEDDED MOBILE WEB APP (PRO MULTI-MODE COCKPIT) ========================
static const char PROGMEM INDEX_HTML[] = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>Agri Rover Pro Cockpit</title>
<style>
  * { box-sizing: border-box; touch-action: none; -webkit-user-select: none; user-select: none; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  html, body { background: #0a0e14; color: #fff; width: 100vw; height: 100vh; height: 100dvh; overflow: hidden; display: flex; flex-direction: column; }

  /* TOP HUD BAR (OUTSIDE SCREEN) */
  .hud-top { flex: 0 0 34px; height: 34px; background: #0e141c; border-bottom: 1px solid #1c2736; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; z-index: 30; font-size: 11px; }
  .hud-left { display: flex; align-items: center; gap: 6px; font-weight: 800; font-size: 11px; }
  .badge { background: #27ae60; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 8px; }
  .hud-center { display: flex; align-items: center; gap: 6px; font-family: monospace; font-size: 10px; color: #2ecc71; background: rgba(18,24,32,0.8); padding: 3px 8px; border-radius: 5px; border: 1px solid #223042; }
  .hud-right { display: flex; align-items: center; gap: 6px; }
  #hud-ping { font-family: monospace; font-size: 10px; color: #2ecc71; }
  .hud-btn { background: #16202c; border: 1px solid #2c3e50; color: #fff; border-radius: 5px; padding: 3px 7px; cursor: pointer; font-size: 11px; }

  /* MAIN COCKPIT WORKSPACE */
  #main-cockpit { flex: 1; display: flex; overflow: hidden; position: relative; width: 100%; height: calc(100% - 66px); }
  .control-view { width: 100%; height: 100%; display: none; }
  .control-view.active { display: flex; }

  /* ================= DUAL THUMBS: 56% CENTER VIDEO + FLANKED CONTROLS ================= */
  .view-flanked { flex-direction: row; align-items: stretch; }
  
  /* LEFT & RIGHT WINGS (22% EACH) */
  .wing { flex: 0 0 22%; width: 22%; background: #101620; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 6px 4px; gap: 4px; z-index: 10; border-right: 1px solid #1a2533; }
  .wing-right { border-right: none; border-left: 1px solid #1a2533; }

  /* Compact Wing Cards */
  .wing-card { background: #16202c; border: 1px solid #223042; border-radius: 7px; padding: 4px; width: 100%; display: flex; flex-direction: column; gap: 3px; }
  .card-title { font-size: 8px; font-weight: 800; color: #8b9bb4; display: flex; justify-content: space-between; align-items: center; }
  .tag-accent { color: #2ecc71; font-family: monospace; font-weight: 900; }
  
  .pill-group { display: flex; gap: 2px; width: 100%; }
  .btn-pill { flex: 1; background: #0f151d; border: 1px solid #223042; color: #8b9bb4; padding: 3px 0; border-radius: 3px; font-size: 8px; font-weight: 800; cursor: pointer; text-align: center; }
  .btn-pill.active { background: #2ecc71; color: #000; border-color: #2ecc71; font-weight: 900; }
  .duration-pills .btn-pill.active { background: #3498db; color: #fff; border-color: #3498db; }

  /* Main Action Buttons in Wings */
  .btn-spray-main { background: linear-gradient(135deg, #2980b9, #3498db); border: 1px solid #5dade2; color: #fff; border-radius: 5px; padding: 6px 2px; font-size: 9px; font-weight: 800; cursor: pointer; text-align: center; width: 100%; box-shadow: 0 2px 6px rgba(0,0,0,0.4); }
  .btn-spray-main:active { background: #27ae60; }
  
  .btn-wing-action { width: 100%; border-radius: 6px; padding: 6px 2px; font-size: 9px; font-weight: 800; cursor: pointer; text-align: center; border: 1px solid #223042; background: #16202c; color: #fff; }
  .btn-flash { border-color: #f39c12; color: #f1c40f; }
  .btn-flash:active { background: #f39c12; color: #000; }
  .btn-stop { background: rgba(231, 76, 60, 0.25); border-color: #e74c3c; color: #ff7675; }
  .btn-stop:active { background: #e74c3c; color: #fff; }

  /* Stick Sections */
  .stick-section { display: flex; flex-direction: column; align-items: center; gap: 3px; }
  .stick-title { font-size: 8px; font-weight: 800; color: #8b9bb4; letter-spacing: 0.5px; }

  /* Dual Stick Oval Bases */
  .joy-base { background: radial-gradient(circle, #1a2533, #0b0f15); border: 2px solid #223042; position: relative; display: flex; justify-content: center; align-items: center; box-shadow: inset 0 2px 8px rgba(0,0,0,0.8); }
  .joy-v-base { width: 84px; height: 126px; border-radius: 42px; }
  .joy-h-base { width: 126px; height: 84px; border-radius: 42px; }
  
  .joy-guide-v { width: 5px; height: 74px; background: rgba(46,204,113,0.18); border-radius: 3px; border: 1px solid rgba(46,204,113,0.3); pointer-events: none; }
  .joy-guide-h { width: 74px; height: 5px; background: rgba(52,152,219,0.18); border-radius: 3px; border: 1px solid rgba(52,152,219,0.3); pointer-events: none; }

  .joy-thumb { width: 44px; height: 44px; border-radius: 50%; position: absolute; transform: translate(0, 0); box-shadow: 0 3px 10px rgba(0,0,0,0.7); pointer-events: none; }
  .joy-thumb-throttle { background: radial-gradient(circle, #2ecc71, #27ae60); box-shadow: 0 0 10px rgba(46,204,113,0.6); }
  .joy-thumb-steer { background: radial-gradient(circle, #3498db, #2980b9); box-shadow: 0 0 10px rgba(52,152,219,0.6); }

  .stick-hint { position: absolute; font-size: 8px; font-weight: 800; pointer-events: none; }
  .hint-top { top: 5px; color: #2ecc71; }
  .hint-bottom { bottom: 5px; color: #e74c3c; }
  .hint-left { left: 6px; color: #3498db; }
  .hint-right { right: 6px; color: #3498db; }

  /* ================= CENTER VIDEO STAGE (56% OF WIDTH) ================= */
  .center-video-stage { flex: 0 0 56%; width: 56%; height: 100%; background: #000; position: relative; display: flex; justify-content: center; align-items: center; overflow: hidden; border-left: 1px solid #2ecc71; border-right: 1px solid #2ecc71; }
  .video-frame { width: 100%; height: 100%; position: relative; display: flex; justify-content: center; align-items: center; }
  #stream { width: 100%; height: 100%; object-fit: contain; display: block; }
  .btn-cam-rotate { position: absolute; top: 6px; right: 6px; background: rgba(14,20,28,0.85); border: 1px solid #2ecc71; color: #2ecc71; padding: 4px 8px; border-radius: 5px; font-size: 10px; font-weight: 800; cursor: pointer; z-index: 28; backdrop-filter: blur(4px); box-shadow: 0 2px 6px rgba(0,0,0,0.5); }
  .btn-cam-rotate:active { background: #2ecc71; color: #000; }
  .rot-tag { font-family: monospace; font-weight: 900; }
  .stream-feed { max-width: 100%; max-height: 100%; object-fit: contain; display: block; transition: transform 0.25s ease-in-out; }
  .reticle { position: absolute; border: 1px dashed rgba(46, 204, 113, 0.45); width: 100px; height: 100px; border-radius: 8px; pointer-events: none; }
  #spray-alert { position: absolute; top: 10px; background: linear-gradient(90deg, #2980b9, #27ae60); color: #fff; padding: 4px 14px; border-radius: 12px; font-size: 10px; font-weight: 800; display: none; z-index: 25; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }

  /* ================= SINGLE STICK LAYOUT (STACKED) ================= */
  .view-stacked { flex-direction: column; }
  .stacked-video { flex: 0 0 54%; height: 54%; position: relative; background: #000; display: flex; justify-content: center; align-items: center; overflow: hidden; border-bottom: 2px solid #2ecc71; }
  .stacked-controls { flex: 1; background: #121820; display: flex; padding: 6px 10px; gap: 8px; }
  .joy-single-wrap { flex: 0 0 45%; display: flex; justify-content: center; align-items: center; }
  .joy-single-base { width: 120px; height: 120px; border-radius: 50%; }
  .tactical-single { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 4px; }
  .aux-row-single { display: flex; gap: 4px; }

  /* ================= D-PAD LAYOUT ================= */
  .dpad-group { display: flex; flex-direction: column; gap: 8px; width: 100%; padding: 4px; }
  .btn-dpad { background: #16202c; border: 2px solid #2a3c50; color: #fff; padding: 14px 4px; border-radius: 8px; font-size: 10px; font-weight: 800; cursor: pointer; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.4); }
  .btn-dpad:active, .btn-dpad.active { background: #2ecc71; color: #000; border-color: #2ecc71; }

  /* BOTTOM CONTROL BAR (OUTSIDE SCREEN) */
  .bar-bottom { flex: 0 0 32px; height: 32px; background: #0c1219; border-top: 1px solid #1c2736; display: flex; align-items: center; justify-content: space-between; padding: 2px 10px; gap: 8px; z-index: 30; }
  .mode-selector { display: flex; gap: 4px; flex: 1; max-width: 320px; }
  .btn-mode { flex: 1; height: 26px; background: #151d27; border: 1px solid #233348; color: #8b9bb4; border-radius: 4px; font-size: 9px; font-weight: 800; cursor: pointer; }
  .btn-mode.active { background: #2ecc71; color: #000; border-color: #2ecc71; font-weight: 900; box-shadow: 0 0 8px rgba(46,204,113,0.4); }
  
  .slider-wrapper { display: flex; align-items: center; gap: 5px; flex: 1; max-width: 220px; }
  .slider-wrapper input { flex: 1; height: 4px; accent-color: #2ecc71; }
  .slider-icon { font-size: 11px; }

  /* CALIBRATION MODAL */
  #modal { position: fixed; inset: 0; background: rgba(0,0,0,0.82); backdrop-filter: blur(4px); display: none; justify-content: center; align-items: center; z-index: 100; }
  #modal.open { display: flex; }
  .mcard { background: #121820; border: 1px solid #223042; border-radius: 12px; width: 92%; max-width: 380px; padding: 14px; font-size: 11px; display: flex; flex-direction: column; gap: 10px; }
  .mcard h3 { color: #2ecc71; font-size: 13px; display: flex; justify-content: space-between; }
  .mcard label { display: block; font-weight: 700; margin-bottom: 2px; }
  .mcard input[type="range"] { width: 100%; accent-color: #2ecc71; }
  .mcard-row { display: flex; justify-content: space-between; }
  .btn-modal-opt { flex: 1; background: #182230; border: 1px solid #223042; color: #8b9bb4; padding: 6px 2px; border-radius: 6px; font-size: 10px; font-weight: 700; cursor: pointer; }
  .btn-modal-opt.active { background: #2ecc71; color: #000; border-color: #2ecc71; font-weight: 800; }

  /* Responsive Scaling for Narrow Phones */
  @media (max-width: 480px) and (orientation: portrait) {
    .wing { flex: 0 0 24%; width: 24%; padding: 4px 2px; }
    .center-video-stage { flex: 0 0 52%; width: 52%; }
    .joy-v-base { width: 72px; height: 110px; }
    .joy-h-base { width: 110px; height: 72px; }
    .joy-thumb { width: 38px; height: 38px; }
    .btn-spray-main { font-size: 8px; padding: 5px 1px; }
  }
</style>
</head>
<body>

<!-- TOP HUD BAR (OUTSIDE SCREEN) -->
<header class="hud-top">
  <div class="hud-left">
    <span>🌿</span>
    <span>AGRI ROVER</span>
    <span class="badge" id="hud-status">ONLINE</span>
  </div>
  <div class="hud-center">
    <span id="motion-dir">■ STOPPED</span>
    <span>|</span>
    <span id="motor-val">L:0 R:0</span>
  </div>
  <div class="hud-right">
    <span id="hud-ping">-- ms</span>
    <button class="hud-btn" onclick="openModal()" title="Settings & Calib">⚙️</button>
  </div>
</header>

<!-- MAIN COCKPIT WORKSPACE -->
<main id="main-cockpit">

  <!-- ================= MODE 1: DUAL THUMBS (56% CENTER VIDEO + FLANKED WINGS) ================= -->
  <div id="view-dual" class="control-view active view-flanked">
    
    <!-- LEFT WING: LEFT THUMB THROTTLE + SPEED -->
    <aside class="wing wing-left">
      <div class="wing-card">
        <div class="card-title">
          <span>SPEED</span>
          <span id="speed-tag-left" class="tag-accent">65%</span>
        </div>
        <div class="pill-group">
          <button class="btn-pill" onclick="setSpeed(35)">35%</button>
          <button class="btn-pill active" onclick="setSpeed(65)">65%</button>
          <button class="btn-pill" onclick="setSpeed(100)">100%</button>
        </div>
      </div>

      <div class="stick-section">
        <div class="stick-title">THROTTLE (L)</div>
        <div id="joy-dual-left" class="joy-base joy-v-base">
          <div class="joy-guide-v"></div>
          <div id="joy-dual-left-thumb" class="joy-thumb joy-thumb-throttle"></div>
          <span class="stick-hint hint-top">▲ FWD</span>
          <span class="stick-hint hint-bottom">▼ REV</span>
        </div>
      </div>

      <button class="btn-wing-action btn-flash" id="btn-flash-left" onclick="toggleFlash()">💡 FLASH</button>
    </aside>

    <!-- CENTER VIDEO STAGE: 50% TO 60% (56% EXACT) -->
    <section class="center-video-stage">
      <div class="video-frame">
        <button class="btn-cam-rotate" onclick="cycleCameraRotation()" title="Rotate Video 90°">🔄 <span class="rot-tag">0°</span></button>
        <img id="stream" class="stream-feed" alt="Live Camera Stream">
        <div class="reticle"></div>
        <div id="spray-alert">💦 SPRAY ACTIVE (1.0s)</div>
      </div>
    </section>

    <!-- RIGHT WING: RIGHT THUMB STEERING + SPRAY & STOP -->
    <aside class="wing wing-right">
      <div class="wing-card">
        <button class="btn-spray-main" id="btn-spray-right" onclick="triggerSpray()">💦 SPRAY (1.0s)</button>
        <button class="btn-spray-main" id="btn-probe-right" style="background:linear-gradient(135deg, #1b4332, #2d6a4f); border-color:#2ecc71; margin-top:4px;" onclick="triggerProbeSequence()">🌱 PROBE & WATER</button>
        
        <!-- Interactive Soil Moisture Threshold Slider -->
        <div style="background:#0e141c; border:1px solid #223042; border-radius:5px; padding:3px 5px; margin-top:3px;">
          <div style="display:flex; justify-content:space-between; font-size:8px; font-weight:800; color:#2ecc71;">
            <span>💧 DRY LIMIT</span>
            <span id="thresh-val-display">35%</span>
          </div>
          <input type="range" id="slider-moisture-thresh" min="10" max="80" value="35" step="5"
                 style="width:100%; height:12px; accent-color:#2ecc71; cursor:pointer; margin:1px 0;"
                 oninput="onMoistureThreshChange(this.value)">
          <div style="font-size:7px; color:#7f8c8d; text-align:center;">Sprinkle if soil &lt; limit</div>
        </div>

        <div class="pill-group duration-pills">
          <button class="btn-pill btn-dur" onclick="setSprayDuration(500)">0.5s</button>
          <button class="btn-pill btn-dur active" onclick="setSprayDuration(1000)">1.0s</button>
          <button class="btn-pill btn-dur" onclick="setSprayDuration(2000)">2.0s</button>
        </div>
      </div>

      <div class="stick-section">
        <div class="stick-title">STEERING (R)</div>
        <div id="joy-dual-right" class="joy-base joy-h-base">
          <div class="joy-guide-h"></div>
          <div id="joy-dual-right-thumb" class="joy-thumb joy-thumb-steer"></div>
          <span class="stick-hint hint-left">◄ L</span>
          <span class="stick-hint hint-right">R ►</span>
        </div>
      </div>

      <button class="btn-wing-action btn-stop" onclick="emergencyStop()">🛑 STOP</button>
    </aside>
  </div>

  <!-- ================= MODE 2: SINGLE STICK (DEFAULT 360°) ================= -->
  <div id="view-single" class="control-view view-stacked">
    <div class="stacked-video">
      <button class="btn-cam-rotate" onclick="cycleCameraRotation()" title="Rotate Video 90°">🔄 <span class="rot-tag">0°</span></button>
      <img class="stream-single stream-feed" alt="Camera Stream" style="width:100%; height:100%; object-fit:contain;">
      <div class="reticle"></div>
    </div>
    <div class="stacked-controls">
      <div class="joy-single-wrap">
        <div id="joy-single-base" class="joy-base joy-single-base">
          <div id="joy-single-thumb" class="joy-thumb joy-thumb-throttle"></div>
          <span style="position:absolute; bottom:6px; font-size:8px; font-weight:800; color:#8b9bb4;">360° DRIVE</span>
        </div>
      </div>
      <div class="tactical-single">
        <div class="wing-card">
          <div class="card-title">
            <span>SPEED REGIME</span>
            <span id="speed-tag-single" class="tag-accent">65% (MED)</span>
          </div>
          <div class="pill-group">
            <button class="btn-pill" onclick="setSpeed(35)">SLOW</button>
            <button class="btn-pill active" onclick="setSpeed(65)">MED</button>
            <button class="btn-pill" onclick="setSpeed(100)">FAST</button>
          </div>
        </div>
        <div class="wing-card">
          <button class="btn-spray-main" id="btn-spray-single" onclick="triggerSpray()">💦 SPRAY BURST (1.0s)</button>
          <div class="pill-group duration-pills">
            <button class="btn-pill btn-dur" onclick="setSprayDuration(500)">0.5s</button>
            <button class="btn-pill btn-dur active" onclick="setSprayDuration(1000)">1.0s</button>
            <button class="btn-pill btn-dur" onclick="setSprayDuration(2000)">2.0s</button>
          </div>
        </div>
        <div class="aux-row-single">
          <button class="btn-wing-action btn-flash" onclick="toggleFlash()">💡 FLASH</button>
          <button class="btn-wing-action" onclick="openModal()">📐 CALIB</button>
          <button class="btn-wing-action btn-stop" onclick="emergencyStop()">🛑 STOP</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= MODE 3: D-PAD BUTTONS (FLANKED) ================= -->
  <div id="view-dpad" class="control-view view-flanked">
    <aside class="wing wing-left">
      <div class="stick-title">THROTTLE</div>
      <div class="dpad-group">
        <button class="btn-dpad" id="btn-dpad-fwd">▲ FWD</button>
        <button class="btn-dpad" id="btn-dpad-rev">▼ REV</button>
      </div>
      <button class="btn-wing-action btn-flash" onclick="toggleFlash()">💡 FLASH</button>
    </aside>

    <section class="center-video-stage">
      <div class="video-frame">
        <button class="btn-cam-rotate" onclick="cycleCameraRotation()" title="Rotate Video 90°">🔄 <span class="rot-tag">0°</span></button>
        <img class="stream-dpad stream-feed" alt="Camera Stream" style="width:100%; height:100%; object-fit:contain;">
        <div class="reticle"></div>
      </div>
    </section>

    <aside class="wing wing-right">
      <div class="stick-title">STEERING</div>
      <div class="dpad-group">
        <button class="btn-dpad" id="btn-dpad-left">◄ LEFT</button>
        <button class="btn-dpad" id="btn-dpad-right">RIGHT ►</button>
      </div>
      <button class="btn-wing-action btn-stop" onclick="emergencyStop()">🛑 STOP</button>
    </aside>
  </div>

</main>

<!-- BOTTOM BAR: MODE SELECTOR & SPEED SLIDER (OUTSIDE SCREEN) -->
<footer class="bar-bottom">
  <div class="mode-selector">
    <button class="btn-mode active" id="btn-mode-dual" onclick="switchControlMode('dual')">🎮 DUAL THUMBS</button>
    <button class="btn-mode" id="btn-mode-single" onclick="switchControlMode('single')">🕹️ SINGLE STICK</button>
    <button class="btn-mode" id="btn-mode-dpad" onclick="switchControlMode('dpad')">🎛️ D-PAD</button>
  </div>
  <div class="slider-wrapper">
    <span class="slider-icon">🐢</span>
    <input type="range" id="speed-slider" min="25" max="100" value="65" oninput="setSpeed(this.value)">
    <span class="slider-icon">🐇</span>
  </div>
</footer>

<!-- CALIBRATION & DIAGNOSTICS MODAL -->
<div id="modal">
  <div class="mcard">
    <h3>
      <span>🛠️ Rover Controls & Calibration</span>
      <span style="cursor:pointer;" onclick="closeModal()">&times;</span>
    </h3>

    <div>
      <label>Preferred Control Layout:</label>
      <div style="display:flex; gap:4px; margin-top:3px;">
        <button class="btn-modal-opt active" id="m-opt-dual" onclick="switchControlMode('dual')">🎮 Dual Thumbs</button>
        <button class="btn-modal-opt" id="m-opt-single" onclick="switchControlMode('single')">🕹️ Single Stick</button>
        <button class="btn-modal-opt" id="m-opt-dpad" onclick="switchControlMode('dpad')">🎛️ D-Pad</button>
      </div>
    </div>

    <div>
      <div class="mcard-row">
        <label>Turn Sensitivity (K_steer):</label>
        <span id="lbl-sens" style="color:#2ecc71;">0.75x</span>
      </div>
      <input type="range" id="cfg-sens" min="0.30" max="1.20" step="0.05" value="0.75" oninput="updateCalibLabels()">
    </div>

    <div>
      <div class="mcard-row">
        <label>Motor Drift Trim:</label>
        <span id="lbl-trim" style="color:#2ecc71;">0%</span>
      </div>
      <input type="range" id="cfg-trim" min="-25" max="25" step="1" value="0" oninput="updateCalibLabels()">
    </div>

    <div style="display:flex; flex-direction:column; gap:5px;">
      <label style="cursor:pointer;"><input type="checkbox" id="cfg-inv-throt"> Invert Throttle (Forward ↔ Reverse)</label>
      <label style="cursor:pointer;"><input type="checkbox" id="cfg-inv-steer"> Invert Steering (Left ↔ Right)</label>
    </div>

    <div style="border-top:1px solid #223042; padding-top:8px; display:flex; flex-direction:column; gap:6px;">
      <label style="color:#8b9bb4; font-weight:800;">Pump & Relay Hardware Diagnostics:</label>
      <label style="cursor:pointer; display:flex; align-items:center; gap:6px; font-size:10px;">
        <input type="checkbox" id="cfg-relay-low" onchange="toggleRelayPolarity(this.checked)"> Invert Relay Logic (Active-LOW: 0V=ON, 3.3V=OFF)
      </label>
      <div style="display:flex; gap:4px;">
        <button style="flex:1; background:#2980b9; border:1px solid #3498db; color:#fff; padding:6px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="triggerSpray()">💦 Test 1.0s Spray</button>
        <button id="btn-pump-test" style="flex:1; background:#1f2d3d; border:1px solid #34495e; color:#5dade2; padding:6px; border-radius:6px; font-weight:800; cursor:pointer;" onclick="togglePumpManual()">⚡ Manual ON/OFF</button>
      </div>
      <div id="relay-diag-status" style="font-family:monospace; font-size:9px; color:#2ecc71; text-align:center;">Relay Mode: Active-HIGH (0V=OFF) | GPIO 2</div>
    </div>

    <div style="border-top:1px solid #223042; padding-top:8px; display:flex; flex-direction:column; gap:6px;">
      <div class="mcard-row">
        <label style="color:#8b9bb4; font-weight:800;">📷 Camera Video Orientation:</label>
        <span id="lbl-cam-rot" style="color:#2ecc71; font-weight:800; font-family:monospace;">0° (Normal)</span>
      </div>
      <div style="display:flex; gap:3px;">
        <button class="btn-modal-opt btn-rot-opt active" id="btn-rot-0" onclick="setCameraRotation(0)">0° Normal</button>
        <button class="btn-modal-opt btn-rot-opt" id="btn-rot-90" onclick="setCameraRotation(90)">90° CW</button>
        <button class="btn-modal-opt btn-rot-opt" id="btn-rot-180" onclick="setCameraRotation(180)">180° Invert</button>
        <button class="btn-modal-opt btn-rot-opt" id="btn-rot-270" onclick="setCameraRotation(270)">270° CCW</button>
      </div>
      <label style="cursor:pointer; display:flex; align-items:center; gap:6px; font-size:10px;">
        <input type="checkbox" id="cfg-cam-mirror" onchange="toggleCameraMirror(this.checked)"> ⇋ Mirror Flip (Horizontal Invert)
      </label>
    </div>

    <div style="border-top:1px solid #223042; padding-top:8px; display:flex; flex-direction:column; gap:6px;">
      <label style="color:#8b9bb4; font-weight:800;">Motor Bench Diagnostics:</label>
      <div style="display:flex; gap:4px;">
        <button style="flex:1; background:#182838; border:1px solid #2980b9; color:#5dade2; padding:7px 2px; border-radius:6px; font-weight:800; cursor:pointer; font-size:10px;" onclick="benchTestMotors('left')">◀ Test Left (OUT1/2)</button>
        <button style="flex:1; background:#182838; border:1px solid #2980b9; color:#5dade2; padding:7px 2px; border-radius:6px; font-weight:800; cursor:pointer; font-size:10px;" onclick="benchTestMotors('right')">Test Right (OUT3/4) ▶</button>
      </div>
      <button style="background:#16a085; border:none; color:#fff; padding:7px; border-radius:6px; font-weight:800; cursor:pointer; font-size:10px;" onclick="benchTestMotors('both')">⚡ Test All 4 Motors (1.5s Forward)</button>
    </div>

    <button style="background:#2ecc71; border:none; padding:9px; border-radius:6px; font-weight:800; cursor:pointer; color:#000; margin-top:4px;" onclick="saveCalib()">Save & Apply</button>
  </div>
</div>

<script>
  let speedPercent = 65;
  let flashVal = 0;
  let turnSens = 0.75;
  let steeringTrim = 0;
  let invertSteer = false;
  let invertThrot = false;
  let sprayDuration = 1000;
  let currentMode = 'dual';

  let targetLeft = 0;
  let targetRight = 0;
  let lastSend = 0;
  let driveHeartbeat = null;
  let manualPumpActive = false;
  let isDriveInFlight = false;
  let relayIsLow = false;
  let camRotation = 0; // 0, 90, 180, 270
  let camMirror = false;

  // Dual Thumb State
  let dualLeftTouchId = null;
  let dualRightTouchId = null;
  let dualLeftCenter = { x: 0, y: 0 };
  let dualRightCenter = { x: 0, y: 0 };
  let dualThrottle = 0;
  let dualSteer = 0;
  let maxTravelV = 36;
  let maxTravelH = 36;

  // Single Stick State
  let isDraggingSingle = false;
  let singleCenter = { x: 0, y: 0 };
  const singleMaxRadius = 45;

  // D-Pad State
  let dpadThrottle = 0;
  let dpadSteer = 0;

  // Elements
  const streamImg = document.getElementById('stream');
  const sprayAlert = document.getElementById('spray-alert');
  const motionDir = document.getElementById('motion-dir');
  const motorVal = document.getElementById('motor-val');

  const joyDualLeft = document.getElementById('joy-dual-left');
  const joyDualLeftThumb = document.getElementById('joy-dual-left-thumb');
  const joyDualRight = document.getElementById('joy-dual-right');
  const joyDualRightThumb = document.getElementById('joy-dual-right-thumb');

  const joySingleBase = document.getElementById('joy-single-base');
  const joySingleThumb = document.getElementById('joy-single-thumb');

  window.addEventListener('DOMContentLoaded', () => {
    connectStream();

    // Restore saved settings
    try {
      let saved = JSON.parse(localStorage.getItem('rover_calib'));
      if (saved) {
        turnSens = saved.turnSens || 0.75;
        steeringTrim = saved.steeringTrim || 0;
        invertSteer = saved.invertSteer || false;
        invertThrot = saved.invertThrot || false;
        relayIsLow = saved.relayIsLow || false;
        let rBox = document.getElementById('cfg-relay-low');
        if (rBox) rBox.checked = relayIsLow;
        if (relayIsLow) {
          fetch('/spray?polarity=low').catch(() => {});
          updateRelayDiagLabel(true);
        }
      }
      let savedMode = localStorage.getItem('agrirover_mode');
      if (savedMode) switchControlMode(savedMode);

      let savedRot = localStorage.getItem('rover_cam_rot');
      if (savedRot !== null) camRotation = parseInt(savedRot, 10);
      let savedMirror = localStorage.getItem('rover_cam_mirror');
      if (savedMirror === '1') camMirror = true;
      applyCameraTransform();
      updateRotationUI();
    } catch(e) {}
  });

  function setCameraRotation(deg) {
    camRotation = parseInt(deg, 10) % 360;
    applyCameraTransform();
    localStorage.setItem('rover_cam_rot', camRotation);
    updateRotationUI();
  }

  function cycleCameraRotation() {
    let next = (camRotation + 90) % 360;
    setCameraRotation(next);
  }

  function toggleCameraMirror(checked) {
    if (typeof checked !== 'undefined') {
      camMirror = checked;
    } else {
      camMirror = !camMirror;
    }
    applyCameraTransform();
    localStorage.setItem('rover_cam_mirror', camMirror ? '1' : '0');
    updateRotationUI();
  }

  function applyCameraTransform() {
    let transformStr = '';
    if (camRotation === 90 || camRotation === 270) {
      transformStr = `rotate(${camRotation}deg) scale(0.72)`;
    } else {
      transformStr = `rotate(${camRotation}deg) scale(1.0)`;
    }
    if (camMirror) {
      transformStr += ' scaleX(-1)';
    }

    document.querySelectorAll('.stream-feed').forEach(img => {
      img.style.transform = transformStr;
      img.style.transformOrigin = 'center center';
    });
  }

  function updateRotationUI() {
    document.querySelectorAll('.rot-tag').forEach(tag => {
      tag.textContent = `${camRotation}°`;
    });

    let lbl = document.getElementById('lbl-cam-rot');
    if (lbl) {
      let desc = (camRotation === 0) ? '0° (Normal)' : (camRotation === 90) ? '90° (Clockwise)' : (camRotation === 180) ? '180° (Inverted)' : '270° (Counter-CW)';
      if (camMirror) desc += ' [Mirrored]';
      lbl.textContent = desc;
    }

    document.querySelectorAll('.btn-rot-opt').forEach(b => b.classList.remove('active'));
    let activeBtn = document.getElementById('btn-rot-' + camRotation);
    if (activeBtn) activeBtn.classList.add('active');

    let mBox = document.getElementById('cfg-cam-mirror');
    if (mBox) mBox.checked = camMirror;
  }

  function connectStream() {
    let host = window.location.hostname || '192.168.4.1';
    let streamUrl = `http://${host}:81/stream`;
    document.querySelectorAll('.stream-feed').forEach(img => {
      img.src = streamUrl;
      img.onerror = () => {
        // Auto-reconnect stream if momentarily dropped
        setTimeout(() => {
          img.src = `http://${host}:81/stream?t=` + Date.now();
        }, 1200);
      };
    });
  }

  function toggleRelayPolarity(isLow) {
    relayIsLow = isLow;
    updateRelayDiagLabel(isLow);
    fetch('/spray?polarity=' + (isLow ? 'low' : 'high')).catch(() => {});
    saveCalib();
  }

  function updateRelayDiagLabel(isLow) {
    let el = document.getElementById('relay-diag-status');
    if (el) {
      el.textContent = isLow 
        ? 'Relay Mode: Active-LOW (0V=ON, 3.3V=OFF) | GPIO 2' 
        : 'Relay Mode: Active-HIGH (3.3V=ON, 0V=OFF) | GPIO 2';
    }
  }

  // Switch Control Layout Mode
  function switchControlMode(mode) {
    if (['dual', 'single', 'dpad'].indexOf(mode) === -1) mode = 'dual';
    currentMode = mode;
    emergencyStop();

    document.querySelectorAll('.btn-mode').forEach(b => b.classList.remove('active'));
    let btn = document.getElementById('btn-mode-' + mode);
    if (btn) btn.classList.add('active');

    document.querySelectorAll('.control-view').forEach(v => v.classList.remove('active'));
    let v = document.getElementById('view-' + mode);
    if (v) v.classList.add('active');

    document.querySelectorAll('.btn-modal-opt').forEach(b => b.classList.remove('active'));
    let mb = document.getElementById('m-opt-' + mode);
    if (mb) mb.classList.add('active');

    localStorage.setItem('agrirover_mode', mode);
  }

  // Speed Regime
  function setSpeed(val) {
    speedPercent = Math.max(25, Math.min(100, parseInt(val, 10)));
    let slider = document.getElementById('speed-slider');
    if (slider) slider.value = speedPercent;
    let tag = (speedPercent === 35) ? 'SLOW' : (speedPercent === 65) ? 'MED' : (speedPercent === 100) ? 'FAST' : 'CUSTOM';
    
    let tl = document.getElementById('speed-tag-left');
    let ts = document.getElementById('speed-tag-single');
    if (tl) tl.textContent = `${speedPercent}%`;
    if (ts) ts.textContent = `${speedPercent}% (${tag})`;

    document.querySelectorAll('.btn-pill').forEach(b => {
      let t = b.textContent.trim();
      let matches = (t === 'SLOW' && speedPercent === 35) || (t === 'MED' && speedPercent === 65) || (t === 'FAST' && speedPercent === 100) ||
                    (t === '35%' && speedPercent === 35) || (t === '65%' && speedPercent === 65) || (t === '100%' && speedPercent === 100);
      if (matches) b.classList.add('active');
      else if (['35%','65%','100%','SLOW','MED','FAST'].indexOf(t) !== -1) b.classList.remove('active');
    });
  }

  // Spray Controls
  function setSprayDuration(ms) {
    sprayDuration = parseInt(ms, 10);
    let tag = (sprayDuration / 1000).toFixed(1) + 's';
    document.querySelectorAll('.btn-dur').forEach(b => {
      if (b.textContent.trim() === tag) b.classList.add('active');
      else b.classList.remove('active');
    });
    let btnRight = document.getElementById('btn-spray-right');
    let btnSingle = document.getElementById('btn-spray-single');
    if (btnRight) btnRight.textContent = `💦 SPRAY (${tag})`;
    if (btnSingle) btnSingle.textContent = `💦 SPRAY BURST (${tag})`;
  }

  function onMoistureThreshChange(val) {
    document.getElementById('thresh-val-display').textContent = val + '%';
    fetch('/probe_threshold?val=' + val)
      .then(r => r.json())
      .then(d => {
        console.log('[THRESH] Set to', val + '%');
      })
      .catch(e => console.error(e));
  }

  function triggerProbeSequence() {
    const btn = document.getElementById('btn-probe-right');
    if (btn) btn.textContent = "⏳ PROBING...";
    sprayAlert.textContent = "🌱 PROBE INITIATED - ROVER IMMOBILIZED";
    sprayAlert.style.display = 'block';

    fetch('/probe')
      .then(r => r.json())
      .then(d => {
        pollProbeStatus();
      })
      .catch(e => {
        console.error(e);
        if (btn) btn.textContent = "🌱 PROBE & WATER";
      });
  }

  function pollProbeStatus() {
    const pollTimer = setInterval(() => {
      fetch('/probe_status')
        .then(r => r.json())
        .then(d => {
          sprayAlert.textContent = d.status;
          sprayAlert.style.display = 'block';
          if (d.idle) {
            clearInterval(pollTimer);
            const btn = document.getElementById('btn-probe-right');
            if (btn) btn.textContent = "🌱 PROBE & WATER";
            setTimeout(() => { sprayAlert.style.display = 'none'; }, 3000);
          }
        })
        .catch(e => clearInterval(pollTimer));
    }, 500);
  }

  function triggerSpray() {
    let tag = (sprayDuration / 1000).toFixed(1) + 's';
    sprayAlert.textContent = `💦 SPRAY ACTIVE (${tag})`;
    sprayAlert.style.display = 'block';
    fetch(`/spray?ms=${sprayDuration}`).catch(() => {});
    setTimeout(() => { sprayAlert.style.display = 'none'; }, sprayDuration);
  }

  function togglePumpManual() {
    manualPumpActive = !manualPumpActive;
    let btn = document.getElementById('btn-pump-test');
    if (manualPumpActive) {
      if (btn) {
        btn.textContent = '🛑 STOP PUMP TEST (RUNNING)';
        btn.style.background = '#e74c3c';
        btn.style.color = '#fff';
      }
      sprayAlert.textContent = '⚡ MANUAL PUMP: FORCED ON';
      sprayAlert.style.display = 'block';
      fetch('/spray?state=on').catch(() => {});
    } else {
      if (btn) {
        btn.textContent = '⚡ Manual Pump Test (Toggle ON/OFF)';
        btn.style.background = '#1f2d3d';
        btn.style.color = '#5dade2';
      }
      sprayAlert.style.display = 'none';
      fetch('/spray?state=off').catch(() => {});
    }
  }

  function toggleFlash() {
    flashVal = flashVal === 0 ? 180 : 0;
    document.querySelectorAll('.btn-flash').forEach(b => {
      b.style.background = (flashVal > 0) ? '#f39c12' : '#16202c';
      b.style.color = (flashVal > 0) ? '#000' : '#f1c40f';
    });
    fetch('/flash?val=' + flashVal).catch(() => {});
  }

  function benchTestMotors(side) {
    let l = (side === 'left' || side === 'both') ? 220 : 0;
    let r = (side === 'right' || side === 'both') ? 220 : 0;
    targetLeft = l;
    targetRight = r;
    updateMotionHud(l, r, 0.8, 0);
    sendDrivePacket();
    setTimeout(() => {
      emergencyStop();
    }, 1500);
  }

  // Kinematic Mixing & HUD
  function computeMotorMix(throttle, steer) {
    if (invertThrot) throttle = -throttle;
    if (invertSteer) steer = -steer;

    if (Math.hypot(throttle, steer) < 0.06) {
      throttle = 0;
      steer = 0;
    }

    let scaledSteer = steer * turnSens;
    let left = throttle + scaledSteer;
    let right = throttle - scaledSteer;

    if (steeringTrim !== 0 && Math.abs(throttle) > 0.05) {
      let f = steeringTrim / 100;
      if (f > 0) right *= (1 - f);
      else left *= (1 + f);
    }

    let maxPWM = Math.round((speedPercent / 100) * 255);
    let leftPWM = Math.round(Math.max(-255, Math.min(255, left * maxPWM)));
    let rightPWM = Math.round(Math.max(-255, Math.min(255, right * maxPWM)));

    targetLeft = leftPWM;
    targetRight = rightPWM;

    updateMotionHud(leftPWM, rightPWM, throttle, steer);

    let now = Date.now();
    if (now - lastSend > 60) {
      sendDrivePacket();
    }
  }

  function updateMotionHud(left, right, throttle, steer) {
    motorVal.textContent = `L:${left} R:${right}`;
    if (left === 0 && right === 0) {
      motionDir.textContent = '■ STOPPED';
      return;
    }
    if (throttle > 0.15 && Math.abs(steer) <= 0.25) motionDir.textContent = `▲ FWD ${speedPercent}%`;
    else if (throttle < -0.15 && Math.abs(steer) <= 0.25) motionDir.textContent = `▼ REV ${speedPercent}%`;
    else if (steer > 0.25 && Math.abs(throttle) <= 0.25) motionDir.textContent = '► PIVOT RIGHT';
    else if (steer < -0.25 && Math.abs(throttle) <= 0.25) motionDir.textContent = '◄ PIVOT LEFT';
    else if (throttle > 0.15 && steer > 0.25) motionDir.textContent = '⮡ CURVE RIGHT';
    else if (throttle > 0.15 && steer < -0.25) motionDir.textContent = '⮢ CURVE LEFT';
    else if (throttle < -0.15 && steer > 0.25) motionDir.textContent = '⮣ REV RIGHT';
    else if (throttle < -0.15 && steer < -0.25) motionDir.textContent = '⮠ REV LEFT';
    else motionDir.textContent = `● ACTIVE (${speedPercent}%)`;
  }

  // Network Heartbeat Loop
  function sendDrivePacket() {
    if (isDriveInFlight) return;
    let now = Date.now();
    if (now - lastSend < 40) return;
    lastSend = now;
    isDriveInFlight = true;

    let controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    let timeoutId = controller ? setTimeout(() => controller.abort(), 200) : null;

    let t0 = performance.now();
    let opts = controller ? { signal: controller.signal } : {};
    fetch(`/drive?left=${targetLeft}&right=${targetRight}`, opts)
      .then(r => r.json())
      .then(() => {
        if (timeoutId) clearTimeout(timeoutId);
        let p = Math.round(performance.now() - t0);
        let el = document.getElementById('hud-ping');
        let st = document.getElementById('hud-status');
        if (el) el.textContent = `${p} ms`;
        if (st) { st.textContent = 'ONLINE'; st.style.background = '#27ae60'; }
      })
      .catch(() => {
        let st = document.getElementById('hud-status');
        if (st) { st.textContent = 'LAG'; st.style.background = '#e67e22'; }
      })
      .finally(() => {
        if (timeoutId) clearTimeout(timeoutId);
        isDriveInFlight = false;
      });
  }

  function startHeartbeat() {
    if (!driveHeartbeat) {
      driveHeartbeat = setInterval(sendDrivePacket, 75);
    }
  }

  function stopHeartbeat() {
    if (driveHeartbeat) {
      clearInterval(driveHeartbeat);
      driveHeartbeat = null;
    }
  }

  function emergencyStop() {
    targetLeft = 0;
    targetRight = 0;
    dualThrottle = 0;
    dualSteer = 0;
    dpadThrottle = 0;
    dpadSteer = 0;
    dualLeftTouchId = null;
    dualRightTouchId = null;
    isDraggingSingle = false;

    if (joyDualLeftThumb) joyDualLeftThumb.style.transform = 'translate(0px, 0px)';
    if (joyDualRightThumb) joyDualRightThumb.style.transform = 'translate(0px, 0px)';
    if (joySingleThumb) joySingleThumb.style.transform = 'translate(0px, 0px)';
    document.querySelectorAll('.btn-dpad').forEach(b => b.classList.remove('active'));

    stopHeartbeat();
    fetch('/drive?left=0&right=0').catch(() => {});
    updateMotionHud(0, 0, 0, 0);
  }

  // ======================== MULTI-TOUCH DUAL STICKS ========================
  joyDualLeft.addEventListener('touchstart', e => {
    e.preventDefault();
    for (let i = 0; i < e.changedTouches.length; i++) {
      let t = e.changedTouches[i];
      if (dualLeftTouchId === null) {
        dualLeftTouchId = t.identifier;
        let rect = joyDualLeft.getBoundingClientRect();
        dualLeftCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        handleDualLeftMove(t);
        startHeartbeat();
        break;
      }
    }
  }, { passive: false });

  joyDualRight.addEventListener('touchstart', e => {
    e.preventDefault();
    for (let i = 0; i < e.changedTouches.length; i++) {
      let t = e.changedTouches[i];
      if (dualRightTouchId === null) {
        dualRightTouchId = t.identifier;
        let rect = joyDualRight.getBoundingClientRect();
        dualRightCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        handleDualRightMove(t);
        startHeartbeat();
        break;
      }
    }
  }, { passive: false });

  function handleDualLeftMove(t) {
    let dy = t.clientY - dualLeftCenter.y;
    dy = Math.max(-maxTravelV, Math.min(maxTravelV, dy));
    joyDualLeftThumb.style.transform = `translate(0px, ${dy}px)`;
    dualThrottle = -dy / maxTravelV;
    computeMotorMix(dualThrottle, dualSteer);
  }

  function handleDualRightMove(t) {
    let dx = t.clientX - dualRightCenter.x;
    dx = Math.max(-maxTravelH, Math.min(maxTravelH, dx));
    joyDualRightThumb.style.transform = `translate(${dx}px, 0px)`;
    dualSteer = dx / maxTravelH;
    computeMotorMix(dualThrottle, dualSteer);
  }

  // ======================== SINGLE STICK 360° ========================
  if (joySingleBase) {
    joySingleBase.addEventListener('touchstart', e => {
      e.preventDefault();
      isDraggingSingle = true;
      let rect = joySingleBase.getBoundingClientRect();
      singleCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
      handleSingleMove(e.touches[0]);
      startHeartbeat();
    }, { passive: false });
  }

  function handleSingleMove(pt) {
    let dx = pt.clientX - singleCenter.x;
    let dy = pt.clientY - singleCenter.y;
    let dist = Math.hypot(dx, dy);
    if (dist > singleMaxRadius) {
      dx = (dx / dist) * singleMaxRadius;
      dy = (dy / dist) * singleMaxRadius;
    }
    if (joySingleThumb) joySingleThumb.style.transform = `translate(${dx}px, ${dy}px)`;
    let throttle = -dy / singleMaxRadius;
    let steer = dx / singleMaxRadius;
    computeMotorMix(throttle, steer);
  }

  // ======================== GLOBAL TOUCH MOVE & END ========================
  window.addEventListener('touchmove', e => {
    if (currentMode === 'dual') {
      for (let i = 0; i < e.changedTouches.length; i++) {
        let t = e.changedTouches[i];
        if (t.identifier === dualLeftTouchId) {
          e.preventDefault();
          handleDualLeftMove(t);
        } else if (t.identifier === dualRightTouchId) {
          e.preventDefault();
          handleDualRightMove(t);
        }
      }
    } else if (currentMode === 'single' && isDraggingSingle) {
      e.preventDefault();
      handleSingleMove(e.touches[0]);
    }
  }, { passive: false });

  function handleTouchRelease(e) {
    if (currentMode === 'dual') {
      for (let i = 0; i < e.changedTouches.length; i++) {
        let t = e.changedTouches[i];
        if (t.identifier === dualLeftTouchId) {
          dualLeftTouchId = null;
          dualThrottle = 0;
          joyDualLeftThumb.style.transform = 'translate(0px, 0px)';
          computeMotorMix(dualThrottle, dualSteer);
        } else if (t.identifier === dualRightTouchId) {
          dualRightTouchId = null;
          dualSteer = 0;
          joyDualRightThumb.style.transform = 'translate(0px, 0px)';
          computeMotorMix(dualThrottle, dualSteer);
        }
      }
      if (dualLeftTouchId === null && dualRightTouchId === null) {
        emergencyStop();
      }
    } else if (currentMode === 'single') {
      if (isDraggingSingle) {
        isDraggingSingle = false;
        emergencyStop();
      }
    }
  }

  window.addEventListener('touchend', handleTouchRelease);
  window.addEventListener('touchcancel', handleTouchRelease);

  // Desktop Mouse Support
  let mouseActiveLeft = false;
  let mouseActiveRight = false;
  joyDualLeft.addEventListener('mousedown', e => {
    mouseActiveLeft = true;
    let rect = joyDualLeft.getBoundingClientRect();
    dualLeftCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    handleDualLeftMove(e);
    startHeartbeat();
  });
  joyDualRight.addEventListener('mousedown', e => {
    mouseActiveRight = true;
    let rect = joyDualRight.getBoundingClientRect();
    dualRightCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    handleDualRightMove(e);
    startHeartbeat();
  });
  if (joySingleBase) {
    joySingleBase.addEventListener('mousedown', e => {
      isDraggingSingle = true;
      let rect = joySingleBase.getBoundingClientRect();
      singleCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
      handleSingleMove(e);
      startHeartbeat();
    });
  }
  window.addEventListener('mousemove', e => {
    if (mouseActiveLeft) handleDualLeftMove(e);
    if (mouseActiveRight) handleDualRightMove(e);
    if (isDraggingSingle) handleSingleMove(e);
  });
  window.addEventListener('mouseup', () => {
    if (mouseActiveLeft || mouseActiveRight || isDraggingSingle) {
      mouseActiveLeft = false;
      mouseActiveRight = false;
      isDraggingSingle = false;
      emergencyStop();
    }
  });

  // ======================== D-PAD BUTTON CONTROLS ========================
  function bindDpad(btnId, throttleVal, steerVal) {
    let btn = document.getElementById(btnId);
    if (!btn) return;
    const start = (e) => {
      e.preventDefault();
      btn.classList.add('active');
      if (throttleVal !== null) dpadThrottle = throttleVal;
      if (steerVal !== null) dpadSteer = steerVal;
      startHeartbeat();
      computeMotorMix(dpadThrottle, dpadSteer);
    };
    const end = (e) => {
      e.preventDefault();
      btn.classList.remove('active');
      if (throttleVal !== null) dpadThrottle = 0;
      if (steerVal !== null) dpadSteer = 0;
      if (dpadThrottle === 0 && dpadSteer === 0) emergencyStop();
      else computeMotorMix(dpadThrottle, dpadSteer);
    };
    btn.addEventListener('touchstart', start, { passive: false });
    btn.addEventListener('touchend', end);
    btn.addEventListener('touchcancel', end);
    btn.addEventListener('mousedown', start);
    btn.addEventListener('mouseup', end);
  }

  bindDpad('btn-dpad-fwd', 1, null);
  bindDpad('btn-dpad-rev', -1, null);
  bindDpad('btn-dpad-left', null, -1);
  bindDpad('btn-dpad-right', null, 1);

  // ======================== CALIBRATION MODAL ========================
  function openModal() {
    document.getElementById('cfg-sens').value = turnSens;
    document.getElementById('cfg-trim').value = steeringTrim;
    document.getElementById('cfg-inv-steer').checked = invertSteer;
    document.getElementById('cfg-inv-throt').checked = invertThrot;
    let rBox = document.getElementById('cfg-relay-low');
    if (rBox) rBox.checked = relayIsLow;
    updateRelayDiagLabel(relayIsLow);
    updateCalibLabels();
    document.getElementById('modal').classList.add('open');
  }

  function closeModal() {
    document.getElementById('modal').classList.remove('open');
  }

  function updateCalibLabels() {
    document.getElementById('lbl-sens').textContent = parseFloat(document.getElementById('cfg-sens').value).toFixed(2) + 'x';
    let t = parseInt(document.getElementById('cfg-trim').value, 10);
    document.getElementById('lbl-trim').textContent = (t > 0 ? '+' : '') + t + '%';
  }

  function saveCalib() {
    turnSens = parseFloat(document.getElementById('cfg-sens').value) || 0.75;
    steeringTrim = parseInt(document.getElementById('cfg-trim').value, 10) || 0;
    invertSteer = document.getElementById('cfg-inv-steer').checked;
    invertThrot = document.getElementById('cfg-inv-throt').checked;
    let rBox = document.getElementById('cfg-relay-low');
    if (rBox) relayIsLow = rBox.checked;

    localStorage.setItem('rover_calib', JSON.stringify({ turnSens, steeringTrim, invertSteer, invertThrot, relayIsLow }));
    closeModal();
  }
</script>
</body>
</html>
)rawliteral";

// ======================== HTTP REQUEST HANDLERS ========================
static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, INDEX_HTML, strlen(INDEX_HTML));
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char part_buf[64];

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("[ERROR] Camera capture failed");
      res = ESP_FAIL;
    } else {
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) {
          Serial.println("[ERROR] JPEG compression failed");
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }

    if (res == ESP_OK) {
      size_t hlen = snprintf(part_buf, 64, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }

    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }

    if (res != ESP_OK) break;

    // Frame pacing delay (~22-25 FPS): frees CPU cycles for Wi-Fi stack & prevents socket saturation
    vTaskDelay(pdMS_TO_TICKS(28));
  }
  return res;
}

static esp_err_t drive_handler(httpd_req_t *req) {
  char buf[64];
  int left = 0, right = 0;

  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[16];
    if (httpd_query_key_value(buf, "left", param, sizeof(param)) == ESP_OK) {
      left = atoi(param);
    }
    if (httpd_query_key_value(buf, "right", param, sizeof(param)) == ESP_OK) {
      right = atoi(param);
    }
  }

  set_motors(left, right);
  last_command_time = millis();  // Refresh watchdog timer

  // Serial diagnostics: print motor values every 500ms when motors are active
  static unsigned long last_serial_log = 0;
  if (millis() - last_serial_log > 500 && (left != 0 || right != 0)) {
    Serial.printf("[DRIVE] Left PWM: %d (IN1: GPIO14, IN2: GPIO15) | Right PWM: %d (IN3: GPIO13, IN4: GPIO12)\n",
                  left, right);
    last_serial_log = millis();
  }

  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, "{\"status\":\"ok\"}", strlen("{\"status\":\"ok\"}"));
}

static esp_err_t spray_handler(httpd_req_t *req) {
  char buf[64];
  unsigned long duration = 1000;  // Calibrated default: 1.0 second (1000ms)

  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[16];
    if (httpd_query_key_value(buf, "polarity", param, sizeof(param)) == ESP_OK) {
      if (strcmp(param, "low") == 0) {
        relay_active_low = true;
        Serial.println("[PUMP] Polarity changed -> ACTIVE-LOW (0V = ON)");
      } else {
        relay_active_low = false;
        Serial.println("[PUMP] Polarity changed -> ACTIVE-HIGH (3.3V = ON)");
      }
      digitalWrite(PIN_RELAY, get_relay_off());
      spray_active = false;
    } else if (httpd_query_key_value(buf, "state", param, sizeof(param)) == ESP_OK) {
      // Manual bench test override
      if (strcmp(param, "on") == 0 || strcmp(param, "1") == 0) {
        digitalWrite(PIN_RELAY, get_relay_on());
        spray_active = false;
        Serial.println("[PUMP] Manual Override -> ON");
      } else {
        digitalWrite(PIN_RELAY, get_relay_off());
        spray_active = false;
        Serial.println("[PUMP] Manual Override -> OFF");
      }
    } else if (httpd_query_key_value(buf, "ms", param, sizeof(param)) == ESP_OK) {
      duration = atol(param);
      if (duration < 50) duration = 50;
      if (duration > 5000) duration = 5000;
      trigger_spray(duration);
    } else {
      trigger_spray(duration);
    }
  } else {
    trigger_spray(duration);
  }

  httpd_resp_set_type(req, "application/json");
  char res_json[96];
  snprintf(res_json, sizeof(res_json), "{\"status\":\"ok\",\"ms\":%lu,\"polarity\":\"%s\",\"relay_pin\":%d}",
           duration, (relay_active_low ? "LOW" : "HIGH"), PIN_RELAY);
  return httpd_resp_send(req, res_json, strlen(res_json));
}

static esp_err_t flash_handler(httpd_req_t *req) {
  char buf[32];
  int val = 0;

  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[16];
    if (httpd_query_key_value(buf, "val", param, sizeof(param)) == ESP_OK) {
      val = atoi(param);
      val = constrain(val, 0, 255);
    }
  }

  pwm_write(PIN_FLASH, LEDC_CH_FLASH, val);
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, "{\"status\":\"ok\"}", strlen("{\"status\":\"ok\"}"));
}

static esp_err_t probe_handler(httpd_req_t *req) {
  trigger_soil_probe();
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, "{\"status\":\"probing_started\"}", strlen("{\"status\":\"probing_started\"}"));
}

static esp_err_t probe_threshold_handler(httpd_req_t *req) {
  char buf[32];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[16];
    if (httpd_query_key_value(buf, "val", param, sizeof(param)) == ESP_OK) {
      moisture_threshold = atoi(param);
      moisture_threshold = constrain(moisture_threshold, 5, 95);
      Serial.printf("[PROBE] Moisture Threshold set to %d%%\n", moisture_threshold);
    }
  }
  char res_json[64];
  snprintf(res_json, sizeof(res_json), "{\"status\":\"ok\",\"threshold\":%d}", moisture_threshold);
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, res_json, strlen(res_json));
}

static esp_err_t probe_status_handler(httpd_req_t *req) {
  char res_json[220];
  snprintf(res_json, sizeof(res_json),
           "{\"state\":%d,\"dry\":%s,\"raw\":%d,\"percent\":%d,\"threshold\":%d,\"status\":\"%s\",\"idle\":%s}",
           (int)current_probe_state,
           (last_probe_dry ? "true" : "false"),
           last_moisture_raw,
           last_moisture_percent,
           moisture_threshold,
           probe_telemetry_status.c_str(),
           (current_probe_state == PROBE_IDLE ? "true" : "false"));
  httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, res_json, strlen(res_json));
}

// ======================== SERVER INITIALIZATION ========================
void startCameraServer() {
  // -------------------------------------------------------------------
  // Port 80 HTTP Server: DEDICATED EXCLUSIVELY TO UI & CONTROL COMMANDS
  // -------------------------------------------------------------------
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.ctrl_port = 32768;
  config.max_open_sockets = 7;
  config.lru_purge_enable = true;
  config.stack_size = 8192;

  httpd_uri_t index_uri = { .uri = "/", .method = HTTP_GET, .handler = index_handler, .user_ctx = NULL };
  httpd_uri_t drive_uri = { .uri = "/drive", .method = HTTP_GET, .handler = drive_handler, .user_ctx = NULL };
  httpd_uri_t spray_uri = { .uri = "/spray", .method = HTTP_GET, .handler = spray_handler, .user_ctx = NULL };
  httpd_uri_t flash_uri = { .uri = "/flash", .method = HTTP_GET, .handler = flash_handler, .user_ctx = NULL };
  httpd_uri_t probe_uri = { .uri = "/probe", .method = HTTP_GET, .handler = probe_handler, .user_ctx = NULL };
  httpd_uri_t probe_status_uri = { .uri = "/probe_status", .method = HTTP_GET, .handler = probe_status_handler, .user_ctx = NULL };

  // Note: /stream is deliberately NOT registered on Port 80 to prevent thread starvation!
  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &drive_uri);
    httpd_register_uri_handler(camera_httpd, &spray_uri);
    httpd_register_uri_handler(camera_httpd, &flash_uri);
    httpd_uri_t probe_thresh_uri = { .uri = "/probe_threshold", .method = HTTP_GET, .handler = probe_threshold_handler, .user_ctx = NULL };
    httpd_register_uri_handler(camera_httpd, &probe_uri);
    httpd_register_uri_handler(camera_httpd, &probe_status_uri);
    httpd_register_uri_handler(camera_httpd, &probe_thresh_uri);
  }

  // -------------------------------------------------------------------
  // Port 81 HTTP Server: DEDICATED EXCLUSIVELY TO MJPEG STREAMING
  // -------------------------------------------------------------------
  httpd_config_t stream_config = HTTPD_DEFAULT_CONFIG();
  stream_config.server_port = 81;
  stream_config.ctrl_port = 32769;
  stream_config.max_open_sockets = 3;
  stream_config.lru_purge_enable = true;
  stream_config.stack_size = 8192;

  httpd_uri_t stream_uri = { .uri = "/stream", .method = HTTP_GET, .handler = stream_handler, .user_ctx = NULL };

  if (httpd_start(&stream_httpd, &stream_config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

// ======================== SETUP & MAIN LOOP ========================
void setup() {
  // Disable brownout detector during bench setup
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  Serial.println("\n[BOOT] Agri Rover ESP32-CAM Prototype Initializing...");

  // Setup Relay Pin (Ensure relay starts in confirmed OFF state)
  digitalWrite(PIN_RELAY, get_relay_off());
  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, get_relay_off());

  // 1. Camera Configuration & Init FIRST
  // CRITICAL: esp_camera_init() configures the 20MHz XCLK clock and resets the LEDC hardware driver.
  // We MUST initialize the camera before configuring motor LEDC PWM channels, otherwise
  // esp_camera_init() wipes out motor pin attachments!
  camera_config_t cam_config;
  cam_config.ledc_channel = LEDC_CHANNEL_7;
  cam_config.ledc_timer = LEDC_TIMER_3;
  cam_config.pin_d0 = Y2_GPIO_NUM;
  cam_config.pin_d1 = Y3_GPIO_NUM;
  cam_config.pin_d2 = Y4_GPIO_NUM;
  cam_config.pin_d3 = Y5_GPIO_NUM;
  cam_config.pin_d4 = Y6_GPIO_NUM;
  cam_config.pin_d5 = Y7_GPIO_NUM;
  cam_config.pin_d6 = Y8_GPIO_NUM;
  cam_config.pin_d7 = Y9_GPIO_NUM;
  cam_config.pin_xclk = XCLK_GPIO_NUM;
  cam_config.pin_pclk = PCLK_GPIO_NUM;
  cam_config.pin_vsync = VSYNC_GPIO_NUM;
  cam_config.pin_href = HREF_GPIO_NUM;
  cam_config.pin_sscb_sda = SIOD_GPIO_NUM;
  cam_config.pin_sscb_scl = SIOC_GPIO_NUM;
  cam_config.pin_pwdn = PWDN_GPIO_NUM;
  cam_config.pin_reset = RESET_GPIO_NUM;
  cam_config.xclk_freq_hz = 20000000;
  cam_config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    Serial.println("[INFO] PSRAM Detected! Enabling HVGA Double Buffering (Optimized Bandwidth).");
    cam_config.frame_size = FRAMESIZE_HVGA;  // 480x320 - crisp on mobile & low Wi-Fi congestion
    cam_config.jpeg_quality = 16;            // Quality 16 reduces frame payload to ~12KB
    cam_config.fb_count = 2;
  } else {
    Serial.println("[WARN] No PSRAM Found. Falling back to QVGA Single Buffer.");
    cam_config.frame_size = FRAMESIZE_QVGA;  // 320x240
    cam_config.jpeg_quality = 18;
    cam_config.fb_count = 1;
  }

  // Camera Init
  esp_err_t err = esp_camera_init(&cam_config);
  if (err != ESP_OK) {
    Serial.printf("[ERROR] Camera init failed with error 0x%x\n", err);
    return;
  }
  Serial.println("[OK] Camera Initialized.");

  // 2. Setup PWM channels for Motors AFTER Camera Init (Guarantees LEDC channels remain active)
#if CORE_V3
  ledcAttach(PIN_MOTOR_L_A, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_MOTOR_L_B, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_MOTOR_R_A, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_MOTOR_R_B, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_FLASH, 1000, PWM_RES);
#else
  ledcSetup(LEDC_CH_L_A, PWM_FREQ, PWM_RES);
  ledcSetup(LEDC_CH_L_B, PWM_FREQ, PWM_RES);
  ledcSetup(LEDC_CH_R_A, PWM_FREQ, PWM_RES);
  ledcSetup(LEDC_CH_R_B, PWM_FREQ, PWM_RES);
  ledcSetup(LEDC_CH_FLASH, 1000, PWM_RES);

  ledcAttachPin(PIN_MOTOR_L_A, LEDC_CH_L_A);
  ledcAttachPin(PIN_MOTOR_L_B, LEDC_CH_L_B);
  ledcAttachPin(PIN_MOTOR_R_A, LEDC_CH_R_A);
  ledcAttachPin(PIN_MOTOR_R_B, LEDC_CH_R_B);
  ledcAttachPin(PIN_FLASH, LEDC_CH_FLASH);
#endif

  // Setup MG996R Servo & Soil Moisture Sensor Pins
  pinMode(PIN_MOISTURE_IN, INPUT_PULLUP);
#if CORE_V3
  ledcAttach(PIN_SERVO, SERVO_PWM_FREQ, SERVO_PWM_RES);
#else
  ledcSetup(LEDC_CH_SERVO, SERVO_PWM_FREQ, SERVO_PWM_RES);
  ledcAttachPin(PIN_SERVO, LEDC_CH_SERVO);
#endif
  set_servo_angle(10); // Initialize in safe stowed/transport position

  stop_motors();
  pwm_write(PIN_FLASH, LEDC_CH_FLASH, 0);
  Serial.println("[OK] Motor PWM (Pins 14, 15, 13, 12), Direct 12V Relay & Servo Configured.");

  // Setup Wi-Fi SoftAP (Pure AP mode + Zero Modem Sleep + Max TX Power)
  if (strlen(STA_SSID) > 0) {
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(STA_SSID, STA_PASS);
    Serial.print("[STA] Connecting to router: ");
    Serial.println(STA_SSID);
  } else {
    WiFi.mode(WIFI_AP);
  }

  WiFi.softAP(AP_SSID, AP_PASS, 1, 0, 4);
  WiFi.setSleep(false);                 // CRITICAL: Disable Wi-Fi modem sleep for rock-solid connection!
  WiFi.setTxPower(WIFI_POWER_19_5dBm);  // Maximize RF transmission power (+19.5dBm)

  IPAddress IP = WiFi.softAPIP();
  Serial.print("[AP] Access Point Started. SSID: ");
  Serial.println(AP_SSID);
  Serial.print("[AP] Connect Phone to: http://");
  Serial.println(IP);

  startCameraServer();
  Serial.println("[OK] HTTP & MJPEG Stream Servers Active.");
  last_command_time = millis();
}

void loop() {
  // Process Non-blocking direct 12V chemical/water spray pulse
  process_spray_watchdog();

  // Process In-Situ Soil Moisture Probing & Localized Sprinkler FSM
  process_soil_probe_fsm();

  // Process Safety Watchdog (Auto-halt if Wi-Fi packets stall)
  if (millis() - last_command_time > WATCHDOG_TIMEOUT_MS) {
    stop_motors();
  }

  delay(5);
}
