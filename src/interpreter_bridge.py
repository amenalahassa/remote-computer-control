"""
Bridge module to connect Discord messages with Open Interpreter
Handles AI task interpretation and execution with streaming support
"""

import logging
import asyncio
import os
import threading
from typing import Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from queue import Queue
import time
from src.runner.lpython import PythonLocal
from src.runner.lpowershell import PowerShellLocal

logger = logging.getLogger(__name__)

class InterpreterBridge:
    """Bridge between Discord bot and Open Interpreter with streaming support"""
    
    def __init__(self):
        load_dotenv()
        self.interpreter = None
        self.current_task = None
        self.cancel_flag = threading.Event()
        self.output_queue = Queue()
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
            interpreter.llm.api_key = os.getenv('LM_STUDIO_API_KEY', '')
            
            # Configure interpreter settings from environment
            interpreter.auto_run = os.getenv('INTERPRETER_AUTO_RUN', 'false').lower() == 'true'
            interpreter.verbose = os.getenv('INTERPRETER_VERBOSE', 'true').lower() == 'true'
            interpreter.safe_mode = os.getenv('INTERPRETER_SAFE_MODE', 'ask')  # 'off', 'ask', or 'auto'
            interpreter.offline = os.getenv('INTERPRETER_OFFLINE', 'true').lower() == 'true'
            
            # Set context window and max tokens from env
            interpreter.llm.context_window = int(os.getenv('LLM_CONTEXT_WINDOW', 8192))
            interpreter.llm.max_tokens = int(os.getenv('LLM_MAX_TOKENS', 2000))

            # Advanced capabilities
            interpreter.os = True
            interpreter.llm.supports_vision = True
            interpreter.llm.supports_functions = True
            
            # Set output directory
            output_dir = os.path.abspath("src/output")
            os.makedirs(output_dir, exist_ok=True)

            os.environ['INTERPRETER_OUTPUT_DIR'] = output_dir
            os.environ['INTERPRETER_VIRTUAL_ENV'] = os.getenv('INTERPRETER_VIRTUAL_ENV', '')
            
            # Enhanced system message with confirmation requirement
            interpreter.system_message += f"""You are a helpful AI assistant with access to the user's computer.
IMPORTANT RULES:
1. When saving files, use the output directory: {output_dir} also available os.environ['INTERPRETER_OUTPUT_DIR'].
2. You can read and write files from/to this directory.
3. Current working directory: {os.getcwd()}
4. Use the virtual environment's Python in {os.getenv("INTERPRETER_VIRTUAL_ENV")} available as os.environ['INTERPRETER_VIRTUAL_ENV'].
4. ALWAYS ask for user confirmation before running any code or system commands.
5. Explain what the code will do before asking for confirmation.
6. Format your confirmation requests clearly, like:
   "I'm about to run a command that will [description]. 
   This will [effects].
   Do you want me to proceed?"

Remember: User safety and consent are paramount. Never execute code without explicit permission."""

            interpreter.computer.emit_images = True
            interpreter.computer.import_computer_api = True
            interpreter.computer.terminate()
            interpreter.computer.languages = [PythonLocal, PowerShellLocal]
            
            self.interpreter = interpreter
            self.output_dir = output_dir
            
            logger.info(f"Open Interpreter initialized with {llm_provider} using model {llm_model}")
            logger.info(f"LM Studio URL: {lm_studio_url}")
            logger.info(f"Output directory: {output_dir}")
            
        except ImportError:
            logger.error("Open Interpreter not installed. Please install with: pip install open-interpreter")
            self.interpreter = None
        except Exception as e:
            logger.error(f"Failed to initialize interpreter: {e}")
            self.interpreter = None
    
    def load_context(self, messages: list):
        """Load conversation context into interpreter"""
        if self.interpreter and messages:
            try:
                # Set the conversation history
                self.interpreter.messages = messages
                logger.info(f"Loaded {len(messages)} messages into context")
            except Exception as e:
                logger.error(f"Failed to load context: {e}")
    
    async def process_message_stream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a message through the interpreter with streaming output
        
        Yields dictionaries with:
        - type: 'message', 'code', 'console', 'confirmation', 'error'
        - content: The actual content
        - metadata: Additional information
        """
        if not self.interpreter:
            yield {
                'type': 'error',
                'content': 'Interpreter not initialized. Check LM Studio is running.',
            }
            return
        
        try:

            # Clear cancel flag and queue
            self.cancel_flag.clear()
            while not self.output_queue.empty():
                self.output_queue.get()
            
            # Start interpreter in a thread
            thread = threading.Thread(
                target=self._run_interpreter_stream,
                args=(message,)
            )
            thread.start()
            
            # Stream output from queue
            last_yield_time = time.time()
            accumulated_content = []
            current_type = None
            current_metadata = None
            
            while thread.is_alive() or not self.output_queue.empty():
                try:
                    if not self.output_queue.empty():
                        chunk = self.output_queue.get(timeout=0.1)
                        
                        # Check for cancellation
                        if chunk.get('type') == 'cancelled':
                            yield chunk
                            break

                        if current_type is None:
                            current_type = chunk['type']
                            current_metadata = {
                                "format": chunk.get('format', 'text'),
                                "role": chunk.get('role', 'assistant'),
                            }

                        if current_type == 'confirmation' or isinstance(chunk["content"], dict):

                            # Yield accumulated content of previous type
                            if len(accumulated_content) > 0:
                                yield {
                                    'type': current_type,
                                    'content': ''.join(accumulated_content),
                                    "metadata": current_metadata
                                }
                                accumulated_content = []

                            # Yield confirmation immediately
                            yield chunk

                            current_type = None
                            current_metadata = None
                            last_yield_time = time.time()
                            continue

                        if chunk['type'] != current_type:
                            # Yield accumulated content of previous type
                            if len(accumulated_content) > 0:
                                yield {
                                    'type': current_type,
                                    'content': ''.join(accumulated_content),
                                }
                            accumulated_content = [chunk['content']]
                            current_type = chunk['type']
                            current_metadata = {
                                "format": chunk.get('format', 'text'),
                                "role": chunk.get('role', 'assistant'),
                            }
                            last_yield_time = time.time()

                        else:
                            accumulated_content.append(chunk['content'])
                            # Yield accumulated content periodically
                            if time.time() - last_yield_time > 0.5 or len(accumulated_content) > 10:
                                yield {
                                    'type': current_type,
                                    'content': ''.join(accumulated_content),
                                    "metadata": current_metadata
                                }
                                accumulated_content = []
                                last_yield_time = time.time()

                    await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning

                except Exception as e:
                    logger.error(f"Error retrieving from output queue {e}")
                    await asyncio.sleep(0.01)

            
            # Yield any remaining accumulated content
            if accumulated_content:
                yield {
                    'type': current_type,
                    'content': ''.join(accumulated_content),
                }
            # Ensure thread is done
            thread.join(timeout=1.0)
            
        except Exception as e:
            logger.error(f"Error in stream processing: {e}")
            yield {
                'type': 'error',
                'content': str(e),
            }
    
    def _run_interpreter_stream(self, message: str):
        """Run interpreter and stream output (runs in thread)"""
        try:
            for chunk in self.interpreter.chat(message, display=False, stream=True):
                if self.cancel_flag.is_set():
                    self.output_queue.put({
                        'type': 'cancelled',
                        'content': 'Task cancelled by user',
                    })
                    break
                
                # Process streaming chunk
                if chunk:
                    if 'content' in chunk:

                        # Only return output for running code
                        if chunk.get('type') == 'console' and chunk.get('format') == 'active_line':
                            continue

                        self.output_queue.put({
                            'role': chunk.get('role', 'assistant'),
                            'type': chunk.get('type', 'message'),
                            'content': chunk['content'],
                            'format': chunk.get('format', 'text'),
                        })

        except Exception as e:
            logger.error(f"Interpreter execution error: {e}")
            self.output_queue.put({
                'type': 'error',
                'content': str(e),
            })
    
    def cancel_current_task(self):
        """Cancel the currently running task"""
        self.cancel_flag.set()
        logger.info("Cancellation requested")
        return True
    
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
    
    def get_output_directory(self) -> str:
        """Get the output directory path"""
        return self.output_dir