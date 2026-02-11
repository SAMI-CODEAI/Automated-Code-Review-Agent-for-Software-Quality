"""
Security Agent - Security Vulnerability Analysis with Gemini AI
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Union
from langchain_core.messages import SystemMessage, HumanMessage

from tools.bandit_tool import run_bandit_scan
from utils.file_scanner import read_file_content
from utils.logger import get_logger
from utils.llm_factory import create_llm
from utils.llm_parser import safe_parse_json
from prompts.security import SECURITY_PROMPT

logger = get_logger(__name__)


class SecurityAgent:
    """
    AI-powered security analysis agent.
    
    Combines Bandit static analysis with LLM (Gemini or Ollama) for intelligent
    vulnerability detection and remediation recommendations.
    """
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0.1,
        max_tokens: int = 8192
    ):
        """
        Initialize Security Agent.
        
        Args:
            model_name: LLM model name (from env if None)
            temperature: LLM temperature (lower = more focused)
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
            logger.info(f"🔐 Security Agent initialized with {provider} provider")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {str(e)}")
            raise
    
    def analyze_directory(
        self,
        directory_path: Union[str, Path],
        file_list: List[Dict] = None
    ) -> List[Dict]:
        """
        Analyze directory for security vulnerabilities.
        
        Args:
            directory_path: Path to directory
            file_list: Optional list of specific files to analyze
            
        Returns:
            List of security findings
        """
        logger.info("🔐 Security Agent: Starting security analysis")
        
        directory = Path(directory_path)
        findings = []
        
        # Step 1: Run Bandit scan
        logger.info("🔍 Running Bandit security scan...")
        bandit_results = run_bandit_scan(directory, severity_level='LOW')
        
        if not bandit_results.get('success'):
            logger.warning(f"⚠️ Bandit scan failed: {bandit_results.get('error')}")
            # Continue with LLM-only analysis
            bandit_issues = []
        else:
            bandit_issues = bandit_results.get('issues', [])
            logger.info(f"📊 Bandit found {len(bandit_issues)} potential issues")
        
        # Step 2: Analyze with AI
        # Group files by priority (those with Bandit findings first)
        files_with_issues = {issue['file'] for issue in bandit_issues}
        
        if file_list:
            # Use provided file list
            files_to_analyze = [f for f in file_list if Path(f['path']).suffix == '.py']
        else:
            # Analyze only Python files with issues
            files_to_analyze = [
                {'path': f, 'relative_path': str(Path(f).relative_to(directory))}
                for f in files_with_issues
            ]
        
        # Limit to prevent token overflow
        max_files = 20
        if len(files_to_analyze) > max_files:
            logger.info(f"📉 Limiting analysis to {max_files} highest-priority files")
            # Prioritize files with high-severity Bandit findings
            priority_files = sorted(
                files_to_analyze,
                key=lambda f: len([i for i in bandit_issues if i['file'] == f['path']]),
                reverse=True
            )[:max_files]
            files_to_analyze = priority_files
        
        # Analyze each file
        for idx, file_info in enumerate(files_to_analyze, 1):
            file_path = file_info['path']
            logger.info(f"🔍 Analyzing ({idx}/{len(files_to_analyze)}): {Path(file_path).name}")
            
            try:
                file_findings = self._analyze_file(file_path, bandit_issues)
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"❌ Failed to analyze {file_path}: {str(e)}")
                continue
        
        logger.info(f"✅ Security analysis complete: {len(findings)} findings")
        return findings
    
    def _analyze_file(
        self,
        file_path: Union[str, Path],
        bandit_issues: List[Dict]
    ) -> List[Dict]:
        """
        Analyze a single file for security issues.
        
        Args:
            file_path: Path to file
            bandit_issues: Bandit scan results for context
            
        Returns:
            List of findings for this file
        """
        file_path = Path(file_path)
        
        # Read file content
        content = read_file_content(file_path)
        if not content:
            logger.warning(f"⚠️ Could not read file: {file_path}")
            return []
        
        # Filter Bandit issues for this file
        file_bandit_issues = [
            issue for issue in bandit_issues
            if Path(issue['file']).resolve() == file_path.resolve()
        ]
        
        # Prepare context for LLM
        bandit_context = self._format_bandit_results(file_bandit_issues)
        
        # Create prompt
        user_message = f"""Analyze this Python file for security vulnerabilities.

## File Information
- **Path**: {file_path}
- **Lines of Code**: {len(content.splitlines())}

## Bandit Static Analysis Results
{bandit_context}

## Source Code
```python
{content}
```

## Instructions
1. Review the Bandit findings - validate if they are real vulnerabilities or false positives
2. Identify any additional security issues Bandit might have missed
3. Focus on OWASP Top 10 vulnerabilities
4. Provide specific, actionable recommendations

Return your findings as a valid JSON array:
```json
[
  {{
    "file": "{file_path}",
    "line": <line_number>,
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "confidence": "HIGH|MEDIUM|LOW",
    "issue_type": "descriptive_type",
    "description": "clear description",
    "recommendation": "specific fix with code example",
    "cwe_id": <cwe_number or null>,
    "owasp_category": "category or null"
  }}
]
```

If no issues found, return an empty array: []
"""
        
        try:
            # Call Gemini
            messages = [
                SystemMessage(content=SECURITY_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse response
            findings = self._parse_llm_response(response.content, str(file_path))
            
            logger.info(f"   Found {len(findings)} security issues")
            return findings
            
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for {file_path}: {str(e)}")
            return []
    
    def _format_bandit_results(self, bandit_issues: List[Dict]) -> str:
        """Format Bandit results for LLM context."""
        if not bandit_issues:
            return "No issues detected by Bandit scanner."
        
        formatted = []
        for issue in bandit_issues:
            formatted.append(
                f"- **Line {issue['line']}**: {issue['issue_name']} "
                f"(Severity: {issue['severity']}, Confidence: {issue['confidence']})\n"
                f"  {issue['description']}\n"
                f"  ```python\n  {issue['code']}\n  ```"
            )
        
        return "\n\n".join(formatted)
    
    def _parse_llm_response(self, response: Union[str, list], file_path: str) -> List[Dict]:
        """
        Parse LLM JSON response into structured findings.
        
        Args:
            response: LLM response text or list of content parts
            file_path: File being analyzed
            
        Returns:
            List of parsed findings
        """
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
                'line': finding.get('line', 0),
                'severity': finding.get('severity', 'MEDIUM'),
                'confidence': finding.get('confidence', 'MEDIUM'),
                'issue_type': finding.get('issue_type', 'SECURITY_ISSUE'),
                'description': finding.get('description', ''),
                'recommendation': finding.get('recommendation', ''),
                'cwe_id': finding.get('cwe_id'),
                'owasp_category': finding.get('owasp_category')
            }
            validated_findings.append(validated_finding)
        
        return validated_findings


def create_security_agent_node():
    """
    Create security analysis node function for LangGraph.
    
    Returns:
        Node function that processes ReviewState
    """
    def security_node(state: Dict) -> Dict:
        """Security analysis node for LangGraph workflow."""
        logger.info("🔐 Security Node: Starting AI-powered analysis")
        
        # Check for errors
        if state.get('error'):
            logger.warning("⚠️ Security Node: Skipping due to previous error")
            return {**state, 'security_findings': []}
        
        # Get working directory
        working_dir = state.get('working_directory')
        if not working_dir:
            logger.error("❌ Security Node: No working directory in state")
            return {**state, 'security_findings': []}
        
        # Get file list from ingestion
        file_tree = state.get('file_tree', {})
        file_list = file_tree.get('files', [])
        
        if not file_list:
            logger.warning("⚠️ Security Node: No files to analyze")
            return {**state, 'security_findings': []}
        
        try:
            # Create and run agent
            agent = SecurityAgent()
            findings = agent.analyze_directory(working_dir, file_list)
            
            logger.info(f"🔐 Security Node: Completed with {len(findings)} findings")
            
            return {
                'security_findings': findings
            }
            
        except Exception as e:
            logger.error(f"❌ Security Node failed: {str(e)}", exc_info=True)
            warning_msg = f"Security analysis failed: {str(e)}"
            warnings = state.get('warnings', [])
            warnings.append(warning_msg)
            
            return {
                'security_findings': [],
                'warnings': warnings
            }
    
    return security_node
