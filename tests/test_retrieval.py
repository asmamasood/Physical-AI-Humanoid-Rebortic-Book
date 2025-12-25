from unittest.mock import AsyncMock, patch
from backend.app.models import ChatResponse

@patch("backend.app.routers.chat.get_cohere_embedder")
@patch("backend.app.routers.chat.get_qdrant_service")
@patch("backend.app.routers.chat.get_gemini_agent")
def test_chat_flow(mock_gemini, mock_qdrant, mock_cohere, client, mock_settings):
    """Test standard chat flow end-to-end with mocks."""
    # Mock services
    mock_cohere.return_value.embed_query = AsyncMock(return_value=[0.1] * 1024)
    mock_qdrant.return_value.search_chunks = AsyncMock(return_value=[
        {"chunk_id": "1", "content": "text", "module": "m1", "chapter": "c1", "source_url": "url"}
    ])
    mock_gemini.return_value.generate_rag_answer = AsyncMock(return_value=("Answer", []))
    
    response = client.post("/api/chat", json={"query": "test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
