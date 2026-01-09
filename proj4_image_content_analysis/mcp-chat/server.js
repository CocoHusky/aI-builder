const express = require('express');
const path = require('path');
const fs = require('fs').promises;

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Create conversations directory
const conversationsDir = path.join(__dirname, 'conversations');
fs.mkdir(conversationsDir, { recursive: true }).catch(console.error);

// Model capabilities for server-side processing
const modelCapabilities = {
  'deepseek': ['text'],
  'gpt-5': ['text', 'vision'],
  'gpt-image-1.5': ['image_generation'],
  'grok-4-fast': ['text'],
  'gemini-2.5-pro': ['text', 'vision'],
  'gemini-3-flash-preview': ['text', 'vision'],
  'gemini-2.5-flash-image': ['image_generation'],
  'supermind-agent-v1': ['text', 'web_search']
};

// Chat with AI models
app.post('/chat', async (req, res) => {
  const { messages, model = 'grok-4-fast' } = req.body;
  console.log('Chat request received - Model:', model, 'Messages count:', messages.length);

  try {
    const token = process.env.AI_BUILDER_TOKEN;
    if (!token) {
      return res.json({
        choices: [{ message: { role: 'assistant', content: 'AI_BUILDER_TOKEN not set' } }]
      });
    }

    // Process messages - AI Builder doesn't support images, so strip them out
    const processedMessages = messages.map(msg => {
      // Always remove image data since AI Builder doesn't support it
      const { image, ...cleanMsg } = msg;
      return cleanMsg;
    });

    const requestBody = {
      model,
      messages: processedMessages,
      temperature: 0.7
    };

    console.log('Sending to AI Builder:', JSON.stringify(requestBody, null, 2));

    const response = await fetch('https://space.ai-builders.com/backend/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI Builder API Error:', response.status, errorText);
      return res.json({
        choices: [{ message: { role: 'assistant', content: `API Error: ${response.status}` } }]
      });
    }

    const data = await response.json();
    console.log('AI Builder API Success Response:', JSON.stringify(data, null, 2));
    res.json(data);
  } catch (error) {
    res.json({
      choices: [{ message: { role: 'assistant', content: `Error: ${error.message}` } }]
    });
  }
});

// Get available models
app.get('/models', async (req, res) => {
  try {
    const token = process.env.AI_BUILDER_TOKEN;
    if (!token) return res.status(500).json({ error: 'AI_BUILDER_TOKEN not set' });

    const response = await fetch('https://space.ai-builders.com/backend/v1/models', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) return res.status(500).json({ error: 'Failed to fetch models' });
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Save conversation
app.post('/conversations', async (req, res) => {
  try {
    const { id, title, messages, model } = req.body;
    const conversation = {
      id,
      title: title || 'New Chat',
      messages,
      model: model, // No hardcoded default - frontend must provide valid model
      timestamp: new Date().toISOString()
    };

    await fs.writeFile(
      path.join(conversationsDir, `${id}.json`),
      JSON.stringify(conversation, null, 2)
    );
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all conversations
app.get('/conversations', async (req, res) => {
  try {
    const files = await fs.readdir(conversationsDir);
    const conversations = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        try {
          const data = await fs.readFile(path.join(conversationsDir, file), 'utf8');
          const conv = JSON.parse(data);
          conversations.push({
            id: conv.id,
            title: conv.title,
            model: conv.model,
            timestamp: conv.timestamp
          });
        } catch (e) { /* skip invalid files */ }
      }
    }

    conversations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    res.json(conversations);
  } catch (error) {
    res.json([]);
  }
});

// Load specific conversation
app.get('/conversations/:id', async (req, res) => {
  try {
    const data = await fs.readFile(path.join(conversationsDir, `${req.params.id}.json`), 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    res.status(404).json({ error: 'Not found' });
  }
});

// Delete conversation
app.delete('/conversations/:id', async (req, res) => {
  try {
    await fs.unlink(path.join(conversationsDir, `${req.params.id}.json`));
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Serve chat interface
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`🐕 Coco Chat server running at http://localhost:${PORT}`);
  console.log(`🐶 Woof woof! Ready to chat with your furry AI friend!`);
});
