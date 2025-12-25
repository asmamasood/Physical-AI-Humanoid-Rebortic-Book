"""
Collect chapters from Docusaurus docs directory.

This script enumerates all Markdown files, extracts frontmatter metadata,
and returns structured Chapter objects for processing.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import yaml


@dataclass
class Chapter:
    """Represents a chapter from the book."""
    path: Path
    module: str
    title: str
    content: str
    source_url: str
    sidebar_position: Optional[int] = None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from Markdown content.
    
    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    frontmatter = {}
    body = content
    
    # Check for YAML frontmatter (--- at start)
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError:
                # If YAML parsing fails, treat as no frontmatter
                pass
    
    return frontmatter, body


def extract_module_from_path(file_path: Path, docs_root: Path) -> str:
    """
    Extract module name from file path.
    
    Example: docs/module-1/chapter-1.md -> "module-1"
    """
    try:
        relative = file_path.relative_to(docs_root)
        parts = relative.parts
        
        # Look for module-* directory
        for part in parts:
            if part.startswith('module-'):
                return part
        
        # If no module found, use parent directory or "general"
        if len(parts) > 1:
            return parts[0]
        return "general"
    except ValueError:
        return "general"


def generate_source_url(file_path: Path, root_path: Path, base_url: str = "https://asmamasood.github.io/Physical-AI-Humanoid-Rebortic-Book", url_prefix: str = "/docs/") -> str:
    """
    Generate the GitHub Pages URL for a chapter.
    
    Example: docs/module-1/chapter-1.md -> https://asmamasood.github.io/Physical-AI-Humanoid-Rebortic-Book/docs/module-1/chapter-1
    """
    try:
        relative = file_path.relative_to(root_path)
        # Remove .md extension and convert to URL path
        url_path = str(relative).replace('\\', '/').replace('.md', '')
        # Handle index files (blog posts often use index.md)
        if url_path.endswith('/index'):
            url_path = url_path[:-6]
            
        return f"{base_url}{url_prefix}{url_path}"
    except ValueError:
        return base_url


def collect_chapters(
    root_path: Path, 
    base_url: str = "https://asmamasood.github.io/Physical-AI-Humanoid-Rebortic-Book",
    url_prefix: str = "/docs/",
    fixed_module: Optional[str] = None
) -> List[Chapter]:
    """
    Recursively enumerate .md files and extract chapter information.
    
    Args:
        root_path: Path to the directory (docs or blog)
        base_url: Base URL for generating source links
        url_prefix: URL prefix (e.g. "/docs/" or "/blog/")
        fixed_module: If provided, all chapters get this module name
        
    Returns:
        List of Chapter objects with extracted metadata
    """
    chapters = []
    
    if not root_path.exists():
        print(f"Warning: Directory not found: {root_path}")
        return []
    
    # Find all Markdown files
    for md_file in sorted(root_path.rglob("*.md")):
        # Skip category files and hidden files
        if md_file.name.startswith('_') or md_file.name.startswith('.'):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")
            continue
        
        # Parse frontmatter
        frontmatter, body = parse_frontmatter(content)
        
        # Extract metadata
        if fixed_module:
            module = fixed_module
        else:
            module = extract_module_from_path(md_file, root_path)
            
        title = frontmatter.get('title', md_file.stem.replace('-', ' ').title())
        sidebar_position = frontmatter.get('sidebar_position')
        source_url = generate_source_url(md_file, root_path, base_url, url_prefix)
        
        chapter = Chapter(
            path=md_file,
            module=module,
            title=title,
            content=body,
            source_url=source_url,
            sidebar_position=sidebar_position
        )
        
        chapters.append(chapter)
        print(f"  Collected: {module}/{title}")
    
    return chapters


def main():
    """Test chapter collection."""
    import sys
    
    # Default to physical-ai-robotics-book/docs
    if len(sys.argv) > 1:
        docs_path = Path(sys.argv[1])
    else:
        # Find project root (where .env.example is)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        docs_path = project_root / "physical-ai-robotics-book" / "docs"
    
    print(f"Collecting chapters from: {docs_path}")
    
    try:
        chapters = collect_chapters(docs_path)
        print(f"\nCollected {len(chapters)} chapters:")
        for ch in chapters:
            print(f"  - [{ch.module}] {ch.title} ({len(ch.content)} chars)")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
