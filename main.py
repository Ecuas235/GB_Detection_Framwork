import os
import random
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langchain_neo4j import Neo4jGraph

# Custom Imports
from src.data_ingestion.kg_population import KnowledgeGraphPopulator
from ml.search_agent import FAISSIndex
from ml.anomaly_scoring_agent import assess_bot_likelihood, extract_player_features
from ml.social_diversity_agent import assess_social_bot_likelihood, extract_player_social_diversity_features
from ml.player_actions_agent import extract_player_action_features, assess_player_action
from src.data_ingestion.load_data import load_player_data

# Load Environment Variables
load_dotenv()

class PlayerAnalysisState(TypedDict):
    """
    Enhanced state management with clear typing and comprehensive analysis state.
    """
    player_ids: List[str]
    current_player_id: str
    remaining_steps: int
    
    # Extracted Data
    player_data: Dict[str, Any]
    social_data: Dict[str, Any]
    player_action_data: Dict[str, Any]
    similar_player_ids: List[str]
    
    # Analysis Results
    anomaly_score: float
    anomaly_reasoning: str
    social_diversity_score: float
    social_reasoning: str
    player_action_score: float
    player_action_reasoning: str
    
    # Final Classification
    classification_result: str
    classification_reasoning: str
    classification_confidence: float
    
    # Aggregated Reports
    reports: List[Dict[str, Any]]
class BotDetectionOrchestrator:
    def __init__(
        self, 
        llm: BaseLanguageModel, 
        neo4j_graph: Neo4jGraph,
        faiss_index: FAISSIndex
    ):
        """
        Initialize the bot detection orchestrator with core dependencies.
        
        Args:
            llm: Language model for advanced reasoning
            neo4j_graph: Knowledge graph for data storage
            faiss_index: Semantic search index
        """
        self.llm = llm
        self.neo4j_graph = neo4j_graph
        self.faiss_index = faiss_index
        
        # Predefined classification prompt with more structured output
        self.classification_prompt = ChatPromptTemplate.from_template("""
        Analyze bot detection results from multiple agents:
        
        **Anomaly Detection**
        Score: {anomaly_score}/100
        Reasoning: {anomaly_reasoning}
        
        **Social Diversity Analysis**
        Score: {social_diversity_score}/100
        Reasoning: {social_reasoning}
        
        **Player Action Analysis**
        Score: {player_action_score}/100
        Reasoning: {player_action_reasoning}
        
        Rules:
        1. Score ABOVE 80 in either category indicates high bot probability
        2. Scores BETWEEN 40-79 require contextual analysis
        3. BELOW 40 suggests legitimate play
        
        Final output format:
        Classification: [Bot/Human]
        Confidence: [0-100]
        Reasoning: [Concise analysis combining both reports]
        """)

    def data_ingestion(self, state: PlayerAnalysisState) -> Dict[str, List[str]]:
        """Ingest data into knowledge graph with robust error handling."""
        try:
            kg_populator = KnowledgeGraphPopulator()
            kg_populator.populate_knowledge_graph()
            return {"player_ids": state['player_ids']}
        except Exception as e:
            print(f"Data ingestion failed: {e}")
            return {"player_ids": state['player_ids']}

    def extract_player_features(self, state: PlayerAnalysisState) -> Dict[str, Dict]:
        """Advanced feature extraction with current player context."""
        player_id = state['current_player_id']
        return {
            "player_data": extract_player_features(player_id, self.neo4j_graph),
            "social_data": extract_player_social_diversity_features(player_id, self.neo4j_graph),
            "player_action_data": extract_player_action_features(player_id, self.neo4j_graph)
        }

    def semantic_search(self, state: PlayerAnalysisState) -> Dict[str, List[str]]:
        """Enhanced semantic search with robust indexing."""
        try:
            player_df = load_player_data()
            self.faiss_index.load_index(player_df)
            similar_player_ids = self.faiss_index.search(
                str(state['player_data']), 
                top_k=3
            )
            return {"similar_player_ids": similar_player_ids}
        except Exception as e:
            print(f"Semantic search error: {e}")
            return {"similar_player_ids": []}

    def analyze_player(self, state: PlayerAnalysisState) -> Dict[str, Any]:
        """Comprehensive player analysis combining multiple signals."""
        anomaly_score, anomaly_reasoning, _ = assess_bot_likelihood(
            state['player_data'], 
            self.llm,
            self.neo4j_graph,
            state['similar_player_ids']
        )
        
        social_diversity_score, social_reasoning, _ = assess_social_bot_likelihood(
            state['social_data'],
            self.llm
        )
        
        player_action_score, player_action_reasoning, _ = assess_player_action(
            state['player_action_data'],
            self.llm
        )
        return {
            "anomaly_score": anomaly_score,
            "anomaly_reasoning": anomaly_reasoning,
            "social_diversity_score": social_diversity_score,
            "social_reasoning": social_reasoning,
            "player_action_score": player_action_score,
            "player_action_reasoning": player_action_reasoning
        }

    def classify_player(self, state: PlayerAnalysisState) -> Dict[str, Any]:
        """Advanced classification using language model reasoning."""
        classification_input = self.classification_prompt.format_messages(
            anomaly_score=state["anomaly_score"],
            anomaly_reasoning=state["anomaly_reasoning"],
            social_diversity_score=state["social_diversity_score"],
            social_reasoning=state["social_reasoning"],
            player_action_score=state["player_action_score"],
            player_action_reasoning=state["player_action_reasoning"]

        )
        
        response = self.llm.invoke(classification_input)
        
        # Enhanced parsing of classification response
        classification_parts = response.content.split("\n")
        
        # for line in classification_parts:
        #     if line.startswith("Classification:"):
        #         classification_result = line.split(":")[1].strip()
        #     elif line.startswith("Confidence:"):
        #         try:
        #             classification_confidence = float(line.split(":")[1].strip())
        #         except ValueError:
        #             classification_confidence = 0.0
        
        return {
            "classification_result": response.content
        }
    def persist_classification_to_kg(self, state: PlayerAnalysisState) -> Dict[str, Any]:
        """
        Persist player classification to Neo4j Knowledge Graph.
        
        Creates or updates a classification node and links it to the player node.
        """
        player_id = state['current_player_id']
        classification = state['classification_result']
        
        try:
            # Cypher query to create or merge classification node and link to player
            merge_query = """
            // Find or create the player node
            MERGE (p:Player {Actor: $player_id})
            
            // Create or find the classification node
            MERGE (c:Classification {
                type: $classification
            })
            
            // Create or update the relationship
            MERGE (p)-[r:HAS_CLASSIFICATION]->(c)
            ON CREATE SET 
                r.timestamp = datetime()
            ON MATCH SET 
                r.timestamp = datetime()
            
            RETURN p, c, r
            """
            
            # Execute the query
            result = self.neo4j_graph.query(merge_query, {
                "player_id": player_id,
                "classification": classification,
            })
            
            print(f"Classification persisted for player {player_id}: {classification}")
            
            return {"kg_persist_status": "Success"}
        
        except Exception as e:
            print(f"Error persisting classification to Knowledge Graph: {e}")
            return {"kg_persist_status": "Failed"}
        
    def generate_report(self, state: PlayerAnalysisState) -> Dict[str, List[Dict]]:
        """Create comprehensive report with aggregation."""
        report = {
            "player_id": state['current_player_id'],
            "classification_result": state["classification_result"],
            "anomaly_score": state["anomaly_score"],
            "social_diversity_score": state["social_diversity_score"],
            "player_action_score": state["player_action_score"]
        }
        
        reports = state.get('reports', [])
        reports.append(report)
        
        return {"reports": reports}
    
    def advance_to_next_player(self, state: PlayerAnalysisState) -> Dict[str, Any]:
        """Intelligent player processing with recursion limit."""
        if state["remaining_steps"] <= 0 or not state["player_ids"]:
            return {"player_ids": [], "end": True}
        
        next_player_id = state["player_ids"].pop(0)
        
        return {
            "current_player_id": next_player_id,
            "player_ids": state["player_ids"],
            "remaining_steps": state["remaining_steps"] - 1
        }
        
    def create_workflow(self) -> Any:
        """Construct the LangGraph workflow with advanced routing."""
        graph = StateGraph(PlayerAnalysisState)
        
        # Add workflow nodes
        graph.add_node("ingest_data", self.data_ingestion)
        graph.add_node("extract_features", self.extract_player_features)
        graph.add_node("semantic_search", self.semantic_search)
        graph.add_node("analyze_player", self.analyze_player)
        graph.add_node("classify_player", self.classify_player)
        graph.add_node("persist_to_kg", self.persist_classification_to_kg)
        graph.add_node("generate_report", self.generate_report)
        graph.add_node("advance_player", self.advance_to_next_player)
        
        # Define workflow edges
        graph.set_entry_point("ingest_data")
        graph.add_edge("ingest_data", "extract_features")
        graph.add_edge("extract_features", "semantic_search")
        graph.add_edge("semantic_search", "analyze_player")
        graph.add_edge("analyze_player", "classify_player")
        graph.add_edge("classify_player", "persist_to_kg")
        graph.add_edge("persist_to_kg", "generate_report")
        graph.add_edge("generate_report", "advance_player")
        
        # Conditional routing for continuous processing
        graph.add_conditional_edges(
            "advance_player",
            lambda state: "end" not in state or not state.get("end", False),
            {
                True: "extract_features",
                False: END
            }
        )
        
        return graph.compile()

def main():
    # Configure dependencies
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY2")
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGCHAIN_PROJECT"] = "Game Bot Detection Framework"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    neo4j_graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"), 
        username=os.getenv("NEO4J_USERNAME"), 
        password=os.getenv("NEO4J_PASSWORD")
    )
    faiss_index = FAISSIndex()

    # Load and sample player data
    player_df = load_player_data()
    player_ids = player_df['Actor'].unique().tolist()
    
    sample_size = min(30, len(player_ids))
    sampled_player_ids = random.sample(player_ids, sample_size)

    # Initialize orchestrator
    orchestrator = BotDetectionOrchestrator(llm, neo4j_graph, faiss_index)
    workflow = orchestrator.create_workflow()

    # Prepare initial state
    initial_state = {
        "player_ids": sampled_player_ids[1:],
        "current_player_id": sampled_player_ids[0],
        "remaining_steps": 100,
        "reports": []
    }

    # Execute workflow
    results = workflow.invoke(initial_state, {"recursion_limit": 250})
    print("Bot Detection Analysis Complete:")
    for report in results.get('reports', []):
        print(f"Player {report['player_id']}: {report['classification_result']}")

if __name__ == "__main__":
    main()