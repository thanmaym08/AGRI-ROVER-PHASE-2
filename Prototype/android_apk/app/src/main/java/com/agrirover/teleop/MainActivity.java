package com.agrirover.teleop;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

/**
 * Agri Rover Android Native App Wrapper
 * Provides dedicated hardware-accelerated fullscreen teleoperation console
 * directly connected to ESP32-CAM (http://192.168.4.1).
 */
public class MainActivity extends Activity {

    private WebView webView;
    private static final String DEFAULT_ROVER_URL = "http://192.168.4.1";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Enforce Fullscreen Hardware Display
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        // Hide navigation bar for immersive cockpit view
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        );

        webView = new WebView(this);
        setContentView(webView);

        // Hardware accelerated WebView settings
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setMediaPlaybackRequiresUserGesture(false);
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setUseWideViewPort(true);
        webSettings.setLoadWithOverviewMode(true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                Toast.makeText(MainActivity.this, 
                    "Connecting to AgriRover Wi-Fi (192.168.4.1)...", 
                    Toast.LENGTH_SHORT).show();
            }
        });

        // Load the Rover Cockpit
        webView.loadUrl(DEFAULT_ROVER_URL);
    }

    @Override
    public void onBackPressed() {
        // Prevent accidental back exit during rover driving
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            Toast.makeText(this, "Press Home to exit Agri Rover Cockpit", Toast.LENGTH_SHORT).show();
        }
    }
}
