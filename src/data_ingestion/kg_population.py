import os
from tqdm import tqdm
from neo4j import GraphDatabase, exceptions
from src.data_ingestion import load_data
from src.graph.neo4j_driver import Neo4jConnection  # Assuming you have this class
from src.graph.queries import CypherQueries  # Assuming this class holds your queries

class KnowledgeGraphPopulator:
    """
    Populates the knowledge graph with data from CSV files using modular components.
    """

    def __init__(self):
        """Initializes the KnowledgeGraphPopulator with graph connection and query objects."""
        self.neo4j_connection = Neo4jConnection(
            uri=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        self.cypher_queries = CypherQueries()

    def _prepare_data_list(self, df):
        """Helper function to convert a DataFrame to a list of dictionaries."""
        return [row.to_dict() for index, row in df.iterrows()]

    def _execute_cypher_query(self, session, query_method, data_list, description, batch_size=1000):
        """Helper function to execute a Cypher query with batching and progress bar."""
        total = len(data_list)
        with tqdm(total=total, desc=description, unit="item") as pbar:
            for i in range(0, total, batch_size):
                batch = data_list[i:i + batch_size]
                try:
                    session.execute_write(lambda tx: query_method(tx, batch)) # Pass the transaction and batch into the function
                    pbar.update(len(batch))
                except exceptions.ClientError as e:
                    print(f"ClientError during {description}: {e}")
                    raise
                except exceptions.ServiceUnavailable as e:
                    print(f"ServiceUnavailable during {description}: {e}")
                    raise
                except Exception as e:
                    print(f"Unexpected error during {description}: {e}")
                    raise

    def create_player_nodes(self, tx, player_data_list):
        query = self.cypher_queries.create_player_nodes()
        tx.run(query, data_list=player_data_list)

    def create_action_nodes(self, tx, action_data_list):
        query = self.cypher_queries.create_action_nodes()
        tx.run(query, data_list=action_data_list)

    def create_performed_relationships(self, tx, action_data_list):
        query = self.cypher_queries.create_performed_relationships()
        tx.run(query, data_list=action_data_list)

    def create_social_relationships(self, tx, social_data_list):
        query = self.cypher_queries.create_social_relationships()
        tx.run(query, data_list=social_data_list)

    def create_group_relationships(self, tx, group_data_list):
        query = self.cypher_queries.create_group_relationships()
        tx.run(query, data_list=group_data_list)

    def create_network_properties(self, tx, network_data_list):
        query = self.cypher_queries.create_network_properties()
        for data in network_data_list:
            data.pop('Actor', None)
            data.pop('A_Acc', None)
        tx.run(query, data_list=network_data_list)

    def populate_knowledge_graph(self):
        """Populates the knowledge graph with data from CSV files."""

        # Load data
        player_df = load_data.load_player_data()
        action_df = load_data.load_action_data()
        social_df = load_data.load_social_data()
        network_df = load_data.load_network_data()
        group_df = load_data.load_group_data()

        # Check if any dataframe is None (loading failed)
        if any(df is None for df in [player_df, action_df, social_df, network_df, group_df]):
            print("Error: Could not load all dataframes. Aborting KG population.")
            return

        try:
            # Prepare data lists
            player_data_list = self._prepare_data_list(player_df)
            action_data_list = self._prepare_data_list(action_df)
            social_data_list = self._prepare_data_list(social_df)
            group_data_list = self._prepare_data_list(group_df)
            network_data_list = self._prepare_data_list(network_df)

            batch_size = 1000  # Adjust batch size as needed

            with self.neo4j_connection.driver.session() as session:
                # Execute each query
                self._execute_cypher_query(session, self.create_player_nodes, player_data_list, "Creating Player Nodes", batch_size)
                self._execute_cypher_query(session, self.create_action_nodes, action_data_list, "Creating Action Nodes", batch_size)
                self._execute_cypher_query(session, self.create_performed_relationships, action_data_list, "Creating PERFORMED Relationships", batch_size)
                self._execute_cypher_query(session, self.create_social_relationships, social_data_list, "Creating Social Relationships", batch_size)
                self._execute_cypher_query(session, self.create_group_relationships, group_data_list, "Creating Group Relationships", batch_size)
                self._execute_cypher_query(session, self.create_network_properties, network_data_list, "Creating Network Properties", batch_size)

            print("\nKnowledge Graph Creation Complete!")

        except Exception as e:
            print(f"Error populating knowledge graph: {e}")


