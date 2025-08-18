# Local AI Productivity Assistant (Discord Interface)

A desktop automation assistant that helps streamline your daily workflows through a Discord chat interface. This tool runs locally on your machine and uses AI to interpret and execute productivity tasks.

## <¯ Purpose

This is a **local productivity tool** designed to help you automate repetitive tasks on your own computer. It uses Discord as a convenient chat interface to receive your commands, but all execution happens locally on your machine.

**Important:** This is NOT a remote control system. It does not allow third parties to control your computer. Only you, as the authorized user, can issue commands through your Discord account.

## ( Features

- **Discord Integration**: Use Discord as a natural language interface to control your local machine
- **AI-Powered Interpretation**: Leverages Open Interpreter to understand and execute complex tasks
- **Local Automation**: 
  - Open applications (browsers, editors, etc.)
  - Create and edit files
  - Capture screenshots
  - System monitoring
- **Multimodal Input** (planned):
  - Voice commands via Whisper STT
  - Image understanding for visual tasks
- **Security First**:
  - Whitelist-based authentication (only responds to your Discord ID)
  - Complete activity logging
  - All processing happens locally

## =€ Getting Started

### Prerequisites

- Python 3.8 or higher
- Discord account and bot token
- Windows/macOS/Linux desktop environment

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/remote-computer-control.git
cd remote-computer-control
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Discord bot token and user ID
```

5. Run the assistant:
```bash
python src/main.py
```

## =' Configuration

Create a `.env` file in the project root with:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
AUTHORIZED_USER_ID=your_discord_user_id_here
OPENAI_API_KEY=your_api_key_here  # Optional, for Open Interpreter
```

### Getting Discord Credentials

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token
4. Invite the bot to your server with appropriate permissions
5. Get your Discord user ID (Enable Developer Mode in Discord settings)

## =Á Project Structure

```
/src
  main.py              # Main entry point
  discord_bot.py       # Discord bot integration
  interpreter_bridge.py # AI task interpretation
  /tasks              # Specific automation modules
    gmail.py          # Gmail automation
    screenshot.py     # Screenshot capture
  /logs              # Activity logs and outputs
requirements.txt      # Python dependencies
.env.example         # Environment variables template
```

## = Security

- **Authentication**: Only responds to whitelisted Discord user IDs
- **Logging**: All commands and actions are logged locally
- **Local Execution**: No external servers or remote access
- **Safe Mode**: Open Interpreter runs with safety confirmations

## =Ý Usage Examples

Once running, you can send messages to your bot in Discord:

- "Take a screenshot of my desktop"
- "Open VS Code"
- "Create a file called notes.txt with my meeting agenda"
- "Show me system resource usage"
- "Open Gmail in my browser"

## =à Development Roadmap

###  Milestone 1: Foundation Setup
- Python environment configuration
- Basic project structure
- Core module scaffolding

### =Ë Upcoming Milestones

- **Milestone 2**: Discord bot connection and authentication
- **Milestone 3**: Open Interpreter integration
- **Milestone 4**: Productivity task implementations
- **Milestone 5**: Voice and image input support
- **Milestone 6**: Enhanced security features
- **Milestone 7**: Testing and optimization

##   Disclaimer

This tool is designed for personal productivity automation on your local machine. It should only be used by the authorized owner of the computer. Always review and understand any code that will be executed on your system.

## =Ä License

This project is for personal use. Please ensure you comply with Discord's Terms of Service and any applicable local regulations when using automation tools.

## > Contributing

This is a personal productivity tool. Feel free to fork and adapt it for your own needs.

---

**Remember**: This assistant runs locally and only responds to your commands. It's your personal productivity companion, not a remote access tool.