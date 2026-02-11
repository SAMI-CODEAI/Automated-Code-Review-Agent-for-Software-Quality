"""
Style Agent - Code Style and Quality Analysis with Gemini AI
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Union
from utils.llm_factory import create_llm
from utils.llm_parser import safe_parse_json
from langchain_core.messages import SystemMessage, HumanMessage

from tenacity import retry, stop_after_attempt, wait_exponential

from utils.file_scanner import read_file_content
from utils.logger import get_logger

from prompts.style import STYLE_PROMPT

logger = get_logger(__name__)


class StyleAgent:
    """
    AI-powered code style and quality analysis agent.
    
    Uses LLM (Gemini or Ollama) for intelligent code style, readability,
    and maintainability analysis based on Clean Code principles.
    """
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0.1,
        max_tokens: int = 8192
    ):
        """
        Initialize Style Agent.
        
        Args:
            model_name: LLM model name (from env if None)
            temperature: LLM temperature
            max_tokens: Maximum tokens per request
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM using factory
        try:
            self.llm = create_llm(
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            provider = os.getenv('LLM_PROVIDER', 'gemini')
            logger.info(f"✨ Style Agent initialized with {provider} provider")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {str(e)}")
            raise
    
    def analyze_directory(
        self,
        directory_path: Union[str, Path],
        file_list: List[Dict] = None
    ) -> List[Dict]:
        """
        Analyze directory for code style and quality issues.
        
        Args:
            directory_path: Path to directory
            file_list: Optional list of specific files to analyze
            
        Returns:
            List of style findings
        """
        logger.info("✨ Style Agent: Starting code quality analysis")
        
        directory = Path(directory_path)
        findings = []
        
        # Get files to analyze
        if file_list:
            # Filter for code files
            code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go'}
            files_to_analyze = [
                f for f in file_list 
                if Path(f['path']).suffix in code_extensions
            ]
        else:
            # Scan for Python files
            files_to_analyze = [
                {'path': str(f), 'relative_path': str(f.relative_to(directory))}
                for f in directory.rglob('*.py')
                if f.is_file()
            ]
        
        # Limit to prevent token overflow
        max_files = 15
        if len(files_to_analyze) > max_files:
            logger.info(f"📉 Limiting analysis to {max_files} files")
            files_to_analyze = files_to_analyze[:max_files]
        
        # Analyze each file
        for idx, file_info in enumerate(files_to_analyze, 1):
            file_path = file_info['path']
            logger.info(f"✨ Analyzing ({idx}/{len(files_to_analyze)}): {Path(file_path).name}")
            
            try:
                file_findings = self._analyze_file(file_path)
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"❌ Failed to analyze {file_path}: {str(e)}")
                continue
        
        logger.info(f"✅ Style analysis complete: {len(findings)} findings")
        return findings
    
    def _analyze_file(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Analyze a single file for style and quality issues.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of findings for this file
        """
        file_path = Path(file_path)
        
        # Read file content
        content = read_file_content(file_path)
        if not content:
            logger.warning(f"⚠️ Could not read file: {file_path}")
            return []
        
        # Get file extension for language-specific analysis
        file_ext = file_path.suffix
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript/React',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript/React',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go'
        }
        language = language_map.get(file_ext, 'Unknown')
        
        # Create prompt
        user_message = f"""Analyze this {language} file for code style, quality, and maintainability issues.

## File Information
- **Path**: {file_path}
- **Language**: {language}
- **Lines of Code**: {len(content.splitlines())}

## Source Code
```{language.lower()}
{content}
```

## Instructions
Apply Clean Code principles and SOLID design patterns:

1. **Naming Conventions**: Check variable, function, class names
2. **Function Size**: Identify overly long functions (>50 lines)
3. **Code Complexity**: Look for deeply nested logic
4. **Documentation**: Missing or inadequate docstrings/comments
5. **DRY Violations**: Code duplication
6. **Error Handling**: Improper exception handling
7. **Type Hints**: Missing type annotations (for Python)
8. **Magic Numbers**: Hardcoded values that should be constants
9. **Dead Code**: Unused imports, variables, functions
10. **SOLID Principles**: Single responsibility, proper abstraction

Focus on issues that impact:
- Readability
- Maintainability  
- Team collaboration
- Future refactoring ease

Return your findings as a valid JSON array:
```json
[
  {{
    "file": "{file_path}",
    "line": <line_number or null>,
    "issue_type": "descriptive_type",
    "description": "clear description",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "recommendation": "specific improvement with refactored code example",
    "principle_violated": "principle name or null",
    "impact_on_maintainability": "description"
  }}
]
```

If no significant issues found, return an empty array: []
Be constructive and educational in your recommendations.
"""
        
        try:
            # Call Gemini
            messages = [
                SystemMessage(content=STYLE_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self._get_llm_response(messages)
            
            # Parse response
            findings = self._parse_llm_response(response, str(file_path))
            
            logger.info(f"   Found {len(findings)} style issues")
            return findings
            
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for {file_path}: {str(e)}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _get_llm_response(self, messages: List) -> str:
        """Get response from LLM with retries."""
        response = self.llm.invoke(messages)
        return response.content
    
    def _parse_llm_response(self, response: Union[str, list], file_path: str) -> List[Dict]:
        """Parse LLM JSON response into structured findings."""
        # Parse JSON using robust parser
        findings = safe_parse_json(response, expected_type=list)
        
        # Validate structure
        if not isinstance(findings, list):
            logger.warning("⚠️ LLM returned non-list response, wrapping in list")
            findings = [findings] if findings else []
        
        # Ensure required fields
        validated_findings = []
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            
            # Add defaults for missing fields
            validated_finding = {
                'file': finding.get('file', file_path),
                'line': finding.get('line'),
                'issue_type': finding.get('issue_type', 'STYLE_ISSUE'),
                'description': finding.get('description', ''),
                'severity': finding.get('severity', 'MEDIUM'),
                'recommendation': finding.get('recommendation', ''),
                'principle_violated': finding.get('principle_violated'),
                'impact_on_maintainability': finding.get('impact_on_maintainability', '')
            }
            validated_findings.append(validated_finding)
        
        return validated_findings


def create_style_agent_node():
    """Create style analysis node function for LangGraph."""
    def style_node(state: Dict) -> Dict:
        """Style analysis node for LangGraph workflow."""
        logger.info("✨ Style Node: Starting AI-powered analysis")
        
        # Check for errors
        if state.get('error'):
            logger.warning("⚠️ Style Node: Skipping due to previous error")
            return {'style_findings': []}
        
        # Get working directory
        working_dir = state.get('working_directory')
        if not working_dir:
            logger.error("❌ Style Node: No working directory in state")
            return {'style_findings': []}
        
        # Get file list
        file_tree = state.get('file_tree', {})
        file_list = file_tree.get('files', [])
        
        if not file_list:
            logger.warning("⚠️ Style Node: No files to analyze")
            return {'style_findings': []}
        
        try:
            # Create and run agent
            agent = StyleAgent()
            findings = agent.analyze_directory(working_dir, file_list)
            
            logger.info(f"✨ Style Node: Completed with {len(findings)} findings")
            
            return {
                'style_findings': findings
            }
            
        except Exception as e:
            logger.error(f"❌ Style Node failed: {str(e)}", exc_info=True)
            warning_msg = f"Style analysis failed: {str(e)}"
            warnings = state.get('warnings', [])
            warnings.append(warning_msg)
            
            return {
                'style_findings': [],
                'warnings': warnings
            }
    
    return style_node
