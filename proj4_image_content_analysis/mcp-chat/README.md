# Coco Chat 🐕

A paw-some ChatGPT-like interface for chatting with AI models via the AI Builder API. Woof woof! 🐶

## Features

- **🐕 Coco Chat interface** - Dog-themed design with sidebar and chat area
- **🐾 Paw-some conversations** - Save, load, and delete conversations
- **🦴 Model selection** - Choose from available AI models
- **🏡 Individual conversations** - Each chat is completely isolated like good dogs

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

4. Open http://localhost:3001 in your browser and start chatting with your furry AI friend! 🐶

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