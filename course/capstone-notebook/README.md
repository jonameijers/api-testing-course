# Capstone: Testing the ShopSmart Customer Support System

Interactive Jupyter notebook for the GenAI API Testing course capstone exercise.

## Setup

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Launch the notebook
jupyter notebook 06-capstone-notebook.ipynb
```

## What's Inside

- **`06-capstone-notebook.ipynb`** — The main capstone notebook with guided exercises
- **`chatassist_sim/`** — Simulated ChatAssist API (no external services needed)
- **`test_helpers/`** — Lightweight test runner and assertion utilities
- **`shopmart_config.py`** — ShopSmart system configuration and constants

## No API Keys Required

The notebook uses a fully simulated ChatAssist API that runs in-process. It supports all four API modes (chat completion, structured output, tool calling, streaming), realistic error responses, and configurable non-determinism. No network access, API keys, or cloud services are needed.

## Prerequisites

- Python 3.8+
- Completion of Sessions 0-5 of the GenAI API Testing course
