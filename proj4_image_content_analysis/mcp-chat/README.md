# Coco Chat 🐕

A paw-some ChatGPT-like interface for chatting with AI models via the AI Builder API. Woof woof! 🐶

## 🚀 Deployment on AI Builder

This application is ready for deployment on AI Builder platforms.

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

## 🌐 AI Builder Deployment

### Prerequisites
- AI Builder account with API access
- Valid `AI_BUILDER_TOKEN`

### Deployment Steps

1. **Prepare the Application**
   - Ensure all files are committed to your repository
   - Verify `package.json` includes all dependencies
   - Test locally: `npm install && npm start`

2. **AI Builder Deployment**
   - Access your AI Builder deployment dashboard
   - Create a new web application deployment
   - Select "Node.js" as the runtime environment
   - Set the entry point to `server.js`

3. **Environment Configuration**
   - Set environment variable: `AI_BUILDER_TOKEN=your_token_here`
   - Optionally set: `NODE_ENV=production`
   - The application will automatically use AI Builder's assigned PORT

4. **Upload & Deploy**
   - Upload the entire project directory
   - AI Builder will automatically install dependencies and start the application
   - The application will be available at your AI Builder deployment URL

### Production Features
- ✅ Automatic port detection (`process.env.PORT`)
- ✅ Production-ready error handling
- ✅ Shared conversation storage for all users
- ✅ Static file serving optimized
- ✅ Environment variable support

### Troubleshooting
- Check AI Builder logs for any startup errors
- Verify `AI_BUILDER_TOKEN` is properly set
- Ensure all dependencies are listed in `package.json`

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