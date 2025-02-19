import pandas as pd
import os 

player_information = pd.read_csv('./data/csv_data/(after) Player information features.csv')
player_actions = pd.read_csv('./data/csv_data/(after) Player actions features.csv')
social_interaction = pd.read_csv('./data/csv_data/(after) Social interaction diversity features.csv')
network_measure = pd.read_csv('./data/csv_data/(after) Network measures features.csv')
group_activities = pd.read_csv('./data/csv_data/(after) Group activities features.csv')


def get_player_summary(actor_id):
    player_info = player_information[player_information['Actor'] == actor_id].iloc[0]
    player_action = player_actions[player_actions['Actor'] == actor_id].iloc[0]
    social = social_interaction[social_interaction['Actor'] == actor_id].iloc[0]
    group_actions = group_activities[group_activities['Actor'] == actor_id].iloc[0]
    network = network_measure[network_measure['Actor'] == actor_id].iloc[0]

    summary = f"""
    Player Summary for Actor ID {actor_id}:

    - **Login Statistics**: Logged in for {player_info['Login_day_count']} days, logged out for {player_info['Logout_day_count']} days.
    - **Playtime**: Total playtime is {player_info['Playtime']} seconds, averaging {player_info['playtime_per_day']} seconds per day.
    - **Currency**: Average money collected is {player_info['avg_money']}, with a maximum level reached of {player_info['Max_level']}.

    - **Player Actions**:
    - Collected items a maximum of {player_action['collect_max_count']} times.
    - Sit ratio: {player_action['Sit_ratio']}.
    - Experience gain ratio: {player_action['Exp_get_ratio']} with an experience count of {player_action['Exp_get_count']}.
    - Money gain ratio: {player_action['Money_get_ratio']} with a total money count of {player_action['Money_get_count']}.

    - **Social Interaction**: 
    - Social diversity score: {social['Social_diversity']}.

    - **Group Actions**:
    - Average party time: {group_actions['Avg_PartyTime']} seconds.
    - Guild activities count: {group_actions['GuildAct_count']}, Guild joins: {group_actions['GuildJoin_count']}.

    - **Network Measures**:
    - In-degree: {network['p_in_deg']}, Out-degree: {network['p_out_deg']}.

    """
    
    return summary

if __name__ == '__main__':
    actor_ids = player_information['Actor'].tolist()
    for actor_id in actor_ids:
        summary  = get_player_summary(actor_id)
        
        with open(f'./data/markdown/{actor_id}.md', 'w') as file:
            file.write(summary)