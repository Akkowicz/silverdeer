# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_common import *
from header_operations import *
from module_constants import *
from header_parties import *
from header_triggers import *
from module_quests import *
from header_items import *

####################################################################################################################
# scripts is a list of script records.
# Each script record contains the following two fields:
# 1) Script id: The prefix "script_" will be inserted when referencing scripts.
# 2) Operation block: This must be a valid operation block. See header_operations.py for reference.
####################################################################################################################

scripts = [
####################################################################################################################################
############                                              COMMON SCRIPTS                                                 ###########
####################################################################################################################################

# script_oath_join_master_party
# PURPOSE: Merges the player party into the $oathbound_master's party.
# EXAMPLE: (call_script, "script_oath_join_master_party", ":party_no"),
("oath_join_master_party",
    [	
		#needed to stop bug where parties attack the old player party
		(call_script, "script_set_parties_around_player_ignore_player", 2, 4),
		
		## SECTION: GLOBAL INITIALIZATION
		(assign, "$oathbound_leave_granted", 0),	# Covered when you come back, but just in case it should always be set here on a rejoin.
		(assign, "$oathbound_master", "$g_talk_troop"),
		(troop_get_slot, "$oathbound_party", "$oathbound_master", slot_troop_leaded_party), 
		(assign, ":party_no", "$oathbound_party"),
		(assign, "$oathbound_exit_allowed", 1),
		(assign, "$oathbound_betrayed_faction", 0),
		(assign, "$oathbound_hours_since_visit", 0),
		
		## SECTION: PLAYER DISPLAY
		(str_store_troop_name, s21, "$oathbound_master"),
		(party_get_num_companion_stacks, reg2, "p_main_party"),
		(display_message, "@{reg2?Your band of followers has:You have} rejoined {s21}'s army.", gpu_green),
		
		## SECTION: COMPANION STORAGE - Tracks which companions were a part of our party prior to joining.
		(try_for_range, ":troop_no", companions_begin, companions_end),
			(try_begin),
				(main_party_has_troop, ":troop_no"),
				(troop_set_slot, ":troop_no", slot_troop_in_player_merc_group, 1),
			(else_try),
				(troop_set_slot, ":troop_no", slot_troop_in_player_merc_group, 0),
			(try_end),
		(try_end),
		
		## SECTION: PRISONER TRANSFER - Moves player's prisoners to $oathbound_party and compensates the player.
		(assign, ":orig_talk_troop", "$g_talk_troop"), # Stored since we'll need to setup this global for prisoner costs.
		(assign, ":orig_current_town", "$current_town"), # Stored since we'll need to setup this global for prisoner costs.
		(party_get_num_prisoner_stacks, ":stack_limit", "p_main_party"),
		(assign, ":compensation_prisoners", 0),
		(assign, ":relation_change_total", 0),
		(try_for_range_backwards, ":stack_no", 0, ":stack_limit"),
			(party_prisoner_stack_get_troop_id, ":stack_troop","p_main_party",":stack_no"),
			(party_prisoner_stack_get_size, ":stack_size", "p_main_party", ":stack_no"),
			# (neg|troop_is_hero, ":stack_troop"),
			## Transfer the troops from the player party to $oathbound_party.
			(party_remove_prisoners, "p_main_party", ":stack_troop", ":stack_size"),
			(party_add_prisoners, ":party_no", ":stack_troop", ":stack_size"),
			## Determine the prisoner's value.
			(try_begin),
				## RANSOM: Standard troops.
				(neg|troop_is_hero, ":stack_troop"),
				(assign, "$g_talk_troop", "$oathbound_master"),
				# Use a town in $oathbound_master's faction.
				(assign, "$current_town", "p_town_1"), # Sargoth is our default.
				(store_troop_faction, ":faction_lord", "$oathbound_master"),
				(try_for_range, ":town_no", towns_begin, towns_end),
					(store_faction_of_party, ":faction_town", ":town_no"),
					(eq, ":faction_lord", ":faction_town"),
					(assign, "$current_town", ":town_no"),
				(try_end),
				(call_script, "script_game_get_prisoner_price", ":stack_troop"),
				(assign, ":cost_per_troop", reg0),
				(troop_get_slot, ":cost_per_troop", ":stack_troop", slot_troop_purchase_cost),
			(else_try),
				## RANSOM: Lords, Ladies, Pretenders & Companions.
				(troop_is_hero, ":stack_troop"),
				(call_script, "script_calculate_ransom_amount_for_troop", ":stack_troop"),
				(assign, ":cost_per_troop", reg0),
				# Ransomable nobility also result in relation gain with your lord.
				(store_div, ":relation_change", ":cost_per_troop", 2000),
				(val_clamp, ":relation_change", 1, 6),
				(val_add, ":relation_change_total", ":relation_change"),
			(else_try),
				## RANSOM: Default.  Shouldn't ever be used.
				(assign, ":cost_per_troop", 50),
			(try_end),
			(val_mul, ":cost_per_troop", OATHBOUND_PRISONER_COMPENSATION),
			(val_div, ":cost_per_troop", 100),
			(store_mul, ":cost_troop_stack", ":cost_per_troop", ":stack_size"),
			(val_add, ":compensation_prisoners", ":cost_troop_stack"),
		(try_end),
		(assign, "$g_talk_troop", ":orig_talk_troop"),	 # Restoring our original value to this global.
		(assign, "$current_town", ":orig_current_town"), # Restoring our original value to this global.
		
		## SECTION: TROOP TRANSFER - Transfers non-hero troops to $oathbound_party and compensates you for their cost.
		(party_get_num_companion_stacks, ":stack_limit", "p_main_party"),
		(assign, ":compensation_troops", 0),
		(try_for_range_backwards, ":stack_no", 0, ":stack_limit"),
			(party_stack_get_troop_id, ":stack_troop","p_main_party",":stack_no"),
			(party_stack_get_size, ":stack_size", "p_main_party", ":stack_no"),
			(neg|troop_is_hero, ":stack_troop"),
			## Transfer the troops from the player party to $oathbound_party.
			(party_remove_members, "p_main_party", ":stack_troop", ":stack_size"),
			(party_add_members, ":party_no", ":stack_troop", ":stack_size"),
			## Determine their purchasing cost.
			(troop_get_slot, ":cost_per_troop", ":stack_troop", slot_troop_purchase_cost),
			(val_mul, ":cost_per_troop", OATHBOUND_TROOP_COMPENSATION_RATE),
			(val_div, ":cost_per_troop", 100),
			(store_mul, ":cost_troop_stack", ":cost_per_troop", ":stack_size"),
			(val_add, ":compensation_troops", ":cost_troop_stack"),
		(try_end),
		
		## SECTION: COMPENSATION - Compensate the player for any transferred troops & prisoners.
		(try_begin),
			(ge, ":compensation_troops", 1),
			(str_store_string, s11, "@ as compensation for your transferred troops"),
			(call_script, "script_oath_pay_player_because_s11", ":compensation_troops"),
		(try_end),
		(try_begin),
			(ge, ":compensation_prisoners", 1),
			(str_store_string, s11, "@ as compensation for your transferred prisoners"),
			(call_script, "script_oath_pay_player_because_s11", ":compensation_prisoners"),
		(try_end),
		(try_begin),
			(neq, ":relation_change_total", 0),
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@{s21} is pleased with noble captives you have brought him.", gpu_green),
			(call_script,"script_change_player_relation_with_troop", "$oathbound_master", ":relation_change_total", 0),
		(try_end),
		
		## SECTION: ATTACHMENT - Set player party as part of $oathbound_party & align camera.
		(party_attach_to_party, "p_main_party", ":party_no"),
        (set_camera_follow_party, ":party_no"),
        (party_set_flags, ":party_no", pf_always_visible, 1),
		(party_set_flags, "p_main_party", pf_always_visible, 0),
        (disable_party, "p_main_party"),
    ]),

# script_oath_detach_from_master_party
# PURPOSE: Splits the player party from the $oathbound_master's party ($oathbound_party).
# EXAMPLE: (call_script, "script_oath_detach_from_master_party"),
("oath_detach_from_master_party",
    [
	    ## Splits out the player party from $oathbound_party.
		(enable_party, "p_main_party"),
        (party_detach, "p_main_party"),
		
		## Moves the player's party to be near $oathbound_party if it still exists.
		(try_begin),
			(party_is_active, "$oathbound_party"),
			(party_relocate_near_party, "p_main_party", "$oathbound_party", 2),
			(party_set_flags, "$oathbound_party", pf_always_visible, 0),
		(try_end),	
		
		(troop_set_slot, "trp_player", slot_troop_leaded_party, "p_main_party"),
		
		## Resets our camera viewpoint to follow the player's party.
	    (set_camera_follow_party, "p_main_party"),
		(assign, "$g_player_icon_state", pis_normal),
		(party_set_flags, "p_main_party", pf_always_visible, 1),
		
		## SECTION: PLAYER DISPLAY
		(str_store_troop_name, s21, "$oathbound_master"),
		(party_get_num_companion_stacks, reg2, "p_main_party"),
		(display_message, "@{reg2?Your band of followers has:You have} split off from {s21}'s army.", gpu_green),
	]),
	
# script_oath_set_contract_status
# PURPOSE: Sets your contract status and handles any catch-all updates that should happen based on status.
# EXAMPLE: (call_script, "script_oath_set_contract_status", ":new_status"),
("oath_set_contract_status",
    [
	    (store_script_param, ":new_status", 1),
		
		(assign, ":old_status", "$oathbound_status"),
		
		# $oathbound_status 			= (Int)		- This tracks the main status of your contract via a constant.
		# OATHBOUND_STATUS_NOT_HIRED  = 0				# No contract in effect.
		# OATHBOUND_STATUS_CONTRACTED = 1				# On contract, within the lord's party.
		# OATHBOUND_STATUS_AWAY       = 2				# Away from the party on a mission or during periods of leave.
		# OATHBOUND_STATUS_SEPARATED  = 3				# Separated due to lord being captured.
		# OATHBOUND_STATUS_DESERTER   = 4				# Desertion status.
		# OATHBOUND_STATUS_END        = 5				# This needs to be +1 from the last status used.
		
		(try_begin),
			(neg|is_between, ":new_status", OATHBOUND_STATUS_NOT_HIRED, OATHBOUND_STATUS_END),
			(assign, reg31, ":new_status"),
			(display_message, "@ERROR (Oathbound) - Invalid status #{reg31} requested.", gpu_red),
		(else_try),
			(assign, "$oathbound_status", ":new_status"),
			(try_begin),
				(ge, "$oathbound_debugging", 1),
				(call_script, "script_oath_describe_contract_status", "$oathbound_status"), # Stores to s1
				(display_message, "@DEBUG (Oathbound): Contract status set to {s1}.", gpu_debug),
			(try_end),
		(try_end),
		
		## OATHBOUND EVENT LOG
		(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_STATUS_CHANGE, ":new_status"),
		
		########################
		### NOT_HIRED -> ??? ###
		########################
		
		## NOT_HIRED -> CONTRACTED (Contract Begins)
		# Trigger: oath_dialog.py
		(try_begin),
			(eq, ":old_status", OATHBOUND_STATUS_NOT_HIRED),
			(eq, ":new_status", OATHBOUND_STATUS_CONTRACTED),
			
			## Setup contract timer.
			#store joining date in global variable for payment system
			(store_current_day, "$join_date"),
			(store_current_hours, ":start_hours"),
			(assign, "$oathbound_contract_started", ":start_hours"),
			(assign, "$oathbound_remaining_hours", OATHBOUND_CONTRACT_DURATION),
			
			## Merge the player party into the lord's party.
			(call_script, "script_oath_join_master_party"),
			
			## Setup faction relations that allow you to join $oathbound_party's battles.
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			
			## Setup initial rank.
			(store_troop_faction, ":commander_faction", "$oathbound_master"),
			(faction_get_slot, ":initial_rank", ":commander_faction", slot_faction_oathbound_rank),
			(val_max, ":initial_rank", OATHBOUND_RANK_INITIATE),
			(faction_set_slot, ":commander_faction", slot_faction_oathbound_rank, ":initial_rank"),
			(try_begin),
				(ge, "$oathbound_debugging", 1),
				(call_script, "script_oath_describe_oathbound_rank", ":initial_rank"), # Stores s1 (rank name), s2 (rank title)
				(str_store_troop_name, s21, "trp_player"),
				(display_message, "@DEBUG (Oathbound): Initial rank set to {s1} with title '{s2}{s21}'.", gpu_debug),
			(try_end),
			
			## Display joining status.
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@You have vowed to serve {s21}!"),
			(assign, "$g_infinite_camping", 1),
			(rest_for_hours_interactive, 24 * 365, 5, 1),
			
			## Reset Leave Status
			(assign, "$oathbound_time_since_leave", 0),
			
			## Reset contract based globals.
			(assign, "$oathbound_bounty_count", 0),
			(assign, "$oathbound_contract_periods", 0),
		(try_end),
		
		#########################
		### CONTRACTED -> ??? ###
		#########################
		
		## CONTRACTED -> NOT_HIRED (Standard Separation)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":new_status", OATHBOUND_STATUS_NOT_HIRED),
			
			(call_script, "script_oath_player_faction_relations", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(call_script, "script_oath_detach_from_master_party"),
			(rest_for_hours, 0,0,0),
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@You have been released from your vow to {s21}!"),
			# Cancel any active quests.
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
			(try_end),
			# Reset all relevant globals.
			(assign, "$oathbound_bounty_count", 0),
			
		(try_end),
		
		## CONTRACTED -> AWAY (On Leave) (Taking vacation)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":new_status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 1),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(call_script, "script_oath_detach_from_master_party"),
			(rest_for_hours, 0,0,0),
			# Begin "Leave of Duty" Quest.
			(call_script, "script_quest_oathbound_leave", OATH_QUEST_BEGIN), 
		(try_end),
		
		## CONTRACTED -> AWAY (On Mission)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":new_status", OATHBOUND_STATUS_AWAY),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(call_script, "script_oath_detach_from_master_party"),
			(rest_for_hours, 0,0,0),
		(try_end),
		
		## CONTRACTED -> SEPARATED (From Combat)
		#  Trigger: oath_simple_triggers.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_SEPARATED),
			(eq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(call_script, "script_oath_detach_from_master_party"),
			# Cancel any active quests.
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
			(try_end),
			# Trigger "Separated" Quest.
			(call_script, "script_quest_oathbound_separated", OATH_QUEST_BEGIN),
		(try_end),
		
		## CONTRACTED -> DESERTER (From Oathbound Main Menu)
		#  Trigger: oath_game_menus.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_DESERTER),
			(eq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(call_script, "script_oath_detach_from_master_party"),
			# Cancel any active quests.
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
			(try_end),
			# Begin "Desertion" Quest.
			(call_script, "script_quest_oathbound_desertion", OATH_QUEST_BEGIN),
		(try_end),
		
		
		#########################
		###    AWAY -> ???    ###
		#########################
		
		## AWAY (on mission) -> CONTRACTED (Rejoining)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":old_status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 0),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(call_script, "script_oath_join_master_party"),
			## Trigger any completed quests as necessary.
			(call_script, "script_oath_check_quest_success_if_active", "qst_oath_courage_casks"), # Quest #7
		(try_end),
		
		## AWAY (on leave) -> CONTRACTED (Rejoining)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":old_status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 1),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(call_script, "script_oath_join_master_party"),
			(assign, "$oathbound_leave_granted", 0),
			(assign, "$oathbound_time_since_leave", 0),
			# Succeed "Leave of Duty" Quest.
			(call_script, "script_quest_oathbound_leave", OATH_QUEST_SUCCEED),
		(try_end),
		
		## AWAY (on leave) -> DESERTER (Leave Expired)
		#  Trigger: module_simple_triggers.py "quest expired" -> module_scripts.py "end_quest" -> oath_scripts.py "script_quest_oathbound_leave"
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_DESERTER),
			(eq, ":old_status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 1),
			(eq, "$oathbound_betrayed_faction", 0),
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@You have stayed away from {s21}'s army beyond your allowed time and have been branded a deserter!  You may yet keep your head from the headsman's block if you return immediately.", gpu_red),
			# Cancel any active quests.
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
			(try_end),
			# Begin "Desertion" Quest.
			(call_script, "script_quest_oathbound_desertion", OATH_QUEST_BEGIN),
		(try_end),
		
		## AWAY (on leave/on mission) -> DESERTER (Betrayal)
		#  Trigger: module_game_menus.py "mnu_pre_join"
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_DESERTER),
			(eq, ":old_status", OATHBOUND_STATUS_AWAY),
			(ge, "$oathbound_betrayed_faction", 1),
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@Your actions against your allies have been noticed and you have been branded a deserter!  You may yet keep your head from the headsman's block if you return immediately.", gpu_red),
			(call_script, "script_oath_cancel_quest_if_active", "qst_oath_leave"), # Quest: Leave of Duty
			# Cancel any active quests.
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
			(try_end),
			# Begin "Desertion" Quest.
			(call_script, "script_quest_oathbound_desertion", OATH_QUEST_BEGIN),
		(try_end),
		
		
		#########################
		### SEPARATED -> ???  ###
		#########################
		
		## SEPARATED -> CONTRACTED (Rejoining)
		#  Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":old_status", OATHBOUND_STATUS_SEPARATED),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(call_script, "script_oath_join_master_party"),
			# Succeed "Separated" Quest.
			(call_script, "script_quest_oathbound_separated", OATH_QUEST_SUCCEED),
		(try_end),
		
		
		#########################
		###  DESERTER -> ???  ###
		#########################
		
		## DESERTER -> NOT_HIRED (Desertion grace period passed)
		#  Trigger: module_simple_triggers.py "quest expired" -> module_scripts.py "end_quest" -> oath_scripts.py "script_quest_oathbound_desertion"
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_NOT_HIRED),
			(eq, ":old_status", OATHBOUND_STATUS_DESERTER),
			# Reset all relevant globals.
			(assign, "$oathbound_master", -1),
			(assign, "$oathbound_party", -1),
			(assign, "$oathbound_bounty_count", 0),
			(assign, "$oathbound_contract_periods", 0),
		(try_end),
		
		## DESERTER -> CONTRACTED (Rejoined during desertion grace period)
		# Trigger: oath_dialogs.py
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, ":old_status", OATHBOUND_STATUS_DESERTER),
			(call_script, "script_oath_player_faction_relations", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(call_script, "script_oath_join_master_party"),
			(assign, "$oathbound_leave_granted", 0), # Just in case.
			# Succeed "Desertion" Quest.
			(call_script, "script_quest_oathbound_desertion", OATH_QUEST_SUCCEED),
		(try_end),
		
		
		#########################
		###    MISC -> ???    ###
		#########################
		
		## CONTRACT TERMINATED (Unusual Termination Catch-all)
		(try_begin),
			(eq, ":new_status", OATHBOUND_STATUS_NOT_HIRED),
			(neq, ":old_status", OATHBOUND_STATUS_CONTRACTED),
			# Reset all relevant globals.
			(assign, "$oathbound_master", -1),
			(assign, "$oathbound_party", -1),
			(assign, "$oathbound_bounty_count", 0),
			
		(try_end),
	]),
	
# script_oath_force_rejoin_if_no_active_missions
# PURPOSE: Checks if any missions are still active.  If not then it forces the player to rejoin $oathbound_party after a dialog turn-in.
# EXAMPLE: (call_script, "script_oath_force_rejoin_if_no_active_missions"),
("oath_force_rejoin_if_no_active_missions",
    [
	    (try_begin),
			## FILTER - Player still has an active mission requiring him not to be in $oathbound_party.
			(call_script, "script_cf_oath_mission_is_active"),
		(else_try),
			## FILTER - Player is on granted leave.
			(eq, "$oathbound_leave_granted", 1),
		(else_try),
			## FILTER - Player is already within $oathbound_party when turning the quest in.
			(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
		(else_try),
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),
		(try_end),
	]),
	
# script_oath_lord_decides_if_leave_is_okay
# PURPOSE: This is the $oathbound_master's checklist to see if he is letting people leave his camp at this time.
# EXAMPLE: (call_script, "script_oath_lord_decides_if_leave_is_okay"), # Stores s41 (reason to block)
("oath_lord_decides_if_leave_is_okay",
    [
	    (assign, ":original_value", "$oathbound_exit_allowed"),
		(assign, "$oathbound_exit_allowed", 1), # Standard default is that it is okay.
		
		(get_party_ai_current_behavior, ":ai_behavior", "$oathbound_party"),	# $oathbound_party's immediate behavior.
		# (get_party_ai_current_object, ":ai_focus", "$oathbound_party"),			# $oathbound_party's immediate focus.
		(get_party_ai_behavior, ":ai_behavior_plan", "$oathbound_party"),		# $oathbound_party's planned behavior.
		(get_party_ai_object, ":ai_focus_plan", "$oathbound_party"),			# $oathbound_party's planned focus.
		
		## CASE #1 - $oathbound_master is currently in battle.
		(try_begin),
			(party_is_active, "$oathbound_party"),
			(party_get_battle_opponent, ":enemy_lord", "$oathbound_party"),
			(gt, ":enemy_lord", 0),
			(assign, "$oathbound_exit_allowed", 0),
			(str_store_string, s41, "@has closed off leaving the army due to being in battle."),
		(try_end),
		
		## CASE #2 - $oathbound_party is raiding a village.
		(try_begin),
			(eq, ":ai_behavior", ai_bhvr_hold),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(is_between, ":ai_focus_plan", villages_begin, villages_end),
			(assign, "$oathbound_exit_allowed", 0),
			(str_store_party_name, s21, ":ai_focus_plan"),
			(str_store_string, s41, "@has closed off leaving the army while he is raiding {s21}."),
		(try_end),
		
		## DEBUG OUTPUT: Let us know if he has changed his mind.
		(try_begin),
			(ge, "$oathbound_debugging", 1),
			(neq, ":original_value", "$oathbound_exit_allowed"),
			(str_store_troop_name, s32, "$oathbound_master"),
			(try_begin),
				(eq, "$oathbound_exit_allowed", 0),
				(display_message, "@DEBUG (Oathbound): {s32} {s41}.", gpu_red),
			(else_try),
				(display_message, "@DEBUG (Oathbound): {s32} has decided to ALLOW troops to leave his army.", gpu_green),
			(try_end),
		(try_end),
	]),
	
# script_oath_word_wrap_text (WSE DEPENDENT)
# PURPOSE: This is the $oathbound_master's checklist to see if he is letting people leave his camp at this time.
# EXAMPLE: (call_script, "script_oath_word_wrap_text", ":line_length"), # Input s1, Returns s1 (wrapped text), reg1 (# lines)
("oath_word_wrap_text",
    [
	    (store_script_param, ":line_length", 1),
		
		(assign, ":last_space", 0),
		(assign, ":chars_this_line", 0),
		(assign, ":start_grab", 0),
		(assign, ":number_of_lines", 1), # Start with 1 in the event the text doesn't need wrapping.
		(str_clear, s2),
		(str_clear, s4),
		(str_store_string, s3, "@ "), # Blank Space for control
		(str_get_char, ":blank", s3, 0),
		
		(str_length, ":text_length", s1),
		(try_for_range, ":char", 0, ":text_length"),
		
			## Keep track of our last space value so we know where to wrap things.
			(str_get_char, ":char_value", s1, ":char"),
			(try_begin),
				(eq, ":char_value", ":blank"),
				(assign, ":last_space", ":char"),
			(try_end),
			
			## Check when we exceed our intended line_length.
			(val_add, ":chars_this_line", 1),
			(try_begin),
				(ge, ":chars_this_line", ":line_length"),
				(store_sub, ":grab_length", ":last_space", ":start_grab"),
				(str_store_substring, s3, s1, ":start_grab", ":grab_length"), 	# This is our wrapped line.
				(store_add, ":start_remainder", ":last_space", 1),
				(str_store_substring, s2, s1, ":start_remainder"), 				# This is the remainder.
				(str_store_string, s4, "@{s4}{s3}^"), 							# Wrapped line carried over with our carriage return.
				# Reset our repeat back to the beginning of the new line.
				(val_add, ":number_of_lines", 1),
				(store_sub, ":chars_this_line", ":char", ":last_space"),
				(store_add, ":start_grab", ":last_space", 1),
			(try_end),
		(try_end),
		# We only need the wrapped output if number of lines exceeded 1.
		(try_begin),
			(ge, ":number_of_lines", 2),
			(str_store_string, s1, "@{s4}{s2}"), # s4 was our wrapped text line by line.
		(try_end),
		(assign, reg1, ":number_of_lines"),
	]),
	
# script_oath_describe_oathbound_party_actions
# PURPOSE: Look at the behavior of $oathbound_party and try to determine what they're doing to display for the player.
# EXAMPLE: (call_script, "script_oath_describe_oathbound_party_actions"), # Returns s11 (description)
("oath_describe_oathbound_party_actions",
    [
	    (party_is_active, "$oathbound_party"),
		(get_party_ai_current_behavior, ":ai_behavior", "$oathbound_party"),	# $oathbound_party's immediate behavior.
		(get_party_ai_current_object, ":ai_focus", "$oathbound_party"),			# $oathbound_party's immediate focus.
		(get_party_ai_behavior, ":ai_behavior_plan", "$oathbound_party"),		# $oathbound_party's planned behavior.
		(get_party_ai_object, ":ai_focus_plan", "$oathbound_party"),			# $oathbound_party's planned focus.
		## Short Term Focus
		(try_begin),
			(party_is_active, ":ai_focus"),
			(str_store_party_name, s12, ":ai_focus"),
		(else_try),
			(str_store_string, s12, "@<Bad Input>"),
		(try_end),
		
		(try_begin),
			(eq, ":ai_behavior", ai_bhvr_hold),
			(str_store_string, s11, "@camping"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_travel_to_party),
			(str_store_string, s11, "@travelling to {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_patrol_location),
			(str_store_string, s11, "@patrolling around {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_patrol_party),
			(str_store_string, s11, "@patrolling near {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_attack_party),
			(str_store_string, s11, "@attacking {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_avoid_party),
			(str_store_string, s11, "@trying to avoid {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_travel_to_point),
			(str_store_string, s11, "@travelling to {s12} (point)"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_negotiate_party),
			(str_store_string, s11, "@negotiating with {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_in_town),
			(str_store_string, s11, "@staying at {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_travel_to_ship),
			(str_store_string, s11, "@travelling to a ship"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_escort_party),
			(str_store_string, s11, "@escorting {s12}"),
		(else_try),
			(eq, ":ai_behavior", ai_bhvr_driven_by_party),
			(str_store_string, s11, "@running from {s12}"),
		(try_end),
		(str_store_party_name, s14, "$oathbound_party"),
		(str_store_string, s18, "@DEBUG (Oathbound): {s14} is currently {s11}. (Immediate)"),
		
		(try_begin),
			(party_is_active, ":ai_focus_plan"),
			(str_store_party_name, s13, ":ai_focus_plan"),
		(else_try),
			(str_store_string, s13, "@<Bad Input>"),
		(try_end),
		
		(try_begin),
			(eq, ":ai_behavior_plan", ai_bhvr_hold),
			(str_store_string, s11, "@camping"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(str_store_string, s11, "@travelling to {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_patrol_location),
			(str_store_string, s11, "@patrolling around {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_patrol_party),
			(str_store_string, s11, "@patrolling near {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_attack_party),
			(str_store_string, s11, "@attacking {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_avoid_party),
			(str_store_string, s11, "@trying to avoid {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(str_store_string, s11, "@travelling to {s12} (point)"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_negotiate_party),
			(str_store_string, s11, "@negotiating with {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_in_town),
			(str_store_string, s11, "@staying at {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_ship),
			(str_store_string, s11, "@travelling to a ship"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_escort_party),
			(str_store_string, s11, "@escorting {s12}"),
		(else_try),
			(eq, ":ai_behavior_plan", ai_bhvr_driven_by_party),
			(str_store_string, s11, "@running from {s12}"),
		(try_end),
		(str_store_party_name, s14, "$oathbound_party"),
		(str_store_string, s19, "@DEBUG (Oathbound): {s14} is currently {s11}. (Planned)"),
		
		(try_begin), ## BEHAVIOR: RAIDING / SIEGING (Immediate: Hold, Plan: Travel to Party/Point)
			(eq, ":ai_behavior", ai_bhvr_hold),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@{s1}"),
		(else_try), ## BEHAVIOR: FLEEING, WANTS TO VISIT LOCATION (Immediate: Avoiding, Plan: Travel to Party/Point)
			(eq, ":ai_behavior", ai_bhvr_avoid_party),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(is_between, ":ai_focus_plan", centers_begin, centers_end),
			(str_store_string, s11, "@attempting to reach {s13}, but has been forced to divert by {s12} forces"),
		(else_try), ## BEHAVIOR: FLEEING, WANTS TO VISIT ARMY (Immediate: Avoiding, Plan: Travel to Party/Point)
			(eq, ":ai_behavior", ai_bhvr_avoid_party),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(str_store_string, s11, "@attempting to reach {s13}, but has been forced to change direction by {s12} forces"),
		(else_try), ## BEHAVIOR: TRAVELLING TO PARTY (Immediate: Travel to Party/Point, Plan: Travel to Party/Point)
			(this_or_next|eq, ":ai_behavior", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior", ai_bhvr_travel_to_point),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_travel_to_party),
			(eq, ":ai_behavior_plan", ai_bhvr_travel_to_point),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@travelling to {s1}"),
		(else_try), ## BEHAVIOR: PATROLLING (Immediate: Patrol Location/Party, Plan: Travel to Location/Party)
			(this_or_next|eq, ":ai_behavior", ai_bhvr_patrol_location),
			(eq, ":ai_behavior", ai_bhvr_patrol_party),
			(this_or_next|eq, ":ai_behavior_plan", ai_bhvr_patrol_location),
			(eq, ":ai_behavior_plan", ai_bhvr_patrol_party),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@patrolling the area near {s1}"),
		(else_try), ## BEHAVIOR: RESTING (Immediate: Resting at Location/Party)
			(eq, ":ai_behavior", ai_bhvr_in_town),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@resting in {s1}"),
		(else_try), ## BEHAVIOR: ESCORTING (Immediate: Escorting Party)
			(eq, ":ai_behavior", ai_bhvr_escort_party),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@resting in {s1}"),
		(else_try), ## BEHAVIOR: ATTACKING LOCATION (Immediate: Attacking Party)
			(eq, ":ai_behavior", ai_bhvr_attack_party),
			(is_between, ":ai_focus", centers_begin, centers_end),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@engaged in battle in {s1}"),
		(else_try), ## BEHAVIOR: ATTACKING PARTY (Immediate: Attacking Party)
			(this_or_next|eq, ":ai_behavior", ai_bhvr_attack_party),
			(eq, ":ai_behavior", ai_bhvr_negotiate_party),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@engaged in battle with {s1}"),
		(else_try), ## BEHAVIOR: AVOIDING PARTY (Immediate: Avoiding Party)
			(eq, ":ai_behavior", ai_bhvr_avoid_party),
			(call_script, "script_oath_describe_party", ":ai_focus", ":ai_behavior"), # Stores s1 (description)
			(str_store_string, s11, "@retreating before {s1}"),
		(else_try), ## BEHAVIOR: CAMPING (Immediate: Hold)
			(eq, ":ai_behavior", ai_bhvr_hold),
			(str_store_string, s11, "@resting in camp"),
		(else_try),
			## DEFAULT: I don't yet know what the AI is doing in this combination.
			(str_store_string, s11, "@UNDEFINED BEHAVIOR"),
			(display_message, s18, gpu_debug), # Immediate behaviour.
			(display_message, s19, gpu_debug), # Planned behaviour.
		(try_end),
		(str_store_party_name, s14, "$oathbound_party"),
		(str_store_string, s11, "@{s14} is currently {s11}."),
		
		### DIAGNOSTIC+ ###
		(try_begin),
			(ge, "$oathbound_debugging", 2),
			(display_message, "@DEBUG (Oathbound): {s11} (Actual)", gpu_debug),
		(try_end),
		### DIAGNOSTIC- ###
	]),
	
# script_oath_describe_party
# PURPOSE: Receives a location and returns a description of it to help condense code.
# EXAMPLE: (call_script, "script_oath_describe_party", ":party_no", ":intentions"), # Stores s1 (description)
("oath_describe_party",
    [
	    (store_script_param, ":party_no", 1),
		(store_script_param, ":intentions", 2),
		
		(party_is_active, ":party_no"),
		(str_store_party_name, s2, ":party_no"),
		(try_begin),
			(this_or_next|eq, ":intentions", ai_bhvr_travel_to_party),
			(this_or_next|eq, ":intentions", ai_bhvr_patrol_location),
			(this_or_next|eq, ":intentions", ai_bhvr_patrol_party),
			(this_or_next|eq, ":intentions", ai_bhvr_escort_party),
			(this_or_next|eq, ":intentions", ai_bhvr_negotiate_party),
			(this_or_next|eq, ":intentions", ai_bhvr_avoid_party),
			(this_or_next|eq, ":intentions", ai_bhvr_in_town),
			(this_or_next|eq, ":intentions", ai_bhvr_attack_party),
			(eq, ":intentions", ai_bhvr_travel_to_point),
			(try_begin),
				(is_between, ":party_no", towns_begin, towns_end),
				(str_store_string, s1, "@the town of {s2}"),
			(else_try),
				(is_between, ":party_no", castles_begin, castles_end),
				(str_store_string, s1, "@{s2}"),
			(else_try),
				(is_between, ":party_no", villages_begin, villages_end),
				(str_store_string, s1, "@the village of {s2}"),
			(else_try),
				(str_store_string, s1, "@{s2}"),
			(try_end),
		(else_try),
			(eq, ":intentions", ai_bhvr_hold),
			(try_begin),
				(is_between, ":party_no", towns_begin, towns_end),
				(str_store_string, s1, "@laying siege to the town of {s2}"),
			(else_try),
				(is_between, ":party_no", castles_begin, castles_end),
				(str_store_string, s1, "@laying siege to {s2}"),
			(else_try),
				(is_between, ":party_no", villages_begin, villages_end),
				(str_store_string, s1, "@raiding the village of {s2}"),
			(else_try),
				(str_store_string, s1, "@camping near {s2} army"),
			(try_end),
		(try_end),
	]),
	
# script_oath_describe_party_health
# PURPOSE: Gives a description of the current battle shape of a party.
# EXAMPLE: (call_script, "script_oath_describe_party_health", ":party_no"), # Stores s1 (description)
("oath_describe_party_health",
    [
	    (store_script_param, ":party_no", 1),
		(party_is_active, ":party_no"),
		(party_get_num_companions, ":total_size", ":party_no"),
		(call_script, "script_party_count_fit_for_battle", ":party_no"),
		(assign, ":fit_size", reg0),
		(store_mul, ":fit_percent", ":fit_size", 100),
		(val_div, ":fit_percent", ":total_size"),
		
		# The host...
		(call_script, "script_party_get_ideal_size", ":party_no"),
		(assign, ":ideal_size", reg0),
		(store_mul, ":ideal_percent", ":total_size", 100),
		(val_div, ":ideal_percent", ":ideal_size"),
		(try_begin),
			(ge, ":fit_percent", 80),
			(str_store_string, s3, "@is ready for an offensive campaign"),
			(assign, reg1, 1),
		(else_try),
			(ge, ":fit_percent", 60),
			(str_store_string, s3, "@is of a reasonable size"),
			(assign, reg1, 1),
		(else_try),
			(ge, ":fit_percent", 40),
			(str_store_string, s3, "@is looking thinner than you're used to"),
			(assign, reg1, 0),
		(else_try),
			(ge, ":fit_percent", 20),
			(str_store_string, s3, "@is in desperate need of more men"),
			(assign, reg1, 0),
		(else_try),
			(str_store_string, s3, "@has been nearly decimated with few members left in the ranks"),
			(assign, reg1, 0),
		(try_end),
		(str_store_string, s1, "@The host {s3}"),
		
		# ...
		(str_store_troop_name, s2, "$oathbound_master"),
		(try_begin),
			(ge, ":fit_percent", 90),
			(str_store_string, s3, "@{reg1? and:, yet} the men around you look ready to strike fear into the hearts of {s2}'s enemies."),
		(else_try),
			(ge, ":fit_percent", 80),
			(str_store_string, s3, "@{reg1? and:, yet} the men around you look defiant in the face of {s2}'s enemies."),
		(else_try),
			(ge, ":fit_percent", 60),
			(str_store_string, s3, "@{reg1?, but:, yet} the men around camp look tired."),
		(else_try),
			(ge, ":fit_percent", 40),
			(str_store_string, s3, "@{reg1?, yet: and} the remaining men have lost their will to fight such that you do not think they will withstand another battle."),
		(else_try),
			(ge, ":fit_percent", 20),
			(str_store_string, s3, "@{reg1?, yet: and} the talk around the camp is rumors of desertion."),
		(else_try),
			(str_store_string, s3, "@{reg1?, yet: and} those remaining look barely able to stand on their own."),
		(try_end),
		(str_store_string, s1, "@{s1}{s3}"),
	]),
	
# script_oath_player_faction_relations
# PURPOSE: Changes your relation with the other factions as needed to support contract status.
# EXAMPLE: (call_script, "script_oath_player_faction_relations", ":function"),
("oath_player_faction_relations",
    [
	    (store_script_param, ":function", 1),
		
		(try_begin),
			## FUNCTION #1 - Clears your faction relations when leaving the party.  Sets them to equal your reputation with that faction.
			(eq, ":function", OATHBOUND_FACTION_CLEAR_RELATIONS),
			(try_for_range, ":faction_no", kingdoms_begin, kingdoms_end),
				(faction_slot_eq, ":faction_no", slot_faction_state, sfs_active),
				(faction_get_slot, ":reputation", ":faction_no", slot_faction_oathbound_reputation),
				(try_begin), # If you have no reputation directly with a faction then your global reputation is used.
					(eq, ":reputation", 0),
					(assign, ":reputation", "$oathbound_reputation"),
				(try_end),
				(call_script, "script_set_player_relation_with_faction", ":faction_no", ":reputation"),
			(try_end),
			
		(else_try),
			## FUNCTION #2 - Sets your faction relations so that you can join in combat.
			(eq, ":function", OATHBOUND_ESTABLISH_MASTER_RELATIONS),
			(store_troop_faction, ":commander_faction", "$oathbound_master"),
			(try_for_range, ":faction_no", kingdoms_begin, kingdoms_end),
			   (faction_slot_eq, ":faction_no", slot_faction_state, sfs_active),
			   (store_relation, ":relation", ":faction_no", ":commander_faction"),
			   (call_script, "script_set_player_relation_with_faction", ":faction_no", ":relation"),
			(try_end),
		(try_end),
	]),
	
# script_oath_describe_contract_status
# PURPOSE: Describe the current status of your contract.
# EXAMPLE: (call_script, "script_oath_describe_contract_status", "$oathbound_status"), # Stores to s1
("oath_describe_contract_status",
    [
	    (store_script_param, ":status", 1),
		
		(try_begin),
			(eq, ":status", OATHBOUND_STATUS_NOT_HIRED),
			(str_store_string, s1, "@Inactive"),
		(else_try),
			(eq, ":status", OATHBOUND_STATUS_CONTRACTED),
			(str_store_string, s1, "@Serving in Party"),
		(else_try),
			(eq, ":status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 1),
			(str_store_string, s1, "@On Leave"),
		(else_try),
			(eq, ":status", OATHBOUND_STATUS_AWAY),
			(str_store_string, s1, "@On Mission"),
		(else_try),
			(eq, ":status", OATHBOUND_STATUS_SEPARATED),
			(str_store_string, s1, "@Separated"),
		(else_try),
			(eq, ":status", OATHBOUND_STATUS_DESERTER),
			(str_store_string, s1, "@Desertion"),
		(else_try),
			(str_store_string, s1, "@Undefined"),
		(try_end),
	]),
	
# script_oath_describe_oathbound_rank
# PURPOSE: Describe the name of your current rank and the title that goes with it.
# EXAMPLE: (call_script, "script_oath_describe_oathbound_rank", ":rank"), # Stores s1 (rank name), s2 (rank title), reg0 (pay boost)
("oath_describe_oathbound_rank",
    [
	    (store_script_param, ":rank", 1),
		(troop_get_type, reg1, "trp_player"),
		
		(try_begin),
			(eq, ":rank", OATHBOUND_RANK_NONE),
			(str_store_string, s1, "@None"),
			(str_clear, s2),
			(assign, reg0, 0),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_INITIATE),
			(str_store_string, s1, "@Initiate"),
			(str_clear, s2),
			(assign, reg0, 0),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_MILITIA),
			(str_store_string, s1, "@Militia"),
			(str_clear, s2),
			(assign, reg0, 20),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_SERGEANT),
			(str_store_string, s1, "@Sergeant"),
			(str_store_string, s2, "@Sergeant "),
			(assign, reg0, 40),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_CAPTAIN),
			(str_store_string, s1, "@Captain"),
			(str_store_string, s2, "@Captain "),
			(assign, reg0, 70),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_GREAT_CAPTAIN),
			(str_store_string, s1, "@Great Captain"),
			(str_store_string, s2, "@Captain "),
			(assign, reg0, 100),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_HEDGE_KNIGHT),
			(str_store_string, s1, "@Hedge Knight"),
			(str_store_string, s2, "@{reg1?Dame:Sir} "),
			(assign, reg0, 250),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_ELDER_KNIGHT),
			(str_store_string, s1, "@Elder Knight"),
			(str_store_string, s2, "@{reg1?Dame:Sir} "),
			(assign, reg0, 400),
		(else_try),
			(eq, ":rank", OATHBOUND_RANK_VASSAL_KNIGHT),
			(str_store_string, s1, "@Vassal"),
			(str_store_string, s2, "@{reg1?Lady:Lord} "),
			(assign, reg0, 400),
		(else_try),
			(str_store_string, s1, "@Undefined"),
			(str_clear, s2),
		(try_end),
	]),
	
# script_oath_change_oathbound_rating
# PURPOSE: Changes your oathbound rating within the faction you are serving and applies rank promotions/demotions as applicable.
# EXAMPLE: (call_script, "script_oath_change_oathbound_rating", ":amount"),
("oath_change_oathbound_rating",
    [
	    (store_script_param, ":amount", 1),
		
		## SECTION: Change our rating with the current oathbound faction.
		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(faction_get_slot, ":initial_rating", ":faction_no", slot_faction_oathbound_rating),
		(store_add, ":final_rating", ":initial_rating", ":amount"),
		(val_clamp, ":final_rating", -400, 1501),
		(try_begin),
			(eq, ":amount", OATHBOUND_VALUE_RESET),
			(assign, ":final_rating", 0),
			(store_mul, ":amount", ":initial_rating", -1),
		(try_end),
		(faction_set_slot, ":faction_no", slot_faction_oathbound_rating, ":final_rating"),
		
		## SECTION: Check for rank increases.
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(assign, ":initial_rank", reg1),
		(assign, ":final_rank", reg1),
		(try_begin),
			(ge, ":final_rating", OATHBOUND_RATING_VASSAL_KNIGHT),
			(assign, ":final_rank", OATHBOUND_RANK_VASSAL_KNIGHT),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_ELDER_KNIGHT),
			(assign, ":final_rank", OATHBOUND_RANK_ELDER_KNIGHT),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_HEDGE_KNIGHT),
			(assign, ":final_rank", OATHBOUND_RANK_HEDGE_KNIGHT),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_GREAT_CAPTAIN),
			(assign, ":final_rank", OATHBOUND_RANK_GREAT_CAPTAIN),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_CAPTAIN),
			(assign, ":final_rank", OATHBOUND_RANK_CAPTAIN),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_SERGEANT),
			(assign, ":final_rank", OATHBOUND_RANK_SERGEANT),	
		(else_try),
			(ge, ":final_rating", OATHBOUND_RATING_MILITIA),
			(assign, ":final_rank", OATHBOUND_RANK_MILITIA),	
		(else_try),
			(assign, ":final_rank", OATHBOUND_RANK_INITIATE),	
		(try_end),
		(faction_set_slot, ":faction_no", slot_faction_oathbound_rank, ":final_rank"),
		
		## SECTION: Report rating changes to the player.
		(assign, reg21, ":final_rating"),
		(assign, reg22, ":amount"),
		(try_begin),
			(gt, ":final_rating", ":initial_rating"),
			(display_message, "@Your oathbound rating has increased to {reg21}. (+{reg22})", gpu_green),
			## OATHBOUND EVENT LOG
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_RATING_CHANGE, ":amount"),
		(else_try),
			(lt, ":final_rating", ":initial_rating"),
			(display_message, "@Your oathbound rating has decreased to {reg21}. ({reg22})", gpu_red),
			## OATHBOUND EVENT LOG
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_RATING_CHANGE, ":amount"),
		(try_end),
		
		## SECTION: Notify player if rank changes.
		(str_store_troop_name, s21, "trp_player"),
		(try_begin),
			(gt, ":final_rank", ":initial_rank"),
			(call_script, "script_oath_describe_oathbound_rank", ":final_rank"), # Stores s1 (rank name), s2 (rank title)
			(play_sound, "snd_quest_succeeded"),
			(display_message, "@You have been promoted to the rank of {s1} and are now known as {s2}{s21}!", gpu_green),
			## OATHBOUND EVENT LOG
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_RANK_CHANGE, ":final_rank"),
		(else_try),
			(lt, ":final_rank", ":initial_rank"),
			(call_script, "script_oath_describe_oathbound_rank", ":final_rank"), # Stores s1 (rank name), s2 (rank title)
			(play_sound, "snd_quest_failed"),
			(display_message, "@You have been demoted to the rank of {s1} and are now known as {s2}{s21}!", gpu_red),
			## OATHBOUND EVENT LOG
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_RANK_CHANGE, ":final_rank"),
		(try_end),
		
		## SECTION: Award emblems upon rank promotion.
		(try_begin),
			(neg|faction_slot_ge, ":faction_no", slot_faction_oathbound_high_rank, ":final_rank"),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_high_rank, ":final_rank"),
			(call_script, "script_emblem_award_to_player", ":final_rank"), # emblem_scripts.py
		(try_end),
		
		## SECTION: Check for special events such as being offered vassalage.
		(try_begin),
			(ge, ":final_rank", OATHBOUND_RANK_HEDGE_KNIGHT),
			(neq, "$g_player_banner_granted", 1),
			(assign, "$g_player_banner_granted", 1),
			(display_message, "@You have been granted the right to carry a banner device in your name!", gpu_green),
		(try_end),
		
		(try_begin),
			(ge, ":final_rank", OATHBOUND_RANK_VASSAL_KNIGHT),
			(neq, ":initial_rank", OATHBOUND_RANK_VASSAL_KNIGHT),
			(str_store_troop_name, s21, "$oathbound_master"),
			(display_message, "@You have been made a vassal of {s21}!", gpu_green),
		(try_end),
		
	]),
	
# script_oath_get_rating_to_next_rank
# PURPOSE: Determines how much rating is required to reach the next rank, returns that amount and what the next rank is.
# EXAMPLE: (call_script, "script_oath_get_rating_to_next_rank"), # Stores reg1 (remaining rating), reg2 (next rank)
("oath_get_rating_to_next_rank",
    [
	    (assign, reg1, 0),
		(assign, reg2, 0),
		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(faction_get_slot, ":current_rating", ":faction_no", slot_faction_oathbound_rating),
		(try_begin), ## Currently: OATHBOUND_RANK_VASSAL_KNIGHT
			(ge, ":current_rating", OATHBOUND_RATING_VASSAL_KNIGHT),
			(assign, reg1, 0),
			(assign, reg2, OATHBOUND_RANK_VASSAL_KNIGHT),
		(else_try), ## Currently: OATHBOUND_RANK_ELDER_KNIGHT
			(ge, ":current_rating", OATHBOUND_RATING_ELDER_KNIGHT),
			(store_sub, reg1, OATHBOUND_RATING_VASSAL_KNIGHT, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_VASSAL_KNIGHT),
		(else_try), ## Currently: OATHBOUND_RANK_HEDGE_KNIGHT
			(ge, ":current_rating", OATHBOUND_RATING_HEDGE_KNIGHT),
			(store_sub, reg1, OATHBOUND_RATING_ELDER_KNIGHT, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_ELDER_KNIGHT),
		(else_try), ## Currently: OATHBOUND_RANK_GREAT_CAPTAIN
			(ge, ":current_rating", OATHBOUND_RATING_GREAT_CAPTAIN),
			(store_sub, reg1, OATHBOUND_RATING_HEDGE_KNIGHT, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_HEDGE_KNIGHT),
		(else_try), ## Currently: OATHBOUND_RANK_CAPTAIN
			(ge, ":current_rating", OATHBOUND_RATING_CAPTAIN),
			(store_sub, reg1, OATHBOUND_RATING_GREAT_CAPTAIN, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_GREAT_CAPTAIN),	
		(else_try), ## Currently: OATHBOUND_RANK_SERGEANT
			(ge, ":current_rating", OATHBOUND_RATING_SERGEANT),
			(store_sub, reg1, OATHBOUND_RATING_CAPTAIN, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_CAPTAIN),	
		(else_try), ## Currently: OATHBOUND_RANK_MILITIA
			(ge, ":current_rating", OATHBOUND_RATING_MILITIA),
			(store_sub, reg1, OATHBOUND_RATING_SERGEANT, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_SERGEANT),	
		(else_try), ## Currently: OATHBOUND_RANK_INITIATE
			(store_sub, reg1, OATHBOUND_RATING_MILITIA, ":current_rating"),
			(assign, reg2, OATHBOUND_RANK_MILITIA),
		(try_end),
	]),
	
# script_oath_change_oathbound_reputation
# PURPOSE: Changes your oathbound reputation within the faction you are serving.
# EXAMPLE: (call_script, "script_oath_change_oathbound_reputation", ":amount"),
("oath_change_oathbound_reputation",
    [
	    (store_script_param, ":amount", 1),
		
		## SECTION: Change our reputation with the current oathbound faction.
		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(faction_get_slot, ":initial_reputation", ":faction_no", slot_faction_oathbound_reputation),
		(store_add, ":final_reputation", ":initial_reputation", ":amount"),
		(val_clamp, ":final_reputation", -100, 101),
		(try_begin),
			(eq, ":amount", OATHBOUND_VALUE_RESET),
			(assign, ":final_reputation", 0),
			(store_mul, ":amount", ":initial_reputation", -1),
		(try_end),
		(faction_set_slot, ":faction_no", slot_faction_oathbound_reputation, ":final_reputation"),
		
		## SECTION: Report reputation changes to the player.
		(assign, reg21, ":final_reputation"),
		(assign, reg22, ":amount"),
		(str_store_faction_name, s21, ":faction_no"),
		(try_begin),
			(gt, ":final_reputation", ":initial_reputation"),
			(display_message, "@Your reputation with {s21} has increased to {reg21}. (+{reg22})", gpu_green),
		(else_try),
			(lt, ":final_reputation", ":initial_reputation"),
			(display_message, "@Your reputation with {s21} has decreased to {reg21}. ({reg22})", gpu_red),
		(try_end),
		
		## OATHBOUND EVENT LOG
		(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_REPUTATION_CHANGE, ":amount"),
		
		## TODO - SECTION: EVENT - Reputation falls below -75 = Being Fired!
		
		## UPDATE GLOBAL REPUTATION
		(call_script, "script_oath_calculate_global_reputation"),
	]),
	
# script_oath_calculate_global_reputation
# PURPOSE: Calculates your global oathbound reputation and updates $oathbound_reputation.
# EXAMPLE: (call_script, "script_oath_calculate_global_reputation"),
("oath_calculate_global_reputation",
    [
	    (assign, ":initial_reputation", "$oathbound_reputation"),
		(assign, ":total", 0),
		(store_sub, ":faction_count", kingdoms_end, kingdoms_begin),
		(try_for_range, ":faction_no", kingdoms_begin, kingdoms_end),
			# Consider your reputation with the faction.
			(faction_get_slot, ":faction_reputation", ":faction_no", slot_faction_oathbound_reputation),
			(val_div, ":faction_reputation", ":faction_count"),
			(val_add, ":total", ":faction_reputation"),
			# Check if you have betrayed the faction while under contract.
			(faction_get_slot, ":betrayals", ":faction_no", slot_faction_oathbound_betrayals),
			(val_mul, ":betrayals", -4),
			(val_add, ":total", ":betrayals"),
			# Check if you have ever renewed your contract witht he faction.
			(faction_get_slot, ":renewals", ":faction_no", slot_faction_oathbound_renewals),
			(val_mul, ":renewals", 3),
			(val_add, ":total", ":renewals"),
		(try_end),
		(val_clamp, ":total", -100, 101),
		(assign, "$oathbound_reputation", ":total"),
		
		## If global reputation has changed make mention of it.
		(try_begin),
			(neq, ":initial_reputation", "$oathbound_reputation"),
			(assign, reg21, "$oathbound_reputation"),
			(store_sub, reg22, "$oathbound_reputation", ":initial_reputation"),
			(try_begin),
				(gt, "$oathbound_reputation", ":initial_reputation"),
				(display_message, "@Your global reputation has increased to {reg21}. (+{reg22})", gpu_green),
			(else_try),
				(lt, "$oathbound_reputation", ":initial_reputation"),
				(display_message, "@Your global reputation has decreased to {reg21}. ({reg22})", gpu_red),
			(try_end),
			## OATHBOUND EVENT LOG
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_GLOBAL_REPUTATION, reg22),
		(try_end),
	]),
	
# script_oath_describe_reputation_with_faction
# PURPOSE: Converts the reputation you have with the given faction to a text format.
# EXAMPLE: (call_script, "script_oath_describe_reputation_with_faction", ":faction_no"), # Stores s1 (reputation text), reg1 (reputation value)
("oath_describe_reputation_with_faction",
    [
	    (store_script_param, ":faction_no", 1),
		
		(try_begin),
			(neg|is_between, ":faction_no", kingdoms_begin, kingdoms_end),
			(store_troop_faction, ":faction_no", "$oathbound_master"),
		(try_end),
		(faction_get_slot, ":reputation", ":faction_no", slot_faction_oathbound_reputation),
		
		(try_begin),
			(ge, ":reputation", 75),
			(str_store_string, s1, "@Revered"),
		(else_try),
			(is_between, ":reputation", 30, 75),
			(str_store_string, s1, "@Trusted"),
		(else_try),
			(is_between, ":reputation", 6, 30),
			(str_store_string, s1, "@Favored"),
		(else_try),
			(is_between, ":reputation", -5, 6),
			(str_store_string, s1, "@Neutral"),
		(else_try),
			(is_between, ":reputation", -29, -5),
			(str_store_string, s1, "@Disliked"),
		(else_try),
			(is_between, ":reputation", -74, -29),
			(str_store_string, s1, "@Distrusted"),
		(else_try),
			(lt, ":reputation", -74), # You should be fired.
			(str_store_string, s1, "@Hated"),
		(try_end),
		(assign, reg1, ":reputation"),
	]),
	
# script_oath_get_current_oathbound_rank
# PURPOSE: Gets your current rank with the faction you are serving.
# EXAMPLE: (call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
("oath_get_current_oathbound_rank",
    [
	    (store_troop_faction, ":faction_no", "$oathbound_master"),
		(faction_get_slot, reg1, ":faction_no", slot_faction_oathbound_rank),
	]),
	
# script_cf_oath_player_meets_minimum_rank
# PURPOSE: Gets your current rank with the faction you are serving and fails if you do not meet the requested minimum.
# EXAMPLE: (call_script, "script_cf_oath_player_meets_minimum_rank", ":minimum_rank"),
("cf_oath_player_meets_minimum_rank",
    [
	    (store_script_param, ":minimum_rank", 1),
		
		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(faction_get_slot, ":rank", ":faction_no", slot_faction_oathbound_rank),
		(ge, ":rank", ":minimum_rank"),
	]),
	
# script_oath_convert_hours_to_description
# PURPOSE: Converts your remaining contract hours into a more readable format.
# EXAMPLE: (call_script, "script_oath_convert_hours_to_description", ":hours_remaining", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
("oath_convert_hours_to_description",
    [
	    (store_script_param, ":hours_remaining", 1),
		(store_script_param, ":output_type", 2),
		
		(str_clear, s1),
		(try_begin),
			(eq, ":output_type", OATHBOUND_CONTRACT_HOURS),
			(assign, reg1, ":hours_remaining"),
			(store_sub, reg2, reg1, 1),
			(str_store_string, s1, "@{reg1} hour{reg2?s:} remain{reg2?:s}"),
		(else_try),
			(eq, ":output_type", OATHBOUND_CONTRACT_DAYS),
			(store_div, reg1, ":hours_remaining", 24),
			(store_sub, reg2, reg1, 1),
			(str_store_string, s1, "@{reg1} day{reg2?s:} remain{reg2?:s}"),
		(else_try),
			(eq, ":output_type", OATHBOUND_CONTRACT_MONTHS),
			(store_div, reg1, ":hours_remaining", 24*30),
			(store_sub, reg2, reg1, 1),
			(str_store_string, s1, "@{reg1} month{reg2?s:} remain{reg2?:s}"),
		(else_try),
			(eq, ":output_type", OATHBOUND_CONTRACT_TIME),
			(store_div, ":days_raw", ":hours_remaining", 24),
			(store_mod, ":hours", ":hours_remaining", 24),
			(store_div, ":months", ":days_raw", 30),
			(store_mod, ":days", ":days_raw", 30),
			(str_clear, s1),
			(assign, reg3, 0),
			(try_begin),
				(ge, ":months", 1),
				(assign, reg1, ":months"),
				(store_sub, reg2, reg1, 1),
				(str_store_string, s1, "@{s1}{reg1} month{reg2?s:}"),
				(assign, reg3, 1),
			(try_end),
			(try_begin),
				(ge, ":days", 1),
				(assign, reg1, ":days"),
				(store_sub, reg2, reg1, 1),
				(try_begin),
					(eq, ":hours", 0),
					(ge, ":months", 1),
					(str_store_string, s2, "@ & "),
				(else_try),
					(str_store_string, s2, "@{reg3?, :}"),
				(try_end),
				(str_store_string, s1, "@{s1}{s2}{reg1} day{reg2?s:}"),
				(assign, reg3, 1),
			(try_end),
			(try_begin),
				(ge, ":hours", 1),
				(assign, reg1, ":hours"),
				(store_sub, reg2, reg1, 1),
				(str_store_string, s1, "@{s1}{reg3? & :}{reg1} hour{reg2?s:}"),
				(assign, reg3, 1),
			(try_end),
			(str_store_string, s1, "@{s1} remain{reg2?:s}"),
		(try_end),
		
	]),
	
# script_oath_pay_player_because_s11
# PURPOSE: Splits the player party from the $oathbound_master's party ($oathbound_party).
# EXAMPLE: (call_script, "script_oath_pay_player_because_s11", ":amount"),
("oath_pay_player_because_s11",
    [
	    (store_script_param, ":amount", 1),
		
		(set_show_messages, 0),
		(troop_add_gold, "trp_player", ":amount"),
		(set_show_messages, 1),
		(assign, reg1, ":amount"),
		(store_sub, reg2, reg1, 1),
		(display_message, "@You receive {reg1} denar{reg2?s:}{s11}."),
		(play_sound, "snd_money_received"),
	]),
	
# script_oath_calculate_weekly_pay
# PURPOSE: This determines how much pay your character should receive on a weekly basis for your contract.
# EXAMPLE: (call_script, "script_oath_calculate_weekly_pay"), # Returns reg1 (pay)
("oath_calculate_weekly_pay",
    [
	    (assign, ":total_base_pay", 0),
		# Value
		(assign, reg21, OATHBOUND_BASE_PAY_VALUE),
		(val_add, ":total_base_pay", OATHBOUND_BASE_PAY_VALUE),
		(store_character_level, ":level", "trp_player"),
		(assign, reg1, ":level"),
		(store_sub, ":pay", ":level", 5),
		(val_div, ":pay", 3),
		(val_mul, ":pay", 25),
		(val_add, ":total_base_pay", ":pay"),
		(assign, reg21, ":pay"),
		(store_character_level, ":level", "trp_player"),
		(assign, reg21, OATHBOUND_BOUNTY_PAY),
		(assign, reg22, "$oathbound_bounty_count"),
		(store_sub, reg23, reg22, 1),
		(store_mul, ":pay", "$oathbound_bounty_count", OATHBOUND_BOUNTY_PAY),
		(val_add, ":total_base_pay", ":pay"),
		(assign, reg21, ":pay"),
		(assign, reg21, ":total_base_pay"),
		
		
		###########################
		### PERCENT PAY FACTORS ###
		###########################
		(assign, ":total_percent_pay", 0),
		
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title), reg0 (pay boost)
		(assign, ":bonus", reg0),
		(assign, reg21, ":bonus"),
		(val_add, ":total_percent_pay", ":bonus"),
		## LINES 2 to 9 - Skills: Persuasion, Surgery, First Aid, Wound Treatment, Engineer, Path-finding, Spotting & Tracking
		(try_for_range, ":skill_no", "skl_trade", "skl_reserved_18"),
			(this_or_next|eq, ":skill_no", "skl_persuasion"),
			(this_or_next|eq, ":skill_no", "skl_surgery"),
			(this_or_next|eq, ":skill_no", "skl_first_aid"),
			(this_or_next|eq, ":skill_no", "skl_wound_treatment"),
			(this_or_next|eq, ":skill_no", "skl_engineer"),
			(this_or_next|eq, ":skill_no", "skl_pathfinding"),
			(this_or_next|eq, ":skill_no", "skl_spotting"),
			(eq, ":skill_no", "skl_tracking"),
			
			# Get our relevant skill value.
			(try_begin),
				(eq, ":skill_no", "skl_persuasion"),
				(store_skill_level, ":skill_level", ":skill_no", "trp_player"),
			(else_try),
				(party_get_skill_level, ":skill_level", "p_main_party", ":skill_no"),
			(try_end),
			
			# Get our skill payment factor
			(try_begin),
				(this_or_next|eq, ":skill_no", "skl_surgery"),
				(eq, ":skill_no", "skl_engineer"),
				(assign, ":factor", 4),
			(else_try),
				(this_or_next|eq, ":skill_no", "skl_persuasion"),
				(this_or_next|eq, ":skill_no", "skl_wound_treatment"),
				(this_or_next|eq, ":skill_no", "skl_first_aid"),
				(eq, ":skill_no", "skl_tracking"),
				(assign, ":factor", 3),
			(else_try),
				(assign, ":factor", 2),
			(try_end),
			
			# Name
			(assign, reg1, ":skill_level"),
			(assign, reg21, ":factor"),
			(store_mul, ":bonus", ":skill_level", ":factor"),
			(assign, reg21, ":bonus"),
			(val_add, ":total_percent_pay", ":bonus"),
		(try_end),
		
		(assign, reg21, "$oathbound_contract_periods"),
		(assign, reg22, OATHBOUND_RENEWAL_PAY_BOOST),
		(store_mul, ":bonus", "$oathbound_contract_periods", OATHBOUND_RENEWAL_PAY_BOOST),
		(assign, reg21, ":bonus"),
		(val_add, ":total_percent_pay", ":bonus"),
		(assign, reg21, ":total_percent_pay"),

		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(call_script, "script_oath_describe_reputation_with_faction", ":faction_no"), # Stores s1 (reputation text), reg1 (reputation value)
		(assign, ":reputation", reg1),
		(call_script, "script_oath_get_reputation_pay_factor", ":reputation"), # Returns reg1 (value)
		(assign, ":reputation_multiplier", reg1),
		(assign, reg21, ":reputation_multiplier"),

		(assign, reg21, ":total_base_pay"),
		(assign, reg22, ":total_percent_pay"),
		(store_mul, ":bonus_pay", ":total_base_pay", ":total_percent_pay"),
		(val_div, ":bonus_pay", 100),
		(store_add, ":total_pay", ":total_base_pay", ":bonus_pay"),
		# Now tie in the reputation multiplier
		(store_mul, ":reputation_bonus", ":total_pay", ":reputation_multiplier"),
		(val_div, ":reputation_bonus", 100),
		(val_add, ":total_pay", ":reputation_bonus"),
		(assign, reg21, ":total_pay"),
		# Create global total_pay variable for payment system
		(assign, "$total_pay", ":total_pay"),
		(assign, reg1, ":total_pay"),
	]),

# script_oath_get_reputation_pay_factor
# PURPOSE: Receives a reputation value and returns the pay bonus for that rank as reg1.
# EXAMPLE: (call_script, "script_oath_get_reputation_pay_factor", ":reputation"), # Returns reg1 (value)
("oath_get_reputation_pay_factor",
	[ 
		(store_script_param, ":reputation", 1),
		
		(try_begin),
			(ge, ":reputation", 75),
			(assign, reg1, 100),
		(else_try),
			(is_between, ":reputation", 30, 75),
			(assign, reg1, 50),
		(else_try),
			(is_between, ":reputation", 6, 30),
			(assign, reg1, 25),
		(else_try),
			(is_between, ":reputation", -5, 6),
			(assign, reg1, 0),
		(else_try),
			(is_between, ":reputation", -29, -5),
			(assign, reg1, -25),
		(else_try),
			(is_between, ":reputation", -74, -29),
			(assign, reg1, -50),
		(else_try),
			(lt, ":reputation", -74), # You should be fired.
			(assign, reg1, -100),
		(try_end),
	]),
	
# script_oath_convert_value_to_denars_string
# PURPOSE: Simply turns 14 into 14 denars or 1 into 1 denar with green coloring for positive values and red coloring for negative ones.
# EXAMPLE: (call_script, "script_oath_convert_value_to_denars_string", ":amount", ":string_no"), # Returns s20 (value), reg20 (color code)
("oath_convert_value_to_denars_string",
	[ 
		(store_script_param, ":amount", 1),
		(store_script_param, ":string_no", 2),
		
		(str_store_string, s1, ":string_no"),
		
		(store_sub, reg1, ":amount", 1),
		(str_store_string, s20, "@{s1}{reg1?s:}"),
		
		(try_begin),
			(ge, ":amount", 0),
			(assign, reg20, 23552), # Dark Green
		(else_try),
			(assign, reg20, 4325376), # Dark Red
		(try_end),
	]),

# script_oath_keep_field_loot
# PURPOSE: Any equipment picked up by the player is kept.
# EXAMPLE: (call_script, "script_oath_keep_field_loot"), # oath_scripts.py
("oath_keep_field_loot",
	[
		(get_player_agent_no, ":player"),
		(try_for_range, ":ek_slot", ek_item_0, ek_head),
			(agent_get_item_slot, ":item", ":player", ":ek_slot"), 
			(gt, ":item", 0),
			(neg|troop_has_item_equipped, "trp_player", ":item"),
			(troop_add_item, "trp_player", ":item"),
		(try_end),
		(agent_get_horse, ":horse", ":player"),
		(try_begin),
			(gt, ":horse", 0),
			(agent_get_item_id, ":horse", ":horse"),
			(troop_get_inventory_slot, ":old_horse", "trp_player", ek_horse),
			(neq, ":horse", ":old_horse"),
			(try_begin),
				(gt, ":old_horse", 0),
				(troop_get_inventory_slot_modifier, ":horse_imod", "trp_player", ek_horse),
				(troop_add_item, "trp_player", ":old_horse", ":horse_imod"),
			(try_end),
			(troop_set_inventory_slot, "trp_player", ek_horse, ":horse"),
		(try_end),
		
		### DIAGNOSTIC+ ###
		(try_begin),
			(ge, "$oathbound_debugging", 1),
			(display_message, "@DEBUG (Oathbound): Battlefield loot is being retained.", gpu_debug),
		(try_end),
		### DIAGNOSTIC- ###
	]),
   
   
####################################################################################################################################
############                                              LOGGING SCRIPTS                                                ###########
####################################################################################################################################
# dict_create      = 3200 #(dict_create, <destination>), #Creates an empty dictionary object and stores it into <destination>
# dict_free        = 3201 #(dict_free, <dict>), #Frees the dictionary object <dict>. A dictionary can't be used after freeing it
# dict_load_file   = 3202 #(dict_load_file, <dict>, <file>, [<mode>]), #Loads a dictionary file into <dict>. Setting [<mode>] to 0 (default) clears <dict> and then loads the file, setting [<mode>] to 1 doesn't clear <dict> but overrides any key that's already present, [<mode>] to 2 doesn't clear <dict> and doesn't overwrite keys that are already present
# dict_load_dict   = 3203 #(dict_load_dict, <dict_1>, <dict_2>, [<mode>]), #Loads <dict_2> into <dict_1>. [<mode>]: see above
# dict_save        = 3204 #(dict_save, <dict>, <file>), #Saves <dict> into a file. For security reasons, <file> is just a name, not a full path, and will be stored into a WSE managed directory
# dict_clear       = 3205 #(dict_clear, <dict>), #Clears all key-value pairs from <dict>
# dict_is_empty    = 3206 #(dict_is_empty, <dict>), #Fails if <dict> is not empty
# dict_has_key     = 3207 #(dict_has_key, <dict>, <key>), #Fails if <key> is not present in <dict>
# dict_get_size    = 3208 #(dict_get_size, <destination>, <dict>), #Stores the count of key-value pairs in <dict> into <destination>
# dict_delete_file = 3209 #(dict_delete_file, <file>), #Deletes dictionary file <file> from disk
# dict_get_str     = 3210 #(dict_get_str, <string_register>, <dict>, <key>, [<default>]), #Stores the string value paired to <key> into <string_register>. If the key is not found and [<default>] is set, [<default>] will be stored instead. If [<default>] is not set, an empty string will be stored
# dict_get_int     = 3211 #(dict_get_int, <destination>, <dict>, <key>, [<default>]), #Stores the numeric value paired to <key> into <destination>. If the key is not found and [<default>] is set, [<default>] will be stored instead. If [<default>] is not set, 0 will be stored
# dict_set_str     = 3212 #(dict_set_str, <dict>, <key>, <string_no>), #Adds (or changes) <string_no> as the string value paired to <key>
# dict_set_int     = 3213 #(dict_set_int, <dict>, <key>, <value>), #Adds (or changes) <value> as the numeric value paired to <key>

# script_oath_add_log_entry
# PURPOSE: Handles storing event log entries and stores them into a separate text file.
# EXAMPLE: (call_script, "script_oath_add_log_entry", ":entry_no", ":entry_type", ":focus"),
("oath_add_log_entry",
	[ 
		(store_script_param, ":entry_no", 1),
		(store_script_param, ":entry_type", 2),
		(store_script_param, ":focus", 3),
		
		(str_store_string, s10, "@No event added due to WSE not running."),
		(try_begin),
			(neg|is_vanilla_warband),
			## CREATE DICTIONARY & LOAD FILE
			(dict_create, ":dict_titles"),
			(dict_clear, ":dict_titles"),
			(dict_load_file, ":dict_titles", OATHBOUND_EVENT_LOG, 0),
			
			## Create our entry.
			# OATHBOUND_EVENT_QUEST_COMPLETION	= 1		(Focus = Quest #)
			# OATHBOUND_EVENT_QUEST_FAILURE		= 2		(Focus = Quest #)
			# OATHBOUND_EVENT_REPUTATION_CHANGE	= 3		(Focus = Change Value)
			# OATHBOUND_EVENT_RATING_CHANGE		= 4		(Focus = Change Value)
			# OATHBOUND_EVENT_RANK_CHANGE		= 5		(Focus = Change Value)
			# OATHBOUND_EVENT_STATUS_CHANGE		= 6		(Focus = New Status)
			# OATHBOUND_EVENT_CONTRACT_RENEWAL	= 7		(Focus = N/A)
			# OATHBOUND_EVENT_JOINED_SIEGE		= 8		(Focus = Party #)
			# OATHBOUND_EVENT_DEFENDED_SIEGE	= 9		(Focus = Party #)
			(try_begin),
				(eq, ":entry_type", OATHBOUND_EVENT_QUEST_COMPLETION),
				(str_store_quest_name, s2, ":focus"),
				(str_store_string, s4, "@Completed quest {s2}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_QUEST_FAILURE),
				(str_store_quest_name, s2, ":focus"),
				(str_store_string, s4, "@Failed quest {s2}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_REPUTATION_CHANGE),
				(assign, reg2, ":focus"),
				(store_troop_faction, ":faction_no", "$oathbound_master"),
				(str_store_faction_name, s3, ":faction_no"),
				(faction_get_slot, reg3, ":faction_no", slot_faction_oathbound_reputation),
				(str_clear, s5),
				(try_begin),
					(ge, reg2, 0),
					(str_store_string, s5, "@+"),
				(try_end),
				(str_store_string, s4, "@Reputation with the {s3} changed to {reg3}. ({s5}{reg2})"),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_RATING_CHANGE),
				(assign, reg2, ":focus"),
				(store_troop_faction, ":faction_no", "$oathbound_master"),
				(str_store_faction_name, s3, ":faction_no"),
				(faction_get_slot, reg3, ":faction_no", slot_faction_oathbound_rating),
				(str_clear, s5),
				(try_begin),
					(ge, reg2, 0),
					(str_store_string, s5, "@+"),
				(try_end),
				(str_store_string, s4, "@Rating with the {s3} changed to {reg3}. ({s5}{reg2})"),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_RANK_CHANGE),
				(call_script, "script_oath_describe_oathbound_rank", ":focus"), # Stores s1 (rank name), s2 (rank title)
				(str_store_string, s4, "@Rank within the {s3} changed to {s1}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_STATUS_CHANGE),
				(call_script, "script_oath_describe_contract_status", ":focus"), # Stores to s1
				(str_store_string, s4, "@Contract status changed to {s1}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_CONTRACT_RENEWAL),
				(call_script, "script_oath_convert_hours_to_description", OATHBOUND_CONTRACT_DURATION, OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
				(str_store_string, s4, "@You have renewed your contract for another {s1} days."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_JOINED_SIEGE),
				(str_store_party_name, s1, ":focus"),
				(str_store_string, s4, "@You joined in the Siege of {s1}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_DEFENDED_SIEGE),
				(str_store_party_name, s1, ":focus"),
				(str_store_string, s4, "@You aided in the Battle for {s1}."),
			(else_try),
				(eq, ":entry_type", OATHBOUND_EVENT_GLOBAL_REPUTATION),
				(assign, reg2, ":focus"),
				(assign, reg3, "$oathbound_reputation"),
				(str_clear, s5),
				(try_begin),
					(ge, reg2, 0),
					(str_store_string, s5, "@+"),
				(try_end),
				(str_store_string, s4, "@Your global reputation has changed to {reg3}. ({s5}{reg2})"),
			(try_end),
			
			# Tack the date onto the beginning of the entry.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s5, ":cur_hours"),
			(store_time_of_day, reg6),
			(str_store_string, s6, "@{reg6}00"),
			(try_begin),
				(lt, reg6, 10),
				(str_store_string, s6, "@0{reg6}00"),
			(try_end),
			(str_store_string, s7, "@[{s5} @ {s6}]: "),
			(str_store_string, s10, "@{s7}{s4}"),
			
			## Store the entry.
			(assign, reg1, ":entry_no"),
			(str_store_string, s1, "@Event_{reg1}"), # Key
			(dict_set_str, ":dict_titles", s1, s10),
			
			## SAVE TO FILE
			(dict_save, ":dict_titles", OATHBOUND_EVENT_LOG),
			
			## Update $oathbound_events
			(val_add, "$oathbound_events", 1),
		(try_end),
		
		## Display
		(try_begin),
			(ge, "$oathbound_debugging", 1),
			(display_message, "@DEBUG (Oathbound Log): {s10}", gpu_debug),
		(try_end),
	]),
	
# script_oath_get_log_entry
# PURPOSE: Sets each title textbox to the default version for that faction.  This is only useful within prsnt_vassal_titles.
# EXAMPLE: (call_script, "script_oath_get_log_entry", ":entry_no"), # returns s1 (event description)
("oath_get_log_entry",
	[
		(store_script_param, ":entry_no", 1),
		
		(str_store_string, s1, "@No event added due to WSE not running."),
		(try_begin),
			(neg|is_vanilla_warband),
			
			## CREATE DICTIONARY & LOAD FILE
			(dict_create, ":dict_titles"),
			(dict_clear, ":dict_titles"),
			(dict_load_file, ":dict_titles", OATHBOUND_EVENT_LOG, 0),
			
			## Setup Event Key
			(assign, reg1, ":entry_no"),
			(str_store_string, s2, "@Event_{reg1}"), # Key
			
			## Get Event.
			(str_clear, s1),
			(try_begin),
				(dict_has_key, ":dict_titles", s2),
				(dict_get_str, s1, ":dict_titles", s2, "@Undefined Event"),
			(try_end),
		(try_end),
	]),
	
	
####################################################################################################################################
############                                               QUEST SCRIPTS                                                 ###########
####################################################################################################################################
# script_oath_start_quest
# PURPOSE: Handles the common start properties for an Oathbound quest.
# EXAMPLE: (call_script, "script_oath_start_quest", ":quest_no"),
("oath_start_quest",
	[ 
		(store_script_param, ":quest_no", 1),
		
		## Display $oathbound_master as the giver & the start time.
		# (str_store_troop_name, s62, "$oathbound_master"),
		(str_store_string, s62, "str_oath_quest_title"),
		(str_store_string, s63, "@Given by: {s62}"),
		(store_current_hours, ":cur_hours"),
		(str_store_date, s60, ":cur_hours"),
		(str_store_string, s60, "@Given on: {s60}"),
		(add_quest_note_from_sreg, ":quest_no", 0, s60, 0),
		(add_quest_note_from_sreg, ":quest_no", 1, s63, 0),
		(add_quest_note_from_sreg, ":quest_no", 2, s61, 0),
		
		## Common Slot Designations
		(quest_set_slot, ":quest_no", slot_quest_giver_troop, "$oathbound_master"),
		
		(try_begin),
		  (quest_slot_ge, ":quest_no", slot_quest_expiration_days, 1),
		  (quest_get_slot, reg20, ":quest_no", slot_quest_expiration_days),
		  (add_quest_note_from_sreg, ":quest_no", 7, "@You have {reg20} days to finish this quest.", 0),
		(try_end),
		
		(start_quest, ":quest_no", "$oathbound_master"),
		
		(display_message, "str_quest_log_updated"),
	]),
	
# script_oath_quest_change_slot
# PURPOSE: Condenses the code for changing a quest slot so it can be more easily debugged in real time.
# EXAMPLE: (call_script, "script_oath_quest_change_slot", ":quest_no", ":quest_slot", ":amount"),
("oath_quest_change_slot",
	[ 
		(store_script_param, ":quest_no", 1),
		(store_script_param, ":quest_slot", 2),
		(store_script_param, ":amount", 3),
		
		(quest_get_slot, ":value", ":quest_no", ":quest_slot"),
		(val_add, ":value", ":amount"),
		(quest_set_slot, ":quest_no", ":quest_slot", ":value"),
		
		(try_begin),
			(ge, "$oathbound_debugging", 1), # Diagnostic
			(assign, reg31, ":amount"),
			(quest_get_slot, ":title_string", ":quest_no", slot_quest_unique_name),
			(str_store_string, s31, ":title_string"),
			(assign, reg32, ":quest_slot"),
			(assign, reg33, ":value"),
			(display_message, "@DEBUG (Oathbound): Quest [ {s31} ], Slot #{reg32} changed by {reg31} to {reg33}.", gpu_debug),
		(try_end),
	]),
	
# script_oath_quest_set_slot
# PURPOSE: Condenses the code for changing a quest slot so it can be more easily debugged in real time.
# EXAMPLE: (call_script, "script_oath_quest_set_slot", ":quest_no", ":quest_slot", ":amount"),
("oath_quest_set_slot",
	[ 
		(store_script_param, ":quest_no", 1),
		(store_script_param, ":quest_slot", 2),
		(store_script_param, ":amount", 3),
		
		(quest_set_slot, ":quest_no", ":quest_slot", ":amount"),
		
		(try_begin),
			(ge, "$oathbound_debugging", 1), # Diagnostic
			(assign, reg31, ":amount"),
			(quest_get_slot, ":title_string", ":quest_no", slot_quest_unique_name),
			(str_store_string, s31, ":title_string"),
			(assign, reg32, ":quest_slot"),
			(display_message, "@DEBUG (Oathbound): Quest [ {s31} ], Slot #{reg32} set to {reg31}.", gpu_debug),
		(try_end),
	]),
	
# script_oath_quest_change_state
# PURPOSE: Common utility script used to change the current stage of a quest, force a reset of any dialog comments that 
# may be relevant and report back that action being taken if desired.
# EXAMPLE: (call_script, "script_oath_quest_change_state", ":quest_no", ":new_stage"),
("oath_quest_change_state",
  [
		(store_script_param, ":quest_no", 1),
		(store_script_param, ":new_stage", 2),
		
		(quest_set_slot, ":quest_no", slot_quest_current_state, ":new_stage"),
		(quest_set_slot, ":quest_no", slot_quest_comment_made, 0),
		
		(try_begin),
			(ge, "$oathbound_debugging", 1),
			(quest_get_slot, ":quest_title", ":quest_no", slot_quest_unique_name),
			(str_store_string, s41, ":quest_title"),
			(assign, reg31, ":new_stage"),
			(display_message, "@DEBUG (Oathbound): Quest '{s41}' current state changed to {reg31}.", gpu_debug),
		(try_end),
	]),
	
# script_oath_cancel_quest_if_active
# PURPOSE: If a given quest is active then cancel it without penalty.
# EXAMPLE: (call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
("oath_cancel_quest_if_active",
	[ 
		(store_script_param, ":quest_no", 1),
		
		(try_begin),
			(check_quest_active, ":quest_no"),
			(quest_get_slot, ":unique_script", ":quest_no", slot_quest_unique_script),
			(call_script, ":unique_script", OATH_QUEST_CANCEL),
		(try_end),
	]),
	
# script_oath_check_quest_success_if_active
# PURPOSE: If a given quest is active then check if it has met the victory conditions.
# EXAMPLE: (call_script, "script_oath_check_quest_success_if_active", ":quest_no"),
("oath_check_quest_success_if_active",
	[ 
		(store_script_param, ":quest_no", 1),
		
		(try_begin),
			(check_quest_active, ":quest_no"),
			(quest_get_slot, ":unique_script", ":quest_no", slot_quest_unique_script),
			(call_script, ":unique_script", OATH_QUEST_VICTORY_CONDITION),
		(try_end),
	]),
	
# script_cf_oath_mission_is_active
# PURPOSE: Checks to see if any valid "Away" missions are active.
# EXAMPLE: (call_script, "script_cf_oath_mission_is_active"),
("cf_oath_mission_is_active",
	[ 
		(this_or_next|check_quest_active, "qst_oath_butchers_bill"),	# Quest #5
		(this_or_next|check_quest_active, "qst_oath_sealed_letter"),	# Quest #6
		(this_or_next|check_quest_active, "qst_oath_courage_casks"),	# Quest #7
		(this_or_next|check_quest_active, "qst_oath_scouting_ahead"),	# Quest #8
		(this_or_next|check_quest_active, "qst_oath_only_the_finest"),	# Quest #9
		(check_quest_active, "qst_oath_make_your_mark"),				# Quest #10
	]),
	
# script_oath_refresh_unique_scripts
# PURPOSE: Refreshes the "unique script" slot for Oathbound quests to prevent save game irregularities after script updates.
# EXAMPLE: (call_script, "script_oath_refresh_unique_scripts"),
("oath_refresh_unique_scripts",
	[ 
		(quest_set_slot, "qst_oath_desertion", 			slot_quest_unique_script, "script_quest_oathbound_desertion"), 			# Quest #1
		(quest_set_slot, "qst_oath_separated", 			slot_quest_unique_script, "script_quest_oathbound_separated"), 			# Quest #2
		(quest_set_slot, "qst_oath_prisoners_of_war", 	slot_quest_unique_script, "script_quest_oathbound_prisoners_of_war"), 	# Quest #3
		(quest_set_slot, "qst_oath_leave", 				slot_quest_unique_script, "script_quest_oathbound_leave"), 				# Quest #4
		(quest_set_slot, "qst_oath_butchers_bill",		slot_quest_unique_script, "script_quest_oathbound_butchers_bill"),		# Quest #5
		(quest_set_slot, "qst_oath_sealed_letter",		slot_quest_unique_script, "script_quest_oathbound_sealed_letter"),		# Quest #6
		(quest_set_slot, "qst_oath_courage_casks",		slot_quest_unique_script, "script_quest_oathbound_courage_casks"),		# Quest #7
		(quest_set_slot, "qst_oath_scouting_ahead",		slot_quest_unique_script, "script_quest_oathbound_scouting_ahead"),		# Quest #8
		(quest_set_slot, "qst_oath_only_the_finest",	slot_quest_unique_script, "script_quest_oathbound_only_the_finest"),	# Quest #9
		(quest_set_slot, "qst_oath_make_your_mark",		slot_quest_unique_script, "script_quest_oathbound_make_your_mark"),		# Quest #10
		(quest_set_slot, "qst_oath_fresh_meat",			slot_quest_unique_script, "script_quest_oathbound_fresh_meat"),			# Quest #13
		
	]),
	
# script_cf_oath_quest_allowed_for_selection
# PURPOSE: This prevents certain quests from showing up in the quest selection UI in the event that they're function based quests or unfinished.
# EXAMPLE: (call_script, "script_cf_oath_quest_allowed_for_selection", ":quest_no"),
("cf_oath_quest_allowed_for_selection",
	[ 
		(store_script_param, ":quest_no", 1),
		
		(neq, ":quest_no", "qst_oath_desertion"),		# Quest #1 - Oathbound Function
		(neq, ":quest_no", "qst_oath_separated"),		# Quest #2 - Oathbound Function
		(neq, ":quest_no", "qst_oath_leave"),			# Quest #4 - Oathbound Function
		
		## Unfinished Quests Within OATHBOUND_QUESTS_BEGIN to OATHBOUND_QUESTS_END
		(neq, ":quest_no", "qst_oath_reserved_11"),
		(neq, ":quest_no", "qst_oath_reserved_12"),
		(neq, ":quest_no", "qst_oath_reserved_14"),
		(neq, ":quest_no", "qst_oath_reserved_15"),
		(neq, ":quest_no", "qst_oath_reserved_16"),
		(neq, ":quest_no", "qst_oath_reserved_17"),
		(neq, ":quest_no", "qst_oath_reserved_18"),
		(neq, ":quest_no", "qst_oath_reserved_19"),
		(neq, ":quest_no", "qst_oath_reserved_20"),
		(neq, ":quest_no", "qst_oath_reserved_21"),
		(neq, ":quest_no", "qst_oath_reserved_22"),
		(neq, ":quest_no", "qst_oath_reserved_23"),
		(neq, ":quest_no", "qst_oath_reserved_24"),
		(neq, ":quest_no", "qst_oath_reserved_25"),
		(neq, ":quest_no", "qst_oath_reserved_26"),
		(neq, ":quest_no", "qst_oath_reserved_27"),
		(neq, ":quest_no", "qst_oath_reserved_28"),
		(neq, ":quest_no", "qst_oath_reserved_29"),
		(neq, ":quest_no", "qst_oath_reserved_30"),
		
	]),
	
	
# script_cf_oath_player_meets_minimum_rank_for_quest
# PURPOSE: Quick filter to ensure a quest meets the minimum requirement.
# EXAMPLE: (call_script, "script_cf_oath_player_meets_minimum_rank_for_quest", ":quest_no"),
("cf_oath_player_meets_minimum_rank_for_quest",
	[ 
		(store_script_param, ":quest_no", 1),
		
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(assign, ":rank_current", reg1),
		(call_script, "script_oath_quest_get_minimum_rank_requirement", ":quest_no"), # Returns reg1 (minimum rank)
		(assign, ":rank_requirement", reg1),
		(ge, ":rank_current", ":rank_requirement"),
	]),
	
# script_oath_quest_get_minimum_rank_requirement
# PURPOSE: Consolidated location for determining a quest's oathbound rank requirement.
# EXAMPLE: (call_script, "script_oath_quest_get_minimum_rank_requirement", ":quest_no"), # Returns reg1 (minimum rank)
("oath_quest_get_minimum_rank_requirement",
	[ 
		(store_script_param, ":quest_no", 1),
		
		(assign, reg1, OATHBOUND_RANK_INITIATE),
		(try_begin),
			### RANK 2 QUESTS - OATHBOUND_RANK_MILITIA ###
			(this_or_next|eq, ":quest_no", "qst_oath_butchers_bill"),
			(this_or_next|eq, ":quest_no", "qst_oath_sealed_letter"),
			(this_or_next|eq, ":quest_no", "qst_oath_courage_casks"),
			(this_or_next|eq, ":quest_no", "qst_oath_scouting_ahead"),
			(this_or_next|eq, ":quest_no", "qst_oath_only_the_finest"),
			(eq, ":quest_no", "qst_oath_leave"),
			(assign, reg1, OATHBOUND_RANK_MILITIA),
		(else_try),
			### RANK 3 QUESTS - OATHBOUND_RANK_SERGEANT ###
			(this_or_next|eq, ":quest_no", "qst_oath_make_your_mark"),
			(eq, ":quest_no", "qst_oath_fresh_meat"),
			(assign, reg1, OATHBOUND_RANK_SERGEANT),
		# (else_try),
			# ### RANK 4 QUESTS - OATHBOUND_RANK_CAPTAIN ###
			# # (eq, ":quest_no", "qst_oath_leave"),
			# (assign, reg1, OATHBOUND_RANK_CAPTAIN),
		# (else_try),
			# ### RANK 5 QUESTS - OATHBOUND_RANK_GREAT_CAPTAIN ###
			# # (eq, ":quest_no", "qst_oath_leave"),
			# (assign, reg1, OATHBOUND_RANK_GREAT_CAPTAIN),
		# (else_try),
			# ### RANK 6 QUESTS - OATHBOUND_RANK_HEDGE_KNIGHT ###
			# # (eq, ":quest_no", "qst_oath_leave"),
			# (assign, reg1, OATHBOUND_RANK_HEDGE_KNIGHT),
		# (else_try),
			# ### RANK 7 QUESTS - OATHBOUND_RANK_ELDER_KNIGHT ###
			# # (eq, ":quest_no", "qst_oath_leave"),
			# (assign, reg1, OATHBOUND_RANK_ELDER_KNIGHT),
		# (else_try),
			# ### RANK 8 QUESTS - OATHBOUND_RANK_VASSAL_KNIGHT ###
			# # (eq, ":quest_no", "qst_oath_leave"),
			# (assign, reg1, OATHBOUND_RANK_VASSAL_KNIGHT),
		(try_end),
	]),
	
# script_oath_get_random_lord
# PURPOSE: Picks a lord based on preference settings compared to the given lord's number.  Used for quests.
# EXAMPLE: (call_script, "script_oath_get_random_lord", ":troop_giver", OATHBOUND_LORD_PREF_ANY_LORD), # Returns reg1 (lord troop #)
("oath_get_random_lord",
	[ 
		(store_script_param, ":troop_giver", 1),
		(store_script_param, ":preference", 2),
		
		# OATHBOUND_LORD_PREF_ENEMY_LORD
		# OATHBOUND_LORD_PREF_FRIENDLY_LORD
		# OATHBOUND_LORD_PREF_ANY_LORD
		# OATHBOUND_LORD_PREF_ENEMY_RULER
		# OATHBOUND_LORD_PREF_FRIENDLY_RULER
		# OATHBOUND_LORD_PREF_ANY_RULER
		
		(assign, ":target_lord", -1),
		(store_troop_faction, ":faction_giver", ":troop_giver"),
		(try_begin),
			## PREFERENCE - LORDS
			(this_or_next|eq, ":preference", OATHBOUND_LORD_PREF_ENEMY_LORD),
			(this_or_next|eq, ":preference", OATHBOUND_LORD_PREF_FRIENDLY_LORD),
			(eq, ":preference", OATHBOUND_LORD_PREF_ANY_LORD),
			(try_for_range, ":troop_no", active_npcs_begin, active_npcs_end),
				(troop_slot_eq, ":troop_no", slot_troop_occupation, slto_kingdom_hero),	# We only care about active vassals.
				(store_troop_faction, ":faction_target", ":troop_no"),
				(store_relation, ":relation", ":faction_target", ":faction_giver"),
				# Apply our filter
				(assign, ":pass", 0),
				(try_begin),
					(this_or_next|ge, ":relation", 0),
					(eq, ":preference", OATHBOUND_LORD_PREF_FRIENDLY_LORD),
					(assign, ":pass", 1),
				(else_try),
					(this_or_next|lt, ":relation", 0),
					(eq, ":preference", OATHBOUND_LORD_PREF_ENEMY_LORD),
					(assign, ":pass", 1),
				(try_end),
				(this_or_next|eq, ":pass", 1),
				(eq, ":preference", OATHBOUND_LORD_PREF_ANY_LORD),
				# Apply a random filter to prevent the same lords being chosen.
				(store_random_in_range, ":roll", 0, 100),
				(lt, ":roll", 20),
				(eq, ":target_lord", -1), # Grab the first hit.
				(assign, ":target_lord", ":troop_no"),
			(try_end),
			
		(else_try),
			## PREFERENCE - RULERS
			(this_or_next|eq, ":preference", OATHBOUND_LORD_PREF_ENEMY_RULER),
			(this_or_next|eq, ":preference", OATHBOUND_LORD_PREF_FRIENDLY_RULER),
			(eq, ":preference", OATHBOUND_LORD_PREF_ANY_RULER),
			(try_for_range, ":kingdom_no", kingdoms_begin, kingdoms_end),
				(faction_get_slot, ":troop_no", ":kingdom_no", slot_faction_leader),
				(store_troop_faction, ":faction_target", ":troop_no"),
				(store_relation, ":relation", ":faction_target", ":faction_giver"),
				# Apply our filter
				(assign, ":pass", 0),
				(try_begin),
					(this_or_next|ge, ":relation", 0),
					(eq, ":preference", OATHBOUND_LORD_PREF_FRIENDLY_RULER),
					(assign, ":pass", 1),
				(else_try),
					(this_or_next|lt, ":relation", 0),
					(eq, ":preference", OATHBOUND_LORD_PREF_ENEMY_RULER),
					(assign, ":pass", 1),
				(try_end),
				(this_or_next|eq, ":pass", 1),
				(eq, ":preference", OATHBOUND_LORD_PREF_ANY_RULER),
				# Apply a random filter to prevent the same lords being chosen.
				(store_random_in_range, ":roll", 0, 100),
				(lt, ":roll", 50),
				(eq, ":target_lord", -1), # Grab the first hit.
				(assign, ":target_lord", ":troop_no"),
			(try_end),
		(try_end),
		(assign, reg1, ":target_lord"),
	]),
	
	
# script_cf_oath_kingdom_status_is
# PURPOSE: Checks if a faction is at war or peace and fails if it is not in the desired condition.
# EXAMPLE: (call_script, "script_cf_oath_kingdom_status_is", OATHBOUND_KINGDOM_STATUS_WAR),
("cf_oath_kingdom_status_is",
	[ 
		(store_script_param, ":preference", 1),
		
		# OATHBOUND_KINGDOM_STATUS_WAR
		# OATHBOUND_KINGDOM_STATUS_PEACE
		
		(assign, ":at_war", 0),
		(store_troop_faction, ":faction_oathbound", "$oathbound_master"),
		(try_for_range, ":kingdom_no", kingdoms_begin, kingdoms_end),
			(neq, ":kingdom_no", ":faction_oathbound"),
			(faction_slot_eq, ":kingdom_no", slot_faction_state, sfs_active),
			(store_relation, ":relation", ":faction_oathbound", ":kingdom_no"),
			(lt, ":relation", 0),
			(assign, ":at_war", 1),
		(try_end),
		
		(assign, ":pass", 0),
		(try_begin),
			(eq, ":at_war", 1),
			(eq, ":preference", OATHBOUND_KINGDOM_STATUS_WAR),
			(assign, ":pass", 1),
		(else_try),
			(eq, ":at_war", 0),
			(eq, ":preference", OATHBOUND_KINGDOM_STATUS_PEACE),
			(assign, ":pass", 1),
		(try_end),
		(eq, ":pass", 1),
	]),
	
# script_cf_oath_player_has_item_with_modifier
# PURPOSE: Checks if the player has a specific item with a specific modifier.  Used in quest "Only the Finest".
# EXAMPLE: (call_script, "script_cf_oath_player_has_item_with_modifier", ":item_no", ":imod"), # Returns reg1 (inventory slot item is in)
("cf_oath_player_has_item_with_modifier",
	[
		(store_script_param, ":item_no", 1),
		(store_script_param, ":imod", 2),
		
		(player_has_item, ":item_no"),
		(assign, ":inventory_slot", -1),
		(troop_get_inventory_capacity, ":inv_size", "trp_player"),
		(try_for_range, ":i_slot", 10, ":inv_size"),
			(troop_get_inventory_slot, ":item_current", "trp_player", ":i_slot"),
			(eq, ":item_current", ":item_no"),
			(troop_get_inventory_slot_modifier, ":imod_current", "trp_player", ":i_slot"),
			(eq, ":imod_current", ":imod"),
			(assign, ":inventory_slot", ":i_slot"),
			(assign, ":inv_size", 0), #break
		(try_end),
		(neq, ":inventory_slot", -1),
		(assign, reg1, ":inventory_slot"),
	]),
  
####################################
###    SPECIFIC QUEST SCRIPTS    ###
####################################

############################
### QUEST #1 - DESERTION ###
############################
# script_quest_oathbound_desertion
# PURPOSE: Handles all quest specific actions for quest "qst_oath_desertion".
# EXAMPLE: (call_script, "script_quest_oathbound_desertion", FUNCTION),
("quest_oathbound_desertion",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_desertion"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_01"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_desertion"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					30),			# No expiration.
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			0),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	0),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,   						0), 
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(str_store_string, s61, "@You have been branded a deserter!  There's still a chance to keep your head from the headsman's block if you track down {s21}'s army and swear allegiance again or pay off the remainder of your contract."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			# Entry into desertion always penalizes rating & reputation.
			(call_script, "script_oath_change_oathbound_rating", -100),
			(call_script, "script_oath_change_oathbound_reputation", -30),
			
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			# Remove you from the oathbound system.
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_NOT_HIRED),
			(call_script, "script_oath_change_oathbound_rating", OATHBOUND_VALUE_RESET),
			(call_script, "script_oath_change_oathbound_reputation", -30),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 0),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
############################
### QUEST #2 - SEPARATED ###
############################
# script_quest_oathbound_separated
# PURPOSE: Handles all quest specific actions for quest "qst_oath_separated".
# EXAMPLE: (call_script, "script_quest_oathbound_separated", FUNCTION),
("quest_oathbound_separated",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_separated"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_02"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_separated"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					0),				# No expiration.
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			0),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	0),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,   						0), 
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(str_store_string, s61, "@You have been separated from {s21}'s army and must return or risk being branded a deserter."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 10),
			(call_script, "script_oath_change_oathbound_reputation", 2),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 2, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_quest_oathbound_desertion", OATH_QUEST_BEGIN),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 0),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
###################################
### QUEST #3 - PRISONERS OF WAR ###
###################################
# script_quest_oathbound_prisoners_of_war
# PURPOSE: Handles all quest specific actions for quest "qst_oath_prisoners_of_war".
# EXAMPLE: (call_script, "script_quest_oathbound_prisoners_of_war", FUNCTION),
("quest_oathbound_prisoners_of_war",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_prisoners_of_war"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_03"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_prisoners_of_war"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					0),			# No expiration.
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			4),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	4),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					10), 
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(quest_get_slot, reg21, ":quest_no", slot_quest_target_amount),
			(str_store_string, s61, "@{s21} wishes to gather a number of prisoners for a future exchange and has tasked your squad with incapacitating {reg21} troops.  This will require the use of a blunt weapon to ensure they are merely rendered unconscious."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			(call_script, "script_quest_oathbound_prisoners_of_war", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(quest_get_slot, reg21, ":quest_no", slot_quest_temp_slot),
				(quest_get_slot, reg22, ":quest_no", slot_quest_target_amount),
				(str_store_string, s65, "@You have helped capture {reg21} of the {reg22} enemies required."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			#(display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 5),
			(call_script, "script_oath_change_oathbound_reputation", 2),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -15),
			(call_script, "script_oath_change_oathbound_reputation", -6),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			(try_begin),
				(quest_get_slot, ":goal", ":quest_no", slot_quest_target_amount), 
				(quest_slot_ge, ":quest_no", slot_quest_temp_slot, ":goal"),
				(call_script, "script_quest_oathbound_prisoners_of_war", OATH_QUEST_SUCCEED),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
################################
### QUEST #4 - LEAVE OF DUTY ###
################################
# script_quest_oathbound_leave
# PURPOSE: Handles all quest specific actions for quest "qst_oath_leave".
# EXAMPLE: (call_script, "script_quest_oathbound_leave", FUNCTION),
("quest_oathbound_leave",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_leave"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_04"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_leave"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			30),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	30),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,   						0), 
			# Setup expiration period based on rank.
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(assign, ":rank", reg1),
			(try_begin),
				(eq, ":rank", OATHBOUND_RANK_MILITIA),
				(assign, ":duration", 30),
				(str_store_string, s22, "@, but must return within one month"),
			(else_try),
				(this_or_next|eq, ":rank", OATHBOUND_RANK_SERGEANT),
				(eq, ":rank", OATHBOUND_RANK_CAPTAIN),
				(assign, ":duration", 45),
				(str_store_string, s22, "@, but must return within one and a half months"),
			(else_try),
				(eq, ":rank", OATHBOUND_RANK_GREAT_CAPTAIN),
				(assign, ":duration", 60),
				(str_store_string, s22, "@, but must return within two months"),
			(else_try),
				(this_or_next|eq, ":rank", OATHBOUND_RANK_HEDGE_KNIGHT),
				(this_or_next|eq, ":rank", OATHBOUND_RANK_ELDER_KNIGHT),
				(eq, ":rank", OATHBOUND_RANK_VASSAL_KNIGHT),
				(assign, ":duration", 0),
				(str_clear, s22),
			(else_try),
				(assign, ":duration", 30),
				(str_store_string, s22, "@, but must return within one month"),
			(try_end),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days, ":duration"),
			# Setup quest description.
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(str_store_string, s61, "@You have been granted leave by {s21}'s order{s22}.  During this period the remaining time on your contract will not continue until you return.  If you fail to return by the allotted time you will be branded a deserter."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 3),
			(call_script, "script_oath_change_oathbound_reputation", 1),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(try_begin),
				## $oathbound_master is a prisoner -> SEPARATED
				(troop_slot_ge, "$oathbound_master", slot_troop_prisoner_of_party, 0),
				(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_SEPARATED),
			(else_try),
				## $oathbound_master is NOT a prisoner -> DESERTER
				(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_DESERTER),
			(try_end),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 0),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
#####################################
### QUEST #5 - THE BUTCHER'S BILL ###
#####################################
# script_quest_oathbound_butchers_bill
# PURPOSE: Handles all quest specific actions for quest "qst_oath_butchers_bill".
# EXAMPLE: (call_script, "script_quest_oathbound_butchers_bill", FUNCTION),
("quest_oathbound_butchers_bill",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_butchers_bill"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_05"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_butchers_bill"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					30),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			8),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	8),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(store_random_in_range, ":cattle", 6, 14),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					":cattle"), 
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),
			(quest_set_slot, ":quest_no", slot_quest_target_party,						-1), # Must be -1 so a driven herd party takes this slot.
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(quest_get_slot, reg21, ":quest_no", slot_quest_target_amount),
			(str_store_string, s61, "@{s21} has tasked you with bringing back {reg21} head of cattle to supply the army with fresh beef.  You may accomplish this however you feel appropriate so long as you do not dishonor {s21}."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Pay the player a reasonable sum to afford the cattle.
			(store_item_value, ":cattle_cost", "itm_cattle_meat"),
			(call_script, "script_game_get_item_buy_price_factor", "itm_cattle_meat"),
			(val_mul, ":cattle_cost", reg0),
			#Multiplied by 2 and divided by 100
			(val_div, ":cattle_cost", 50),
			(store_mul, ":payment", ":cattle", ":cattle_cost"),
			(str_store_string, s11, "@ to purchase the required cattle"),
			(call_script, "script_oath_pay_player_because_s11", ":payment"),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			(call_script, "script_quest_oathbound_butchers_bill", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(quest_get_slot, reg21, ":quest_no", slot_quest_temp_slot),
				(quest_get_slot, reg22, ":quest_no", slot_quest_target_amount),
				(str_store_string, s65, "@You have brought back {reg21} of the {reg22} cattle you were tasked with."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			#(display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 4),
			(call_script, "script_oath_change_oathbound_reputation", 2),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(set_show_messages, 0),
			(fail_quest, ":quest_no"),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -12),
			(call_script, "script_oath_change_oathbound_reputation", -6),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			(try_begin),
				(quest_get_slot, ":goal", ":quest_no", slot_quest_target_amount), 
				(quest_slot_ge, ":quest_no", slot_quest_temp_slot, ":goal"),
				(call_script, "script_quest_oathbound_butchers_bill", OATH_QUEST_SUCCEED),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	

####################################
### QUEST #6 - THE SEALED LETTER ###
####################################
# script_quest_oathbound_sealed_letter
# PURPOSE: Handles all quest specific actions for quest "qst_oath_sealed_letter".
# EXAMPLE: (call_script, "script_quest_oathbound_sealed_letter", FUNCTION),
("quest_oathbound_sealed_letter",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_sealed_letter"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_06"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_SEALED_LETTER_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_sealed_letter"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					30),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			6),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	6),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					0), 
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),
			
			# Determine our target to deliver the letter to.
			(call_script, "script_oath_get_random_lord", "$oathbound_master", OATHBOUND_LORD_PREF_ENEMY_LORD), # Returns reg1 (lord troop #)
			(try_begin),
				(eq, reg1, -1), # Failed our attempt.
				(call_script, "script_oath_get_random_lord", "$oathbound_master", OATHBOUND_LORD_PREF_ENEMY_LORD), # Returns reg1 (lord troop #)
			(try_end),
			(try_begin),
				(eq, reg1, -1), # Failed our attempt again.  Now let's just grab any lord.
				(call_script, "script_oath_get_random_lord", "$oathbound_master", OATHBOUND_LORD_PREF_ANY_LORD), # Returns reg1 (lord troop #)
			(try_end),
			(assign, ":object_troop", reg1),
			(quest_set_slot, ":quest_no", slot_quest_object_troop, ":object_troop"),
			# Setup our quest description.
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(str_store_troop_name_link, s22, ":object_troop"),
			(troop_get_type, reg1, "$oathbound_master"),
			(troop_get_type, reg2, ":object_troop"),
			(store_troop_faction, ":target_faction", ":object_troop"),
			(str_store_faction_name_link, s23, ":target_faction"),
			(str_store_string, s61, "@{s21} has tasked you with tracking down {s22} of the {s23} and delivering a sealed letter to {reg2?her:him} without reading the contents.  {reg1?She:He} expects your return with {reg2?her:his} reply within a month's time.  Discretion has been urged so you must ensure that you are not captured during your travels."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Pay the player a modest amount for travel expenses.
			(str_store_string, s11, "@ to cover travel expenses"),
			(call_script, "script_oath_pay_player_because_s11", 200),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_SEALED_LETTER_DELIVERED),
				(quest_get_slot, ":object_troop", ":quest_no", slot_quest_object_troop),
				(str_store_troop_name_link, s21, "$oathbound_master"),
				(str_store_troop_name_link, s22, ":object_troop"),
				(troop_get_type, reg1, ":object_troop"),
				(str_store_string, s65, "@You have delivered the letter to {s22}.  Now return to {s21} with {reg1?her:his} reply."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			(display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 3),
			(call_script, "script_oath_change_oathbound_reputation", 1),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(set_show_messages, 0),
			(fail_quest, ":quest_no"),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -9),
			(call_script, "script_oath_change_oathbound_reputation", -3),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
###################################
### QUEST #7 - CASKS OF COURAGE ###
###################################
# script_quest_oathbound_courage_casks
# PURPOSE: Handles all quest specific actions for quest "qst_oath_courage_casks".
# EXAMPLE: (call_script, "script_quest_oathbound_courage_casks", FUNCTION),
("quest_oathbound_courage_casks",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_courage_casks"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_07"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_courage_casks"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					20),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			5),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	5),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					6), 
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),
			(quest_set_slot, ":quest_no", slot_quest_target_party,						0),
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(quest_get_slot, reg21, ":quest_no", slot_quest_target_amount),
			(str_store_string, s61, "@The army quartermaster has sent you with coin to purchase {reg21} casks of ale for restocking the wagons.  An army needs a steady supply of ale to celebrate its victories and drown its losses so your task, though seemingly mundane, is important."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Pay the player a reasonable sum to afford the cattle.
			(quest_get_slot, ":target_amount", ":quest_no", slot_quest_target_amount),
			(store_item_value, ":cask_cost", "itm_ale"),
			(store_mul, ":payment", ":target_amount", ":cask_cost"),
			(str_store_string, s11, "@ to purchase the required casks of ale"),
			(call_script, "script_oath_pay_player_because_s11", ":payment"),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			(call_script, "script_quest_oathbound_courage_casks", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(quest_get_slot, reg21, ":quest_no", slot_quest_temp_slot),
				(quest_get_slot, reg22, ":quest_no", slot_quest_target_amount),
				(str_store_string, s65, "@You have obtained {reg21} of the {reg22} ale casks you were sent for."),
				(assign, ":note_slot", 3),
				(str_clear, s1),
				(add_quest_note_from_sreg, ":quest_no", 4, s1, 0), # Do this in the event we lost some casks and need to clear out completion.
			(else_try),
				(eq, ":quest_stage", OATH_QUEST_STAGE_GOAL_MET),
				(str_store_troop_name, s21, "$oathbound_master"),
				(str_store_string, s65, "@You have the required ale.  Now just join back with {s21}'s army to turn them in."),
				(assign, ":note_slot", 4),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			# (display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 5),
			(call_script, "script_oath_change_oathbound_reputation", 2),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(set_show_messages, 0),
			(fail_quest, ":quest_no"),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -15),
			(call_script, "script_oath_change_oathbound_reputation", -6),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			(try_begin),
				(quest_get_slot, ":goal", ":quest_no", slot_quest_target_amount),
				(store_item_kind_count, ":casks_carried", "itm_ale", "trp_player"),
				(ge, ":casks_carried", ":goal"),
				(troop_remove_items, "trp_player", "itm_ale", ":goal"),
				(val_sub, ":casks_carried", ":goal"),
				(try_begin),
					(ge, ":casks_carried", 1), # Player still has some.
					(store_item_value, ":cask_cost", "itm_ale"),
					(store_mul, ":payment", ":casks_carried", ":cask_cost"),
					(str_store_string, s11, "@ to for the extra casks of ale you've brought back"),
					(call_script, "script_oath_pay_player_because_s11", ":payment"),
					(troop_remove_items, "trp_player", "itm_ale", ":casks_carried"),
				(try_end),
				(call_script, "script_quest_oathbound_courage_casks", OATH_QUEST_SUCCEED),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
#################################
### QUEST #8 - SCOUTING AHEAD ###
#################################
# script_quest_oathbound_scouting_ahead
# PURPOSE: Handles all quest specific actions for quest "qst_oath_scouting_ahead".
# EXAMPLE: (call_script, "script_quest_oathbound_scouting_ahead", FUNCTION),
("quest_oathbound_scouting_ahead",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_scouting_ahead"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_08"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_scouting_ahead"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					20),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			5),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	5),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					0), 
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),
			(quest_set_slot, ":quest_no", slot_quest_target_party,						0),
			
			## Choose our waypoints.
			# $oathbound_waypoint_1			= (Party #)	- Tracks the first waypoint in quest "oath_scouting_ahead".
			# $oathbound_waypoint_2			= (Party #)	- Tracks the second waypoint in quest "oath_scouting_ahead".
			# $oathbound_waypoint_3			= (Party #)	- Tracks the third waypoint in quest "oath_scouting_ahead".
			# $oathbound_waypoint_1_visited	= (Boolean)	- Tracks if you have scouted the first waypoint in quest "oath_scouting_ahead".
			# $oathbound_waypoint_2_visited	= (Boolean)	- Tracks if you have scouted the second waypoint in quest "oath_scouting_ahead".
			# $oathbound_waypoint_3_visited	= (Boolean)	- Tracks if you have scouted the third waypoint in quest "oath_scouting_ahead".
			(try_begin),
				(assign, ":end_cond", 100),
				(try_for_range, ":unused", 0, ":end_cond"),
					(assign, reg21, 0),
					(assign, reg22, 0),
					(assign, reg23, 0),
					(assign, "$oathbound_waypoint_1", -1),
					(assign, "$oathbound_waypoint_2", -1),
					(assign, "$oathbound_waypoint_3", -1),
					(try_begin),
						(lt, "$oathbound_waypoint_1", 0),
						(call_script, "script_cf_get_random_enemy_center_within_range", "$oathbound_party", 50),
						(assign, "$oathbound_waypoint_1", reg0),
						(assign, reg21, 1),
					(try_end),
					(try_begin),
						(lt, "$oathbound_waypoint_2", 0),
						(call_script, "script_cf_get_random_enemy_center_within_range", "$oathbound_party", 50),
						(neq, "$oathbound_waypoint_1", reg0),
						(assign, "$oathbound_waypoint_2", reg0),
						(assign, reg22, 1),
					(try_end),
					(try_begin),
						(lt, "$oathbound_waypoint_3", 0),
						(call_script, "script_cf_get_random_enemy_center_within_range", "$oathbound_party", 50),
						(neq, "$oathbound_waypoint_1", reg0),
						(neq, "$oathbound_waypoint_2", reg0),
						(assign, "$oathbound_waypoint_3", reg0),
						(assign, reg23, 1),
					(try_end),
					(neq, "$oathbound_waypoint_1", "$oathbound_waypoint_2"),
					(neq, "$oathbound_waypoint_1", "$oathbound_waypoint_2"),
					(neq, "$oathbound_waypoint_2", "$oathbound_waypoint_3"),
					(ge, "$oathbound_waypoint_1", 0),
					(ge, "$oathbound_waypoint_2", 0),
					(ge, "$oathbound_waypoint_3", 0),
					(assign, ":end_cond", 0),
				(try_end),
				(assign, "$oathbound_waypoint_1_visited", 0),
				(assign, "$oathbound_waypoint_2_visited", 0),
				(assign, "$oathbound_waypoint_3_visited", 0),
			(try_end),
			
			(str_clear, s20),
			(try_begin),
				(str_store_party_name_link, s21, "$oathbound_waypoint_1"),
				(str_store_string, s20, s21),
				(try_begin),
					(is_between, "$oathbound_waypoint_2", centers_begin, centers_end),
					(str_store_party_name_link, s22, "$oathbound_waypoint_2"),
					(str_store_string, s20, "@{s20}, {s22}"),
				(try_end),
				(try_begin),
					(is_between, "$oathbound_waypoint_3", centers_begin, centers_end),
					(str_store_party_name_link, s22, "$oathbound_waypoint_3"),
					(str_store_string, s20, "@{s20} and {s22}"),
				(try_end),
			(try_end),
			(str_store_troop_name_link, s24, "$oathbound_master"),
			(str_store_string, s61, "@You have been tasked with scouting the area around {s20} to look for suitable camping sites for {s24}'s army and check for enemy ambushes.  It is imperative that you remain undetected during your travels to prevent alerting {s24}'s enemies of his passage."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s63, ":cur_hours"),
			(str_store_string, s63, "@[{s63}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				# Scouted the first waypoint.
				(try_begin),
					(party_is_active, "$oathbound_waypoint_1"),
					(str_store_party_name_link, s21, "$oathbound_waypoint_1"),
					(try_begin),
						(eq, "$oathbound_waypoint_1_visited", 1),
						(str_store_string, s65, "@You have scouted around the area of {s21}. (Objective Completed)"),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 3, s64, 0),
					(else_try),
						(str_store_string, s65, "@You need to scout near {s21}."),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 3, s64, 0),
					(try_end),
				(try_end),
				# Scouted the second waypoint.
				(try_begin),
					(party_is_active, "$oathbound_waypoint_2"),
					(str_store_party_name_link, s22, "$oathbound_waypoint_2"),
					(try_begin),
						(eq, "$oathbound_waypoint_2_visited", 1),
						(str_store_string, s65, "@You have scouted around the area of {s22}. (Objective Completed)"),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 4, s64, 0),
					(else_try),
						(str_store_string, s65, "@You need to scout near {s22}."),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 4, s64, 0),
					(try_end),
				(try_end),
				# Scouted the third waypoint.
				(try_begin),
					(party_is_active, "$oathbound_waypoint_3"),
					(str_store_party_name_link, s23, "$oathbound_waypoint_3"),
					(try_begin),
						(eq, "$oathbound_waypoint_3_visited", 1),
						(str_store_string, s65, "@You have scouted around the area of {s23}. (Objective Completed)"),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 5, s64, 0),
					(else_try),
						(str_store_string, s65, "@You need to scout near {s23}."),
						(str_store_string, s64, "@{s63} {s65}"),
						(add_quest_note_from_sreg, ":quest_no", 5, s64, 0),
					(try_end),
					(display_message, "str_quest_log_updated"),
				(try_end),
			(else_try),
				(eq, ":quest_stage", OATH_QUEST_STAGE_GOAL_MET),
				(str_store_troop_name_link, s24, "$oathbound_master"),
				(str_store_string, s65, "@You have scouted all of the areas.  Return to {s24} to give your report."),
				(str_store_string, s64, "@{s64} {s65}"),
				(add_quest_note_from_sreg, ":quest_no", 6, s64, 0),
				(display_message, "str_quest_log_updated"),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 5),
			(call_script, "script_oath_change_oathbound_reputation", 2),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(set_show_messages, 0),
			(fail_quest, ":quest_no"),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -15),
			(call_script, "script_oath_change_oathbound_reputation", -6),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			# All objectives complete.
			(try_begin),
				(this_or_next|eq, "$oathbound_waypoint_1_visited", 1),
				(eq, "$oathbound_waypoint_1", -1),
				(this_or_next|eq, "$oathbound_waypoint_2_visited", 1),
				(eq, "$oathbound_waypoint_2", -1),
				(this_or_next|eq, "$oathbound_waypoint_3_visited", 1),
				(eq, "$oathbound_waypoint_3", -1),
				(call_script, "script_oath_quest_change_state", "qst_oath_scouting_ahead", OATH_QUEST_STAGE_GOAL_MET),
				(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_UPDATE),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 0),
			(call_script, "script_cf_oath_kingdom_status_is", OATHBOUND_KINGDOM_STATUS_WAR),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
##################################
### QUEST #9 - ONLY THE FINEST ###
##################################
# script_quest_oathbound_only_the_finest
# PURPOSE: Handles all quest specific actions for quest "qst_oath_only_the_finest".
# EXAMPLE: (call_script, "script_quest_oathbound_only_the_finest", FUNCTION),
("quest_oathbound_only_the_finest",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_only_the_finest"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_09"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_only_the_finest"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					0),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			15),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	15),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_party,						0),
			
			## CHOOSE OUR ITEM/IMOD COMBINATION:
			(store_random_in_range, ":roll", 0, 5),
			(try_begin),
				(eq, ":roll", 0), # Heavy Plate Mittens
				(assign, ":item_no", "itm_plate_mittens"),
				(assign, ":imod", imod_heavy),
			(else_try),
				(eq, ":roll", 1), # Heavy Plate Boots
				(assign, ":item_no", "itm_plate_boots"),
				(assign, ":imod", imod_heavy),
			(else_try),
				(eq, ":roll", 2), # Balanced Ornate Knight Sword
				(assign, ":item_no", "itm_jack_faramir"),
				(assign, ":imod", imod_balanced),
			(else_try),
				(eq, ":roll", 3), # Tempered Morningstar
				(assign, ":item_no", "itm_morningstar"),
				(assign, ":imod", imod_tempered),
			(else_try),
				(eq, ":roll", 4), # Fine War Bow
				(assign, ":item_no", "itm_war_bow"),
				(assign, ":imod", imod_fine),
			(try_end),
			(quest_set_slot, ":quest_no", slot_quest_target_amount, ":item_no"), # Item #
			(quest_set_slot, ":quest_no", slot_quest_temp_slot, ":imod"), # IMOD #
			# Setup our quest text.
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(call_script, "script_cci_describe_imod_to_s1", ":imod", 0), # cci_scripts.py
			(str_store_item_name, s22, ":item_no"),
			(str_store_string, s23, "@{s1} {s22}"),
			(str_store_string, s61, "@{s21} has sent you to find a blacksmith capable of crafting a {s23} worth carrying.  The exact type and quality of weapon was quite specific so care must be taken in relaying the proper instructions for commissioning."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Pay the player a reasonable sum to afford the commission.
			(call_script, "script_cci_get_commission_price", ":item_no", ":imod"), # Returns reg1 (value) - cci_scripts.py
			(assign, ":payment", reg1),
			(str_store_string, s11, "@ to purchase the {s23}"),
			(call_script, "script_oath_pay_player_because_s11", ":payment"),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			# (call_script, "script_quest_oathbound_only_the_finest", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(str_clear, s65),
				(str_store_string, s65, "@You need to have the requested item commissioned."),
				(assign, ":note_slot", 3),
			(else_try),
				(eq, ":quest_stage", OATH_QUEST_STAGE_GOAL_MET),
				(str_store_troop_name, s21, "$oathbound_master"),
				(str_store_string, s65, "@You have obtained the requested item.  Now just bring it back to {s21}."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			(display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			(try_begin), # Remove the item.
				(quest_get_slot, ":item_no", ":quest_no", slot_quest_target_amount),
				(quest_get_slot, ":imod", ":quest_no", slot_quest_temp_slot),
				(call_script, "script_cf_oath_player_has_item_with_modifier", ":item_no", ":imod"), # Returns reg1 (inventory slot item is in)
				(troop_set_inventory_slot, "trp_player", reg1, -1),
				(troop_set_inventory_slot_modifier, "trp_player", reg1, imod_plain),
				(str_store_troop_name, s21, "$oathbound_master"),
				(call_script, "script_cci_describe_imod_to_s1", ":imod", 0), # cci_scripts.py
				(str_store_item_name, s22, ":item_no"),
				(display_message, "@You hand the {s1} {s22} over to {s21}.", gpu_green),
			(try_end),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 8),
			(call_script, "script_oath_change_oathbound_reputation", 1),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 4, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(set_show_messages, 0),
			(fail_quest, ":quest_no"),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -24),
			(call_script, "script_oath_change_oathbound_reputation", -3),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -12, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	

##################################
### QUEST #10 - MAKE YOUR MARK ###
##################################
# script_quest_oathbound_make_your_mark
# PURPOSE: Handles all quest specific actions for quest "qst_oath_make_your_mark".
# EXAMPLE: (call_script, "script_quest_oathbound_make_your_mark", FUNCTION),
("quest_oathbound_make_your_mark",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_make_your_mark"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_10"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_make_your_mark"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					15),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			5),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	5),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					20), # Requested number.
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,   						0), # Progress towards goal.
			(quest_set_slot, ":quest_no", slot_quest_object_state,                      0), # We'll track our total bonus with this.
			
			# Get our requested recruit type.
			(store_troop_faction, ":faction_no", "$oathbound_master"),
			(faction_get_slot, ":troops_begin", ":faction_no", slot_faction_troops_begin),
			(faction_get_slot, ":troops_end", ":faction_no", slot_faction_troops_end),
			(assign, ":troop_target", -1),
			(try_for_range, ":cycle", 0, 3),
				(eq, ":troop_target", -1),
				(try_for_range, ":troop_no", ":troops_begin", ":troops_end"),
					(troop_get_slot, ":tier", ":troop_no", slot_troop_tier),
					(is_between, ":tier", 2, 4),
					(store_random_in_range, ":roll", 0, 100),
					(lt, ":roll", 40),
					
					(assign, ":troop_target", ":troop_no"),
				(try_end),
				(assign, reg1, ":cycle"), # So the compiler doesn't complain about it.
			(try_end),
			(try_begin),	
				(neg|is_between, ":troop_target", ":troops_begin", ":troops_end"),
				(assign, ":troop_target", ":troops_begin"),
			(try_end),
			(quest_set_slot, ":quest_no", slot_quest_object_troop, ":troop_target"),  # Troop type.
			# Setup our quest description.
			(str_store_troop_name_plural, s22, ":troop_target"),
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(quest_get_slot, reg21, ":quest_no", slot_quest_target_amount),
			(str_store_string, s61, "@{s21} tasked you with hiring {reg21} {s22} to fill out the ranks.  Only fresh recruits were requested, but you were promised a bonus for any that have gained extra experience along the way."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Pay the player a reasonable sum to the new troops + 10%.
			(quest_get_slot, ":quantity", ":quest_no", slot_quest_target_amount),
			(troop_get_slot, ":cost_per_troop", ":troop_target", slot_troop_purchase_cost),
			(store_mul, ":payment", ":quantity", ":cost_per_troop"),
			(store_mul, ":extra", ":payment", 10),
			(val_div, ":extra", 100),
			(val_add, ":payment", ":extra"),
			(assign, reg21, ":quantity"),
			(str_store_troop_name_plural, s23, ":troop_target"),
			(str_store_string, s11, "@ to hire {reg21} {s23}"),
			(call_script, "script_oath_pay_player_because_s11", ":payment"),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			(call_script, "script_quest_oathbound_make_your_mark", OATH_QUEST_UPDATE),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(quest_get_slot, reg21, ":quest_no", slot_quest_temp_slot),
				(quest_get_slot, reg22, ":quest_no", slot_quest_target_amount),
				(quest_get_slot, ":troop_type", ":quest_no", slot_quest_object_troop),
				(str_store_troop_name_plural, s21, ":troop_type"),
				(str_store_string, s65, "@You have brought {reg21} of the {reg22} {s21} requested."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			#(display_message, "str_quest_log_updated"), # Very spammy on this quest if left.
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			# Bonus for experienced troops.
			(assign, ":rating", 6),
			(assign, ":relation", 1),
			(try_begin),
				(quest_slot_ge, ":quest_no", slot_quest_object_state, 1),
				(quest_get_slot, ":bonus", ":quest_no", slot_quest_object_state),
				(val_div, ":bonus", 5),
				(val_add, ":rating", ":bonus"),
				(val_add, ":relation", ":bonus"),
			(try_end),
			(call_script, "script_oath_change_oathbound_rating", ":rating"),
			(call_script, "script_oath_change_oathbound_reputation", 3),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", ":relation", 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -18),
			(call_script, "script_oath_change_oathbound_reputation", -9),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			(quest_get_slot, ":troop_base", ":quest_no", slot_quest_object_troop),
			(quest_get_slot, ":goal", ":quest_no", slot_quest_target_amount), 
			(quest_get_slot, ":progress", ":quest_no", slot_quest_temp_slot),
			(store_sub, ":goal_adjusted", ":goal", ":progress"), # Check for previous progress credit.
			(assign, ":orig_progress", ":progress"), # To check if we actually added any for updating the quest log.
			(assign, ":bonus", 0),
			# Turn in each of the requested troop type that we have as well as any upgraded versions.
			(try_begin),
				(party_count_companions_of_type, ":count", "p_main_party", ":troop_base"),
				(ge, ":count", 1),
				(val_min, ":count", ":goal_adjusted"), # Don't take more than the requested amount.
				(party_remove_members, "p_main_party", ":troop_base", ":count"),
				(str_store_troop_name_by_count, s21, ":troop_base", ":count"),
				(assign, reg21, ":count"),
				(display_message, "@You turn in {reg21} {s21}.", gpu_green),
				(val_sub, ":goal_adjusted", ":count"),
				(val_add, ":progress", ":count"),
				(quest_set_slot, ":quest_no", slot_quest_temp_slot, ":progress"),
			(try_end),
			# Check for upgrades
			(assign, ":troop_prev", ":troop_base"),
			(try_for_range, ":cycle", 1, 7),
				(ge, ":troop_prev", 1),
				(troop_get_upgrade_troop, ":troop_next", ":troop_prev", 0), #upgrade_path can be: 0 = get first node, 1 = get second node (returns -1 if not available)
				(assign, ":troop_prev", ":troop_next"),
				(ge, ":troop_next", 1),
				(party_count_companions_of_type, ":count", "p_main_party", ":troop_next"),
				(ge, ":count", 1),
				(val_min, ":count", ":goal_adjusted"), # Don't take more than the requested amount.
				(party_remove_members, "p_main_party", ":troop_next", ":count"),
				(store_mul, ":bonus_add", ":count", ":cycle"),
				(val_add, ":bonus", ":bonus_add"),
				(str_store_troop_name_by_count, s21, ":troop_next", ":count"),
				(assign, reg21, ":count"),
				(assign, reg22, ":bonus"),
				(display_message, "@You turn in {reg21} {s21}.", gpu_green),
				(val_sub, ":goal_adjusted", ":count"),
				(val_add, ":progress", ":count"),
				(quest_set_slot, ":quest_no", slot_quest_temp_slot, ":progress"),
			(try_end),
			# Check if we are giving a bonus.
			(try_begin),
				(ge, ":bonus", 1),
				(troop_get_slot, ":cost_per_troop", ":troop_base", slot_troop_purchase_cost),
				(store_mul, ":cash_per_bonus", ":cost_per_troop", 25),
				(val_div, ":cash_per_bonus", 100),
				(store_mul, ":payment", ":cash_per_bonus", ":bonus"),
				(str_store_string, s11, "@ as a reward for bringing experienced troops"),
				(call_script, "script_oath_pay_player_because_s11", ":payment"),
				(call_script, "script_oath_quest_change_slot", ":quest_no", slot_quest_object_state, ":bonus"),
			(try_end),
			# Check if we should update our quest log.
			(try_begin),
				(quest_slot_ge, ":quest_no", slot_quest_temp_slot, ":orig_progress"),
				(call_script, "script_quest_oathbound_make_your_mark", OATH_QUEST_UPDATE),
			(try_end),
			# Check if we have enough to complete the quest.
			(try_begin),
				(quest_get_slot, ":progress", ":quest_no", slot_quest_temp_slot),
				(quest_slot_ge, ":quest_no", slot_quest_temp_slot, ":goal"),
				(call_script, "script_quest_oathbound_make_your_mark", OATH_QUEST_SUCCEED),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
##############################
### QUEST #13 - FRESH MEAT ###
##############################
# script_quest_oathbound_fresh_meat
# PURPOSE: Handles all quest specific actions for quest "qst_oath_fresh_meat".
# EXAMPLE: (call_script, "script_quest_oathbound_fresh_meat", FUNCTION),
("quest_oathbound_fresh_meat",
  [
		(store_script_param, ":function", 1),
		(assign, ":quest_no",    "qst_oath_fresh_meat"),
		# Get specific string data.
		(assign, ":quest_title", "str_oath_quest_title_13"),
		(str_store_string, s41, ":quest_title"),
		
		(try_begin),
			##### QUEST START #####
			(eq, ":function", OATH_QUEST_BEGIN),
			# Setup quest parameters.
			(call_script, "script_common_quest_change_state", ":quest_no", OATH_QUEST_STAGE_BEGUN),
			(quest_set_slot, ":quest_no", slot_quest_unique_script,						"script_quest_oathbound_fresh_meat"),
			(quest_set_slot, ":quest_no", slot_quest_giver_center,						-1),			# Unnecessary.
			(quest_set_slot, ":quest_no", slot_quest_target_center,						-1),
			(quest_set_slot, ":quest_no", slot_quest_expiration_days,					0),			# No expiration.
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period,			4),
			(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days,	4),
			(quest_set_slot, ":quest_no", slot_quest_comment_made,						0),
			(quest_set_slot, ":quest_no", slot_quest_unique_name,						":quest_title"),
			(quest_set_slot, ":quest_no", slot_quest_target_amount,   					5), # This tracks how many sessions we need to hold total.
			(quest_set_slot, ":quest_no", slot_quest_temp_slot,							0),	# This tracks how many sessions we have held.
			(quest_set_slot, ":quest_no", slot_quest_object_state,						0),	# This is tracking if we win/lose a match.
			(quest_set_slot, ":quest_no", slot_quest_target_state,						0),	# This is tracking if we were in a match and it didn't get resolved.
			
			(str_store_troop_name_link, s21, "$oathbound_master"),
			(quest_get_slot, reg21, ":quest_no", slot_quest_target_amount),
			(str_store_string, s61, "@{s21} has tasked you with training several of the new recruits in the art of swordsmanship when the army stops for the night.  This will require having several training sessions with the troops when you are fit to do so."),
			# Clear out any old quest notes.
			(str_clear, s1),
			(add_quest_note_from_sreg, ":quest_no", 3, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 4, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 5, s1, 0),
			(add_quest_note_from_sreg, ":quest_no", 6, s1, 0),
			# Activate the quest.
			(setup_quest_text, ":quest_no"),
			(call_script, "script_oath_start_quest", ":quest_no"),
			
		(else_try),
			##### QUEST UPDATE #####
			(eq, ":function", OATH_QUEST_UPDATE),
			# Get the date stamp.
			(store_current_hours, ":cur_hours"),
			(str_store_date, s64, ":cur_hours"),
			(str_store_string, s64, "@[{s64}]: "),
			# Update quest notes as required.
			(quest_get_slot, ":quest_stage", ":quest_no", slot_quest_current_state),
			(try_begin),
				(eq, ":quest_stage", OATH_QUEST_STAGE_BEGUN),
				(quest_get_slot, reg21, ":quest_no", slot_quest_temp_slot),
				(quest_get_slot, reg22, ":quest_no", slot_quest_target_amount),
				(str_store_string, s65, "@You have held {reg21} of the {reg22} training sessions needed."),
				(assign, ":note_slot", 3),
			(else_try),
				# Default error on failure to update note.
				(display_message, "str_oath_quest_s41_update_note_error", qp_error_color),
			(try_end),
			# Update quest note.
			(str_store_string, s64, "@{s64} {s65}"),
			(add_quest_note_from_sreg, ":quest_no", ":note_slot", s64, 0),
			(display_message, "str_quest_log_updated"),
		
		(else_try),
			##### QUEST SUCCEED #####
			(eq, ":function", OATH_QUEST_SUCCEED),
			# Complete the quest.
			(succeed_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", 6),
			(call_script, "script_oath_change_oathbound_reputation", 1),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", 1, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_COMPLETION, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST FAIL #####
			(eq, ":function", OATH_QUEST_FAIL),
			(fail_quest, ":quest_no"),
			(set_show_messages, 0),
			(complete_quest, ":quest_no"),
			(set_show_messages, 1),
			(call_script, "script_oath_change_oathbound_rating", -18),
			(call_script, "script_oath_change_oathbound_reputation", -3),
			(call_script, "script_change_player_relation_with_troop", "$oathbound_master", -3, 0),
			(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_QUEST_FAILURE, ":quest_no"), ## OATHBOUND EVENT LOG
			
		(else_try),
			##### QUEST CANCEL #####
			(eq, ":function", OATH_QUEST_CANCEL),
			(cancel_quest, ":quest_no"),
			(display_message, "@Quest '{s41}' was cancelled without consequence."),
			
		(else_try),
			##### QUEST VICTORY CONDITION #####
			(eq, ":function", OATH_QUEST_VICTORY_CONDITION),
			(try_begin),
				(quest_get_slot, ":goal", ":quest_no", slot_quest_target_amount), 
				(quest_slot_ge, ":quest_no", slot_quest_temp_slot, ":goal"),
				(call_script, "script_quest_oathbound_fresh_meat", OATH_QUEST_SUCCEED),
			(try_end),
			
		(else_try),
			##### QUEST PREREQUISITES #####
			(eq, ":function", OATH_QUEST_PREREQUISITES),
			(assign, reg1, 1),
			
		(else_try),
			(assign, reg31, ":function"),
			(display_message, "str_oath_quest_s41_update_error", qp_error_color),
		(try_end),
	]),
	
	
###########################################################################################################################
#####                                           OATHBOUND HUB SWITCHING                                               #####
###########################################################################################################################

# script_oath_create_mode_switching_buttons
# PURPOSE: These button declarations are common to each presentation mode so this prevents needing to recreate this code for each window.
("oath_create_mode_switching_buttons",
    [
		### COMMON ELEMENTS ###
		(assign, "$gpu_storage", PRES_OBJECTS),
		(assign, "$gpu_data",    PRES_OBJECTS),
		
		(call_script, "script_gpu_draw_line", 850, 2, 73, 650, gpu_gray), # - Footer
		
		# Setup an initial false value for objects so if they don't get loaded they aren't 0's.
		(try_for_range, ":slot_no", 0, 50),
			(store_add, ":value", ":slot_no", 1234),
			(troop_set_slot, PRES_OBJECTS, ":slot_no", ":value"),
		(try_end),
		
		## COMMON PRESENTATION HEADER
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		(str_store_troop_name, s21, "trp_player"),
		(str_store_string, s21, "@{s2}{s21}'s Contract Information"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", 500, 665, oath_obj_main_title, gpu_center), # 680
		(call_script, "script_gpu_resize_object", oath_obj_main_title, 150),
		
		(call_script, "script_gpu_create_text_label", "str_oath_s21", 500, 665, oath_obj_main_title2, gpu_center), # 680
		(call_script, "script_gpu_resize_object", oath_obj_main_title2, 150),
		
		## CONTAINERS ##
		(call_script, "script_gpu_container_heading", 50, 80, 175, 505, oath_obj_container_left_buttons),
			
			## BUTTONS ##
			(assign, ":x_buttons", 0), # 90 
			(assign, ":y_button_step", 55),
			(assign, ":pos_y", 420),
			
			(str_store_string, s21, "@Contract Info "),
			(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_contract_info), ### CONTRACT INFO ###
			
			### BUTTON : COMMANDER AUDIENCE ###
			(try_begin),
				(party_get_battle_opponent, ":commander_opponent", "$oathbound_party"),
				(lt, ":commander_opponent", 0),
				(str_store_troop_name, s21, "$oathbound_master"),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Audience "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_commander_audience),
			(try_end),
			
			### BUTTON : JOIN BATTLE ###
			(try_begin),
				(party_get_battle_opponent, ":commander_opponent", "$oathbound_party"),
				(gt, ":commander_opponent", 0),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Join Battle! "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_join_battle),
			(try_end),
			
			### BUTTON : ENTER LOCATION ###
			(try_begin),
				(party_get_attached_to, reg5, "$oathbound_party"),
				(gt, reg5, 0),
				(this_or_next|party_slot_eq, reg5, slot_party_type, spt_town),
				(party_slot_eq, reg5, slot_party_type, spt_castle),
				# (str_store_party_name, s21, reg5),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Enter Location "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_enter_location), 
			(try_end),
			
			### BUTTON : QUEST SELECTOR ###
			(try_begin),
				(party_get_battle_opponent, ":commander_opponent", "$oathbound_party"),
				(neg|gt, ":commander_opponent", 0),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Available Tasks "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_quest_selector),
			(try_end),
			
			(val_sub, ":pos_y", ":y_button_step"),
			(str_store_string, s21, "@Companions "),
			(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_manage_companions), ### BUTTON : MANAGE COMPANIONS ###
			
			# (val_sub, ":pos_y", ":y_button_step"),
			# (str_store_string, s21, "@Reference Guide "),
			# (call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_reference), ### BUTTON : REFERENCE GUIDE ###
			
			(val_sub, ":pos_y", ":y_button_step"),
			(str_store_string, s21, "@Pay Information "),
			(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_pay_info), ### BUTTON : PAY INFORMATION ###
			
			### BUTTON : EVENT LOG ### (WSE Dependent)
			(try_begin),
				(neg|is_vanilla_warband),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Event Log "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_event_log), 
			(try_end),
			
			### BUTTON : DEBUGGING OPTIONS ###
			(try_begin),
				(ge, "$oathbound_debugging", 1),
				(val_sub, ":pos_y", ":y_button_step"),
				(str_store_string, s21, "@Debugging "),
				(call_script, "script_gpu_create_button", "str_oath_s21", ":x_buttons", ":pos_y", oath_obj_button_debugging),
			(try_end),
			
		(set_container_overlay, -1),
		
		### BUTTON : DESERT! ###
		(try_begin),
			(call_script, "script_gpu_create_mesh", "mesh_button_up", 775, 40, 710, 500),
			(str_store_string, s21, "@Abandon Army!"),
			(call_script, "script_gpu_create_button", "str_oath_s21", 785, 45, oath_obj_button_desert),
		(try_end),
		
		### BUTTON : RETURN TO MAP ###
		(try_begin),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(call_script, "script_gpu_create_mesh", "mesh_button_up", 410, 40, 720, 500),
			(str_store_string, s21, "@Return to Map"),
			(call_script, "script_gpu_create_button", "str_oath_s21", 420, 45, oath_obj_button_return_to_map),
			# "Or Hit Escape" Label
			(str_store_string, s21, "@Or Press Escape"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", 500, 33, oath_obj_label_hit_escape, gpu_center),
			(call_script, "script_gpu_resize_object", oath_obj_label_hit_escape, 50),
		(try_end),
	]),
	
# script_oath_handle_mode_switching_buttons
# PURPOSE: These button declarations are common to each presentation mode so this prevents needing to recreate the code to handle their functionality for each window.
("oath_handle_mode_switching_buttons",
    [
		(store_script_param, ":object", 1),
		(store_script_param, ":value", 2),
		(assign, reg1, ":value"), # So it won't be whined about.
		
		### COMMON ELEMENTS ###
		(try_begin), ####### BUTTON : RETURN TO MAP #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_return_to_map, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : CONTRACT INFO #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_contract_info, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_CONTRACT_INFO),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : COMMANDER AUDIENCE #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_commander_audience, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_COMMANDER_AUDIENCE),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : DEBUGGING #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_debugging, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_DEBUGGING),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : JOIN BATTLE #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_join_battle, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_JOIN_BATTLE),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : ENTER CITY #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_enter_location, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_ENTER_LOCATION),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : MANAGE COMPANIONS #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_manage_companions, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_MANAGE_COMPANIONS),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : OATHBOUND REFERENCE #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_reference, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_OATHBOUND_REFERENCE),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : PAY INFORMATION #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_pay_info, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_PAY_INFORMATION),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : QUEST SELECTOR #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_quest_selector, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_QUEST_SELECTION),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : DESERT! #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_desert, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_DESERT),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(else_try), ####### BUTTON : EVENT LOG #######
			(troop_slot_eq, PRES_OBJECTS, oath_obj_button_event_log, ":object"),
			(assign, "$oathbound_mode", OATH_MODE_EVENT_LOG),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
			
		(try_end),
	]),
	
# script_cf_oath_allow_return_to_map
# PURPOSE: Common code for preventing the "Return to Map" button from functioning in the Oathbound Interface Hub.
# EXAMPLE: (call_script, "script_cf_oath_allow_return_to_map"),
("cf_oath_allow_return_to_map",
    [
		(party_get_battle_opponent, ":commander_opponent", "$oathbound_party"),
		(this_or_next|lt, ":commander_opponent", 0),
		(troop_is_wounded, "trp_player"),
	]),
	
# script_oath_system_initialize
# PURPOSE: Sets up global variables for the Oathbound system.
# EXAMPLE: (call_script, "script_oath_system_initialize"),
("oath_system_initialize",
    [
		(assign, "$oathbound_pause_at_fiefs", 1),	# Sets mod option for pausing.
		(assign, "$oathbound_events", 0),			# Sets up an initial position for the Oathbound Event Log.
		(assign, "$oathbound_reputation", 0),		# Sets up your initial global reputation.
		
		## Delete our event log at the start of a new game.
		(dict_delete_file, OATHBOUND_EVENT_LOG),
		
		## Initialize faction slots.
		(try_for_range, ":faction_no", kingdoms_begin, kingdoms_end),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_rank, 0),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_rating, 0),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_reputation, 0),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_betrayals, 0),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_renewals, 0),
			(faction_set_slot, ":faction_no", slot_faction_oathbound_high_rank, 0),
		(try_end),
	]),
]

from util_wrappers import *
from util_scripts import *

scripts_directives = [
	# # HOOK: Inserts a script that tracks village entry.
	# # [SD_OP_BLOCK_INSERT, "update_center_recon_notes", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (try_end), 0, 
		# # [(call_script, "script_qp4_arrive_in_village", ":center_no"),], 1],
		
	# # HOOK: Insert failure condition checks for quests that need them.
	# [SD_OP_BLOCK_INSERT, "abort_quest", D_SEARCH_FROM_TOP | D_SEARCH_SCRIPTLINE | D_INSERT_BEFORE, (try_begin), 0, 
		# [(call_script, "script_qp3_check_failure_conditions", ":quest_no"),], 1],
		
	# # HOOK: Inserts a script that forces hired mercenary companies to join the player in battle.
	# [SD_OP_BLOCK_INSERT, "let_nearby_parties_join_current_battle", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_BEFORE, (try_end), 0, 
		# [
			# (assign, reg41, ":party_no"),
			# (call_script, "script_qp3_quest_mercenary_function", mercs_join_combat),
		# ], 1],
		
	# # HOOK: Inserts a script that tracks village entry.
	# [SD_OP_BLOCK_INSERT, "enter_court", D_SEARCH_FROM_TOP | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (assign, ":cur_pos", 16), 0, 
		# [
			# (call_script, "script_qp3_enter_court", ":center_no", ":cur_pos"),
			# (assign, ":cur_pos", reg1),
		# ], 1],
		
	# # HOOK: Inserts script into game_event_battle_end to check on types of enemies killed.
	# [SD_OP_BLOCK_INSERT, "event_player_defeated_enemy_party", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (try_end), 0, 
		# [(call_script, "script_qp3_event_player_defeated_enemy_party"),], 1],
		
	# HOOK: Inserts the initializing scripts in game start as needed.
	[SD_OP_BLOCK_INSERT, "game_start", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (try_end), 0, 
		[(call_script, "script_oath_system_initialize"),], 1],
		
	# # HOOK: Inserts the names of quests I do not want humanitarian companions to object to failing.
	# [SD_OP_BLOCK_INSERT, "abort_quest", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_BEFORE, (call_script, "script_objectionable_action", tmt_honest, "str_fail_quest"), 0, 
		# [(call_script, "script_cf_qp3_ignore_failures", ":quest_no"),], 1],
		
	# HOOK: When a quest fails due to expiration this makes sure the quest failure script runs for that quest.
	[SD_OP_BLOCK_INSERT, "abort_quest", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_BEFORE, (call_script, "script_end_quest", ":quest_no"), 0, 
		[
			## WINDYPLAINS+ ## - Oathbound - Quest failure
			(try_begin),
				(is_between, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(quest_get_slot, ":unique_script", ":quest_no", slot_quest_unique_script),
				(call_script, ":unique_script", OATH_QUEST_FAIL),
			(try_end),
			## WINDYPLAINS- ##
		], 1],
		
	# # HOOK: Captures when a player enters town.
	# [SD_OP_BLOCK_INSERT, "game_event_party_encounter", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (party_slot_eq, "$g_encountered_party", slot_party_type, spt_town), 0, 
		# [(call_script, "script_qp3_track_town_entry", "$g_encountered_party"),], 1],
		
	# # HOOK: Prevent spawned bandits from joining nearby battles.
	# # [SD_OP_BLOCK_INSERT, "let_nearby_parties_join_current_battle", D_SEARCH_FROM_BOTTOM | D_SEARCH_SCRIPTLINE | D_INSERT_AFTER, (neg|quest_slot_eq, "qst_troublesome_bandits", slot_quest_target_party, ":party_no"), 0, 
		# # [(call_script, "script_cf_qp2_parties_that_wont_join_battles", ":party_no"),], 1],

] # scripts_rename
                
def modmerge_scripts(orig_scripts):
	# process script directives first
	process_script_directives(orig_scripts, scripts_directives)
	# add remaining scripts
	add_scripts(orig_scripts, scripts, True)
	
# Used by modmerger framework version >= 200 to merge stuff
# This function will be looked for and called by modmerger if this mod is active
# Do not rename the function, though you can insert your own merging calls where indicated
def modmerge(var_set):
    try:
        var_name_1 = "scripts"
        orig_scripts = var_set[var_name_1]
    
        
		# START do your own stuff to do merging
		
        modmerge_scripts(orig_scripts)

		# END do your own stuff
        
    except KeyError:
        errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
        raise ValueError(errstring)