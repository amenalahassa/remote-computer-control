"""
Gmail automation tasks
Handles opening Gmail and basic email operations
"""

import webbrowser
import logging

logger = logging.getLogger(__name__)

class GmailTask:
    """Handle Gmail-related automation tasks"""
    
    @staticmethod
    def open_gmail():
        """Open Gmail in the default web browser"""
        try:
            webbrowser.open('https://mail.google.com')
            logger.info("Opened Gmail in browser")
            return True, "Gmail opened successfully"
        except Exception as e:
            logger.error(f"Failed to open Gmail: {e}")
            return False, f"Error opening Gmail: {str(e)}"
    
    @staticmethod
    def compose_email(to=None, subject=None, body=None):
        """Open Gmail compose window with pre-filled fields"""
        try:
            # Build Gmail compose URL
            url = "https://mail.google.com/mail/?view=cm&fs=1"
            
            if to:
                url += f"&to={to}"
            if subject:
                url += f"&su={subject}"
            if body:
                url += f"&body={body}"
            
            webbrowser.open(url)
            logger.info(f"Opened Gmail compose window")
            return True, "Gmail compose window opened"
        except Exception as e:
            logger.error(f"Failed to open compose window: {e}")
            return False, f"Error: {str(e)}"