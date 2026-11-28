package com.agrirover.teleop;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import androidx.annotation.Nullable;

/**
 * Premium Mars Rover 360° Omnidirectional Joystick.
 * Warm coral gradient knob with smooth capacitive physics.
 */
public class JoystickView extends View {

    public interface JoystickListener {
        void onMotionUpdate(int leftPwm, int rightPwm, float throttle, float steer, String vectorText);
        void onMotionStop();
    }

    private RoverConfig config;
    private JoystickListener listener;

    private int speedPercent = 65;
    private float centerX = 0f;
    private float centerY = 0f;
    private float baseRadius = 0f;
    private float thumbRadius = 0f;
    private float maxTravelRadius = 0f;

    private float thumbX = 0f;
    private float thumbY = 0f;
    private boolean isDragging = false;

    private long lastDispatchTime = 0;
    private static final long DISPATCH_INTERVAL_MS = 50;

    private final Paint basePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint baseRingPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint guidePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint glowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint thumbPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint thumbHighlightPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    public JoystickView(Context context) {
        super(context);
        init();
    }

    public JoystickView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public JoystickView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        basePaint.setColor(Color.parseColor("#F2F3F9"));
        basePaint.setStyle(Paint.Style.FILL);

        baseRingPaint.setColor(Color.parseColor("#E0BFBA"));
        baseRingPaint.setStyle(Paint.Style.STROKE);
        baseRingPaint.setStrokeWidth(2f);

        guidePaint.setColor(Color.parseColor("#FFDDC4"));
        guidePaint.setStyle(Paint.Style.STROKE);
        guidePaint.setStrokeWidth(1.5f);

        thumbPaint.setColor(Color.parseColor("#FF6F59"));
        thumbPaint.setStyle(Paint.Style.FILL);

        thumbHighlightPaint.setColor(Color.parseColor("#99FFFFFF"));
        thumbHighlightPaint.setStyle(Paint.Style.FILL);

        textPaint.setColor(Color.parseColor("#8C716C"));
        textPaint.setTextSize(20f);
        textPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        textPaint.setTextAlign(Paint.Align.CENTER);
    }

    public void setConfig(RoverConfig config) {
        this.config = config;
    }

    public void setListener(JoystickListener listener) {
        this.listener = listener;
    }

    public void setSpeedPercent(int percent) {
        this.speedPercent = Math.max(25, Math.min(100, percent));
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        centerX = w / 2f;
        centerY = h / 2f;
        thumbX = centerX;
        thumbY = centerY;

        float minDim = Math.min(w, h);
        baseRadius = (minDim / 2f) * 0.88f;
        thumbRadius = baseRadius * 0.34f;
        maxTravelRadius = Math.max(1f, baseRadius - thumbRadius);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (baseRadius <= 0) return;

        canvas.drawCircle(centerX, centerY, baseRadius, basePaint);
        canvas.drawCircle(centerX, centerY, baseRadius, baseRingPaint);

        canvas.drawLine(centerX - baseRadius, centerY, centerX + baseRadius, centerY, guidePaint);
        canvas.drawLine(centerX, centerY - baseRadius, centerX, centerY + baseRadius, guidePaint);
        canvas.drawCircle(centerX, centerY, baseRadius * 0.52f, guidePaint);

        canvas.drawText("360° DRIVE", centerX, centerY + baseRadius - 16f, textPaint);

        int glowColor = isDragging ? 0x4DFF6B4E : 0x20FF6B4E;
        glowPaint.setShader(new RadialGradient(thumbX, thumbY, thumbRadius * 1.5f,
                glowColor, Color.TRANSPARENT, Shader.TileMode.CLAMP));
        canvas.drawCircle(thumbX, thumbY, thumbRadius * 1.5f, glowPaint);

        canvas.drawCircle(thumbX, thumbY, thumbRadius, thumbPaint);
        canvas.drawCircle(thumbX - thumbRadius * 0.22f, thumbY - thumbRadius * 0.22f,
                thumbRadius * 0.26f, thumbHighlightPaint);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                isDragging = true;
                processTouch(event.getX(), event.getY());
                return true;

            case MotionEvent.ACTION_MOVE:
                if (isDragging) {
                    processTouch(event.getX(), event.getY());
                }
                return true;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
            case MotionEvent.ACTION_POINTER_UP:
                isDragging = false;
                resetThumb();
                return true;
        }
        return super.onTouchEvent(event);
    }

    private void processTouch(float touchX, float touchY) {
        float dx = touchX - centerX;
        float dy = touchY - centerY;
        float distance = (float) Math.hypot(dx, dy);

        if (distance > maxTravelRadius) {
            float ratio = maxTravelRadius / distance;
            dx *= ratio;
            dy *= ratio;
        }

        thumbX = centerX + dx;
        thumbY = centerY + dy;
        invalidate();

        float normSteer = dx / maxTravelRadius;
        float normThrottle = -dy / maxTravelRadius;

        long now = System.currentTimeMillis();
        if (now - lastDispatchTime >= DISPATCH_INTERVAL_MS) {
            lastDispatchTime = now;
            dispatchKinematics(normThrottle, normSteer);
        }
    }

    public void resetThumb() {
        thumbX = centerX;
        thumbY = centerY;
        invalidate();

        if (listener != null) {
            listener.onMotionStop();
        }
    }

    private void dispatchKinematics(float throttle, float steer) {
        if (listener == null) return;

        KinematicsHelper.MotionResult result =
                KinematicsHelper.compute(throttle, steer, speedPercent, config);

        listener.onMotionUpdate(
                result.leftPwm,
                result.rightPwm,
                throttle,
                steer,
                result.vectorText
        );
    }
}
