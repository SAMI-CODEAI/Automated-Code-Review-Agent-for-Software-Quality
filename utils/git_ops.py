"""
Git Operations - Repository Cloning and URL Detection
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from git import Repo, GitCommandError
from .logger import get_logger

logger = get_logger(__name__)


def is_git_url(path: str) -> bool:
    """
    Determine if the given path is a Git repository URL.
    
    Supports:
    - https://github.com/user/repo
    - git@github.com:user/repo.git
    - https://gitlab.com/user/repo
    - https://bitbucket.org/user/repo
    
    Args:
        path: Input path or URL
        
    Returns:
        True if path is a Git URL, False otherwise
    """
    # Common Git hosting patterns
    git_patterns = [
        r'^https?://github\.com/',
        r'^https?://gitlab\.com/',
        r'^https?://bitbucket\.org/',
        r'^git@github\.com:',
        r'^git@gitlab\.com:',
        r'^git@bitbucket\.org:',
        r'\.git$',
    ]
    
    for pattern in git_patterns:
        if re.search(pattern, path, re.IGNORECASE):
            return True
    
    # Check if it looks like a URL
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clone_repository(
    repo_url: str,
    target_dir: Optional[Path] = None,
    branch: Optional[str] = None,
    depth: int = 1
) -> Tuple[Path, bool]:
    """
    Clone a Git repository to a local directory.
    
    Args:
        repo_url: Git repository URL
        target_dir: Target directory (creates temp dir if None)
        branch: Specific branch to clone (default: default branch)
        depth: Clone depth (1 for shallow clone, None for full history)
        
    Returns:
        Tuple of (cloned_path, is_temp_dir)
        
    Raises:
        ValueError: If repo_url is invalid
        GitCommandError: If cloning fails
    """
    if not is_git_url(repo_url):
        raise ValueError(f"Invalid Git repository URL: {repo_url}")
    
    # Create target directory
    is_temp = target_dir is None
    if is_temp:
        temp_dir = tempfile.mkdtemp(prefix="code_review_")
        target_dir = Path(temp_dir)
        logger.info(f"📁 Created temporary directory: {target_dir}")
    else:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"🔄 Cloning repository: {repo_url}")
        logger.info(f"📍 Target directory: {target_dir}")
        
        # Clone options
        clone_kwargs = {
            'depth': depth if depth > 0 else None,
        }
        
        if branch:
            clone_kwargs['branch'] = branch
            logger.info(f"🌿 Cloning branch: {branch}")
        
        # Perform clone
        repo = Repo.clone_from(
            repo_url,
            str(target_dir),
            **clone_kwargs
        )
        
        logger.info(f"✅ Repository cloned successfully")
        logger.info(f"📊 Active branch: {repo.active_branch.name}")
        
        # Get commit info
        latest_commit = repo.head.commit
        logger.info(f"📝 Latest commit: {latest_commit.hexsha[:8]} - {latest_commit.message.strip()}")
        
        return target_dir, is_temp
        
    except GitCommandError as e:
        logger.error(f"❌ Failed to clone repository: {str(e)}")
        
        # Clean up if we created a temp directory
        if is_temp and target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        
        raise


def cleanup_repository(repo_path: Path, force: bool = False):
    """
    Clean up a cloned repository directory.
    
    Args:
        repo_path: Path to repository directory
        force: Force cleanup even if not in temp directory
    """
    if not repo_path.exists():
        logger.warning(f"⚠️ Repository path does not exist: {repo_path}")
        return
    
    # Safety check: only auto-cleanup if in temp directory
    is_temp = str(repo_path).startswith(tempfile.gettempdir())
    
    if not is_temp and not force:
        logger.warning(
            f"⚠️ Skipping cleanup of non-temporary directory: {repo_path}\n"
            f"   Use force=True to override"
        )
        return
    
    try:
        logger.info(f"🧹 Cleaning up repository: {repo_path}")
        shutil.rmtree(repo_path, ignore_errors=True)
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Failed to cleanup repository: {str(e)}")


def extract_repo_name(repo_url: str) -> str:
    """
    Extract repository name from URL.
    
    Args:
        repo_url: Git repository URL
        
    Returns:
        Repository name
        
    Example:
        'https://github.com/user/my-repo' -> 'my-repo'
    """
    # Remove .git suffix if present
    url = repo_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Extract last path component
    parts = url.split('/')
    repo_name = parts[-1]
    
    # Handle git@ URLs
    if ':' in repo_name:
        repo_name = repo_name.split(':')[-1]
    
    return repo_name or "unknown_repo"
