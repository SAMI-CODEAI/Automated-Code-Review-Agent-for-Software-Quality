"""
Aggregator Agent - Final Report Compilation
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class AggregatorAgent:
    """
    Aggregates findings from all analysis agents and generates
    a comprehensive code review report in markdown format.
    """
    
    def __init__(self):
        """Initialize Aggregator Agent."""
        logger.info("📋 Aggregator Agent initialized")
    
    def generate_report(
        self,
        state: Dict,
        output_dir: Union[str, Path]
    ) -> tuple[str, str]:
        """
        Generate comprehensive code review report.
        
        Args:
            state: ReviewState with all findings
            output_dir: Directory to save report
            
        Returns:
            Tuple of (report_content, report_path)
        """
        logger.info("📋 Generating comprehensive code review report")
        
        # Extract data from state
        input_path = state.get('input_path', 'Unknown')
        source_type = state.get('source_type', 'unknown')
        total_files = state.get('total_files', 0)
        file_tree = state.get('file_tree', {})
        
        security_findings = state.get('security_findings', [])
        performance_findings = state.get('performance_findings', [])
        style_findings = state.get('style_findings', [])
        warnings = state.get('warnings', [])
        
        # Build report sections
        sections = []
        
        # Header
        sections.append(self._generate_header(input_path, source_type))
        
        # Executive Summary
        sections.append(self._generate_executive_summary(
            total_files,
            security_findings,
            performance_findings,
            style_findings,
            file_tree
        ))
        
        # Critical Issues Alert
        critical_section = self._generate_critical_issues(
            security_findings,
            performance_findings
        )
        if critical_section:
            sections.append(critical_section)
        
        # Security Findings
        if security_findings:
            sections.append(self._generate_security_section(security_findings))
        
        # Performance Findings
        if performance_findings:
            sections.append(self._generate_performance_section(performance_findings))
        
        # Style & Quality Findings
        if style_findings:
            sections.append(self._generate_style_section(style_findings))
        
        # Recommendations
        sections.append(self._generate_recommendations(
            security_findings,
            performance_findings,
            style_findings
        ))
        
        # Warnings
        if warnings:
            sections.append(self._generate_warnings_section(warnings))
        
        # Footer
        sections.append(self._generate_footer())
        
        # Combine all sections
        report_content = "\n\n".join(sections)
        
        # Save report
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"REVIEW_REPORT_{timestamp}.md"
        report_path = output_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"✅ Report saved to: {report_path}")
        
        return report_content, str(report_path)
    
    def _generate_header(self, input_path: str, source_type: str) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# 🔍 Automated Code Review Report

**Generated**: {timestamp}  
**Source**: {input_path}  
**Type**: {source_type.title()}  
**Analyzer**: Multi-Agent AI Code Review System

---
"""
    
    def _generate_executive_summary(
        self,
        total_files: int,
        security_findings: List[Dict],
        performance_findings: List[Dict],
        style_findings: List[Dict],
        file_tree: Dict
    ) -> str:
        """Generate executive summary."""
        # Count by severity
        security_critical = len([f for f in security_findings if f.get('severity') == 'CRITICAL'])
        security_high = len([f for f in security_findings if f.get('severity') == 'HIGH'])
        security_medium = len([f for f in security_findings if f.get('severity') == 'MEDIUM'])
        security_low = len([f for f in security_findings if f.get('severity') == 'LOW'])
        
        perf_critical = len([f for f in performance_findings if f.get('impact') == 'CRITICAL'])
        perf_high = len([f for f in performance_findings if f.get('impact') == 'HIGH'])
        
        total_issues = len(security_findings) + len(performance_findings) + len(style_findings)
        total_critical = security_critical + perf_critical
        
        # File statistics
        total_size_mb = file_tree.get('total_size_mb', 0)
        extensions = file_tree.get('extensions', {})
        
        # Health score (simple calculation)
        health_score = max(0, 100 - (total_critical * 10) - (security_high * 5) - (perf_high * 3))
        
        if health_score >= 90:
            health_label = "🟢 Excellent"
        elif health_score >= 75:
            health_label = "🟡 Good"
        elif health_score >= 50:
            health_label = "🟠 Fair"
        else:
            health_label = "🔴 Needs Attention"
        
        return f"""## 📊 Executive Summary

### Code Health Score: {health_score}/100 {health_label}

### Statistics
- **Files Analyzed**: {total_files}
- **Total Code Size**: {total_size_mb:.2f} MB
- **Total Issues Found**: {total_issues}
- **Critical Issues**: {total_critical}

### Findings Breakdown

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| 🔒 **Security** | {security_critical} | {security_high} | {security_medium} | {security_low} | {len(security_findings)} |
| ⚡ **Performance** | {perf_critical} | {perf_high} | - | - | {len(performance_findings)} |
| ✨ **Style & Quality** | - | - | - | - | {len(style_findings)} |

### File Type Distribution
{self._format_extension_distribution(extensions)}
"""
    
    def _format_extension_distribution(self, extensions: Dict[str, int]) -> str:
        """Format extension distribution."""
        if not extensions:
            return "No extension data available"
        
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
        lines = []
        for ext, count in sorted_exts:
            lines.append(f"- **{ext}**: {count} files")
        
        return "\n".join(lines)
    
    def _generate_critical_issues(
        self,
        security_findings: List[Dict],
        performance_findings: List[Dict]
    ) -> str:
        """Generate critical issues alert section."""
        critical_security = [f for f in security_findings if f.get('severity') in ['CRITICAL', 'HIGH']]
        critical_performance = [f for f in performance_findings if f.get('impact') in ['CRITICAL', 'HIGH']]
        
        if not critical_security and not critical_performance:
            return ""
        
        section = """## 🚨 Critical Issues Requiring Immediate Attention

> **Action Required**: The following issues should be addressed as soon as possible.

"""
        
        if critical_security:
            section += "### 🔒 Security\n\n"
            for finding in critical_security[:5]:  # Top 5
                section += f"- **{finding.get('issue_type', 'Unknown')}** in `{Path(finding.get('file', '')).name}`\n"
                section += f"  - Severity: {finding.get('severity')}\n"
                section += f"  - {finding.get('description', 'No description')}\n\n"
        
        if critical_performance:
            section += "### ⚡ Performance\n\n"
            for finding in critical_performance[:5]:  # Top 5
                section += f"- **{finding.get('issue_type', 'Unknown')}** in `{Path(finding.get('file', '')).name}`\n"
                section += f"  - Impact: {finding.get('impact')}\n"
                section += f"  - {finding.get('description', 'No description')}\n\n"
        
        return section
    
    def _generate_security_section(self, findings: List[Dict]) -> str:
        """Generate detailed security findings section."""
        section = """## 🔒 Security Analysis

### Overview
Security analysis performed using Bandit static analyzer enhanced with AI-powered expert review.

"""
        
        # Group by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            by_severity.setdefault(severity, []).append(finding)
        
        # Generate subsections for each severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity not in by_severity:
                continue
            
            items = by_severity[severity]
            section += f"\n### {severity} Severity ({len(items)} issues)\n\n"
            
            for idx, finding in enumerate(items, 1):
                file_name = Path(finding.get('file', '')).name
                line = finding.get('line', 'N/A')
                issue_type = finding.get('issue_type', 'Unknown')
                description = finding.get('description', 'No description')
                recommendation = finding.get('recommendation', 'No recommendation')
                
                section += f"#### {idx}. {issue_type}\n"
                section += f"- **File**: `{file_name}` (Line {line})\n"
                section += f"- **Description**: {description}\n"
                section += f"- **Recommendation**: {recommendation}\n\n"
        
        return section
    
    def _generate_performance_section(self, findings: List[Dict]) -> str:
        """Generate detailed performance findings section."""
        section = """## ⚡ Performance Analysis

### Overview
Performance analysis performed using Radon complexity analyzer enhanced with AI-powered optimization recommendations.

"""
        
        # Group by impact
        by_impact = {}
        for finding in findings:
            impact = finding.get('impact', 'UNKNOWN')
            by_impact.setdefault(impact, []).append(finding)
        
        # Generate subsections for each impact level
        for impact in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if impact not in by_impact:
                continue
            
            items = by_impact[impact]
            section += f"\n### {impact} Impact ({len(items)} issues)\n\n"
            
            for idx, finding in enumerate(items, 1):
                file_name = Path(finding.get('file', '')).name
                line = finding.get('line', 'N/A')
                issue_type = finding.get('issue_type', 'Unknown')
                description = finding.get('description', 'No description')
                recommendation = finding.get('recommendation', 'No recommendation')
                current_complexity = finding.get('current_complexity', 'N/A')
                optimized_complexity = finding.get('optimized_complexity', 'N/A')
                
                section += f"#### {idx}. {issue_type}\n"
                section += f"- **File**: `{file_name}` (Line {line})\n"
                section += f"- **Description**: {description}\n"
                if current_complexity != 'N/A':
                    section += f"- **Current Complexity**: {current_complexity}\n"
                if optimized_complexity != 'N/A':
                    section += f"- **Optimized Complexity**: {optimized_complexity}\n"
                section += f"- **Recommendation**: {recommendation}\n\n"
        
        return section
    
    def _generate_style_section(self, findings: List[Dict]) -> str:
        """Generate detailed style & quality findings section."""
        section = """## ✨ Code Style & Quality Analysis

### Overview
Code quality analysis based on Clean Code principles, SOLID design patterns, and language-specific best practices.

"""
        
        # Group by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'MEDIUM')
            by_severity.setdefault(severity, []).append(finding)
        
        # Generate subsections
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if severity not in by_severity:
                continue
            
            items = by_severity[severity]
            section += f"\n### {severity} Priority ({len(items)} issues)\n\n"
            
            for idx, finding in enumerate(items, 1):
                file_name = Path(finding.get('file', '')).name
                line = finding.get('line', 'N/A')
                issue_type = finding.get('issue_type', 'Unknown')
                description = finding.get('description', 'No description')
                recommendation = finding.get('recommendation', 'No recommendation')
                principle = finding.get('principle_violated', '')
                
                section += f"#### {idx}. {issue_type}\n"
                section += f"- **File**: `{file_name}` (Line {line})\n"
                if principle:
                    section += f"- **Principle Violated**: {principle}\n"
                section += f"- **Description**: {description}\n"
                section += f"- **Recommendation**: {recommendation}\n\n"
        
        return section
    
    def _generate_recommendations(
        self,
        security_findings: List[Dict],
        performance_findings: List[Dict],
        style_findings: List[Dict]
    ) -> str:
        """Generate prioritized recommendations."""
        section = """## 🎯 Prioritized Recommendations

### Immediate Actions (Next 24-48 hours)
"""
        
        # Critical security issues
        critical_security = [f for f in security_findings if f.get('severity') == 'CRITICAL']
        if critical_security:
            section += "\n**Critical Security Vulnerabilities:**\n"
            for finding in critical_security[:3]:
                section += f"- Fix {finding.get('issue_type')} in `{Path(finding.get('file', '')).name}`\n"
        
        # Critical performance issues
        critical_perf = [f for f in performance_findings if f.get('impact') == 'CRITICAL']
        if critical_perf:
            section += "\n**Critical Performance Bottlenecks:**\n"
            for finding in critical_perf[:3]:
                section += f"- Optimize {finding.get('issue_type')} in `{Path(finding.get('file', '')).name}`\n"
        
        section += """

### Short-term (Week 1-2)
- Address all HIGH severity security issues
- Implement caching for frequently accessed data
- Refactor highest-complexity functions (CC > 20)
- Add comprehensive error handling

### Medium-term (Month 1)
- Resolve all MEDIUM security issues
- Optimize database queries (address N+1 patterns)
- Improve code documentation and type hints
- Reduce code duplication (DRY violations)

### Long-term (Quarter 1)
- Comprehensive code review and refactoring
- Performance benchmarking and optimization
- Establish coding standards and CI/CD checks
- Technical debt paydown strategy
"""
        
        return section
    
    def _generate_warnings_section(self, warnings: List[str]) -> str:
        """Generate warnings section."""
        section = """## ⚠️ Analysis Warnings

The following warnings occurred during analysis:

"""
        for warning in warnings:
            section += f"- {warning}\n"
        
        return section
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        return """---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Clean Code Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Python PEP8 Style Guide](https://peps.python.org/pep-0008/)
- [Security Best Practices](https://cheatsheetseries.owasp.org/)

---

**Report Generated by**: Automated Code Review Agent (Multi-Agent AI System)  
**Powered by**: LangGraph + Google Gemini AI  
**Contact**: For questions about this report, consult your development team lead.
"""


def create_aggregator_agent_node():
    """Create aggregator node function for LangGraph."""
    def aggregator_node(state: Dict) -> Dict:
        """Aggregator node for LangGraph workflow."""
        logger.info("📋 Aggregator Node: Starting report compilation")
        
        # Check for errors
        if state.get('error'):
            logger.error(f"❌ Aggregator Node: Cannot generate report due to error: {state['error']}")
            return state
        
        # Get output directory
        output_dir = state.get('output_dir', './code_reviews')
        
        try:
            # Create aggregator and generate report
            aggregator = AggregatorAgent()
            report_content, report_path = aggregator.generate_report(state, output_dir)
            
            logger.info("📋 Aggregator Node: Completed")
            
            return {
                **state,
                'final_report': report_content,
                'report_path': report_path
            }
            
        except Exception as e:
            logger.error(f"❌ Aggregator Node failed: {str(e)}", exc_info=True)
            return {
                **state,
                'error': f"Report generation failed: {str(e)}"
            }
    
    return aggregator_node
