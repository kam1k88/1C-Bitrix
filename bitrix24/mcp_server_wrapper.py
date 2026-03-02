#!/usr/bin/env python3
"""
MCP Server Wrapper for Bitrix24
Bridges Kiro's MCP protocol with Bitrix24 MCP API
"""

import sys
import json
import os
from bitrix24.mcp_client import Bitrix24MCPClient

def main():
    """Main MCP server loop"""
    client = Bitrix24MCPClient()
    
    # Read MCP requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            # Route to appropriate Bitrix24 method
            if method == "tools/list":
                response = {
                    "tools": [
                        {"name": "bitrix24_get_leads", "description": "Get leads from Bitrix24"},
                        {"name": "bitrix24_get_deals", "description": "Get deals from Bitrix24"},
                        {"name": "bitrix24_get_contacts", "description": "Get contacts from Bitrix24"},
                        {"name": "bitrix24_create_lead", "description": "Create a new lead"},
                        {"name": "bitrix24_add_comment", "description": "Add comment to entity"},
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                
                # Execute the tool
                if tool_name == "bitrix24_get_leads":
                    result = client.get_leads(tool_params.get("filter"))
                elif tool_name == "bitrix24_get_deals":
                    result = client.get_deals(tool_params.get("filter"))
                elif tool_name == "bitrix24_get_contacts":
                    result = client.get_contacts(tool_params.get("filter"))
                elif tool_name == "bitrix24_create_lead":
                    result = client.create_lead(tool_params.get("fields"))
                elif tool_name == "bitrix24_add_comment":
                    result = client.add_comment(
                        tool_params.get("entity_type"),
                        tool_params.get("entity_id"),
                        tool_params.get("comment")
                    )
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                response = {"content": [{"type": "text", "text": json.dumps(result)}]}
            else:
                response = {"error": f"Unknown method: {method}"}
            
            # Send response
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
