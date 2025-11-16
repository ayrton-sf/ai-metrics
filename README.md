# 🤖 AIM - AI Metrics

A modular and extensible toolkit to **evaluate LLM outputs** using various metrics including **criteria-based evaluation**, **factual claim checking**, and **semantic similarity**, with support for multiple data backends like **web search**, **vector retrieval**, and **custom retrievers**.

> ⚠️ **WIP:** This toolkit is a work in progress. APIs, behaviors, and outputs are subject to change.

---

## 📋 Available Models

### LLM Models
- **OpenAI**
  - `gpt-4o`
  - `gpt-4.1`
  - `gpt-5`
  - `o3`
- **Anthropic**
  - `claude-3-5-sonnet-latest`
  - `claude-3-7-sonnet-latest`
  - `claude-sonnet-4-20250514`
  - `claude-sonnet-4-5-latest`
  - `claude-haiku-4-5-20251001`
  - `claude-opus-4-1-latest`

### Embedding Models
- **OpenAI**
  - `text-embedding-3-large`
  - `text-embedding-3-small`
  - `text-embedding-ada-002`
- **Voyage AI**
  - `voyage-3-large`
- **Anthropic**
  - `voyage-3.5`
  - `voyage-3.5-lite`

---

## 🚀 Quickstart

```python
from aim.metrics import Metrics
from aim.data_sources import DataSource

# 🔧 Initialize the Metrics class
metrics = Metrics(
    reference_id="my_test",
    llm_model="claude-haiku-4-5-20251001",
    llm_api_key="your-anthropic-key",
    embed_api_key="your-voyage-key",
    embed_model="voyage-ai"
)
```

### 🔧 Optional: Set Custom Thresholds

Override default thresholds at the class level:

```python
metrics = Metrics(
    reference_id="my_test",
    llm_model="claude-haiku-4-5-20251001",
    llm_api_key="your-anthropic-key",
    embed_api_key="your-voyage-key",
    embed_model="voyage-ai",
    claim_check_threshold=0.85,      # 85% instead of default 90%
    criteria_check_threshold=0.95,   # 95% instead of default 90%
    similarity_threshold=0.80        # 80% for semantic similarity
)
```

---

## ✅ Criteria Evaluation

Evaluate LLM outputs against custom criteria.

```python
assistant_response = """
# The impact of LLMs
Large Language Models (LLMs) such as GPT-4, Claude 3, and Gemini 1.5 are transforming the way we interact with technology.

## Capabilities of LLMs
These models understand and generate human-like text, supporting tasks from summarization to code generation.

## Popular LLMs in 2025
Current leading models include GPT-4o by OpenAI, Claude 3 by Anthropic, and Gemini 1.5 by Google DeepMind.
"""

# ✅ Basic usage with default threshold (90%)
result = metrics.criteria_check(
    content=assistant_response,
    criteria=[
        "The content should talk about LLMs",
        "The response should mention GPT-4o, Claude 3, and Gemini 1.5",
        "The content should have one title and two subtitles"
    ]
)

# ✅ Override threshold for this specific check
result = metrics.criteria_check(
    content=assistant_response,
    criteria=["The response should be helpful and accurate"],
    threshold=0.95  # Require 95% for this check
)

# Result format:
# {
#     "score": 100.0,
#     "content": "...",
#     "criteria": [
#         {"criterion": "...", "result": True},
#         {"criterion": "...", "result": True}
#     ]
# }
```

---

## 🧠 Semantic Similarity

Compare semantic similarity between a reference and candidate response using a reference-baseline-test workflow.

### Setting Reference

First, create your reference data by running with `aim set-reference`:

```python
# In your test file (e.g., test_conversation.py)
metrics = Metrics(
    reference_id="conversation_test",  # This determines the reference filename
    llm_model="claude-haiku-4-5-20251001",
    llm_api_key="your-key",
    embed_api_key="your-embed-key",
    embed_model="voyage-ai"
)

# Get a response from your chatbot/service
chatbot_response = await chatbot.ask("Show me apartments in Seattle")

metrics.similarity_score(
    candidate=chatbot_response,
    assertion_id="seattle_apartments_response"
)
```

Run with CLI:
```bash
aim set-reference -c aim.config.json
```

This saves to `aim_data/reference/conversation_test.json`:
```json
{
    "semantic_similarity": {
        "seattle_apartments_response": {
            "reference": "Here are some apartments in Seattle...",
            "scores": [],
            "mean": null,
            "std": null,
            "suggested_threshold": null
        }
    }
}
```

### Setting Baseline

Establish statistical baseline by running multiple times:

```bash
# Run 5-10 times to calculate mean, std, and suggested_threshold
aim set-baseline -c aim.config.json -r 10
```

Each iteration:
1. Executes your test
2. Compares candidate against reference
3. Accumulates scores in the reference file
4. Updates `mean`, `std`, and `suggested_threshold = mean - std`

Updated reference file after baseline:
```json
{
    "semantic_similarity": {
        "seattle_apartments_response": {
            "reference": "Here are some apartments in Seattle...",
            "scores": [0.92, 0.89, 0.91, 0.88, 0.90, ...],
            "mean": 0.90,
            "std": 0.015,
            "suggested_threshold": 0.885
        }
    }
}
```

### Testing with Assertions

Run tests with assertions against thresholds:

```python
# Your test uses the same pattern - get live response
chatbot_response = await chatbot.ask("Show me apartments in Seattle")

# ✅ Use suggested_threshold from baseline (0.885 in this case)
score = metrics.similarity_score(
    candidate=chatbot_response,
    assertion_id="seattle_apartments_response"
)

# ✅ Override with class-level threshold for all similarity checks
metrics = Metrics(
    reference_id="conversation_test",
    llm_model="claude-haiku-4-5-20251001",
    llm_api_key="your-key",
    embed_api_key="your-embed-key",
    embed_model="voyage-ai",
    similarity_threshold=0.85  # Use 85% instead of suggested_threshold
)

# ✅ Override threshold for this specific assertion only
score = metrics.similarity_score(
    candidate=chatbot_response,
    assertion_id="seattle_apartments_response",
    threshold=0.90  # Require 90% similarity for this check
)
```

Run with CLI:
```bash
aim test -c aim.config.json
```

If assertion fails, details are saved to `aim_data/failures/failures_<timestamp>.json`.

> **Note:** The `reference_id` in your `Metrics` class maps to the filename in `aim_data/reference/<reference_id>.json`.

---

## 🔍 Claim Checking

Verify factual consistency against various data sources using a pluggable retriever pattern.

### 🔌 With Custom Retriever (Recommended)

The toolkit accepts any async function that takes a query string and returns a list of strings:

```python
from aim.data_sources import DataSource

# Define your custom retriever
async def my_retriever(query: str) -> list[str]:
    # Your retrieval logic here (vector DB, API, etc.)
    results = await my_vector_db.search(query)
    return [doc.content for doc in results]

# ✅ Basic usage with default threshold (90%)
result = await metrics.claim_check(
    content=assistant_response,
    data_source=DataSource.RETRIEVER,
    retriever_request=my_retriever
)

# ✅ Override threshold for this specific check
result = await metrics.claim_check(
    content=assistant_response,
    data_source=DataSource.RETRIEVER,
    retriever_request=my_retriever,
    threshold=0.85  # Require 85% claim validity
)

# Result format:
# {
#     "total_score": 100.0,
#     "content": "...",
#     "claims": [
#         {"claim": "...", "validity": True, "reasoning": "..."},
#         {"claim": "...", "validity": True, "reasoning": "..."}
#     ]
# }
```

### 🌐 With Web URLs

```python
generated_content = """2025 has cemented the 'anything-goes' era of AI, with over $300 billion 
poured into rapid LLM development by tech giants and governments alike."""

result = await metrics.claim_check(
    content=generated_content,
    data_source=DataSource.WEB,
    urls=[
        "https://www.techinsights.org/reports/ai-trends-2025",
        "https://www.datasciencehub.com/articles/global-llm-developments"
    ]
)
```

### 🗄️ With SQL/MCP

```python
from mcp import StdioServerParameters

# Configure MCP server parameters
mcp_params = StdioServerParameters(
    command="uvx",
    args=["mcp-server-postgres", "postgresql://user:pass@localhost/db"]
)

result = await metrics.claim_check(
    content=assistant_response,
    data_source=DataSource.MCP,
    params=mcp_params
)
```

> ⚠️ **Note:** When using `DataSource.MCP`, the tool engages an **agentic loop** which leverages **MCP (Model Context Protocol)**.  
> MCP enables a **retrieval subagent** to:
> - Fetch table lists 🗂️  
> - Select relevant tables 📊  
> - Craft and run SQL queries dynamically 🔎  
> ✅ Supports any MCP server (PostgreSQL, SQLite, etc.)

---

## 📦 Supported Data Sources

- `DataSource.RETRIEVER` – pluggable custom retriever (recommended)
- `DataSource.WEB` – web-grounded evaluation  
- `DataSource.MCP` – structured data validation (via MCP, PostgreSQL default)

---

## 🖥️ CLI Usage

The toolkit includes a CLI for running tests with different execution modes.

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ai-metrics.git

# Install the package
pip install path/to/ai-metrics
```

### Configuration

In your test suite folder, create an `aim.config.json`:

```json
{
    "run": "pytest"
}
```

### Commands

#### 🧪 Run Tests (Assertion Mode)

Run your test suite with assertions enabled:

```bash
aim test -c aim.config.json
```

This executes your configured test command and asserts against thresholds. Failed assertions are saved to `aim_data/failures/failures_<timestamp>.json`.

#### 📋 Set Reference

Capture reference responses for similarity comparisons:

```bash
aim set-reference -c aim.config.json
```

Stores reference data in `aim_data/reference/<reference_id>.json`.

#### 📊 Set Baseline

Run tests multiple times to establish statistical baselines:

```bash
# Run 5 times to calculate mean, std, and suggested_threshold
aim set-baseline -c aim.config.json -r 5
```

Each iteration calculates similarity scores and updates statistics in the reference file.

#### 📈 Report Mode

Collect metrics without assertions (for CI/observability):

```bash
aim report -c aim.config.json
```

Aggregates scores across all metrics and saves to `aim_data/report/report_<timestamp>.json`.

### Example Workflow

```bash
# 1. Set your reference responses
aim set-reference -c aim.config.json

# 2. Establish baseline with multiple runs
aim set-baseline -c aim.config.json -r 10

# 3. Run tests with assertions
aim test -c aim.config.json

# 4. Generate reports for observability
aim report -c aim.config.json
```

---

## 🧪 Example Test

```python
import pytest
from aim.metrics import Metrics
from aim.data_sources import DataSource

@pytest.mark.asyncio
async def test_chatbot_response():
    metrics = Metrics(
        reference_id="conversation_test",
        llm_model="claude-haiku-4-5-20251001",
        llm_api_key="your-key",
        embed_api_key="your-embed-key",
        embed_model="voyage-ai",
        claim_check_threshold=0.85  # Custom class-level threshold
    )
    
    # Your retriever
    async def db_retriever(query: str) -> list[str]:
        response = await db_service.search(query)
        return [doc["content"] for doc in response["results"]]
    
    # Get response from your system
    response = await chatbot.ask("Show me apartments in Seattle")
    
    # ✅ Check semantic similarity
    metrics.similarity_score(
        candidate=response,
        assertion_id="seattle_response"
    )
    
    # ✅ Verify claims against vector DB
    await metrics.claim_check(
        content=response,
        data_source=DataSource.RETRIEVER,
        retriever_request=db_retriever,
        threshold=0.90  # Override for this check
    )
    
    # ✅ Validate against criteria
    metrics.criteria_check(
        content=response,
        criteria=[
            "Response should mention apartments",
            "Response should reference Seattle",
            "Response should be helpful and professional"
        ]
    )
```

---

## 🎯 Threshold Hierarchy

Thresholds can be set at three levels (highest priority first):

1. **Call-level** – passed directly to the metric method
2. **Class-level** – set during `Metrics` initialization  
3. **Default** – from `ExecutionMode.default_thresholds` (90% for claim/criteria) or baseline statistics (for similarity)

```python
# Default threshold (90%)
result = metrics.criteria_check(content, criteria)

# Class-level threshold (85%)
metrics = Metrics(..., criteria_check_threshold=0.85)

# Call-level threshold (95%) - highest priority
result = metrics.criteria_check(content, criteria, threshold=0.95)
```
