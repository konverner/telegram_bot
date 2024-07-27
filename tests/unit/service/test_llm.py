import pytest
from unittest.mock import patch, MagicMock
from telegram_bot.service.llm import FireworksLLM

@patch('fireworks.client.Completion.create')
def test_prompts(mock_create):
    # Arrange
    llm = FireworksLLM()
    document = "test document"
    question = "test question"

    # Act
    prompt = llm.prompt(document, question)

    # Assert
    assert document in prompt
    assert question in prompt
