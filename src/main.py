#!/usr/bin/env python3
"""
Main entry point for the Local AI Productivity Assistant
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all requirements are met"""
    load_dotenv()
    
    # Check Discord token
    if not os.getenv('DISCORD_BOT_TOKEN'):
        logger.error("❌ DISCORD_BOT_TOKEN not found in .env file")
        print("\nPlease set up your .env file with:")
        print("DISCORD_BOT_TOKEN=your_bot_token_here")
        return False
    
    # Check LM Studio configuration
    lm_studio_url = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
    logger.info(f"LM Studio URL configured: {lm_studio_url}")
    
    # Show current configuration
    print("\n" + "="*50)
    print("Local AI Productivity Assistant")
    print("="*50)
    print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'lmstudio')}")
    print(f"Model: {os.getenv('LLM_MODEL', 'google/gemma-3n-e4b')}")
    print(f"LM Studio URL: {lm_studio_url}")
    print("="*50 + "\n")
    
    return True

def main():
    """Main function to start the AI assistant"""
    print("🚀 Starting Local AI Productivity Assistant...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Import and run the Discord bot
        from discord_bot import main as run_discord_bot
        
        print("📡 Connecting to Discord...")
        print("✨ Bot will respond to all messages in channels it can access")
        print("\nCommands:")
        print("  !ping - Check if bot is responsive")
        print("  !status - Show bot and interpreter status")
        print("  !reset - Reset conversation context")
        print("  !help_ai - Show help message")
        print("\nOr just type naturally for AI assistance!\n")
        
        # Run the bot
        run_discord_bot()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down assistant...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start assistant: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()