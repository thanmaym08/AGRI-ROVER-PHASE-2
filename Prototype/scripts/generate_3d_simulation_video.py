"""
Agri Rover Phase 2 — 3D Video & Kinematics Simulation Generator
Generates a 720p HD MP4 video and animated GIF showing the complete cyber-physical
working of AgriRover_ESP32CAM.ino in lockstep with the Mobile Teleoperation App.
"""

import math
import cv2
import numpy as np

WIDTH = 1280
HEIGHT = 720
FPS = 24
DURATION_SEC = 14
TOTAL_FRAMES = DURATION_SEC * FPS

def project_3d(x, y, z, cx=460, cy=380, scale=110):
    """Isometric 3D projection to 2D screen coordinates."""
    # Rotate slightly around Y axis and tilt down (isometric perspective)
    angle_y = math.radians(35)
    angle_x = math.radians(25)
    
    # Rotate Y
    x1 = x * math.cos(angle_y) + z * math.sin(angle_y)
    y1 = y
    z1 = -x * math.sin(angle_y) + z * math.cos(angle_y)
    
    # Rotate X (pitch down)
    x2 = x1
    y2 = y1 * math.cos(angle_x) - z1 * math.sin(angle_x)
    z2 = y1 * math.sin(angle_x) + z1 * math.cos(angle_x)
    
    # Perspective division
    dist = 8.0
    factor = scale / (1.0 + z2 / dist)
    sx = int(cx + x2 * factor)
    sy = int(cy - y2 * factor)
    return sx, sy

def draw_polygon_3d(img, points_3d, color, border_color=(40, 50, 65)):
    pts_2d = [project_3d(p[0], p[1], p[2]) for p in points_3d]
    cv2.fillPoly(img, [np.array(pts_2d, dtype=np.int32)], color)
    cv2.polylines(img, [np.array(pts_2d, dtype=np.int32)], True, border_color, 2)

def generate_video():
    print(f"[INFO] Generating 3D simulation video: {TOTAL_FRAMES} frames @ {FPS} FPS...")
    
    video_path = r"F:\agrirover phase 2\Prototype\agrirover_3d_simulation.mp4"
    gif_path = r"F:\agrirover phase 2\Prototype\agrirover_3d_simulation.gif"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, FPS, (WIDTH, HEIGHT))
    
    gif_frames = []
    
    # Rover physical state
    rover_x = 0.0
    rover_z = -1.5
    rover_heading = 0.0 # radians
    wheel_angle = 0.0
    
    # Particle mist emitter
    particles = []
    
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        
        # -------------------------------------------------------------
        # STATE MACHINE SIMULATING AgriRover_ESP32CAM.ino & Mobile App
        # -------------------------------------------------------------
        if t < 2.0:
            # Phase 1: Boot & Connect
            phase_title = "PHASE 1: ESP32-CAM Boot & Wi-Fi Connect (SoftAP: 192.168.4.1)"
            left_pwm = 0
            right_pwm = 0
            joy_x, joy_y = 0, 0
            spray_active = False
            speed_mode = "MED 65%"
        elif t < 6.0:
            # Phase 2: Forward Drive (65% PWM)
            phase_title = "PHASE 2: Phone Joystick Forward -> All 4 Motors 65% PWM (165)"
            left_pwm = 165
            right_pwm = 165
            joy_x, joy_y = 0, -45
            spray_active = False
            speed_mode = "MED 65%"
            rover_x += math.sin(rover_heading) * 0.045
            rover_z += math.cos(rover_heading) * 0.045
            wheel_angle += 0.28
        elif t < 9.0:
            # Phase 3: Pivot Left Turn
            phase_title = "PHASE 3: Phone Joystick Left -> Skid-Steer Pivot Turn"
            left_pwm = -200
            right_pwm = 200
            joy_x, joy_y = -45, 0
            spray_active = False
            speed_mode = "MED 65%"
            rover_heading += 0.035
            wheel_angle += 0.22
        elif t < 12.0:
            # Phase 4: Target Lock & Spray Burst
            phase_title = "PHASE 4: Threat Detected -> Spray Micro-Burst (GPIO 2 HIGH)"
            left_pwm = 0
            right_pwm = 0
            joy_x, joy_y = 0, 0
            spray_active = True
            speed_mode = "BURST"
        else:
            # Phase 5: Failsafe Watchdog Auto-Brake
            phase_title = "PHASE 5: Watchdog Auto-Brake (500ms Signal Timeout Safe)"
            left_pwm = 0
            right_pwm = 0
            joy_x, joy_y = 0, 0
            spray_active = False
            speed_mode = "BRAKED"
            
        # -------------------------------------------------------------
        # CANVAS RENDERING
        # -------------------------------------------------------------
        img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        img[:] = (18, 22, 28) # Dark sci-fi background
        
        # 1. FARMLAND GROUND GRID & CROP ROWS
        for grid_z in range(-12, 14, 2):
            p1 = project_3d(-8, 0, grid_z)
            p2 = project_3d(8, 0, grid_z)
            cv2.line(img, p1, p2, (30, 38, 48), 1)
        for grid_x in range(-8, 9, 2):
            p1 = project_3d(grid_x, 0, -12)
            p2 = project_3d(grid_x, 0, 14)
            cv2.line(img, p1, p2, (30, 38, 48), 1)
            
        # Draw green crop bushes along rows
        for crop_x in [-3.2, 3.2]:
            for crop_z in range(-8, 10, 2):
                cx, cy = project_3d(crop_x, 0.4, crop_z)
                cv2.circle(img, (cx, cy), 16, (34, 139, 34), -1)
                cv2.circle(img, (cx, cy), 16, (46, 204, 113), 2)
                
        # 2. ROVER 3D MODEL
        rx = rover_x
        rz = rover_z
        rh = rover_heading
        
        def transform(local_x, local_y, local_z):
            # Rotate by rover heading
            tx = local_x * math.cos(rh) - local_z * math.sin(rh)
            tz = local_x * math.sin(rh) + local_z * math.cos(rh)
            return rx + tx, local_y, rz + tz

        # Chassis Plate
        p_chassis = [
            transform(-0.8, 0.4, -1.0),
            transform( 0.8, 0.4, -1.0),
            transform( 0.8, 0.4,  1.0),
            transform(-0.8, 0.4,  1.0),
        ]
        draw_polygon_3d(img, p_chassis, (40, 48, 58), (46, 204, 113))

        # Battery Pack
        p_batt = [
            transform(-0.5, 0.7, -0.6),
            transform( 0.5, 0.7, -0.6),
            transform( 0.5, 0.7,  0.1),
            transform(-0.5, 0.7,  0.1),
        ]
        draw_polygon_3d(img, p_batt, (180, 80, 20), (220, 120, 40))

        # L298N Motor Driver (Red Module)
        p_l298n = [
            transform(-0.4, 0.65, 0.15),
            transform( 0.4, 0.65, 0.15),
            transform( 0.4, 0.65, 0.65),
            transform(-0.4, 0.65, 0.65),
        ]
        draw_polygon_3d(img, p_l298n, (35, 35, 180), (50, 50, 230))

        # Camera Mast & Lens
        mast_b = transform(0, 0.4, 0.85)
        mast_t = transform(0, 1.1, 0.85)
        cv2.line(img, project_3d(*mast_b), project_3d(*mast_t), (150, 150, 150), 4)
        lens_p = project_3d(*mast_t)
        cv2.circle(img, lens_p, 10, (20, 20, 20), -1)
        cv2.circle(img, lens_p, 10, (46, 204, 113), 2)
        cv2.circle(img, lens_p, 4, (0, 165, 255), -1)

        # 4 Yellow DC Gear Motors & Rubber Wheels
        wheels_rel = [
            (-0.95, 0.25,  0.65), # FL
            (-0.95, 0.25, -0.65), # RL
            ( 0.95, 0.25,  0.65), # FR
            ( 0.95, 0.25, -0.65), # RR
        ]
        for wx, wy, wz in wheels_rel:
            p_center = transform(wx, wy, wz)
            px, py = project_3d(*p_center)
            # Motor body (yellow)
            cv2.rectangle(img, (px - 14, py - 10), (px + 14, py + 10), (0, 215, 255), -1)
            # Tire (dark rubber)
            tire_col = (46, 204, 113) if (left_pwm != 0 or right_pwm != 0) else (60, 60, 60)
            cv2.circle(img, (px, py), 16, (25, 25, 25), -1)
            cv2.circle(img, (px, py), 16, tire_col, 3)

        # 3. CHEMICAL SPRAY PARTICLES
        if spray_active:
            # Emit new particles
            for _ in range(8):
                sp_speed = 0.08 + np.random.rand() * 0.04
                sp_angle = rh + (np.random.rand() - 0.5) * 0.4
                particles.append({
                    'x': rx + math.sin(rh) * 0.9,
                    'y': 0.5 + (np.random.rand() - 0.5) * 0.1,
                    'z': rz + math.cos(rh) * 0.9,
                    'vx': math.sin(sp_angle) * sp_speed,
                    'vy': -0.015 - np.random.rand() * 0.01,
                    'vz': math.cos(sp_angle) * sp_speed,
                    'life': 1.0
                })
        
        # Update and draw particles
        active_particles = []
        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz']
            p['life'] -= 0.04
            if p['life'] > 0 and p['y'] > 0:
                sx, sy = project_3d(p['x'], p['y'], p['z'])
                size = max(2, int(p['life'] * 6))
                cv2.circle(img, (sx, sy), size, (255, 191, 0), -1) # Blue chemical mist
                active_particles.append(p)
        particles = active_particles

        # -------------------------------------------------------------
        # RIGHT PANEL: MOBILE TELEOPERATION APP COCKPIT (SPLIT SCREEN)
        # -------------------------------------------------------------
        app_x = 940
        app_y = 20
        app_w = 320
        app_h = 680
        
        # Phone body
        cv2.rectangle(img, (app_x, app_y), (app_x + app_w, app_y + app_h), (25, 33, 44), -1)
        cv2.rectangle(img, (app_x, app_y), (app_x + app_w, app_y + app_h), (46, 204, 113), 2)
        
        # Phone Header
        cv2.putText(img, "AGRI ROVER TELEOP", (app_x + 55, app_y + 30), cv2.FONT_HERSHEY_DUPLEX, 0.6, (46, 204, 113), 1)
        cv2.putText(img, "Wi-Fi: 192.168.4.1 [CONNECTED]", (app_x + 35, app_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # 60% LIVE CAMERA VIEWPORT OVERLAY
        cam_h = 240
        cv2.rectangle(img, (app_x + 15, app_y + 65), (app_x + app_w - 15, app_y + 65 + cam_h), (0, 0, 0), -1)
        cv2.rectangle(img, (app_x + 15, app_y + 65), (app_x + app_w - 15, app_y + 65 + cam_h), (70, 80, 95), 1)
        
        # Simulated POV crop view
        cv2.putText(img, "ESP32-CAM (OV2640 LIVE)", (app_x + 25, app_y + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (46, 204, 113), 1)
        cv2.putText(img, "25 FPS | 640x480 VGA", (app_x + 25, app_y + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # Crosshair in camera
        cv2.drawMarker(img, (app_x + 160, app_y + 185), (0, 255, 0), cv2.MARKER_CROSS, 24, 2)
        if spray_active:
            cv2.circle(img, (app_x + 160, app_y + 185), 35, (0, 0, 255), 2)
            cv2.putText(img, "TARGET LOCKED: WEED", (app_x + 50, app_y + 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 40% CONTROL SECTION: JOYSTICK & BUTTONS
        joy_cx = app_x + 160
        joy_cy = app_y + 380
        # Base
        cv2.circle(img, (joy_cx, joy_cy), 55, (40, 50, 65), -1)
        cv2.circle(img, (joy_cx, joy_cy), 55, (70, 85, 105), 2)
        # Thumbstick knob
        knob_x = int(joy_cx + joy_x)
        knob_y = int(joy_cy + joy_y)
        cv2.circle(img, (knob_x, knob_y), 24, (46, 204, 113), -1)
        cv2.circle(img, (knob_x, knob_y), 24, (255, 255, 255), 2)
        
        # SPEED PRESETS (SLOW / MED / FAST)
        presets = ["SLOW 35%", "MED 65%", "FAST 100%"]
        for idx, p_name in enumerate(presets):
            bx = app_x + 20 + idx * 95
            by = app_y + 460
            is_active = (idx == 1 and speed_mode == "MED 65%")
            bg_col = (46, 204, 113) if is_active else (35, 45, 58)
            txt_col = (0, 0, 0) if is_active else (180, 190, 200)
            cv2.rectangle(img, (bx, by), (bx + 85, by + 32), bg_col, -1)
            cv2.rectangle(img, (bx, by), (bx + 85, by + 32), (60, 75, 95), 1)
            cv2.putText(img, p_name, (bx + 8, by + 21), cv2.FONT_HERSHEY_SIMPLEX, 0.38, txt_col, 1)

        # SPRAY BURST BUTTON (TACTICAL BLUE)
        spray_bg = (235, 75, 50) if spray_active else (180, 100, 30)
        cv2.rectangle(img, (app_x + 20, app_y + 510), (app_x + app_w - 20, app_y + 555), spray_bg, -1)
        cv2.putText(img, "CHEMICAL SPRAY BURST (200ms)", (app_x + 35, app_y + 538), cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1)
        
        # EMERGENCY STOP
        cv2.rectangle(img, (app_x + 20, app_y + 570), (app_x + app_w - 20, app_y + 610), (40, 40, 200), -1)
        cv2.putText(img, "EMERGENCY BRAKE (STOP)", (app_x + 60, app_y + 595), cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1)

        # -------------------------------------------------------------
        # BOTTOM-LEFT HUD: LOGIC ANALYZER & FIRMWARE NETLIST STATUS
        # -------------------------------------------------------------
        hud_x = 30
        hud_y = 520
        cv2.rectangle(img, (hud_x, hud_y), (hud_x + 620, hud_y + 175), (15, 20, 28), -1)
        cv2.rectangle(img, (hud_x, hud_y), (hud_x + 620, hud_y + 175), (35, 48, 65), 1)
        
        cv2.putText(img, "LOGIC ANALYZER & ESP32-CAM GPIO STATUS (AgriRover_ESP32CAM.ino)", (hud_x + 15, hud_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.45, (46, 204, 113), 1)
        
        # GPIO 14 (IN1 - Left Fwd)
        col_14 = (46, 204, 113) if left_pwm > 0 else (100, 110, 120)
        cv2.putText(img, f"GPIO 14 [IN1 Left Fwd]:  {max(0, left_pwm)} PWM", (hud_x + 15, hud_y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col_14, 1)
        
        # GPIO 15 (IN2 - Left Rev)
        col_15 = (46, 204, 113) if left_pwm < 0 else (100, 110, 120)
        cv2.putText(img, f"GPIO 15 [IN2 Left Rev]:  {abs(min(0, left_pwm))} PWM", (hud_x + 15, hud_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col_15, 1)
        
        # GPIO 13 (IN3 - Right Fwd)
        col_13 = (46, 204, 113) if right_pwm > 0 else (100, 110, 120)
        cv2.putText(img, f"GPIO 13 [IN3 Right Fwd]: {max(0, right_pwm)} PWM", (hud_x + 320, hud_y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col_13, 1)
        
        # GPIO 12 (IN4 - Right Rev)
        col_12 = (46, 204, 113) if right_pwm < 0 else (100, 110, 120)
        cv2.putText(img, f"GPIO 12 [IN4 Right Rev]: {abs(min(0, right_pwm))} PWM", (hud_x + 320, hud_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col_12, 1)

        # GPIO 2 (Relay Pump)
        col_2 = (0, 0, 255) if spray_active else (100, 110, 120)
        status_2 = "HIGH (PUMP ON)" if spray_active else "LOW (PUMP OFF)"
        cv2.putText(img, f"GPIO 2  [RELAY PUMP]:    {status_2}", (hud_x + 15, hud_y + 115), cv2.FONT_HERSHEY_SIMPLEX, 0.48, col_2, 1)

        # Power Rail & Watchdog status
        cv2.putText(img, "Buck Output: +5.10V DC | Battery: 12.2V | Watchdog Failsafe: 500ms Active", (hud_x + 15, hud_y + 150), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        # -------------------------------------------------------------
        # TOP BANNER: ACTIVE FLIGHT PHASE TITLE
        # -------------------------------------------------------------
        cv2.rectangle(img, (30, 20), (880, 65), (15, 20, 28), -1)
        cv2.rectangle(img, (30, 20), (880, 65), (46, 204, 113), 2)
        cv2.putText(img, phase_title, (45, 50), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)
        
        out.write(img)
        
        # Keep sample frames for animated GIF (sample every 3rd frame to keep GIF compact)
        if frame_idx % 3 == 0:
            small = cv2.resize(img, (640, 360))
            gif_frames.append(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
            
    out.release()
    print(f"[SUCCESS] 3D Simulation MP4 Video saved to: {video_path}")
    
    # Save GIF using PIL
    print(f"[INFO] Compiling animated GIF preview ({len(gif_frames)} frames)...")
    from PIL import Image
    pil_images = [Image.fromarray(f) for f in gif_frames]
    pil_images[0].save(
        gif_path,
        save_all=True,
        append_images=pil_images[1:],
        duration=int(1000 / (FPS / 3)),
        loop=0
    )
    print(f"[SUCCESS] Animated GIF saved to: {gif_path}")

if __name__ == "__main__":
    generate_video()
