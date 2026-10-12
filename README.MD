# Local Code AI

> A lightweight, local-first AI coding agent designed to run AI-assisted development directly on consumer hardware.

Local Code AI is an open-source experiment focused on building a **privacy-friendly, offline-capable coding assistant** that can understand a codebase, interact with project files, execute controlled tools, and use local language models.

The project is being built with a strong focus on:

- 🖥️ Local-first AI inference
- 🔒 Security and permission boundaries
- 🧠 Codebase understanding
- ⚡ Hardware-efficient execution
- 🛠️ Controlled tool execution
- 🧪 Verification and testing
- 🌐 Open-source development

---

## Current Status

**Development stage:** Active development 🚧

The core local inference and agent infrastructure is already functional.

### Implemented

- Local GGUF model inference through `llama.cpp`
- Qwen2.5-Coder support
- GPU acceleration through Vulkan
- CPU fallback support
- Configurable model/runtime settings
- Resource monitoring
- Inference performance measurement
- Python code extraction and syntax verification
- Secure project file reading/writing
- Permission-controlled tool execution
- Secure shell execution
- Tool registry and validation
- Model-generated tool requests
- Multi-step tool execution loop
- Codebase scanning
- Codebase file reading
- Code chunking
- Offline keyword-based retrieval
- Python symbol extraction
- Symbol-aware codebase retrieval
- Codebase context injection
- Context selection for repository-related questions

---

## Architecture

The project follows a simple principle:

```text
                 ┌────────────────────┐
                 │     User Request   │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │    Agent Layer     │
                 └─────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     ┌────────────────┐          ┌─────────────────┐
     │ Local Inference│          │ Codebase        │
     │     Engine     │          │ Intelligence    │
     └───────┬────────┘          └────────┬────────┘
             │                            │
             ▼                            ▼
        Local LLM                 Repository Context
             │
             ▼
     ┌────────────────┐
     │ Tool Requests  │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Validation &   │
     │ Permissions    │
     └───────┬────────┘
             │
             ▼
     ┌────────────────┐
     │ Tool Executor  │
     └────────────────┘
```

The architecture intentionally separates **model intelligence from system authority**.

The model can propose an action, but the application decides whether that action is valid and permitted.

---

## Core Principle

> **The LLM proposes. The system validates.**

Local Code AI is designed so that generated output is not automatically trusted.

Tool requests pass through:

```text
Model
  ↓
Parser
  ↓
Validator
  ↓
Permission Check
  ↓
Tool Executor
  ↓
Result
  ↓
Model
```

This provides a foundation for building safer autonomous coding workflows.

---

## Technology Stack

### Language

- Python 3.11+

### Local AI

- `llama.cpp`
- GGUF models
- Qwen2.5-Coder

### Runtime

- Vulkan GPU acceleration
- CPU fallback

### Current Python Dependencies

- PyYAML
- psutil

### Development

- Git
- GitHub
- pytest

---

## Hardware

The project is being developed and tested on consumer hardware rather than a dedicated AI server.

Current development machine:

```text
CPU: AMD Ryzen 5 5600H
GPU: NVIDIA GeForce GTX 1650 4GB
RAM: 8GB
```

The goal is to keep the system lightweight enough to remain useful on modest hardware.

Performance will vary significantly depending on the hardware, model, quantization, context size, and runtime configuration.

---

## Project Structure

```text
local-code-ai/
│
├── app/
│   ├── agent/
│   │   ├── context_selector.py
│   │   ├── codebase_agent.py
│   │   ├── codebase_context.py
│   │   ├── prompt.py
│   │   └── tool_agent.py
│   │
│   ├── codebase/
│   │   ├── chunker.py
│   │   ├── indexer.py
│   │   ├── reader.py
│   │   ├── retriever.py
│   │   ├── scanner.py
│   │   └── symbols.py
│   │
│   ├── core/
│   │   ├── benchmark.py
│   │   ├── config.py
│   │   └── resources.py
│   │
│   ├── inference/
│   │   └── engine.py
│   │
│   ├── tools/
│   │   ├── base.py
│   │   ├── executor.py
│   │   ├── files.py
│   │   ├── permissions.py
│   │   ├── parser.py
│   │   ├── registry.py
│   │   ├── request.py
│   │   ├── result.py
│   │   ├── result_formatter.py
│   │   ├── shell.py
│   │   └── validation.py
│   │
│   └── verification/
│       ├── code.py
│       └── extractor.py
│
├── config/
│   └── config.yaml
│
├── tests/
│
├── models/
│   └── (local GGUF models)
│
├── requirements.txt
└── README.md
```

---

## Running Locally

Clone the repository:

```bash
git clone <repository-url>
cd rebelions-resolve
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the local model and `llama.cpp` executable in:

```text
config/config.yaml
```

Then run:

```bash
python -m app.main
```

---

## Models

Local Code AI is designed to work with GGUF-compatible local models through `llama.cpp`.

The current development model is:

```text
Qwen2.5-Coder-3B-Instruct
Quantization: Q4_K_M
Format: GGUF
```

Model files are intentionally **not stored in this repository**.

Users should download their chosen compatible model separately and configure its path locally.

---

## Security Philosophy

Local Code AI is being designed around explicit authority boundaries.

The project avoids treating model output as trusted instructions.

For example:

```text
LLM says:
"Execute this command."

        ↓

System validates request

        ↓

Permission policy checked

        ↓

Tool executes only if permitted
```

This approach will become increasingly important as the project evolves toward more autonomous coding capabilities.

---

## Roadmap

### Phase 1 — Local Inference
- [x] Local model execution
- [x] GGUF support
- [x] GPU acceleration
- [x] Runtime configuration
- [x] Performance measurement

### Phase 2 — Coding Agent
- [x] Tool system
- [x] File operations
- [x] Shell execution
- [x] Permission system
- [x] Tool request parsing
- [x] Multi-step tool loop

### Phase 3 — Codebase Intelligence
- [x] Repository scanning
- [x] File reading
- [x] Chunking
- [x] Retrieval
- [x] Symbol extraction
- [x] Symbol-aware retrieval
- [x] Context selection

### Phase 4 — Advanced Code Understanding
- [ ] Better semantic retrieval
- [ ] Dependency awareness
- [ ] Cross-file relationships
- [ ] Improved repository context
- [ ] Incremental indexing

### Phase 5 — Reliable Coding Actions
- [ ] Code editing
- [ ] Patch generation
- [ ] Diff validation
- [ ] Automatic test execution
- [ ] Failure recovery

### Phase 6 — Safety & Reliability
- [ ] Stronger command restrictions
- [ ] Tool sandboxing
- [ ] Resource-aware execution
- [ ] Failure recovery
- [ ] Security testing

### Phase 7 — Performance
- [ ] Hardware detection
- [ ] Model routing
- [ ] Context optimization
- [ ] Memory optimization
- [ ] Faster inference workflows

### Phase 8 — Developer Interface
- [ ] Interactive terminal interface
- [ ] Editor integration
- [ ] Project dashboard
- [ ] Human approval controls

### Phase 9 — Evaluation
- [ ] Automated test suite expansion
- [ ] Agent benchmarks
- [ ] Code-generation evaluations
- [ ] Regression tests

### Phase 10 — Open Source
- [ ] CI/CD
- [ ] Documentation
- [ ] Contribution guidelines
- [ ] Issue templates
- [ ] Release process
- [ ] First public release

---

## Development Philosophy

Local Code AI is developed incrementally:

```text
LEARN
  ↓
IMPLEMENT
  ↓
TEST
  ↓
BREAK IT
  ↓
FIX IT
  ↓
COMMIT
  ↓
PUSH
  ↓
NEXT STEP
```

The goal is not simply to build another chatbot.

The goal is to understand and engineer the systems required to build a reliable local AI coding environment from the ground up.

---

## Contributing

The project is currently under active development.

Contribution guidelines will be added as the architecture stabilizes.

Ideas, issues, experiments, and improvements are welcome.

---

## License

License information will be added before the first public release.