"""
Performance Agent - Performance Optimization Analysis with Gemini AI
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Union
from utils.llm_factory import create_llm
from utils.llm_parser import safe_parse_json
from langchain_core.messages import SystemMessage, HumanMessage

from tools.radon_tool import run_radon_analysis
from utils.file_scanner import read_file_content
from utils.logger import get_logger
from prompts.performance import PERFORMANCE_PROMPT

logger = get_logger(__name__)


class PerformanceAgent:
    """
    AI-powered performance analysis agent.
    
    Combines Radon complexity analysis with LLM (Gemini or Ollama) for intelligent
    performance optimization recommendations.
    """
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = 0.1,
        max_tokens: int = 8192
    ):
        """
        Initialize Performance Agent.
        
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
            logger.info(f"⚡ Performance Agent initialized with {provider} provider")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {str(e)}")
            raise
    
    def analyze_directory(
        self,
        directory_path: Union[str, Path],
        file_list: List[Dict] = None
    ) -> List[Dict]:
        """
        Analyze directory for performance issues.
        
        Args:
            directory_path: Path to directory
            file_list: Optional list of specific files to analyze
            
        Returns:
            List of performance findings
        """
        logger.info("⚡ Performance Agent: Starting performance analysis")
        
        directory = Path(directory_path)
        findings = []
        
        # Step 1: Run Radon analysis
        logger.info("📊 Running Radon complexity analysis...")
        radon_results = run_radon_analysis(
            directory,
            analyze_complexity=True,
            analyze_maintainability=True,
            min_complexity_grade='C',
            min_maintainability_score=10
        )
        
        if not radon_results.get('success'):
            logger.warning(f"⚠️ Radon analysis failed: {radon_results.get('complexity', {}).get('error')}")
            complexity_issues = []
            maintainability_issues = []
        else:
            complexity_issues = radon_results.get('complexity', {}).get('results', [])
            maintainability_issues = radon_results.get('maintainability', {}).get('results', [])
            
            logger.info(f"📊 Radon found {len(complexity_issues)} complexity issues")
            logger.info(f"📊 Radon found {len(maintainability_issues)} maintainability issues")
        
        # Step 2: Analyze with AI
        # Group files by priority
        files_with_issues = set()
        for issue in complexity_issues:
            files_with_issues.add(issue['file'])
        for issue in maintainability_issues:
            files_with_issues.add(issue['file'])
        
        if file_list:
            # Use provided file list, prioritize Python files
            files_to_analyze = [f for f in file_list if Path(f['path']).suffix == '.py']
        else:
            # Analyze only files with complexity issues
            files_to_analyze = [
                {'path': f, 'relative_path': str(Path(f).relative_to(directory))}
                for f in files_with_issues
            ]
        
        # Limit to prevent token overflow
        max_files = 15
        if len(files_to_analyze) > max_files:
            logger.info(f"📉 Limiting analysis to {max_files} highest-priority files")
            # Prioritize files with high complexity
            priority_files = sorted(
                files_to_analyze,
                key=lambda f: len([i for i in complexity_issues if i['file'] == f['path']]),
                reverse=True
            )[:max_files]
            files_to_analyze = priority_files
        
        # Analyze each file
        for idx, file_info in enumerate(files_to_analyze, 1):
            file_path = file_info['path']
            logger.info(f"⚡ Analyzing ({idx}/{len(files_to_analyze)}): {Path(file_path).name}")
            
            try:
                file_findings = self._analyze_file(
                    file_path,
                    complexity_issues,
                    maintainability_issues
                )
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"❌ Failed to analyze {file_path}: {str(e)}")
                continue
        
        logger.info(f"✅ Performance analysis complete: {len(findings)} findings")
        return findings
    
    def _analyze_file(
        self,
        file_path: Union[str, Path],
        complexity_issues: List[Dict],
        maintainability_issues: List[Dict]
    ) -> List[Dict]:
        """
        Analyze a single file for performance issues.
        
        Args:
            file_path: Path to file
            complexity_issues: Radon complexity results
            maintainability_issues: Radon maintainability results
            
        Returns:
            List of findings for this file
        """
        file_path = Path(file_path)
        
        # Read file content
        content = read_file_content(file_path)
        if not content:
            logger.warning(f"⚠️ Could not read file: {file_path}")
            return []
        
        # Filter Radon issues for this file
        file_complexity = [
            issue for issue in complexity_issues
            if Path(issue['file']).resolve() == file_path.resolve()
        ]
        
        file_maintainability = [
            issue for issue in maintainability_issues
            if Path(issue['file']).resolve() == file_path.resolve()
        ]
        
        # Prepare context for LLM
        radon_context = self._format_radon_results(file_complexity, file_maintainability)
        
        # Create prompt
        user_message = f"""Analyze this Python file for performance issues and optimization opportunities.

## File Information
- **Path**: {file_path}
- **Lines of Code**: {len(content.splitlines())}

## Radon Complexity Analysis Results
{radon_context}

## Source Code
```python
{content}
```

## Instructions
1. Review the Radon complexity metrics - identify functions/methods that need refactoring
2. Look for common performance anti-patterns:
   - N+1 query problems
   - Inefficient loops (O(n²) or worse)
   - Missing caching opportunities
   - Synchronous I/O in hot paths
   - Unnecessary object creation
   - Memory leaks or excessive allocations
3. Analyze algorithm complexity with Big-O notation
4. Suggest concrete optimizations with estimated performance gains

Return your findings as a valid JSON array:
```json
[
  {{
    "file": "{file_path}",
    "line": <line_number or null>,
    "issue_type": "descriptive_type",
    "description": "clear description",
    "complexity_score": <cc_score or null>,
    "impact": "CRITICAL|HIGH|MEDIUM|LOW",
    "current_complexity": "O(n) notation",
    "optimized_complexity": "O(n) notation or null",
    "recommendation": "specific optimization with code example",
    "estimated_improvement": "percentage or description"
  }}
]
```

If no issues found, return an empty array: []
"""
        
        try:
            # Call Gemini
            messages = [
                SystemMessage(content=PERFORMANCE_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse response
            findings = self._parse_llm_response(response.content, str(file_path))
            
            logger.info(f"   Found {len(findings)} performance issues")
            return findings
            
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for {file_path}: {str(e)}")
            return []
    
    def _format_radon_results(
        self,
        complexity_issues: List[Dict],
        maintainability_issues: List[Dict]
    ) -> str:
        """Format Radon results for LLM context."""
        sections = []
        
        if complexity_issues:
            sections.append("### Cyclomatic Complexity Issues")
            for issue in complexity_issues:
                sections.append(
                    f"- **{issue['function']}** (Line {issue['line']}): "
                    f"CC={issue['complexity']}, Grade={issue['grade']}\n"
                    f"  {issue['description']}"
                )
        
        if maintainability_issues:
            sections.append("\n### Maintainability Index Issues")
            for issue in maintainability_issues:
                sections.append(
                    f"- File MI Score: {issue['mi_score']:.2f} (Rank: {issue['rank']})\n"
                    f"  {issue['description']}"
                )
        
        if not sections:
            return "No complexity or maintainability issues detected by Radon."
        
        return "\n\n".join(sections)
    
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
                'issue_type': finding.get('issue_type', 'PERFORMANCE_ISSUE'),
                'description': finding.get('description', ''),
                'complexity_score': finding.get('complexity_score'),
                'impact': finding.get('impact', 'MEDIUM'),
                'current_complexity': finding.get('current_complexity'),
                'optimized_complexity': finding.get('optimized_complexity'),
                'recommendation': finding.get('recommendation', ''),
                'estimated_improvement': finding.get('estimated_improvement')
            }
            validated_findings.append(validated_finding)
        
        return validated_findings


def create_performance_agent_node():
    """Create performance analysis node function for LangGraph."""
    def performance_node(state: Dict) -> Dict:
        """Performance analysis node for LangGraph workflow."""
        logger.info("⚡ Performance Node: Starting AI-powered analysis")
        
        # Check for errors
        if state.get('error'):
            logger.warning("⚠️ Performance Node: Skipping due to previous error")
            return {'performance_findings': []}
        
        # Get working directory
        working_dir = state.get('working_directory')
        if not working_dir:
            logger.error("❌ Performance Node: No working directory in state")
            return {'performance_findings': []}
        
        # Get file list
        file_tree = state.get('file_tree', {})
        file_list = file_tree.get('files', [])
        
        if not file_list:
            logger.warning("⚠️ Performance Node: No files to analyze")
            return {'performance_findings': []}
        
        try:
            # Create and run agent
            agent = PerformanceAgent()
            findings = agent.analyze_directory(working_dir, file_list)
            
            logger.info(f"⚡ Performance Node: Completed with {len(findings)} findings")
            
            return {
                'performance_findings': findings
            }
            
        except Exception as e:
            logger.error(f"❌ Performance Node failed: {str(e)}", exc_info=True)
            warning_msg = f"Performance analysis failed: {str(e)}"
            warnings = state.get('warnings', [])
            warnings.append(warning_msg)
            
            return {
                'performance_findings': [],
                'warnings': warnings
            }
    
    return performance_node
