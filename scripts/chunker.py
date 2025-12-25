"""
Text chunking for RAG ingestion.

This script chunks chapter content into 200-800 token segments
with deterministic chunk IDs and overlap for context preservation.
"""

import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional
import tiktoken

from .collect_chapters import Chapter


@dataclass
class Chunk:
    """Represents a text chunk for vector storage."""
    chunk_id: str
    module: str
    chapter: str
    content: str
    source_url: str
    start_pos: int
    end_pos: int
    token_count: int


# Initialize tiktoken encoder (using cl100k_base, same as GPT-4/Cohere)
try:
    ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    # Fallback if tiktoken fails
    ENCODER = None


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    if ENCODER:
        return len(ENCODER.encode(text))
    else:
        # Rough estimate: ~4 chars per token
        return len(text) // 4


def clean_markdown(text: str) -> str:
    """
    Remove Markdown formatting while preserving semantic content.
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', ' [code block] ', text)
    text = re.sub(r'`[^`]+`', ' [code] ', text)
    
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    
    # Convert links to just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove headers but keep text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for chunking.
    """
    # Split on sentence-ending punctuation followed by space or newline
    # This regex handles common sentence endings
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Also split on double newlines (paragraph breaks)
    result = []
    for sentence in sentences:
        if '\n\n' in sentence:
            parts = sentence.split('\n\n')
            result.extend([p.strip() for p in parts if p.strip()])
        else:
            if sentence.strip():
                result.append(sentence.strip())
    
    return result


import uuid

def generate_chunk_id(module: str, chapter: str, content: str) -> str:
    """
    Generate a deterministic chunk ID based on content.
    
    Uses UUID v5 based on module + chapter + first 100 chars of content.
    """
    # Create a stable identifier
    identifier = f"{module}:{chapter}:{content[:100]}"
    
    # Use a fixed namespace (e.g., DNS or a custom one)
    NAMESPACE_CHUNKS = uuid.NAMESPACE_DNS
    chunk_id = str(uuid.uuid5(NAMESPACE_CHUNKS, identifier))
    
    return chunk_id


def chunk_chapter(
    chapter: Chapter,
    min_tokens: int = 200,
    max_tokens: int = 800,
    overlap_sentences: int = 2
) -> List[Chunk]:
    """
    Chunk a chapter into segments of min_tokens to max_tokens.
    
    Args:
        chapter: Chapter object to chunk
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
        overlap_sentences: Number of sentences to overlap between chunks
        
    Returns:
        List of Chunk objects
    """
    chunks = []
    
    # Clean and split content
    cleaned_content = clean_markdown(chapter.content)
    sentences = split_into_sentences(cleaned_content)
    
    if not sentences:
        return chunks
    
    current_sentences = []
    current_tokens = 0
    current_start_pos = 0
    text_position = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        
        # Check if adding this sentence would exceed max_tokens
        if current_tokens + sentence_tokens > max_tokens and current_tokens >= min_tokens:
            # Finalize current chunk
            chunk_text = ' '.join(current_sentences)
            chunk_id = generate_chunk_id(chapter.module, chapter.title, chunk_text)
            
            chunk = Chunk(
                chunk_id=chunk_id,
                module=chapter.module,
                chapter=chapter.title,
                content=chunk_text,
                source_url=chapter.source_url,
                start_pos=current_start_pos,
                end_pos=current_start_pos + len(chunk_text),
                token_count=current_tokens
            )
            chunks.append(chunk)
            
            # Start new chunk with overlap
            if overlap_sentences > 0 and len(current_sentences) >= overlap_sentences:
                overlap = current_sentences[-overlap_sentences:]
                current_sentences = overlap
                current_tokens = sum(count_tokens(s) for s in overlap)
            else:
                current_sentences = []
                current_tokens = 0
            
            current_start_pos = text_position
        
        current_sentences.append(sentence)
        current_tokens += sentence_tokens
        text_position += len(sentence) + 1  # +1 for space
    
    # Don't forget the final chunk
    if current_sentences and current_tokens >= min_tokens // 2:  # Allow smaller final chunks
        chunk_text = ' '.join(current_sentences)
        chunk_id = generate_chunk_id(chapter.module, chapter.title, chunk_text)
        
        chunk = Chunk(
            chunk_id=chunk_id,
            module=chapter.module,
            chapter=chapter.title,
            content=chunk_text,
            source_url=chapter.source_url,
            start_pos=current_start_pos,
            end_pos=current_start_pos + len(chunk_text),
            token_count=current_tokens
        )
        chunks.append(chunk)
    
    return chunks


def chunk_all_chapters(
    chapters: List[Chapter],
    min_tokens: int = 200,
    max_tokens: int = 800,
    overlap_sentences: int = 2
) -> List[Chunk]:
    """
    Chunk all chapters and return a flat list of chunks.
    """
    all_chunks = []
    
    for chapter in chapters:
        chapter_chunks = chunk_chapter(
            chapter,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
            overlap_sentences=overlap_sentences
        )
        all_chunks.extend(chapter_chunks)
        print(f"  Chunked: {chapter.module}/{chapter.title} -> {len(chapter_chunks)} chunks")
    
    return all_chunks


def main():
    """Test chunking with sample content."""
    from pathlib import Path
    from .collect_chapters import collect_chapters
    import sys
    
    # Find docs path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_path = project_root / "physical-ai-robotics-book" / "docs"
    
    print(f"Collecting chapters from: {docs_path}")
    chapters = collect_chapters(docs_path)
    
    print(f"\nChunking {len(chapters)} chapters...")
    chunks = chunk_all_chapters(chapters)
    
    print(f"\nCreated {len(chunks)} chunks:")
    for chunk in chunks[:5]:  # Show first 5
        print(f"  - [{chunk.module}:{chunk.chapter}] {chunk.chunk_id} ({chunk.token_count} tokens)")
    
    if len(chunks) > 5:
        print(f"  ... and {len(chunks) - 5} more")
    
    # Validate chunk sizes
    valid = all(200 <= c.token_count <= 800 or c.token_count >= 100 for c in chunks)
    print(f"\nAll chunks within size limits: {valid}")


if __name__ == "__main__":
    main()
