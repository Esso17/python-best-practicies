# Contributing to Python Best Practices

Thank you for your interest in contributing! This repository aims to provide practical, runnable examples of Python best practices with real benchmarks.

## How to Contribute

### Setup Development Environment

Before contributing, set up your local environment:

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/python-best-practices.git
cd python-best-practices

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Adding a New Topic

1. **Create a new directory** under the root for your topic (e.g., `error-handling/`, `testing/`, `performance/`)

2. **Structure your topic directory**:
   ```
   your-topic/
   ├── README.md              # Topic overview
   ├── 01_example_name.py     # Numbered examples
   ├── 02_another_example.py
   └── requirements.txt       # Dependencies
   ```

3. **Follow the example format**:
   - Include ❌ BAD and ✅ GOOD code examples
   - Add inline comments explaining the "why"
   - Include runnable benchmarks when applicable
   - Demonstrate real-world performance differences

4. **Documentation requirements**:
   - Topic README with overview and learning objectives
   - Each example should be runnable standalone
   - Include expected benchmark results
   - Add links to authoritative sources

### Example Template

```python
"""
Python Best Practice: [Topic Name]

The Problem: [Brief explanation of the anti-pattern]

This example demonstrates [what you're showing].
"""

import time

# ❌ BAD: [What's wrong]
def bad_example():
    """
    Explanation of why this is problematic.
    """
    pass

# ✅ GOOD: [What's correct]
def good_example():
    """
    Explanation of why this is better.
    """
    pass

# Benchmark
def benchmark():
    """Compare performance"""
    start = time.perf_counter()
    bad_example()
    bad_time = time.perf_counter() - start

    start = time.perf_counter()
    good_example()
    good_time = time.perf_counter() - start

    print(f"❌ Bad: {bad_time:.3f}s")
    print(f"✅ Good: {good_time:.3f}s")
    print(f"Speedup: {bad_time/good_time:.1f}x")

if __name__ == "__main__":
    benchmark()
```

### Code Quality Standards

- **PEP 8 compliant**: Follow Python style guide
- **Type hints**: Use where appropriate
- **Docstrings**: Explain complex logic
- **Comments**: Focus on "why", not "what"
- **Runnable**: All examples must execute successfully
- **Dependencies**: Minimize external dependencies

### Submission Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b topic/your-topic-name`
3. **Add your examples** following the structure above
4. **Test your code**: Ensure all examples run successfully
5. **Update main README**: Add your topic to the navigation
6. **Submit a Pull Request** with:
   - Clear description of the topic
   - Why it's a best practice
   - Expected learning outcomes

### Review Criteria

Your contribution will be reviewed for:
- ✅ Correctness of best practices
- ✅ Code quality and style
- ✅ Clear explanations
- ✅ Runnable benchmarks
- ✅ Proper documentation
- ✅ Real-world applicability

## Questions?

Open an issue for:
- Topic suggestions
- Clarification on contribution guidelines
- Discussion of best practices

## Code of Conduct

- Be respectful and constructive
- Focus on technical merit
- Welcome newcomers
- Assume good intent

Thank you for helping make Python development better! 🐍
