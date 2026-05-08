import warnings
warnings.filterwarnings("ignore")

import os
import json
from typing import TypedDict, Optional
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger("ContentEngine")

# ---------------------------------------------------------
# 1. State Definition
# ---------------------------------------------------------
class GraphState(TypedDict):
    bot_id: str
    persona: str
    search_query: Optional[str]
    search_results: Optional[str]
    final_post: Optional[dict]

# ---------------------------------------------------------
# 2. Mock Tool
# ---------------------------------------------------------
@tool
def mock_searxng_search(query: str) -> str:
    """Mock search tool that returns hardcoded news headlines based on keywords."""
    query_lower = query.lower()
    if "crypto" in query_lower or "bitcoin" in query_lower:
        return "Bitcoin hits new all-time high amid regulatory ETF approvals. Crypto markets surge."
    elif "ai" in query_lower or "openai" in query_lower:
        return "OpenAI releases new model capable of autonomous coding. Tech industry divided on safety."
    elif "market" in query_lower or "fed" in query_lower or "rate" in query_lower:
        return "Federal Reserve hints at aggressive rate cuts in Q4. S&P 500 rallies."
    elif "climate" in query_lower or "nature" in query_lower:
        return "Global temperatures reach record highs. Tech monopolies criticized for massive carbon footprint."
    else:
        return "General global news: Markets stabilize after a week of high volatility."

# ---------------------------------------------------------
# 3. LLM Setup & Schemas
# ---------------------------------------------------------
# Load model from settings to prevent hardcoding
llm = ChatOllama(model=settings.MODEL_NAME, temperature=0.7)

# Pydantic schema for the final strict JSON output.
# This acts as the "Function Calling" schema constraint.
class GeneratedPost(BaseModel):
    bot_id: str = Field(description="The ID or name of the bot generating the post.")
    topic: str = Field(description="The main topic of the post.")
    post_content: str = Field(description="The highly opinionated, 280-character post.")

# ---------------------------------------------------------
# 4. Nodes
# ---------------------------------------------------------
def decide_search(state: GraphState) -> GraphState:
    """Node 1: Decide what topic to post about and format a search query."""
    logger.info("--- [Node 1] Decide Search ---")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an autonomous AI agent with the following persona:\n{persona}\n\nBased on your persona, decide on a single topic you want to post about today and output ONLY a short search query (1-4 words) to find recent news about it. Do not include quotes or any other text."),
        ("user", "What should we search for today?")
    ])
    
    chain = prompt | llm
    try:
        result = chain.invoke({"persona": state["persona"]})
        query = result.content.strip().strip('"').strip("'")
    except Exception as e:
        logger.error(f"Could not connect to local Ollama server ({settings.MODEL_NAME}). Error: {e}")
        query = "Fallback query due to LLM error"
    
    logger.debug(f"[*] Generated Query: '{query}'")
    return {"search_query": query}

def web_search(state: GraphState) -> GraphState:
    """Node 2: Executes the mock_searxng_search tool to get real-world context."""
    logger.info("--- [Node 2] Web Search ---")
    
    query = state["search_query"]
    logger.debug(f"[*] Executing search for: '{query}'")
    
    # Execute the tool
    results = mock_searxng_search.invoke({"query": query})
    
    logger.debug(f"[*] Search Results: '{results}'")
    return {"search_results": results}

def draft_post(state: GraphState) -> GraphState:
    """Node 3: Drafts the final post using structured outputs (Function Calling)."""
    logger.info("--- [Node 3] Draft Post ---")
    
    # Bind the LLM to the Pydantic schema to enforce strict JSON function calling
    structured_llm = llm.with_structured_output(GeneratedPost)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an autonomous AI agent with the following persona:\n{persona}\n\n"
                   "Write a highly opinionated post (max 280 characters) reacting to the following news:\n{news}\n\n"
                   "Ensure the post heavily reflects your persona."),
        ("user", "Draft the post now.")
    ])
    
    chain = prompt | structured_llm
    
    try:
        # The result will be a validated Pydantic object
        result: GeneratedPost = chain.invoke({
            "persona": state["persona"],
            "news": state["search_results"]
        })
        # Convert Pydantic object to dict
        final_json = result.model_dump()
        final_json["bot_id"] = state["bot_id"]
        logger.info("[*] Drafted Post successfully.")
        
    except Exception as e:
        logger.error(f"Failed to draft post via structured output. Ollama running? Error: {e}")
        final_json = {"bot_id": state["bot_id"], "topic": "Error", "post_content": "LLM generation failed."}
        
    return {"final_post": final_json}

# ---------------------------------------------------------
# 5. Graph Orchestrator
# ---------------------------------------------------------
def build_graph() -> StateGraph:
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("decide_search", decide_search)
    workflow.add_node("web_search", web_search)
    workflow.add_node("draft_post", draft_post)
    
    # Add edges
    workflow.add_edge(START, "decide_search")
    workflow.add_edge("decide_search", "web_search")
    workflow.add_edge("web_search", "draft_post")
    workflow.add_edge("draft_post", END)
    
    return workflow.compile()

# ---------------------------------------------------------
# 6. Test Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    app = build_graph()
    
    from src.core.personas import PERSONAS
    
    # Test Bot Persona
    test_bot_id = "Bot B (Doomer / Skeptic)"
    test_persona = PERSONAS[test_bot_id]
    
    initial_state = {
        "bot_id": test_bot_id,
        "persona": test_persona,
        "search_query": None,
        "search_results": None,
        "final_post": None
    }
    
    logger.info(f"Starting Graph for {test_bot_id}...")
    
    # Run graph
    try:
        final_state = app.invoke(initial_state)
        logger.info("--- [Final Output] (Strict JSON) ---")
        print(json.dumps(final_state["final_post"], indent=4))
    except Exception as e:
        logger.error(f"Graph execution failed. Please ensure your Ollama backend is running. Details: {e}")
