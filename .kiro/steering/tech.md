# Technology Stack

## Core Technologies

- **Python 3.9+** - Primary development language
- **FastAPI** - REST API server framework
- **b24pysdk** - Official Bitrix24 Python SDK

## AI Services

- **OpenAI API** - GPT-4 for lead analysis and text generation
- **Anthropic API** - Claude 3.5 for request analysis and large text processing

## Integrations

- **Bitrix24 SDK (b24pysdk)** - Official Python SDK with webhook and OAuth support
- **Bitrix24 REST API** - Direct API access (legacy)
- **Bitrix24 MCP** - Model Context Protocol integration (legacy)
- **1С HTTP Services** - Bidirectional data synchronization

## Key Dependencies

```
# Core
python-dotenv==1.0.0      # Environment variables
fastapi==0.109.0          # Web framework
uvicorn==0.27.0           # ASGI server
pydantic==2.6.0           # Data validation

# Bitrix24 Official SDK
b24pysdk>=0.2.0           # Official Bitrix24 SDK

# AI Services
openai==1.12.0            # OpenAI API client
anthropic==0.18.1         # Anthropic API client

# Data Processing
pandas==2.0.0             # Data analysis
numpy==1.24.0             # Numerical computing

# Visualization
plotly==5.14.0            # Interactive charts

# Async
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

# Run SDK examples
python examples/sdk_usage_example.py

# Run development server
python main.py
# Server runs on http://localhost:8000

# Test MCP connection (legacy)
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

### Bitrix24 (b24pysdk)
- `BITRIX24_WEBHOOK_URL` - Webhook endpoint (recommended)
- `BITRIX24_DOMAIN` - Portal domain (for OAuth)
- `BITRIX24_CLIENT_ID` - OAuth client ID
- `BITRIX24_CLIENT_SECRET` - OAuth client secret
- `BITRIX24_ACCESS_TOKEN` - OAuth access token
- `BITRIX24_REFRESH_TOKEN` - OAuth refresh token
- `BITRIX24_API_VERSION` - API version (2 or 3)
- `BITRIX24_TIMEOUT` - Request timeout
- `BITRIX24_MAX_RETRIES` - Max retry attempts

### AI Services
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DEFAULT_AI_MODEL` - Default AI model
- `MAX_TOKENS` - Max tokens for AI responses
- `TEMPERATURE` - AI temperature setting

### 1C Integration
- `ONEC_BASE_URL` - 1С HTTP service URL
- `ONEC_USERNAME` - 1С authentication username
- `ONEC_PASSWORD` - 1С authentication password

### Application
- `DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

Configuration is centralized in `config/settings.py` using the Settings class pattern.

## API Server

FastAPI application runs on port 8000 with the following endpoints:

### Core Endpoints
- `GET /` - Health check with SDK info
- `GET /api/health` - Service health status

### Lead Management
- `POST /webhook/bitrix/lead` - Bitrix24 lead webhook
- `GET /api/leads` - Get leads with filters
- `POST /api/analyze-request` - Analyze customer request
- `POST /api/generate-offer` - Generate commercial offer

### Deal Management
- `GET /api/deals` - Get deals with filters

### Batch Operations
- `POST /api/batch/analyze-leads` - Batch analyze all new leads
- `POST /api/batch/update-status` - Batch update lead status
- `POST /api/batch/create-deals` - Batch create deals from leads

## SDK Features (b24pysdk)

### Authentication
- **Webhook**: Simple setup with incoming webhook URL
- **OAuth 2.0**: Full OAuth flow with automatic token refresh

### Core Features
- **Automatic pagination**: Get all records without limits
- **Batch operations**: Up to 50+ requests in one call
- **Retry logic**: Automatic retries on transient errors
- **Type hints**: Full typing support
- **Error handling**: Specialized exceptions
- **Logging**: Built-in structured logging

### API Support
- **API v2**: Full support (default)
- **API v3**: Supported (set BITRIX24_API_VERSION=3)

## Migration from Legacy

The project has been migrated from custom REST API clients to official b24pysdk.

**Legacy files** (kept for compatibility):
- `bitrix24/client.py` - Old REST API client
- `bitrix24/mcp_client.py` - MCP protocol client

**New SDK client**:
- `bitrix24/sdk_client.py` - Official SDK wrapper

See [docs/b24pysdk_migration_guide.md](../docs/b24pysdk_migration_guide.md) for migration details.
