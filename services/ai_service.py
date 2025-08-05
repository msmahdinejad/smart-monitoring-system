"""
AI Analysis Service  
Handles AI image analysis using AvalAI API or test responses
"""

import re
import logging
import requests

try:
    from config import AI_CONFIG, AVALAI_CONFIG, get_test_response
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """AI analysis engine for image comparison and threat detection"""
    
    def __init__(self):
        self.test_mode = AI_CONFIG.get('test_mode', False)
        self.ai_enabled = AI_CONFIG.get('ai_enabled', True)
    
    def analyze_images(self, baseline_b64, current_b64, prompt_text):
        """Analyze images using AvalAI API or return test response"""
        
        # Check if we should use test mode
        if self.test_mode or not self.ai_enabled:
            logger.info("Using test mode - returning simulated AI response")
            return self._get_test_response_text()
        
        # Real AI analysis
        try:
            headers = {
                "Authorization": f"Bearer {AVALAI_CONFIG['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": AVALAI_CONFIG['model'],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{baseline_b64}"}
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{current_b64}"}
                            }
                        ]
                    }
                ],
                "max_tokens": AVALAI_CONFIG['max_tokens'],
                "temperature": AVALAI_CONFIG['temperature']
            }
            
            response = requests.post(
                f"{AVALAI_CONFIG['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=AVALAI_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Analysis Error: {str(e)}"
    
    def parse_response(self, ai_response):
        """Enhanced parsing for both real and test responses"""
        
        # Check if this is a test mode response
        if "TEST MODE RESPONSE" in ai_response:
            return self._parse_test_response(ai_response)
        
        # Existing parsing logic for real AI responses
        result = {
            'status': 'NORMAL',
            'confidence': 0.0,
            'threat_level': 0,
            'summary': '',
            'analysis': ai_response,
            'action': ''
        }
        
        # Enhanced parsing with regex patterns
        try:
            # Parse STATUS
            status_match = re.search(r'STATUS:\s*([A-Z]+)', ai_response, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).upper()
                if status in ['NORMAL', 'WARNING', 'DANGER']:
                    result['status'] = status
            
            # Parse CONFIDENCE
            confidence_match = re.search(r'CONFIDENCE:\s*([0-9]+(?:\.[0-9]+)?)', ai_response, re.IGNORECASE)
            if confidence_match:
                try:
                    result['confidence'] = float(confidence_match.group(1))
                except:
                    pass
            
            # Parse THREAT_LEVEL
            threat_match = re.search(r'THREAT[_\s]*LEVEL:\s*([0-9]+)', ai_response, re.IGNORECASE)
            if threat_match:
                try:
                    result['threat_level'] = int(threat_match.group(1))
                except:
                    pass
            
            # Parse SUMMARY
            summary_match = re.search(r'SUMMARY:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE | re.MULTILINE)
            if summary_match:
                result['summary'] = summary_match.group(1).strip()
            
            # Parse ACTION
            action_match = re.search(r'ACTION:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE | re.MULTILINE)
            if action_match:
                result['action'] = action_match.group(1).strip()
            
            # Parse ANALYSIS
            analysis_match = re.search(r'ANALYSIS:\s*(.+?)(?:\nACTION:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            if analysis_match:
                result['analysis'] = analysis_match.group(1).strip()
        
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        # Ensure minimum values
        if result['confidence'] == 0.0:
            result['confidence'] = 50.0
        
        logger.info(f"Parsed result: STATUS={result['status']}, CONFIDENCE={result['confidence']}, THREAT={result['threat_level']}")
        return result
    
    def _get_test_response_text(self):
        """Generate test response text based on config"""
        test_response = get_test_response()
        
        if not test_response:
            return "Test mode error: No test response available"
        
        # Format test response as text that mimics real AI response
        response_text = f"""TEST MODE RESPONSE - NO REAL AI ANALYSIS

STATUS: {test_response['status']}
CONFIDENCE: {test_response['confidence']}
THREAT_LEVEL: {test_response['threat_level']}
SUMMARY: {test_response['summary']}
ANALYSIS: {test_response['analysis']}
ACTION: {test_response['action']}

NOTE: This is a simulated response for testing purposes. 
Real AI analysis is disabled in configuration."""
        
        return response_text
    
    def _parse_test_response(self, ai_response):
        """Parse test mode response"""
        test_response = get_test_response()
        
        if test_response:
            logger.info(f"Test mode: Using simulated response - {test_response['status']}")
            return test_response
        
        # Fallback
        return {
            'status': 'NORMAL',
            'confidence': 75.0,
            'threat_level': 0,
            'summary': 'Test mode fallback response',
            'analysis': 'Test mode is active - no real AI analysis performed',
            'action': 'Continue testing'
        }
    
    def toggle_test_mode(self, enable_test_mode=True):
        """Toggle between test mode and real AI"""
        self.test_mode = enable_test_mode
        self.ai_enabled = not enable_test_mode
        AI_CONFIG['test_mode'] = enable_test_mode
        AI_CONFIG['ai_enabled'] = not enable_test_mode