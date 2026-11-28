package com.agrirover.teleop;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Manages persistent configuration and kinematics tuning parameters
 * for Agri Rover teleoperation.
 */
public class RoverConfig {

    private static final String PREFS_NAME = "agrirover_prefs_v2";

    public static final String KEY_HOST = "cfg_host";
    public static final String KEY_CTRL_PORT = "cfg_ctrl_port";
    public static final String KEY_STREAM_PORT = "cfg_stream_port";
    public static final String KEY_SPRAY_MS = "cfg_spray_ms";
    public static final String KEY_TURN_SENS = "cfg_turn_sens";
    public static final String KEY_STEERING_TRIM = "cfg_steering_trim";
    public static final String KEY_INVERT_THROTTLE = "cfg_invert_throttle";
    public static final String KEY_INVERT_STEER = "cfg_invert_steer";
    public static final String KEY_DEADZONE = "cfg_deadzone";
    public static final String KEY_PROBE_THRESHOLD = "cfg_probe_threshold";
    public static final String KEY_RELAY_POLARITY = "cfg_relay_polarity";
    public static final String KEY_MIRROR_STREAM = "cfg_mirror_stream";

    // Defaults matching firmware
    public static final String DEFAULT_HOST = "192.168.4.1";
    public static final int DEFAULT_CTRL_PORT = 80;
    public static final int DEFAULT_STREAM_PORT = 81;
    public static final int DEFAULT_SPRAY_MS = 200;
    public static final float DEFAULT_TURN_SENS = 0.75f;
    public static final int DEFAULT_STEERING_TRIM = 0;
    public static final boolean DEFAULT_INVERT_THROTTLE = false;
    public static final boolean DEFAULT_INVERT_STEER = false;
    public static final float DEFAULT_DEADZONE = 0.08f;
    public static final int DEFAULT_PROBE_THRESHOLD = 35;
    public static final String DEFAULT_RELAY_POLARITY = "high"; // "high" or "low"
    public static final boolean DEFAULT_MIRROR_STREAM = false;

    private final SharedPreferences prefs;

    public RoverConfig(Context context) {
        this.prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public String getHost() {
        return prefs.getString(KEY_HOST, DEFAULT_HOST);
    }

    public void setHost(String host) {
        prefs.edit().putString(KEY_HOST, host != null && !host.trim().isEmpty() ? host.trim() : DEFAULT_HOST).apply();
    }

    public int getCtrlPort() {
        return prefs.getInt(KEY_CTRL_PORT, DEFAULT_CTRL_PORT);
    }

    public void setCtrlPort(int port) {
        prefs.edit().putInt(KEY_CTRL_PORT, port > 0 ? port : DEFAULT_CTRL_PORT).apply();
    }

    public int getStreamPort() {
        return prefs.getInt(KEY_STREAM_PORT, DEFAULT_STREAM_PORT);
    }

    public void setStreamPort(int port) {
        prefs.edit().putInt(KEY_STREAM_PORT, port > 0 ? port : DEFAULT_STREAM_PORT).apply();
    }

    public int getSprayMs() {
        return prefs.getInt(KEY_SPRAY_MS, DEFAULT_SPRAY_MS);
    }

    public void setSprayMs(int ms) {
        prefs.edit().putInt(KEY_SPRAY_MS, Math.max(50, Math.min(5000, ms))).apply();
    }

    public float getTurnSensitivity() {
        return prefs.getFloat(KEY_TURN_SENS, DEFAULT_TURN_SENS);
    }

    public void setTurnSensitivity(float sens) {
        prefs.edit().putFloat(KEY_TURN_SENS, Math.max(0.30f, Math.min(1.20f, sens))).apply();
    }

    public int getSteeringTrim() {
        return prefs.getInt(KEY_STEERING_TRIM, DEFAULT_STEERING_TRIM);
    }

    public void setSteeringTrim(int trim) {
        prefs.edit().putInt(KEY_STEERING_TRIM, Math.max(-25, Math.min(25, trim))).apply();
    }

    public boolean isInvertThrottle() {
        return prefs.getBoolean(KEY_INVERT_THROTTLE, DEFAULT_INVERT_THROTTLE);
    }

    public void setInvertThrottle(boolean invert) {
        prefs.edit().putBoolean(KEY_INVERT_THROTTLE, invert).apply();
    }

    public boolean isInvertSteer() {
        return prefs.getBoolean(KEY_INVERT_STEER, DEFAULT_INVERT_STEER);
    }

    public void setInvertSteer(boolean invert) {
        prefs.edit().putBoolean(KEY_INVERT_STEER, invert).apply();
    }

    public int getProbeThreshold() {
        return prefs.getInt(KEY_PROBE_THRESHOLD, DEFAULT_PROBE_THRESHOLD);
    }

    public void setProbeThreshold(int threshold) {
        prefs.edit().putInt(KEY_PROBE_THRESHOLD, Math.max(10, Math.min(80, threshold))).apply();
    }

    public String getRelayPolarity() {
        return prefs.getString(KEY_RELAY_POLARITY, DEFAULT_RELAY_POLARITY);
    }

    public void setRelayPolarity(String polarity) {
        prefs.edit().putString(KEY_RELAY_POLARITY, "low".equalsIgnoreCase(polarity) ? "low" : "high").apply();
    }

    public boolean isMirrorStream() {
        return prefs.getBoolean(KEY_MIRROR_STREAM, DEFAULT_MIRROR_STREAM);
    }

    public void setMirrorStream(boolean mirror) {
        prefs.edit().putBoolean(KEY_MIRROR_STREAM, mirror).apply();
    }

    public float getDeadzone() {
        return prefs.getFloat(KEY_DEADZONE, DEFAULT_DEADZONE);
    }

    public String getStreamUrl() {
        return "http://" + getHost() + ":" + getStreamPort() + "/stream";
    }

    public String getFallbackStreamUrl() {
        return "http://" + getHost() + ":" + getCtrlPort() + "/stream";
    }

    public String getControlBaseUrl() {
        return "http://" + getHost() + ":" + getCtrlPort();
    }

    public void resetDefaults() {
        prefs.edit().clear().apply();
    }
}
