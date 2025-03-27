import uvicorn
from app.api.routes import app
from app.core.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

if __name__ == "__main__":
    logger.info(f"Starting MCP Intent Server on port {settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)