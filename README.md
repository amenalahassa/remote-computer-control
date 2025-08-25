# Local AI Productivity Assistant (Discord Interface)

A desktop automation assistant that helps streamline your daily workflows through a Discord chat interface. This tool runs locally on your machine and uses AI to interpret and execute productivity tasks.

## <� Purpose

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

## =� Getting Started

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

### Running as a Background Service

For production use, you can run the assistant as a background service that starts automatically and can be managed remotely.

#### Windows Service (using NSSM)

1. **Install NSSM** (if not already installed):
   - Download from [nssm.cc](https://nssm.cc/download)
   - Extract and add `nssm.exe` to your PATH

2. **Install the service**:
```cmd
python service_control.py install
```

3. **Start the service**:
```cmd
python service_control.py start
```

4. **Check service status**:
```cmd
python service_control.py status
```

#### Linux Service (using systemd)

1. **Install the service** (requires sudo):
```bash
sudo python service_control.py install
```

2. **Start the service**:
```bash
sudo python service_control.py start
```

3. **Enable auto-start on boot**:
```bash
sudo systemctl enable localaiaassistant.service
```

#### Universal Service Management Commands

```bash
# Install service
python service_control.py install

# Start service
python service_control.py start

# Stop service
python service_control.py stop

# Restart service
python service_control.py restart

# Check status
python service_control.py status

# Uninstall service
python service_control.py uninstall
```

#### Remote Control via Discord

Once running as a service, you can control it remotely through Discord:

- **Stop the service**: Use `/stop` command or `!stop`
- **Check service status**: Use `/service_status` command
- **View bot status**: Use `/status` command

## =' Configuration

Create a `.env` file in the project root with:

```env
DISCORD_BOT_TOKEN=your_bot_token_here

# LM Studio Configuration (Local LLM)
LLM_PROVIDER=lm_studio
LLM_MODEL=your_model_name
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=  # Usually not required for local LM Studio

# Interpreter Settings
INTERPRETER_AUTO_RUN=false  # Safety first - require confirmation
INTERPRETER_VERBOSE=true
INTERPRETER_SAFE_MODE=off
INTERPRETER_OFFLINE=true
INTERPRETER_OUTPUT_DIR=src/output

# LLM Settings
LLM_CONTEXT_WINDOW=8192
LLM_MAX_TOKENS=2000
```

### Advanced Configuration

The assistant supports extensive configuration through environment variables. Key settings include:

- **Model Configuration**: Choose your local LLM provider and model
- **Safety Settings**: Control code execution behavior
- **Output Management**: Configure file generation and attachment
- **Service Settings**: Customize logging and performance

### Getting Discord Credentials

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token
4. Invite the bot to your server with appropriate permissions
5. Get your Discord user ID (Enable Developer Mode in Discord settings)

## =� Project Structure

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

## =� Usage Examples

Once running, you can interact with your bot through Discord:

### Slash Commands (Recommended)
- `/ask Take a screenshot of my desktop`
- `/ask Create a file called notes.txt with my meeting agenda`
- `/ask Show me system resource usage`
- `/status` - Check bot and interpreter status
- `/stop` - Stop the assistant service remotely
- `/service_status` - Check service health

### Natural Language (Just type in chat)
- "Take a screenshot of my desktop"
- "Open VS Code" 
- "Create a file called notes.txt with my meeting agenda"
- "Show me system resource usage"
- "Generate a Python script that sorts files GEN_FILE[/path/to/script.py]GEN_FILE"

### File Generation
When asking the AI to create files, it will automatically attach them to the response when you use the GEN_FILE format:
```
Create a Python script that does X and save it as GEN_FILE[src/output/my_script.py]GEN_FILE
```

## =� Development Roadmap

###  Milestone 1: Foundation Setup
- Python environment configuration
- Basic project structure
- Core module scaffolding

### =� Upcoming Milestones

- **Milestone 2**: Discord bot connection and authentication
- **Milestone 3**: Open Interpreter integration
- **Milestone 4**: Productivity task implementations
- **Milestone 5**: Voice and image input support
- **Milestone 6**: Enhanced security features
- **Milestone 7**: Testing and optimization

## � Disclaimer

This tool is designed for personal productivity automation on your local machine. It should only be used by the authorized owner of the computer. Always review and understand any code that will be executed on your system.

## =� License

This project is for personal use. Please ensure you comply with Discord's Terms of Service and any applicable local regulations when using automation tools.

## > Contributing

This is a personal productivity tool. Feel free to fork and adapt it for your own needs.

---

**Remember**: This assistant runs locally and only responds to your commands. It's your personal productivity companion, not a remote access tool.