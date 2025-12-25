from unittest.mock import AsyncMock, patch

@patch("backend.app.routers.chat.get_qdrant_service")
@patch("backend.app.routers.chat.get_gemini_agent")
def test_selective_chat_skips_qdrant(mock_gemini, mock_qdrant, client, mock_settings):
    """CRITICAL: Test that selective chat does NOT call Qdrant."""
    # Mock services
    mock_gemini.return_value.generate_selective_answer = AsyncMock(return_value="Answer from selection")
    
    response = client.post("/api/selective-chat", json={
        "query": "test",
        "selection_text": "This is a long enough selection text for testing purposes."
    })
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Answer from selection"
    
    # Verify Qdrant was NOT called
    mock_qdrant.return_value.search_chunks.assert_not_called()
