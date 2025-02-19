class CypherQueries:
    def create_player_nodes(self):
        return """
        UNWIND $data_list AS playerData
        CREATE (p:Player)
        SET p = playerData
        """

    def create_action_nodes(self):
        return """
        UNWIND $data_list AS actionData
        CREATE (a:Action)
        SET a = actionData
        """

    def create_performed_relationships(self):
        return """
        UNWIND $data_list AS actionData
        MATCH (p:Player {Actor: toInteger(actionData.Actor)}),
            (a:Action {collect_max_count: toInteger(actionData.collect_max_count),
            Sit_ratio: toFloat(actionData.Sit_ratio),
            Sit_count: toInteger(actionData.Sit_count),
            sit_count_per_day: toFloat(actionData.sit_count_per_day),
            Exp_get_ratio: toFloat(actionData.Exp_get_ratio),
            Exp_get_count: toInteger(actionData.Exp_get_count),
            exp_get_count_per_day: toFloat(actionData.exp_get_count_per_day),
            Item_get_ratio: toFloat(actionData.Item_get_ratio),
            Item_get_count: toInteger(actionData.Item_get_count),
            item_get_count_per_day: toFloat(actionData.item_get_count_per_day),
            Money_get_ratio: toFloat(actionData.Money_get_ratio),
            Money_get_count: toInteger(actionData.Money_get_count),
            money_get_count_per_day: toFloat(actionData.money_get_count_per_day),
            Abyss_get_ratio: toFloat(actionData.Abyss_get_ratio),
            Abyss_get_count: toInteger(actionData.Abyss_get_count),
            abyss_get_count_per_day: toFloat(actionData.abyss_get_count_per_day),
            Exp_repair_count: toInteger(actionData.Exp_repair_count),
            Exp_repair_count_per_day: toFloat(actionData.Exp_repair_count_per_day),
            Use_portal_count: toInteger(actionData.Use_portal_count),
            Use_portal_count_per_day: toFloat(actionData.Use_portal_count_per_day),
            Killed_bypc_count: toInteger(actionData.Killed_bypc_count),
            Killed_bypc_count_per_day: toFloat(actionData.Killed_bypc_count_per_day),
            Killed_bynpc_count: toInteger(actionData.Killed_bynpc_count),
            Killed_bynpc_count_per_day: toFloat(actionData.Killed_bynpc_count_per_day),
            Teleport_count: toInteger(actionData.Teleport_count),
            Teleport_count_per_day: toFloat(actionData.Teleport_count_per_day),
            Reborn_count: toInteger(actionData.Reborn_count),
            Reborn_count_per_day: toFloat(actionData.Reborn_count_per_day)
        })
        CREATE (p)-[:PERFORMED]->(a)
        """

    def create_social_relationships(self):
        return """
        UNWIND $data_list AS socialData
        MATCH (p:Player {Actor: toInteger(socialData.Actor)})
        SET p.Social_diversity = toFloat(socialData.Social_diversity)
        """

    def create_group_relationships(self):
        return """
        UNWIND $data_list AS groupData
        MATCH (p:Player {Actor: toInteger(groupData.Actor)})
        SET p.Avg_PartyTime = toFloat(groupData.Avg_PartyTime),
            p.GuildAct_count = toInteger(groupData.GuildAct_count),
            p.GuildJoin_count = toInteger(groupData.GuildJoin_count)
        """

    def create_network_properties(self):
        return """
        UNWIND $data_list AS networkData
        MATCH (p:Player {Actor: toInteger(networkData.Actor)})
        SET p += networkData
        """
