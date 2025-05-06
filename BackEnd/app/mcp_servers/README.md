# MCP Servers

This directory contains configuration for Model Context Protocol (MCP) servers. The `mcp.json` file defines different MCP server configurations that can be used with your application.

## Configuration Format

The `mcp.json` file should be placed in this directory with the following structure:

```json
{
    "sequential-thinking": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-sequential-thinking"
        ],
        "transport": "stdio"
    },
    "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp@latest"]
    }
}
```