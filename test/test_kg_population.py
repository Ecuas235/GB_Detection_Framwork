import unittest
import os
from src.data_ingestion import kg_population
from src.graph.neo4j_driver import Neo4jConnection
from neo4j import GraphDatabase

class TestKGPopulation(unittest.TestCase):

    def setUp(self):
        """Setup method to establish connection before each test."""
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_username = os.getenv("NEO4J_USERNAME")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.conn = Neo4jConnection(self.neo4j_uri, self.neo4j_username, self.neo4j_password)
        self.driver = self.conn.driver  # Access the driver from Neo4jConnection
        self.db = "neo4j"

    def tearDown(self):
        """Teardown method to close the connection and drop the graph after each test."""
        if self.conn.driver:
            self.conn.close()
        self._clear_graph()

    def _clear_graph(self):
        """Helper method to clear the graph after each test."""
        try:
            with self.driver.session(database=self.db) as session:
                session.run("MATCH (n) DETACH DELETE n")
        except Exception as e:
            print(f"Error clearing graph: {e}")

    def test_kg_population_runs_without_error(self):
        """Test that the KG population script runs without raising exceptions."""
        try:
            kg_population.populate_knowledge_graph()
        except Exception as e:
            self.fail(f"KG population failed with exception: {e}")

    def test_player_nodes_created(self):
        """Test that player nodes are created after running the script."""
        kg_population.populate_knowledge_graph()
        with self.driver.session(database=self.db) as session:
            result = session.run("MATCH (p:Player) RETURN count(p) AS player_count").single()
            player_count = result["player_count"] if result else 0
            self.assertGreater(player_count, 0, "No player nodes were created.")
    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()
