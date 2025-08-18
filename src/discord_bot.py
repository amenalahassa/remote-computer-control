"""
Discord bot module for the Local AI Productivity Assistant
Handles Discord integration and message processing
"""

import discord
from discord.ext import commands
import os
import logging

# Configure logging
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
    
    def __init__(self, authorized_user_id=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.authorized_user_id = authorized_user_id
        
    async def on_ready(self):
        """Called when bot successfully connects to Discord"""
        logger.info(f'Bot connected as {self.user}')
        print(f'Bot is ready! Logged in as {self.user}')
        
    async def on_message(self, message):
        """Process incoming messages"""
        # Ignore bot's own messages
        if message.author.bot:
            return
            
        # Check if message is from authorized user
        if self.authorized_user_id and str(message.author.id) != str(self.authorized_user_id):
            logger.warning(f'Unauthorized message from {message.author} (ID: {message.author.id})')
            return
            
        # Log the message
        logger.info(f'Message from {message.author}: {message.content}')
        
        # Process commands
        await self.process_commands(message)
        
        # TODO: Bridge to interpreter for natural language processing
        
async def run_bot(token, authorized_user_id=None):
    """Run the Discord bot"""
    bot = ProductivityBot(authorized_user_id=authorized_user_id)
    
    @bot.command(name='ping')
    async def ping(ctx):
        """Test command to check if bot is responsive"""
        await ctx.send('Pong! Assistant is running.')
    
    @bot.command(name='status')
    async def status(ctx):
        """Check the status of the assistant"""
        await ctx.send('✅ Assistant is online and ready to help!')
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')
        raise