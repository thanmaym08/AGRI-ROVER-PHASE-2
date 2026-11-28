package com.agrirover.teleop;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import androidx.annotation.NonNull;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * REST API client dispatching non-blocking HTTP requests to ESP32-CAM firmware.
 */
public class RoverApiClient {

    private static final String TAG = "RoverApiClient";

    public static class ProbeStatus {
        @SerializedName("state")
        public int state;

        @SerializedName("dry")
        public boolean dry;

        @SerializedName("raw")
        public int raw;

        @SerializedName("percent")
        public int percent;

        @SerializedName("threshold")
        public int threshold;

        @SerializedName("status")
        public String status;

        @SerializedName("idle")
        public boolean idle;
    }

    public interface ApiCallback {
        void onSuccess(String responseText);
        void onError(String errorMessage);
    }

    public interface ProbeCallback {
        void onStatus(ProbeStatus status);
        void onError(String errorMessage);
    }

    public interface PingCallback {
        void onPingResult(boolean success, long latencyMs);
    }

    private final RoverConfig config;
    private final OkHttpClient httpClient;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final Gson gson = new Gson();

    public RoverApiClient(RoverConfig config) {
        this.config = config;
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(500, TimeUnit.MILLISECONDS)
                .readTimeout(800, TimeUnit.MILLISECONDS)
                .writeTimeout(500, TimeUnit.MILLISECONDS)
                .retryOnConnectionFailure(false)
                .build();
    }

    public void sendDriveCommand(int left, int right, ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/drive?left=" + left + "&right=" + right;
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void triggerSpray(int ms, ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/spray?ms=" + ms;
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void setFlash(int val, ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/flash?val=" + val;
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void triggerProbe(ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/probe";
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void getProbeStatus(ProbeCallback callback) {
        String url = config.getControlBaseUrl() + "/probe_status";
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful() && response.body() != null) {
                    String json = response.body().string();
                    try {
                        ProbeStatus status = gson.fromJson(json, ProbeStatus.class);
                        if (callback != null) {
                            mainHandler.post(() -> callback.onStatus(status));
                        }
                    } catch (Exception e) {
                        if (callback != null) {
                            mainHandler.post(() -> callback.onError("JSON Parse error"));
                        }
                    }
                } else {
                    if (callback != null) {
                        mainHandler.post(() -> callback.onError("HTTP " + response.code()));
                    }
                }
                response.close();
            }
        });
    }

    public void setProbeThreshold(int threshold, ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/probe_threshold?val=" + threshold;
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void setRelayPolarity(String polarity, ApiCallback callback) {
        String pol = "low".equalsIgnoreCase(polarity) ? "low" : "high";
        String url = config.getControlBaseUrl() + "/spray?polarity=" + pol;
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void setPumpManualState(boolean on, ApiCallback callback) {
        String url = config.getControlBaseUrl() + "/spray?state=" + (on ? "on" : "off");
        Request request = new Request.Builder().url(url).build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e.getMessage()));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "";
                if (callback != null) {
                    mainHandler.post(() -> {
                        if (response.isSuccessful()) {
                            callback.onSuccess(body);
                        } else {
                            callback.onError("HTTP " + response.code());
                        }
                    });
                }
                response.close();
            }
        });
    }

    public void runBenchMotorTest(int left, int right, int durationMs, ApiCallback callback) {
        sendDriveCommand(left, right, new ApiCallback() {
            @Override
            public void onSuccess(String responseText) {
                mainHandler.postDelayed(() -> sendDriveCommand(0, 0, callback), durationMs);
            }

            @Override
            public void onError(String errorMessage) {
                if (callback != null) {
                    callback.onError(errorMessage);
                }
            }
        });
    }

    public void ping(PingCallback callback) {
        // Probe the firmware's root page instead of sending a zero-PWM drive command.
        // A "ping" must never interrupt an active joystick command.
        String url = config.getControlBaseUrl() + "/probe_status";
        Request request = new Request.Builder().url(url).get().build();
        final long t0 = System.currentTimeMillis();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onPingResult(false, -1));
                }
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) {
                final long latency = System.currentTimeMillis() - t0;
                final boolean ok = response.isSuccessful();
                response.close();
                if (callback != null) {
                    mainHandler.post(() -> callback.onPingResult(ok, latency));
                }
            }
        });
    }
}
