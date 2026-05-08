# EchoGrid

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

**EchoGrid** is an advanced orchestration framework for autonomous AI agent networks, demonstrating capabilities in semantic routing, LangGraph-based workflow orchestration, and prompt-injection-resistant RAG engines. 

<img width="959" height="539" alt="Screenshot 2026-05-08 185812" src="https://github.com/user-attachments/assets/ec03a8e7-2ac0-46a6-8d30-97575b2aa154" />

<img width="1920" height="1080" alt="Screenshot (67)" src="https://github.com/user-attachments/assets/c607159f-877d-441e-b7b0-7cedf99d89bf" />

Built strictly with local-first, privacy-preserving infrastructure using Ollama and Hugging Face embeddings, organized into a professional, production-ready Python package structure.

## Key Features
- **Centralized Persona Management:** All agents operate from a single source of truth (`src/core/personas.py`).
- **Hybrid Vector Routing:** Combines FAISS retrieval with strict Scikit-Learn mathematical scoring.
- **Agentic Workflows:** LangGraph state machines with Pydantic-enforced structured outputs.
- **Adversarial Resilience:** Context Window RAG fortified with XML Demarcation and strict IF/ELSE logic against prompt injection.
- **Production-Ready Structure:** Implements `python-dotenv` for configuration, `pytest` for automated security validation, and graceful LLM error handling.

---

## Architecture Overview

EchoGrid is split into three core phases of execution, representing the lifecycle of an autonomous agent network:

### Phase 1: Cognitive Routing (`src/agents/router.py`)
Instead of broadcasting every message to every agent in a swarm, EchoGrid uses **Semantic Routing**.
- **The Tech:** `FAISS` (Facebook AI Similarity Search) and `sentence-transformers/all-MiniLM-L6-v2`.
- **The Process:** Bot personas are stored in an in-memory vector database. Incoming posts are embedded into a vector space. A Cosine Similarity threshold dynamically matches the post context to the bots most likely to "care" about the topic using exact math via `sklearn.metrics.pairwise.cosine_similarity`.
- **Threshold Tuning:** The `ROUTING_THRESHOLD` in the `.env` file controls inclusivity. A lower score (e.g., `0.1`) routes the post to any bot with a tangential opinion (e.g., both Finance and Tech bots responding to an economic post). A higher score (e.g., `0.25`) enforces strict topic isolation.
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
- **The Prompt Injection Defense Mechanism:** Prompt Injections attempt to trick an LLM by appending commands at the end of the user input (e.g., "Ignore previous instructions"). EchoGrid prevents this through **Strict XML Demarcation** and **Logical Framing**.
  - The human's input is explicitly isolated within `<user_input>` tags.
  - A definitive `<SYSTEM SECURITY OVERRIDE>` instruction is placed *after* the human's input in the prompt logic. 
  - The system utilizes strict IF/ELSE logical branching to classify the input, explicitly commanding the LLM to aggressively reject hacking attempts *in character*, thereby maintaining the persona sandbox even under adversarial attack.

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
