"""
AI Prompt Generation Engine
Advanced prompt generation with specialized monitoring scenarios
"""


class PromptEngine:
    """Advanced prompt generation with specialized monitoring scenarios"""
    
    MONITORING_PROMPTS = {
        "security": {
            "focus": "security threats, unauthorized access, intrusion detection, suspicious activities",
            "specific_prompt": """I'm your security guard monitoring this location. Compare these surveillance images from my patrol.

    I check for: unauthorized persons, moved/stolen items, open doors/windows, suspicious behavior, equipment changes, lighting tampering.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Security status in one sentence]
    ANALYSIS: [My security assessment]
    ACTION: [My security recommendations]"""
        },
        
        "presence": {
            "focus": "human presence, occupancy detection, movement patterns, people counting",
            "specific_prompt": """I'm your facility supervisor tracking occupancy. Analyzing these images for presence changes.

    I monitor: people entering/leaving, occupant numbers, body positions, belongings, seating changes, activity signs.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Occupancy status in one sentence]
    ANALYSIS: [My facility assessment]
    ACTION: [My management recommendations]"""
        },
        
        "lighting": {
            "focus": "lighting conditions, electrical status, energy monitoring, illumination changes",
            "specific_prompt": """I'm your electrical technician checking power systems. Examining these images for electrical changes.

    I inspect: lights ON/OFF, brightness changes, shadows, screens, emergency lighting, natural light, indicators, power issues.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Electrical status in one sentence]
    ANALYSIS: [My technical assessment]
    ACTION: [My electrical recommendations]"""
        },
        
        "classroom": {
            "focus": "educational environment, student activity, learning engagement, classroom management",
            "specific_prompt": """I'm your classroom teacher observing the learning environment. Reviewing these images for educational insights.

    I assess: student attendance/engagement, teacher presence, participation, equipment use, organization, attention, group work, disruptions.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Classroom status in one sentence]
    ANALYSIS: [My educational assessment]
    ACTION: [My teaching recommendations]"""
        },
        
        "workplace": {
            "focus": "workplace safety, productivity, compliance, professional environment monitoring",
            "specific_prompt": """I'm your safety officer evaluating workplace conditions. Analyzing these images for safety and efficiency.

    I check: employee activity, safety compliance, equipment status, emergency access, organization, hazards, occupancy, productivity.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Workplace status in one sentence]
    ANALYSIS: [My safety assessment]
    ACTION: [My compliance recommendations]"""
        },
        
        "custom": {
            "focus": "user-defined monitoring requirements",
            "specific_prompt": """I'm your specialist monitoring professional. Analyzing these images for your specific requirements: {custom_context}

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Status in one sentence]
    ANALYSIS: [My specialist assessment]
    ACTION: [My expert recommendations]"""
        }
    }

    STYLE_MODIFIERS = {
        "formal": {
            "tone": "professional report style",
            "instruction": "Use formal professional language for official reports. Write in plain text without any bold, italic, or markdown formatting."
        },
        "technical": {
            "tone": "expert technical analysis with specifications",
            "instruction": "Provide technical details with measurements and expert terminology. Use plain text only, no formatting."
        },
        "casual": {
            "tone": "friendly everyday language",
            "instruction": "Explain like a helpful colleague in simple terms. Use plain text without any formatting."
        },
        "security": {
            "tone": "alert-focused protective language",
            "instruction": "Communicate like experienced security personnel focused on threats. Use plain text only."
        },
        "report": {
            "tone": "executive summary format",
            "instruction": "Present findings like a consultant briefing executives. Write in plain text without formatting."
        }
    }

    @classmethod
    def generate_optimized_prompt(cls, monitoring_type, style, custom_context=""):
        """Generate optimized cost-effective prompts for each monitoring scenario"""
        
        # Get base prompt
        if monitoring_type in cls.MONITORING_PROMPTS:
            base_prompt = cls.MONITORING_PROMPTS[monitoring_type]["specific_prompt"]
            
            # Handle custom monitoring with user context
            if monitoring_type == "custom" and custom_context.strip():
                base_prompt = base_prompt.format(custom_context=custom_context.strip()[:100])
            elif monitoring_type == "custom":
                base_prompt = """I'm your monitoring specialist. Compare these images and analyze significant changes.

    IMPORTANT: Respond in plain text only. Do not use any formatting like ** or _ or other markdown.

    STATUS: [NORMAL/WARNING/DANGER]
    CONFIDENCE: [0-100]
    THREAT_LEVEL: [0-10]
    SUMMARY: [Main change in one sentence]
    ANALYSIS: [Detailed change description]
    ACTION: [Recommended response]"""
        else:
            # Fallback
            base_prompt = cls.MONITORING_PROMPTS["custom"]["specific_prompt"].format(
                custom_context="general environmental monitoring"
            )
        
        # Apply style modifications (minimal)
        style_config = cls.STYLE_MODIFIERS.get(style, cls.STYLE_MODIFIERS["formal"])
        
        # Add concise style instruction
        enhanced_prompt = f"{base_prompt}\n\nStyle: {style_config['instruction']}"
        
        # Add custom context for non-custom types (limited to save tokens)
        if monitoring_type != "custom" and custom_context.strip():
            enhanced_prompt += f"\nFocus: {custom_context.strip()[:80]}"
        
        # Add final formatting reminder
        enhanced_prompt += "\n\nRemember: Use only plain text in your response. No bold, italic, asterisks, underscores, or any markdown formatting."
        
        return enhanced_prompt