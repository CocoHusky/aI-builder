const express = require('express');
const path = require('path');
const fs = require('fs').promises;

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Create conversations directory if it doesn't exist
const conversationsDir = path.join(__dirname, 'conversations');
fs.mkdir(conversationsDir, { recursive: true }).catch(console.error);

app.post('/chat', async (req, res) => {
  const { messages, model = 'grok-4-fast' } = req.body;

  try {
    const token = process.env.AI_BUILDER_TOKEN;
    if (!token) {
      return res.json({
        choices: [{
          message: {
            role: 'assistant',
            content: '❌ AI_BUILDER_TOKEN not set. Run: export AI_BUILDER_TOKEN=your_token'
          }
        }]
      });
    }

    const response = await fetch('https://space.ai-builders.com/backend/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        model: model,
        messages,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const error = await response.text();
      return res.json({
        choices: [{
          message: {
            role: 'assistant',
            content: `❌ API Error ${response.status}: ${error}`
          }
        }]
      });
    }

    const data = await response.json();
    res.json(data);

  } catch (error) {
    res.json({
      choices: [{
        message: {
          role: 'assistant',
          content: `❌ Network Error: ${error.message}`
        }
      }]
    });
  }
});


// Get available models
app.get('/models', async (req, res) => {
  try {
    const token = process.env.AI_BUILDER_TOKEN;
    if (!token) {
      return res.status(500).json({ error: 'AI_BUILDER_TOKEN not set' });
    }

    const response = await fetch('https://space.ai-builders.com/backend/v1/models', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to fetch models' });
    }

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
    const filename = `${id}.json`;
    const filepath = path.join(conversationsDir, filename);

    const conversation = {
      id,
      title: title || 'New Chat',
      messages,
      model: model || 'grok-4-fast',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await fs.writeFile(filepath, JSON.stringify(conversation, null, 2));
    res.json({ success: true, conversation });
  } catch (error) {
    console.error('Error saving conversation:', error);
    res.status(500).json({ success: false, error: error.message });
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
          const filepath = path.join(conversationsDir, file);
          const data = await fs.readFile(filepath, 'utf8');
          const conversation = JSON.parse(data);
          conversations.push({
            id: conversation.id,
            title: conversation.title,
            model: conversation.model,
            createdAt: conversation.createdAt,
            updatedAt: conversation.updatedAt,
            messageCount: conversation.messages.length
          });
        } catch (error) {
          console.error(`Error reading ${file}:`, error.message);
        }
      }
    }

    // Sort by updated date (newest first)
    conversations.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    res.json(conversations);
  } catch (error) {
    console.error('Error listing conversations:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get specific conversation
app.get('/conversations/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const filename = `${id}.json`;
    const filepath = path.join(conversationsDir, filename);

    const data = await fs.readFile(filepath, 'utf8');
    const conversation = JSON.parse(data);
    res.json(conversation);
  } catch (error) {
    console.error('Error loading conversation:', error);
    res.status(404).json({ error: 'Conversation not found' });
  }
});

// Update conversation
app.put('/conversations/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { title, messages, model } = req.body;
    const filename = `${id}.json`;
    const filepath = path.join(conversationsDir, filename);

    // Read existing conversation
    const existingData = await fs.readFile(filepath, 'utf8');
    const existingConversation = JSON.parse(existingData);

    // Update conversation
    const updatedConversation = {
      ...existingConversation,
      title: title || existingConversation.title,
      messages: messages || existingConversation.messages,
      model: model || existingConversation.model,
      updatedAt: new Date().toISOString()
    };

    await fs.writeFile(filepath, JSON.stringify(updatedConversation, null, 2));
    res.json({ success: true, conversation: updatedConversation });
  } catch (error) {
    console.error('Error updating conversation:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Delete conversation
app.delete('/conversations/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const filename = `${id}.json`;
    const filepath = path.join(conversationsDir, filename);

    await fs.unlink(filepath);
    res.json({ success: true, message: 'Conversation deleted' });
  } catch (error) {
    console.error('Error deleting conversation:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Serve the main chat interface
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Coco Chat running on port ${PORT}`);
  console.log(`Access at: http://localhost:${PORT}`);
});
