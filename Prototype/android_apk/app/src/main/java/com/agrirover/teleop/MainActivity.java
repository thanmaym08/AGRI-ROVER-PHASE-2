package com.agrirover.teleop;

import android.annotation.SuppressLint;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Vibrator;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.util.Locale;

/**
 * Premium Mars Rover Teleoperation & Robotics Telematics Application.
 * Unifies Home/Discover, Remote Control Cockpit, Subsoil Intelligence, and Settings.
 */
public class MainActivity extends AppCompatActivity implements
        MjpegStreamer.StreamListener,
        JoystickView.JoystickListener {

    public static final String MODE_DUAL_THUMBS = "DUAL_THUMBS";
    public static final String MODE_SINGLE_STICK = "SINGLE_STICK";
    public static final String MODE_DPAD = "DPAD";

    public static final int TAB_HOME = 0;
    public static final int TAB_REMOTE = 1;
    public static final int TAB_INTELLIGENCE = 2;
    public static final int TAB_SETTINGS = 3;

    private int activeTab = TAB_HOME;
    private String activeMode = MODE_SINGLE_STICK;

    // Core Subsystems
    private RoverConfig config;
    private RoverApiClient apiClient;
    private MjpegStreamer streamer;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private Vibrator vibrator;

    // Top Status Bar
    private TextView tvTopStatusBadge;
    private TextView tvTopPing;
    private TextView tvTopBattery;

    // Content Containers
    private ScrollView sectionHome;
    private LinearLayout sectionRemote;
    private ScrollView sectionIntelligence;
    private ScrollView sectionSettings;

    // Bottom Navigation Elements
    private LinearLayout navTabHome, navTabRemote, navTabIntelligence, navTabSettings;
    private ImageView ivNavHome, ivNavRemote, ivNavIntelligence, ivNavSettings;
    private TextView tvNavHome, tvNavRemote, tvNavIntelligence, tvNavSettings;

    // Home Section Views
    private TextView tvHomeIp, tvHomeSoilVal, tvHomeSoilDesc, tvHomeMotionTag;
    private Button btnHomeStartControl;
    private LinearLayout cardHomeSoil, cardHomeModeDual, cardHomeModeSingle, cardHomeModeDpad;

    // Remote Section Views
    private ImageView ivCameraStream;
    private View layoutStreamPlaceholder;
    private TextView tvStreamStatus, tvHudFps, tvHudMotionVector, tvSprayAlertBanner, tvProbeMoistureVal;
    private Button btnRetryStream, btnRotateStream;
    private LinearLayout leftSidePanel, rightSidePanel, singleStickBottomPanel;
    private LinearLayout leftDualControls, rightDualControls, leftDpadControls, rightDpadControls;

    // Dual Thumbs Controls
    private AxisSliderView sliderThrottle, sliderSteering;
    private TextView tvDualSpeedVal;
    private Button btnDualSpeed35, btnDualSpeed65, btnDualSpeed100;
    private Button btnDualSpray, btnDualSpray05, btnDualSpray10, btnDualSpray20;

    // Single Stick Controls
    private JoystickView joystickView;
    private TextView tvSingleSpeedVal;
    private Button btnSingleSpeed35, btnSingleSpeed65, btnSingleSpeed100;
    private Button btnSingleSpray, btnSingleSpray05, btnSingleSpray10, btnSingleSpray20;
    private Button btnSingleFlash, btnSingleProbe, btnSingleCalib, btnSingleEstop;

    // Shared & Side Controls
    private Button btnSideFlash, btnSideProbe, btnSideEstop;
    private Button btnModeDualThumbs, btnModeSingleStick, btnModeDpad;
    private SeekBar sbSpeed;

    // Intelligence Section Views
    private TextView tvIntelMoistureLarge, tvIntelStatusBadge;
    private Button btnIntelTriggerProbe;

    // Settings Section Views
    private SeekBar sbSettingsProbeThreshold, sbSettingsTurnSens, sbSettingsTrim;
    private TextView tvSettingsProbeThresholdVal, tvSettingsTurnSensVal, tvSettingsTrimVal;
    private CheckBox cbSettingsInvertThrottle, cbSettingsInvertSteer, cbSettingsMirrorStream, cbSettingsRelayActiveLow;
    private EditText etSettingsHost, etSettingsCtrlPort, etSettingsStreamPort, etSettingsSprayMs;
    private Button btnSettingsReset, btnSettingsSave;
    private Button btnBenchTestLeft, btnBenchTestRight, btnBenchTestBoth, btnBenchPrimePump;
    private boolean isPumpPriming = false;

    // State Variables
    private int currentSpeed = 65;
    private int currentSprayMs = 1000;
    private int flashBrightness = 0;
    private int streamRotationDeg = 0;
    private boolean isSprayActive = false;
    private boolean isProbing = false;
    private int lastReportedMoisture = -1;

    // D-Pad Touch State
    private float dpadThrottle = 0f;
    private float dpadSteer = 0f;
    private long lastAxisDispatchTime = 0;

    // Periodic Loops
    private final Runnable pingRunnable = new Runnable() {
        @Override
        public void run() {
            if (apiClient != null) {
                apiClient.ping((success, latencyMs) -> updateConnectionStatus(success, latencyMs));
            }
            mainHandler.postDelayed(this, 1500);
        }
    };

    private final Runnable dpadDispatchLoop = new Runnable() {
        @Override
        public void run() {
            if (LandingActivity.MODE_DPAD.equals(activeMode) && (dpadThrottle != 0f || dpadSteer != 0f)) {
                dispatchAxisKinematics(dpadThrottle, dpadSteer);
                mainHandler.postDelayed(this, 60);
            }
        }
    };

    private final Runnable probePollRunnable = new Runnable() {
        @Override
        public void run() {
            if (!isProbing || apiClient == null) return;
            apiClient.getProbeStatus(new RoverApiClient.ProbeCallback() {
                @Override
                public void onStatus(RoverApiClient.ProbeStatus status) {
                    if (status == null) {
                        isProbing = true;
                        tvProbeMoistureVal.setText("Soil status unavailable • drive locked");
                        tvProbeMoistureVal.setTextColor(Color.parseColor("#D97706"));
                        mainHandler.postDelayed(probePollRunnable, 1000);
                        return;
                    }
                    updateProbeUI(status);
                    if (!status.idle) {
                        mainHandler.postDelayed(probePollRunnable, 500);
                    } else {
                        isProbing = false;
                    }
                }

                @Override
                public void onError(String errorMessage) {
                    // A lost status response does not prove that the physical probe is stowed.
                    // Keep the drive interlock asserted and retry until firmware confirms idle.
                    isProbing = true;
                    tvProbeMoistureVal.setText("Soil status unavailable • drive locked");
                    tvProbeMoistureVal.setTextColor(Color.parseColor("#D97706"));
                    mainHandler.postDelayed(probePollRunnable, 1000);
                }
            });
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.activity_main);

        vibrator = (Vibrator) getSystemService(VIBRATOR_SERVICE);
        config = new RoverConfig(this);
        apiClient = new RoverApiClient(config);
        streamer = new MjpegStreamer(config, this);

        initViews();
        setupListeners();
        setupSettingsTabValues();

        // Default to Home Tab & Single Stick Architecture
        switchNavigationTab(TAB_HOME);
        switchControlMode(MODE_SINGLE_STICK);
        applySpeed(currentSpeed);
        applySprayDuration(currentSprayMs);

        mainHandler.post(pingRunnable);
    }

    private void initViews() {
        // Top Bar
        tvTopStatusBadge = findViewById(R.id.tv_top_status_badge);
        tvTopPing = findViewById(R.id.tv_top_ping);
        tvTopBattery = findViewById(R.id.tv_top_battery);

        // Sections
        sectionHome = findViewById(R.id.section_home);
        sectionRemote = findViewById(R.id.section_remote);
        sectionIntelligence = findViewById(R.id.section_intelligence);
        sectionSettings = findViewById(R.id.section_settings);

        // Bottom Nav Tabs
        navTabHome = findViewById(R.id.nav_tab_home);
        navTabRemote = findViewById(R.id.nav_tab_remote);
        navTabIntelligence = findViewById(R.id.nav_tab_intelligence);
        navTabSettings = findViewById(R.id.nav_tab_settings);

        ivNavHome = findViewById(R.id.iv_nav_home);
        ivNavRemote = findViewById(R.id.iv_nav_remote);
        ivNavIntelligence = findViewById(R.id.iv_nav_intelligence);
        ivNavSettings = findViewById(R.id.iv_nav_settings);

        tvNavHome = findViewById(R.id.tv_nav_home);
        tvNavRemote = findViewById(R.id.tv_nav_remote);
        tvNavIntelligence = findViewById(R.id.tv_nav_intelligence);
        tvNavSettings = findViewById(R.id.tv_nav_settings);

        // Home Section
        tvHomeIp = findViewById(R.id.tv_home_ip);
        tvHomeSoilVal = findViewById(R.id.tv_home_soil_val);
        tvHomeSoilDesc = findViewById(R.id.tv_home_soil_desc);
        tvHomeMotionTag = findViewById(R.id.tv_home_motion_tag);
        btnHomeStartControl = findViewById(R.id.btn_home_start_control);
        cardHomeSoil = findViewById(R.id.card_home_soil);
        cardHomeModeDual = findViewById(R.id.card_home_mode_dual);
        cardHomeModeSingle = findViewById(R.id.card_home_mode_single);
        cardHomeModeDpad = findViewById(R.id.card_home_mode_dpad);

        // Remote Section
        ivCameraStream = findViewById(R.id.iv_camera_stream);
        layoutStreamPlaceholder = findViewById(R.id.layout_stream_placeholder);
        tvStreamStatus = findViewById(R.id.tv_stream_status);
        tvHudFps = findViewById(R.id.tv_hud_fps);
        tvHudMotionVector = findViewById(R.id.tv_hud_motion_vector);
        tvSprayAlertBanner = findViewById(R.id.tv_spray_alert_banner);
        tvProbeMoistureVal = findViewById(R.id.tv_probe_moisture_val);
        btnRetryStream = findViewById(R.id.btn_retry_stream);
        btnRotateStream = findViewById(R.id.btn_rotate_stream);

        leftSidePanel = findViewById(R.id.left_side_panel);
        rightSidePanel = findViewById(R.id.right_side_panel);
        singleStickBottomPanel = findViewById(R.id.single_stick_bottom_panel);
        leftDualControls = findViewById(R.id.left_dual_controls);
        rightDualControls = findViewById(R.id.right_dual_controls);
        leftDpadControls = findViewById(R.id.left_dpad_controls);
        rightDpadControls = findViewById(R.id.right_dpad_controls);

        sliderThrottle = findViewById(R.id.slider_throttle);
        sliderSteering = findViewById(R.id.slider_steering);
        sliderSteering.configure(AxisSliderView.ORIENTATION_HORIZONTAL, Color.parseColor("#FF6F59"), "R", "L");

        tvDualSpeedVal = findViewById(R.id.tv_dual_speed_val);
        btnDualSpeed35 = findViewById(R.id.btn_dual_speed_35);
        btnDualSpeed65 = findViewById(R.id.btn_dual_speed_65);
        btnDualSpeed100 = findViewById(R.id.btn_dual_speed_100);
        btnDualSpray = findViewById(R.id.btn_dual_spray);
        btnDualSpray05 = findViewById(R.id.btn_dual_spray_05);
        btnDualSpray10 = findViewById(R.id.btn_dual_spray_10);
        btnDualSpray20 = findViewById(R.id.btn_dual_spray_20);

        joystickView = findViewById(R.id.joystick_view);
        joystickView.setConfig(config);
        joystickView.setListener(this);

        tvSingleSpeedVal = findViewById(R.id.tv_single_speed_val);
        btnSingleSpeed35 = findViewById(R.id.btn_single_speed_35);
        btnSingleSpeed65 = findViewById(R.id.btn_single_speed_65);
        btnSingleSpeed100 = findViewById(R.id.btn_single_speed_100);
        btnSingleSpray = findViewById(R.id.btn_single_spray);
        btnSingleSpray05 = findViewById(R.id.btn_single_spray_05);
        btnSingleSpray10 = findViewById(R.id.btn_single_spray_10);
        btnSingleSpray20 = findViewById(R.id.btn_single_spray_20);

        btnSingleFlash = findViewById(R.id.btn_single_flash);
        btnSingleProbe = findViewById(R.id.btn_single_probe);
        btnSingleCalib = findViewById(R.id.btn_single_calib);
        btnSingleEstop = findViewById(R.id.btn_single_estop);

        btnSideFlash = findViewById(R.id.btn_side_flash);
        btnSideProbe = findViewById(R.id.btn_side_probe);
        btnSideEstop = findViewById(R.id.btn_side_estop);

        btnModeDualThumbs = findViewById(R.id.btn_mode_dual_thumbs);
        btnModeSingleStick = findViewById(R.id.btn_mode_single_stick);
        btnModeDpad = findViewById(R.id.btn_mode_dpad);
        sbSpeed = findViewById(R.id.sb_speed);

        // Intelligence Section
        tvIntelMoistureLarge = findViewById(R.id.tv_intel_moisture_large);
        tvIntelStatusBadge = findViewById(R.id.tv_intel_status_badge);
        btnIntelTriggerProbe = findViewById(R.id.btn_intel_trigger_probe);

        // Settings Section
        sbSettingsProbeThreshold = findViewById(R.id.sb_settings_probe_threshold);
        tvSettingsProbeThresholdVal = findViewById(R.id.tv_settings_probe_threshold_val);
        sbSettingsTurnSens = findViewById(R.id.sb_settings_turn_sens);
        tvSettingsTurnSensVal = findViewById(R.id.tv_settings_turn_sens_val);
        sbSettingsTrim = findViewById(R.id.sb_settings_trim);
        tvSettingsTrimVal = findViewById(R.id.tv_settings_trim_val);
        cbSettingsInvertThrottle = findViewById(R.id.cb_settings_invert_throttle);
        cbSettingsInvertSteer = findViewById(R.id.cb_settings_invert_steer);
        cbSettingsMirrorStream = findViewById(R.id.cb_settings_mirror_stream);
        cbSettingsRelayActiveLow = findViewById(R.id.cb_settings_relay_active_low);
        etSettingsHost = findViewById(R.id.et_settings_host);
        etSettingsCtrlPort = findViewById(R.id.et_settings_ctrl_port);
        etSettingsStreamPort = findViewById(R.id.et_settings_stream_port);
        etSettingsSprayMs = findViewById(R.id.et_settings_spray_ms);
        btnSettingsReset = findViewById(R.id.btn_settings_reset);
        btnSettingsSave = findViewById(R.id.btn_settings_save);

        // Hardware Bench Diagnostics Views
        btnBenchTestLeft = findViewById(R.id.btn_bench_test_left);
        btnBenchTestRight = findViewById(R.id.btn_bench_test_right);
        btnBenchTestBoth = findViewById(R.id.btn_bench_test_both);
        btnBenchPrimePump = findViewById(R.id.btn_bench_prime_pump);
    }

    @SuppressLint("ClickableViewAccessibility")
    private void setupListeners() {
        // Bottom Navigation Bar
        navTabHome.setOnClickListener(v -> switchNavigationTab(TAB_HOME));
        navTabRemote.setOnClickListener(v -> switchNavigationTab(TAB_REMOTE));
        navTabIntelligence.setOnClickListener(v -> switchNavigationTab(TAB_INTELLIGENCE));
        navTabSettings.setOnClickListener(v -> switchNavigationTab(TAB_SETTINGS));

        // Home Actions
        btnHomeStartControl.setOnClickListener(v -> switchNavigationTab(TAB_REMOTE));
        cardHomeSoil.setOnClickListener(v -> switchNavigationTab(TAB_INTELLIGENCE));
        cardHomeModeDual.setOnClickListener(v -> {
            switchControlMode(MODE_DUAL_THUMBS);
            switchNavigationTab(TAB_REMOTE);
        });
        cardHomeModeSingle.setOnClickListener(v -> {
            switchControlMode(MODE_SINGLE_STICK);
            switchNavigationTab(TAB_REMOTE);
        });
        cardHomeModeDpad.setOnClickListener(v -> {
            switchControlMode(MODE_DPAD);
            switchNavigationTab(TAB_REMOTE);
        });

        // Remote Camera Controls
        btnRetryStream.setOnClickListener(v -> {
            tvStreamStatus.setText("Reconnecting...");
            streamer.restart();
        });
        btnRotateStream.setOnClickListener(v -> {
            streamRotationDeg = (streamRotationDeg + 90) % 360;
            btnRotateStream.setText(String.format(Locale.US, "ROTATE %d°", streamRotationDeg));
            if (ivCameraStream != null) {
                ivCameraStream.setRotation(streamRotationDeg);
            }
        });

        // Driving Modes
        btnModeDualThumbs.setOnClickListener(v -> switchControlMode(MODE_DUAL_THUMBS));
        btnModeSingleStick.setOnClickListener(v -> switchControlMode(MODE_SINGLE_STICK));
        btnModeDpad.setOnClickListener(v -> switchControlMode(MODE_DPAD));

        // Speed Controls
        btnDualSpeed35.setOnClickListener(v -> applySpeed(35));
        btnDualSpeed65.setOnClickListener(v -> applySpeed(65));
        btnDualSpeed100.setOnClickListener(v -> applySpeed(100));
        btnSingleSpeed35.setOnClickListener(v -> applySpeed(35));
        btnSingleSpeed65.setOnClickListener(v -> applySpeed(65));
        btnSingleSpeed100.setOnClickListener(v -> applySpeed(100));

        sbSpeed.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (fromUser) applySpeed(Math.max(25, progress));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Spray Controls
        btnDualSpray.setOnClickListener(v -> triggerChemicalSpray());
        btnSingleSpray.setOnClickListener(v -> triggerChemicalSpray());
        btnDualSpray05.setOnClickListener(v -> applySprayDuration(500));
        btnDualSpray10.setOnClickListener(v -> applySprayDuration(1000));
        btnDualSpray20.setOnClickListener(v -> applySprayDuration(2000));
        btnSingleSpray05.setOnClickListener(v -> applySprayDuration(500));
        btnSingleSpray10.setOnClickListener(v -> applySprayDuration(1000));
        btnSingleSpray20.setOnClickListener(v -> applySprayDuration(2000));

        // Auxiliary Utilities
        btnSideFlash.setOnClickListener(v -> toggleFlash());
        btnSingleFlash.setOnClickListener(v -> toggleFlash());
        btnSideProbe.setOnClickListener(v -> triggerSoilProbe());
        btnSingleProbe.setOnClickListener(v -> triggerSoilProbe());
        btnSingleCalib.setOnClickListener(v -> switchNavigationTab(TAB_SETTINGS));
        btnSideEstop.setOnClickListener(v -> emergencyStop());
        btnSingleEstop.setOnClickListener(v -> emergencyStop());
        tvProbeMoistureVal.setOnClickListener(v -> switchNavigationTab(TAB_INTELLIGENCE));

        // Axis Sliders
        AxisSliderView.AxisListener dualAxisListener = val ->
                dispatchAxisKinematics(sliderThrottle.getValue(), sliderSteering.getValue());
        sliderThrottle.setListener(dualAxisListener);
        sliderSteering.setListener(dualAxisListener);

        // D-Pad Touch Listeners
        bindDpadButton(findViewById(R.id.btn_dpad_fwd), true, 1f);
        bindDpadButton(findViewById(R.id.btn_dpad_rev), true, -1f);
        bindDpadButton(findViewById(R.id.btn_dpad_left), false, -1f);
        bindDpadButton(findViewById(R.id.btn_dpad_right), false, 1f);

        // Intelligence Tab Actions
        btnIntelTriggerProbe.setOnClickListener(v -> triggerSoilProbe());

        // Settings Tab Listeners
        setupSettingsTabListeners();
    }

    private void switchNavigationTab(int tabIndex) {
        activeTab = tabIndex;
        vibrate(20);

        sectionHome.setVisibility(tabIndex == TAB_HOME ? View.VISIBLE : View.GONE);
        sectionRemote.setVisibility(tabIndex == TAB_REMOTE ? View.VISIBLE : View.GONE);
        sectionIntelligence.setVisibility(tabIndex == TAB_INTELLIGENCE ? View.VISIBLE : View.GONE);
        sectionSettings.setVisibility(tabIndex == TAB_SETTINGS ? View.VISIBLE : View.GONE);

        int activeColor = Color.parseColor("#FF6B4E");
        int mutedColor = Color.parseColor("#A49C96");

        ivNavHome.setColorFilter(tabIndex == TAB_HOME ? activeColor : mutedColor);
        tvNavHome.setTextColor(tabIndex == TAB_HOME ? activeColor : mutedColor);

        ivNavRemote.setColorFilter(tabIndex == TAB_REMOTE ? activeColor : mutedColor);
        tvNavRemote.setTextColor(tabIndex == TAB_REMOTE ? activeColor : mutedColor);

        ivNavIntelligence.setColorFilter(tabIndex == TAB_INTELLIGENCE ? activeColor : mutedColor);
        tvNavIntelligence.setTextColor(tabIndex == TAB_INTELLIGENCE ? activeColor : mutedColor);

        ivNavSettings.setColorFilter(tabIndex == TAB_SETTINGS ? activeColor : mutedColor);
        tvNavSettings.setTextColor(tabIndex == TAB_SETTINGS ? activeColor : mutedColor);

        if (streamer != null) {
            if (tabIndex == TAB_REMOTE) {
                streamer.start();
            } else {
                streamer.stop();
            }
        }
    }

    private void switchControlMode(String mode) {
        activeMode = mode;
        emergencyStopQuiet();

        boolean isDual = MODE_DUAL_THUMBS.equals(mode);
        boolean isSingle = MODE_SINGLE_STICK.equals(mode);
        boolean isDpad = MODE_DPAD.equals(mode);

        leftSidePanel.setVisibility(isSingle ? View.GONE : View.VISIBLE);
        rightSidePanel.setVisibility(isSingle ? View.GONE : View.VISIBLE);
        singleStickBottomPanel.setVisibility(isSingle ? View.VISIBLE : View.GONE);

        leftDualControls.setVisibility(isDual ? View.VISIBLE : View.GONE);
        rightDualControls.setVisibility(isDual ? View.VISIBLE : View.GONE);
        leftDpadControls.setVisibility(isDpad ? View.VISIBLE : View.GONE);
        rightDpadControls.setVisibility(isDpad ? View.VISIBLE : View.GONE);

        styleModeButton(btnModeDualThumbs, isDual);
        styleModeButton(btnModeSingleStick, isSingle);
        styleModeButton(btnModeDpad, isDpad);
    }

    private void styleModeButton(Button btn, boolean active) {
        btn.setBackgroundResource(active ? R.drawable.bg_button_tactical_active : R.drawable.bg_button_tactical);
        btn.setTextColor(Color.parseColor(active ? "#FFFFFF" : "#23201E"));
    }

    @SuppressLint("ClickableViewAccessibility")
    private void bindDpadButton(Button btn, boolean isThrottle, float value) {
        btn.setOnTouchListener((v, event) -> {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    v.setBackgroundResource(R.drawable.bg_button_tactical_active);
                    ((Button) v).setTextColor(Color.WHITE);
                    vibrate(20);
                    if (isThrottle) dpadThrottle = value;
                    else dpadSteer = value;
                    mainHandler.removeCallbacks(dpadDispatchLoop);
                    mainHandler.post(dpadDispatchLoop);
                    return true;

                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    v.setBackgroundResource(R.drawable.bg_button_tactical);
                    ((Button) v).setTextColor(Color.parseColor("#23201E"));
                    if (isThrottle) dpadThrottle = 0f;
                    else dpadSteer = 0f;

                    if (dpadThrottle == 0f && dpadSteer == 0f) {
                        mainHandler.removeCallbacks(dpadDispatchLoop);
                        onMotionStop();
                    } else {
                        dispatchAxisKinematics(dpadThrottle, dpadSteer);
                    }
                    return true;
            }
            return false;
        });
    }

    private void dispatchAxisKinematics(float throttle, float steer) {
        if (isProbing) {
            tvHudMotionVector.setText("🔒 DRIVE LOCKED | SOIL PROBE ACTIVE");
            return;
        }
        KinematicsHelper.MotionResult res = KinematicsHelper.compute(throttle, steer, currentSpeed, config);
        long now = System.currentTimeMillis();
        if (now - lastAxisDispatchTime >= 50 || (res.leftPwm == 0 && res.rightPwm == 0)) {
            lastAxisDispatchTime = now;
            onMotionUpdate(res.leftPwm, res.rightPwm, throttle, steer, res.vectorText);
        }
    }

    @Override
    public void onMotionUpdate(int leftPwm, int rightPwm, float throttle, float steer, String vectorText) {
        if (isProbing) return;
        tvHudMotionVector.setText(String.format(Locale.US, "%s | L:%d R:%d", vectorText, leftPwm, rightPwm));
        tvHomeMotionTag.setText(leftPwm == 0 && rightPwm == 0 ? "STOPPED" : "ACTIVE");
        apiClient.sendDriveCommand(leftPwm, rightPwm, null);
    }

    @Override
    public void onMotionStop() {
        tvHudMotionVector.setText("STOPPED | L:0 R:0");
        tvHomeMotionTag.setText("STOPPED");
        apiClient.sendDriveCommand(0, 0, null);
    }

    private void applySpeed(int speed) {
        currentSpeed = Math.max(25, Math.min(100, speed));
        joystickView.setSpeedPercent(currentSpeed);
        sbSpeed.setProgress(currentSpeed);

        String tag = currentSpeed == 35 ? "SLOW" : (currentSpeed == 65 ? "MED" : (currentSpeed == 100 ? "FAST" : "CUSTOM"));
        tvDualSpeedVal.setText(String.format(Locale.US, "%d%% (%s)", currentSpeed, tag));
        tvSingleSpeedVal.setText(String.format(Locale.US, "%d%% (%s)", currentSpeed, tag));

        styleSpeedBtn(btnDualSpeed35, currentSpeed == 35);
        styleSpeedBtn(btnDualSpeed65, currentSpeed == 65);
        styleSpeedBtn(btnDualSpeed100, currentSpeed == 100);
        styleSpeedBtn(btnSingleSpeed35, currentSpeed == 35);
        styleSpeedBtn(btnSingleSpeed65, currentSpeed == 65);
        styleSpeedBtn(btnSingleSpeed100, currentSpeed == 100);
    }

    private void styleSpeedBtn(Button btn, boolean active) {
        btn.setBackgroundResource(active ? R.drawable.bg_button_tactical_active : R.drawable.bg_button_tactical);
        btn.setTextColor(Color.parseColor(active ? "#FFFFFF" : "#23201E"));
    }

    private void applySprayDuration(int ms) {
        currentSprayMs = ms;
        String secLabel = String.format(Locale.US, "%.1fs", ms / 1000f);
        btnDualSpray.setText(String.format(Locale.US, "SPRAY (%s)", secLabel));
        btnSingleSpray.setText(String.format(Locale.US, "SPRAY BURST (%s)", secLabel));

        styleSprayPill(btnDualSpray05, ms == 500);
        styleSprayPill(btnDualSpray10, ms == 1000);
        styleSprayPill(btnDualSpray20, ms == 2000);
        styleSprayPill(btnSingleSpray05, ms == 500);
        styleSprayPill(btnSingleSpray10, ms == 1000);
        styleSprayPill(btnSingleSpray20, ms == 2000);
    }

    private void styleSprayPill(Button btn, boolean active) {
        btn.setBackgroundResource(active ? R.drawable.bg_button_spray_pill_active : R.drawable.bg_button_tactical);
        btn.setTextColor(Color.parseColor(active ? "#FF6B4E" : "#23201E"));
    }

    private void triggerChemicalSpray() {
        if (isSprayActive) return;
        isSprayActive = true;
        vibrate(60);

        tvSprayAlertBanner.setVisibility(View.VISIBLE);
        tvSprayAlertBanner.setText(String.format(Locale.US, "CHEMICAL SPRAY ACTIVE (%dms)", currentSprayMs));

        apiClient.triggerSpray(currentSprayMs, new RoverApiClient.ApiCallback() {
            @Override public void onSuccess(String responseText) {}
            @Override public void onError(String errorMessage) {
                Toast.makeText(MainActivity.this, "Spray: " + errorMessage, Toast.LENGTH_SHORT).show();
            }
        });

        mainHandler.postDelayed(() -> {
            tvSprayAlertBanner.setVisibility(View.GONE);
            isSprayActive = false;
        }, currentSprayMs);
    }

    private void toggleFlash() {
        flashBrightness = (flashBrightness == 0) ? 180 : 0;
        vibrate(30);

        if (flashBrightness > 0) {
            btnSideFlash.setBackgroundResource(R.drawable.bg_button_flash);
            btnSideFlash.setTextColor(Color.parseColor("#92400E"));
            btnSingleFlash.setBackgroundResource(R.drawable.bg_button_flash);
            btnSingleFlash.setTextColor(Color.parseColor("#92400E"));
        } else {
            btnSideFlash.setBackgroundResource(R.drawable.bg_button_tactical);
            btnSideFlash.setTextColor(Color.parseColor("#78706B"));
            btnSingleFlash.setBackgroundResource(R.drawable.bg_button_tactical);
            btnSingleFlash.setTextColor(Color.parseColor("#78706B"));
        }

        apiClient.setFlash(flashBrightness, null);
    }

    private void triggerSoilProbe() {
        if (isProbing) return;
        isProbing = true;
        vibrate(50);
        emergencyStopQuiet();
        tvHudMotionVector.setText("🔒 DRIVE LOCKED | SOIL PROBE ACTIVE");
        tvProbeMoistureVal.setText("Soil: PROBING 50mm...");
        tvProbeMoistureVal.setTextColor(Color.parseColor("#FF6B4E"));

        apiClient.triggerProbe(new RoverApiClient.ApiCallback() {
            @Override
            public void onSuccess(String responseText) {
                mainHandler.postDelayed(probePollRunnable, 400);
            }

            @Override
            public void onError(String errorMessage) {
                // Command outcome is ambiguous after a network failure. Do not unlock drive
                // until /probe_status explicitly reports idle from the rover.
                isProbing = true;
                tvProbeMoistureVal.setText("Probe response lost • checking rover state");
                tvProbeMoistureVal.setTextColor(Color.parseColor("#D97706"));
                tvHudMotionVector.setText("DRIVE LOCKED • PROBE STATE UNKNOWN");
                mainHandler.postDelayed(probePollRunnable, 1000);
            }
        });
    }

    private void updateProbeUI(RoverApiClient.ProbeStatus status) {
        if (status == null) return;
        if (!status.idle) {
            isProbing = true;
            tvHudMotionVector.setText("🔒 DRIVE LOCKED | " + (status.status != null ? status.status.toUpperCase(Locale.US) : "PROBING"));
            String statusMsg = status.status != null ? status.status : "Sampling...";
            tvProbeMoistureVal.setText(String.format(Locale.US, "Soil: %s (%d%%)", statusMsg, status.percent));
            tvProbeMoistureVal.setTextColor(Color.parseColor("#FF6B4E"));
        } else {
            isProbing = false;
            tvHudMotionVector.setText("STOPPED | L:0 R:0");
            lastReportedMoisture = status.percent;

            String condition = status.dry ? "DRY (Hydrated)" : "OPTIMAL";
            String detail = status.status != null ? status.status : condition;

            // Update Cockpit Chip
            tvProbeMoistureVal.setText(String.format(Locale.US, "Soil: %d%% | Limit: %d%% (%s)",
                    status.percent, status.threshold, detail));
            tvProbeMoistureVal.setTextColor(Color.parseColor(status.dry ? "#D97706" : "#2E7D5B"));

            // Update Home Snapshot
            tvHomeSoilVal.setText(String.format(Locale.US, "%d%%", status.percent));
            tvHomeSoilDesc.setText(status.dry ? "Dry • Hydrated" : "Optimal Moisture");

            // Update Intelligence Dashboard
            tvIntelMoistureLarge.setText(String.format(Locale.US, "%d%%", status.percent));
            tvIntelStatusBadge.setText(status.dry ? "HYDRATED" : "OPTIMAL");
            tvIntelStatusBadge.setTextColor(Color.parseColor(status.dry ? "#D97706" : "#2E7D5B"));
        }
    }

    private void emergencyStopQuiet() {
        dpadThrottle = 0f;
        dpadSteer = 0f;
        mainHandler.removeCallbacks(dpadDispatchLoop);
        if (sliderThrottle != null) sliderThrottle.reset();
        if (sliderSteering != null) sliderSteering.reset();
        if (joystickView != null) joystickView.resetThumb();
        onMotionStop();
    }

    private void emergencyStop() {
        vibrate(120);
        emergencyStopQuiet();
        tvHudMotionVector.setText("E-STOP ASSERTED");
        Toast.makeText(this, "EMERGENCY STOP ASSERTED", Toast.LENGTH_SHORT).show();
    }

    private void updateConnectionStatus(boolean success, long latencyMs) {
        if (success) {
            tvTopStatusBadge.setText("ONLINE");
            tvTopStatusBadge.setTextColor(Color.parseColor("#2E7D5B"));
            tvTopStatusBadge.setBackgroundResource(R.drawable.bg_badge_online);
            tvTopPing.setText(String.format(Locale.US, "%d ms", latencyMs));
        } else {
            tvTopStatusBadge.setText("OFFLINE");
            tvTopStatusBadge.setTextColor(Color.parseColor("#DC2626"));
            tvTopStatusBadge.setBackgroundResource(R.drawable.bg_badge_offline);
            tvTopPing.setText("-- ms");
        }
    }

    private void setupSettingsTabValues() {
        float currentSens = config.getTurnSensitivity();
        sbSettingsTurnSens.setProgress(Math.round((currentSens - 0.30f) * 100f));
        tvSettingsTurnSensVal.setText(String.format(Locale.US, "%.2fx", currentSens));

        int currentTrim = config.getSteeringTrim();
        sbSettingsTrim.setProgress(currentTrim + 25);
        tvSettingsTrimVal.setText(String.format(Locale.US, "%s%d%%", (currentTrim > 0 ? "+" : ""), currentTrim));

        int currentThreshold = config.getProbeThreshold();
        sbSettingsProbeThreshold.setProgress(Math.max(0, Math.min(70, currentThreshold - 10)));
        tvSettingsProbeThresholdVal.setText(String.format(Locale.US, "%d%%", currentThreshold));

        cbSettingsInvertThrottle.setChecked(config.isInvertThrottle());
        cbSettingsInvertSteer.setChecked(config.isInvertSteer());
        if (cbSettingsMirrorStream != null) {
            cbSettingsMirrorStream.setChecked(config.isMirrorStream());
        }
        if (cbSettingsRelayActiveLow != null) {
            cbSettingsRelayActiveLow.setChecked("low".equalsIgnoreCase(config.getRelayPolarity()));
        }

        if (ivCameraStream != null) {
            ivCameraStream.setScaleX(config.isMirrorStream() ? -1f : 1f);
            ivCameraStream.setRotation(streamRotationDeg);
        }

        etSettingsHost.setText(config.getHost());
        etSettingsCtrlPort.setText(String.valueOf(config.getCtrlPort()));
        etSettingsStreamPort.setText(String.valueOf(config.getStreamPort()));
        etSettingsSprayMs.setText(String.valueOf(config.getSprayMs()));
        tvHomeIp.setText(config.getHost() + "\nAgriRover-CAM-AP");
    }

    private void setupSettingsTabListeners() {
        sbSettingsTurnSens.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tvSettingsTurnSensVal.setText(String.format(Locale.US, "%.2fx", 0.30f + (progress / 100f)));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        sbSettingsTrim.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                int val = progress - 25;
                tvSettingsTrimVal.setText(String.format(Locale.US, "%s%d%%", (val > 0 ? "+" : ""), val));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        sbSettingsProbeThreshold.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tvSettingsProbeThresholdVal.setText(String.format(Locale.US, "%d%%", 10 + progress));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        btnSettingsReset.setOnClickListener(v -> {
            config.resetDefaults();
            setupSettingsTabValues();
            streamer.restart();
            apiClient.setProbeThreshold(RoverConfig.DEFAULT_PROBE_THRESHOLD, null);
            Toast.makeText(this, "Settings reset to defaults", Toast.LENGTH_SHORT).show();
        });

        btnSettingsSave.setOnClickListener(v -> {
            config.setTurnSensitivity(0.30f + (sbSettingsTurnSens.getProgress() / 100f));
            config.setSteeringTrim(sbSettingsTrim.getProgress() - 25);
            int newThreshold = 10 + sbSettingsProbeThreshold.getProgress();
            config.setProbeThreshold(newThreshold);
            apiClient.setProbeThreshold(newThreshold, null);

            config.setInvertThrottle(cbSettingsInvertThrottle.isChecked());
            config.setInvertSteer(cbSettingsInvertSteer.isChecked());
            if (cbSettingsMirrorStream != null) {
                config.setMirrorStream(cbSettingsMirrorStream.isChecked());
                if (ivCameraStream != null) {
                    ivCameraStream.setScaleX(config.isMirrorStream() ? -1f : 1f);
                }
            }
            if (cbSettingsRelayActiveLow != null) {
                String pol = cbSettingsRelayActiveLow.isChecked() ? "low" : "high";
                config.setRelayPolarity(pol);
                apiClient.setRelayPolarity(pol, null);
            }

            config.setHost(etSettingsHost.getText().toString());
            try { config.setCtrlPort(Integer.parseInt(etSettingsCtrlPort.getText().toString().trim())); } catch (Exception ignored) {}
            try { config.setStreamPort(Integer.parseInt(etSettingsStreamPort.getText().toString().trim())); } catch (Exception ignored) {}
            try { config.setSprayMs(Integer.parseInt(etSettingsSprayMs.getText().toString().trim())); } catch (Exception ignored) {}

            tvHomeIp.setText(config.getHost() + "\nAgriRover-CAM-AP");
            streamer.restart();
            Toast.makeText(this, "Settings saved & applied", Toast.LENGTH_SHORT).show();
        });

        // Hardware Bench Diagnostics Listeners
        if (btnBenchTestLeft != null) {
            btnBenchTestLeft.setOnClickListener(v -> {
                vibrate(40);
                Toast.makeText(this, "⚡ Testing Left Wheels (1.2s @ 180 PWM)...", Toast.LENGTH_SHORT).show();
                apiClient.runBenchMotorTest(180, 0, 1200, null);
            });
        }

        if (btnBenchTestRight != null) {
            btnBenchTestRight.setOnClickListener(v -> {
                vibrate(40);
                Toast.makeText(this, "⚡ Testing Right Wheels (1.2s @ 180 PWM)...", Toast.LENGTH_SHORT).show();
                apiClient.runBenchMotorTest(0, 180, 1200, null);
            });
        }

        if (btnBenchTestBoth != null) {
            btnBenchTestBoth.setOnClickListener(v -> {
                vibrate(40);
                Toast.makeText(this, "⚡ Testing All 4 Wheels (1.2s @ 180 PWM)...", Toast.LENGTH_SHORT).show();
                apiClient.runBenchMotorTest(180, 180, 1200, null);
            });
        }

        if (btnBenchPrimePump != null) {
            btnBenchPrimePump.setOnClickListener(v -> {
                vibrate(50);
                isPumpPriming = !isPumpPriming;
                apiClient.setPumpManualState(isPumpPriming, new RoverApiClient.ApiCallback() {
                    @Override
                    public void onSuccess(String responseText) {
                        btnBenchPrimePump.setText(isPumpPriming ? "STOP PUMP PRIME" : "Prime / Drain Pump");
                        Toast.makeText(MainActivity.this, isPumpPriming ? "💧 Direct 12V Pump Priming ON" : "💧 Direct 12V Pump STOPPED", Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void onError(String errorMessage) {
                        isPumpPriming = false;
                        btnBenchPrimePump.setText("Prime / Drain Pump");
                        Toast.makeText(MainActivity.this, "Pump error: " + errorMessage, Toast.LENGTH_SHORT).show();
                    }
                });
            });
        }
    }

    private void vibrate(long ms) {
        if (vibrator != null && vibrator.hasVibrator()) {
            vibrator.vibrate(ms);
        }
    }

    @Override
    public void onStreamConnected(String url) {
        layoutStreamPlaceholder.setVisibility(View.GONE);
        ivCameraStream.setVisibility(View.VISIBLE);
        if (ivCameraStream != null) {
            ivCameraStream.setScaleX(config.isMirrorStream() ? -1f : 1f);
            ivCameraStream.setRotation(streamRotationDeg);
        }
    }

    @Override
    public void onNewFrame(Bitmap frame, int fps) {
        ivCameraStream.setImageBitmap(frame);
        if (ivCameraStream.getRotation() != streamRotationDeg) {
            ivCameraStream.setRotation(streamRotationDeg);
        }
        float targetScaleX = (config != null && config.isMirrorStream()) ? -1f : 1f;
        if (ivCameraStream.getScaleX() != targetScaleX) {
            ivCameraStream.setScaleX(targetScaleX);
        }
        tvHudFps.setText(String.format(Locale.US, "%d FPS", fps));
    }

    @Override
    public void onStreamError(String message) {
        layoutStreamPlaceholder.setVisibility(View.VISIBLE);
        tvStreamStatus.setText(message);
    }

    @Override
    public void onStreamDisconnected() {
        layoutStreamPlaceholder.setVisibility(View.VISIBLE);
        tvStreamStatus.setText("Stream Disconnected");
    }

    @Override
    protected void onResume() {
        super.onResume();
        mainHandler.removeCallbacks(pingRunnable);
        mainHandler.post(pingRunnable);
        if (activeTab == TAB_REMOTE && streamer != null) {
            streamer.start();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        mainHandler.removeCallbacks(pingRunnable);
        if (streamer != null) streamer.stop();
        emergencyStopQuiet();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mainHandler.removeCallbacks(pingRunnable);
        mainHandler.removeCallbacks(dpadDispatchLoop);
        mainHandler.removeCallbacks(probePollRunnable);
        if (streamer != null) streamer.stop();
    }
}
