from scripts.chunker import chunk_chapter, Chunk
from scripts.collect_chapters import Chapter
from pathlib import Path

def test_chunker_creates_valid_chunks():
    """Test that chunker respects token limits and creates valid chunks."""
    content = "Sentence one. " * 50  # ~100 tokens
    chapter = Chapter(
        path=Path("test.md"),
        module="test",
        title="Test Chapter",
        content=content,
        source_url="http://test"
    )
    
    chunks = chunk_chapter(chapter, min_tokens=50, max_tokens=200)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, Chunk)
        assert chunk.token_count <= 200
        assert chunk.module == "test"
