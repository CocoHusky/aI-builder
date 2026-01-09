# Coco Chat 🤖

A beautiful ChatGPT-like interface that connects to multiple AI models via the AI Builder API. Run locally as a simple server!

## ✨ Features

- ✅ ChatGPT-like dark interface
- ✅ **Persistent conversation saving** - Save, load, and delete conversations like ChatGPT
- ✅ **Complete conversation isolation** - Each chat is completely separate with no bleeding
- ✅ **Beautiful sidebar model selector** - Switch between all available AI models
- ✅ **New Chat button** - Start fresh conversations anytime
- ✅ **Auto-save** - Conversations saved automatically after each message
- ✅ **Model display in chat** - See which model you're using in each conversation

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set your AI Builder token
export AI_BUILDER_TOKEN=your_token_here

# Run locally
npm start
```

Open **http://localhost:3001** in your browser!

## 📁 Project Structure
```
coco-chat/
├── server.js              # Express server with AI Builder API
├── public/
│   └── index.html         # ChatGPT-like interface
├── conversations/         # Auto-created directory for saved chats
├── package.json           # Dependencies & scripts
└── README.md             # This file
```

## Conversation Storage:
Conversations are automatically saved to `conversations/` directory as JSON files.
Each conversation includes:
- Full message history
- Title and timestamp
- Unique ID for loading
- Model used for the conversation

## 🎯 Model Selection

The interface includes a **model selector** in the **left sidebar** that allows you to choose which AI model to use for new conversations:

### 📋 **Available Models:**
- **Grok-4-Fast** - X.AI's fastest model (default)
- **Supermind Agent v1** - Multi-tool agent with web search
- **Gemini 2.5 Pro** - Google's advanced reasoning model
- **Gemini 3 Flash** - Fast Gemini model
- **GPT-5** - OpenAI's latest
- **DeepSeek** - Cost-effective alternative

**How to use:**
1. Select a model from the dropdown in the left sidebar before starting a new chat
2. Each conversation uses the model selected when it was created
3. The model is displayed at the top of each chat

The interface shows all available models with emoji icons for easy identification.

## 🔒 Security Notes
- Never commit your `AI_BUILDER_TOKEN` to GitHub
- Use environment variables for all secrets
- The app runs on port 3001 by default