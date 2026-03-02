# Technology Stack

## Core Technologies

- **Python 3.9+** - Primary development language
- **FastAPI** - REST API server framework
- **Node.js 18+** - Required for Bitrix24 JS SDK integration

## AI Services

- **OpenAI API** - GPT-4 for lead analysis and text generation
- **Anthropic API** - Claude 3.5 for request analysis and large text processing

## Integrations

- **Bitrix24 REST API** - CRM integration via webhooks
- **Bitrix24 JS SDK** - Advanced operations (batch, streaming)
- **Bitrix24 MCP** - Model Context Protocol integration
- **1С HTTP Services** - Bidirectional data synchronization

## Key Dependencies

```
requests==2.31.0          # HTTP client
python-dotenv==1.0.0      # Environment variables
openai==1.12.0            # OpenAI API client
anthropic==0.18.1         # Anthropic API client
fastapi==0.109.0          # Web framework
uvicorn==0.27.0           # ASGI server
pydantic==2.6.0           # Data validation
aiohttp==3.9.3            # Async HTTP client
```

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
python main.py
# Server runs on http://localhost:8000

# Test MCP connection
python test_mcp_connection.py
```

### Production

```bash
# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Run with auto-reload (development)
uvicorn main:app --reload
```

## Configuration

All configuration is managed through environment variables in `.env`:

- `BITRIX24_WEBHOOK_URL` - Bitrix24 webhook endpoint
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `ONEC_BASE_URL` - 1С HTTP service URL
- `ONEC_USERNAME` - 1С authentication username
- `ONEC_PASSWORD` - 1С authentication password

Configuration is centralized in `config/settings.py` using the Settings class pattern.

## API Server

FastAPI application runs on port 8000 with the following endpoints:

- `GET /` - Health check
- `POST /webhook/bitrix/lead` - Bitrix24 lead webhook
- `POST /api/analyze-request` - Analyze customer request
- `POST /api/generate-offer` - Generate commercial offer
- `GET /api/leads` - Get leads from Bitrix24
