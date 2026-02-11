"""
LLM Parser Utility - Robust JSON extraction and parsing from LLM responses.
"""

import json
import re
from typing import Any, Dict, List, Optional, Type
from utils.logger import get_logger

logger = get_logger(__name__)

def safe_parse_json(text: str, expected_type: Type = list) -> Any:
    """
    Safely extract and parse JSON from LLM response text.
    
    Handles:
    1. Markdown code blocks (```json ... ``` or ``` ... ```)
    2. Conversational text before/after JSON
    3. Truncated JSON (missing closing brackets) - Basic attempt
    4. Common encoding issues
    
    Args:
        text: Raw text from LLM
        expected_type: Expected Python type (list or dict)
        
    Returns:
        Parsed JSON object or empty instance of expected_type on failure
    """
    if not text:
        logger.warning("⚠️ Received empty text for JSON parsing")
        return expected_type()

    # Handle list of parts if Gemini returns multiple
    if isinstance(text, list):
        text = "".join([str(item) for item in text])

    # 1. Try to extract from markdown blocks
    json_str = ""
    
    # Try ```json first
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Try any generic code block
        json_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Maybe there are no backticks, look for the first [ or {
            start_idx = -1
            if expected_type == list:
                start_idx = text.find('[')
            elif expected_type == dict:
                start_idx = text.find('{')
            else:
                # Try both
                start_list = text.find('[')
                start_dict = text.find('{')
                if start_list != -1 and (start_dict == -1 or start_list < start_dict):
                    start_idx = start_list
                else:
                    start_idx = start_dict
            
            if start_idx != -1:
                # Basic heuristic: find last bracket
                end_idx = -1
                if expected_type == list:
                    end_idx = text.rfind(']')
                elif expected_type == dict:
                    end_idx = text.rfind('}')
                else:
                    end_idx = max(text.rfind(']'), text.rfind('}'))
                
                if end_idx != -1 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx+1].strip()
                else:
                    # Truncated? Just take from start_idx to end
                    json_str = text[start_idx:].strip()
            else:
                json_str = text.strip()

    if not json_str:
        logger.error("❌ Could not locate JSON structure in response")
        return expected_type()

    # 2. Basic cleanup for common issues
    # Remove common conversational prefixes if they slipped in
    # (e.g. "Here is the JSON: [ ... ]")
    
    # 3. Attempt parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ Initial JSON parse failed: {str(e)}")
        
        # 4. Attempt to fix truncated JSON (very basic)
        if expected_type == list:
            if not json_str.endswith(']'):
                # Try adding closing brackets
                # This is risky but often works for truncated lists of dicts
                try:
                    # If it ends in a comma, remove it
                    temp_str = json_str.rstrip().rstrip(',')
                    # Count open vs closed braces for the last item
                    open_braces = temp_str.count('{')
                    close_braces = temp_str.count('}')
                    if open_braces > close_braces:
                        temp_str += '}' * (open_braces - close_braces)
                    
                    temp_str += ']'
                    return json.loads(temp_str)
                except:
                    pass
        elif expected_type == dict:
            if not json_str.endswith('}'):
                try:
                    temp_str = json_str.rstrip().rstrip(',')
                    open_braces = temp_str.count('{')
                    close_braces = temp_str.count('}')
                    if open_braces > close_braces:
                        temp_str += '}' * (open_braces - close_braces)
                    return json.loads(temp_str)
                except:
                    pass

        logger.error(f"❌ Failed to parse JSON even after cleanup attempts")
        logger.error(f"Malformed JSON string: {json_str[:500]}...")
        return expected_type()
