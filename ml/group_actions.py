
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from .prompts_v2 import group_actions_prompt

from langchain_groq import ChatGroq



def extract_player_group_action_features(player_id: str, graph) -> dict:
    """
    Extracts features from the knowledge graph for a given player.
    """
    query = f"""
    MATCH (p:Player {{Actor: toInteger('{player_id}')}})
    RETURN
        p.Actor AS player_id,
        p.A_Acc AS a_acc,
        p.Avg_PartyTime AS avg_partytime,
        p.GuildAct_count AS guild_act_count,
        p.GuildJoin_count AS guild_join_count
    """
    results = graph.query(query)
    if results:
        return results[0]
    else:
        return {}

prompt_template = group_actions_prompt()

if prompt_template:
    prompt = ChatPromptTemplate.from_template(prompt_template)
else:
    prompt = None  # 

def assess_group_action_bot_likelihood(player_data, llm) -> tuple[int, str, str]:
    """
    Assesses the likelihood of a player being a bot using LLM and extracts score and reasoning.
    Returns a tuple of (anomaly_score, reasoning, full_analysis).
    """
    # Format the prompt
    formatted_prompt = prompt.format_messages(
        actor=player_data['player_id'],
        a_acc=player_data['a_acc'],
        avg_partytime=player_data['avg_partytime'],
        guildact_count=player_data['guild_act_count'],
        guildjoin_count=player_data['guild_join_count']
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