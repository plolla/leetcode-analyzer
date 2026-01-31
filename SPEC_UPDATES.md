# Spec Updates: Claude Primary + OpenAI Fallback

## Summary

Updated the LeetCode Analysis Website spec and implementation to use:
- **Primary AI Service**: Claude API with Claude Sonnet 4.5 model
- **Fallback AI Service**: OpenAI API with GPT-5-mini model

## Changes Made

### 1. Spec Documents Updated

#### design.md
- Updated External Integrations section to specify Claude as primary and OpenAI GPT-5-mini as fallback
- Updated AIService interface documentation to reflect new implementations
- Updated cost analysis to reflect pay-as-you-go pricing for both services

#### requirements.md
- Updated Requirement 7 (AI Model Integration) to specify Claude as primary with automatic fallback to OpenAI
- Clarified acceptance criteria for failover behavior

#### tasks.md
- Updated Task 6 to reflect Claude implementation as primary
- Updated Task 6.2 to implement Claude service
- Updated Task 6.3 to implement OpenAI as fallback (marked as complete)

### 2. Backend Code Changes

#### New Files Created

**backend/services/claude_service.py**
- Implements ClaudeService class using Anthropic Python SDK
- Provides all four analysis types (complexity, hints, optimization, debugging)
- Includes retry logic and error handling
- Uses Claude Sonnet 4.5 model

**backend/services/ai_service_factory.py**
- Implements AIServiceWithFallback wrapper class
- Provides automatic fallback from primary to secondary service
- Includes logging for fallback events
- Factory function to create configured service instance

#### Modified Files

**backend/config.py**
- Updated AIProvider enum to include CLAUDE and OPENAI (removed HUGGINGFACE, OLLAMA)
- Added CLAUDE_API_KEY and CLAUDE_MODEL configuration
- Added FALLBACK_PROVIDER configuration
- Updated OPENAI_MODEL default to "gpt-5-mini"
- Added get_fallback_provider() method

**backend/.env.example**
- Updated to show Claude as primary provider
- Added Claude API configuration section
- Updated OpenAI section to show it as fallback
- Removed Hugging Face and Ollama configurations

**backend/.env**
- Set AI_PROVIDER=claude
- Set FALLBACK_PROVIDER=openai
- Added CLAUDE_API_KEY placeholder
- Updated OPENAI_MODEL to gpt-5-mini

**backend/requirements.txt**
- Added anthropic==0.40.0 package

### 3. How It Works

1. **Primary Service**: System attempts to use Claude API first for all analysis requests
2. **Automatic Fallback**: If Claude fails (API error, rate limit, unavailable), system automatically falls back to OpenAI
3. **Logging**: All fallback events are logged for monitoring
4. **Configuration**: Both API keys must be configured in .env file

### 4. Environment Variables Required

```bash
# Primary AI Service
CLAUDE_API_KEY=your_claude_api_key_here

# Fallback AI Service  
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Next Steps

To complete the implementation:

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   - Add your Claude API key to backend/.env
   - Ensure OpenAI API key is configured for fallback

3. **Update Main Application**:
   - Import `ai_service` from `ai_service_factory` instead of individual services
   - The factory handles all provider logic automatically

4. **Test Fallback Behavior**:
   - Test with valid Claude API key (should use Claude)
   - Test with invalid/missing Claude key (should fall back to OpenAI)
   - Verify logging shows fallback events

## Benefits

- **Reliability**: Automatic fallback ensures service availability
- **Performance**: Claude Sonnet 4.5 provides high-quality analysis
- **Cost-Effective**: GPT-5-mini provides economical fallback
- **Flexibility**: Easy to switch primary/fallback providers via configuration
