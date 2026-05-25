"""All constants and sample data for the benchmark suite."""

from __future__ import annotations

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE = "http://localhost:11434"
GEN_MODEL = "phi3.5:3.8b"
EMBED_MODEL = "nomic-embed-text:latest"
TIMEOUT = 60.0
N_TICKETS = 6
N_CHUNKS = 8
MAX_TOKENS = 10

# ── Simulate ──────────────────────────────────────────────────────────────────
N_SIM_CALLS = 20
SIM_LATENCY_MS = 100
SEM_LIMIT = 5
N_CPU_BATCHES = 8
CPU_WORKLOAD = 3_000_000
N_HTTP_CALLS = 10
HTTP_TIMEOUT = 10.0

# ── Sample data ───────────────────────────────────────────────────────────────
SUPPORT_TICKETS = [
    "The checkout button is completely broken — I can't complete my purchase!",
    "Your team resolved my billing issue within 2 hours. Absolutely outstanding!",
    "Package arrived 3 weeks late with no communication from your side.",
    "I love the new dashboard design — so much cleaner and faster.",
    "My API key stopped working overnight with no warning email.",
    "The documentation is clear and the onboarding is smooth. Great job!",
]

KNOWLEDGE_BASE = [
    (
        "kb_001",
        "Python's asyncio event loop runs coroutines concurrently on a single thread.",
    ),
    (
        "kb_002",
        "The GIL prevents multiple threads from executing Python bytecode simultaneously.",
    ),
    ("kb_003", "ProcessPoolExecutor spawns separate processes, each with its own GIL."),
    ("kb_004", "ThreadPoolExecutor is effective for I/O-bound blocking code."),
    (
        "kb_005",
        "FastAPI async def endpoints run on the event loop; sync def runs in a thread pool.",
    ),
    ("kb_006", "asyncio.Semaphore limits the number of concurrent coroutines."),
    ("kb_007", "httpx.AsyncClient reuses a single connection pool across requests."),
    (
        "kb_008",
        "loop.run_in_executor() offloads blocking calls without blocking the event loop.",
    ),
]

REVIEW_CODE = """def find_user(users, target_id):
    for user in users:
        if user["id"] == target_id:
            return user
    return None"""

REVIEW_MODELS = [GEN_MODEL, "mistral:latest"]
_REVIEW_PROMPT = (
    "Review this Python function in 15 words or fewer. "
    "Mention one improvement:\n```python\n{code}\n```"
)

RAG_QUERY = "How do I run CPU-intensive code without blocking FastAPI?"
