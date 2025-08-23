"""
Discord bot module for the Local AI Productivity Assistant
Handles Discord integration and message processing
"""

import discord
from discord.ext import commands
import os
import logging
import asyncio
from interpreter_bridge import InterpreterBridge

# Configure logging
os.makedirs('src/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductivityBot(commands.Bot):
    """Discord bot for local productivity assistance"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.interpreter_bridge = InterpreterBridge()
        
    async def on_ready(self):
        """Called when bot successfully connects to Discord"""
        logger.info(f'Bot connected as {self.user}')
        print(f'✅ Bot is ready! Logged in as {self.user}')
        print(f'Connected to {len(self.guilds)} server(s)')
        
    async def on_message(self, message):
        """Process incoming messages"""
        # Ignore bot's own messages
        if message.author.bot:
            return
        
        # Log the message
        logger.info(f'Message from {message.author}: {message.content}')
        
        # Check if message is a command first
        ctx = await self.get_context(message)
        if ctx.valid:
            await self.process_commands(message)
            return
        
        # If not a command, process with Open Interpreter
        if message.content.strip():
            await self.process_with_interpreter(message)
    
    async def process_with_interpreter(self, message):
        """Send message to Open Interpreter and return response"""
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Process message through interpreter
                result = await self.interpreter_bridge.process_message(message.content)
                
                if result['success']:
                    output = result['output']
                    
                    # Split long messages
                    if len(output) > 1900:
                        # Send as file for very long outputs
                        with open('src/logs/output.txt', 'w') as f:
                            f.write(output)
                        await message.reply(
                            "Response was too long, sending as file:",
                            file=discord.File('src/logs/output.txt')
                        )
                    else:
                        # Send as message
                        await message.reply(f"```\n{output}\n```")
                else:
                    error_msg = result['error']
                    await message.reply(f"❌ Error: {error_msg}")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.reply(f"❌ An error occurred: {str(e)}")

async def run_bot(token):
    """Run the Discord bot"""
    bot = ProductivityBot()
    
    @bot.command(name='ping')
    async def ping(ctx):
        """Test command to check if bot is responsive"""
        await ctx.send('🏓 Pong! Assistant is running.')
    
    @bot.command(name='status')
    async def status(ctx):
        """Check the status of the assistant"""
        interpreter_status = "✅ Connected" if bot.interpreter_bridge.interpreter else "❌ Not connected"
        
        embed = discord.Embed(
            title="Assistant Status",
            color=discord.Color.green() if bot.interpreter_bridge.interpreter else discord.Color.red()
        )
        embed.add_field(name="Bot", value="✅ Online", inline=True)
        embed.add_field(name="Open Interpreter", value=interpreter_status, inline=True)
        embed.add_field(name="LLM Provider", value=os.getenv('LLM_PROVIDER', 'lmstudio'), inline=True)
        embed.add_field(name="Model", value=os.getenv('LLM_MODEL', 'Not set'), inline=False)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='reset')
    async def reset(ctx):
        """Reset the interpreter conversation"""
        if bot.interpreter_bridge.reset_conversation():
            await ctx.send("🔄 Conversation reset successfully!")
        else:
            await ctx.send("❌ Failed to reset conversation")
    
    @bot.command(name='help_ai')
    async def help_ai(ctx):
        """Show help for using the AI assistant"""
        help_text = """
**Local AI Productivity Assistant - Help**

**Natural Language Commands:**
Just type normally! The assistant understands requests like:
• "Take a screenshot"
• "Open notepad"
• "Create a file called test.txt"
• "Show system information"
• "What files are in the current directory?"

**Bot Commands:**
• `!ping` - Check if bot is responsive
• `!status` - Show bot and interpreter status
• `!reset` - Reset the conversation context
• `!help_ai` - Show this help message

**Tips:**
• Be specific in your requests
• The assistant can execute code and system commands
• Long responses will be sent as files
        """
        await ctx.send(help_text)
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')
        raise

# Main entry point for running the bot
def main():
    """Main function to run the Discord bot"""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("No Discord bot token found. Please set DISCORD_BOT_TOKEN in .env file")
        return
    
    # Run the bot
    asyncio.run(run_bot(token))

if __name__ == "__main__":
    main()