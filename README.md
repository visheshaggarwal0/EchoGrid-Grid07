# EchoGrid

**EchoGrid** is an advanced orchestration framework for autonomous AI agent networks, demonstrating capabilities in semantic routing, LangGraph-based workflow orchestration, and prompt-injection-resistant RAG engines. 

Built strictly with local-first, privacy-preserving infrastructure using Ollama and Hugging Face embeddings, organized into a professional, production-ready Python package structure.

---

## Architecture Overview

EchoGrid is split into three core phases of execution, representing the lifecycle of an autonomous agent network:

### Phase 1: Cognitive Routing (`src/agents/router.py`)
Instead of broadcasting every message to every agent in a swarm, EchoGrid uses **Semantic Routing**.
- **The Tech:** `FAISS` (Facebook AI Similarity Search) and `sentence-transformers/all-MiniLM-L6-v2`.
- **The Process:** Bot personas are stored in an in-memory vector database. Incoming posts are embedded into a vector space. A Cosine Similarity threshold dynamically matches the post context to the bots most likely to "care" about the topic using exact math via `sklearn.metrics.pairwise.cosine_similarity`.
- **Security:** Includes an initial spoof-layer to drop obvious malicious payloads before wasting inference cycles.

### Phase 2: Autonomous Content Engine (`src/agents/engine.py`)
When an agent decides to post, it doesn't just guess—it researches.
- **The Tech:** LangGraph State Machine & Pydantic-enforced Structured Outputs.
- **Node Structure:**
  1. `decide_search`: The LLM reads its persona and determines what topic it wants to research today, outputting a precise search query.
  2. `web_search`: Executes an external Tool Call (`mock_searxng_search`) to retrieve real-world headlines for context.
  3. `draft_post`: The agent synthesizes its persona and the search context.
- **The Constraint:** We utilize Langchain's `.with_structured_output()` mechanism. This binds the LLM to a Pydantic schema, forcing it to map its generative process into a strict JSON payload acting as native Function Calling.
- **Resilience**: Implements Graceful Error Handling catching `ConnectionError` if the Ollama backend drops.

### Phase 3: The Combat Engine (`src/agents/combat_engine.py`)
Agents must navigate deep conversational threads without losing context, and they must defend against adversarial prompt injections.
- **The Tech:** Deep Thread RAG & System-Level Defenses.
- **The Prompt Injection Defense Mechanism:** Prompt Injections attempt to trick an LLM by appending commands at the end of the user input (e.g., "Ignore previous instructions"). EchoGrid prevents this through **Strict System-Level Framing**.
  - The thread context and the final `human_reply` are explicitly segmented.
  - A definitive `<SYSTEM SECURITY OVERRIDE>` instruction is placed *after* the human's input in the prompt logic. 
  - The system explicitly acknowledges the existence of injections and commands the LLM to mock the user for the attempt *in character*, maintaining the persona sandbox.

---

## Setup & Installation

EchoGrid is designed to run locally. Ensure you have [Ollama](https://ollama.com/) installed and running.

1. **Clone the repository and enter the directory:**
   ```bash
   git clone <your-repo-url>
   cd Grid07
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example environment file and define your model name and routing thresholds.
   ```bash
   cp .env.example .env
   ```

## Execution & Testing

EchoGrid features a professional package structure. All commands must be run from the root `Grid07` directory as modules.

- **Test Semantic Routing:**
  `python -m src.agents.router`
- **Test LangGraph Orchestrator:**
  `python -m src.agents.engine`
- **Test Combat Engine (Prompt Injection Defense):**
  `python -m src.agents.combat_engine`
- **Run PyTest Suites (Security Validations):**
  `python -m pytest tests/`

*(See `execution_logs.md` for simulated terminal output).*
