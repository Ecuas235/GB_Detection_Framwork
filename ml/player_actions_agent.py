import os
from typing import List
# from langchain_community.graphs import Neo4jGraph
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import json

from .prompts_v2 import player_action_prompt
import numpy as np


def extract_player_action_features(player_id: str, graph: Neo4jGraph) -> dict:
    """
    Extracts features from the knowledge graph for a given player.
    """
    query = f"""
    MATCH (p:Player {{Actor: toInteger('{player_id}')}})-[:PERFORMED]->(a:Action)
    RETURN 
        p.Actor as actor,
        a.collect_max_count as collect_max_count,
        a.Sit_ratio as Sit_ratio,
        a.Sit_count as Sit_count,
        a.sit_count_per_day as sit_count_per_day,
        a.Exp_get_ratio as Exp_get_ratio,
        a.Exp_get_count as Exp_get_count,
        a.exp_get_count_per_day as exp_get_count_per_day,
        a.Item_get_ratio as Item_get_ratio,
        a.Item_get_count as Item_get_count,
        a.item_get_count_per_day as item_get_count_per_day,
        a.Money_get_ratio as Money_get_ratio,
        a.Money_get_count as Money_get_count,
        a.money_get_count_per_day as money_get_count_per_day,
        a.Abyss_get_ratio as Abyss_get_ratio,
        a.Abyss_get_count as Abyss_get_count,
        a.abyss_get_count_per_day as abyss_get_count_per_day,
        a.Exp_repair_count as Exp_repair_count,
        a.Exp_repair_count_per_day as Exp_repair_count_per_day,
        a.Use_portal_count as Use_portal_count,
        a.Use_portal_count_per_day as Use_portal_count_per_day,
        a.Killed_bypc_count as Killed_bypc_count,
        a.Killed_bypc_count_per_day as Killed_bypc_count_per_day,
        a.Killed_bynpc_count as Killed_bynpc_count,
        a.Killed_bynpc_count_per_day as Killed_bynpc_count_per_day,
        a.Teleport_count as Teleport_count,
        a.Teleport_count_per_day as Teleport_count_per_day,
        a.Reborn_count as Reborn_count,
        a.Reborn_count_per_day as Reborn_count_per_day
    """
    results = graph.query(query)
    if results:
        return results[0]
    else:
        return {}
prompt_template = player_action_prompt()

if prompt_template:
    prompt = ChatPromptTemplate.from_template(prompt_template)
else:
    prompt = None  # Handle the case where the prompt couldn't be loaded
    
def assess_player_action(player_data, llm) -> tuple[int, str, str]:
    """
    Assesses the likelihood of a player being a bot using LLM and extracts score and reasoning.
    Returns a tuple of (anomaly_score, reasoning, full_analysis).
    """
    
    formatted_prompt = prompt.format_messages(**player_data)

    response = llm.invoke(formatted_prompt)

    try:
        json_str = response.content
        response_dict = json.loads(json_str[json_str.find('{'):json_str.rfind('}')+1])
        
        response_dict = {key.strip(): value for key, value in response_dict.items()}
        anomaly_score = response_dict.get("anomaly_score", None)
        reasoning = response_dict.get("reasoning", "Could not parse reasoning.")
        full_analysis = response.content
        
        return anomaly_score, reasoning, full_analysis
        
    except (json.JSONDecodeError, Exception) as e:
        anomaly_score = None
        #reasoning = f"Could not reliably parse LLM response: {str(e)}"
        reasoning = response.content
        full_analysis = response.content
    
    return anomaly_score, reasoning, full_analysis