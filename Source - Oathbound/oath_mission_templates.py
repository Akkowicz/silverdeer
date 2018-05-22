# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_common import *
from header_operations import *
from module_constants import *
from header_mission_templates import *
from header_items import *
from module_mission_templates import *

oathbound_triggers = [  

## TRIGGER: Quest "Prisoners of War"
## PURPOSE: Tallies when you knock out troops of the specified faction.
(ti_on_agent_killed_or_wounded, 0, 0,
	[(neq, "$g_mt_mode", abm_tournament),], 
	[
		(store_trigger_param_1, ":agent_victim"),
		(store_trigger_param_2, ":agent_killer"),
		
		(agent_is_active, ":agent_killer"),
		(agent_is_active, ":agent_victim"),
		
		(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
		(check_quest_active, "qst_oath_prisoners_of_war"),
		(get_player_agent_no, ":agent_player"),
		(agent_get_troop_id, ":troop_killer", ":agent_killer"),
		(this_or_next|eq, ":agent_killer", ":agent_player"),
		(troop_slot_eq, ":troop_killer", slot_troop_in_player_merc_group, 1), # One of your squad.
		(agent_get_troop_id, ":troop_victim", ":agent_victim"),
		(str_store_troop_name, s21, ":troop_victim"),
		(agent_is_wounded, ":agent_victim"),
		(str_store_troop_name, s22, ":troop_killer"),
		(display_message, "@{s22} knocked out {s21}! (Prisoners of War)", gpu_green),
		(call_script, "script_oath_quest_change_slot", "qst_oath_prisoners_of_war", slot_quest_temp_slot, 1),
		(call_script, "script_quest_oathbound_prisoners_of_war", OATH_QUEST_UPDATE),
		(call_script, "script_quest_oathbound_prisoners_of_war", OATH_QUEST_VICTORY_CONDITION),
	]),

## TRIGGER: Combat Bounty
## PURPOSE: Tallies when you or your men take out troops in combat for pay bonuses.
(ti_on_agent_killed_or_wounded, 0, 0,
	[(neq, "$g_mt_mode", abm_tournament),], 
	[
		(store_trigger_param_1, ":agent_victim"),
		(store_trigger_param_2, ":agent_killer"),
		
		(agent_is_active, ":agent_killer"),
		(agent_is_active, ":agent_victim"),
		
		(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
		(get_player_agent_no, ":agent_player"),
		(agent_get_troop_id, ":troop_killer", ":agent_killer"),
		(this_or_next|eq, ":agent_killer", ":agent_player"),
		(troop_slot_eq, ":troop_killer", slot_troop_in_player_merc_group, 1), # One of your squad.
		(val_add, "$oathbound_bounty_count", 1),
		(agent_get_troop_id, ":troop_victim", ":agent_victim"),
		(str_store_troop_name, s21, ":troop_victim"),
		(str_store_troop_name, s22, ":troop_killer"),
		(assign, reg21, "$oathbound_bounty_count"),
		(display_message, "@{s22} dispatched {s21}! ({reg21} total)", gpu_debug),
		
		## Increase rating every so often based on kills.
		(try_begin),
			(store_mod, ":remainder", "$oathbound_bounty_count", OATHBOUND_BOUNTY_RATING_DIVISOR),
			(eq, ":remainder", 0),
			(display_message, "@Your squad's effectiveness in combat has increased your rating!", gpu_green),
			(call_script, "script_oath_change_oathbound_rating", 1),
		(try_end),
	]),
	
## TRIGGER: DEBUGGING - KILL ALL ENEMIES! (Cntl + K)
## PURPOSE: Tallies when you knock out troops of the specified faction.
(1, 0, 0,
	[
		(neq, "$g_mt_mode", abm_tournament),
		(ge, "$oathbound_debugging", 1),
		(key_is_down, key_k),
		(this_or_next|key_is_down, key_left_control),
		(key_is_down, key_right_control),
	], 
	[
		(get_player_agent_no, ":agent_player"),
		# (agent_get_team, ":team_player", ":agent_player"),
		(try_for_agents, ":agent_no"),
			(agent_is_alive, ":agent_no"),
			# (agent_get_team, ":team_no", ":agent_no"),
			(neg|agent_is_ally, ":agent_player"),
			# (neq, ":team_no", ":team_player"),
			(agent_deliver_damage_to_agent, ":agent_player", ":agent_no", 400), 
		(try_end),
		# (display_message, "@DEBUG (Oathbound): Every enemy agent on the battlefield receives 400 damage.", gpu_green),
	]),
	
## TRIGGER: BATTLEFIELD LOOTING
## PURPOSE: Captures any loot the player has picked up during combat to update his gear.
(0, 0, ti_once,
	[], 
	[
		# (display_message, "@DEBUG: THE PLAYER HAS LEFT THE BUILDING!", gpu_red),
	]),
################
# END TRIGGERS #
################
]

oathbound_mission_templates = [

("oathbound_army_training", mtf_arena_fight, -1,
    "oathbound_army_training",
    [
		(2,mtef_visitor_source|mtef_team_0,af_override_weapons|af_override_horse,aif_start_alarmed,1,[]),
		(4,mtef_visitor_source|mtef_team_1,af_override_weapons|af_override_horse,aif_start_alarmed,1,[]),
    ],
    [
		## MISSION INITIALIZATION
		(ti_before_mission_start, 0, 0, [],
			[
				(call_script, "script_oath_quest_set_slot", "qst_oath_fresh_meat", slot_quest_object_state, 0),
				(call_script, "script_oath_quest_set_slot", "qst_oath_fresh_meat", slot_quest_target_state, 1),
				(call_script, "script_change_banners_and_chest"),
			]),
		
		## TAB QUIT+ ##
		common_arena_fight_tab_press,

		(ti_question_answered, 0, 0, [],
			[
				(store_trigger_param_1,":answer"),
				(eq,":answer",0),
				(finish_mission),
			]),
		## TAB QUIT- ##
		
		common_inventory_not_available,
		
		## MISSION END CONDITIONS
		(1, 4, ti_once,
			[
				(this_or_next|main_hero_fallen),
				(num_active_teams_le, 1)
			],
			[
				(try_begin),
					(neg|main_hero_fallen),
					(call_script, "script_oath_quest_set_slot", "qst_oath_fresh_meat", slot_quest_object_state, 1),
				(try_end),
				(jump_to_menu, "mnu_oathbound_fresh_meat_result"),
				(finish_mission),
			]),

	],),

]

def modmerge_mission_templates(orig_mission_templates, check_duplicates = False):
	if( not check_duplicates ):
		orig_mission_templates.extend(oathbound_mission_templates) # Use this only if there are no replacements (i.e. no duplicated item names)
	else:
		# Use the following loop to replace existing entries with same id
		for i in range (0,len(oathbound_mission_templates)-1):
			find_index = find_object(orig_mission_templates, oathbound_mission_templates[i][0]); # find_object is from header_common.py
			if( find_index == -1 ):
				orig_mission_templates.append(oathbound_mission_templates[i])
			else:
				orig_mission_templates[find_index] = oathbound_mission_templates[i]
	
	for i in range (0,len(orig_mission_templates)):
		# brute force add formation triggers to all mission templates with mtf_battle_mode
		if( orig_mission_templates[i][1] & mtf_battle_mode ):
			orig_mission_templates[i][5].extend(oathbound_triggers)
		# # brute force add formation triggers to all mission templates with mtf_arena_fight
		# if( orig_mission_templates[i][1] & mtf_arena_fight ):
			# orig_mission_templates[i][5].extend(oathbound_triggers)
		
# Used by modmerger framework version >= 200 to merge stuff
# This function will be looked for and called by modmerger if this mod is active
# Do not rename the function, though you can insert your own merging calls where indicated
def modmerge(var_set):
	try:
		var_name_1 = "mission_templates"
		orig_mission_templates = var_set[var_name_1]
		modmerge_mission_templates(orig_mission_templates)

	except KeyError:
		errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
		raise ValueError(errstring)
	
	##Extending Mission Templates' trigger lists with triggers appropriate to the templates
	for i in range(len(orig_mission_templates)):
		mt_name = orig_mission_templates[i][0]
		if(mt_name=="bandits_at_night" or mt_name=="castle_visit" or mt_name=="town_fight" or mt_name=="town_center" or mt_name=="visit_town_castle" or mt_name=="village_center" or mt_name=="village_training"):
			orig_mission_templates[i][5].extend(oathbound_triggers)