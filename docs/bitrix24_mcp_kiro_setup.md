# Bitrix24 MCP Setup for Kiro

## Problem Solved

The Bitrix24 MCP server doesn't exist as a standalone `uvx` package. This guide explains how to use Bitrix24 with Kiro's MCP system.

## Solution

We've created a Python wrapper (`bitrix24/mcp_server_wrapper.py`) that bridges Kiro's MCP protocol with the Bitrix24 MCP HTTP API.

## Prerequisites

1. **Python 3.9+** - Already installed for your project
2. **uv/uvx** - Now installed at `C:\Users\kam1k88\.local\bin`
3. **Bitrix24 JWT Token** - Already configured in `.env.mcp`

## Configuration

Your `.kiro/settings/mcp.json` is now configured to use the wrapper:

```json
{
  "mcpServers": {
    "bitrix24": {
      "command": "python",
      "args": ["bitrix24/mcp_server_wrapper.py"],
      "env": {
        "BITRIX24_MCP_URL": "https://mcp-dev.bitrix24.tech/mcp",
        "BITRIX24_MCP_TOKEN": "your-jwt-token",
        "BITRIX24_DOMAIN": "b24-z373vc.bitrix24.ru"
      },
      "disabled": false,
      "autoApprove": [
        "bitrix24_get_leads",
        "bitrix24_get_deals",
        "bitrix24_get_contacts"
      ]
    }
  }
}
```

## Available Tools

The MCP server provides these tools:

- `bitrix24_get_leads` - Get leads with optional filters
- `bitrix24_get_deals` - Get deals with optional filters
- `bitrix24_get_contacts` - Get contacts with optional filters
- `bitrix24_create_lead` - Create a new lead
- `bitrix24_add_comment` - Add comment to any entity

## Usage in Kiro

Once configured, you can use natural language:

```
"Get all new leads from Bitrix24"
"Create a lead for John Doe with phone +79001234567"
"Add a comment to lead 123 saying 'Follow up tomorrow'"
```

## Troubleshooting

### Error: "uvx not recognized"
**Solution**: Add to PATH permanently:
```powershell
# Add to user PATH
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\kam1k88\.local\bin",
    "User"
)
```

Then restart your terminal.

### Error: "Connection closed"
**Check**:
1. Python is in PATH: `python --version`
2. Wrapper file exists: `bitrix24/mcp_server_wrapper.py`
3. Token is valid (expires 2026-03-10)

### Error: "Module not found"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Direct Python Usage (Alternative)

If MCP integration doesn't work, use the Python client directly:

```python
from bitrix24.mcp_client import Bitrix24MCPClient

client = Bitrix24MCPClient()
leads = client.get_leads({"STATUS_ID": "NEW"})
```

## Token Expiry

Your JWT token expires on **2026-03-10**. To check:

```python
from bitrix24.mcp_client import Bitrix24MCPClient

client = Bitrix24MCPClient()
info = client.check_token_expiry()
print(f"Days until expiry: {info['days_until_expiry']}")
```

## Next Steps

1. Restart Kiro to load the new configuration
2. Test with: "Get leads from Bitrix24"
3. Check MCP logs for any errors

## Support

- MCP Logs: View in Kiro's MCP Logs panel
- Python Client: `bitrix24/mcp_client.py`
- Documentation: `docs/bitrix24_mcp_integration.md`
