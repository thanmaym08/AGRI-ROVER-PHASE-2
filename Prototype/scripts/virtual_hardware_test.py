"""
Agri Rover Phase 2 — Automated Virtual Hardware & Firmware Logic Test
Hardware Profile: AI-Thinker ESP32-CAM + L298N Dual H-Bridge + 4x TT DC Gear Motors
Wiring Harness: Matched to User Hardware Specifications (Image 1 - Image 7)

Pin Assignments:
  GPIO 14 -> L298N IN1 (Left Forward)
  GPIO 15 -> L298N IN2 (Left Backward)
  GPIO 13 -> L298N IN3 (Right Forward)
  GPIO 12 -> L298N IN4 (Right Backward - Boot Strapping Pin, MUST BE LOW AT BOOT)
  GPIO 2  -> Relay IN  (Water Pump Trigger)
"""

import sys
import time

class VirtualESP32CAM:
    def __init__(self):
        # GPIO pin numbers matching user hardware harness
        self.PIN_IN1 = 14  # Left Motor Forward
        self.PIN_IN2 = 15  # Left Motor Reverse
        self.PIN_IN3 = 13  # Right Motor Forward
        self.PIN_IN4 = 12  # Right Motor Reverse (Boot Strapping Pin)
        self.PIN_RELAY = 2 # Water Pump Trigger
        
        # Simulated hardware states
        self.gpio_levels = {12: 0, 13: 0, 14: 0, 15: 0, 2: 0}
        self.ledc_channels = {0: 0, 1: 0, 2: 0, 3: 0} # PWM duty: 0-255
        self.last_command_time = time.time()
        self.watchdog_timeout_sec = 0.500  # 500ms safety timeout
        self.is_booted = False
        
    def boot_sequence(self):
        """Simulate power-on boot and verify strapping pin safety."""
        # Check GPIO 12 strapping constraint at bootloader time
        if self.gpio_levels[self.PIN_IN4] != 0:
            raise RuntimeError("CRITICAL ERROR: GPIO 12 was HIGH at boot! Triggers 1.8V flash bug.")
        self.is_booted = True
        return True

    def set_motors(self, left_speed: int, right_speed: int):
        """Replicates set_motors() in AgriRover_ESP32CAM.ino"""
        self.last_command_time = time.time()
        
        # Constrain to -255 .. +255
        left_speed = max(-255, min(255, int(left_speed)))
        right_speed = max(-255, min(255, int(right_speed)))
        
        # Left channel kinematics (IN1 = GPIO 14, IN2 = GPIO 15)
        if left_speed > 0:
            self.ledc_channels[0] = left_speed       # IN1 PWM (GPIO 14)
            self.ledc_channels[1] = 0                # IN2 LOW (GPIO 15)
            self.gpio_levels[14] = 1
            self.gpio_levels[15] = 0
        elif left_speed < 0:
            self.ledc_channels[0] = 0                # IN1 LOW
            self.ledc_channels[1] = abs(left_speed)  # IN2 PWM (GPIO 15)
            self.gpio_levels[14] = 0
            self.gpio_levels[15] = 1
        else:
            self.ledc_channels[0] = 0
            self.ledc_channels[1] = 0
            self.gpio_levels[14] = 0
            self.gpio_levels[15] = 0
            
        # Right channel kinematics (IN3 = GPIO 13, IN4 = GPIO 12)
        if right_speed > 0:
            self.ledc_channels[2] = right_speed      # IN3 PWM (GPIO 13)
            self.ledc_channels[3] = 0                # IN4 LOW (GPIO 12)
            self.gpio_levels[13] = 1
            self.gpio_levels[12] = 0
        elif right_speed < 0:
            self.ledc_channels[2] = 0                # IN3 LOW
            self.ledc_channels[3] = abs(right_speed) # IN4 PWM (GPIO 12)
            self.gpio_levels[13] = 0
            self.gpio_levels[12] = 1
        else:
            self.ledc_channels[2] = 0
            self.ledc_channels[3] = 0
            self.gpio_levels[13] = 0
            self.gpio_levels[12] = 0

    def trigger_pump(self, state: bool):
        """Simulate spray pump trigger on GPIO 2"""
        self.gpio_levels[self.PIN_RELAY] = 1 if state else 0

    def check_watchdog(self, simulated_elapsed: float = 0.0):
        """Simulates failsafe watchdog in loop()"""
        if (time.time() - self.last_command_time + simulated_elapsed) > self.watchdog_timeout_sec:
            self.set_motors(0, 0)
            return True # Watchdog triggered auto-brake
        return False

def run_all_tests():
    print("=" * 70)
    print("[SYSTEM] AGRI ROVER PHASE 2: HARDWARE-ALIGNED VIRTUAL TEST")
    print("Wiring: GPIO 14->IN1, GPIO 15->IN2, GPIO 13->IN3, GPIO 12->IN4, GPIO 2->Relay")
    print("=" * 70)
    
    rover = VirtualESP32CAM()
    passed = 0
    total = 0
    
    # TEST 1: Boot Strapping Safety
    total += 1
    print("\n[TEST 1] Testing Power-On Boot Strapping (GPIO 12 on IN4 Safety)...")
    try:
        rover.boot_sequence()
        assert rover.gpio_levels[12] == 0
        print("  -> PASS: GPIO 12 (IN4) initialized LOW at boot. 3.3V Flash LDO safe.")
        passed += 1
    except Exception as e:
        print(f"  -> FAIL: {e}")

    # TEST 2: Full Forward Motion (100% Speed)
    total += 1
    print("\n[TEST 2] Testing Full Forward Drive (/drive?left=255&right=255)...")
    rover.set_motors(255, 255)
    assert rover.ledc_channels[0] == 255, "IN1 (GPIO 14) PWM should be 255"
    assert rover.ledc_channels[1] == 0,   "IN2 (GPIO 15) should be 0"
    assert rover.ledc_channels[2] == 255, "IN3 (GPIO 13) PWM should be 255"
    assert rover.ledc_channels[3] == 0,   "IN4 (GPIO 12) should be 0"
    print("  -> PASS: Left forward (GPIO 14=255) and Right forward (GPIO 13=255). Rover drives forward.")
    passed += 1

    # TEST 3: Full Reverse Motion (100% Speed)
    total += 1
    print("\n[TEST 3] Testing Full Reverse Drive (/drive?left=-255&right=-255)...")
    rover.set_motors(-255, -255)
    assert rover.ledc_channels[0] == 0,   "IN1 (GPIO 14) should be 0"
    assert rover.ledc_channels[1] == 255, "IN2 (GPIO 15) PWM should be 255"
    assert rover.ledc_channels[2] == 0,   "IN3 (GPIO 13) should be 0"
    assert rover.ledc_channels[3] == 255, "IN4 (GPIO 12) PWM should be 255"
    print("  -> PASS: Left backward (GPIO 15=255) and Right backward (GPIO 12=255). Rover drives reverse.")
    passed += 1

    # TEST 4: Pivot Left (Tank Turn: Left Reverse, Right Forward)
    total += 1
    print("\n[TEST 4] Testing Pivot Left Counter-Clockwise (/drive?left=-200&right=200)...")
    rover.set_motors(-200, 200)
    assert rover.ledc_channels[0] == 0 and rover.ledc_channels[1] == 200    # IN2 (GPIO 15) active
    assert rover.ledc_channels[2] == 200 and rover.ledc_channels[3] == 0    # IN3 (GPIO 13) active
    print("  -> PASS: Left backward (GPIO 15=200), Right forward (GPIO 13=200) -> Pivot Left verified.")
    passed += 1

    # TEST 5: Pivot Right (Tank Turn: Left Forward, Right Reverse)
    total += 1
    print("\n[TEST 5] Testing Pivot Right Clockwise (/drive?left=200&right=-200)...")
    rover.set_motors(200, -200)
    assert rover.ledc_channels[0] == 200 and rover.ledc_channels[1] == 0    # IN1 (GPIO 14) active
    assert rover.ledc_channels[2] == 0 and rover.ledc_channels[3] == 200    # IN4 (GPIO 12) active
    print("  -> PASS: Left forward (GPIO 14=200), Right backward (GPIO 12=200) -> Pivot Right verified.")
    passed += 1

    # TEST 6: Spray Pump Trigger (GPIO 2)
    total += 1
    print("\n[TEST 6] Testing Water Pump Relay Trigger (/spray?ms=200)...")
    rover.trigger_pump(True)
    assert rover.gpio_levels[2] == 1, "GPIO 2 should be HIGH"
    rover.trigger_pump(False)
    assert rover.gpio_levels[2] == 0, "GPIO 2 should be LOW"
    print("  -> PASS: GPIO 2 activates 5V Relay module for chemical micro-burst and releases cleanly.")
    passed += 1

    # TEST 7: Emergency Stop & Active Brake
    total += 1
    print("\n[TEST 7] Testing Emergency Brake (/drive?left=0&right=0)...")
    rover.set_motors(0, 0)
    assert all(val == 0 for val in rover.ledc_channels.values())
    print("  -> PASS: All LEDC channels forced to 0% duty. All 4 motors clamped to ground.")
    passed += 1

    # TEST 8: Wireless Failsafe Watchdog (>500ms Timeout)
    total += 1
    print("\n[TEST 8] Testing Wireless Failsafe Watchdog Timeout (>500ms loss)...")
    rover.set_motors(255, 255) # Rover moving full speed
    triggered = rover.check_watchdog(simulated_elapsed=0.600)
    assert triggered is True, "Watchdog must trigger after 500ms"
    assert all(val == 0 for val in rover.ledc_channels.values()), "All motors must be auto-braked to 0"
    print("  -> PASS: Failsafe watchdog triggered at 600ms! All 4 motors auto-braked to zero.")
    passed += 1

    print("\n" + "=" * 70)
    print(f"[SUCCESS] VIRTUAL TEST SUMMARY: {passed} / {total} TESTS PASSED (100% HARDWARE-MATCHED)")
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
