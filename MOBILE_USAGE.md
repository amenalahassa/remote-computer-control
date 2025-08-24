# Mobile Discord Usage Guide

## 📱 Using the AI Assistant on Mobile

The bot is fully optimized for mobile Discord usage with slash commands that work seamlessly on iOS and Android.

## 🚀 Getting Started

### 1. First Time Setup
After the bot is added to your server and running:
1. Open Discord on your phone
2. Go to your server/channel where the bot is active
3. Type `/` to see all available commands
4. The commands will auto-complete as you type!

### 2. Available Slash Commands

#### `/ask [prompt]`
The main command for interacting with the AI.
- **Usage**: `/ask create a python script that lists files`
- **Mobile Tip**: Use voice-to-text for longer prompts!

#### `/cancel`
Stop any currently running task.
- **Usage**: `/cancel`
- **When to use**: If a task is taking too long or you want to stop it

#### `/status`
Check if the bot and AI are working properly.
- **Usage**: `/status`
- **Shows**: Connection status, model info, output directory

#### `/reset`
Clear the conversation context and start fresh.
- **Usage**: `/reset`
- **When to use**: Starting a new unrelated task

#### `/history`
Export your chat history as a file.
- **Usage**: `/history`
- **Result**: Downloads a JSON file with all conversations

#### `/help_ai`
Show the help menu with all commands.
- **Usage**: `/help_ai`

## 📝 Mobile Tips & Tricks

### Voice Input
1. Tap the `/ask` command
2. In the prompt field, use your phone's voice-to-text
3. Speak your command naturally
4. Submit when done

### Quick Actions
Create shortcuts for common tasks:
- "Take a screenshot" 
- "Show system info"
- "List files in output"
- "Create a note file"

### Viewing Long Responses
- Long responses are automatically sent as files
- Tap to download and view in your preferred app
- Code blocks are formatted for easy copying

### Streaming Responses
- Watch responses appear in real-time
- See code execution as it happens
- Use `/cancel` if something goes wrong

## 🎯 Common Mobile Workflows

### Quick File Creation
```
/ask create a file called shopping_list.txt with items: milk, eggs, bread
```

### Take Screenshot
```
/ask take a screenshot of the desktop
```

### System Check
```
/ask show CPU and memory usage
```

### Code Generation
```
/ask write a Python function to sort a list of numbers
```

## ⚡ Performance Tips

1. **Use Slash Commands**: Faster than typing regular messages
2. **Short Prompts**: Mobile keyboards can be slow, keep it concise
3. **Voice Input**: Faster for longer commands
4. **Cancel Early**: Don't wait if you see it's going wrong

## 🔧 Troubleshooting

### Commands Not Showing?
1. Make sure bot is online (`/status`)
2. Force-close and reopen Discord app
3. Check bot has proper permissions in the channel

### Responses Cut Off?
- Long responses are sent as files
- Check your Downloads folder
- Ask for "shorter summary" if needed

### Bot Not Responding?
1. Check with `/status`
2. Try `/reset` to clear context
3. Ensure LM Studio is running on the host machine

## 📱 Platform-Specific Notes

### iOS
- Swipe down to dismiss keyboard while viewing responses
- Use 3D touch/long press to preview file attachments
- Share files directly to other apps

### Android
- Use split-screen to reference responses while working
- Files download to your Downloads folder
- Long-press messages to copy text

## 🎨 Customization

You can ask the AI to format responses specifically for mobile:
- "Give me a brief summary"
- "Format this as a bullet list"
- "Make this mobile-friendly"

## 💡 Pro Tips

1. **Batch Commands**: Ask multiple things in one prompt
2. **Save Templates**: Keep common prompts in your notes
3. **Use History**: Export conversations for reference
4. **Context Aware**: The bot remembers recent conversations

---

## Quick Start Example

1. Open Discord on your phone
2. Type: `/ask`
3. Enter: "Create a file called test.txt with 'Hello World'"
4. Watch the AI create your file!
5. Check output directory for the file

That's it! The bot is designed to be intuitive and mobile-friendly. Just type `/` and explore!