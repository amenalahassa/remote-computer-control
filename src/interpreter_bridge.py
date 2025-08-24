"""
Bridge module to connect Discord messages with Open Interpreter
Handles AI task interpretation and execution with streaming support
"""

import logging
import asyncio
import os
import threading
from typing import Optional, Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from queue import Queue
import time

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
            interpreter.llm.api_key = "not-needed"  # LM Studio doesn't need API key
            
            # Configure interpreter settings
            interpreter.auto_run = True  # Auto-run commands for automation
            interpreter.verbose = True  # Show what's happening
            interpreter.safe_mode = 'off'  # Trust local execution
            interpreter.offline = True  # Use local models
            
            # Set context window and max tokens from env
            interpreter.llm.context_window = int(os.getenv('LLM_CONTEXT_WINDOW', 8192))
            interpreter.llm.max_tokens = int(os.getenv('LLM_MAX_TOKENS', 2000))
            
            # Set output directory
            output_dir = os.path.abspath("src/output")
            os.makedirs(output_dir, exist_ok=True)
            interpreter.system_message += f"""When saving files, use the output directory: {output_dir}
            You can read and write files from/to this directory.
            Current working directory: {os.getcwd()}
            """
            
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
                'metadata': {}
            }
            return
        
        try:
            logger.info(f"Processing message with streaming: {message[:100]}...")
            
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
            
            while thread.is_alive() or not self.output_queue.empty():
                try:
                    if not self.output_queue.empty():
                        chunk = self.output_queue.get(timeout=0.1)
                        
                        # Check for cancellation
                        if chunk.get('type') == 'cancelled':
                            yield chunk
                            break
                        
                        # Accumulate similar types for batching
                        if current_type == chunk['type'] and chunk['type'] == 'message':
                            accumulated_content.append(chunk['content'])
                            
                            # Yield accumulated content periodically
                            if time.time() - last_yield_time > 0.5:  # Every 500ms
                                yield {
                                    'type': current_type,
                                    'content': ''.join(accumulated_content),
                                    'metadata': chunk.get('metadata', {})
                                }
                                accumulated_content = []
                                last_yield_time = time.time()
                        else:
                            # Yield any accumulated content first
                            if accumulated_content:
                                yield {
                                    'type': current_type,
                                    'content': ''.join(accumulated_content),
                                    'metadata': {}
                                }
                                accumulated_content = []
                            
                            # Yield the new chunk
                            yield chunk
                            current_type = chunk['type']
                            last_yield_time = time.time()
                    
                    await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                    
                except:
                    await asyncio.sleep(0.01)
            
            # Yield any remaining accumulated content
            if accumulated_content:
                yield {
                    'type': current_type,
                    'content': ''.join(accumulated_content),
                    'metadata': {}
                }
            
            # Ensure thread is done
            thread.join(timeout=1.0)
            
        except Exception as e:
            logger.error(f"Error in stream processing: {e}")
            yield {
                'type': 'error',
                'content': str(e),
                'metadata': {}
            }
    
    def _run_interpreter_stream(self, message: str):
        """Run interpreter and stream output (runs in thread)"""
        try:
            # Custom display function to capture streaming output
            def display_output(output):
                if self.cancel_flag.is_set():
                    return False  # Stop execution
                
                # Parse output type
                if isinstance(output, dict):
                    output_type = output.get('type', 'message')
                    content = output.get('content', '')
                    
                    if output_type == 'code':
                        self.output_queue.put({
                            'type': 'code',
                            'content': content,
                            'metadata': {'language': output.get('language', 'python')}
                        })
                    elif output_type == 'console':
                        self.output_queue.put({
                            'type': 'console',
                            'content': content,
                            'metadata': {}
                        })
                    elif output_type == 'confirmation':
                        # Auto-confirm for now
                        self.output_queue.put({
                            'type': 'confirmation',
                            'content': content,
                            'metadata': {'auto_confirmed': True}
                        })
                        return True  # Confirm execution
                    else:
                        self.output_queue.put({
                            'type': 'message',
                            'content': str(content),
                            'metadata': {}
                        })
                else:
                    # Plain text output
                    self.output_queue.put({
                        'type': 'message',
                        'content': str(output),
                        'metadata': {}
                    })
                
                return not self.cancel_flag.is_set()
            
            # Set custom display
            original_display = getattr(self.interpreter, 'display', None)
            self.interpreter.display = display_output
            
            # Run interpreter
            for chunk in self.interpreter.chat(message, display=True, stream=True):
                if self.cancel_flag.is_set():
                    self.output_queue.put({
                        'type': 'cancelled',
                        'content': 'Task cancelled by user',
                        'metadata': {}
                    })
                    break
                
                # Process streaming chunk
                if chunk:
                    if isinstance(chunk, dict):
                        if 'content' in chunk:
                            self.output_queue.put({
                                'type': chunk.get('type', 'message'),
                                'content': chunk['content'],
                                'metadata': chunk.get('metadata', {})
                            })
                    else:
                        self.output_queue.put({
                            'type': 'message',
                            'content': str(chunk),
                            'metadata': {}
                        })
            
            # Restore original display
            if original_display:
                self.interpreter.display = original_display
                
        except Exception as e:
            logger.error(f"Interpreter execution error: {e}")
            self.output_queue.put({
                'type': 'error',
                'content': str(e),
                'metadata': {}
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