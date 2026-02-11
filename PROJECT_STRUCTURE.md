# Automated Code Review Agent - Project Structure

## 📦 Phase 1: Environment Setup (COMPLETED)

### Created Files

#### Core Configuration
- ✅ `requirements.txt` - Python dependencies including LangGraph, LangChain, Gemini, static analysis tools
- ✅ `.env.template` - Environment variable template for API keys and configuration
- ✅ `.gitignore` - Git ignore patterns for Python projects
- ✅ `README.md` - Comprehensive project documentation

#### Application Entry Point
- ✅ `main.py` - CLI entry point with Click framework

#### Package Structure
```
📁 Automated Code Review Agent for Software Quality/
├── 📄 main.py                          # CLI entry point
├── 📄 requirements.txt                 # Dependencies
├── 📄 .env.template                    # Environment configuration
├── 📄 .gitignore                       # Git ignore patterns
├── 📄 README.md                        # Documentation
│
├── 📁 agents/                          # Agent implementations
│   ├── 📄 __init__.py                 # Package exports
│   ├── 📄 ingestor.py                 # [TO BE IMPLEMENTED]
│   ├── 📄 security.py                 # [TO BE IMPLEMENTED]
│   ├── 📄 performance.py              # [TO BE IMPLEMENTED]
│   ├── 📄 style.py                    # [TO BE IMPLEMENTED]
│   └── 📄 aggregator.py               # [TO BE IMPLEMENTED]
│
├── 📁 graph/                           # LangGraph orchestration
│   ├── 📄 __init__.py                 # Package exports
│   ├── 📄 state.py                    # [TO BE IMPLEMENTED]
│   └── 📄 workflow.py                 # [TO BE IMPLEMENTED]
│
├── 📁 tools/                           # Static analysis tools
│   ├── 📄 __init__.py                 # Package exports
│   ├── 📄 bandit_tool.py              # [TO BE IMPLEMENTED]
│   └── 📄 radon_tool.py               # [TO BE IMPLEMENTED]
│
├── 📁 utils/                           # Utility functions
│   ├── 📄 __init__.py                 # Package exports
│   ├── 📄 git_ops.py                  # [TO BE IMPLEMENTED]
│   ├── 📄 file_scanner.py             # [TO BE IMPLEMENTED]
│   └── 📄 logger.py                   # [TO BE IMPLEMENTED]
│
└── 📁 prompts/                         # Agent system prompts
    ├── 📄 __init__.py                 # Package exports
    ├── 📄 security.py                 # [TO BE IMPLEMENTED]
    ├── 📄 performance.py              # [TO BE IMPLEMENTED]
    └── 📄 style.py                    # [TO BE IMPLEMENTED]
```

---

## 🔄 Next Steps: Phase 2-5 Implementation

### Phase 2: Ingestion Logic
**Files to implement:**
- `utils/git_ops.py` - Clone repositories and detect URLs
- `utils/file_scanner.py` - Scan local directories with .gitignore support
- `utils/logger.py` - Logging configuration
- `agents/ingestor.py` - Ingestor agent implementation

### Phase 3: LangGraph Orchestration
**Files to implement:**
- `graph/state.py` - ReviewState TypedDict definition
- `graph/workflow.py` - LangGraph workflow with parallel execution
- Agent nodes and edge routing logic

### Phase 4: Specialized Agents & Prompts
**Files to implement:**
- `prompts/security.py` - Expert security analysis prompt
- `prompts/performance.py` - Performance optimization prompt
- `prompts/style.py` - Code style compliance prompt
- `agents/security.py` - Security agent with Bandit integration
- `agents/performance.py` - Performance agent with Radon integration
- `agents/style.py` - Style agent with Pylint integration
- `agents/aggregator.py` - Report aggregation agent
- `tools/bandit_tool.py` - Bandit wrapper
- `tools/radon_tool.py` - Radon wrapper

### Phase 5: Testing & Documentation
- Unit tests for each agent
- Integration tests for workflow
- Usage examples
- Performance optimization

---

## 🎯 Key Design Decisions

### 1. **Parallel Agent Execution**
The LangGraph workflow will execute Security, Performance, and Style agents in parallel to minimize total processing time.

### 2. **File-by-File Processing**
To handle large repositories and avoid token limits:
- Files processed individually
- Results accumulated in state
- Configurable max file size (5MB default)

### 3. **Static Analysis Integration**
Each agent will:
1. Run static analysis tools (Bandit/Radon/Pylint)
2. Feed results to LLM for expert interpretation
3. Combine automated + AI insights

### 4. **State Management**
```python
class ReviewState(TypedDict):
    # Input
    input_path: str
    output_dir: str
    
    # Ingestion
    file_tree: List[Dict]
    total_files: int
    
    # Agent Findings
    security_findings: List[Dict]
    performance_findings: List[Dict]
    style_findings: List[Dict]
    
    # Aggregation
    final_report: str
    report_path: str
    
    # Error Handling
    error: Optional[str]
```

### 5. **Error Handling**
- Retry logic for API calls (Tenacity)
- Graceful degradation if static tools fail
- Detailed error logging
- Validation for URLs and paths

---

## 🔑 Environment Variables Required

Based on `.env.template`, you will need:
- `GOOGLE_API_KEY` - Your Gemini API key (required)
- `GEMINI_MODEL` - Model selection (optional, defaults to gemini-1.5-pro-latest)
- Configuration for file size limits, ignore patterns, etc.

---

## ✅ Ready for Approval

**Current Status:** Phase 1 (Environment Setup) is complete.

**Awaiting your approval to proceed with:**
- Phase 2: Ingestion Logic Implementation
- Phase 3: LangGraph Workflow Implementation
- Phase 4: Agent & Prompt Implementation
- Phase 5: Testing & Verification

Please review the project structure and confirm if you'd like me to proceed with the implementation phases.
