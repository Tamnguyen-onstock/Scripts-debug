# Stock Market Analysis Chatbot - MCP Server

This project implements a stock market analysis chatbot with multiple specialized agents (intent, live, news, fundamental analysis, technical analysis, RAG, etc.) organized using the Model Context Protocol (MCP).

## Project Structure

```
server/
│
├── app/                        # Main application code
│   ├── api/                    # API definitions and routes
│   │   ├── models.py           # Pydantic models for API
│   │   └── routes.py           # FastAPI routes and MCP handlers
│   │
│   ├── core/                   # Core functionality
│   │   ├── constants.py        # MCP server constants and tool definitions
│   │   └── settings.py         # Application settings
│   │
│   ├── services/               # Service implementations
│   │   ├── agent/              # Agent-specific services
│   │   │   ├── intent.py       # Intent analysis service
│   │   │   ├── live.py         # Real-time market data service
│   │   │   ├── news.py         # News analysis service
│   │   │   ├── ta.py           # Technical analysis service
│   │   │   ├── fa.py           # Fundamental analysis service
│   │   │   └── rag.py          # Retrieval-augmented generation service
│   │   │
│   │   ├── cache.py            # Cache implementation
│   │   └── llm.py              # LLM service implementation
│   │
│   └── utils/                  # Utility functions
│       └── helpers.py          # Helper functions
│
├── prompts/                    # LLM prompts organized by agent
│   ├── intent/                 # Intent analysis prompts
│   ├── live/                   # Real-time market data prompts
│   ├── news/                   # News analysis prompts
│   ├── ta/                     # Technical analysis prompts
│   ├── fa/                     # Fundamental analysis prompts
│   └── rag/                    # RAG prompts
│
├── main.py                     # Application entry point
└── .env                        # Environment variables
```

## Setup and Deployment

### Initial Setup

1. Create and configure the environment:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd <repository-directory>
   
   # Create a virtual environment
   python -m venv .venv
   
   # Activate the virtual environment
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create and configure .env file
   cp .env.example .env
   # Edit .env with your LLM API keys and other settings
   ```

2. Run the server:
   ```bash
   python server/main.py
   ```

### Adding a New Agent Tool

To add a new agent tool (e.g., live market data, news analysis, etc.), follow these steps:

1. **Create prompt templates**:
   ```bash
   # Create directory for new agent's prompts
   mkdir -p server/prompts/new_agent
   
   # Create prompt template files
   touch server/prompts/new_agent/__init__.py
   touch server/prompts/new_agent/main_prompt.py
   ```

2. **Implement the agent service**:
   ```bash
   # Create service file for the new agent
   mkdir -p server/app/services/agent
   touch server/app/services/agent/__init__.py
   touch server/app/services/agent/new_agent.py
   ```

3. **Define the agent service implementation**:
   ```python
   # server/app/services/agent/new_agent.py
   import json
   import time
   import logging
   from typing import Dict, Any
   
   from app.services.llm import llm
   from app.services.cache import query_cache
   from prompts.new_agent.main_prompt import main_prompt_template, MAIN_SYSTEM_PROMPT
   
   # Initialize logger
   logger = logging.getLogger("mcp_server")
   
   def perform_new_agent_analysis(query: str, additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
       """Perform new agent analysis."""
       tool_name = "new_agent_analysis"
       
       # Check cache first
       cache_key = query
       if additional_params:
           cache_key = f"{query}_{json.dumps(additional_params)}"
           
       cached_result = query_cache.get(tool_name, cache_key)
       if cached_result is not None:
           logger.info(f"Using cached result for {tool_name}: {cache_key}")
           return cached_result
       
       logger.info(f"Cache miss, performing {tool_name} for: {cache_key}")
       analysis_start_time = time.time()
       
       try:
           system_prompt = MAIN_SYSTEM_PROMPT
           user_prompt = main_prompt_template.format(query=query, **additional_params or {})
           
           response = llm.invoke([
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_prompt}
           ])
           
           response_text = response.content
           
           try:
               result = json.loads(response_text)
           except json.JSONDecodeError:
               logger.warning(f"Failed to parse JSON from {tool_name} response, retrying with simplified prompt")
               
               # Retry logic
               retry_prompt = f"""
               {query}
               
               Trả về kết quả dưới dạng JSON chính xác:
               {{
                   "key1": "value1",
                   "key2": "value2"
               }}
               CHÚ Ý: Chỉ trả về JSON thuần túy, không có văn bản khác.
               """
               
               retry_response = llm.invoke([
                   {"role": "system", "content": system_prompt},
                   {"role": "user", "content": retry_prompt}
               ])
               
               result = json.loads(retry_response.content)
           
           # Cache the result
           query_cache.set(tool_name, cache_key, result)
           
           analysis_time = time.time() - analysis_start_time
           logger.info(f"{tool_name} completed in {analysis_time:.2f} seconds")
           
           return result
       except Exception as e:
           logger.error(f"Error in {tool_name}: {str(e)}")
           analysis_time = time.time() - analysis_start_time
           logger.error(f"Analysis failed after {analysis_time:.2f} seconds")
           
           # Return default result in case of error
           default_result = {
               "error": f"Error performing {tool_name}: {str(e)}",
               # Add default values for your agent
           }
           
           return default_result
   ```

4. **Update the constants.py file** to include the new tool:
   ```python
   # server/app/core/constants.py
   # Add your new tool to AVAILABLE_TOOLS
   AVAILABLE_TOOLS = [
       # Existing tools...
       {
           "name": "new_agent_analysis",
           "description": "Performs new agent analysis",
           "parameters": {
               "type": "object",
               "properties": {
                   "query": {
                       "type": "string",
                       "description": "Query for analysis"
                   },
                   # Add additional parameters as needed
               },
               "required": ["query"]
           },
           "returns": {
               "type": "object",
               "description": "Analysis results"
           }
       },
   ]
   ```

5. **Update the routes.py file** to handle the new tool:
   ```python
   # server/app/api/routes.py
   # Import your new agent service
   from app.services.agent.new_agent import perform_new_agent_analysis
   
   # Update handle_tools_call function
   async def handle_tools_call(params: dict) -> dict:
       """Handle tools/call method."""
       tool_name = params.get("name")
       arguments = params.get("arguments", {})
       
       # Existing tool handlers...
       
       elif tool_name == "new_agent_analysis":
           query = arguments.get("query")
           additional_params = {k: v for k, v in arguments.items() if k != "query"}
           
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
               result = await asyncio.to_thread(perform_new_agent_analysis, query, additional_params)
               
               return {
                   "content": [
                       {
                           "type": "text",
                           "text": f"Đã phân tích {tool_name} cho câu hỏi: {query}"
                       },
                       {
                           "type": "json",
                           "json": result
                       }
                   ],
                   "isError": False
               }
           except Exception as e:
               logger.error(f"Error executing {tool_name}: {str(e)}")
               return {
                   "content": [
                       {
                           "type": "text",
                           "text": f"Error: {str(e)}"
                       }
                   ],
                   "isError": True
               }
       # ...
   ```

## Testing Your MCP Server

You can test your MCP server using tools like `curl`:

```bash
# Initialize the connection
curl -X POST http://localhost:5002/ -H "Content-Type: application/json" -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {
        "capabilities": {}
    }
}'

# List available tools
curl -X POST http://localhost:5002/ -H "Content-Type: application/json" -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2,
    "params": {}
}'

# Call a tool
curl -X POST http://localhost:5002/ -H "Content-Type: application/json" -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 3,
    "params": {
        "name": "analyze_intent",
        "arguments": {
            "query": "Phân tích VNM có nên mua không?"
        }
    }
}'
```

## Deployment Best Practices

1. **Containerization**: Use Docker to containerize your application
   ```bash
   # Example Dockerfile for your project
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "server/main.py"]
   ```

2. **Environment Variables**: Keep all configuration in environment variables
   ```
   # .env.example
   HOST=0.0.0.0
   PORT=5002
   CACHE_ENABLED=true
   CACHE_TTL=3600
   MAX_CACHE_SIZE=1000
   OPENAI_API_KEY=your-openai-key
   OPENAI_MODEL=gpt-4
   BEDROCK_REGION=us-east-1
   BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

3. **Load Testing**: Test your MCP server under load to ensure it can handle multiple requests
   ```bash
   # Using k6 for load testing
   k6 run --vus 10 --duration 30s loadtest.js
   ```

4. **Monitoring**: Add monitoring to track your server's performance
   ```python
   # Add Prometheus metrics to your FastAPI app
   from prometheus_fastapi_instrumentator import Instrumentator
   
   Instrumentator().instrument(app).expose(app)
   ```

## Troubleshooting

- **JSON Parsing Issues**: If you encounter JSON parsing errors, make sure your prompt explicitly instructs the LLM to return only JSON.
- **Cache Issues**: If caching doesn't work as expected, check the TTL and cache key generation.
- **LLM Response Time**: If the LLM takes too long to respond, consider optimizing prompts or setting timeouts.