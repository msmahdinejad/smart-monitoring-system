"""
Web Routes Controller
Handles web interface routes and static file serving
"""

from flask import Blueprint, render_template_string, send_from_directory

try:
    from config import ESP32_CAM_CONFIG, IMAGES_DIR
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

web_bp = Blueprint('web', __name__)

# HTML Templates
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Monitoring System</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .video-indicator {
            display: inline-flex;
            align-items: center;
            background: #e74c3c;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .video-indicator i {
            margin-right: 5px;
        }
        .mode-selector {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }
        .mode-btn {
            display: inline-block;
            padding: 15px 30px;
            margin: 10px;
            border: 2px solid #667eea;
            border-radius: 10px;
            background: white;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .mode-btn.active {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        .mode-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        .content-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            display: none;
        }
        .content-panel.active {
            display: block;
        }
        .status-card {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .status-card.active {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 5px;
            text-decoration: none;
        }
        .btn i { margin-right: 8px; }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #56ab2f, #a8e6cf);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .stream-container {
            text-align: center;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        .stream-img {
            width: 100%;
            max-width: 800px;
            height: auto;
        }
        .prompt-styles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .prompt-style {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .prompt-style.selected {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }
        .recent-records {
            margin-top: 30px;
        }
        .record-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .record-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .status-badge {
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .status-normal { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-danger { background: #f8d7da; color: #721c24; }
        .video-badge {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            margin-left: 5px;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .custom-input-group {
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .custom-input-group.show {
            display: block;
        }
        .telegram-status {
            display: inline-flex;
            align-items: center;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9rem;
            margin-left: 10px;
        }
        .telegram-enabled {
            background: #d4edda;
            color: #155724;
        }
        .telegram-disabled {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-eye"></i> Smart Monitoring System</h1>
            <p>AI-Powered Environmental Analysis with ESP32-CAM & Video Recording</p>
        </div>
        
        <div class="mode-selector">
            <button class="mode-btn active" onclick="setMode('stream')">
                <i class="fas fa-video"></i> Live Stream
            </button>
            <button class="mode-btn" onclick="setMode('monitor')">
                <i class="fas fa-brain"></i> AI Monitoring
            </button>
            <a href="/history" class="mode-btn">
                <i class="fas fa-history"></i> History
            </a>
        </div>
        
        <div id="statusCard" class="status-card">
            <i class="fas fa-circle"></i> <span id="statusText">System Ready</span>
            <span id="telegramStatus" class="telegram-status telegram-disabled">
                <i class="fab fa-telegram"></i> Telegram: Checking...
            </span>
        </div>
        
        <!-- Stream Panel -->
        <div id="streamPanel" class="content-panel active">
            <h3><i class="fas fa-video"></i> Live Camera Stream</h3>
            <div class="stream-container">
                <img id="streamImg" src="http://{{ esp32_ip }}/stream" class="stream-img" alt="Live Stream">
            </div>
            <p style="margin-top: 15px; color: #666;">
                <i class="fas fa-info-circle"></i> Camera monitoring with automatic video recording during analysis
            </p>
        </div>
        
        <!-- Monitor Panel -->
        <div id="monitorPanel" class="content-panel">
            <h3><i class="fas fa-brain"></i> AI Monitoring with Video Recording</h3>
            
            <div class="form-group">
                <label class="form-label"><i class="fas fa-crosshairs"></i> Monitoring Type</label>
                <select id="monitoringType" class="form-control" onchange="toggleCustomInput()">
                    <option value="security">Security & Threat Detection</option>
                    <option value="presence">Human Presence & Activity</option>
                    <option value="lighting">Lighting & Energy Management</option>
                    <option value="classroom">Classroom Environment</option>
                    <option value="workplace">Workplace Monitoring</option>
                    <option value="custom">Custom Monitoring</option>
                </select>
            </div>
            
            <div id="customInputGroup" class="custom-input-group">
                <label class="form-label"><i class="fas fa-edit"></i> Custom Monitoring Instructions</label>
                <textarea id="customInstructions" class="form-control" rows="5" 
                         placeholder="Describe exactly what you want the AI to monitor and analyze...

Examples for Custom Monitoring:
• 'Check if my plants need watering by looking at soil moisture and leaf condition'
• 'Monitor my elderly parent for fall detection and unusual behavior patterns'
• 'Detect if my car is parked properly and hasn't been moved or damaged'
• 'Watch for specific hand gestures or sign language'
• 'Monitor fish tank water level and fish activity'
• 'Check if manufacturing equipment is running smoothly'
• 'Detect if my pet cat is eating, sleeping, or playing'
• 'Monitor construction site for safety violations'
• 'Check inventory levels on store shelves'
• 'Detect if students are wearing required uniforms'

Be as specific as possible - the AI will focus exactly on what you describe."></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label"><i class="fas fa-comments"></i> Analysis Style</label>
                <div class="prompt-styles">
                    <div class="prompt-style selected" data-style="formal">
                        <strong>Formal</strong><br>
                        <small>Professional</small>
                    </div>
                    <div class="prompt-style" data-style="technical">
                        <strong>Technical</strong><br>
                        <small>Expert Level</small>
                    </div>
                    <div class="prompt-style" data-style="casual">
                        <strong>Casual</strong><br>
                        <small>Easy to Read</small>
                    </div>
                    <div class="prompt-style" data-style="security">
                        <strong>Security</strong><br>
                        <small>Alert Focused</small>
                    </div>
                    <div class="prompt-style" data-style="report">
                        <strong>Report</strong><br>
                        <small>Structured</small>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label"><i class="fas fa-clock"></i> Analysis Interval</label>
                <select id="intervalSelect" class="form-control">
                    <option value="15">15 seconds (Recommended)</option>
                    <option value="30">30 seconds</option>
                    <option value="60">1 minute</option>
                    <option value="120">2 minutes</option>
                    <option value="300">5 minutes</option>
                </select>
                <small style="color: #666; margin-top: 5px; display: block;">
                    <i class="fas fa-video"></i> Video will be recorded for the entire interval duration
                </small>
            </div>
            
            <div class="form-group">
                <label class="form-label"><i class="fas fa-edit"></i> Additional Context (Optional)</label>
                <textarea id="customContext" class="form-control" rows="4" 
                         placeholder="Add specific monitoring instructions or focus areas...

Examples:
• 'Monitor for fire or smoke detection'
• 'Check if the printer is working properly'  
• 'Detect package deliveries at the door'
• 'Monitor computer screens for activity'
• 'Check for water leaks or flooding'
• 'Detect if windows or doors are open'
• 'Monitor pet activity and behavior'
• 'Check for equipment malfunction signs'

Write naturally - describe what you want the AI to watch for."></textarea>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn btn-success" id="startBtn" onclick="startMonitoring()">
                    <i class="fas fa-play"></i> Start Monitoring
                </button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopMonitoring()">
                    <i class="fas fa-stop"></i> Stop
                </button>
                <button class="btn btn-primary" onclick="testCamera()">
                    <i class="fas fa-camera"></i> Test Camera
                </button>
                <button class="btn btn-primary" onclick="testTelegram()">
                    <i class="fab fa-telegram"></i> Test Telegram
                </button>
            </div>
            
            <div id="testResult" class="alert"></div>
        </div>
        
        <!-- Recent Records -->
        <div class="recent-records">
            <h3><i class="fas fa-chart-bar"></i> Recent Analysis Results</h3>
            <div id="recentRecords"></div>
        </div>
    </div>

    <script>
        let currentMode = 'stream';
        let selectedStyle = 'formal';
        let isProcessing = false;
        
        function setMode(mode) {
            currentMode = mode;
            
            // Update buttons
            document.querySelectorAll('.mode-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update panels
            document.querySelectorAll('.content-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            if (mode === 'stream') {
                document.getElementById('streamPanel').classList.add('active');
                // Restart stream
                const img = document.getElementById('streamImg');
                img.src = '';
                setTimeout(() => {
                    img.src = 'http://{{ esp32_ip }}/stream?' + new Date().getTime();
                }, 500);
            } else if (mode === 'monitor') {
                document.getElementById('monitorPanel').classList.add('active');
                // Stop stream
                document.getElementById('streamImg').src = '';
            }
        }
        
        function toggleCustomInput() {
            const monitoringType = document.getElementById('monitoringType').value;
            const customGroup = document.getElementById('customInputGroup');
            
            if (monitoringType === 'custom') {
                customGroup.classList.add('show');
            } else {
                customGroup.classList.remove('show');
            }
        }
        
        // Prompt style selection
        document.querySelectorAll('.prompt-style').forEach(style => {
            style.addEventListener('click', function() {
                document.querySelectorAll('.prompt-style').forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
                selectedStyle = this.dataset.style;
            });
        });
        
        function setButtonState(processing) {
            isProcessing = processing;
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            
            startBtn.disabled = processing;
            stopBtn.disabled = processing;
            
            if (processing) {
                startBtn.innerHTML = '<div class="loading"></div> Processing...';
            } else {
                startBtn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
            }
        }
        
        function startMonitoring() {
            if (isProcessing) return;
            
            if (currentMode !== 'monitor') {
                showAlert('Please switch to AI Monitoring mode first', 'error');
                return;
            }
            
            const monitoringType = document.getElementById('monitoringType').value;
            let context = document.getElementById('customContext').value;
            
            // For custom monitoring, use custom instructions as context
            if (monitoringType === 'custom') {
                const customInstructions = document.getElementById('customInstructions').value.trim();
                if (!customInstructions) {
                    showAlert('Please enter custom monitoring instructions', 'error');
                    return;
                }
                context = customInstructions;
            }
            
            setButtonState(true);
            
            const data = {
                interval: parseInt(document.getElementById('intervalSelect').value),
                type: monitoringType,
                style: selectedStyle,
                context: context
            };
            
            fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(d => {
                setButtonState(false);
                if (d.status === 'started') {
                    updateStatus(true);
                    showAlert('Monitoring started successfully!', 'success');
                } else {
                    showAlert('Error: ' + (d.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                setButtonState(false);
                showAlert('Network error: ' + error.message, 'error');
            });
        }
        
        function stopMonitoring() {
            if (isProcessing) return;
            
            setButtonState(true);
            
            fetch('/api/stop', {method: 'POST'})
            .then(r => r.json())
            .then(d => {
                setButtonState(false);
                updateStatus(false);
                showAlert('Monitoring stopped', 'success');
                setTimeout(loadRecentRecords, 1000);
            })
            .catch(error => {
                setButtonState(false);
                showAlert('Network error: ' + error.message, 'error');
            });
        }
        
        function testCamera() {
            const resultDiv = document.getElementById('testResult');
            resultDiv.className = 'alert alert-success';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<i class="loading"></i> Testing camera...';
            
            fetch('/api/test-capture')
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    resultDiv.innerHTML = `<i class="fas fa-check"></i> Camera test successful! Image size: ${data.size} bytes`;
                } else {
                    resultDiv.className = 'alert alert-error';
                    resultDiv.innerHTML = `<i class="fas fa-times"></i> Test failed: ${data.error}`;
                }
            })
            .catch(error => {
                resultDiv.className = 'alert alert-error';
                resultDiv.innerHTML = `<i class="fas fa-times"></i> Test failed: ${error.message}`;
            });
        }
        
        function testTelegram() {
            const resultDiv = document.getElementById('testResult');
            resultDiv.className = 'alert alert-success';
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<i class="loading"></i> Testing Telegram bot...';
            
            fetch('/api/test-telegram')
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    resultDiv.innerHTML = `<i class="fas fa-check"></i> Telegram test successful! ${data.message}`;
                } else {
                    resultDiv.className = 'alert alert-error';
                    resultDiv.innerHTML = `<i class="fas fa-times"></i> Telegram test failed: ${data.error}`;
                }
            })
            .catch(error => {
                resultDiv.className = 'alert alert-error';
                resultDiv.innerHTML = `<i class="fas fa-times"></i> Telegram test failed: ${error.message}`;
            });
        }
        
        function updateStatus(active) {
            const statusCard = document.getElementById('statusCard');
            const statusText = document.getElementById('statusText');
            
            if (active) {
                statusCard.className = 'status-card active';
                statusText.innerHTML = '<i class="fas fa-play-circle"></i> Monitoring: ACTIVE';
            } else {
                statusCard.className = 'status-card';
                statusText.innerHTML = '<i class="fas fa-pause-circle"></i> System Ready';
            }
        }
        
        function updateTelegramStatus(enabled) {
            const telegramStatus = document.getElementById('telegramStatus');
            if (enabled) {
                telegramStatus.className = 'telegram-status telegram-enabled';
                telegramStatus.innerHTML = '<i class="fab fa-telegram"></i> Telegram: Online';
            } else {
                telegramStatus.className = 'telegram-status telegram-disabled';
                telegramStatus.innerHTML = '<i class="fab fa-telegram"></i> Telegram: Offline';
            }
        }
        
        function loadRecentRecords() {
            fetch('/api/records')
            .then(r => r.json())
            .then(records => {
                const container = document.getElementById('recentRecords');
                
                if (records.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #666;">No records yet. Start monitoring to see results.</p>';
                    return;
                }
                
                container.innerHTML = '';
                records.slice(0, 5).forEach(record => {
                    const statusClass = record.status.toLowerCase();
                    const threatIcon = record.threat_level > 7 ? '🚨' : record.threat_level > 4 ? '⚠️' : '✅';
                    const videoIndicator = record.has_video ? '<span class="video-badge"><i class="fas fa-video"></i> VIDEO</span>' : '';
                    
                    const recordEl = document.createElement('div');
                    recordEl.className = 'record-item';
                    recordEl.innerHTML = `
                        <div class="record-header">
                            <strong>${record.timestamp}</strong>
                            <span class="status-badge status-${statusClass}">
                                ${threatIcon} ${record.status} (${Math.round(record.confidence)}%)
                                ${videoIndicator}
                            </span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>Type:</strong> ${record.monitoring_type} | 
                            <strong>Style:</strong> ${record.prompt_style}
                            ${record.threat_level > 0 ? ` | <strong>Threat Level:</strong> ${record.threat_level}/10` : ''}
                        </div>
                        ${record.summary ? `<div style="background: rgba(102,126,234,0.1); padding: 10px; border-radius: 5px;"><strong>Summary:</strong> ${record.summary}</div>` : ''}
                    `;
                    container.appendChild(recordEl);
                });
            })
            .catch(error => console.error('Failed to load records:', error));
        }
        
        function checkStatus() {
            fetch('/api/status')
            .then(r => r.json())
            .then(d => {
                updateStatus(d.active);
                if (d.telegram_status !== undefined) {
                    updateTelegramStatus(d.telegram_status);
                }
            })
            .catch(error => console.error('Status check failed:', error));
        }
        
        function showAlert(message, type) {
            // Remove existing alerts
            document.querySelectorAll('.alert').forEach(alert => {
                if (alert.id !== 'testResult') {
                    alert.remove();
                }
            });
            
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';
            alert.innerHTML = message;
            
            document.querySelector('.container').appendChild(alert);
            
            setTimeout(() => {
                alert.style.display = 'none';
                alert.remove();
            }, 5000);
        }
        
        // Initialize
        setInterval(checkStatus, 3000);
        setInterval(loadRecentRecords, 10000);
        checkStatus();
        loadRecentRecords();
    </script>
</body>
</html>
'''

HISTORY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoring History</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .controls {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn i { margin-right: 8px; }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .record-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .record-card:hover {
            transform: translateY(-3px);
        }
        .record-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        .record-id {
            font-size: 1.2rem;
            font-weight: 700;
            color: #333;
        }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .status-normal { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-danger { background: #f8d7da; color: #721c24; }
        .video-badge {
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-left: 10px;
        }
        .record-body {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 25px;
        }
        @media (max-width: 768px) {
            .record-body {
                grid-template-columns: 1fr;
                gap: 20px;
            }
        }
        .media-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .video-container {
            position: relative;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
        }
        .video-container video {
            width: 100%;
            height: auto;
            display: block;
        }
        .images-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .image-container {
            position: relative;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        .image-label, .video-label {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: center;
        }
        .analysis-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .info-block {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }
        .info-block h4 {
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .info-block h4 i {
            margin-right: 8px;
            color: #667eea;
        }
        .info-block p {
            margin: 5px 0;
            line-height: 1.5;
        }
        .prompt-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
        }
        .response-box {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .no-records {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 50px;
            text-align: center;
            color: #666;
        }
        .filter-controls {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .form-control {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        .threat-indicator {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-history"></i> Monitoring History</h1>
            <p>Complete analysis records with images, videos and AI responses</p>
        </div>
        
        <div class="controls">
            <div class="filter-controls">
                <select id="statusFilter" class="form-control" onchange="filterRecords()">
                    <option value="">All Status</option>
                    <option value="NORMAL">Normal</option>
                    <option value="WARNING">Warning</option>
                    <option value="DANGER">Danger</option>
                </select>
                <select id="typeFilter" class="form-control" onchange="filterRecords()">
                    <option value="">All Types</option>
                    <option value="security">Security</option>
                    <option value="presence">Presence</option>
                    <option value="lighting">Lighting</option>
                    <option value="classroom">Classroom</option>
                    <option value="workplace">Workplace</option>
                    <option value="custom">Custom</option>
                </select>
                <select id="videoFilter" class="form-control" onchange="filterRecords()">
                    <option value="">All Records</option>
                    <option value="with_video">With Video</option>
                    <option value="without_video">Without Video</option>
                </select>
            </div>
            <div>
                <a href="/" class="btn btn-primary">
                    <i class="fas fa-home"></i> Back to Home
                </a>
                <button class="btn btn-primary" onclick="refreshHistory()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
        
        <div id="recordsContainer"></div>
    </div>

    <script>
        let allRecords = [];
        
        function loadHistory() {
            fetch('/api/records?limit=100')
            .then(r => r.json())
            .then(records => {
                allRecords = records;
                displayRecords(records);
            })
            .catch(error => {
                console.error('Failed to load history:', error);
                document.getElementById('recordsContainer').innerHTML = 
                    '<div class="no-records"><i class="fas fa-exclamation-triangle"></i> Failed to load records</div>';
            });
        }
        
        function displayRecords(records) {
            const container = document.getElementById('recordsContainer');
            
            if (records.length === 0) {
                container.innerHTML = `
                    <div class="no-records">
                        <i class="fas fa-history" style="font-size: 3rem; color: #ddd; margin-bottom: 20px;"></i>
                        <h3>No Records Found</h3>
                        <p>Start monitoring to see analysis results here</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = records.map(record => {
                const threatIcon = record.threat_level > 7 ? '🚨' : record.threat_level > 4 ? '⚠️' : '✅';
                const statusClass = record.status.toLowerCase();
                const videoIndicator = record.has_video ? '<span class="video-badge"><i class="fas fa-video"></i> VIDEO</span>' : '';
                
                // Generate media section
                let mediaSection = '';
                if (record.has_video && record.video_path) {
                    mediaSection = `
                        <div class="media-section">
                            <div class="video-container">
                                <video controls preload="metadata">
                                    <source src="/${record.video_path}" type="video/mp4">
                                    Your browser does not support video playback.
                                </video>
                                <div class="video-label"><i class="fas fa-video"></i> Recording</div>
                            </div>
                            <div class="images-section">
                                <div class="image-container">
                                    <img src="/${record.baseline_path}" alt="Baseline Image" loading="lazy">
                                    <div class="image-label">Baseline</div>
                                </div>
                                <div class="image-container">
                                    <img src="/${record.current_path}" alt="Analysis Image" loading="lazy">
                                    <div class="image-label">Analysis</div>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    mediaSection = `
                        <div class="images-section">
                            <div class="image-container">
                                <img src="/${record.baseline_path}" alt="Baseline Image" loading="lazy">
                                <div class="image-label">Baseline Image</div>
                            </div>
                            <div class="image-container">
                                <img src="/${record.current_path}" alt="Current Image" loading="lazy">
                                <div class="image-label">Analysis Image</div>
                            </div>
                        </div>
                    `;
                }
                
                return `
                    <div class="record-card">
                        <div class="record-header">
                            <div class="record-id">
                                Record #${record.id}
                                ${videoIndicator}
                            </div>
                            <div class="status-badge status-${statusClass}">
                                ${threatIcon} ${record.status} (${Math.round(record.confidence)}%)
                            </div>
                        </div>
                        
                        <div class="record-body">
                            ${mediaSection}
                            
                            <div class="analysis-section">
                                <div class="info-block">
                                    <h4><i class="fas fa-info-circle"></i> Analysis Details</h4>
                                    <p><strong>Timestamp:</strong> ${record.timestamp}</p>
                                    <p><strong>Type:</strong> ${record.monitoring_type === 'custom' ? 'Custom Monitoring' : record.monitoring_type}</p>
                                    <p><strong>Style:</strong> ${record.prompt_style}</p>
                                    <p><strong>Session:</strong> ${record.session_id}</p>
                                    <div class="threat-indicator">
                                        <strong>Threat Level:</strong> 
                                        <span style="color: ${record.threat_level > 7 ? '#dc3545' : record.threat_level > 4 ? '#ffc107' : '#28a745'}">
                                            ${record.threat_level}/10
                                        </span>
                                    </div>
                                    ${record.summary ? `<p><strong>Summary:</strong> ${record.summary}</p>` : ''}
                                    ${record.has_video ? `<p><strong>Video:</strong> <i class="fas fa-video"></i> Recording available</p>` : ''}
                                </div>
                                
                                ${record.custom_context ? `
                                    <div class="info-block">
                                        <h4><i class="fas fa-edit"></i> ${record.monitoring_type === 'custom' ? 'Custom Instructions' : 'Custom Context'}</h4>
                                        <p>${record.custom_context}</p>
                                    </div>
                                ` : ''}
                                
                                <div class="info-block">
                                    <h4><i class="fas fa-brain"></i> AI Prompt Used</h4>
                                    <div class="prompt-box">${record.prompt_used}</div>
                                </div>
                                
                                <div class="info-block">
                                    <h4><i class="fas fa-robot"></i> AI Analysis Response</h4>
                                    <div class="response-box">${record.ai_response}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function filterRecords() {
            const statusFilter = document.getElementById('statusFilter').value;
            const typeFilter = document.getElementById('typeFilter').value;
            const videoFilter = document.getElementById('videoFilter').value;
            
            let filtered = allRecords;
            
            if (statusFilter) {
                filtered = filtered.filter(r => r.status === statusFilter);
            }
            
            if (typeFilter) {
                filtered = filtered.filter(r => r.monitoring_type === typeFilter);
            }
            
            if (videoFilter) {
                if (videoFilter === 'with_video') {
                    filtered = filtered.filter(r => r.has_video);
                } else if (videoFilter === 'without_video') {
                    filtered = filtered.filter(r => !r.has_video);
                }
            }
            
            displayRecords(filtered);
        }
        
        function refreshHistory() {
            loadHistory();
        }
        
        // Initialize
        loadHistory();
    </script>
</body>
</html>
'''


@web_bp.route('/')
def index():
    """Main web interface"""
    return render_template_string(MAIN_TEMPLATE, esp32_ip=ESP32_CAM_CONFIG['ip_address'])


@web_bp.route('/history')
def history():
    """History page"""
    return render_template_string(HISTORY_TEMPLATE)


@web_bp.route(f'/{IMAGES_DIR}/<path:filename>')
def serve_media(filename):
    """Serve images and videos from configured directories"""
    return send_from_directory(IMAGES_DIR, filename)