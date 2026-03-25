# Python Best Practices 🐍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Practical, runnable Python code examples demonstrating best practices with real benchmarks.**

Each topic includes side-by-side ❌ BAD vs ✅ GOOD comparisons, detailed explanations, and performance benchmarks showing measurable improvements.

---

## 📚 Topics

### ✅ [Concurrency & Async/Await](concurrency/)
Learn proper async/await patterns, avoid blocking the event loop, and handle CPU vs I/O-bound work correctly.

**What you'll learn:**
- ❌ Common concurrency mistakes that freeze your application
- ✅ Proper async HTTP clients (`httpx` vs `requests`)
- ✅ `ProcessPoolExecutor` for CPU-bound work
- ✅ FastAPI patterns for AI services
- ✅ Advanced `asyncio.gather()` patterns

**Benchmarks:** 5-15x speedup with proper concurrency

[**→ Explore Concurrency Examples**](concurrency/)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/python-best-practices.git
cd python-best-practices

# Navigate to a topic
cd concurrency

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run examples
python 01_blocking_vs_async.py

# When done, deactivate
deactivate
```

## 🎯 Philosophy

This repository focuses on:

✅ **Runnable examples** - Every example executes and demonstrates the concept

✅ **Real benchmarks** - Show actual performance differences, not just theory

✅ **Side-by-side comparisons** - ❌ BAD vs ✅ GOOD code patterns

✅ **Practical applications** - Real-world scenarios, not toy examples

✅ **Clear explanations** - Understand the "why", not just the "what"

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Want to add a topic?**
1. Create a new directory for your topic
2. Add runnable examples with benchmarks
3. Include a comprehensive README
4. Submit a pull request

**Suggested topics:**
- Error handling & exceptions
- Testing best practices
- Performance optimization
- Security practices
- Code organization & architecture
- Database interactions
- API design patterns
- Memory management
- Logging & debugging

## 📖 Resources

Each topic includes references to authoritative sources:
- Official Python documentation
- PEPs (Python Enhancement Proposals)
- Industry best practices
- Real-world case studies

## 🌟 Why This Repository?

Most Python tutorials show you **what** to do. This repository shows you:
- **Why** certain patterns are better
- **How much** better (with benchmarks)
- **When** to use each approach
- **What** mistakes to avoid

Perfect for:
- 🎓 Learning Python best practices
- 🔍 Code reviews and team standards
- 📊 Performance optimization
- 🏗️ Production-ready code patterns

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This repository compiles best practices from:
- Python official documentation
- Industry experts and tech blogs
- Real-world production experience
- Community feedback

---

**⭐ If you find this helpful, please star the repo!**

**🐛 Found an issue?** [Open an issue](../../issues)

**💡 Have a suggestion?** [Start a discussion](../../discussions)
