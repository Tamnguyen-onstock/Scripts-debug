import json
from fastapi import FastAPI, Request, HTTPException
import logging
from datetime import datetime

from app.api.models import ErrorResponse
from app.services.intent_analysis import (
    perform_intent_analysis,
    perform_information_extraction
)
from app.core.constants import SERVER_CAPABILITIES, AVAILABLE_TOOLS

# Initialize logger
logger = logging.getLogger("mcp_server")

# Initialize FastAPI app
app = FastAPI(title="Intent Analysis MCP Server")

# Define route handlers for MCP methods - now async
async def handle_initialize(params: dict) -> dict:
    """Handle initialize method."""
    client_capabilities = params.get("capabilities", {})
    logger.info(f"Received client capabilities: {client_capabilities}")
    
    return {
        "capabilities": SERVER_CAPABILITIES
    }

async def handle_tools_list(params: dict) -> dict:
    """Handle tools/list method."""
    cursor = params.get("cursor")
    
    # Simplified, no pagination needed for few tools
    return {
        "tools": AVAILABLE_TOOLS,
        "nextCursor": None  # No next page
    }

async def handle_tools_call(params: dict) -> dict:
    """Handle tools/call method."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name == "analyze_intent":
        query = arguments.get("query")
        
        if not query:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Missing required parameter 'query'"
                    }
                ],
                "isError": True
            }
        
        try:
            # Use asyncio to run CPU-bound task in a separate thread pool
            import asyncio
            result = await asyncio.to_thread(perform_intent_analysis, query)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Đã phân tích ý định cho câu hỏi: {query}"
                    },
                    {
                        "type": "json",
                        "json": result
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Error executing intent analysis: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    elif tool_name == "extract_information":
        query = arguments.get("query")
        
        if not query:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Missing required parameter 'query'"
                    }
                ],
                "isError": True
            }
        
        try:
            # Use asyncio to run CPU-bound task in a separate thread pool
            import asyncio
            result = await asyncio.to_thread(perform_information_extraction, query)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Đã trích xuất thông tin từ câu hỏi: {query}"
                    },
                    {
                        "type": "json",
                        "json": result
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Error executing information extraction: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }

    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: Unknown tool '{tool_name}'"
                }
            ],
            "isError": True
        }

# Main MCP endpoint
@app.post("/")
async def mcp_endpoint(request: Request):
    """Main endpoint handling JSON-RPC requests according to MCP spec."""
    try:
        # Parse JSON request
        request_data = await request.json()
        
        # Validate JSON-RPC request
        if not all(k in request_data for k in ["jsonrpc", "method", "id"]):
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC request")
        
        jsonrpc_version = request_data.get("jsonrpc")
        method = request_data.get("method")
        request_id = request_data.get("id")
        params = request_data.get("params", {})
        
        # Check JSON-RPC version
        if jsonrpc_version != "2.0":
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": request_id}
        
        # Route to appropriate handler
        result = None
        if method == "initialize":
            result = await handle_initialize(params)
        elif method == "tools/list":
            result = await handle_tools_list(params)
        elif method == "tools/call":
            result = await handle_tools_call(params)
        else:
            # Method not supported
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not supported"
                },
                "id": request_id
            }
        
        # Return successful response
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Return error response
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": request_data.get("id") if "request_data" in locals() else None
        }

# Health check route
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}