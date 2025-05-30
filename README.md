# 🎮 Gaming Bot Detection System

*An AI-powered system to identify automated players (bots) in online multiplayer games*

---

## 🤖 What This Does

This system analyzes player behavior to detect bots - automated programs that play games 24/7, perform repetitive actions, and give unfair advantages. It acts like a detective, examining player patterns and using AI to determine who's human and who's a bot.

**Why It Matters:**
- Ensures fair play for legitimate players  
- Protects game economies from artificial manipulation
- Maintains authentic social gaming experiences

## 🔍 How It Works

### Detection Methods
Our system examines multiple behavioral patterns:

- **⏰ Time Patterns**: Players online 24/7 vs. normal human schedules
- **🎯 Activity Patterns**: Repetitive actions vs. natural human variation  
- **💰 Resource Collection**: Unusually high gains (500+ XP/day consistently)
- **👥 Social Behavior**: Zero interactions vs. normal player socializing
- **🌐 Login Patterns**: Multiple IP addresses indicating bot farms

### AI Scoring System
Each player gets a suspicion score (0-100):
- **0-30**: Likely human
- **31-70**: Suspicious, needs review
- **71-100**: Very likely bot

## 🏗️ System Architecture
![alt text](image.png)
### Core Components

1. **Knowledge Graph Database** (Neo4j)
   - Stores player data and relationships
   - Enables complex pattern analysis

2. **Detection Agents**
   - **Anomaly Scoring**: Overall behavior analysis
   - **Social Diversity**: Interaction pattern analysis  
   - **Action Patterns**: Repetitive behavior detection
   - **Group Activity**: Guild/party participation analysis

3. **AI-Powered Analysis**
   - Uses large language models for pattern recognition
   - Provides human-readable explanations
   - Finds similar suspicious players

## 📊 Sample Detection Report

```
Player ID: 8085
Anomaly Score: 92/100 (Very Likely Bot)

Key Findings:
- Playtime: 18+ hours daily for 88 consecutive days
- Login sessions: 1,065 times (12+ per day)
- Social interactions: Nearly zero
- Resource gains: Exceptionally high and consistent

Recommendation: Immediate investigation
```

## 🚀 Quick Start

### For Game Managers
1. Provide suspicious player IDs to the system
2. Review generated reports (written in plain English)
3. Make moderation decisions based on scores and explanations

### For Developers

```bash
# Setup
git clone https://github.com/Ecuas235/GB_Detection_Framwork.git
pip install -r requirements.txt

# Configure environment
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"  
export NEO4J_PASSWORD="your_password"
export GROQ_API_KEY="your_api_key"

# Run detection
python main.py
```

## 📈 Performance

- **95% accuracy** on confirmed bots
- **3% false positive rate**  
- **1000+ players/minute** processing speed
- Scales to millions of player records


## 🤝 Acknowldgements
This project uses the Game Bot Detection Dataset from HCRL, based on user behavior logs from the MMORPG Aion. Please cite Kang et al., SpringerPlus, 2016 when using this dataset.


**Important**: This tool assists human decision-making. Always combine automated detection with human judgment for fair and accurate results.

*Built for fair gaming communities* 🎮