import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# DATA_DIR = 'data/csv_data/'  # Relative path to CSV files
# PLAYER_FILE = '(after) Player information features.csv'
# ACTION_FILE = '(after) Player actions features.csv'
# SOCIAL_FILE = '(after) Social interaction diversity features.csv'
# NETWORK_FILE = '(after) Network measures features.csv'
# GROUP_FILE = '(after) Group activities features.csv'

DATA_DIR = 'data/sample/'  # Relative path to CSV files
PLAYER_FILE = 'sample_player_data.csv'
ACTION_FILE = 'sample_action_data.csv'
SOCIAL_FILE = 'sample_social_data.csv'
NETWORK_FILE = 'sample_network_data.csv'
GROUP_FILE = 'sample_group_data.csv'

def load_player_data():
    """Loads player data from CSV."""
    try:
        player_df = pd.read_csv(os.path.join(DATA_DIR, PLAYER_FILE))
        return player_df
    except FileNotFoundError:
        print(f"Error: {PLAYER_FILE} not found in {DATA_DIR}")
        return None

def load_action_data():
    """Loads action data from CSV."""
    try:
        action_df = pd.read_csv(os.path.join(DATA_DIR, ACTION_FILE))
        return action_df
    except FileNotFoundError:
        print(f"Error: {ACTION_FILE} not found in {DATA_DIR}")
        return None

def load_social_data():
    """Loads social data from CSV."""
    try:
        social_df = pd.read_csv(os.path.join(DATA_DIR, SOCIAL_FILE))
        return social_df
    except FileNotFoundError:
        print(f"Error: {SOCIAL_FILE} not found in {DATA_DIR}")
        return None

def load_network_data():
    """Loads network data from CSV."""
    try:
        network_df = pd.read_csv(os.path.join(DATA_DIR, NETWORK_FILE))
        return network_df
    except FileNotFoundError:
        print(f"Error: {NETWORK_FILE} not found in {DATA_DIR}")
        return None

def load_group_data():
    """Loads group data from CSV."""
    try:
        group_df = pd.read_csv(os.path.join(DATA_DIR, GROUP_FILE))
        return group_df
    except FileNotFoundError:
        print(f"Error: {GROUP_FILE} not found in {DATA_DIR}")
        return None
