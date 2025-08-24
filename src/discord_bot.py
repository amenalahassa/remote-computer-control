"""
Discord bot module for the Local AI Productivity Assistant
Handles Discord integration with slash commands and streaming
"""

import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
import asyncio
from interpreter_bridge import InterpreterBridge
from database import ChatDatabase

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
    """Discord bot for local productivity assistance with slash commands"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        self.interpreter_bridge = InterpreterBridge()
        self.db = ChatDatabase()
        self.active_messages = {}  # Track active streaming messages
        
        # Load conversation history on startup
        self._load_history()
    
    def _load_history(self):
        """Load conversation history into interpreter"""
        try:
            context = self.db.get_conversation_context(limit=20)
            if context:
                self.interpreter_bridge.load_context(context)
                logger.info(f"Loaded {len(context)} messages from history")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
    
    async def setup_hook(self):
        """Setup hook for syncing slash commands"""
        try:
            # Sync commands globally (or to specific guild)
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot successfully connects to Discord"""
        logger.info(f'Bot connected as {self.user}')
        print(f'✅ Bot is ready! Logged in as {self.user}')
        print(f'Connected to {len(self.guilds)} server(s)')
        print(f'Slash commands are ready! Type / to see available commands')
        
    async def on_message(self, message):
        """Process incoming messages"""
        # Ignore bot's own messages
        if message.author.bot:
            return

        # Log the message to database
        self.db.add_message(
            user_id=str(message.author.id),
            username=message.author.name,
            role='user',
            content=message.content,
            message_type='text'
        )
        # Check if message is a command first
        ctx = await self.get_context(message)
        if ctx.valid:
            await self.process_commands(message)
            return
        
        # If not a command, process with Open Interpreter
        if message.content.strip():
            await self.process_with_interpreter_stream(message)



    async def process_message(self, response_msg, content):
        """Process message without streaming (legacy)"""
        self.active_messages[response_msg.id] = True  # Mark message as active
        try:
            # Stream content accumulation
            full_content = []
            last_chuck_type = None
            current_content = []
            display_content = ""

            # Process streaming response
            async for chunk in self.interpreter_bridge.process_message_stream(content):
                # Check if message was cancelled
                if response_msg.id not in self.active_messages:
                    break

                chunk_type = chunk.get('type', 'message')
                content = chunk.get('content', '')

                if last_chuck_type is None:
                    last_chuck_type = chunk_type

                if chunk_type == 'cancelled':
                    await response_msg.edit(content="❌ Task cancelled by user")
                    break
                elif chunk_type == 'error':
                    await response_msg.edit(content=f"❌ Error: {content}")
                    break
                else:

                    if chunk_type != last_chuck_type:
                        # Flush current content
                        if current_content:
                            formatted = self._format_display_content(
                                current_content, last_chuck_type
                            )
                            full_content.append(formatted)
                            current_content = [chunk['content']]
                        last_chuck_type = chunk_type
                    else:
                        current_content.append(chunk['content'])

                # Update message periodically with accumulated content
                try:
                    full_content.append(self._format_display_content(current_content, chunk_type))
                    display_content = "\n".join(full_content)
                    full_content.pop(-1)  # Remove last added content to avoid duplication

                    await response_msg.edit(content=display_content)
                except discord.errors.HTTPException:
                    print(f"Error updating message, content too long")
                    # Rate limited, wait a bit
                    await asyncio.sleep(1)

            # Save assistant response to database
            self.db.add_message(
                user_id='bot',
                username=self.user.name,
                role='assistant',
                content=display_content,
                message_type='mixed'
            )

            # Clean up active message
            if response_msg.id in self.active_messages:
                del self.active_messages[response_msg.id]

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await response_msg.edit(content=f"❌ An error occurred: {str(e)}")
    
    async def process_with_interpreter_stream(self, message):
        """Send message to Open Interpreter with streaming response"""
        # Create initial message
        response_msg = await message.reply("🤔 Processing...")
        await self.process_message(response_msg, message.content)

    def _format_display_content(self, messages, message_type):
        """Format content for Discord display"""

        if message_type == 'message':
            return ' '.join(messages)
        elif message_type == 'code':
            language = messages[0].get('format', 'python')
            return f"```{language}\n{' '.join(messages)}\n```"
        elif message_type == 'console':
            return f"```console\n{' '.join(messages)}\n```"
        elif message_type == 'confirmation': # Todo: handle confirmation better
            ask_content = " ".join([msg["content"] for msg in messages])
            ask_format = messages[0].get('format', 'text')
            ask_message = self._format_display_content(ask_content, ask_format)
            return f"**Confirmation needed:**\n{ask_message}"

        return "".join(messages)
    
    async def _send_as_file(self, message, content):
        """Send long content as a file"""
        try:
            output_path = os.path.join(self.interpreter_bridge.get_output_directory(), 'response.md')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            await message.edit(
                content="Response was too long, sending as file:",
                attachments=[discord.File(output_path, filename='response.md')]
            )
        except Exception as e:
            logger.error(f"Failed to send as file: {e}")

# Create bot instance
bot = ProductivityBot()

# Slash Commands
@bot.tree.command(name="ask", description="Ask the AI assistant anything")
@app_commands.describe(prompt="Your question or task for the AI")
async def ask(interaction: discord.Interaction, prompt: str):
    """Slash command to ask the AI with streaming"""
    await interaction.response.defer()
    
    # Log to database
    bot.db.add_message(
        user_id=str(interaction.user.id),
        username=interaction.user.name,
        role='user',
        content=prompt,
        message_type='text'
    )

    # Send initial message
    response_msg = await interaction.followup.send("🤔 Processing...", wait=True)
    await bot.process_message(response_msg, prompt)

@bot.tree.command(name="cancel", description="Cancel the current AI task")
async def cancel(interaction: discord.Interaction):
    """Cancel the currently running task"""
    if bot.interpreter_bridge.cancel_current_task():
        await interaction.response.send_message("🛑 Cancelling current task...")
        
        # Cancel any active streaming messages
        for msg_id in list(bot.active_messages.keys()):
            del bot.active_messages[msg_id]
    else:
        await interaction.response.send_message("ℹ️ No active task to cancel")

@bot.tree.command(name="status", description="Check the assistant status")
async def status(interaction: discord.Interaction):
    """Check bot and interpreter status"""
    interpreter_status = "✅ Connected" if bot.interpreter_bridge.interpreter else "❌ Not connected"
    
    embed = discord.Embed(
        title="Assistant Status",
        color=discord.Color.green() if bot.interpreter_bridge.interpreter else discord.Color.red()
    )
    embed.add_field(name="Bot", value="✅ Online", inline=True)
    embed.add_field(name="Open Interpreter", value=interpreter_status, inline=True)
    embed.add_field(name="LLM Provider", value=os.getenv('LLM_PROVIDER', 'lmstudio'), inline=True)
    embed.add_field(name="Model", value=os.getenv('LLM_MODEL', 'Not set'), inline=False)
    embed.add_field(name="Output Directory", value=bot.interpreter_bridge.get_output_directory(), inline=False)
    
    # Add history stats
    recent_messages = bot.db.get_recent_messages(limit=100)
    embed.add_field(name="Chat History", value=f"{len(recent_messages)} messages", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset", description="Reset the conversation context")
async def reset(interaction: discord.Interaction):
    """Reset conversation context"""
    if bot.interpreter_bridge.reset_conversation():
        await interaction.response.send_message("🔄 Conversation context reset successfully!")
    else:
        await interaction.response.send_message("❌ Failed to reset conversation")

@bot.tree.command(name="history", description="Export chat history")
async def history(interaction: discord.Interaction):
    """Export chat history to file"""
    await interaction.response.defer()
    
    try:
        export_path = bot.db.export_history()
        if export_path and os.path.exists(export_path):
            await interaction.followup.send(
                "📜 Chat history exported:",
                file=discord.File(export_path, filename="chat_history.json")
            )
        else:
            await interaction.followup.send("❌ Failed to export history")
    except Exception as e:
        logger.error(f"Error exporting history: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="flush", description="Clear all chat history from database")
async def flush(interaction: discord.Interaction):
    """Clear all chat history from the database"""
    try:
        # Clear messages from database
        cleared = bot.db.clear_old_messages(days=0)  # Clear all messages
        
        # Reset interpreter conversation
        bot.interpreter_bridge.reset_conversation()
        
        # Respond with confirmation
        embed = discord.Embed(
            title="🗑️ History Flushed",
            description=f"Successfully cleared {cleared} messages from the database.",
            color=discord.Color.green()
        )
        embed.add_field(name="Conversation", value="✅ Reset", inline=True)
        embed.add_field(name="Database", value="✅ Cleared", inline=True)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Flushed {cleared} messages from history by {interaction.user.name}")
        
    except Exception as e:
        logger.error(f"Error flushing history: {e}")
        await interaction.response.send_message(f"❌ Error flushing history: {str(e)}")

@bot.tree.command(name="help_ai", description="Show help for using the AI assistant")
async def help_ai(interaction: discord.Interaction):
    """Show help message"""
    help_text = """
**Local AI Productivity Assistant - Help**

**Slash Commands (works great on mobile!):**
• `/ask [prompt]` - Ask the AI anything
• `/cancel` - Cancel current task
• `/status` - Check bot and interpreter status
• `/reset` - Reset conversation context
• `/history` - Export chat history
• `/flush` - Clear all chat history from database
• `/help_ai` - Show this help

**Natural Language (just type!):**
• "Take a screenshot"
• "Create a file called test.txt"
• "Show system information"
• "What files are in the output directory?"

**Features:**
• 🔄 Streaming responses - see output as it's generated
• 💾 Persistent chat history across sessions
• 📁 Output directory for all generated files
• 🔒 Safe mode - requires confirmation before running code
• ❌ Cancel long-running tasks with `/cancel`

**Output Directory:** All files are saved to `src/output/`
**Safety:** Code execution requires confirmation (auto_run disabled)
    """
    
    embed = discord.Embed(
        title="AI Assistant Help",
        description=help_text,
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)

# Legacy commands (prefix-based)
@bot.command(name='ping')
async def ping(ctx):
    """Test command to check if bot is responsive"""
    await ctx.send('🏓 Pong! Assistant is running.')

async def run_bot(token):
    """Run the Discord bot"""
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')
        raise

# Main entry point
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