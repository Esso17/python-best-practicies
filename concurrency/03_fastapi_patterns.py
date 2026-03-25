"""
Python Best Practice: FastAPI Concurrency Patterns for AI Services

Three architectural levels for handling different workload types:
1. External APIs (I/O-bound): Use async clients
2. Local Inference (CPU-bound): Use ProcessPoolExecutor
3. Production Scale: Externalize to dedicated inference servers

Based on: https://jamwithai.substack.com/p/the-concurrency-mistake-hiding-in
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100


class GenerateResponse(BaseModel):
    response: str
    latency_ms: float


# Simulate heavy model inference
def run_local_inference(prompt: str, max_tokens: int) -> str:
    """Simulates local LLM inference (CPU-bound)"""
    time.sleep(0.5)  # Simulate model computation
    return f"Generated response for: {prompt[:50]}..."


def compute_embeddings(text: str) -> List[float]:
    """Simulates embedding generation (CPU-bound)"""
    time.sleep(0.2)
    return [0.1, 0.2, 0.3] * 100


# =============================================================================
# ❌ LEVEL 0: ANTI-PATTERN - Blocking calls in async endpoints
# =============================================================================

app_bad = FastAPI(title="Bad Example - Blocking in Async")


@app_bad.get("/generate-bad")
async def generate_bad(prompt: str):
    """
    PROBLEM: Synchronous blocking call freezes the event loop.
    All other requests queue behind this one.
    """
    import requests  # Synchronous library

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        json={"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]},
        headers={"Authorization": "Bearer sk-xxx"},
        timeout=30,
    )
    return response.json()


# =============================================================================
# ✅ LEVEL 1: EXTERNAL APIs - Async HTTP Clients (I/O-bound)
# =============================================================================

app_level1 = FastAPI(title="Level 1 - External APIs")


@app_level1.get("/generate")
async def generate_external(prompt: str) -> GenerateResponse:
    """
    GOOD: Async HTTP client for external API calls.
    Event loop can handle other requests during network wait.
    """
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]},
            headers={"Authorization": "Bearer sk-xxx"},
            timeout=60.0,
        )
        result = response.json()

    latency = (time.perf_counter() - start) * 1000
    return GenerateResponse(
        response=result.get("choices", [{}])[0].get("message", {}).get("content", ""),
        latency_ms=latency,
    )


# =============================================================================
# ✅ LEVEL 2: LOCAL INFERENCE - ProcessPoolExecutor (CPU-bound)
# =============================================================================


# Global state for model and executor
class AppState:
    model = None
    executor: ProcessPoolExecutor = None


@asynccontextmanager
async def lifespan_level2(app: FastAPI):
    """
    BEST PRACTICE: Load models during startup, not on first request.
    Avoids cold-start penalty on every request.
    """
    # Startup
    print("Loading model at startup...")
    AppState.model = "loaded-model-placeholder"  # In reality: load your model here
    AppState.executor = ProcessPoolExecutor(max_workers=2)
    print("Model loaded and executor initialized")

    yield

    # Shutdown
    print("Shutting down executor...")
    AppState.executor.shutdown(wait=True)


app_level2 = FastAPI(title="Level 2 - Local Inference", lifespan=lifespan_level2)


@app_level2.post("/generate")
async def generate_local(request: GenerateRequest) -> GenerateResponse:
    """
    GOOD: CPU-bound work offloaded to ProcessPoolExecutor.
    Event loop remains free for other requests.
    """
    start = time.perf_counter()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        AppState.executor, run_local_inference, request.prompt, request.max_tokens
    )

    latency = (time.perf_counter() - start) * 1000
    return GenerateResponse(response=result, latency_ms=latency)


# =============================================================================
# ✅ LEVEL 3: PRODUCTION SCALE - External Inference Servers
# =============================================================================

app_level3 = FastAPI(title="Level 3 - Production Scale")


@app_level3.post("/generate")
async def generate_production(request: GenerateRequest) -> GenerateResponse:
    """
    BEST FOR SCALE: Offload inference to dedicated servers.
    - vLLM: High-throughput LLM serving
    - TGI (Text Generation Inference): Optimized inference
    - Triton: NVIDIA's inference server

    FastAPI becomes a thin async layer making API calls.
    """
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        # Call dedicated inference server
        response = await client.post(
            "http://vllm-server:8000/v1/completions",
            json={
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": 0.7,
            },
            timeout=60.0,
        )
        result = response.json()

    latency = (time.perf_counter() - start) * 1000
    return GenerateResponse(
        response=result.get("choices", [{}])[0].get("text", ""), latency_ms=latency
    )


# =============================================================================
# ✅ ADVANCED PATTERN: Parallel Guardrails with Early Cancellation
# =============================================================================


async def check_content_safety(prompt: str) -> bool:
    """Simulate async content moderation check"""
    await asyncio.sleep(0.1)
    # In reality: call moderation API
    return "unsafe" not in prompt.lower()


async def run_inference_async(prompt: str) -> str:
    """Wrapper for inference that can be cancelled"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        AppState.executor, run_local_inference, prompt, 100
    )


@app_level2.post("/generate-with-guardrails")
async def generate_with_guardrails(request: GenerateRequest) -> GenerateResponse:
    """
    ADVANCED: Run guardrails in parallel with inference.
    Cancel inference immediately if validation fails.
    Reduces latency on valid requests.
    """
    start = time.perf_counter()

    # Start both tasks concurrently
    safety_task = asyncio.create_task(check_content_safety(request.prompt))
    inference_task = asyncio.create_task(run_inference_async(request.prompt))

    try:
        # Wait for safety check
        is_safe = await safety_task

        if not is_safe:
            # Cancel inference immediately
            inference_task.cancel()
            raise HTTPException(status_code=400, detail="Unsafe content detected")

        # Safety check passed, wait for inference
        result = await inference_task

        latency = (time.perf_counter() - start) * 1000
        return GenerateResponse(response=result, latency_ms=latency)

    except asyncio.CancelledError:
        raise HTTPException(status_code=400, detail="Request cancelled") from None


# =============================================================================
# BENCHMARK HELPER
# =============================================================================


async def benchmark_endpoint(url: str, num_requests: int = 10):
    """Benchmark an endpoint with concurrent requests"""
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()

        tasks = [
            client.get(f"{url}?prompt=test_prompt_{i}") for i in range(num_requests)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.perf_counter() - start
        success = sum(1 for r in responses if not isinstance(r, Exception))

        print(f"URL: {url}")
        print(f"Requests: {num_requests}")
        print(f"Success: {success}/{num_requests}")
        print(f"Total time: {duration:.2f}s")
        print(f"Avg latency: {duration/num_requests*1000:.0f}ms")
        print(f"Throughput: {num_requests/duration:.1f} req/s\n")


if __name__ == "__main__":
    print(
        """
FastAPI Concurrency Patterns Summary:
=====================================

❌ Level 0 (BAD):
   - Blocking sync calls in async functions
   - Freezes event loop

✅ Level 1 (External APIs):
   - Use httpx.AsyncClient for I/O-bound work
   - Handles 100+ concurrent requests easily

✅ Level 2 (Local Inference):
   - Use ProcessPoolExecutor for CPU-bound work
   - Load models in lifespan, not endpoints
   - Run guardrails in parallel

✅ Level 3 (Production):
   - Externalize to vLLM/TGI/Triton
   - FastAPI as thin async layer
   - Best for high-scale deployments

Run with: uvicorn 03_fastapi_patterns:app_level2 --reload
"""
    )
