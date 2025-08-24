"""
Bridge module to connect Discord messages with Open Interpreter
Handles AI task interpretation and execution
"""

import logging
import asyncio
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class InterpreterBridge:
    """Bridge between Discord bot and Open Interpreter"""
    
    def __init__(self):
        load_dotenv()
        self.interpreter = None
        self.initialize_interpreter()
        
    def initialize_interpreter(self):
        """Initialize Open Interpreter with LM Studio settings"""
        try:
            from interpreter import interpreter
            
            # Configure for LM Studio
            llm_provider = os.getenv('LLM_PROVIDER', 'lm_studio')
            llm_model = os.getenv('LLM_MODEL', 'google/gemma-3n-e4b')
            lm_studio_url = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
            
            # Set up interpreter for local LLM
            interpreter.llm.model = f"{llm_provider}/{llm_model}"
            interpreter.llm.api_base = lm_studio_url
            interpreter.llm.api_key = "not-needed"  # LM Studio doesn't need API key
            
            # Configure interpreter settings
            interpreter.auto_run = True  # Auto-run commands for automation
            interpreter.verbose = True  # Show what's happening
            interpreter.safe_mode = 'off'  # Trust local execution
            interpreter.offline = True  # Use local models

            interpreter.llm.context_window = int(os.getenv('LLM_CONTEXT_WINDOW', 5))
            interpreter.llm.max_tokens = int(os.getenv('LLM_MAX_TOKENS', 1000))
            
            self.interpreter = interpreter
            
            logger.info(f"Open Interpreter initialized with {llm_provider} using model {llm_model}")
            logger.info(f"LM Studio URL: {lm_studio_url}")
            
        except ImportError:
            logger.error("Open Interpreter not installed. Please install with: pip install open-interpreter")
            self.interpreter = None
        except Exception as e:
            logger.error(f"Failed to initialize interpreter: {e}")
            self.interpreter = None
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message through the interpreter
        
        Args:
            message: The user's message/command
            
        Returns:
            Dictionary with execution results
        """
        if not self.interpreter:
            return {
                'success': False,
                'error': 'Interpreter not initialized. Check LM Studio is running.',
                'output': None
            }
        
        try:
            logger.info(f"Processing message: {message}")
            
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
            # Send message to interpreter
            response = self.interpreter.chat(message)
            
            # Format the response
            if isinstance(response, list):
                # Join multiple responses
                output = "\n".join(str(item) for item in response)
            else:
                output = str(response)
                
            logger.info(f"Interpreter response: {output[:200]}...")  # Log first 200 chars
            return output
            
        except Exception as e:
            logger.error(f"Interpreter execution error: {e}")
            raise
    
    def reset_conversation(self):
        """Reset the interpreter conversation"""
        try:
            if self.interpreter:
                self.interpreter.messages = []
                logger.info("Interpreter conversation reset")
                return True
        except Exception as e:
            logger.error(f"Failed to reset conversation: {e}")
            return False