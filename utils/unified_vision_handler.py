"""
Disease Advisory Handler
Provides disease detection guidance (vision APIs currently unavailable)
"""

from utils.text_disease_advisor import text_disease_advisor

class UnifiedVisionHandler:
    def __init__(self):
        # Using text-based advisory since all free vision APIs are decommissioned
        self.use_text_fallback = True
    
    def get_vision_response(self, prompt, image_data, system_instruction=None):
        """Returns disease advisory guide"""
        advisory = text_disease_advisor.get_advisory(prompt)
        return advisory, "Text-Based Disease Guide"

# Create singleton instance
unified_vision_handler = UnifiedVisionHandler()
