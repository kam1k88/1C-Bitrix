# Project Structure

## Directory Organization

```
├── ai_services/           # AI service integrations
│   ├── openai_service.py  # OpenAI/GPT-4 client
│   └── claude_service.py  # Anthropic/Claude client
│
├── automation/            # Business process automation
│   ├── lead_processor.py  # Lead analysis and processing
│   ├── mass_operations.py # Batch operations
│   ├── sync.py            # Data synchronization
│   └── mcp_scenarios.py   # MCP-based scenarios
│
├── bitrix24/              # Bitrix24 CRM integration
│   ├── client.py          # REST API client
│   ├── js_integration.py  # JS SDK integration
│   └── mcp_client.py      # MCP protocol client
│
├── onec/                  # 1С ERP integration
│   └── client.py          # HTTP services client
│
├── config/                # Configuration management
│   └── settings.py        # Centralized settings
│
├── docs/                  # Documentation
│   ├── user_guide.md      # User documentation
│   ├── setup_guide.md     # Installation guide
│   ├── prompts_library.md # AI prompt templates
│   └── ...                # Integration guides
│
├── examples/              # Usage examples
│   ├── README.md          # Examples overview
│   ├── scenario_*.py      # Real-world scenarios
│   └── real_world_scenarios.py
│
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment configuration (not in git)
```

## Module Responsibilities

### ai_services/
Contains AI service wrappers with standardized interfaces. Each service class:
- Initializes with API keys from settings
- Provides domain-specific methods (analyze_lead, generate_offer, etc.)
- Handles prompt engineering internally
- Returns structured data

### automation/
Business logic layer that orchestrates AI services and integrations:
- `LeadProcessor` - Main class for lead workflow automation
- `mass_operations.py` - Batch processing utilities
- `sync.py` - Data synchronization between systems
- `mcp_scenarios.py` - Natural language automation scenarios

### bitrix24/
Three integration approaches:
- `client.py` - REST API wrapper (basic operations)
- `js_integration.py` - JS SDK for advanced features
- `mcp_client.py` - Model Context Protocol for AI-driven operations

### onec/
1С integration via HTTP services:
- Client/counterparty management
- Order creation and synchronization
- Price and inventory updates

### config/
Centralized configuration using Settings class pattern:
- Loads from environment variables
- Provides typed access to configuration
- Single source of truth for all settings

## Code Conventions

### Class Structure
- Service classes use dependency injection pattern
- All external API clients inherit common patterns
- Type hints used throughout (`Dict`, `List`, `Optional`)

### Error Handling
- API calls wrapped in try/except blocks
- Graceful degradation when services unavailable
- Logging for debugging and audit

### Naming Conventions
- Classes: PascalCase (`LeadProcessor`, `Bitrix24Client`)
- Functions/methods: snake_case (`process_new_lead`, `get_leads`)
- Constants: UPPER_SNAKE_CASE (`MAX_TOKENS`, `DEFAULT_AI_MODEL`)
- Private methods: prefix with underscore (`_check_client_in_1c`)

### API Response Format
Consistent response structure across endpoints:
```python
{
    "success": bool,
    "data": dict | list,  # or specific keys like "analysis", "offer"
    "error": str  # only on failure
}
```

### Documentation
- Docstrings for all classes and public methods
- Russian language for user-facing documentation
- English for technical/code documentation
- Inline comments for complex logic only

## Integration Patterns

### Service Initialization
Services initialized once and reused:
```python
lead_processor = LeadProcessor()  # In main.py
# Internally initializes all required clients
```

### Data Flow
1. External event (webhook) → FastAPI endpoint
2. Endpoint → Automation layer (LeadProcessor)
3. Automation → AI services + CRM/ERP clients
4. Results → Update CRM + Return response

### Configuration Access
Always use centralized settings:
```python
from config.settings import settings
api_key = settings.OPENAI_API_KEY
```

## File Naming
- Python modules: lowercase with underscores
- Documentation: lowercase with underscores
- Examples: descriptive names with scenario prefix
