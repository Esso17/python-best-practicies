# Python Concurrency Best Practices with Benchmarks

Comprehensive examples demonstrating Python async/await best practices based on [The Concurrency Mistake Hiding in Your FastAPI AI Services](https://jamwithai.substack.com/p/the-concurrency-mistake-hiding-in).

## 🎯 Key Concepts

### The Core Problem
Using `async def` without understanding the contract. **Blocking operations in async functions freeze the event loop**, queuing all other requests behind them.

### I/O-Bound vs Compute-Bound
- **I/O-bound** (async helps): External APIs, databases, file I/O
- **Compute-bound** (async doesn't help): Local inference, embeddings, heavy calculations

## 📚 Examples

### [01_blocking_vs_async.py](01_blocking_vs_async.py)
**What it demonstrates:**
- ❌ Blocking `requests` library in async functions
- ✅ Proper async HTTP with `httpx`
- Live benchmarks showing 5x+ speedup

**Key takeaway:** Never use synchronous I/O in `async def` functions.

```python
# ❌ BAD - Blocks event loop
async def fetch_bad(url):
    response = requests.get(url)  # Blocks!
    return response.json()

# ✅ GOOD - Yields control
async def fetch_good(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

**Run it:**
```bash
python 01_blocking_vs_async.py
```

---

### [02_compute_bound_tasks.py](02_compute_bound_tasks.py)
**What it demonstrates:**
- Why `async/await` doesn't help CPU-bound work
- Why `ThreadPoolExecutor` fails (GIL)
- ✅ Using `ProcessPoolExecutor` to bypass GIL
- Benchmarks showing 4x+ speedup with multiple cores

**Key takeaway:** CPU-bound work requires `ProcessPoolExecutor`, not async/await.

```python
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

async def compute(data):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_compute, data)
    return result
```

**Run it:**
```bash
python 02_compute_bound_tasks.py
```

---

### [03_fastapi_patterns.py](03_fastapi_patterns.py)
**What it demonstrates:**
- Three architectural patterns for FastAPI AI services
- Proper model loading in `lifespan` (not endpoints)
- Parallel guardrails with early cancellation
- Production-ready patterns

**Three Levels:**

**Level 1: External APIs (I/O-bound)**
```python
@app.get("/generate")
async def generate(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.openai.com/...", ...)
        return response.json()
```

**Level 2: Local Inference (CPU-bound)**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model at startup
    AppState.model = load_model()
    AppState.executor = ProcessPoolExecutor(max_workers=2)
    yield
    AppState.executor.shutdown()

@app.post("/generate")
async def generate(prompt: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(AppState.executor, inference, prompt)
    return {"response": result}
```

**Level 3: Production Scale**
```python
@app.post("/generate")
async def generate(prompt: str):
    # Externalize to vLLM/TGI/Triton
    async with httpx.AsyncClient() as client:
        response = await client.post("http://vllm-server:8000/...", ...)
        return response.json()
```

**Run it:**
```bash
uvicorn 03_fastapi_patterns:app_level2 --reload
```

---

### [04_asyncio_gather_patterns.py](04_asyncio_gather_patterns.py)
**What it demonstrates:**
- 7 essential `asyncio.gather()` patterns
- Error handling with `return_exceptions=True`
- Timeouts, rate limiting, early exit
- Benchmarks showing concurrent vs sequential execution

**Patterns covered:**
1. Basic concurrent execution
2. Error handling strategies
3. Dynamic task lists
4. Mixed dependencies
5. Timeout handling
6. Rate limiting with Semaphore
7. Early exit with `as_completed`

**Key patterns:**

```python
# Error handling
results = await asyncio.gather(
    task1(), task2(), task3(),
    return_exceptions=True  # Don't fail all on one error
)

# Rate limiting
semaphore = asyncio.Semaphore(3)
async def limited_task():
    async with semaphore:
        return await expensive_operation()

# Timeout
results = await asyncio.wait_for(
    asyncio.gather(task1(), task2()),
    timeout=5.0
)
```

**Run it:**
```bash
python 04_asyncio_gather_patterns.py
```

## 🚀 Quick Start

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run individual examples
python 01_blocking_vs_async.py
python 02_compute_bound_tasks.py
python 03_fastapi_patterns.py
python 04_asyncio_gather_patterns.py

# When done
deactivate
```

## 📊 Expected Benchmark Results

### 01_blocking_vs_async.py
```
❌ BAD: Blocking requests in async function
   Total time: 5.23s

✅ GOOD: Proper async/await with httpx
   Total time: 1.05s

SPEEDUP: 5.0x faster with async!
```

### 02_compute_bound_tasks.py
```
❌ BAD: CPU-bound work directly in async function
   Total time: 8.45s

⚠️  STILL BAD: ThreadPoolExecutor (doesn't help CPU work)
   Total time: 8.52s

✅ GOOD: ProcessPoolExecutor (bypasses GIL)
   Total time: 2.31s

SPEEDUP: 3.7x faster with ProcessPoolExecutor!
```

### 04_asyncio_gather_patterns.py
```
❌ Sequential: 1.000s
✅ Concurrent: 0.065s

SPEEDUP: 15.4x faster!
```

## 🎓 Key Lessons

### 1. Never Block the Event Loop
```python
# ❌ NEVER DO THIS
async def endpoint():
    response = requests.get(url)  # Blocks!
    time.sleep(1)  # Blocks!
    heavy_compute()  # Blocks!
```

### 2. Choose the Right Tool

| Workload Type | Solution | Example |
|--------------|----------|---------|
| I/O-bound | `async/await` | HTTP calls, database queries |
| CPU-bound | `ProcessPoolExecutor` | Local inference, embeddings |
| Production Scale | External servers | vLLM, TGI, Triton |

### 3. Load Models at Startup
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Load once at startup
    AppState.model = load_model()
    yield
    # Cleanup
```

### 4. Run Guardrails in Parallel
```python
# Start both concurrently
safety_task = asyncio.create_task(check_safety(prompt))
inference_task = asyncio.create_task(run_inference(prompt))

if not await safety_task:
    inference_task.cancel()  # Early cancellation
    raise HTTPException(400, "Unsafe")

return await inference_task
```

## 📖 Reference

Based on the article: [The Concurrency Mistake Hiding in Your FastAPI AI Services](https://jamwithai.substack.com/p/the-concurrency-mistake-hiding-in)

## 🔑 Quick Reference

```python
# I/O-bound: Use async
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# CPU-bound: Use ProcessPoolExecutor
executor = ProcessPoolExecutor(max_workers=4)
result = await loop.run_in_executor(executor, cpu_task, data)

# Concurrent operations
results = await asyncio.gather(task1(), task2(), task3())

# Error handling
results = await asyncio.gather(*tasks, return_exceptions=True)

# Rate limiting
semaphore = asyncio.Semaphore(10)
async with semaphore:
    await operation()

# Timeout
await asyncio.wait_for(operation(), timeout=5.0)
```

## 📝 License

MIT
