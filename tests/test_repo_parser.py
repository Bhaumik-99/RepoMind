import pytest
from backend.app.ingestion.repository import parse_github

def test_parse_github():
    assert parse_github("https://github.com/openai/openai-python") == ("openai", "openai-python")

def test_reject_non_github():
    with pytest.raises(ValueError):
        parse_github("https://gitlab.com/a/b")
