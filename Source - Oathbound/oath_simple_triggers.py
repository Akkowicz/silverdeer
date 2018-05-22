# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_common import *
from header_operations import *
from header_parties import *
from header_items import *
from header_skills import *
from header_triggers import *
from header_troops import *
from header_music import *
from module_quests import *
from module_constants import *

####################################################################################################################
# Simple triggers are the alternative to old style triggers. They do not preserve state, and thus simpler to maintain.
#
#  Each simple trigger contains the following fields:
# 1) Check interval: How frequently this trigger will be checked
# 2) Operation block: This must be a valid operation block. See header_operations.py for reference.
####################################################################################################################



simple_triggers = [
	
	## TRIGGER: Capture any left click and move you to the Oathbound menu.
	(0,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			(key_clicked, key_left_mouse_button),

			(set_fixed_point_multiplier, 1000),
			(mouse_get_position, pos0),
			(position_get_y, ":y", pos0),
			(gt, ":y", 50), #allows the camp, reports, quests, etc. buttons to be clicked
			
			(start_presentation, "prsnt_oathbound_contract_info"),
			(rest_for_hours_interactive, 9999, 4, 0),
		]),
	
	## TRIGGER: Camera tracking to follow the $oathbound_party.
	(0.5,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			## Switch our position and follow the contracted party.
			(party_is_active, "$oathbound_party"),
			(set_camera_follow_party, "$oathbound_party"),
			(party_relocate_near_party, "p_main_party", "$oathbound_party", 1), 
		]),
		
	
	## TRIGGER: Capture when the $oathbound_party is defeated.
	(0,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			(neg|party_is_active, "$oathbound_party"),
			
			## Give the player a chance to escape capture.
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@{s21}'s army has been defeated.", gpu_red),
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_SEPARATED), # You're separated regardless of outcome.
			
			## ESCAPE CHANCE - Fellow companions still conscious.
			(assign, ":chance_of_escape", 15),
			(try_for_range, ":troop_no", companions_begin, companions_end),
				(main_party_has_troop, ":troop_no"),
				(neg|troop_is_wounded, ":troop_no"),
				(val_add, ":chance_of_escape", 15),
				(call_script, "script_cf_ce_troop_has_ability", ":troop_no", BONUS_ESCAPE_ARTIST),
				(val_add, ":chance_of_escape", 40),
			(try_end),
			(val_clamp, ":chance_of_escape", 0, 95),
			
			## RESOLVE ESCAPE ATTEMPT
			(try_begin),
				## Player escapes!
				(store_random_in_range, ":attempt", 0, 100),
				(lt, ":attempt", ":chance_of_escape"),
				(display_message, "@You have escaped capture!", gpu_green),
				(call_script, "script_oath_detach_from_master_party"),
			(else_try),
				## Player is captured!
				(assign, "$g_encountered_party", "$g_enemy_party"),
				(assign, "$g_player_is_captive", 1),
				(assign,"$auto_menu",-1), #We need this since we may come here by something other than auto_menu
				(assign, "$capturer_party", "$g_encountered_party"),
				(jump_to_menu, "mnu_captivity_start_wilderness"),
			(try_end),
		]),
		
	## TRIGGER: Set-up the player to join $oathbound_party's battles.
	(0,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			
			# $oathbound_master & $oathbound_party currently in combat?
			(party_is_active, "$oathbound_party"),
			(party_get_battle_opponent, ":enemy_lord", "$oathbound_party"),
			(gt, ":enemy_lord", 0),
			
			# Only allow player to join the battle if health is high enough.
			(store_troop_health, ":player_health", "trp_player"),
			(ge, ":player_health", 50),
			
			(start_presentation, "prsnt_oathbound_contract_info"),
		]),
		
	## TRIGGER: Whenever $oathbound_party rests at a location display the oathbound interface.
	(0,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, "$oathbound_pause_at_fiefs", 1),
			
			# $oathbound_master & $oathbound_party currently visiting a fief?
			(party_is_active, "$oathbound_party"),
			(party_get_attached_to, ":party_attached", "$oathbound_party"),
			(gt, ":party_attached", 0),
			(this_or_next|party_slot_eq, ":party_attached", slot_party_type, spt_town),
			(this_or_next|party_slot_eq, ":party_attached", slot_party_type, spt_castle),
			(party_slot_eq, ":party_attached", slot_party_type, spt_village),
			# (get_party_ai_current_behavior, ":ai_behavior", "$oathbound_party"),
			# (eq, ":ai_behavior", ai_bhvr_in_town),
			(ge, "$oathbound_hours_since_visit", 12),
			(assign, "$oathbound_hours_since_visit", 0),
			(start_presentation, "prsnt_oathbound_contract_info"),
		]),
		
	## TRIGGER: Hourly Timers
	(1,[
			## FUNCTION: Countdown of Oathbound contract's remaining hours.
			## LOGIC: Only countdown hours if actively serving your contract.
			(assign, ":pass", 0),
			(try_begin),
				## CASE 1 - You are actively serving within the Lord's party.
				(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
				(assign, ":pass", 1),
			(else_try),
				## CASE 2 - You are away on a mission.
				(eq, "$oathbound_status", OATHBOUND_STATUS_AWAY),
				(eq, "$oathbound_leave_granted", 0), # You're not just on leave.
				(assign, ":pass", 1),
			(try_end),
			(eq, ":pass", 1),
			
			## Reduce our hours.
			(val_sub, "$oathbound_remaining_hours", 1),
			(val_max, "$oathbound_remaining_hours", 0),
			(call_script, "script_oath_lord_decides_if_leave_is_okay"),	# $oathbound_master determines if people can leave.
			(val_add, "$oathbound_time_since_leave", 1),				# Add time since the last time player was on leave.
			(val_add, "$oathbound_hours_since_visit", 1),				# Tracks how long since we last triggered the oathbound interface at a fief.
			
			### DIAGNOSTIC+ ###
			(try_begin),
				(ge, "$oathbound_debugging", 1),
				(store_mod, ":limiter", "$oathbound_remaining_hours", 10),
				(eq, ":limiter", 0),
				(call_script, "script_oath_describe_contract_status", "$oathbound_status"), # Stores to s1
				(assign, reg31, "$oathbound_remaining_hours"),
				(assign, reg32, "$oathbound_time_since_leave"),
				(display_message, "@DEBUG (Oathbound): {reg31} hours remain on contract.  Status is '{s1}'.", gpu_debug),
				(display_message, "@DEBUG (Oathbound): {reg32} hours have passed since your last leave period ended.", gpu_debug),
				
			(try_end),
			### DIAGNOSTIC- ###
			
			## Trigger menu to renew contract once duration expires.
			(lt, "$oathbound_remaining_hours", 1),
			# (map_free),
			(jump_to_menu, "mnu_oathbound_renew_contract"),
		]),
		
	(3,[
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			
			(call_script, "script_oath_describe_oathbound_party_actions"), # Stores s11 (description)
		]),
		
	## TRIGGER: Quest "The Butcher's Bill" - Tracks when cattle are brought to the main army.
	(0.5, [
			(check_quest_active, "qst_oath_butchers_bill"),
			(neg|check_quest_concluded, "qst_oath_butchers_bill"),
			(quest_get_slot, ":party_cattle", "qst_oath_butchers_bill", slot_quest_target_party),
			(party_is_active, "$oathbound_party"),
			(try_begin),
				(neg|party_is_active, ":party_cattle"),
				(quest_set_slot, "qst_oath_butchers_bill", slot_quest_target_party, -1),
			(try_end),
			(party_is_active, ":party_cattle"),
			(store_distance_to_party_from_party, ":dist", "$oathbound_party", ":party_cattle"),
			(lt, ":dist", 5),
			(party_count_members_of_type, ":heads_of_cattle", ":party_cattle", "trp_cattle"),
			(remove_party, ":party_cattle"),
			(call_script, "script_oath_quest_change_slot", "qst_oath_butchers_bill", slot_quest_temp_slot, ":heads_of_cattle"),
			(call_script, "script_quest_oathbound_butchers_bill", OATH_QUEST_UPDATE),
			(call_script, "script_quest_oathbound_butchers_bill", OATH_QUEST_VICTORY_CONDITION),
		]),
		
	## TRIGGER: Quest "Courage Comes in Casks" - Tracks if you have sufficient casks of ale.
	(3, [
			(check_quest_active, "qst_oath_courage_casks"),
			(neg|check_quest_concluded, "qst_oath_courage_casks"),
			(store_item_kind_count, ":casks_carried", "itm_ale", "trp_player"),
			(quest_get_slot, ":casks_required", "qst_oath_courage_casks", slot_quest_target_amount),
			(try_begin),
				## You have enough to finish the quest.
				(ge, ":casks_carried", ":casks_required"),
				(val_min, ":casks_carried", ":casks_required"),
				(call_script, "script_oath_quest_set_slot", "qst_oath_courage_casks", slot_quest_temp_slot, ":casks_carried"),
				(call_script, "script_oath_quest_change_state", "qst_oath_courage_casks", OATH_QUEST_STAGE_GOAL_MET),
				(call_script, "script_quest_oathbound_courage_casks", OATH_QUEST_UPDATE),
			(else_try),
				## You have a partial amount, but not enough.
				(neg|quest_slot_eq, "qst_oath_courage_casks", slot_quest_temp_slot, ":casks_carried"),
				(call_script, "script_oath_quest_set_slot", "qst_oath_courage_casks", slot_quest_temp_slot, ":casks_carried"),
				(call_script, "script_oath_quest_change_state", "qst_oath_courage_casks", OATH_QUEST_STAGE_BEGUN),
				(call_script, "script_quest_oathbound_courage_casks", OATH_QUEST_UPDATE),
			(try_end),
		]),
		
	## TRIGGER: Quest "Scouting Ahead" - Tracks when you near any of the assigned waypoints.
	(0.5, [
			(check_quest_active, "qst_oath_scouting_ahead"),
			(neg|check_quest_concluded, "qst_oath_scouting_ahead"),
			
			
			## WAYPOINT #1
			(try_begin),
				(party_is_active, "$oathbound_waypoint_1"),
				(neq, "$oathbound_waypoint_1_visited", 1),
				(store_distance_to_party_from_party, ":distance", "$oathbound_waypoint_1", "p_main_party"),
				(lt, ":distance", 3),
				(assign, "$oathbound_waypoint_1_visited", 1),
				(str_store_party_name, s21, "$oathbound_waypoint_1"),
				(str_store_string, s65, "@You have scouted around the area of {s21}.", gpu_green),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_UPDATE),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_VICTORY_CONDITION),
			(try_end),
			
			## WAYPOINT #2
			(try_begin),
				(party_is_active, "$oathbound_waypoint_2"),
				(neq, "$oathbound_waypoint_2_visited", 1),
				(store_distance_to_party_from_party, ":distance", "$oathbound_waypoint_2", "p_main_party"),
				(lt, ":distance", 3),
				(assign, "$oathbound_waypoint_2_visited", 1),
				(str_store_party_name, s21, "$oathbound_waypoint_2"),
				(str_store_string, s65, "@You have scouted around the area of {s21}.", gpu_green),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_UPDATE),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_VICTORY_CONDITION),
			(try_end),
			
			## WAYPOINT #3
			(try_begin),
				(party_is_active, "$oathbound_waypoint_3"),
				(neq, "$oathbound_waypoint_3_visited", 1),
				(store_distance_to_party_from_party, ":distance", "$oathbound_waypoint_3", "p_main_party"),
				(lt, ":distance", 3),
				(assign, "$oathbound_waypoint_3_visited", 1),
				(str_store_party_name, s21, "$oathbound_waypoint_3"),
				(str_store_string, s65, "@You have scouted around the area of {s21}.", gpu_green),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_UPDATE),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_VICTORY_CONDITION),
			(try_end),
		]),
		
	## TRIGGER: Quest "Only the Finest" - Tracks if you have the requested item.
	(3, [
			(check_quest_active, "qst_oath_only_the_finest"),
			(neg|check_quest_concluded, "qst_oath_only_the_finest"),
			(quest_get_slot, ":item_no", "qst_oath_only_the_finest", slot_quest_target_amount),
			(quest_get_slot, ":imod", "qst_oath_only_the_finest", slot_quest_temp_slot),
			(try_begin),
				# CASE 1 - We didn't have the item and now do.  Upgrade to goal met.
				(quest_slot_eq, "qst_oath_only_the_finest", slot_quest_current_state, OATH_QUEST_STAGE_BEGUN),
				(call_script, "script_cf_oath_player_has_item_with_modifier", ":item_no", ":imod"), # Returns reg1 (inventory slot item is in)
				(call_script, "script_oath_quest_change_state", "qst_oath_only_the_finest", OATH_QUEST_STAGE_GOAL_MET),
				(call_script, "script_quest_oathbound_only_the_finest", OATH_QUEST_UPDATE),
			(else_try),
				# CASE 2 - We had the item, but have lost it.  Downgrade to starting state.
				(quest_slot_eq, "qst_oath_only_the_finest", slot_quest_current_state, OATH_QUEST_STAGE_GOAL_MET),
				(try_begin),
					(call_script, "script_cf_oath_player_has_item_with_modifier", ":item_no", ":imod"), # Returns reg1 (inventory slot item is in)
				(else_try),
					(call_script, "script_oath_quest_change_state", "qst_oath_only_the_finest", OATH_QUEST_STAGE_BEGUN),
					(call_script, "script_quest_oathbound_only_the_finest", OATH_QUEST_UPDATE),
				(try_end),
			(try_end),
		]),
		
	## TRIGGER: In-Party Time of Day Functions
	(1, [
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			(store_time_of_day, ":time"),
			
			## QUEST: "Fresh Meat" / Quest #13 - Practice fight menu during the evening.
			(try_begin),
				(check_quest_active, "qst_oath_fresh_meat"),
				(neg|check_quest_concluded, "qst_oath_fresh_meat"),
				(eq, ":time", 19), # Dusk/Evening
				(neq, "$oathbound_exit_allowed", 0), # If you can't leave the party, it is probably busy.
				(jump_to_menu, "mnu_oathbound_fresh_meat"),
			(try_end),
			
			## QUEST: "Fresh Meat" / Quest #13 - Practice fight menu during the evening.
			(try_begin),
				(check_quest_active, "qst_oath_fresh_meat"),
				(neg|check_quest_concluded, "qst_oath_fresh_meat"),
				(quest_slot_eq, "qst_oath_fresh_meat", slot_quest_target_state, 1),
				(jump_to_menu, "mnu_oathbound_fresh_meat_result"),
			(try_end),
			
			
		]),
		
	## TRIGGER: Faction relation tracking if your CONTRACTED.
	(24, [
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
			(set_show_messages, 0),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(set_show_messages, 1),
		]),
]

# Used by modmerger framework version >= 200 to merge stuff
def modmerge(var_set):
    try:
        var_name_1 = "simple_triggers"
        orig_simple_triggers = var_set[var_name_1]
        orig_simple_triggers.extend(simple_triggers)
    except KeyError:
        errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
        raise ValueError(errstring)