# Assuming neo4j_driver.py and queries.py contain the following classes
from neo4j import GraphDatabase
import os

class Neo4jConnection:

    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        except Exception as e:
            print("Failed to create the driver", e)

    def close(self):
        if self.driver is not None:
            self.driver.close()