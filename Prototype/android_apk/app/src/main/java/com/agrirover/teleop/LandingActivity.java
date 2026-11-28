package com.agrirover.teleop;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.util.Locale;

/**
 * Landing Page in Clean Land Rover Luxury Telematics Style.
 */
public class LandingActivity extends AppCompatActivity {

    public static final String EXTRA_CONTROL_MODE = "extra_control_mode";
    public static final String MODE_DUAL_THUMBS = "DUAL_THUMBS";
    public static final String MODE_SINGLE_STICK = "SINGLE_STICK";
    public static final String MODE_DPAD = "DPAD";

    private RoverConfig config;
    private RoverApiClient apiClient;
    private final Handler handler = new Handler(Looper.getMainLooper());

    private TextView tvTargetIp;
    private TextView tvStatusPill;

    private final Runnable pingLoop = new Runnable() {
        @Override
        public void run() {
            if (apiClient != null) {
                apiClient.ping((success, latencyMs) -> {
                    if (success) {
                        tvStatusPill.setText(String.format(Locale.US, "● ONLINE (%dms)", latencyMs));
                        tvStatusPill.setTextColor(Color.parseColor("#059669"));
                        tvStatusPill.setBackgroundResource(R.drawable.bg_status_badge);
                    } else {
                        tvStatusPill.setText("● OFFLINE");
                        tvStatusPill.setTextColor(Color.parseColor("#DC2626"));
                        tvStatusPill.setBackgroundResource(R.drawable.bg_button_tactical);
                    }
                });
            }
            handler.postDelayed(this, 2500);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing);

        config = new RoverConfig(this);
        apiClient = new RoverApiClient(config);

        tvTargetIp = findViewById(R.id.tv_landing_target_ip);
        tvStatusPill = findViewById(R.id.tv_landing_status_pill);
        ImageButton btnSettings = findViewById(R.id.btn_landing_settings);

        refreshEndpointLabel();

        findViewById(R.id.card_mode_dual_thumbs).setOnClickListener(v -> launchCockpit(MODE_DUAL_THUMBS));
        findViewById(R.id.card_mode_single_stick).setOnClickListener(v -> launchCockpit(MODE_SINGLE_STICK));
        findViewById(R.id.card_mode_dpad).setOnClickListener(v -> launchCockpit(MODE_DPAD));

        btnSettings.setOnClickListener(v -> showSettingsDialog());
    }

    private void refreshEndpointLabel() {
        tvTargetIp.setText(String.format(Locale.US, "%s:%d • AgriRover-CAM-AP",
                config.getHost(), config.getCtrlPort()));
    }

    private void launchCockpit(String mode) {
        Intent intent = new Intent(this, MainActivity.class);
        intent.putExtra(EXTRA_CONTROL_MODE, mode);
        startActivity(intent);
    }

    @SuppressLint("InflateParams")
    private void showSettingsDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_settings, null);
        builder.setView(dialogView);

        AlertDialog dialog = builder.create();

        SeekBar sbTurnSens = dialogView.findViewById(R.id.sb_dialog_turn_sens);
        TextView tvTurnSensVal = dialogView.findViewById(R.id.tv_dialog_turn_sens_val);
        SeekBar sbTrim = dialogView.findViewById(R.id.sb_dialog_trim);
        TextView tvTrimVal = dialogView.findViewById(R.id.tv_dialog_trim_val);
        CheckBox cbInvertThrottle = dialogView.findViewById(R.id.cb_invert_throttle);
        CheckBox cbInvertSteer = dialogView.findViewById(R.id.cb_invert_steer);
        CheckBox cbMirrorStream = dialogView.findViewById(R.id.cb_dialog_mirror_stream);
        CheckBox cbRelayActiveLow = dialogView.findViewById(R.id.cb_dialog_relay_active_low);

        EditText etHost = dialogView.findViewById(R.id.et_dialog_host);
        EditText etCtrlPort = dialogView.findViewById(R.id.et_dialog_ctrl_port);
        EditText etStreamPort = dialogView.findViewById(R.id.et_dialog_stream_port);
        EditText etSprayMs = dialogView.findViewById(R.id.et_dialog_spray_ms);

        Button btnReset = dialogView.findViewById(R.id.btn_dialog_reset);
        Button btnSave = dialogView.findViewById(R.id.btn_dialog_save);

        float currentSens = config.getTurnSensitivity();
        sbTurnSens.setProgress(Math.round((currentSens - 0.30f) * 100f));
        tvTurnSensVal.setText(String.format(Locale.US, "%.2fx", currentSens));

        int currentTrim = config.getSteeringTrim();
        sbTrim.setProgress(currentTrim + 25);
        tvTrimVal.setText(String.format(Locale.US, "%s%d%%", (currentTrim > 0 ? "+" : ""), currentTrim));

        cbInvertThrottle.setChecked(config.isInvertThrottle());
        cbInvertSteer.setChecked(config.isInvertSteer());
        if (cbMirrorStream != null) {
            cbMirrorStream.setChecked(config.isMirrorStream());
        }
        if (cbRelayActiveLow != null) {
            cbRelayActiveLow.setChecked("low".equalsIgnoreCase(config.getRelayPolarity()));
        }

        etHost.setText(config.getHost());
        etCtrlPort.setText(String.valueOf(config.getCtrlPort()));
        etStreamPort.setText(String.valueOf(config.getStreamPort()));
        etSprayMs.setText(String.valueOf(config.getSprayMs()));

        sbTurnSens.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                tvTurnSensVal.setText(String.format(Locale.US, "%.2fx", 0.30f + (progress / 100f)));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        sbTrim.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                int val = progress - 25;
                tvTrimVal.setText(String.format(Locale.US, "%s%d%%", (val > 0 ? "+" : ""), val));
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        btnReset.setOnClickListener(v -> {
            config.resetDefaults();
            refreshEndpointLabel();
            dialog.dismiss();
            Toast.makeText(this, "Settings reset to defaults", Toast.LENGTH_SHORT).show();
        });

        btnSave.setOnClickListener(v -> {
            config.setTurnSensitivity(0.30f + (sbTurnSens.getProgress() / 100f));
            config.setSteeringTrim(sbTrim.getProgress() - 25);
            config.setInvertThrottle(cbInvertThrottle.isChecked());
            config.setInvertSteer(cbInvertSteer.isChecked());
            if (cbMirrorStream != null) {
                config.setMirrorStream(cbMirrorStream.isChecked());
            }
            if (cbRelayActiveLow != null) {
                config.setRelayPolarity(cbRelayActiveLow.isChecked() ? "low" : "high");
            }
            config.setHost(etHost.getText().toString());
            try { config.setCtrlPort(Integer.parseInt(etCtrlPort.getText().toString().trim())); } catch (Exception ignored) {}
            try { config.setStreamPort(Integer.parseInt(etStreamPort.getText().toString().trim())); } catch (Exception ignored) {}
            try { config.setSprayMs(Integer.parseInt(etSprayMs.getText().toString().trim())); } catch (Exception ignored) {}

            refreshEndpointLabel();
            dialog.dismiss();
            Toast.makeText(this, "Settings saved", Toast.LENGTH_SHORT).show();
        });

        dialog.show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        handler.post(pingLoop);
    }

    @Override
    protected void onPause() {
        super.onPause();
        handler.removeCallbacks(pingLoop);
    }
}
