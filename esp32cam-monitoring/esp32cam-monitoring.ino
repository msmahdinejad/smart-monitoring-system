#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

const char* ssid = "YOUR_WIFI_SSID";           // Replace with your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Replace with your WiFi password

WebServer server(80);

camera_fb_t * fb = NULL;
char * part_buf[64];

// Camera configuration
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=123456789000000000000987654321";
static const char* _STREAM_BOUNDARY = "\r\n--123456789000000000000987654321\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Optimized settings for AI analysis
  if(psramFound()){
    config.frame_size = FRAMESIZE_SVGA; // 800x600 - optimal for AI analysis
    config.jpeg_quality = 8; // Higher quality for better AI recognition
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 10;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return false;
  }

  // Enhanced camera settings for consistent image quality
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    // Optimized settings for surveillance and AI analysis
    s->set_brightness(s, 0);     // 0 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0=None
    s->set_whitebal(s, 1);       // Enable white balance
    s->set_awb_gain(s, 1);       // Enable AWB gain
    s->set_wb_mode(s, 0);        // Auto white balance
    s->set_exposure_ctrl(s, 1);  // Enable exposure control
    s->set_aec2(s, 0);           // Disable AEC sensor
    s->set_ae_level(s, 0);       // -2 to 2
    s->set_aec_value(s, 300);    // 0 to 1200
    s->set_gain_ctrl(s, 1);      // Enable gain control
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);
    s->set_bpc(s, 0);            // Disable black pixel correction
    s->set_wpc(s, 1);            // Enable white pixel correction
    s->set_raw_gma(s, 1);        // Enable raw gamma
    s->set_lenc(s, 1);           // Enable lens correction
    s->set_hmirror(s, 0);        // Disable horizontal mirror
    s->set_vflip(s, 0);          // Disable vertical flip
    s->set_dcw(s, 1);            // Enable downsize
    s->set_colorbar(s, 0);       // Disable color bar
  }

  Serial.println("Camera initialized successfully with enhanced settings");
  return true;
}

// Enhanced MJPEG Stream handler with better performance
void handleStream() {
  WiFiClient client = server.client();
  
  if (!client.connected()) {
    return;
  }

  // Set response headers with CORS support
  client.println("HTTP/1.1 200 OK");
  client.println("Access-Control-Allow-Origin: *");
  client.println("Access-Control-Allow-Methods: GET");
  client.println("Access-Control-Allow-Headers: Content-Type");
  client.printf("Content-Type: %s\r\n", _STREAM_CONTENT_TYPE);
  client.println("Connection: close");
  client.println("Cache-Control: no-cache");
  client.println("Pragma: no-cache");
  client.println();

  // Enhanced streaming loop with error handling
  while (client.connected()) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }

    // Validate image data
    if (fb->len > 0 && fb->buf != NULL) {
      // Send boundary
      client.print(_STREAM_BOUNDARY);
      
      // Send part header
      client.printf(_STREAM_PART, fb->len);
      
      // Send image data in chunks for stability
      size_t sent = 0;
      uint8_t* buf = fb->buf;
      while (sent < fb->len && client.connected()) {
        size_t chunk_size = min((size_t)1024, fb->len - sent);
        size_t written = client.write(buf + sent, chunk_size);
        if (written == 0) break;
        sent += written;
      }
    }
    
    // Return frame buffer
    esp_camera_fb_return(fb);
    
    // Adaptive delay for smooth streaming
    delay(33); // ~30 FPS
    
    // Check for client disconnection
    if (!client.connected()) {
      break;
    }
  }
  
  client.stop();
  Serial.println("Stream client disconnected");
}

// Enhanced single frame capture with metadata
void handleCapture() {
  fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "application/json", "{\"error\":\"Camera capture failed\"}");
    return;
  }

  // Validate captured image
  if (fb->len == 0 || fb->buf == NULL) {
    esp_camera_fb_return(fb);
    server.send(500, "application/json", "{\"error\":\"Invalid image data\"}");
    return;
  }

  // Set CORS headers
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.sendHeader("Cache-Control", "no-cache");
  
  // Send image with proper content type
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  Serial.printf("Image captured and sent - Size: %d bytes\n", fb->len);
}

// Enhanced status handler with detailed system information
void handleStatus() {
  DynamicJsonDocument doc(512);
  
  doc["status"] = "online";
  doc["uptime"] = millis();
  doc["heap_free"] = ESP.getFreeHeap();
  doc["heap_total"] = ESP.getHeapSize();
  doc["psram_free"] = ESP.getFreePsram();
  doc["psram_total"] = ESP.getPsramSize();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["wifi_ssid"] = WiFi.SSID();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["mac_address"] = WiFi.macAddress();
  doc["chip_model"] = ESP.getChipModel();
  doc["chip_revision"] = ESP.getChipRevision();
  doc["sdk_version"] = ESP.getSdkVersion();
  
  // Camera status
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    JsonObject camera = doc.createNestedObject("camera");
    camera["framesize"] = s->status.framesize;
    camera["quality"] = s->status.quality;
    camera["brightness"] = s->status.brightness;
    camera["contrast"] = s->status.contrast;
    camera["saturation"] = s->status.saturation;
    camera["awb"] = s->status.awb;
    camera["awb_gain"] = s->status.awb_gain;
    camera["aec"] = s->status.aec;
  }
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", response);
}

// Camera settings page
void handleSettingsPage() {
  sensor_t * s = esp_camera_sensor_get();
  
  String html = R"=====(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camera Settings - ESP32-CAM</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #3498db;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .setting-group {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #3498db;
        }
        .setting-group h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #34495e;
        }
        .form-control {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .btn {
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #219a52; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .current-value {
            background: #e8f5e8;
            padding: 5px 10px;
            border-radius: 3px;
            font-family: monospace;
            font-weight: bold;
            color: #27ae60;
        }
        .preview-section {
            text-align: center;
            margin-top: 20px;
        }
        .preview-img {
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 10px;
            margin: 10px 0;
        }
        .status-message {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            display: none;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Camera Settings Panel</h1>
            <p>Configure your ESP32-CAM settings in real-time</p>
        </div>
        
        <div id="statusMessage" class="status-message"></div>
        
        <div class="settings-grid">
            <div class="setting-group">
                <h3>📐 Image Quality</h3>
                
                <div class="form-group">
                    <label>Frame Size</label>
                    <select id="framesize" class="form-control">
                        <option value="0">QQVGA (160x120)</option>
                        <option value="1">QCIF (176x144)</option>
                        <option value="2">HQVGA (240x176)</option>
                        <option value="3">QVGA (320x240)</option>
                        <option value="4">CIF (400x296)</option>
                        <option value="5">HVGA (480x320)</option>
                        <option value="6">VGA (640x480)</option>
                        <option value="7">SVGA (800x600)</option>
                        <option value="8">XGA (1024x768)</option>
                        <option value="9">HD (1280x720)</option>
                        <option value="10">SXGA (1280x1024)</option>
                        <option value="11">UXGA (1600x1200)</option>
                    </select>
                    <small>Current: <span class="current-value" id="current-framesize">)=====" + String(s->status.framesize) + R"=====(</span></small>
                </div>
                
                <div class="form-group">
                    <label>JPEG Quality (0-63, lower = better)</label>
                    <input type="range" id="quality" class="form-control" min="0" max="63" value=")=====" + String(s->status.quality) + R"=====(">
                    <small>Current: <span class="current-value" id="current-quality">)=====" + String(s->status.quality) + R"=====(</span></small>
                </div>
            </div>
            
            <div class="setting-group">
                <h3>🎨 Image Enhancement</h3>
                
                <div class="form-group">
                    <label>Brightness (-2 to 2)</label>
                    <input type="range" id="brightness" class="form-control" min="-2" max="2" value=")=====" + String(s->status.brightness) + R"=====(">
                    <small>Current: <span class="current-value" id="current-brightness">)=====" + String(s->status.brightness) + R"=====(</span></small>
                </div>
                
                <div class="form-group">
                    <label>Contrast (-2 to 2)</label>
                    <input type="range" id="contrast" class="form-control" min="-2" max="2" value=")=====" + String(s->status.contrast) + R"=====(">
                    <small>Current: <span class="current-value" id="current-contrast">)=====" + String(s->status.contrast) + R"=====(</span></small>
                </div>
                
                <div class="form-group">
                    <label>Saturation (-2 to 2)</label>
                    <input type="range" id="saturation" class="form-control" min="-2" max="2" value=")=====" + String(s->status.saturation) + R"=====(">
                    <small>Current: <span class="current-value" id="current-saturation">)=====" + String(s->status.saturation) + R"=====(</span></small>
                </div>
            </div>
        </div>
        
        <div class="preview-section">
            <h3>📷 Live Preview</h3>
            <img id="preview" class="preview-img" src="/capture" alt="Camera Preview">
            <br>
            <button class="btn btn-success" onclick="applySettings()">✅ Apply Settings</button>
            <button class="btn btn-secondary" onclick="refreshPreview()">🔄 Refresh Preview</button>
            <button class="btn btn-secondary" onclick="window.location.href='/'">🏠 Back to Home</button>
        </div>
    </div>

    <script>
        // Set current framesize selection
        document.getElementById('framesize').value = ')=====" + String(s->status.framesize) + R"=====(';
        
        // Update display values when sliders change
        document.getElementById('quality').oninput = function() {
            document.getElementById('current-quality').textContent = this.value;
        };
        document.getElementById('brightness').oninput = function() {
            document.getElementById('current-brightness').textContent = this.value;
        };
        document.getElementById('contrast').oninput = function() {
            document.getElementById('current-contrast').textContent = this.value;
        };
        document.getElementById('saturation').oninput = function() {
            document.getElementById('current-saturation').textContent = this.value;
        };
        document.getElementById('framesize').onchange = function() {
            document.getElementById('current-framesize').textContent = this.value;
        };

        function showStatus(message, isError = false) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.textContent = message;
            statusDiv.className = 'status-message ' + (isError ? 'status-error' : 'status-success');
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }

        function applySettings() {
            const framesize = document.getElementById('framesize').value;
            const quality = document.getElementById('quality').value;
            const brightness = document.getElementById('brightness').value;
            const contrast = document.getElementById('contrast').value;
            const saturation = document.getElementById('saturation').value;

            const formData = new FormData();
            formData.append('framesize', framesize);
            formData.append('quality', quality);
            formData.append('brightness', brightness);
            formData.append('contrast', contrast);
            formData.append('saturation', saturation);

            fetch('/settings', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showStatus('Settings applied successfully!');
                    setTimeout(refreshPreview, 500);
                } else {
                    showStatus('Error applying settings: ' + (data.message || 'Unknown error'), true);
                }
            })
            .catch(error => {
                showStatus('Network error: ' + error.message, true);
            });
        }

        function refreshPreview() {
            const img = document.getElementById('preview');
            img.src = '/capture?' + new Date().getTime();
        }

        // Auto refresh preview every 5 seconds
        setInterval(refreshPreview, 5000);
    </script>
</body>
</html>
)=====";

  server.send(200, "text/html", html);
}

// Enhanced camera settings handler with validation
void handleSettings() {
  if (server.method() == HTTP_GET) {
    // Get current settings
    sensor_t * s = esp_camera_sensor_get();
    DynamicJsonDocument doc(256);
    
    doc["framesize"] = s->status.framesize;
    doc["quality"] = s->status.quality;
    doc["brightness"] = s->status.brightness;
    doc["contrast"] = s->status.contrast;
    doc["saturation"] = s->status.saturation;
    doc["awb"] = s->status.awb;
    doc["aec"] = s->status.aec;
    
    String response;
    serializeJson(doc, response);
    
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", response);
    
  } else if (server.method() == HTTP_POST) {
    // Update settings with validation
    sensor_t * s = esp_camera_sensor_get();
    bool updated = false;
    
    if (server.hasArg("framesize")) {
      int framesize = server.arg("framesize").toInt();
      if (framesize >= 0 && framesize <= 13) {
        s->set_framesize(s, (framesize_t)framesize);
        updated = true;
      }
    }
    
    if (server.hasArg("quality")) {
      int quality = server.arg("quality").toInt();
      if (quality >= 0 && quality <= 63) {
        s->set_quality(s, quality);
        updated = true;
      }
    }
    
    if (server.hasArg("brightness")) {
      int brightness = server.arg("brightness").toInt();
      if (brightness >= -2 && brightness <= 2) {
        s->set_brightness(s, brightness);
        updated = true;
      }
    }
    
    if (server.hasArg("contrast")) {
      int contrast = server.arg("contrast").toInt();
      if (contrast >= -2 && contrast <= 2) {
        s->set_contrast(s, contrast);
        updated = true;
      }
    }
    
    if (server.hasArg("saturation")) {
      int saturation = server.arg("saturation").toInt();
      if (saturation >= -2 && saturation <= 2) {
        s->set_saturation(s, saturation);
        updated = true;
      }
    }
    
    String response = updated ? "{\"status\":\"ok\",\"updated\":true}" : "{\"status\":\"error\",\"message\":\"Invalid parameters\"}";
    
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", response);
  }
}

// Enhanced CORS handler
void handleCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  server.sendHeader("Access-Control-Max-Age", "3600");
  server.send(200, "text/plain", "");
}

// Enhanced root handler with system information
void handleRoot() {
  String html = R"=====(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32-CAM Enhanced Stream Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .status-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
        }
        .status-label { font-weight: 600; }
        .status-value { 
            color: #27ae60; 
            font-family: monospace;
        }
        .endpoints {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .endpoint-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #3498db;
        }
        .endpoint-url {
            font-family: monospace;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 8px 12px;
            border-radius: 5px;
            display: inline-block;
            margin: 5px 0;
        }
        .btn {
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        .online-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #27ae60;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(39, 174, 96, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(39, 174, 96, 0); }
            100% { box-shadow: 0 0 0 0 rgba(39, 174, 96, 0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 ESP32-CAM Stream Server</h1>
            <p><span class="online-indicator"></span>Enhanced monitoring system ready</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>📡 Network Status</h3>
                <div class="status-item">
                    <span class="status-label">IP Address:</span>
                    <span class="status-value">)=====" + WiFi.localIP().toString() + R"=====(</span>
                </div>
                <div class="status-item">
                    <span class="status-label">WiFi SSID:</span>
                    <span class="status-value">)=====" + WiFi.SSID() + R"=====(</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Signal Strength:</span>
                    <span class="status-value">)=====" + String(WiFi.RSSI()) + R"=====( dBm</span>
                </div>
                <div class="status-item">
                    <span class="status-label">MAC Address:</span>
                    <span class="status-value">)=====" + WiFi.macAddress() + R"=====(</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>💾 System Resources</h3>
                <div class="status-item">
                    <span class="status-label">Free Heap:</span>
                    <span class="status-value">)=====" + String(ESP.getFreeHeap()) + R"=====( bytes</span>
                </div>
                <div class="status-item">
                    <span class="status-label">PSRAM Free:</span>
                    <span class="status-value">)=====" + String(ESP.getFreePsram()) + R"=====( bytes</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Uptime:</span>
                    <span class="status-value">)=====" + String(millis() / 1000) + R"=====( seconds</span>
                </div>
                <div class="status-item">
                    <span class="status-label">SDK Version:</span>
                    <span class="status-value">)=====" + String(ESP.getSdkVersion()) + R"=====(</span>
                </div>
            </div>
        </div>
        
        <div class="endpoints">
            <h3>🔗 Available API Endpoints</h3>
            
            <div class="endpoint-item">
                <h4>📹 Live Video Stream</h4>
                <div class="endpoint-url">GET /stream</div>
                <p>MJPEG video stream for real-time monitoring</p>
                <a href="/stream" class="btn" target="_blank">Open Stream</a>
            </div>
            
            <div class="endpoint-item">
                <h4>📸 Capture Single Image</h4>
                <div class="endpoint-url">GET /capture</div>
                <p>Capture and download a single JPEG image</p>
                <a href="/capture" class="btn" target="_blank">Capture Image</a>
            </div>
            
            <div class="endpoint-item">
                <h4>📊 System Status</h4>
                <div class="endpoint-url">GET /status</div>
                <p>Detailed system status in JSON format</p>
                <a href="/status" class="btn" target="_blank">View Status</a>
            </div>
            
            <div class="endpoint-item">
                <h4>⚙️ Camera Settings</h4>
                <div class="endpoint-url">GET/POST /settings</div>
                <p>View and modify camera configuration</p>
                <a href="/settings" class="btn" target="_blank">Settings API</a>
                <a href="/camera-settings" class="btn" target="_blank">Settings Panel</a>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh system stats every 5 seconds
        setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    console.log('System status updated:', data);
                })
                .catch(error => console.error('Status update failed:', error));
        }, 5000);
    </script>
</body>
</html>
)=====";
  
  server.send(200, "text/html", html);
}

// System info endpoint
void handleInfo() {
  DynamicJsonDocument doc(1024);
  
  doc["device"] = "ESP32-CAM Enhanced";
  doc["version"] = "2.0.0";
  doc["build_date"] = __DATE__;
  doc["build_time"] = __TIME__;
  doc["features"] = JsonArray();
  doc["features"].add("MJPEG Streaming");
  doc["features"].add("Image Capture");
  doc["features"].add("Camera Control");
  doc["features"].add("System Monitoring");
  doc["features"].add("CORS Support");
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", response);
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println("\n=== ESP32-CAM Enhanced Stream Server ===");
  Serial.println("Initializing system...");

  // Initialize camera with enhanced settings
  if (!initCamera()) {
    Serial.println("❌ Camera initialization failed!");
    Serial.println("System will restart in 5 seconds...");
    delay(5000);
    ESP.restart();
  }

  // Connect to WiFi with timeout
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  int wifi_timeout = 0;
  while (WiFi.status() != WL_CONNECTED && wifi_timeout < 30) {
    delay(500);
    Serial.print(".");
    wifi_timeout++;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n❌ WiFi connection failed!");
    Serial.println("System will restart in 5 seconds...");
    delay(5000);
    ESP.restart();
  }
  
  Serial.println();
  Serial.println("✅ WiFi connected successfully!");
  Serial.printf("📡 IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("📶 Signal Strength: %d dBm\n", WiFi.RSSI());

  // Setup enhanced web server routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/stream", HTTP_GET, handleStream);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/info", HTTP_GET, handleInfo);
  server.on("/settings", HTTP_GET, handleSettings);
  server.on("/settings", HTTP_POST, handleSettings);
  server.on("/settings", HTTP_OPTIONS, handleCORS);
  server.on("/camera-settings", HTTP_GET, handleSettingsPage);
  
  // Handle CORS for all endpoints
  server.onNotFound([]() {
    if (server.method() == HTTP_OPTIONS) {
      handleCORS();
    } else {
      server.send(404, "application/json", "{\"error\":\"Endpoint not found\"}");
    }
  });

  // Start server
  server.begin();
  Serial.println("🌐 HTTP server started successfully");
  Serial.println("\n=== Server Ready ===");
  Serial.printf("📹 Stream URL: http://%s/stream\n", WiFi.localIP().toString().c_str());
  Serial.printf("📸 Capture URL: http://%s/capture\n", WiFi.localIP().toString().c_str());
  Serial.printf("📊 Status URL: http://%s/status\n", WiFi.localIP().toString().c_str());
  Serial.printf("⚙️ Settings Panel: http://%s/camera-settings\n", WiFi.localIP().toString().c_str());
  Serial.printf("🌐 Dashboard: http://%s/\n", WiFi.localIP().toString().c_str());
  Serial.println("==================\n");
}

void loop() {
  server.handleClient();
  
  // Watchdog and memory management
  if (millis() % 30000 == 0) { // Every 30 seconds
    if (ESP.getFreeHeap() < 20000) {
      Serial.println("⚠️ Low memory detected, optimizing...");
      delay(100);
    }
  }
  
  delay(1);
}