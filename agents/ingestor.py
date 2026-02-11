"""
Ingestor Agent - Code Repository/Directory Ingestion
"""

from pathlib import Path
from typing import Dict, Optional, TypedDict

from utils.git_ops import is_git_url, clone_repository, cleanup_repository, extract_repo_name
from utils.file_scanner import scan_local_directory
from utils.logger import get_logger

logger = get_logger(__name__)


class IngestionResult(TypedDict):
    """Result of ingestion process"""
    success: bool
    source_type: str  # 'git' or 'local'
    source_path: str
    working_directory: str
    file_tree: Dict
    is_temp: bool
    error: Optional[str]


class IngestorAgent:
    """
    Agent responsible for ingesting code from various sources.
    
    Supports:
    - GitHub/GitLab/Bitbucket repositories
    - Local directories
    
    Handles:
    - URL detection and validation
    - Repository cloning
    - Directory scanning
    - .gitignore pattern respect
    - File filtering and validation
    """
    
    def __init__(
        self,
        max_file_size_mb: float = 5.0,
        code_only: bool = True
    ):
        """
        Initialize Ingestor Agent.
        
        Args:
            max_file_size_mb: Maximum file size to process
            code_only: Only process code files
        """
        self.max_file_size_mb = max_file_size_mb
        self.code_only = code_only
        self.temp_directories = []  # Track temp dirs for cleanup
        
        logger.info("🤖 Ingestor Agent initialized")
    
    def ingest(self, input_path: str) -> IngestionResult:
        """
        Ingest code from the specified path.
        
        Args:
            input_path: URL or local directory path
            
        Returns:
            IngestionResult with file tree and metadata
        """
        logger.info("=" * 80)
        logger.info("📥 Starting code ingestion")
        logger.info(f"📍 Input path: {input_path}")
        logger.info("=" * 80)
        
        try:
            # Determine source type
            if is_git_url(input_path):
                result = self._ingest_git_repository(input_path)
            else:
                result = self._ingest_local_directory(input_path)
            
            if result['success']:
                logger.info("=" * 80)
                logger.info("✅ Ingestion completed successfully")
                logger.info(f"📊 Files ingested: {result['file_tree']['total_files']}")
                logger.info(f"💾 Total size: {result['file_tree']['total_size_mb']}MB")
                logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {str(e)}", exc_info=True)
            return IngestionResult(
                success=False,
                source_type='unknown',
                source_path=input_path,
                working_directory='',
                file_tree={},
                is_temp=False,
                error=str(e)
            )
    
    def _ingest_git_repository(self, repo_url: str) -> IngestionResult:
        """
        Ingest a Git repository.
        
        Args:
            repo_url: Git repository URL
            
        Returns:
            IngestionResult
        """
        logger.info("🌐 Source type: Git Repository")
        
        # Extract repo name for logging
        repo_name = extract_repo_name(repo_url)
        logger.info(f"📦 Repository: {repo_name}")
        
        # Clone repository
        clone_path, is_temp = clone_repository(repo_url)
        
        if is_temp:
            self.temp_directories.append(clone_path)
        
        # Scan the cloned repository
        try:
            file_tree = scan_local_directory(
                clone_path,
                max_size_mb=self.max_file_size_mb,
                code_only=self.code_only
            )
            
            return IngestionResult(
                success=True,
                source_type='git',
                source_path=repo_url,
                working_directory=str(clone_path),
                file_tree=file_tree,
                is_temp=is_temp,
                error=None
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to scan repository: {str(e)}")
            
            # Cleanup on failure
            if is_temp:
                cleanup_repository(clone_path)
                self.temp_directories.remove(clone_path)
            
            raise
    
    def _ingest_local_directory(self, directory_path: str) -> IngestionResult:
        """
        Ingest a local directory.
        
        Args:
            directory_path: Local directory path
            
        Returns:
            IngestionResult
        """
        logger.info("📁 Source type: Local Directory")
        
        # Resolve path
        path = Path(directory_path).resolve()
        
        # Scan directory
        file_tree = scan_local_directory(
            path,
            max_size_mb=self.max_file_size_mb,
            code_only=self.code_only
        )
        
        return IngestionResult(
            success=True,
            source_type='local',
            source_path=directory_path,
            working_directory=str(path),
            file_tree=file_tree,
            is_temp=False,
            error=None
        )
    
    def cleanup(self):
        """Clean up temporary directories created during ingestion."""
        if not self.temp_directories:
            return
        
        logger.info(f"🧹 Cleaning up {len(self.temp_directories)} temporary directories")
        
        for temp_dir in self.temp_directories:
            try:
                cleanup_repository(temp_dir)
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {temp_dir}: {str(e)}")
        
        self.temp_directories.clear()
        logger.info("✅ Cleanup completed")
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        try:
            self.cleanup()
        except Exception:
            pass


def create_ingestor_node():
    """
    Create an ingestor node function for LangGraph.
    
    Returns:
        Node function that processes ReviewState
    """
    def ingestor_node(state: Dict) -> Dict:
        """
        Ingestor node for LangGraph workflow.
        
        Processes:
        - input_path: Path or URL to ingest
        
        Updates state with:
        - file_tree: Scanned files information
        - total_files: Number of files found
        - working_directory: Directory being analyzed
        - source_type: 'git' or 'local'
        - error: Error message if failed
        """
        logger.info("🔵 Ingestor Node: Starting")
        
        input_path = state.get('input_path')
        if not input_path:
            error_msg = "No input_path provided in state"
            logger.error(f"❌ {error_msg}")
            return {
                **state,
                'error': error_msg,
                'file_tree': {},
                'total_files': 0
            }
        
        # Create ingestor and ingest
        ingestor = IngestorAgent()
        try:
            result = ingestor.ingest(input_path)
            
            if not result['success']:
                # Clean up temp dirs on failure
                ingestor.cleanup()
                return {
                    **state,
                    'error': result['error'],
                    'file_tree': {},
                    'total_files': 0
                }
            
            # IMPORTANT: Prevent auto-cleanup on __del__ so downstream agents
            # can still read the cloned files. Cleanup will happen in the
            # aggregator node after all agents have finished.
            ingestor.temp_directories.clear()
            
            # Update state
            updated_state = {
                **state,
                'file_tree': result['file_tree'],
                'total_files': result['file_tree']['total_files'],
                'working_directory': result['working_directory'],
                'source_type': result['source_type'],
                'is_temp_directory': result['is_temp'],
            }
            
            logger.info("🔵 Ingestor Node: Completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"❌ Ingestor node failed: {str(e)}", exc_info=True)
            ingestor.cleanup()
            return {
                **state,
                'error': str(e),
                'file_tree': {},
                'total_files': 0
            }
    
    return ingestor_node
