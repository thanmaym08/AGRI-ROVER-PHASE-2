package com.agrirover.teleop;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;

/**
 * High-performance, low-latency Native MJPEG Stream decoder for ESP32-CAM (OV2640).
 * Handles streaming over port 81 with fallback to port 80, automatic reconnection,
 * and thread-safe frame delivery to the UI.
 */
public class MjpegStreamer {

    private static final String TAG = "MjpegStreamer";

    public interface StreamListener {
        void onStreamConnected(String url);
        void onNewFrame(Bitmap bitmap, int fps);
        void onStreamError(String message);
        void onStreamDisconnected();
    }

    private final RoverConfig config;
    private final StreamListener listener;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final OkHttpClient httpClient;

    private Thread workerThread;
    private final AtomicBoolean isRunning = new AtomicBoolean(false);

    // JPEG Markers
    private static final int HEADER_MARKER_1 = 0xFF;
    private static final int HEADER_MARKER_2 = 0xD8; // SOI (Start Of Image)
    private static final int FOOTER_MARKER_1 = 0xFF;
    private static final int FOOTER_MARKER_2 = 0xD9; // EOI (End Of Image)

    // Performance metrics
    private int frameCounter = 0;
    private long lastFpsCalcTime = 0;
    private int currentFps = 0;

    public MjpegStreamer(RoverConfig config, StreamListener listener) {
        this.config = config;
        this.listener = listener;
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(3, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build();
    }

    public synchronized void start() {
        if (isRunning.get()) return;
        isRunning.set(true);

        workerThread = new Thread(this::streamLoop, "MjpegStreamWorker");
        workerThread.setDaemon(true);
        workerThread.start();
    }

    public synchronized void stop() {
        isRunning.set(false);
        if (workerThread != null) {
            workerThread.interrupt();
            workerThread = null;
        }
        mainHandler.post(() -> {
            if (listener != null) listener.onStreamDisconnected();
        });
    }

    public synchronized void restart() {
        stop();
        mainHandler.postDelayed(this::start, 300);
    }

    private void streamLoop() {
        String[] urls = new String[] {
                config.getStreamUrl(),
                config.getFallbackStreamUrl()
        };

        int urlIndex = 0;
        int consecutiveFailures = 0;

        while (isRunning.get() && !Thread.currentThread().isInterrupted()) {
            String targetUrl = urls[urlIndex];
            Log.d(TAG, "Connecting to stream: " + targetUrl);

            Request request = new Request.Builder()
                    .url(targetUrl)
                    .header("User-Agent", "AgriRover-Android-Teleop/2.0")
                    .build();

            Response response = null;
            try {
                response = httpClient.newCall(request).execute();
                if (response.isSuccessful()) {
                    ResponseBody body = response.body();
                    if (body != null) {
                        mainHandler.post(() -> {
                            if (listener != null) listener.onStreamConnected(targetUrl);
                        });

                        consecutiveFailures = 0;
                        readMjpegStream(body.byteStream());
                    }
                } else {
                    final int responseCode = response.code();
                    Log.w(TAG, "HTTP stream error code: " + responseCode);
                    mainHandler.post(() -> {
                        if (listener != null) listener.onStreamError("HTTP " + responseCode);
                    });
                }
            } catch (Exception e) {
                if (isRunning.get()) {
                    Log.w(TAG, "Stream connection failed: " + e.getMessage());
                    mainHandler.post(() -> {
                        if (listener != null) listener.onStreamError(e.getMessage());
                    });
                }
            } finally {
                if (response != null) {
                    try {
                        response.close();
                    } catch (Exception ignored) {}
                }
            }

            if (!isRunning.get()) break;

            consecutiveFailures++;
            // Switch between primary (81) and fallback (80)
            urlIndex = (urlIndex + 1) % urls.length;

            // Exponential backoff up to 2 seconds
            long backoff = Math.min(2000, 300 + (consecutiveFailures * 200));
            try {
                Thread.sleep(backoff);
            } catch (InterruptedException e) {
                break;
            }
        }
    }

    private void readMjpegStream(InputStream inputStream) throws Exception {
        BufferedInputStream bis = new BufferedInputStream(inputStream, 16384);
        ByteArrayOutputStream frameBuffer = new ByteArrayOutputStream(65536);

        int prevByte = -1;
        int curByte;
        boolean inJpeg = false;

        lastFpsCalcTime = System.currentTimeMillis();
        frameCounter = 0;

        while (isRunning.get() && !Thread.currentThread().isInterrupted() && (curByte = bis.read()) != -1) {
            if (!inJpeg) {
                // Look for Start Of Image (SOI): 0xFF 0xD8
                if (prevByte == HEADER_MARKER_1 && curByte == HEADER_MARKER_2) {
                    inJpeg = true;
                    frameBuffer.reset();
                    frameBuffer.write(HEADER_MARKER_1);
                    frameBuffer.write(HEADER_MARKER_2);
                }
            } else {
                frameBuffer.write(curByte);

                // Look for End Of Image (EOI): 0xFF 0xD9
                if (prevByte == FOOTER_MARKER_1 && curByte == FOOTER_MARKER_2) {
                    inJpeg = false;

                    byte[] jpegBytes = frameBuffer.toByteArray();
                    if (jpegBytes.length > 200) {
                        Bitmap bitmap = BitmapFactory.decodeByteArray(jpegBytes, 0, jpegBytes.length);
                        if (bitmap != null) {
                            frameCounter++;
                            long now = System.currentTimeMillis();
                            if (now - lastFpsCalcTime >= 1000) {
                                currentFps = frameCounter;
                                frameCounter = 0;
                                lastFpsCalcTime = now;
                            }

                            final int fps = currentFps;
                            mainHandler.post(() -> {
                                if (listener != null && isRunning.get()) {
                                    listener.onNewFrame(bitmap, fps);
                                }
                            });
                        }
                    }
                    frameBuffer.reset();
                }
            }
            prevByte = curByte;
        }
    }
}
