# main.py
import os
import pandas as pd
from typing_extensions import List, TypedDict, Dict

from langchain_core.runnables import chain
from langgraph.graph import StateGraph, END
from langchain_community.graphs import Neo4jGraph

# Import your existing modules
from src.data_ingestion.kg_population import KnowledgeGraphPopulator
from ml.search_agent import FAISSIndex
from ml.anomaly_scoring_agent import assess_bot_likelihood, extract_player_features
#from ml.embedding_agent import generate_embedding # Assuming you have a function to generate embeddings # REMOVED
from src.data_ingestion.load_data import load_player_data, load_action_data, load_social_data, load_network_data, load_group_data
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Game Bot Detection Framework"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
# --- Define State ---
class State(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        player_id: The player ID to analyze.
        player_data: Player data extracted from the knowledge graph.
        similar_player_ids: List of similar player IDs from semantic search.
        anomaly_score: The anomaly score assigned by the LLM.
        reasoning: The LLM's reasoning for the anomaly score.
        report: The final report generated.
    """
    player_id: str
    player_data: Dict[str, any]
    similar_player_ids: List[str]
    anomaly_score: int
    reasoning: str 
    full_analysis: str 
    report: Dict[str, any]

# --- Define Nodes (Agents) ---
def ingest_data(state: State) -> Dict:
    """
    Ingests data into the knowledge graph.
    """
    print("Starting Data Ingestion...")
    kg_populator = KnowledgeGraphPopulator()
    try:
        kg_populator.populate_knowledge_graph()
        print("Data Ingestion Complete.")
        return {"player_id": state['player_id']}  # Pass player_id to the next state
    except Exception as e:
        print(f"Data ingestion failed: {e}")
        # Handle the failure appropriately, maybe by setting a flag in the state
        return {"player_id": state['player_id']} # Continue but the rest of the agents can check for the flag


def semantic_search(state: State) -> Dict:
    """
    Performs semantic search to find similar players.
    """
    print(f"Starting Semantic Search for player: {state['player_id']}")
    player_id = state['player_id']  # Get player ID from the state
    faiss_index = FAISSIndex() # Instantiate FAISSIndex here

    # Reload dataframes
    player_df = load_player_data()

    # Load the FAISS index with the reloaded player data
    try:
        faiss_index.load_index(player_df)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return {"similar_player_ids": []} # return empty

    player_data = extract_player_features(player_id)
    if not player_data:
        print(f"No player data found for player ID: {player_id}")
        return {"similar_player_ids": []}
        
    query_text = f"Player ID: {player_data['player_id']}, A_Acc: {player_data['a_acc']}, Login_day_count: {player_data['login_day_count']}, Logout_day_count: {player_data['logout_day_count']}, Playtime: {player_data['playtime']}, playtime_per_day: {player_data['playtime_per_day']}, avg_money: {player_data['avg_money']}, Login_count: {player_data['login_count']}, ip_count: {player_data['ip_count']}, Max_level: {player_data['max_level']}"
# Return an empty list if no embedding is found
    # Perform semantic search
    similar_player_ids = faiss_index.search(query_text, top_k=3)
    print(f"Similar players found: {similar_player_ids}")
    return {"similar_player_ids": similar_player_ids}

def anomaly_scoring(state: State) -> Dict:
    """
    Scores the player for bot-like behavior using LLM.
    """
    print(f"Starting Anomaly Scoring for player: {state['player_id']}")
    player_data = state['player_data']
    similar_player_ids = state['similar_player_ids']

    anomaly_score, reasoning, full_analysis = assess_bot_likelihood(player_data, similar_player_ids)

    print(f"Anomaly Score: {anomaly_score}")
    print(f"Reasoning: {reasoning}")

    return {
        "anomaly_score": anomaly_score,
        "reasoning": reasoning,
        "full_analysis": full_analysis
    }


def generate_report(state: State) -> Dict:
    """
    Generates a final report.
    """
    print(f"Generating Report for player: {state['player_id']}")
    report = {
        "player_id": state['player_id'],
        "anomaly_score": state['anomaly_score'],
        "reasoning": state['reasoning'],
        "full_analysis": state['full_analysis'],
        "similar_player_ids": state['similar_player_ids']
    }
    print(f"Final Report: {report}")
    return {"report": report}

def extract_player_data(state: State) -> Dict:
    """
    Extracts player data from the knowledge graph.
    """
    print(f"Extracting player data for player: {state['player_id']}")
    player_data = extract_player_features(state['player_id'])
    print(f"Player Data: {player_data}")
    return {"player_data": player_data}

# --- Define Graph ---
def main():
    graph = StateGraph(State)

    # Define the nodes
    graph.add_node("ingest_data", ingest_data)
    graph.add_node("extract_player_data", extract_player_data)
    graph.add_node("semantic_search", semantic_search)
    graph.add_node("anomaly_scoring", anomaly_scoring)
    graph.add_node("generate_report", generate_report)

    # Define the edges
    graph.set_entry_point("ingest_data")
    graph.add_edge("ingest_data", "extract_player_data")
    graph.add_edge("extract_player_data", "semantic_search")
    graph.add_edge("semantic_search", "anomaly_scoring")
    graph.add_edge("anomaly_scoring", "generate_report")
    graph.add_edge("generate_report", END)

    app = graph.compile()
    return app


# Run the graph
#player_id  = 202735
# player_id = 233533
# inputs = {"player_id": player_id}
# app =main()
# results = app.invoke(inputs)

# print(f"Analysis complete for player_id: {player_id}")
# print(f"Final Results: {results}")
