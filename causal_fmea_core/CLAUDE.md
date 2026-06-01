# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EdgeThemis** — a causal reasoning engine that extracts causal graphs from text, validates them using graph theory (d-separation, cycle detection), scores edges with FMEA (Failure Mode and Effects Analysis), and uses a self-reflection loop where the LLM judges its own outputs against common sense.

The system is a hybrid Python/Rust codebase. Rust handles performance-critical graph algorithms (Kahn cycle detection, Bayesian ball d-separation) exposed to Python via PyO3. Python orchestrates the LLM pipeline using LangGraph.

## Build & Run Commands

**Build the Rust extension (required before running Python code):**
```bash
maturin develop --release
```

**Start the local LLM inference server (required for the pipeline):**
```bash
cd scripts && bash run_llama_server.sh
```
Requires `llama-server` (from llama.cpp) on PATH and a Qwen 2.5 GGUF model at `../../qwen2.5-3b-q4.gguf` relative to `scripts/`.

**Run the main pipeline:**
```bash
cd python/causal_fmea && python app.py
```

**Run the ablation comparison demo (configs A/B/C side-by-side):**
```bash
cd python/causal_fmea && python demo_compare.py
```

**Run Python test snippets:**
```bash
cd testpy && python <filename>.py
```

## Architecture

### Rust Core (`src/`)

- **`lib.rs`** — PyO3 module entry point. Defines `CausalParadigmEngine` (the main Python-facing class) with string interning pool, graph injection, health checks, and d-separation claim extraction. Also re-exports `FmeaScore`.
- **`dag.rs`** — `CompactCausalGraph`: adjacency-list DAG with dynamic capacity expansion. Nodes are integer IDs mapped through the interner.
- **`algorithms.rs`** — `CausalAlgorithms`: static methods for `kahn_cycle_detect` (topological sort cycle detection) and `is_d_separated` (Bayesian ball algorithm for d-separation testing).
- **`fmea_evaluator.rs`** — `FmeaScore`: PyO3 class with S/O/D fields (severity, occurrence, detection, 1-10). RPN formula: `100*S + 10*O + D`.

### Python Pipeline (`python/causal_fmea/`)

- **`agent_state_machine.py`** — Pydantic models (`CausalEdge`, `ExtractedGraph`, `ReflectorVerdict`) and the `CausalAgentState` TypedDict that flows through LangGraph.
- **`nodes.py`** — Three LangGraph node functions:
  - `generate_graph_node`: calls local LLM (via OpenAI-compatible API on port 8080) to extract structured causal graph from text
  - `validate_graph_node`: FFI into Rust for cycle detection + d-separation claim extraction + FMEA RPN alerting
  - `reflector_node`: LLM judges whether d-separation claims are common-sense violations
- **`app.py`** — LangGraph state machine assembly. Wiring: START → generate → validate → (route: retry/reflector/end) → reflector → (route: retry/end). Physical fuse at 3 interception attempts.
- **`context_guard.py`** — `AgentContext` context manager for Rust engine lifecycle and memory cleanup.
- **`demo_compare.py`** — Ablation study comparing three configs: pure LLM, LLM+Schema+Rust validation, full EdgeThemis with reflection loop.

### Key Design Decisions

- **String interning**: Rust side uses `IndexSet<String>` behind `Arc<Mutex<...>>` for deduplication and O(1) ID lookup. Python sends string pairs; Rust converts to integer IDs for graph operations.
- **LLM communication**: Uses OpenAI-compatible API (`openai` Python client) pointing at `llama-server` on localhost:8080. Not using `llama-cpp-python` bindings — the C++ server manages VRAM independently.
- **JSON Schema enforcement**: LLM outputs are constrained via `json_schema` response format matching Pydantic model schemas.
- **Self-correction loop**: When Rust detects violations (cycles or d-separation issues), the interception report is fed back to the generator LLM as a "system warning" for up to 3 retries.
- **FMEA scoring**: Each causal edge carries S/O/D scores (1-10). RPN > 500 or S >= 9 triggers high-risk alerts.

## Dependencies

- **Rust**: `pyo3` 0.20.2 (with `extension-module`, `abi3-py310`), `indexmap` 2.1.0
- **Python**: `langgraph`, `openai`, `pydantic`, `causal_fmea_core` (the compiled Rust extension)
- **External**: `llama-server` (llama.cpp) for local LLM inference
- **Build tool**: `maturin` (>=1.13)
