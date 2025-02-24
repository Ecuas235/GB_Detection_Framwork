import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from src.data_ingestion.load_data import load_player_data
from typing import List
import torch

class FAISSIndex:
    def __init__(self):
        self.faiss_index = None
        self.player_ids = []
        self.embedding_dim = 768  # Adjust if your actual embedding dimension is different
        self.model = None  # Load the SentenceTransformer model
        self.model_name = "intfloat/multilingual-e5-large-instruct"
        
    def load_model(self):
        """Loads the SentenceTransformer model."""
        
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        print(f"Loading SentenceTransformer model: {self.model_name} on device: {device}")
        self.model = SentenceTransformer(self.model_name, device=device)
        print(f"Loaded SentenceTransformer model: {self.model_name} on device: {device}")

    def load_index(self, player_df, embedding_file="ml/model/player_embeddings_4000.npy"):
        """Loads pre-computed embeddings from a pickle file and builds FAISS index."""
        try:
            # with open(embedding_file, "rb") as f:
            #     embeddings = pickle.load(f)
            embeddings = np.load(embedding_file)
            self.player_ids = player_df['Actor'].astype(str).tolist()
            print(f"Type of loaded embeddings: {type(embeddings)}")
            # Ensure loaded embeddings are a numpy array and have the correct shape
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings).astype('float32')  # Convert to numpy array
            if isinstance(embeddings, tuple):
                print("Tuple detected. Converting the embeddings to numpy array")
                embeddings = np.array(embeddings).astype('float32') 
            if not isinstance(embeddings, np.ndarray):
                raise ValueError("Loaded embeddings are not a numpy array.")

            if len(embeddings.shape) != 2:
                raise ValueError(f"Embeddings must be 2D array, got shape {embeddings.shape}")

            if embeddings.shape[1] != self.embedding_dim:
                self.embedding_dim = embeddings.shape[1]  # Update dimension if needed
                print(f"Embedding dimension updated to {self.embedding_dim} based on loaded data.")

            # Build FAISS index
            dimension = self.embedding_dim
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings)
            print("FAISS index loaded successfully from pickle file.")
        except FileNotFoundError:
            print(f"Error: Embedding file not found at {embedding_file}")
            raise
        except Exception as e:
            print(f"Error loading and building FAISS index: {e}")
            raise

    def get_embedding_for_player(self, player_id: str, embedding_file="ml/model/player_embeddings.pkl"):
        """
        Retrieves the pre-computed embedding for a specific player from the embeddings file.
        """
        try:
            with open(embedding_file, "rb") as f:
                embeddings = pickle.load(f)

            player_df = load_player_data()
            self.player_ids = player_df['Actor'].astype(str).tolist()

            player_index = self.player_ids.index(player_id)
            return np.array(embeddings[player_index]).astype('float32')
        except ValueError:
            print(f"Player ID {player_id} not found in embeddings.")
            return None
        except FileNotFoundError:
             print(f"Error: Embedding file not found at {embedding_file}")
             return None
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return None

    def search(self, query_text: str, top_k: int = 5) -> List[str]:
        """Finds similar players using FAISS index based on a pre-computed embedding."""
        
        # Load model if not already loaded
        if self.model is None:
            self.load_model()
        
        query_embedding = self.model.encode([query_text], convert_to_tensor=True)
        query_embedding = query_embedding.cpu().numpy() 
        
        if self.faiss_index is None:
            return ["Error: FAISS index not initialized. Load the index first."]
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)

        D, I = self.faiss_index.search(query_embedding.astype('float32'), top_k)

        similar_player_ids = [self.player_ids[i] for i in I[0]]
        return similar_player_ids

