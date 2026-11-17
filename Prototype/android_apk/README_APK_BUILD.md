# Agri Rover — Android APK & Downloadable App Guide

This directory provides two proven methods to install the Agri Rover Teleoperation App on any Android smartphone.

---

## Method 1: Instant 1-Tap PWA Installation (Recommended — Zero-Compile)

Because the app is built as a **Progressive Web App (PWA)** with embedded `manifest.json` and `sw.js` service worker, **you do not need Android Studio or a computer to install it**.

### How to Install on Any Android Phone:
1. Connect your phone to the rover's Wi-Fi hotspot:
   - **SSID:** `AgriRover-CAM-AP`
   - **Password:** `agrirover123`
2. Open **Google Chrome** on your phone.
3. Go to: **`http://192.168.4.1`**
4. Chrome will automatically display a banner: **"Add Agri Rover to Home screen"** or tap the **3 vertical dots menu (⋮)** in the top right corner and tap **"Install App"** (or **"Add to Home screen"**).
5. Tap **Install**.

### Result:
- An official **Agri Rover App Icon** appears directly on your phone's home screen and app launcher.
- It opens in **Pure Fullscreen Standalone App Mode** (no URL bar, no search bar, no browser controls).
- Caches locally for fast, offline startup in agricultural fields.

---

## Method 2: Build a Standalone Native Android APK (.apk file)

If you need a standalone `.apk` package file for college project evaluation, viva defense, or offline APK sharing via WhatsApp/Drive:

### Option A: Using Android Studio (Local Build)
1. Open **Android Studio**.
2. Select **Open an Existing Project** and browse to:
   ```text
   F:\agrirover phase 2\Prototype\android_apk
   ```
3. Click **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
4. When finished, Android Studio generates:
   `app/build/outputs/apk/debug/app-debug.apk`
5. Transfer `app-debug.apk` to your phone and tap to install.

### Option B: Using Google PWABuilder (Online Zero-Setup APK Generator)
1. If you host the mobile app files on GitHub Pages or local hotspot, enter the URL at [pwabuilder.com](https://www.pwabuilder.com).
2. Click **Package for Android**.
3. Download the signed `.apk` directly to your phone!
