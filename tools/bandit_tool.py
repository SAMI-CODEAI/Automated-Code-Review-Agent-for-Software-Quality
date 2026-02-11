"""
Bandit Security Scanner Tool Wrapper
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class BanditScanner:
    """
    Wrapper for Bandit security vulnerability scanner.
    
    Bandit finds common security issues in Python code.
    """
    
    SEVERITY_LEVELS = ['LOW', 'MEDIUM', 'HIGH']
    CONFIDENCE_LEVELS = ['LOW', 'MEDIUM', 'HIGH']
    
    def __init__(self):
        """Initialize Bandit scanner."""
        self._verify_installation()
    
    def _verify_installation(self):
        """Verify Bandit is installed."""
        try:
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'bandit', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"🔒 Bandit version: {result.stdout.strip()}")
            else:
                logger.warning("⚠️ Bandit not found. Security scanning will be limited.")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"⚠️ Bandit verification failed: {str(e)}")
    
    def scan_file(
        self,
        file_path: Union[str, Path],
        severity_level: str = 'LOW'
    ) -> Dict:
        """
        Scan a single file for security issues.
        
        Args:
            file_path: Path to Python file
            severity_level: Minimum severity: LOW, MEDIUM, HIGH
            
        Returns:
            Dictionary with scan results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'issues': []
            }
        
        if not file_path.suffix == '.py':
            return {
                'success': True,
                'issues': [],
                'message': 'Not a Python file, skipping Bandit scan'
            }
        
        try:
            # Run Bandit with JSON output
            # Run Bandit with JSON output
            import sys
            cmd = [
                sys.executable, '-m', 'bandit',
                '-f', 'json',
                '-ll',  # Only report issues of given severity level or higher
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Bandit returns non-zero if issues found, but that's expected
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = self._parse_bandit_output(data)
                    
                    return {
                        'success': True,
                        'issues': issues,
                        'total_issues': len(issues),
                        'file': str(file_path)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse Bandit output: {str(e)}")
                    return {
                        'success': False,
                        'error': f'JSON parse error: {str(e)}',
                        'issues': []
                    }
            else:
                # No output usually means no issues
                return {
                    'success': True,
                    'issues': [],
                    'total_issues': 0,
                    'file': str(file_path)
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Bandit scan timeout for {file_path}")
            return {
                'success': False,
                'error': 'Scan timeout',
                'issues': []
            }
        except FileNotFoundError:
            logger.error("❌ Bandit not installed")
            return {
                'success': False,
                'error': 'Bandit not installed',
                'issues': []
            }
        except Exception as e:
            logger.error(f"❌ Bandit scan failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    def scan_directory(
        self,
        directory_path: Union[str, Path],
        severity_level: str = 'LOW',
        recursive: bool = True
    ) -> Dict:
        """
        Scan entire directory for security issues.
        
        Args:
            directory_path: Path to directory
            severity_level: Minimum severity level
            recursive: Scan subdirectories
            
        Returns:
            Dictionary with aggregated scan results
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            return {
                'success': False,
                'error': 'Invalid directory',
                'issues': []
            }
        
        try:
            logger.info(f"🔒 Running Bandit scan on: {directory_path}")
            
            # Run Bandit on entire directory
            # Run Bandit on entire directory
            import sys
            cmd = [
                sys.executable, '-m', 'bandit',
                '-f', 'json',
                '-ll',
                '-r' if recursive else '',
                str(directory_path)
            ]
            
            # Remove empty strings
            cmd = [c for c in cmd if c]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for large repos
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = self._parse_bandit_output(data)
                    
                    # Group by severity
                    severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                    for issue in issues:
                        severity_counts[issue['severity']] += 1
                    
                    logger.info(f"✅ Bandit scan complete: {len(issues)} issues found")
                    logger.info(f"   🔴 High: {severity_counts['HIGH']}")
                    logger.info(f"   🟡 Medium: {severity_counts['MEDIUM']}")
                    logger.info(f"   🟢 Low: {severity_counts['LOW']}")
                    
                    return {
                        'success': True,
                        'issues': issues,
                        'total_issues': len(issues),
                        'severity_counts': severity_counts,
                        'directory': str(directory_path)
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse Bandit output: {str(e)}")
                    return {
                        'success': False,
                        'error': f'JSON parse error: {str(e)}',
                        'issues': []
                    }
            else:
                logger.info("✅ Bandit scan complete: No issues found")
                return {
                    'success': True,
                    'issues': [],
                    'total_issues': 0,
                    'severity_counts': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                    'directory': str(directory_path)
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Bandit scan timeout for {directory_path}")
            return {
                'success': False,
                'error': 'Scan timeout',
                'issues': []
            }
        except Exception as e:
            logger.error(f"❌ Bandit scan failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    def _parse_bandit_output(self, data: Dict) -> List[Dict]:
        """
        Parse Bandit JSON output into standardized format.
        
        Args:
            data: Bandit JSON output
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        
        for result in data.get('results', []):
            issue = {
                'file': result.get('filename', ''),
                'line': result.get('line_number', 0),
                'severity': result.get('issue_severity', 'UNKNOWN'),
                'confidence': result.get('issue_confidence', 'UNKNOWN'),
                'issue_type': result.get('test_id', ''),
                'issue_name': result.get('test_name', ''),
                'description': result.get('issue_text', ''),
                'code': result.get('code', '').strip(),
                'cwe': result.get('issue_cwe', {}).get('id', None),
            }
            issues.append(issue)
        
        return issues


def run_bandit_scan(
    target_path: Union[str, Path],
    severity_level: str = 'LOW'
) -> Dict:
    """
    Run Bandit security scan on a file or directory.
    
    Args:
        target_path: Path to file or directory
        severity_level: Minimum severity level (LOW, MEDIUM, HIGH)
        
    Returns:
        Scan results dictionary
    """
    scanner = BanditScanner()
    target = Path(target_path)
    
    if target.is_file():
        return scanner.scan_file(target, severity_level)
    elif target.is_dir():
        return scanner.scan_directory(target, severity_level)
    else:
        return {
            'success': False,
            'error': 'Invalid path',
            'issues': []
        }
