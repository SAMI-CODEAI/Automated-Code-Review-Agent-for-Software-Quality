# System Architecture - Automated Code Review Agent

## 🏛️ High-Level Architecture

```mermaid
graph TD
    A[User Input: Path/URL] --> B[CLI main.py]
    B --> C[LangGraph Workflow]
    
    C --> D[Ingestor Agent]
    D --> E{Path Type?}
    E -->|GitHub URL| F[Clone Repository]
    E -->|Local Path| G[Scan Directory]
    
    F --> H[File Tree Extraction]
    G --> H
    
    H --> I[Parallel Agent Execution]
    
    I --> J[Security Agent]
    I --> K[Performance Agent]
    I --> L[Style Agent]
    
    J --> M[Bandit Scan]
    M --> N[Gemini Analysis]
    
    K --> O[Radon Analysis]
    O --> P[Gemini Analysis]
    
    L --> Q[Pylint Check]
    Q --> R[Gemini Analysis]
    
    N --> S[Aggregator Agent]
    P --> S
    R --> S
    
    S --> T[Generate REVIEW_REPORT.md]
    T --> U[Output Directory]
```

## 🔄 LangGraph Workflow Structure

```mermaid
stateDiagram-v2
    [*] --> Ingestor
    
    Ingestor --> SecurityAgent: File tree ready
    Ingestor --> PerformanceAgent: File tree ready
    Ingestor --> StyleAgent: File tree ready
    
    SecurityAgent --> Aggregator: Security findings
    PerformanceAgent --> Aggregator: Performance findings
    StyleAgent --> Aggregator: Style findings
    
    Aggregator --> [*]: Report generated
    
    note right of Ingestor
        Validates input
        Clones/scans files
        Respects .gitignore
    end note
    
    note right of SecurityAgent
        Runs Bandit
        LLM analysis for:
        - SQL Injection
        - XSS
        - Secret leaks
    end note
    
    note right of PerformanceAgent
        Runs Radon
        LLM analysis for:
        - N+1 queries
        - Memory leaks
        - Complexity
    end note
    
    note right of StyleAgent
        Runs Pylint
        LLM analysis for:
        - PEP8 compliance
        - Clean code
        - Best practices
    end note
    
    note right of Aggregator
        Combines findings
        Generates markdown
        Creates final report
    end note
```

## 📊 State Flow Through Agents

### Initial State (After Ingestor)
```python
{
    "input_path": "https://github.com/user/repo",
    "output_dir": "./code_reviews",
    "file_tree": [
        {"path": "main.py", "size": 1024, "type": "file"},
        {"path": "utils/", "size": 0, "type": "directory"},
        ...
    ],
    "total_files": 25,
}
```

### State After Parallel Agents
```python
{
    # ... previous state ...
    "security_findings": [
        {
            "file": "auth.py",
            "severity": "HIGH",
            "issue": "Hardcoded password",
            "line": 42,
            "recommendation": "Use environment variables"
        },
        ...
    ],
    "performance_findings": [
        {
            "file": "db.py",
            "issue": "N+1 query pattern",
            "line": 78,
            "recommendation": "Use select_related()"
        },
        ...
    ],
    "style_findings": [
        {
            "file": "helper.py",
            "issue": "Line too long (120 chars)",
            "line": 15,
            "recommendation": "Break into multiple lines"
        },
        ...
    ],
}
```

### Final State (After Aggregator)
```python
{
    # ... all previous state ...
    "final_report": "# Code Review Report\n\n...",
    "report_path": "./code_reviews/REVIEW_REPORT_2026-01-09.md",
}
```

## 🔧 Agent Implementation Details

### 1. Ingestor Agent
**Responsibilities:**
- Detect if input is URL or local path
- Clone GitHub repos to temp directory
- Scan local directories
- Parse .gitignore patterns
- Filter files by size/type
- Build file tree structure

**Technologies:**
- GitPython for cloning
- pathlib for file operations
- pathspec for .gitignore parsing

### 2. Security Agent
**Responsibilities:**
- Run Bandit security scanner
- Analyze static analysis results with Gemini
- Identify vulnerabilities:
  - SQL injection patterns
  - XSS vulnerabilities
  - Hardcoded secrets
  - Insecure cryptography
  - Authentication issues

**Prompt Strategy:**
- Expert security engineer persona
- Focus on OWASP Top 10
- Provide severity ratings
- Actionable remediation steps

### 3. Performance Agent
**Responsibilities:**
- Run Radon complexity analysis
- Analyze code patterns with Gemini
- Identify issues:
  - High cyclomatic complexity
  - N+1 query patterns
  - Memory leak indicators
  - Inefficient algorithms
  - Resource management

**Prompt Strategy:**
- Performance optimization expert
- Focus on scalability
- Big-O complexity analysis
- Database query optimization

### 4. Style Agent
**Responsibilities:**
- Run Pylint style checker
- Analyze code quality with Gemini
- Check for:
  - PEP8 compliance
  - Naming conventions
  - Code organization
  - Documentation quality
  - Clean code principles

**Prompt Strategy:**
- Clean code advocate persona
- Focus on maintainability
- Best practices enforcement
- Readability improvements

### 5. Aggregator Agent
**Responsibilities:**
- Collect all agent findings
- Organize by severity/category
- Generate structured markdown report
- Create executive summary
- Prioritize recommendations

**Report Sections:**
1. Executive Summary
2. Critical Issues (High severity)
3. Security Findings
4. Performance Findings
5. Style & Quality Findings
6. File-by-File Analysis
7. Recommendations by Priority

## 🛡️ Error Handling Strategy

### API Errors
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_gemini_api(...):
    # API call logic
```

### File Processing Errors
- Skip files exceeding size limit (log warning)
- Handle binary files gracefully
- Catch and log encoding errors
- Continue processing remaining files

### Repository Access Errors
- Validate GitHub URL format
- Handle authentication failures
- Detect network issues
- Provide clear error messages

## 📈 Performance Optimizations

### 1. Parallel Processing
- Security, Performance, and Style agents run concurrently
- Reduces total processing time by ~66%

### 2. File Filtering
- Skip files based on .gitignore
- Filter by extension (focus on code files)
- Size limits prevent memory issues

### 3. Batch Processing
- Process files in batches if needed
- Checkpoint state for recovery
- Stream large outputs

### 4. Caching
- Cache static analysis results
- Reuse file tree structures
- Store temporary results

## 🔐 Security Considerations

### API Key Management
- Never commit .env files
- Use environment variables
- Validate key presence before execution

### Repository Cloning
- Clone to temporary directory
- Clean up after processing
- Validate repository URLs
- Avoid arbitrary code execution

### Output Sanitization
- Sanitize file paths in reports
- Avoid exposing secrets in output
- Validate user inputs

---

## 📝 LangGraph Node Definitions

### Node Function Signatures

```python
def ingestor_node(state: ReviewState) -> ReviewState:
    """Process input path and extract file tree"""
    pass

def security_node(state: ReviewState) -> ReviewState:
    """Run security analysis on file tree"""
    pass

def performance_node(state: ReviewState) -> ReviewState:
    """Run performance analysis on file tree"""
    pass

def style_node(state: ReviewState) -> ReviewState:
    """Run style analysis on file tree"""
    pass

def aggregator_node(state: ReviewState) -> ReviewState:
    """Compile all findings into final report"""
    pass
```

### Graph Construction

```python
from langgraph.graph import StateGraph

workflow = StateGraph(ReviewState)

# Add nodes
workflow.add_node("ingestor", ingestor_node)
workflow.add_node("security", security_node)
workflow.add_node("performance", performance_node)
workflow.add_node("style", style_node)
workflow.add_node("aggregator", aggregator_node)

# Define edges
workflow.set_entry_point("ingestor")

# Parallel execution after ingestion
workflow.add_edge("ingestor", "security")
workflow.add_edge("ingestor", "performance")
workflow.add_edge("ingestor", "style")

# Aggregation after all agents complete
workflow.add_edge("security", "aggregator")
workflow.add_edge("performance", "aggregator")
workflow.add_edge("style", "aggregator")

workflow.set_finish_point("aggregator")

graph = workflow.compile()
```

---

This architecture ensures:
✅ Scalability for large repositories
✅ Parallel processing for speed
✅ Robust error handling
✅ Extensibility for new agents
✅ Production-ready quality
