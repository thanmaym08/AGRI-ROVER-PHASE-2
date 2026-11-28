package com.agrirover.teleop;

/**
 * Shared differential skid-steer kinematics solver across all 3 control modes
 * (Dual Thumbs, Single Stick, D-Pad).
 */
public class KinematicsHelper {

    public static class MotionResult {
        public final int leftPwm;
        public final int rightPwm;
        public final String vectorText;

        public MotionResult(int leftPwm, int rightPwm, String vectorText) {
            this.leftPwm = leftPwm;
            this.rightPwm = rightPwm;
            this.vectorText = vectorText;
        }
    }

    public static MotionResult compute(float rawThrottle, float rawSteer, int speedPercent, RoverConfig config) {
        float throttle = rawThrottle;
        float steer = rawSteer;

        float deadzone = config != null ? config.getDeadzone() : RoverConfig.DEFAULT_DEADZONE;
        boolean invThrottle = config != null && config.isInvertThrottle();
        boolean invSteer = config != null && config.isInvertSteer();
        float turnSens = config != null ? config.getTurnSensitivity() : RoverConfig.DEFAULT_TURN_SENS;
        int trim = config != null ? config.getSteeringTrim() : RoverConfig.DEFAULT_STEERING_TRIM;

        if (invThrottle) throttle = -throttle;
        if (invSteer) steer = -steer;

        float magnitude = (float) Math.hypot(throttle, steer);
        if (magnitude < deadzone) {
            throttle = 0f;
            steer = 0f;
        }

        // Differential Skid-Steer Mixer
        float scaledSteer = steer * turnSens;
        float left = throttle + scaledSteer;
        float right = throttle - scaledSteer;

        // Straight-line Motor Drift Trim
        if (trim != 0 && Math.abs(throttle) > 0.05f) {
            float trimFactor = trim / 100f;
            if (trimFactor > 0) {
                right *= (1f - trimFactor);
            } else {
                left *= (1f + trimFactor);
            }
        }

        int maxPwm = Math.round((speedPercent / 100f) * 255f);
        int leftPwm = Math.max(-255, Math.min(255, Math.round(left * maxPwm)));
        int rightPwm = Math.max(-255, Math.min(255, Math.round(right * maxPwm)));

        String vectorText = formatVector(leftPwm, rightPwm, throttle, steer, speedPercent);
        return new MotionResult(leftPwm, rightPwm, vectorText);
    }

    private static String formatVector(int leftPwm, int rightPwm, float throttle, float steer, int speedPercent) {
        if (leftPwm == 0 && rightPwm == 0) {
            return "■ STOPPED";
        }
        float absThrot = Math.abs(throttle);
        float absSteer = Math.abs(steer);

        if (throttle > 0.15f && absSteer <= 0.25f) {
            return "▲ FWD " + speedPercent + "%";
        } else if (throttle < -0.15f && absSteer <= 0.25f) {
            return "▼ REV " + speedPercent + "%";
        } else if (steer > 0.25f && absThrot <= 0.25f) {
            return "► PIVOT R";
        } else if (steer < -0.25f && absThrot <= 0.25f) {
            return "◄ PIVOT L";
        } else if (throttle > 0.15f && steer > 0.25f) {
            return "⮡ CURVE R";
        } else if (throttle > 0.15f && steer < -0.25f) {
            return "⮢ CURVE L";
        } else if (throttle < -0.15f && steer > 0.25f) {
            return "⮣ REV R";
        } else if (throttle < -0.15f && steer < -0.25f) {
            return "⮠ REV L";
        }
        return "● ACTIVE " + speedPercent + "%";
    }
}
