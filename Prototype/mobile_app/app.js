/**
 * Agri Rover Mobile Teleoperation Controller
 * File: Prototype/mobile_app/app.js
 * 
 * Features:
 *  - 60% Video Viewport / 40% Control Cockpit
 *  - Slow (35%), Medium (65%), Fast (100%) Speed Presets + Continuous Slider
 *  - Skid-Steer Differential Kinematics with Turn Angle / Sensitivity Scaling (K_steer)
 *  - Motor Drift Trim Calibration (-25% to +25%) for Straight-Line Precision
 *  - Live Direction Vector (▲ FWD, ▼ REV, ◄ LEFT, ► RIGHT, ⮡ CURVE) & PWM Gauges
 *  - Invert Direction Toggles (Steer / Throttle)
 *  - Direct Camera Stream (Port 81 with Port 80 fallback) + Reconnect Button
 *  - Timed 200ms Chemical Spray Micro-Burst
 */

// ======================== DEFAULT CONFIGURATION ========================
const DEFAULT_CONFIG = {
  host: (window.location.hostname && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
        ? window.location.hostname 
        : '192.168.4.1',
  ctrlPort: 80,
  streamPort: 81,
  sprayMs: 200,
  turnSens: 0.75,      // Steering angle / turn multiplier (0.3x to 1.2x)
  steeringTrim: 0,     // Straight line drift compensation (-25% to +25%)
  invertSteer: false,  // Invert left/right
  invertThrottle: false,// Invert forward/backward
  deadzone: 0.08       // Center deadband to eliminate thumb jitter
};

let config = { ...DEFAULT_CONFIG };

// Load persistent settings from localStorage
try {
  const saved = localStorage.getItem('agrirover_config_v2');
  if (saved) {
    config = { ...config, ...JSON.parse(saved) };
  }
} catch (e) {
  console.warn('Storage unavailable:', e);
}

// Runtime State
let currentSpeedPercent = 65; // Default Cruise (MED)
let flashState = 0;
let isConnected = false;
let lastSendTime = 0;
const SEND_INTERVAL_MS = 50; // 20Hz update rate

// DOM References: Video & HUD
const streamImg = document.getElementById('camera-stream');
const streamPlaceholder = document.getElementById('stream-placeholder');
const streamTargetLabel = document.getElementById('stream-target-label');
const btnReconnectStream = document.getElementById('btn-reconnect-stream');
const connBadge = document.getElementById('conn-badge');
const hudBattery = document.getElementById('hud-battery');
const hudPing = document.getElementById('hud-ping');
const sprayBanner = document.getElementById('spray-banner');
const reticle = document.getElementById('reticle');

// Motion & Motor HUD
const hudMotionVector = document.getElementById('hud-motion-vector');
const hudLeftPwm = document.getElementById('hud-left-pwm');
const hudRightPwm = document.getElementById('hud-right-pwm');

// Joystick DOM
const joystickBase = document.getElementById('joystick-base');
const joystickThumb = document.getElementById('joystick-thumb');

// Speed Controls
const btnSpeedSlow = document.getElementById('btn-speed-slow');
const btnSpeedMed = document.getElementById('btn-speed-med');
const btnSpeedFast = document.getElementById('btn-speed-fast');
const speedButtons = [btnSpeedSlow, btnSpeedMed, btnSpeedFast];
const speedSlider = document.getElementById('speed-slider');
const speedDisplayLabel = document.getElementById('speed-display-label');

// Tactical Action Buttons
const btnSpray = document.getElementById('btn-spray');
const btnFlash = document.getElementById('btn-flash');
const btnCalibrate = document.getElementById('btn-calibrate');
const btnStop = document.getElementById('btn-stop');

// Settings & Calibration Modal DOM
const settingsModal = document.getElementById('settings-modal');
const btnSettings = document.getElementById('btn-settings');
const modalClose = document.getElementById('modal-close');
const cfgHostInput = document.getElementById('cfg-host');
const cfgCtrlPortInput = document.getElementById('cfg-ctrl-port');
const cfgStreamPortInput = document.getElementById('cfg-stream-port');
const cfgSprayMsInput = document.getElementById('cfg-spray-ms');
const cfgTurnSens = document.getElementById('cfg-turn-sens');
const valTurnSens = document.getElementById('val-turn-sens');
const cfgSteeringTrim = document.getElementById('cfg-steering-trim');
const valSteeringTrim = document.getElementById('val-steering-trim');
const cfgInvertSteer = document.getElementById('cfg-invert-steer');
const cfgInvertThrottle = document.getElementById('cfg-invert-throttle');
const btnSaveSettings = document.getElementById('btn-save-settings');
const btnResetSettings = document.getElementById('btn-reset-settings');

// ======================== CAMERA STREAM ENGINE ========================
function initCameraStream() {
  const primaryUrl = `http://${config.host}:${config.streamPort}/stream`;
  const fallbackUrl = `http://${config.host}:${config.ctrlPort}/stream`;

  streamTargetLabel.textContent = primaryUrl;
  streamPlaceholder.style.display = 'flex';

  streamImg.onload = () => {
    streamPlaceholder.style.display = 'none';
    setConnectionState(true);
  };

  streamImg.onerror = () => {
    // If port 81 fails, fallback to port 80 /stream
    if (streamImg.src !== fallbackUrl) {
      console.log('Stream port 81 unreached, trying fallback port', config.ctrlPort);
      streamImg.src = fallbackUrl;
      streamTargetLabel.textContent = fallbackUrl;
    } else {
      setConnectionState(false);
      streamPlaceholder.style.display = 'flex';
    }
  };

  streamImg.src = primaryUrl;
}

if (btnReconnectStream) {
  btnReconnectStream.addEventListener('click', (e) => {
    e.stopPropagation();
    initCameraStream();
  });
}

function setConnectionState(connected) {
  isConnected = connected;
  if (connected) {
    connBadge.textContent = 'ONLINE';
    connBadge.className = 'connection-badge status-connected';
  } else {
    connBadge.textContent = 'OFFLINE';
    connBadge.className = 'connection-badge status-disconnected';
    hudPing.textContent = '-- ms';
  }
}

// ======================== REST API DISPATCHER ========================
async function sendDriveCommand(left, right) {
  const url = `http://${config.host}:${config.ctrlPort}/drive?left=${left}&right=${right}`;
  try {
    const t0 = performance.now();
    const res = await fetch(url, { signal: AbortSignal.timeout(400) });
    if (res.ok) {
      const ping = Math.round(performance.now() - t0);
      hudPing.textContent = `${ping} ms`;
      setConnectionState(true);
    }
  } catch (err) {
    setConnectionState(false);
  }
}

async function triggerSpray(ms = config.sprayMs) {
  btnSpray.classList.add('firing');
  sprayBanner.classList.add('active');
  reticle.style.borderColor = 'rgba(231, 76, 60, 0.8)';

  const url = `http://${config.host}:${config.ctrlPort}/spray?ms=${ms}`;
  try {
    await fetch(url, { signal: AbortSignal.timeout(1000) });
  } catch (e) {
    console.error('Spray trigger failed:', e);
  }

  setTimeout(() => {
    btnSpray.classList.remove('firing');
    sprayBanner.classList.remove('active');
    reticle.style.borderColor = '';
  }, ms);
}

async function toggleFlash() {
  flashState = flashState === 0 ? 180 : 0;
  if (flashState > 0) {
    btnFlash.classList.add('active');
  } else {
    btnFlash.classList.remove('active');
  }

  const url = `http://${config.host}:${config.ctrlPort}/flash?val=${flashState}`;
  try {
    await fetch(url, { signal: AbortSignal.timeout(800) });
  } catch (e) {
    console.error('Flash toggle failed:', e);
  }
}

function emergencyStop() {
  sendDriveCommand(0, 0);
  resetJoystickVisual();
  updateMotionHud(0, 0, 0, 0);
}

// Periodic Telemetry Heartbeat (every 2.5s if idle)
setInterval(async () => {
  if (!isConnected) {
    try {
      const t0 = performance.now();
      const res = await fetch(`http://${config.host}:${config.ctrlPort}/drive?left=0&right=0`, {
        signal: AbortSignal.timeout(600)
      });
      if (res.ok) {
        setConnectionState(true);
        hudPing.textContent = `${Math.round(performance.now() - t0)} ms`;
      }
    } catch (_) {
      setConnectionState(false);
    }
  }
}, 2500);

// ======================== SPEED REGIME CONTROLLER ========================
function applySpeed(percent, source = 'button') {
  currentSpeedPercent = Math.max(25, Math.min(100, Math.round(percent)));
  speedSlider.value = currentSpeedPercent;

  // Determine label tag
  let tag = 'CUSTOM';
  if (currentSpeedPercent === 35) tag = 'SLOW';
  else if (currentSpeedPercent === 65) tag = 'MED';
  else if (currentSpeedPercent === 100) tag = 'FAST';

  speedDisplayLabel.textContent = `${currentSpeedPercent}% (${tag})`;

  // Highlight button if matching
  speedButtons.forEach(btn => {
    const val = parseInt(btn.dataset.speed, 10);
    if (val === currentSpeedPercent) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

// Preset Buttons (Slow, Med, Fast)
speedButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const speed = parseInt(btn.dataset.speed, 10);
    applySpeed(speed, 'button');
  });
});

// Fine-Tuning Slider
speedSlider.addEventListener('input', (e) => {
  applySpeed(parseInt(e.target.value, 10), 'slider');
});

// ======================== KINEMATIC & MOTION VECTOR ENGINE ========================
let isDragging = false;
let joystickCenter = { x: 0, y: 0 };
const maxRadius = 45; // pixels within 135px base

function resetJoystickVisual() {
  joystickThumb.style.transform = 'translate(0px, 0px)';
}

function updateJoystickCenter() {
  const rect = joystickBase.getBoundingClientRect();
  joystickCenter = {
    x: rect.left + rect.width / 2,
    y: rect.top + rect.height / 2
  };
}

function updateMotionHud(leftPWM, rightPWM, throttle, steer) {
  hudLeftPwm.textContent = `L: ${leftPWM}`;
  hudRightPwm.textContent = `R: ${rightPWM}`;

  if (leftPWM === 0 && rightPWM === 0) {
    hudMotionVector.textContent = '■ STOPPED';
    hudMotionVector.style.color = '#8b9bb4';
    return;
  }

  hudMotionVector.style.color = 'var(--accent-green)';

  const absThrot = Math.abs(throttle);
  const absSteer = Math.abs(steer);

  if (throttle > 0.15 && absSteer <= 0.25) {
    hudMotionVector.textContent = `▲ FORWARD ${currentSpeedPercent}%`;
  } else if (throttle < -0.15 && absSteer <= 0.25) {
    hudMotionVector.textContent = `▼ REVERSE ${currentSpeedPercent}%`;
  } else if (steer > 0.25 && absThrot <= 0.25) {
    hudMotionVector.textContent = '► PIVOT RIGHT';
  } else if (steer < -0.25 && absThrot <= 0.25) {
    hudMotionVector.textContent = '◄ PIVOT LEFT';
  } else if (throttle > 0.15 && steer > 0.25) {
    hudMotionVector.textContent = '⮡ CURVE RIGHT';
  } else if (throttle > 0.15 && steer < -0.25) {
    hudMotionVector.textContent = '⮢ CURVE LEFT';
  } else if (throttle < -0.15 && steer > 0.25) {
    hudMotionVector.textContent = '⮣ REV RIGHT';
  } else if (throttle < -0.15 && steer < -0.25) {
    hudMotionVector.textContent = '⮠ REV LEFT';
  } else {
    hudMotionVector.textContent = `● ACTIVE (${currentSpeedPercent}%)`;
  }
}

function handlePointerStart(clientX, clientY) {
  isDragging = true;
  updateJoystickCenter();
  handlePointerMove(clientX, clientY);
}

function handlePointerMove(clientX, clientY) {
  if (!isDragging) return;

  let dx = clientX - joystickCenter.x;
  let dy = clientY - joystickCenter.y;
  const distance = Math.hypot(dx, dy);

  if (distance > maxRadius) {
    dx = (dx / distance) * maxRadius;
    dy = (dy / distance) * maxRadius;
  }

  joystickThumb.style.transform = `translate(${dx}px, ${dy}px)`;

  // Normalized raw inputs (-1.0 to +1.0)
  let throttle = -dy / maxRadius; // Up = positive
  let steer = dx / maxRadius;     // Right = positive

  // Invert options
  if (config.invertThrottle) throttle = -throttle;
  if (config.invertSteer) steer = -steer;

  // Central deadzone filter to stop thumb micro-jitters
  const mag = Math.hypot(throttle, steer);
  if (mag < config.deadzone) {
    throttle = 0;
    steer = 0;
  }

  // Turn Sensitivity Scaling (K_steer)
  const scaledSteer = steer * config.turnSens;

  // Differential Skid-Steer Mixer
  let left = throttle + scaledSteer;
  let right = throttle - scaledSteer;

  // Straight-line Motor Drift Trim Compensation
  if (config.steeringTrim !== 0 && Math.abs(throttle) > 0.05) {
    const trimFactor = config.steeringTrim / 100;
    if (trimFactor > 0) {
      right *= (1 - trimFactor); // Pulls left: trim right motor down
    } else {
      left *= (1 + trimFactor);  // Pulls right: trim left motor down
    }
  }

  // Calculate PWM values scaled to active speed ceiling
  const maxPWM = Math.round((currentSpeedPercent / 100) * 255);
  const leftPWM = Math.round(Math.max(-255, Math.min(255, left * maxPWM)));
  const rightPWM = Math.round(Math.max(-255, Math.min(255, right * maxPWM)));

  updateMotionHud(leftPWM, rightPWM, throttle, steer);

  // Throttled Network Dispatch (20Hz)
  const now = performance.now();
  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;
    sendDriveCommand(leftPWM, rightPWM);
  }
}

function handlePointerEnd() {
  if (!isDragging) return;
  isDragging = false;
  resetJoystickVisual();
  emergencyStop();
}

// Touch Event Handlers
joystickBase.addEventListener('touchstart', (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  handlePointerStart(touch.clientX, touch.clientY);
}, { passive: false });

window.addEventListener('touchmove', (e) => {
  if (isDragging) {
    e.preventDefault();
    const touch = e.touches[0];
    handlePointerMove(touch.clientX, touch.clientY);
  }
}, { passive: false });

window.addEventListener('touchend', handlePointerEnd);
window.addEventListener('touchcancel', handlePointerEnd);

// Mouse Event Handlers (for Desktop Pair-Testing)
joystickBase.addEventListener('mousedown', (e) => {
  handlePointerStart(e.clientX, e.clientY);
});

window.addEventListener('mousemove', (e) => {
  if (isDragging) {
    handlePointerMove(e.clientX, e.clientY);
  }
});

window.addEventListener('mouseup', handlePointerEnd);

// Tactical Button Handlers
btnSpray.addEventListener('click', () => triggerSpray());
btnFlash.addEventListener('click', toggleFlash);
btnStop.addEventListener('click', emergencyStop);
if (btnCalibrate) {
  btnCalibrate.addEventListener('click', openSettingsModal);
}

// ======================== CALIBRATION & SETTINGS MODAL ========================
function openSettingsModal() {
  cfgHostInput.value = config.host;
  cfgCtrlPortInput.value = config.ctrlPort;
  cfgStreamPortInput.value = config.streamPort;
  cfgSprayMsInput.value = config.sprayMs;
  cfgTurnSens.value = config.turnSens;
  valTurnSens.textContent = `${config.turnSens.toFixed(2)}x`;
  cfgSteeringTrim.value = config.steeringTrim;
  valSteeringTrim.textContent = `${config.steeringTrim > 0 ? '+' : ''}${config.steeringTrim}%`;
  cfgInvertSteer.checked = config.invertSteer;
  cfgInvertThrottle.checked = config.invertThrottle;
  settingsModal.classList.add('open');
}

btnSettings.addEventListener('click', openSettingsModal);

modalClose.addEventListener('click', () => {
  settingsModal.classList.remove('open');
});

settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) {
    settingsModal.classList.remove('open');
  }
});

// Real-time slider labels in modal
cfgTurnSens.addEventListener('input', (e) => {
  valTurnSens.textContent = `${parseFloat(e.target.value).toFixed(2)}x`;
});

cfgSteeringTrim.addEventListener('input', (e) => {
  const v = parseInt(e.target.value, 10);
  valSteeringTrim.textContent = `${v > 0 ? '+' : ''}${v}%`;
});

btnSaveSettings.addEventListener('click', () => {
  config.host = cfgHostInput.value.trim() || DEFAULT_CONFIG.host;
  config.ctrlPort = parseInt(cfgCtrlPortInput.value, 10) || 80;
  config.streamPort = parseInt(cfgStreamPortInput.value, 10) || 81;
  config.sprayMs = parseInt(cfgSprayMsInput.value, 10) || 200;
  config.turnSens = parseFloat(cfgTurnSens.value) || 0.75;
  config.steeringTrim = parseInt(cfgSteeringTrim.value, 10) || 0;
  config.invertSteer = cfgInvertSteer.checked;
  config.invertThrottle = cfgInvertThrottle.checked;

  try {
    localStorage.setItem('agrirover_config_v2', JSON.stringify(config));
  } catch (e) {}

  settingsModal.classList.remove('open');
  initCameraStream();
});

btnResetSettings.addEventListener('click', () => {
  config = { ...DEFAULT_CONFIG };
  localStorage.removeItem('agrirover_config_v2');
  openSettingsModal();
  initCameraStream();
});

// ======================== INITIALIZATION & PWA SERVICE WORKER ========================
window.addEventListener('DOMContentLoaded', () => {
  applySpeed(65); // Initialize MED cruise speed
  initCameraStream();

  // Register PWA Service Worker for standalone home screen installation
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => console.log('[PWA] Service Worker registered:', reg.scope))
      .catch(err => console.warn('[PWA] Service Worker registration failed:', err));
  }
});

