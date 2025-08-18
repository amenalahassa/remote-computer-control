"""
Screenshot capture and management
"""

import pyautogui
import os
from datetime import datetime
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ScreenshotTask:
    """Handle screenshot capture and processing"""
    
    def __init__(self, save_dir="src/logs/screenshots"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def capture_full_screen(self, filename=None):
        """Capture the entire screen"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.save_dir, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"Screenshot saved to {filepath}")
            return True, filepath
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return False, str(e)
    
    def capture_region(self, x, y, width, height, filename=None):
        """Capture a specific region of the screen"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"region_{timestamp}.png"
            
            filepath = os.path.join(self.save_dir, filename)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(filepath)
            
            logger.info(f"Region screenshot saved to {filepath}")
            return True, filepath
        except Exception as e:
            logger.error(f"Failed to capture region: {e}")
            return False, str(e)
    
    def capture_window(self, window_title, filename=None):
        """Capture a specific window by title"""
        try:
            # This is a placeholder - actual implementation would need
            # platform-specific window handling
            logger.warning("Window capture not fully implemented")
            return self.capture_full_screen(filename)
        except Exception as e:
            logger.error(f"Failed to capture window: {e}")
            return False, str(e)