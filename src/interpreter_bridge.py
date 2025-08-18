"""
Bridge module to connect Discord messages with Open Interpreter
Handles AI task interpretation and execution
"""

import logging
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class InterpreterBridge:
    """Bridge between Discord bot and Open Interpreter"""
    
    def __init__(self):
        self.interpreter = None
        self.initialize_interpreter()
        
    def initialize_interpreter(self):
        """Initialize Open Interpreter with safe settings"""
        try:
            import interpreter
            self.interpreter = interpreter
            
            # Configure interpreter for safe local execution
            self.interpreter.auto_run = False  # Require confirmation
            self.interpreter.safe_mode = 'ask'  # Ask before running code
            self.interpreter.offline = True  # Use local models if available
            
            logger.info("Open Interpreter initialized successfully")
        except ImportError:
            logger.error("Open Interpreter not installed. Please install with: pip install open-interpreter")
            self.interpreter = None
    
    async def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a message through the interpreter
        
        Args:
            message: The user's message/command
            user_id: Discord user ID for logging
            
        Returns:
            Dictionary with execution results
        """
        if not self.interpreter:
            return {
                'success': False,
                'error': 'Interpreter not initialized',
                'output': None
            }
        
        try:
            logger.info(f"Processing message from user {user_id}: {message}")
            
            # Run interpreter in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_interpreter,
                message
            )
            
            return {
                'success': True,
                'output': result,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': None
            }
    
    def _execute_interpreter(self, message: str) -> str:
        """Execute interpreter synchronously (called in thread)"""
        try:
            # Run the interpreter with the message
            response = self.interpreter.chat(message)
            
            # Format the response
            if isinstance(response, list):
                # Join multiple responses
                output = "\n".join(str(item) for item in response)
            else:
                output = str(response)
                
            return output
            
        except Exception as e:
            logger.error(f"Interpreter execution error: {e}")
            raise
    
    async def execute_task(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task type
        
        Args:
            task_type: Type of task (screenshot, open_app, etc.)
            params: Parameters for the task
            
        Returns:
            Execution results
        """
        task_handlers = {
            'screenshot': self._take_screenshot,
            'open_app': self._open_application,
            'create_file': self._create_file,
            'system_info': self._get_system_info
        }
        
        handler = task_handlers.get(task_type)
        if not handler:
            return {
                'success': False,
                'error': f'Unknown task type: {task_type}',
                'output': None
            }
        
        try:
            result = await handler(params)
            return {
                'success': True,
                'output': result,
                'error': None
            }
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': None
            }
    
    async def _take_screenshot(self, params: Dict[str, Any]) -> str:
        """Take a screenshot of the desktop"""
        import pyautogui
        from datetime import datetime
        
        filename = params.get('filename', f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        screenshot = pyautogui.screenshot()
        filepath = f'src/logs/{filename}'
        screenshot.save(filepath)
        
        return f"Screenshot saved to {filepath}"
    
    async def _open_application(self, params: Dict[str, Any]) -> str:
        """Open an application"""
        import subprocess
        import platform
        
        app_name = params.get('app_name', '')
        
        if platform.system() == 'Windows':
            subprocess.Popen(['start', app_name], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', '-a', app_name])
        else:  # Linux
            subprocess.Popen([app_name])
        
        return f"Opened application: {app_name}"
    
    async def _create_file(self, params: Dict[str, Any]) -> str:
        """Create a file with content"""
        filename = params.get('filename', 'untitled.txt')
        content = params.get('content', '')
        
        with open(filename, 'w') as f:
            f.write(content)
        
        return f"Created file: {filename}"
    
    async def _get_system_info(self, params: Dict[str, Any]) -> str:
        """Get system information"""
        import psutil
        import platform
        
        info = {
            'platform': platform.system(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory': f"{psutil.virtual_memory().percent}% used",
            'disk': f"{psutil.disk_usage('/').percent}% used"
        }
        
        return str(info)