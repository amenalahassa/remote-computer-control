"""
Constants and enums for the Local AI Productivity Assistant
"""

from enum import Enum

class MessageType(Enum):
    """Types of messages handled by the bot"""
    TEXT = "text"
    CODE = "code"
    CONSOLE = "console"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    CANCELLED = "cancelled"
    MESSAGE = "message"
    MIXED = "mixed"

class SpecialTags(Enum):
    """Special tags used for file generation and other markers"""
    GEN_FILE_START = "GEN_FILE["
    GEN_FILE_END = "]GEN_FILE"
    CONFIRMATION_NEEDED = "CONFIRMATION_NEEDED"
    STREAM_CANCELLED = "STREAM_CANCELLED"

class BotCommands:
    """Discord bot commands"""
    PING = "!ping"
    STATUS = "!status"
    RESET = "!reset"
    HELP_AI = "!help_ai"
    STOP = "!stop"
    SHUTDOWN = "!shutdown"

class ServiceStatus(Enum):
    """Service status states"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"

# File paths and directories
DEFAULT_OUTPUT_DIR = "src/output"
DEFAULT_LOG_DIR = "src/logs"
SERVICE_LOG_FILE = "service.log"
BOT_LOG_FILE = "bot.log"

# Service configuration
SERVICE_NAME = "LocalAIAssistant"
SERVICE_DISPLAY_NAME = "Local AI Productivity Assistant"
SERVICE_DESCRIPTION = "Discord-based local AI productivity assistant"