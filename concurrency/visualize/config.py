"""Constants, sample data and colour palette for the visualiser."""

OLLAMA = "http://localhost:11434"
GEN_MODEL = "phi3.5:3.8b"
EMBED_MODEL = "nomic-embed-text:latest"
TIMEOUT = 60.0

# Colour palette — consistent across all figures
C = {
    "seq": "#E74C3C",  # red    — sequential (slow)
    "thread": "#3498DB",  # blue   — threading
    "async": "#2ECC71",  # green  — asyncio (fast I/O)
    "proc": "#9B59B6",  # purple — multiprocessing (fast CPU)
    "bg": "#F8F9FA",
    "grid": "#DEE2E6",
    "text": "#212529",
}

TICKETS = [
    "Checkout button is broken — I can't complete my order!",
    "Your team resolved my billing issue in 2 hours. Outstanding!",
    "Package arrived 3 weeks late with zero communication.",
    "Love the new dashboard — much cleaner and faster.",
    "My API key stopped working overnight. No warning email.",
    "Docs are clear and onboarding is smooth. Great job!",
]

CHUNKS = [
    "asyncio event loop runs coroutines concurrently on a single thread.",
    "The GIL prevents multiple threads from executing Python bytecode at once.",
    "ProcessPoolExecutor spawns separate processes, each with its own GIL.",
    "ThreadPoolExecutor helps I/O-bound blocking code by releasing the GIL on waits.",
    "FastAPI uses an async engine; async endpoints run on the event loop.",
    "asyncio.Semaphore limits the number of concurrent coroutines.",
    "httpx.AsyncClient reuses one connection pool across all concurrent requests.",
    "loop.run_in_executor() offloads blocking calls without blocking the event loop.",
]
