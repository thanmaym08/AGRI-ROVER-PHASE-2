package com.agrirover.teleop;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import androidx.annotation.Nullable;

/**
 * Premium Futuristic 1D Pill-Shaped Axis Slider.
 * Mars Rover aesthetic with warm coral & terracotta accents.
 */
public class AxisSliderView extends View {

    public static final int ORIENTATION_VERTICAL = 0;
    public static final int ORIENTATION_HORIZONTAL = 1;

    public interface AxisListener {
        void onAxisChanged(float value);
    }

    private int orientation = ORIENTATION_VERTICAL;
    private int accentColor = Color.parseColor("#FF6F59");
    private String positiveLabel = "FWD";
    private String negativeLabel = "REV";

    private AxisListener listener;
    private float currentValue = 0f;
    private boolean isDragging = false;

    private final Paint trackPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint trackBorderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint centerLinePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint glowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint thumbPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint thumbCorePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint labelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF trackRect = new RectF();

    public AxisSliderView(Context context) {
        super(context);
        init();
    }

    public AxisSliderView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public AxisSliderView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        trackPaint.setColor(Color.parseColor("#F2F3F9"));
        trackPaint.setStyle(Paint.Style.FILL);

        trackBorderPaint.setColor(Color.parseColor("#E0BFBA"));
        trackBorderPaint.setStyle(Paint.Style.STROKE);
        trackBorderPaint.setStrokeWidth(2f);

        centerLinePaint.setColor(Color.parseColor("#E0BFBA"));
        centerLinePaint.setStyle(Paint.Style.STROKE);
        centerLinePaint.setStrokeWidth(2f);

        thumbPaint.setColor(accentColor);
        thumbPaint.setStyle(Paint.Style.FILL);

        thumbCorePaint.setColor(Color.WHITE);
        thumbCorePaint.setStyle(Paint.Style.FILL);

        labelPaint.setColor(Color.parseColor("#58413D"));
        labelPaint.setTextSize(24f);
        labelPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        labelPaint.setTextAlign(Paint.Align.CENTER);
    }

    public void configure(int orientation, int accentColor, String positiveLabel, String negativeLabel) {
        this.orientation = orientation;
        this.accentColor = accentColor;
        this.positiveLabel = positiveLabel;
        this.negativeLabel = negativeLabel;
        thumbPaint.setColor(accentColor);
        invalidate();
    }

    public void setListener(AxisListener listener) {
        this.listener = listener;
    }

    public float getValue() {
        return currentValue;
    }

    public void reset() {
        currentValue = 0f;
        isDragging = false;
        invalidate();
        if (listener != null) listener.onAxisChanged(0f);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float w = getWidth();
        float h = getHeight();
        if (w <= 0 || h <= 0) return;

        float pad = 6f;
        trackRect.set(pad, pad, w - pad, h - pad);
        float corner = Math.min(trackRect.width(), trackRect.height()) / 2f;

        // Clean warm track
        canvas.drawRoundRect(trackRect, corner, corner, trackPaint);
        canvas.drawRoundRect(trackRect, corner, corner, trackBorderPaint);

        float cx = w / 2f;
        float cy = h / 2f;

        if (orientation == ORIENTATION_VERTICAL) {
            float thumbR = Math.min(w * 0.36f, 44f);
            float travel = (h / 2f) - thumbR - 20f;
            float thumbY = cy - (currentValue * travel);

            // Center guideline & notch
            canvas.drawLine(cx, cy - travel, cx, cy + travel, centerLinePaint);
            canvas.drawLine(cx - 14f, cy, cx + 14f, cy, centerLinePaint);

            labelPaint.setColor(Color.parseColor("#FF6F59"));
            canvas.drawText(positiveLabel, cx, 34f, labelPaint);
            labelPaint.setColor(Color.parseColor("#8C716C"));
            canvas.drawText(negativeLabel, cx, h - 18f, labelPaint);

            drawThumb(canvas, cx, thumbY, thumbR);
        } else {
            float thumbR = Math.min(h * 0.36f, 44f);
            float travel = (w / 2f) - thumbR - 20f;
            float thumbX = cx + (currentValue * travel);

            canvas.drawLine(cx - travel, cy, cx + travel, cy, centerLinePaint);
            canvas.drawLine(cx, cy - 14f, cx, cy + 14f, centerLinePaint);

            labelPaint.setColor(Color.parseColor("#FF6F59"));
            canvas.drawText(negativeLabel, 36f, cy + 8f, labelPaint);
            canvas.drawText(positiveLabel, w - 36f, cy + 8f, labelPaint);

            drawThumb(canvas, thumbX, cy, thumbR);
        }
    }

    private void drawThumb(Canvas canvas, float x, float y, float radius) {
        int glowColor = isDragging ? 0x4DFF6B4E : 0x26FF6B4E;
        glowPaint.setShader(new RadialGradient(x, y, radius * 1.5f, glowColor, Color.TRANSPARENT, Shader.TileMode.CLAMP));
        canvas.drawCircle(x, y, radius * 1.5f, glowPaint);

        canvas.drawCircle(x, y, radius, thumbPaint);
        canvas.drawCircle(x, y, radius * 0.36f, thumbCorePaint);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_MOVE:
                isDragging = true;
                processTouch(event.getX(), event.getY());
                return true;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                reset();
                return true;
        }
        return super.onTouchEvent(event);
    }

    private void processTouch(float x, float y) {
        float w = getWidth();
        float h = getHeight();
        if (orientation == ORIENTATION_VERTICAL) {
            float thumbR = Math.min(w * 0.36f, 44f);
            float travel = (h / 2f) - thumbR - 20f;
            float cy = h / 2f;
            float delta = cy - y;
            currentValue = Math.max(-1f, Math.min(1f, delta / travel));
        } else {
            float thumbR = Math.min(h * 0.36f, 44f);
            float travel = (w / 2f) - thumbR - 20f;
            float cx = w / 2f;
            float delta = x - cx;
            currentValue = Math.max(-1f, Math.min(1f, delta / travel));
        }

        invalidate();
        if (listener != null) {
            listener.onAxisChanged(currentValue);
        }
    }
}
