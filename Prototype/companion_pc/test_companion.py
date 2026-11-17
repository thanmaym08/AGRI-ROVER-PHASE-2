#!/usr/bin/env python3
"""
Agri Rover — Companion PC Vision Pipeline Automated Unit Test
File: Prototype/companion_pc/test_companion.py
"""

import cv2
import numpy as np
import unittest

PURPLE_LOWER = np.array([130, 50, 50])
PURPLE_UPPER = np.array([160, 255, 255])

RED_LOWER_1 = np.array([0, 70, 50])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 70, 50])
RED_UPPER_2 = np.array([180, 255, 255])

class TestCompanionVision(unittest.TestCase):
    def setUp(self):
        # Create a 640x480 test image
        self.w, self.h = 640, 480
        self.frame = np.zeros((self.h, self.w, 3), dtype=np.uint8)

    def test_caterpillar_detection(self):
        """Verify that a purple caterpillar target is detected and bounded accurately."""
        # Draw a synthetic purple caterpillar in the center of the frame
        center = (320, 240)
        cv2.circle(self.frame, center, 25, (180, 50, 160), -1)

        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        mask_purple = cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER)

        contours, _ = cv2.findContours(mask_purple, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.assertGreater(len(contours), 0, "Failed to segment purple target")

        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        self.assertGreater(area, 450, f"Target area {area} should exceed threshold 450px")

        x, y, cw, ch = cv2.boundingRect(cnt)
        cx = x + cw // 2
        cy = y + ch // 2

        self.assertAlmostEqual(cx, 320, delta=5, msg="Centroid X misaligned")
        self.assertAlmostEqual(cy, 240, delta=5, msg="Centroid Y misaligned")

    def test_weed_detection(self):
        """Verify that a red weed target is detected and bounded accurately."""
        # Draw a synthetic red weed target
        center = (200, 300)
        cv2.circle(self.frame, center, 20, (30, 40, 220), -1)

        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        mask_r1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
        mask_r2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
        mask_weed = cv2.bitwise_or(mask_r1, mask_r2)

        contours, _ = cv2.findContours(mask_weed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.assertGreater(len(contours), 0, "Failed to segment red weed target")

        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        self.assertGreater(area, 400)

        x, y, cw, ch = cv2.boundingRect(cnt)
        cx = x + cw // 2
        cy = y + ch // 2

        self.assertAlmostEqual(cx, 200, delta=5)
        self.assertAlmostEqual(cy, 300, delta=5)

    def test_reticle_lock_logic(self):
        """Verify targeting reticle lock calculation."""
        ret_xmin, ret_xmax = int(self.w * 0.35), int(self.w * 0.65)
        ret_ymin, ret_ymax = int(self.h * 0.20), int(self.h * 0.80)

        # Center point should be locked
        cx_in, cy_in = 320, 240
        locked = (ret_xmin <= cx_in <= ret_xmax) and (ret_ymin <= cy_in <= ret_ymax)
        self.assertTrue(locked, "Center point should be inside aiming reticle")

        # Edge point should NOT be locked
        cx_out, cy_out = 50, 50
        locked_out = (ret_xmin <= cx_out <= ret_xmax) and (ret_ymin <= cy_out <= ret_ymax)
        self.assertFalse(locked_out, "Corner point should NOT be inside aiming reticle")

if __name__ == "__main__":
    unittest.main(verbosity=2)
