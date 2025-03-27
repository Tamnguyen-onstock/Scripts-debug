import json
import time
import logging
from typing import Dict, Any

from app.services.llm import llm
from app.services.cache import query_cache
from prompts.intent.intent_analysis import intent_prompt_template, INTENT_ANALYSIS
from prompts.intent.information_extraction import info_prompt_template, INFORMATION_EXTRACTION

# Initialize logger
logger = logging.getLogger("mcp_server")

def perform_intent_analysis(query: str) -> Dict[str, Any]:
    """Analyze user intent."""
    tool_name = "analyze_intent"
    
    # Check cache first
    cached_result = query_cache.get(tool_name, query)
    if cached_result is not None:
        logger.info(f"Using cached result for intent analysis: {query}")
        return cached_result
    
    logger.info(f"Cache miss, performing intent analysis for: {query}")
    analysis_start_time = time.time()
    
    try:
        system_prompt = INTENT_ANALYSIS
        user_prompt = intent_prompt_template.format(query=query)
        
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        response_text = response.content
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from intent analysis response, retrying with simplified prompt")
            
            # Retry with a more explicit prompt for JSON formatting
            retry_prompt = f"""
            Phân tích câu hỏi về tài chính và trả về CHÍNH XÁC định dạng JSON sau:

            Câu hỏi: {query}

            {{
                "is_finance_related": true/false,
                "needs_clarification": true/false,
                "main_intent": "Mô tả ngắn gọn",
                "stock_codes": [],
                "company_names": [],
                "financial_metrics": [],
                "time_frame": [],
                "required_analysis": [],
                "question_type": ""
            }}
            CHÚ Ý: Chỉ trả về JSON thuần túy, không có văn bản khác.
            """
            
            retry_response = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": retry_prompt}
            ])
            
            result = json.loads(retry_response.content)
        
        # Cache the result
        query_cache.set(tool_name, query, result)
        
        analysis_time = time.time() - analysis_start_time
        logger.info(f"Intent analysis completed in {analysis_time:.2f} seconds")
        
        return result
    except Exception as e:
        logger.error(f"Error in intent analysis: {str(e)}")
        analysis_time = time.time() - analysis_start_time
        logger.error(f"Analysis failed after {analysis_time:.2f} seconds")
        
        # Return default result in case of error
        default_result = {
            "is_finance_related": False,
            "needs_clarification": True,
            "main_intent": f"Error analyzing intent: {str(e)}",
            "required_analysis": [],
            "question_type": "SIMPLE",
            "stock_codes": []
        }
        
        return default_result

def perform_information_extraction(query: str) -> Dict[str, Any]:
    """Extract information from user query."""
    tool_name = "extract_information"
    
    # Check cache first
    cached_result = query_cache.get(tool_name, query)
    if cached_result is not None:
        logger.info(f"Using cached result for information extraction: {query}")
        return cached_result
    
    logger.info(f"Cache miss, performing information extraction for: {query}")
    extraction_start_time = time.time()
    
    try:
        system_prompt = INFORMATION_EXTRACTION
        user_prompt = info_prompt_template.format(query=query)
        
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        response_text = response.content
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from information extraction response, retrying")
            
            # Retry with a more explicit prompt
            retry_response = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            result = json.loads(retry_response.content)
        
        # Cache the result
        query_cache.set(tool_name, query, result)
        
        extraction_time = time.time() - extraction_start_time
        logger.info(f"Information extraction completed in {extraction_time:.2f} seconds")
        
        return result
    except Exception as e:
        logger.error(f"Error in information extraction: {str(e)}")
        extraction_time = time.time() - extraction_start_time
        logger.error(f"Extraction failed after {extraction_time:.2f} seconds")
        
        # Return default result in case of error
        default_result = {
            "stock_codes": [],
            "company_names": [],
            "financial_metrics": [],
            "quarter": [],
            "year": [],
            "search_live_query": [],
            "search_rag_query": [],
            "search_news_query": []
        }
        
        return default_result
