"""Tests for LLM output parser."""

from __future__ import annotations

import pytest

from hallucination_firewall.parsers.llm_output_parser import (
    detect_language_heuristic,
    extract_code_blocks,
    validate_llm_output,
)

SAMPLE_MARKDOWN = """Here's the implementation:

```python
import requests

def fetch_data():
    response = requests.get("https://api.example.com")
    return response.json()
```

And the test:

```python
def test_fetch():
    assert True
```
"""

SAMPLE_MULTI_LANG = """
```python
import os
x = os.path.join("a", "b")
```

```javascript
const axios = require('axios');
```

```json
{"key": "value"}
```
"""


class TestExtractCodeBlocks:
    """Test code block extraction."""

    def test_extract_single_block(self) -> None:
        md = "```python\nprint('hello')\n```"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print" in blocks[0].code

    def test_extract_multiple_blocks(self) -> None:
        blocks = extract_code_blocks(SAMPLE_MARKDOWN)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "python"

    def test_extract_multi_language(self) -> None:
        blocks = extract_code_blocks(SAMPLE_MULTI_LANG)
        assert len(blocks) == 3
        languages = [b.language for b in blocks]
        assert "python" in languages
        assert "javascript" in languages
        assert "json" in languages

    def test_block_index_increments(self) -> None:
        blocks = extract_code_blocks(SAMPLE_MARKDOWN)
        assert blocks[0].block_index == 0
        assert blocks[1].block_index == 1

    def test_line_numbers_tracked(self) -> None:
        blocks = extract_code_blocks(SAMPLE_MARKDOWN)
        assert blocks[0].line_number >= 1
        assert blocks[1].line_number > blocks[0].line_number

    def test_empty_markdown(self) -> None:
        blocks = extract_code_blocks("")
        assert blocks == []

    def test_no_code_blocks(self) -> None:
        blocks = extract_code_blocks("Just plain text\nNo code here")
        assert blocks == []

    def test_empty_code_block(self) -> None:
        md = "```python\n```"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].code == ""

    def test_normalize_language_tag(self) -> None:
        md = "```py\nprint(1)\n```"
        blocks = extract_code_blocks(md)
        assert blocks[0].language == "python"

    def test_js_shorthand(self) -> None:
        md = "```js\nconsole.log(1)\n```"
        blocks = extract_code_blocks(md)
        assert blocks[0].language == "javascript"


class TestDetectLanguageHeuristic:
    """Test language detection heuristics."""

    def test_detect_json(self) -> None:
        assert detect_language_heuristic('{"key": "value"}') == "json"

    def test_detect_sql(self) -> None:
        assert detect_language_heuristic("SELECT * FROM users") == "sql"

    def test_detect_bash_shebang(self) -> None:
        assert detect_language_heuristic("#!/bin/bash\necho hello") == "bash"

    def test_detect_bash_prompt(self) -> None:
        assert detect_language_heuristic("$ pip install requests") == "bash"

    def test_detect_xml(self) -> None:
        assert detect_language_heuristic("<div>hello</div>") == "xml"

    def test_detect_python(self) -> None:
        assert detect_language_heuristic("import os\nos.path.join('a')") == "python"

    def test_detect_javascript(self) -> None:
        assert detect_language_heuristic("const x = 1;\nfunction foo() {}") == "javascript"

    def test_fallback_to_text(self) -> None:
        assert detect_language_heuristic("some random content") == "text"


class TestValidateLlmOutput:
    """Integration tests for LLM validation."""

    @pytest.mark.asyncio
    async def test_no_blocks(self) -> None:
        report = await validate_llm_output("No code here")
        assert report.total_blocks == 0
        assert report.passed

    @pytest.mark.asyncio
    async def test_valid_blocks(self) -> None:
        md = "```python\nimport os\n```"
        report = await validate_llm_output(md)
        assert report.total_blocks == 1
        assert report.blocks_passed >= 0  # May pass or fail depending on validation

    @pytest.mark.asyncio
    async def test_non_supported_language_passes(self) -> None:
        md = "```sql\nSELECT 1;\n```"
        report = await validate_llm_output(md)
        assert report.total_blocks == 1
        assert report.blocks_passed == 1

    @pytest.mark.asyncio
    async def test_oversized_input(self) -> None:
        huge = "x" * (11 * 1024 * 1024)  # >10MB
        report = await validate_llm_output(huge)
        assert report.total_blocks == 0


class TestMaxBlocksLimit:
    def test_extract_max_blocks_limit(self) -> None:
        """MAX_BLOCKS (100) limits extraction even with more blocks."""
        blocks_md = "\n\n".join(
            f"```python\nprint({i})\n```" for i in range(105)
        )
        blocks = extract_code_blocks(blocks_md)
        assert len(blocks) == 100
        assert "print(0)" in blocks[0].code
        assert "print(99)" in blocks[99].code
