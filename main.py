from src.data_ingestion import kg_population

def main():
    print("Starting Knowledge Graph Population...")
    populator = kg_population.KnowledgeGraphPopulator()
    populator.populate_knowledge_graph()
    print("Knowledge Graph Population Completed.")

if __name__ == "__main__":
    main()
