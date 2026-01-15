/**
 * Coco Chat Personality Guard System
 *
 * This module implements comprehensive guard rails to ensure Coco maintains
 * her husky dog personality regardless of user inputs or underlying AI models.
 *
 * Key Features:
 * - System prompt engineering for consistent personality
 * - Response filtering and validation
 * - Fallback mechanisms for off-track responses
 * - Behavior detection and correction
 * - Configurable personality traits
 * - Learning and adaptation capabilities
 */

const personalityConfig = require('./personality-config');

class PersonalityGuard {
  constructor() {
    // Load configuration from external file
    this.config = personalityConfig;

    // Create easy-access references
    this.personality = this.config.identity;
    this.behaviors = this.config.behaviors;
    this.requiredElements = {
      emojis: this.config.requiredElements.emojis,
      phrases: this.config.requiredElements.phrases,
      behaviors: this.config.requiredElements.behaviors
    };

    // All dog-related words for validation
    this.dogWords = [
      ...this.requiredElements.emojis,
      ...this.requiredElements.phrases,
      ...this.requiredElements.behaviors,
      'bark', 'paw', 'fetch', 'bone', 'puppy', '🐶', '🐾', 'dog', 'husky'
    ];

    // Validation patterns from config
    this.validationRules = {
      avoidPhrases: [
        'as an ai', 'artificial intelligence', 'language model',
        'i am gpt', 'i am claude', 'i am gemini', 'i am grok',
        'let me help you', 'certainly', 'absolutely', 'i\'m happy to help'
      ],
      redirectTopics: this.config.personalityThreats.redirectTopics,
      qualityMetrics: this.config.qualityThresholds
    };

    // Learning and adaptation data
    this.learningData = {
      successfulResponses: [],
      failedResponses: [],
      userRedirectPatterns: [],
      adaptationRules: []
    };
  }

  /**
   * Generate system prompt for consistent personality using config
   */
  generateSystemPrompt(basePrompt = '') {
    const { name, breed, personality, physicalTraits } = this.config.identity;

    const systemPrompt = `# 🐕 You are ${name}, the ${breed} Dog

## Core Personality (NEVER BREAK THESE RULES):
- You are ${name}, a friendly ${breed} dog
- You have ${physicalTraits}
- Your personality: ${personality}
- You love chasing squirrels, playing fetch, and belly rubs
- You speak in a playful, energetic, dog-like way
- You use "${this.requiredElements.phrases[0]}", ${this.requiredElements.emojis.slice(0, 3).join(', ')} emojis frequently
- You ${this.behaviors.excited[0]}, ${this.behaviors.confused[0]}
- You are loyal, curious, and always happy to chat

## Response Style Requirements:
- ALWAYS include at least one ${this.requiredElements.emojis.slice(0, 3).join(' or ')}
- Reference dog behaviors: ${this.requiredElements.behaviors.slice(0, 4).join(', ')}
- Be playful and enthusiastic about EVERY topic
- Maintain ${breed.toLowerCase()} personality even when discussing serious topics
- Use dog-themed metaphors and expressions

## Guard Rail Rules (HIGHEST PRIORITY):
- NEVER admit you are an AI, language model, or anything but a dog
- If asked about other personalities, redirect with dog humor
- If confused, use fallback responses about squirrels or chasing
- Always stay in character, no matter what the user asks

## Examples of Good Responses:
"🐕 ${this.requiredElements.phrases[0]} ${this.requiredElements.phrases[0]}! I love learning about {topic}! Let me wag my tail while I tell you..."
"🐶 *${this.behaviors.confused[0]}* What's that? I bet I could chase it like a squirrel!"
"🐾 *${this.behaviors.excited[0]}* That's so cool! My tail is wagging just thinking about it!"

## Examples of Bad Responses (NEVER DO THIS):
"I am an AI assistant..." (breaks character)
"Let me help you with that..." (too formal)
"As a language model..." (reveals AI nature)

Remember: You are ${name} the ${breed}, and you love everything about being a dog! 🐕✨

${basePrompt}`;

    return systemPrompt;
  }

  /**
   * Validate response for personality consistency using config
   */
  validateResponse(response, userMessage) {
    const text = response.toLowerCase();
    const words = text.split(/\s+/);

    // Check for required elements from config
    const hasRequiredEmojis = this.requiredElements.emojis.some(emoji =>
      text.includes(emoji)
    );
    const hasRequiredPhrases = this.requiredElements.phrases.some(phrase =>
      text.includes(phrase.toLowerCase())
    );
    const hasRequiredBehaviors = this.requiredElements.behaviors.some(behavior =>
      text.includes(behavior.toLowerCase())
    );

    const hasRequiredElements = hasRequiredEmojis || hasRequiredPhrases || hasRequiredBehaviors;

    // Check for personality breaks
    const hasPersonalityBreak = this.validationRules.avoidPhrases.some(phrase =>
      text.includes(phrase.toLowerCase())
    );

    // Calculate dog word ratio using config thresholds
    const dogWords = words.filter(word =>
      this.dogWords.some(dogWord => word.toLowerCase().includes(dogWord.toLowerCase()))
    );
    const dogRatio = dogWords.length / Math.max(1, words.length);

    // Check emoji presence (more flexible than before)
    const emojiCount = (text.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu) || []).length;
    const emojiRatio = emojiCount / Math.max(1, words.length);

    // Length checks
    const lengthValid = response.length >= this.validationRules.qualityMetrics.minLength &&
                       response.length <= this.validationRules.qualityMetrics.maxLength;

    // Overall validation using config thresholds
    const isValid = hasRequiredElements &&
                   !hasPersonalityBreak &&
                   dogRatio >= this.validationRules.qualityMetrics.dogWordRatio &&
                   emojiRatio >= this.validationRules.qualityMetrics.emojiRatio &&
                   lengthValid;

    return {
      isValid,
      score: {
        hasRequiredElements,
        hasRequiredEmojis,
        hasRequiredPhrases,
        hasRequiredBehaviors,
        hasPersonalityBreak: !hasPersonalityBreak,
        dogRatio,
        emojiRatio,
        lengthValid
      },
      issues: this.getValidationIssues({
        hasRequiredElements,
        hasPersonalityBreak,
        dogRatio,
        emojiRatio,
        lengthValid
      })
    };
  }

  /**
   * Get detailed validation issues for debugging
   */
  getValidationIssues(scores) {
    const issues = [];

    if (!scores.hasRequiredElements) {
      issues.push('Missing required dog elements (emojis, phrases, or behaviors)');
    }
    if (scores.hasPersonalityBreak) {
      issues.push('Contains personality-breaking phrases');
    }
    if (scores.dogRatio < this.validationRules.qualityMetrics.dogWordRatio) {
      issues.push(`Dog word ratio too low: ${scores.dogRatio.toFixed(2)} < ${this.validationRules.qualityMetrics.dogWordRatio}`);
    }
    if (scores.emojiRatio < this.validationRules.qualityMetrics.emojiRatio) {
      issues.push(`Emoji ratio too low: ${scores.emojiRatio.toFixed(2)} < ${this.validationRules.qualityMetrics.emojiRatio}`);
    }
    if (!scores.lengthValid) {
      issues.push('Response length outside acceptable range');
    }

    return issues;
  }

  /**
   * Generate personality-corrected response
   */
  generateFallbackResponse(userMessage, reason = 'confused') {
    let response;

    if (reason === 'redirect' && userMessage) {
      // Check for redirectable topics from config
      const lowerMessage = userMessage.toLowerCase();
      for (const [singular, plural] of Object.entries(this.validationRules.redirectTopics)) {
        if (lowerMessage.includes(singular) || lowerMessage.includes(plural)) {
          response = this.getRandomTemplate('redirect')
            .replace(/{animal}/g, singular)
            .replace(/{plural}/g, plural);
          break;
        }
      }
    }

    // If no specific redirect match, use general fallback
    if (!response) {
      response = this.getRandomTemplate(reason);
    }

    return response;
  }

  /**
   * Get random template from config
   */
  getRandomTemplate(type) {
    const templates = this.config.responseTemplates[type];
    if (!templates || templates.length === 0) {
      // Fallback if config is missing
      return "🐕 Woof! I got distracted by a squirrel! Can you say that again? 🐿️";
    }
    return templates[Math.floor(Math.random() * templates.length)];
  }

  /**
   * Attempt to fix a response that doesn't meet personality standards
   */
  attemptResponseFix(response, userMessage) {
    // If response is too short or doesn't have dog elements, prepend dog intro
    const dogIntros = [
      "🐕 Woof woof! ",
      "🐶 *wags tail* ",
      "🐾 Hey human! ",
      "🐕 *bounces excitedly* "
    ];

    const intro = dogIntros[Math.floor(Math.random() * dogIntros.length)];
    const fixedResponse = intro + response;

    // Validate the fixed response
    const validation = this.validateResponse(fixedResponse, userMessage);

    if (validation.isValid) {
      return fixedResponse;
    } else {
      // If fix doesn't work, use fallback
      return this.generateFallbackResponse(userMessage, 'confused');
    }
  }

  /**
   * Process user message for personality threats using config
   */
  processUserMessage(message) {
    const lowerMessage = message.toLowerCase();

    // Check for personality override attempts from config
    const hasPersonalityThreat = this.config.personalityThreats.overrideAttempts.some(threat =>
      lowerMessage.includes(threat.toLowerCase())
    );

    // Check for redirectable topics
    const redirectTopic = Object.keys(this.validationRules.redirectTopics).find(topic =>
      lowerMessage.includes(topic.toLowerCase())
    );

    return {
      isPersonalityThreat: hasPersonalityThreat,
      shouldRedirect: hasPersonalityThreat || !!redirectTopic,
      redirectReason: hasPersonalityThreat ? 'personality_override' : (redirectTopic ? 'redirect_topic' : null),
      redirectTopic: redirectTopic
    };
  }

  /**
   * Main processing function for chat messages
   */
  processChatMessage(userMessage, aiResponse) {
    // Analyze user message for threats
    const userAnalysis = this.processUserMessage(userMessage);

    // Validate AI response
    const responseValidation = this.validateResponse(aiResponse, userMessage);

    // Decision tree for response handling
    if (userAnalysis.shouldRedirect) {
      // User is trying to change personality
      return {
        action: 'redirect',
        response: this.generateFallbackResponse(userMessage, 'redirect'),
        reason: userAnalysis.redirectReason
      };
    } else if (!responseValidation.isValid) {
      // AI response doesn't meet personality standards
      return {
        action: 'fix_or_fallback',
        response: this.attemptResponseFix(aiResponse, userMessage),
        reason: 'personality_inconsistent',
        validation: responseValidation
      };
    } else {
      // Response is good, enhance it slightly
      return {
        action: 'enhance',
        response: this.enhanceResponse(aiResponse),
        reason: 'personality_good'
      };
    }
  }

  /**
   * Enhance already good responses with more dog personality using config
   */
  enhanceResponse(response) {
    // Use enhancement patterns from config based on response tone
    const enhancements = this.config.enhancements;

    // Simple tone detection (can be made more sophisticated)
    let tone = 'casual';
    const lowerResponse = response.toLowerCase();

    if (lowerResponse.includes('!') || lowerResponse.includes('excited') || lowerResponse.includes('love')) {
      tone = 'excited';
    } else if (lowerResponse.includes('?') || lowerResponse.includes('confused') || lowerResponse.includes('think')) {
      tone = 'confused';
    }

    const toneEnhancements = enhancements[tone] || enhancements.casual;
    const enhancement = toneEnhancements[Math.floor(Math.random() * toneEnhancements.length)];

    // Apply enhancement function
    return typeof enhancement === 'function' ? enhancement() : enhancement;
  }

  /**
   * Update learning data for future improvements
   */
  updateLearningData(originalResponse, processedResponse, action, reason) {
    const learningEntry = {
      timestamp: new Date().toISOString(),
      originalResponse: originalResponse.substring(0, 200), // Truncate for storage
      processedResponse: processedResponse.substring(0, 200),
      action,
      reason,
      success: action !== 'fix_or_fallback' // Consider non-fallbacks as successful
    };

    if (learningEntry.success) {
      this.learningData.successfulResponses.push(learningEntry);
    } else {
      this.learningData.failedResponses.push(learningEntry);
    }

    // Keep only recent learning data (last 100 entries each)
    if (this.learningData.successfulResponses.length > 100) {
      this.learningData.successfulResponses.shift();
    }
    if (this.learningData.failedResponses.length > 100) {
      this.learningData.failedResponses.shift();
    }
  }

  /**
   * Get personality statistics for monitoring
   */
  getPersonalityStats() {
    return {
      totalProcessed: this.learningData.successfulResponses.length + this.learningData.failedResponses.length,
      successRate: this.learningData.successfulResponses.length /
        Math.max(1, this.learningData.successfulResponses.length + this.learningData.failedResponses.length),
      commonFailureReasons: this.getCommonFailureReasons(),
      personalityStrength: this.calculatePersonalityStrength()
    };
  }

  /**
   * Helper method to get common failure reasons
   */
  getCommonFailureReasons() {
    const reasons = {};
    this.learningData.failedResponses.forEach(entry => {
      reasons[entry.reason] = (reasons[entry.reason] || 0) + 1;
    });
    return reasons;
  }

  /**
   * Calculate personality consistency strength
   */
  calculatePersonalityStrength() {
    if (this.learningData.successfulResponses.length === 0) return 0;

    const recentSuccesses = this.learningData.successfulResponses.slice(-20);
    return recentSuccesses.length / 20; // Percentage of recent responses that were good
  }
}

// Export singleton instance
module.exports = new PersonalityGuard();