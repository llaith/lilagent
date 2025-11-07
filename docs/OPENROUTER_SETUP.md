# OpenRouter Setup Guide - Free LLM Access

This guide shows you how to use **OpenRouter** to access free LLM models for LilAgent, so you can test the system without paid API keys.

## What is OpenRouter?

[OpenRouter](https://openrouter.ai/) is an LLM gateway that provides access to multiple AI models through a single API. They offer:
- **Free tier models** (perfect for testing!)
- Unified API compatible with OpenAI SDK
- Pay-per-use models (no subscriptions)
- Multiple providers (Anthropic, OpenAI, Google, Meta, etc.)

## Quick Setup (5 minutes)

### Step 1: Create an OpenRouter Account

1. Go to https://openrouter.ai/
2. Click "Sign In" → "Sign up"
3. Create account (free, no credit card required)
4. Verify your email

### Step 2: Get Your API Key

1. Go to https://openrouter.ai/keys
2. Click "Create Key"
3. Give it a name: "LilAgent"
4. Copy the key (starts with `sk-or-v1-...`)

### Step 3: Configure LilAgent

Edit your `.env` file:

```bash
# Comment out or remove the exercise proxy config
# OPENAI_API_KEY=your-api-key-here
# OPENAI_API_BASE=https://api.example.com/v1

# Add OpenRouter configuration
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_API_BASE=https://openrouter.ai/api/v1

# Use free models
NORMALIZER_MODEL=google/gemma-2-9b-it:free
AGENT_MODEL=meta-llama/llama-3.1-70b-instruct:free
```

### Step 4: Test It!

```bash
poetry run lilagent tests/fixtures/calculator_spec.md /tmp/test-calc
```

## Available Free Models

OpenRouter offers several free models (`:free` suffix means no cost):

### Recommended for LilAgent

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `meta-llama/llama-3.1-70b-instruct:free` | Main agent work | Medium | Excellent |
| `meta-llama/llama-3.1-8b-instruct:free` | Spec normalization | Fast | Good |
| `google/gemma-2-9b-it:free` | Quick tasks | Fast | Good |
| `mistralai/mistral-7b-instruct:free` | Code generation | Fast | Good |

### Configuration Examples

**High Quality (slower, free):**
```bash
NORMALIZER_MODEL=meta-llama/llama-3.1-8b-instruct:free
AGENT_MODEL=meta-llama/llama-3.1-70b-instruct:free
```

**Fast (lower quality, free):**
```bash
NORMALIZER_MODEL=google/gemma-2-9b-it:free
AGENT_MODEL=mistralai/mistral-7b-instruct:free
```

**Balanced (good mix):**
```bash
NORMALIZER_MODEL=google/gemma-2-9b-it:free
AGENT_MODEL=meta-llama/llama-3.1-70b-instruct:free
```

## Free Tier Limits

OpenRouter's free models have some limitations:

- **Rate limits**: Typically 10-20 requests/minute
- **Context limits**: Varies by model (usually 4k-32k tokens)
- **Availability**: May have occasional queues during peak times

If you hit rate limits, the system will wait and retry automatically.

## Upgrading to Paid Models

If you want better performance, OpenRouter offers paid models:

### Premium Options (Low Cost)

```bash
# Claude Sonnet 4 (excellent for coding)
NORMALIZER_MODEL=anthropic/claude-haiku-4-0    # ~$0.10/1M input tokens
AGENT_MODEL=anthropic/claude-sonnet-4-0        # ~$1.00/1M input tokens

# GPT-4 (strong general purpose)
NORMALIZER_MODEL=openai/gpt-4o-mini            # ~$0.15/1M input tokens
AGENT_MODEL=openai/gpt-4o                      # ~$2.50/1M input tokens
```

### How to Add Credits

1. Go to https://openrouter.ai/credits
2. Add credits via credit card ($5 minimum)
3. Update your models in `.env` (remove `:free` suffix)

## Alternative Free Options

### 1. Groq (Fastest Free Inference)

[Groq](https://groq.com/) offers blazing-fast free inference:

```bash
OPENAI_API_KEY=your-groq-api-key
OPENAI_API_BASE=https://api.groq.com/openai/v1
NORMALIZER_MODEL=llama-3.1-8b-instant
AGENT_MODEL=llama-3.1-70b-versatile
```

Free tier: 30 requests/minute, 6000 requests/day

### 2. Together AI

[Together.ai](https://together.ai/) offers free trial credits:

```bash
OPENAI_API_KEY=your-together-api-key
OPENAI_API_BASE=https://api.together.xyz/v1
NORMALIZER_MODEL=meta-llama/Llama-3-8b-chat-hf
AGENT_MODEL=meta-llama/Llama-3-70b-chat-hf
```

### 3. Hugging Face Inference API

Free tier available at https://huggingface.co/inference-api

### 4. Local Models (Ollama)

Run models locally for free:

```bash
# Install Ollama: https://ollama.com/
ollama pull llama3.1:70b

# Update config
OPENAI_API_BASE=http://localhost:11434/v1
AGENT_MODEL=llama3.1:70b
```

## Troubleshooting

### "Rate limit exceeded"

**Solution**: Use OpenRouter's free tier with slower models or add credits.

```bash
# Slower but more reliable
AGENT_MODEL=google/gemma-2-9b-it:free
```

### "Model not found"

**Solution**: Check model name at https://openrouter.ai/models

Make sure to include `:free` suffix for free models.

### "Invalid API key"

**Solution**:
1. Verify key starts with `sk-or-v1-`
2. Check you copied the entire key
3. Ensure no extra spaces in `.env` file

### "Context length exceeded"

**Solution**: Spec is too long for the model's context window.

```bash
# Use model with larger context
AGENT_MODEL=meta-llama/llama-3.1-70b-instruct:free  # 32k context
```

## Cost Comparison

For reference, here's typical cost for generating a simple package:

| Provider | Model | Typical Cost |
|----------|-------|--------------|
| OpenRouter (free) | Llama 3.1 70B | $0.00 |
| OpenRouter (paid) | Claude Sonnet 4 | ~$0.50-$2.00 |
| Direct Anthropic | Claude Sonnet 4 | ~$0.50-$2.00 |
| Direct OpenAI | GPT-4o | ~$1.00-$3.00 |

Free tier is perfect for:
- Testing the system
- Learning how it works
- Small projects
- Proof of concepts

## Best Practices

1. **Start with free models** to understand the system
2. **Monitor token usage** in verbose mode
3. **Use cheaper models for normalization** (it's a simple task)
4. **Reserve expensive models for complex coding**
5. **Cache specifications** to avoid reprocessing

## Example: Full Free Setup

```bash
# .env configuration for completely free usage
OPENAI_API_KEY=sk-or-v1-YOUR-OPENROUTER-KEY
OPENAI_API_BASE=https://openrouter.ai/api/v1
NORMALIZER_MODEL=google/gemma-2-9b-it:free
AGENT_MODEL=meta-llama/llama-3.1-70b-instruct:free

# Optional: GitHub integration (free)
GITHUB_TOKEN=ghp_YOUR-GITHUB-TOKEN
GITHUB_REPO=yourusername/yourrepo

# No webhook needed for basic usage
# WEBHOOK_URL=

# Standard agent config
MAX_CODER_REVIEWER_ITERATIONS=3
MAX_PLANNING_UAT_ITERATIONS=2
ENABLE_VERBOSE_LOGGING=true
```

Run it:
```bash
poetry run lilagent tests/fixtures/calculator_spec.md /tmp/test
```

Total cost: **$0.00** ✅

## Getting Help

- OpenRouter Docs: https://openrouter.ai/docs
- OpenRouter Discord: https://discord.gg/openrouter
- LilAgent Issues: https://github.com/your-repo/issues

Happy coding! 🚀
