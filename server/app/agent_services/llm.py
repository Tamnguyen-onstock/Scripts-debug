import logging
from langchain_openai import ChatOpenAI
from app.core.settings import settings

# Initialize logger
logger = logging.getLogger("mcp_server")

def get_llm():
    """Create and return a language model."""
    # Prioritize Bedrock if available
    if settings.BEDROCK_REGION:
        try:
            from langchain_aws import ChatBedrockConverse
            import boto3
            
            bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=settings.BEDROCK_REGION
            )
            
            logger.info(f"Initializing AWS Bedrock model: {settings.BEDROCK_MODEL_ID}")
            
            return ChatBedrockConverse(
                client=bedrock_client,
                model=settings.BEDROCK_MODEL_ID,
                temperature=0
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model, falling back to OpenAI: {str(e)}")
    
    # Fallback to OpenAI
    try:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        logger.info(f"Initializing OpenAI model: {settings.OPENAI_MODEL}")
        
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI model: {str(e)}")
        raise

# Initialize LLM
try:
    llm = get_llm()
    logger.info("Successfully initialized LLM model")
except Exception as e:
    logger.error(f"Failed to initialize LLM model: {str(e)}")
    llm = None