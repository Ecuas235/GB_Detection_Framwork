# ml/anomaly_scoring_agent.py
import os
from typing import List
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from .prompts_v2 import anomaly_scoring_prompt
import numpy as np

# Initialize LLM and Neo4j Graph

def extract_player_features(player_id: str, graph) -> dict:
    """Extracts features from the knowledge graph for a given player."""
    query = f"""
    MATCH (p:Player {{Actor: toInteger('{player_id}')}})
    RETURN
        p.Actor AS player_id,
        p.A_Acc AS a_acc,
        p.Login_day_count AS login_day_count,
        p.Logout_day_count AS logout_day_count,
        p.Playtime AS playtime,
        p.playtime_per_day AS playtime_per_day,
        p.avg_money AS avg_money,
        p.Login_count AS login_count,
        p.ip_count AS ip_count,
        p.Max_level AS max_level
    """
    results = graph.query(query)
    if results:
        return results[0]
    else:
        return {}

prompt_template = anomaly_scoring_prompt()

if prompt_template:
    prompt = ChatPromptTemplate.from_template(prompt_template)
else:
    prompt = None  # Handle the case where the prompt couldn't be loaded

def assess_bot_likelihood(player_data: dict, llm, graph ,similar_player_ids: List[str] = []) -> tuple[int, str, str]:
    """Assesses the likelihood of a player being a bot using LLM, considering player statistics and insights from similar players."""
    if prompt is None:
        return None, "Prompt could not be loaded", None

    # Get insights from similar players
    similar_player_insights = ""
    if similar_player_ids:
        similar_player_data = [extract_player_features(pid, graph) for pid in similar_player_ids]
        # Combine insights (e.g., summarize their behaviors or anomaly scores)
        similar_player_insights = f"Similar players: {', '.join(similar_player_ids)}. " \
                                  f"Insights: {similar_player_data}"  # Simple concatenation for now

    # Format the prompt
    formatted_prompt = prompt.format_messages(
        actor=player_data['player_id'],
        a_acc=player_data['a_acc'],
        login_day_count=player_data['login_day_count'],
        logout_day_count=player_data['logout_day_count'],
        playtime=player_data['playtime'],
        playtime_per_day=player_data['playtime_per_day'],
        avg_money=player_data['avg_money'],
        login_count=player_data['login_count'],
        ip_count=player_data['ip_count'],
        max_level=player_data['max_level'],
        similar_player_insights=similar_player_insights  # Pass insights
    )

    # Call the LLM directly
    response = llm.invoke(formatted_prompt)
    full_analysis = response.content

    # Extract Anomaly Score and Reasoning
    try:
        score_line = next(line for line in full_analysis.split('\n') if "Anomaly Score" in line)
        anomaly_score = int(score_line.split(":")[1].strip())

        reasoning = "\n".join(full_analysis.split('\n')[1:])  # All lines after the score
    except Exception as e:
            anomaly_score = None
            reasoning = f"Could not reliably parse LLM response: {str(e)}"

    return anomaly_score, reasoning, full_analysis

def generate_bot_report(player_ids: list[str], faiss_index) -> list[dict]:
    """Generates a report for a list of player IDs, incorporating insights from semantically similar players."""
    report = []
    for player_id in player_ids:
        player_data = extract_player_features(player_id)
        if player_data:
            # Get the player embedding (Assuming 1-1 correspondence between player_id and embeddings)
            try:
                query_embedding = faiss_index.get_embedding_for_player(player_id)

                if query_embedding is None:
                    print(f"No embedding found for player ID: {player_id}")
                    continue # Skip to the next player

                similar_player_ids = faiss_index.search(query_embedding, top_k=3)

                anomaly_score, reasoning, full_analysis = assess_bot_likelihood(player_data, similar_player_ids)  # Pass similar IDs

                report.append({
                    "player_id": player_id,
                    "anomaly_score": anomaly_score,
                    "reasoning": reasoning,
                    "full_analysis": full_analysis,
                    "similar_player_ids": similar_player_ids,
                })
            except Exception as e:
                print(f"Error generating report for player {player_id}: {e}")
                # You might want to continue to the next player or re-raise the exception
    return report
