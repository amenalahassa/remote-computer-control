# claude.md — Dev Plan for "Local AI Productivity Assistant (Discord Interface)"

This document is the development guide for building the "Local AI Productivity Assistant."  
Claude should follow each milestone in order, completing subtasks before moving forward.  
If a task requires human input (credentials, paths, or decisions), Claude must **ask the human and wait for feedback before continuing.**

---

## Project Summary

The "Local AI Productivity Assistant" is a desktop app that helps automate everyday workflows on your computer.  
It integrates with **Discord as a conversational interface** but runs **locally on your machine** with no external remote access.

**Core functionality:**
- Receive your messages via Discord (for convenience of interaction).
- Interpret tasks using an AI interpreter (Open Interpreter or similar).
- Automate **local productivity tasks** such as:
    - Opening applications (e.g., code editor, browser).
    - Creating or editing local files.
    - Capturing a screenshot of your workspace.
    - Summarizing content (emails, documents, etc.).
- Support multimodal input: voice commands (via Whisper STT) and images.
- Secure: only responds to your Discord account, logs all actions.

⚠️ **Important Clarification:**  
This project is **not** a remote control system.
- It does not allow third parties to control your computer.
- It only automates tasks locally, with you as the sole authorized user.
- Discord is just a user-friendly **chat interface** to issue commands to your own machine.

---

## Milestone 1: Foundation Setup

1. **Setup Python environment**
    - Create a new Python virtual environment (`venv`).
    - Install dependencies:
        - `discord.py` (Discord integration)
        - `open-interpreter` (AI execution)
        - `pyautogui` (automation: mouse, keyboard, screenshots)
        - `psutil` (system monitoring)
        - `selenium` (browser automation, optional)
        - `whisper` (speech-to-text, optional)

2. **Initialize Git repository**
    - Create a new repo with `.gitignore` for Python projects.
    - Set up basic project folder structure:
      ```
      /src
        main.py
        discord_bot.py
        interpreter_bridge.py
        tasks/
          gmail.py
          screenshot.py
        logs/
      requirements.txt
      ```

---

## Milestone 2: Messaging Layer Prototype (Discord)

1. **Discord bot setup**
    - ASK HUMAN: "Please provide Discord Bot Token from Discord Developer Portal."
    - Configure environment variable for token.
    - Write `discord_bot.py` to connect bot to Discord server/DM.

2. **Basic message listener**
    - Bot listens for messages in a specific channel/DM.
    - Responds with a static message (e.g., "Hello, I am your AI Assistant.").
    - ASK HUMAN: "Please provide your Discord user ID to whitelist commands."
    - Only process messages from this ID.

---

## Milestone 3: AI Integration

1. **Bridge Discord to Interpreter**
    - Implement `interpreter_bridge.py` to send user’s message into Open Interpreter.
    - Receive AI’s plan/code/command.
    - Execute locally in sandbox.

2. **Return results**
    - Send execution output back to Discord channel.
    - For long outputs, send as text file.

3. **Test loop**
    - Example: User says: "Create a folder named `test_ai`."
    - AI executes: `mkdir test_ai`.
    - Bot replies: "✅ Folder created: test_ai."

---

## Milestone 4: Local Productivity Tasks

**Objective:** Determine whether Open Interpreter can handle automation tasks directly.

1. **Check Open Interpreter capabilities**
    - Test with natural language prompts if it can:
        - Open a code editor.
        - Open Gmail in a browser.
        - Create and edit a file.
        - Capture and return a screenshot.
    - ASK HUMAN: "Please confirm your OS (Windows, macOS, Linux) to test relevant commands."

2. **Evaluate coverage**
    - If Open Interpreter **successfully handles these tasks out-of-the-box**, no custom code is needed.
    - If not, **report back clearly**:
        - Which tasks failed.
        - Why they failed.
        - What additional code modules or libraries would be needed.

---

## Milestone 5: Voice & Image Input

1. **Voice input (optional)**
    - Integrate Whisper for speech-to-text.
    - If user uploads a `.wav` or `.mp3` file in Discord, transcribe it → send to Interpreter.

2. **Voice output (optional)**
    - Integrate TTS (e.g., pyttsx3).
    - Save as audio file, send back to Discord.

3. **Image input**
    - If user uploads an image to Discord, forward to vision model (GPT-4V or open-source).
    - AI interprets image content, then takes further action.

---

## Milestone 6: Security & Safety

1. **Authentication**
    - Restrict bot to only respond to whitelisted Discord user ID(s).
    - Ignore other users.

2. **Logging**
    - Save all executed commands and outputs into `/logs/commands.log`.

---

## Milestone 7: Testing & Optimization

1. **End-to-end testing**
    - Test text commands (file ops, open apps, screenshots).
    - Test voice input → text → execution.
    - Test image input → interpretation.

2. **Error handling**
    - Catch failed executions and reply with error message instead of crashing.

3. **Background service**
    - Package app so it runs in background:
        - Windows: use Task Scheduler or `nssm` to run as service.
        - macOS/Linux: use `launchd` or `systemd`.

---

## Rules for Claude

- **Never skip asking for human input when required.**
- **Confirm critical OS/system-dependent steps before writing code.**
- **Implement code incrementally by milestone.**
- **After each milestone, pause and ASK HUMAN: "Shall I continue to next milestone?"**

---
