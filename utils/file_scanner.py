"""
File Scanner - Local Directory Scanning with .gitignore Support
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import pathspec

from .logger import get_logger

logger = get_logger(__name__)


# Default ignore patterns
DEFAULT_IGNORE_PATTERNS = [
    # Python
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'pip-log.txt',
    'pip-delete-this-directory.txt',
    '.venv/',
    'venv/',
    'ENV/',
    'env/',
    
    # Node.js
    'node_modules/',
    'npm-debug.log',
    'yarn-error.log',
    
    # Build outputs
    'build/',
    'dist/',
    '*.egg-info/',
    '.eggs/',
    
    # IDEs
    '.vscode/',
    '.idea/',
    '*.swp',
    '*.swo',
    '.DS_Store',
    
    # Version control
    '.git/',
    '.svn/',
    '.hg/',
    
    # Binaries and media
    '*.so',
    '*.dylib',
    '*.dll',
    '*.exe',
    '*.jpg',
    '*.jpeg',
    '*.png',
    '*.gif',
    '*.mp4',
    '*.mp3',
    '*.zip',
    '*.tar',
    '*.gz',
    
    # Logs
    '*.log',
    'logs/',
]


# Code file extensions to focus on
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx',
    '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.go', '.rb', '.php', '.swift',
    '.kt', '.rs', '.scala', '.r', '.m',
    '.sh', '.bash', '.zsh', '.sql',
    '.html', '.css', '.scss', '.sass',
    '.json', '.yaml', '.yml', '.xml',
    '.md', '.rst', '.txt',
}


def load_gitignore_patterns(directory: Path) -> pathspec.PathSpec:
    """
    Load .gitignore patterns from directory.
    
    Args:
        directory: Directory to search for .gitignore
        
    Returns:
        PathSpec object for matching patterns
    """
    patterns = DEFAULT_IGNORE_PATTERNS.copy()
    
    gitignore_path = directory / '.gitignore'
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_patterns = f.read().splitlines()
                # Filter out comments and empty lines
                gitignore_patterns = [
                    line.strip() for line in gitignore_patterns
                    if line.strip() and not line.strip().startswith('#')
                ]
                patterns.extend(gitignore_patterns)
                logger.info(f"📄 Loaded {len(gitignore_patterns)} patterns from .gitignore")
        except Exception as e:
            logger.warning(f"⚠️ Failed to read .gitignore: {str(e)}")
    
    # Add patterns from environment variable
    env_patterns = os.getenv('IGNORE_PATTERNS', '')
    if env_patterns:
        additional = [p.strip() for p in env_patterns.split(',') if p.strip()]
        patterns.extend(additional)
        logger.info(f"📄 Loaded {len(additional)} patterns from environment")
    
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)


def should_scan_file(
    file_path: Path,
    max_size_mb: float = 5.0,
    code_only: bool = True
) -> bool:
    """
    Determine if a file should be scanned.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB
        code_only: Only scan code files
        
    Returns:
        True if file should be scanned
    """
    # Check if file exists and is readable
    if not file_path.is_file():
        return False
    
    try:
        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.debug(f"⏭️ Skipping large file ({size_mb:.2f}MB): {file_path.name}")
            return False
        
        # Check extension if code_only is True
        if code_only and file_path.suffix.lower() not in CODE_EXTENSIONS:
            return False
        
        # Try to detect if file is binary
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try reading first 1KB
        except (UnicodeDecodeError, PermissionError):
            logger.debug(f"⏭️ Skipping binary/unreadable file: {file_path.name}")
            return False
        
        return True
        
    except Exception as e:
        logger.debug(f"⏭️ Error checking file {file_path.name}: {str(e)}")
        return False


def scan_local_directory(
    directory_path: Union[str, Path],
    max_size_mb: Optional[float] = None,
    code_only: bool = True
) -> Dict:
    """
    Scan a local directory and build file tree.
    
    Args:
        directory_path: Path to directory to scan
        max_size_mb: Maximum file size in MB (from env if None)
        code_only: Only include code files
        
    Returns:
        Dictionary with file tree information:
        {
            'root_path': Path,
            'files': List[Dict],
            'total_files': int,
            'total_size_mb': float,
            'extensions': Dict[str, int]
        }
        
    Raises:
        ValueError: If directory doesn't exist or isn't accessible
    """
    directory = Path(directory_path).resolve()
    
    # Validation
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Get max file size from environment if not provided
    if max_size_mb is None:
        max_size_mb = float(os.getenv('MAX_FILE_SIZE_MB', '5.0'))
    
    logger.info(f"🔍 Scanning directory: {directory}")
    logger.info(f"📏 Max file size: {max_size_mb}MB")
    logger.info(f"📝 Code files only: {code_only}")
    
    # Load ignore patterns
    ignore_spec = load_gitignore_patterns(directory)
    
    # Scan files
    files = []
    extensions_count = {}
    total_size = 0
    
    for file_path in directory.rglob('*'):
        # Get relative path for ignore matching
        try:
            relative_path = file_path.relative_to(directory)
        except ValueError:
            continue
        
        # Check if should be ignored
        if ignore_spec.match_file(str(relative_path)):
            logger.debug(f"⏭️ Ignoring: {relative_path}")
            continue
        
        # Check if should scan
        if not should_scan_file(file_path, max_size_mb, code_only):
            continue
        
        # Get file info
        try:
            stat = file_path.stat()
            size_bytes = stat.st_size
            size_mb = size_bytes / (1024 * 1024)
            
            file_info = {
                'path': str(file_path),
                'relative_path': str(relative_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size_bytes': size_bytes,
                'size_mb': round(size_mb, 3),
            }
            
            files.append(file_info)
            total_size += size_bytes
            
            # Track extensions
            ext = file_path.suffix.lower() or 'no_extension'
            extensions_count[ext] = extensions_count.get(ext, 0) + 1
            
        except Exception as e:
            logger.warning(f"⚠️ Error processing {relative_path}: {str(e)}")
            continue
    
    # Sort files by path for consistent ordering
    files.sort(key=lambda x: x['relative_path'])
    
    total_size_mb = total_size / (1024 * 1024)
    
    logger.info(f"✅ Scan completed:")
    logger.info(f"   📊 Files found: {len(files)}")
    logger.info(f"   💾 Total size: {total_size_mb:.2f}MB")
    logger.info(f"   📑 Extensions: {len(extensions_count)}")
    
    # Log top extensions
    top_extensions = sorted(
        extensions_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    for ext, count in top_extensions:
        logger.info(f"      {ext}: {count} files")
    
    return {
        'root_path': str(directory),
        'files': files,
        'total_files': len(files),
        'total_size_mb': round(total_size_mb, 2),
        'extensions': extensions_count,
    }


def read_file_content(file_path: Union[str, Path]) -> Optional[str]:
    """
    Read content of a file safely.
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as string, or None if read fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read {file_path}: {str(e)}")
        return None
