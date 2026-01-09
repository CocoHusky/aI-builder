# AI Chat

A simple ChatGPT-like interface for chatting with AI models via the AI Builder API.

## Features

- **ChatGPT-like interface** - Dark theme with sidebar and chat area
- **Conversation management** - Save, load, and delete conversations
- **Model selection** - Choose from available AI models
- **Individual conversations** - Each chat is completely separate

## Quick Start

1. Set your AI Builder token:
   ```bash
   export AI_BUILDER_TOKEN=your_token_here
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   npm start
   ```

4. Open http://localhost:3001 in your browser

## Usage

- Click "New Chat" to start a conversation
- Select your preferred AI model from the dropdown
- Type messages and press Enter to send
- Conversations are automatically saved
- Click on saved conversations in the sidebar to reload them
- Hover over conversations and click × to delete them

## Project Structure

- `server.js` - Express server with API endpoints
- `public/index.html` - Chat interface
- `conversations/` - Auto-created directory for saved chats