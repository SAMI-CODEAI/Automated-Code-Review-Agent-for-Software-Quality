"""
Radon Code Complexity Analyzer Tool Wrapper
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class RadonAnalyzer:
    """
    Wrapper for Radon code complexity analyzer.
    
    Radon computes various code metrics including:
    - Cyclomatic Complexity (CC)
    - Maintainability Index (MI)
    - Raw metrics (LOC, SLOC, comments, etc.)
    """
    
    # Complexity grades: A (best) to F (worst)
    COMPLEXITY_GRADES = ['A', 'B', 'C', 'D', 'E', 'F']
    
    # Complexity thresholds
    CC_THRESHOLDS = {
        'A': (1, 5),      # Simple
        'B': (6, 10),     # Well structured
        'C': (11, 20),    # Slightly complex
        'D': (21, 30),    # More complex
        'E': (31, 40),    # Too complex
        'F': (41, float('inf'))  # Way too complex
    }
    
    def __init__(self):
        """Initialize Radon analyzer."""
        self._verify_installation()
    
    def _verify_installation(self):
        """Verify Radon is installed."""
        try:
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'radon', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"📊 Radon version: {result.stdout.strip()}")
            else:
                logger.warning("⚠️ Radon not found. Complexity analysis will be limited.")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"⚠️ Radon verification failed: {str(e)}")
    
    def analyze_complexity(
        self,
        target_path: Union[str, Path],
        min_grade: str = 'C'
    ) -> Dict:
        """
        Analyze cyclomatic complexity.
        
        Args:
            target_path: Path to file or directory
            min_grade: Minimum grade to report (A-F)
            
        Returns:
            Dictionary with complexity results
        """
        target = Path(target_path)
        
        if not target.exists():
            return {
                'success': False,
                'error': 'Path not found',
                'results': []
            }
        
        try:
            logger.info(f"📊 Analyzing complexity: {target}")
            
            # Run radon cc (cyclomatic complexity)
            # Run radon cc (cyclomatic complexity)
            import sys
            cmd = [
                sys.executable, '-m', 'radon', 'cc',
                '-j',  # JSON output
                '-n', min_grade,  # Minimum grade
                '-s',  # Show complexity score
                str(target)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = self._parse_complexity_output(data)
                    
                    # Count by grade
                    grade_counts = {grade: 0 for grade in self.COMPLEXITY_GRADES}
                    for issue in issues:
                        grade_counts[issue['grade']] += 1
                    
                    logger.info(f"✅ Complexity analysis complete: {len(issues)} complex functions")
                    
                    return {
                        'success': True,
                        'results': issues,
                        'total_issues': len(issues),
                        'grade_counts': grade_counts,
                        'target': str(target)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse Radon output: {str(e)}")
                    return {
                        'success': False,
                        'error': f'JSON parse error: {str(e)}',
                        'results': []
                    }
            else:
                logger.info("✅ Complexity analysis complete: No issues above threshold")
                return {
                    'success': True,
                    'results': [],
                    'total_issues': 0,
                    'grade_counts': {grade: 0 for grade in self.COMPLEXITY_GRADES},
                    'target': str(target)
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Radon analysis timeout for {target}")
            return {
                'success': False,
                'error': 'Analysis timeout',
                'results': []
            }
        except FileNotFoundError:
            logger.error("❌ Radon not installed")
            return {
                'success': False,
                'error': 'Radon not installed',
                'results': []
            }
        except Exception as e:
            logger.error(f"❌ Radon analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def analyze_maintainability(
        self,
        target_path: Union[str, Path],
        min_score: int = 10
    ) -> Dict:
        """
        Analyze maintainability index.
        
        MI score ranges from 0 to 100:
        - 100-20: Highly maintainable
        - 19-10: Moderately maintainable
        - 9-0: Difficult to maintain
        
        Args:
            target_path: Path to file or directory
            min_score: Minimum score threshold (report below this)
            
        Returns:
            Dictionary with maintainability results
        """
        target = Path(target_path)
        
        if not target.exists():
            return {
                'success': False,
                'error': 'Path not found',
                'results': []
            }
        
        try:
            logger.info(f"📊 Analyzing maintainability: {target}")
            
            # Run radon mi (maintainability index)
            # Run radon mi (maintainability index)
            import sys
            cmd = [
                sys.executable, '-m', 'radon', 'mi',
                '-j',  # JSON output
                '-n', str(min_score),  # Minimum score
                str(target)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = self._parse_maintainability_output(data, min_score)
                    
                    logger.info(f"✅ Maintainability analysis complete: {len(issues)} files below threshold")
                    
                    return {
                        'success': True,
                        'results': issues,
                        'total_issues': len(issues),
                        'target': str(target)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse Radon output: {str(e)}")
                    return {
                        'success': False,
                        'error': f'JSON parse error: {str(e)}',
                        'results': []
                    }
            else:
                logger.info("✅ Maintainability analysis complete: All files above threshold")
                return {
                    'success': True,
                    'results': [],
                    'total_issues': 0,
                    'target': str(target)
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Radon analysis timeout for {target}")
            return {
                'success': False,
                'error': 'Analysis timeout',
                'results': []
            }
        except Exception as e:
            logger.error(f"❌ Radon analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def _parse_complexity_output(self, data: Dict) -> List[Dict]:
        """Parse cyclomatic complexity output."""
        issues = []
        
        for file_path, functions in data.items():
            for func in functions:
                issue = {
                    'file': file_path,
                    'function': func.get('name', ''),
                    'type': func.get('type', ''),  # function, method, class
                    'line': func.get('lineno', 0),
                    'complexity': func.get('complexity', 0),
                    'grade': func.get('rank', 'F'),
                    'description': self._get_complexity_description(
                        func.get('complexity', 0),
                        func.get('rank', 'F')
                    )
                }
                issues.append(issue)
        
        # Sort by complexity (highest first)
        issues.sort(key=lambda x: x['complexity'], reverse=True)
        
        return issues
    
    def _parse_maintainability_output(self, data: Dict, min_score: int) -> List[Dict]:
        """Parse maintainability index output."""
        issues = []
        
        for file_path, mi_data in data.items():
            score = mi_data.get('mi', 100)
            rank = mi_data.get('rank', 'A')
            
            # Only include if below threshold
            if score < min_score:
                issue = {
                    'file': file_path,
                    'mi_score': score,
                    'rank': rank,
                    'description': self._get_maintainability_description(score, rank)
                }
                issues.append(issue)
        
        # Sort by score (lowest first)
        issues.sort(key=lambda x: x['mi_score'])
        
        return issues
    
    def _get_complexity_description(self, complexity: int, grade: str) -> str:
        """Get human-readable complexity description."""
        descriptions = {
            'A': 'Simple and well-structured',
            'B': 'Acceptable complexity',
            'C': 'Slightly complex, consider refactoring',
            'D': 'Complex, refactoring recommended',
            'E': 'Very complex, refactoring needed',
            'F': 'Extremely complex, high maintenance risk'
        }
        return f"{descriptions.get(grade, 'Unknown')} (CC: {complexity})"
    
    def _get_maintainability_description(self, score: float, rank: str) -> str:
        """Get human-readable maintainability description."""
        if score >= 20:
            level = "Highly maintainable"
        elif score >= 10:
            level = "Moderately maintainable"
        else:
            level = "Difficult to maintain"
        
        return f"{level} (MI: {score:.2f}, Rank: {rank})"


def run_radon_analysis(
    target_path: Union[str, Path],
    analyze_complexity: bool = True,
    analyze_maintainability: bool = True,
    min_complexity_grade: str = 'C',
    min_maintainability_score: int = 10
) -> Dict:
    """
    Run Radon code analysis.
    
    Args:
        target_path: Path to file or directory
        analyze_complexity: Run complexity analysis
        analyze_maintainability: Run maintainability analysis
        min_complexity_grade: Minimum complexity grade to report
        min_maintainability_score: Minimum MI score threshold
        
    Returns:
        Combined analysis results
    """
    analyzer = RadonAnalyzer()
    results = {
        'success': True,
        'complexity': None,
        'maintainability': None
    }
    
    if analyze_complexity:
        results['complexity'] = analyzer.analyze_complexity(
            target_path,
            min_complexity_grade
        )
        if not results['complexity']['success']:
            results['success'] = False
    
    if analyze_maintainability:
        results['maintainability'] = analyzer.analyze_maintainability(
            target_path,
            min_maintainability_score
        )
        if not results['maintainability']['success']:
            results['success'] = False
    
    return results
