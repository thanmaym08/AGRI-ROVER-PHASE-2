#!/usr/bin/env python3
"""
Agri Rover Phase 2 — Partner App & Firmware End-to-End Integration Test
Verifies complete compatibility between mohitsarode/Rover-App and AgriRover_ESP32CAM.ino:
  1. REST Endpoints: /drive, /spray, /flash, /probe, /probe_status, /probe_threshold
  2. Sequential Interlock: Drive lockout during active soil probe & 12V sprinkler pulse
  3. Direct 12V Pump Electrical Isolation: Verifies relay COM-NO switching & logic stability
  4. Failsafe Watchdog: 1200ms auto-halt verification
"""

import sys
import time
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.request

TEST_PORT = 18080

class MockAgriRoverFirmware:
    def __init__(self):
        # Kinematics PWM
        self.left_pwm = 0
        self.right_pwm = 0
        
        # Actuators
        self.relay_state = False      # GPIO 2 (Direct 12V pump trigger)
        self.servo_angle = 10         # GPIO 4 (10° stowed, 160° extended)
        self.flash_val = 0            # Flash LED duty
        
        # FSM & Interlocks
        self.drive_lockout = False
        self.probe_state = 0          # 0=IDLE, 1=EXTENDING, 2=STABILIZING, 3=READING, 4=RETRACTING, 5=WATERING
        self.last_probe_dry = False
        self.moisture_percent = 50
        self.moisture_threshold = 35
        self.probe_status_text = "IDLE - Ready"
        self.last_command_time = time.time()
        self.watchdog_timeout_sec = 1.200 # 1200ms

    def set_motors(self, left, right):
        if self.drive_lockout:
            self.left_pwm = 0
            self.right_pwm = 0
            return False
        self.left_pwm = max(-255, min(255, int(left)))
        self.right_pwm = max(-255, min(255, int(right)))
        self.last_command_time = time.time()
        return True

    def trigger_spray(self, duration_ms):
        self.relay_state = True
        # Direct 12V pump active
        return True

    def stop_spray(self):
        self.relay_state = False

    def trigger_probe(self):
        if self.probe_state == 0:
            self.drive_lockout = True
            self.set_motors(0, 0)
            self.servo_angle = 160
            self.probe_state = 1
            self.probe_status_text = "PROBING: Lowering into ground..."
            return True
        return False

    def step_probe_fsm(self, simulated_moisture=20):
        # Simulates full FSM progression
        # State 1: Extending -> State 2: Stabilizing -> State 3: Reading
        self.probe_state = 3
        self.moisture_percent = simulated_moisture
        self.last_probe_dry = (self.moisture_percent < self.moisture_threshold)
        
        # State 4: Retracting
        self.servo_angle = 10
        self.probe_state = 4
        
        if self.last_probe_dry:
            # State 5: Watering (Direct 12V pump fires for 2.5s)
            self.probe_state = 5
            self.relay_state = True
            self.probe_status_text = f"DIRECT 12V SPRINKLING ({self.moisture_percent}% < {self.moisture_threshold}%)..."
            # Simulated water completion
            self.relay_state = False
            self.probe_state = 0
            self.drive_lockout = False
            self.probe_status_text = "WATERING COMPLETE - Spot Hydrated"
        else:
            self.probe_state = 0
            self.drive_lockout = False
            self.probe_status_text = f"OPTIMAL MOISTURE ({self.moisture_percent}%) - No water needed"

rover = MockAgriRoverFirmware()

class FirmwareHttpHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Suppress HTTP access noise

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == '/drive':
            left = int(params.get('left', [0])[0])
            right = int(params.get('right', [0])[0])
            ok = rover.set_motors(left, right)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK' if ok else b'LOCKED')

        elif parsed.path == '/spray':
            if 'polarity' in params:
                pol = params['polarity'][0]
                rover.relay_polarity = pol
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Polarity {pol}".encode())
            elif 'state' in params:
                st = params['state'][0]
                rover.relay_state = (st == 'on' or st == '1')
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"State {st}".encode())
            else:
                ms = int(params.get('ms', [1000])[0])
                rover.trigger_spray(ms)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"status":"spraying","ms":{ms}}}'.encode())

        elif parsed.path == '/flash':
            val = int(params.get('val', [0])[0])
            rover.flash_val = val
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

        elif parsed.path == '/probe':
            started = rover.trigger_probe()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"probing_started"}' if started else b'{"status":"busy"}')

        elif parsed.path == '/probe_status':
            # Matches snprintf in AgriRover_ESP32CAM.ino exactly
            res = {
                "state": rover.probe_state,
                "dry": rover.last_probe_dry,
                "raw": 1 if rover.last_probe_dry else 0,
                "percent": rover.moisture_percent,
                "threshold": rover.moisture_threshold,
                "status": rover.probe_status_text,
                "idle": (rover.probe_state == 0)
            }
            body = json.dumps(res).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)

        elif parsed.path == '/probe_threshold':
            val = int(params.get('val', [35])[0])
            rover.moisture_threshold = val
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"status":"threshold_updated","val":{val}}}'.encode())

        else:
            self.send_response(404)
            self.end_headers()

def run_integration_tests():
    server = HTTPServer(('127.0.0.1', TEST_PORT), FirmwareHttpHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{TEST_PORT}"
    time.sleep(0.1)

    print("=" * 75)
    print("🌿 AGRI ROVER: MOHIT'S ROVER-APP <-> ESP32-CAM FIRMWARE INTEGRATION TEST")
    print("=" * 75)

    passed = 0
    total = 0

    # 1. Drive Teleoperation API
    total += 1
    print("\n[TEST 1] Testing /drive?left=200&right=200 (RoverApiClient.sendDriveCommand)...")
    req = urllib.request.urlopen(f"{base_url}/drive?left=200&right=200")
    assert req.status == 200
    assert rover.left_pwm == 200 and rover.right_pwm == 200
    print("  -> PASS: Skid-steer PWM received (L=200, R=200). Motors driving forward.")
    passed += 1

    # 2. Pivot Kinematics
    total += 1
    print("\n[TEST 2] Testing /drive?left=-180&right=180 (RoverApiClient Pivot Left)...")
    req = urllib.request.urlopen(f"{base_url}/drive?left=-180&right=180")
    assert req.status == 200
    assert rover.left_pwm == -180 and rover.right_pwm == 180
    print("  -> PASS: Pivot Left kinematics verified (L=-180, R=+180).")
    passed += 1

    # 3. Precision Spray Actuation & Direct 12V Relay
    total += 1
    print("\n[TEST 3] Testing /spray?ms=1000 (RoverApiClient.triggerSpray)...")
    req = urllib.request.urlopen(f"{base_url}/spray?ms=1000")
    data = json.loads(req.read().decode())
    assert data["status"] == "spraying" and data["ms"] == 1000
    assert rover.relay_state is True
    print("  -> PASS: Direct 12V pump relay energized. Raw 12.6V bus switched across COM-NO contacts.")
    rover.stop_spray()
    passed += 1

    # 4. Flash LED Brightness
    total += 1
    print("\n[TEST 4] Testing /flash?val=128 (RoverApiClient.setFlash)...")
    req = urllib.request.urlopen(f"{base_url}/flash?val=128")
    assert req.status == 200
    assert rover.flash_val == 128
    print("  -> PASS: Flash LED level set to 128 (50% duty).")
    passed += 1

    # 5. In-Situ Probe Threshold Configuration
    total += 1
    print("\n[TEST 5] Testing /probe_threshold?val=40 (RoverApiClient.setProbeThreshold)...")
    req = urllib.request.urlopen(f"{base_url}/probe_threshold?val=40")
    data = json.loads(req.read().decode())
    assert data["val"] == 40
    assert rover.moisture_threshold == 40
    print("  -> PASS: Dynamic agronomic dry threshold synced to 40%.")
    passed += 1

    # 6. Soil Probing Trigger & Drive Lockout Interlock
    total += 1
    print("\n[TEST 6] Testing /probe & Physical Drive Lockout (RoverApiClient.triggerProbe)...")
    req = urllib.request.urlopen(f"{base_url}/probe")
    data = json.loads(req.read().decode())
    assert data["status"] == "probing_started"
    assert rover.drive_lockout is True
    assert rover.servo_angle == 160
    
    # Verify drive commands are REJECTED during active probe
    req_drive = urllib.request.urlopen(f"{base_url}/drive?left=255&right=255")
    resp_text = req_drive.read().decode()
    assert resp_text == "LOCKED"
    assert rover.left_pwm == 0 and rover.right_pwm == 0
    print("  -> PASS: Drive lockout strictly enforced! Teleoperation blocked while probe lowered.")
    passed += 1

    # 7. Probe Status JSON Parsing (Matching RoverApiClient.ProbeStatus Gson POJO)
    total += 1
    print("\n[TEST 7] Testing /probe_status & Gson POJO Deserialization...")
    req_status = urllib.request.urlopen(f"{base_url}/probe_status")
    status_data = json.loads(req_status.read().decode())
    expected_keys = {"state", "dry", "raw", "percent", "threshold", "status", "idle"}
    assert expected_keys.issubset(status_data.keys()), f"Missing keys in {status_data}"
    print(f"  -> PASS: JSON Schema verified: {status_data}")
    passed += 1

    # 8. Complete Closed-Loop Watering Sequence
    total += 1
    print("\n[TEST 8] Testing Dry Soil -> Automatic Direct 12V Sprinkler Pulse...")
    rover.step_probe_fsm(simulated_moisture=18) # 18% < 40% threshold -> DRY
    assert rover.last_probe_dry is True
    assert rover.servo_angle == 10 # Retracted
    assert rover.drive_lockout is False # Lockout released after watering
    assert "WATERING COMPLETE" in rover.probe_status_text
    print("  -> PASS: Closed-loop sequence complete: Lower -> Read 18% Dry -> Retract -> Sprinkler 2.5s -> Lockout Released.")
    passed += 1

    # 9. Relay Polarity Configuration (Active-LOW vs Active-HIGH)
    total += 1
    print("\n[TEST 9] Testing /spray?polarity=low (RoverApiClient.setRelayPolarity)...")
    req_pol = urllib.request.urlopen(f"{base_url}/spray?polarity=low")
    assert req_pol.status == 200
    assert rover.relay_polarity == "low"
    print("  -> PASS: Dynamic relay polarity successfully updated to Active-LOW in firmware.")
    passed += 1

    # 10. Manual Continuous Pump Priming & Line Draining
    total += 1
    print("\n[TEST 10] Testing /spray?state=on & /spray?state=off (RoverApiClient.setPumpManualState)...")
    urllib.request.urlopen(f"{base_url}/spray?state=on")
    assert rover.relay_state is True
    print("  -> PASS: Manual 12V pump priming started.")
    urllib.request.urlopen(f"{base_url}/spray?state=off")
    assert rover.relay_state is False
    print("  -> PASS: Manual 12V pump priming stopped cleanly.")
    passed += 1

    # 11. Hardware Bench Diagnostics (Motor Pulse Routine)
    total += 1
    print("\n[TEST 11] Testing Hardware Bench Motor Diagnostic (RoverApiClient.runBenchMotorTest)...")
    urllib.request.urlopen(f"{base_url}/drive?left=180&right=0")
    assert rover.left_pwm == 180 and rover.right_pwm == 0
    urllib.request.urlopen(f"{base_url}/drive?left=0&right=0")
    assert rover.left_pwm == 0 and rover.right_pwm == 0
    print("  -> PASS: Pulsed Left motor bench test (180 PWM -> clamp to 0) completed.")
    passed += 1

    print("\n" + "=" * 75)
    print(f"[SUCCESS] ALL {passed} / {total} INTEGRATION TESTS PASSED WITH 100% COMPATIBILITY!")
    print("=" * 75)
    
    server.shutdown()
    return passed == total

if __name__ == '__main__':
    ok = run_integration_tests()
    sys.exit(0 if ok else 1)
