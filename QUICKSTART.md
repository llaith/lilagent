# Quick Start Guide

Get up and running with LilAgent in 5 minutes.

## 1. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -e .
```

## 2. Configure API Access

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your API credentials
nano .env  # or your preferred editor
```

Required configuration in `.env`:
```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://your-llm-proxy.com/v1
NORMALIZER_MODEL=evals-anthropic/claude-haiku-4-0
AGENT_MODEL=evals-anthropic/claude-sonnet-4-0
```

Optional:
```bash
WEBHOOK_URL=http://localhost:8000/agent-blocked
```

## 3. Run the Calculator Example

```bash
# Generate a calculator package from the test specification
poetry run lilagent tests/fixtures/calculator_spec.md /tmp/calculator

# This will:
# 1. Normalize and enhance the specification
# 2. Plan implementation tasks
# 3. Generate code with coder-reviewer feedback loop
# 4. Validate with UAT
# 5. Generate documentation
```

## 4. Test the Generated Package

```bash
# Navigate to the output
cd /tmp/calculator

# Install the generated package
pip install -e .

# Try it out
calculator add 5 3
# Output: 8.0

# Run tests
pytest
```

## 5. Create Your Own Specification

Create a markdown file with your requirements:

```markdown
# My Project Specification

Build a CLI tool that...

## Requirements
- Feature 1
- Feature 2

## Technical Details
- Language: Python 3.11+
- Should be installable via pip
- Include tests
```

Then run:
```bash
poetry run lilagent my-spec.md ./output-directory
```

## Understanding the Output

After successful execution, your output directory contains:

```
output-directory/
├── SPECIFICATION.md          # Enhanced structured spec
├── README.md                 # Generated documentation
├── setup.py or pyproject.toml  # Package configuration
├── src/ or lib/              # Source code
│   └── your_package/
│       ├── __init__.py
│       └── ...
└── tests/                    # Test files
    └── test_*.py
```

## Troubleshooting

### "Configuration validation failed"
- Check your `.env` file exists and has valid API key
- Verify `OPENAI_API_KEY` is set

### "Command timed out"
- Some operations (like package installation) can take time
- Check the verbose output for progress
- Consider increasing timeout in code if needed

### UAT Failed
- Check the detailed output for what failed
- The system will attempt gap analysis and replanning
- After max iterations (2), it will stop and report

### Agent seems stuck
- Enable verbose logging: `lilagent spec.md output/ -v`
- Check if webhook notifications are being sent (if configured)
- Review agent prompts in `src/lilagent/prompts/system_prompts.py`

## Next Steps

1. **Try different specifications**: Start simple, gradually increase complexity
2. **Customize agent prompts**: Edit `src/lilagent/prompts/system_prompts.py` to tune behavior
3. **Adjust iteration limits**: Modify `Config.MAX_CODER_REVIEWER_ITERATIONS` in `.env`
4. **Monitor costs**: Track token usage in verbose output

## Advanced Usage

### Custom Models

Edit `.env` to use different models:
```bash
# Use GPT models instead of Claude
NORMALIZER_MODEL=evals-openai/gpt-4o-mini
AGENT_MODEL=evals-openai/gpt-4
```

### Webhook Notifications

Set up a webhook endpoint to receive notifications when the agent is blocked:

```python
# Simple Flask webhook receiver
from flask import Flask, request
app = Flask(__name__)

@app.route('/agent-blocked', methods=['POST'])
def handle_blocked():
    data = request.json
    print(f"Agent blocked: {data['message']}")
    # Send email, Slack notification, etc.
    return {"status": "received"}

app.run(port=8000)
```

Then set in `.env`:
```bash
WEBHOOK_URL=http://localhost:8000/agent-blocked
```

### Iteration Control

Adjust max iterations in `.env`:
```bash
MAX_CODER_REVIEWER_ITERATIONS=5  # Default: 3
MAX_PLANNING_UAT_ITERATIONS=3    # Default: 2
```

## Getting Help

- Check the full [README.md](README.md) for architecture details
- Review [src/lilagent/prompts/system_prompts.py](src/lilagent/prompts/system_prompts.py) for agent behaviors
- Examine test cases in `tests/` for examples
- Enable verbose mode for detailed execution logs

## Example Specifications

### CLI Tool
```markdown
# Task Manager CLI

Build a command-line task management tool.

## Requirements
- Add, list, complete, and delete tasks
- Store tasks in JSON file
- Support task priorities
- Include tests

## Technical
- Python 3.11+
- Use argparse for CLI
- pytest for testing
```

### Python Library
```markdown
# Data Validator Library

Create a library for validating data structures.

## Requirements
- Validate dictionaries against schemas
- Support nested structures
- Type checking (string, int, bool, list, dict)
- Helpful error messages

## Technical
- Python 3.11+ with type hints
- No external dependencies
- Full test coverage
```

### Web API
```markdown
# RESTful Todo API

Build a REST API for managing todos.

## Requirements
- CRUD operations (Create, Read, Update, Delete)
- JSON responses
- SQLite database
- API documentation

## Technical
- Python 3.11+
- Flask or FastAPI
- pytest for testing
- OpenAPI/Swagger docs
```

Happy coding! 🚀
