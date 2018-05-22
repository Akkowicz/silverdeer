# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_common import *
from header_dialogs import *
from header_operations import *
from header_parties import *
from header_item_modifiers import *
from header_skills import *
from header_triggers import *
from ID_troops import *
from ID_party_templates import *
from module_constants import *

initiation_dialogs	= [   
	## SEPARATED -> REJOINING CATCH
	[anyone ,"start", 
		[
			(eq, "$oathbound_master", "$g_talk_troop"),
			(eq, "$oathbound_status", OATHBOUND_STATUS_SEPARATED),
			(troop_slot_ge, "$oathbound_master", slot_troop_leaded_party, 1), # Make sure he has a party to rejoin so this doesn't trigger when you rescue him.
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "Welcome back, {s2}{playername}!  After we split up I was not sure I would see you {reg2?and your men :}again.  It is good that I was wrong.", "lord_talk", []],
	
	## DESERTER -> REJOINING CATCH
	[anyone,"start", 
		[
			(eq, "$oathbound_master", "$g_talk_troop"),
			(eq, "$oathbound_status", OATHBOUND_STATUS_DESERTER),
			(troop_slot_ge, "$oathbound_master", slot_troop_leaded_party, 1),
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "So your back, {s2}{playername}?  Rumor has it you {reg2?and your men :}might have run off on me without finishing the time I paid you for.  It is good that such rumors were false.  It is an unfortunate necessity that we hang deserters in my army.", "lord_talk",
		[]],				
	
]

lord_talk_addon	= [
	## REQUEST CONTRACT BEGIN
	[anyone|plyr,"lord_talk", [
		(eq, "$oathbound_status", OATHBOUND_STATUS_NOT_HIRED),
		(ge, "$g_talk_troop_faction_relation", 0),
        # (neq, "$players_kingdom", "$g_talk_troop_faction"),
        # (eq, "$players_kingdom", 0),
		(neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(troop_slot_ge, "$g_talk_troop", slot_troop_leaded_party, 1),
		(troop_get_type, reg1, "$g_talk_troop"),
     ],"My {reg1?Lady:Lord}, I would like to enlist in your army.", "oath_request_contract",[]],
	
	## REQUEST RETIREMENT
    [anyone|plyr,"lord_talk", [
        (ge, "$oathbound_debugging", 1),
		(eq, "$g_talk_troop", "$oathbound_master"),
		(this_or_next|eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
        (eq, "$oathbound_status", OATHBOUND_STATUS_AWAY),
        (ge, "$g_talk_troop_faction_relation", 0),
        # (neq, "$players_kingdom", "$g_talk_troop_faction"),
        # (eq, "$players_kingdom", 0),
		(neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0), 
     ], "(DEBUG) I would like to retire from service.", "oath_request_retirement",[]],
	
	## REQUEST A LEAVE OF DUTY
    [anyone|plyr,"lord_talk",[
		(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
        (eq, "$g_talk_troop", "$oathbound_master"),
		(ge, "$oathbound_time_since_leave", OATHBOUND_MIN_TIME_BETWEEN_LEAVE),
		(call_script, "script_cf_oath_player_meets_minimum_rank_for_quest", "qst_oath_leave"),
		(neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0), 
		(troop_get_type, reg1, "$oathbound_master"),
     ], "My {reg1?Lady:Lord}, I would like to request some personal leave.", "oath_request_leave",[]],  
		
	## REQUEST TO EXIT THE PARTY ON A MISSION
    [anyone|plyr,"lord_talk",[
		(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
        (eq, "$g_talk_troop", "$oathbound_master"),
		(neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(call_script, "script_cf_oath_mission_is_active"),
		(troop_get_type, reg1, "$oathbound_master"),
     ], "My {reg1?Lady:Lord}, with your leave I have been given work that requires my leaving the our camp.", "oath_request_go_on_mission",[]],  
		
	## REQUEST TO REJOIN THE PARTY
	[anyone|plyr,"lord_talk",[
		(eq, "$g_talk_troop", "$oathbound_master"),
		(this_or_next|eq, "$oathbound_status", OATHBOUND_STATUS_AWAY),
        (this_or_next|eq, "$oathbound_status", OATHBOUND_STATUS_SEPARATED),
        (eq, "$oathbound_status", OATHBOUND_STATUS_DESERTER),
        # (neq, "$players_kingdom", "$g_talk_troop_faction"),
        # (eq, "$players_kingdom", 0),
		(neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0), 
		(troop_get_type, reg1, "$oathbound_master"),
    ], "My {reg1?Lady:Lord}, I am ready to return to your command.", "oath_ask_to_rejoin",[]],
	 
	## OATHBOUND QUEST+: THE SEALED LETTER (Quest #6)
	# Delivering the letter.
	[anyone|plyr,"lord_talk",[
		(check_quest_active, "qst_oath_sealed_letter"),
		(quest_slot_eq, "qst_oath_sealed_letter", slot_quest_object_troop, "$g_talk_troop"),
		(quest_slot_eq, "qst_oath_sealed_letter", slot_quest_current_state, OATH_SEALED_LETTER_BEGUN),
        (neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(troop_get_type, reg1, "$g_talk_troop"),
		(str_store_troop_name, s21, "$oathbound_master"),
    ], "My {reg1?Lady:Lord}, I been sent to deliver this message to you by {s21}.", "oath_sealed_letter_delivered",[]],
	
	# Returning to turn in the quest with $oathbound_master.
	[anyone|plyr,"lord_talk",[
		(check_quest_active, "qst_oath_sealed_letter"),
		(eq, "$g_talk_troop", "$oathbound_master"),
		(quest_slot_eq, "qst_oath_sealed_letter", slot_quest_current_state, OATH_SEALED_LETTER_DELIVERED),
        (neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(troop_get_type, reg1, "$oathbound_master"),
		(quest_get_slot, ":troop_no", "qst_oath_sealed_letter", slot_quest_object_troop),
		(str_store_troop_name, s21, ":troop_no"),
    ], "My {reg1?Lady:Lord}, I returned with {s21}'s message.", "oath_sealed_letter_turn_in",[]],
	## OATHBOUND QUEST-: THE SEALED LETTER (Quest #6)
	
	## OATHBOUND QUEST+: SCOUTING AHEAD (Quest #8)
	# Returning to turn in the quest with $oathbound_master.
	[anyone|plyr,"lord_talk",[
		(check_quest_active, "qst_oath_scouting_ahead"),
		(eq, "$g_talk_troop", "$oathbound_master"),
		(quest_slot_eq, "qst_oath_scouting_ahead", slot_quest_current_state, OATH_QUEST_STAGE_GOAL_MET),
        (neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(troop_get_type, reg1, "$oathbound_master"),
    ], "My {reg1?Lady:Lord}, I have returned with my scouting report.", "oath_scouting_ahead_turn_in",[]],
	## OATHBOUND QUEST-: SCOUTING AHEAD (Quest #8)
	
	## OATHBOUND QUEST+: ONLY THE FINEST (Quest #9)
	# Returning to turn in the quest with $oathbound_master.
	[anyone|plyr,"lord_talk",[
		(check_quest_active, "qst_oath_only_the_finest"),
		(eq, "$g_talk_troop", "$oathbound_master"),
		(quest_slot_eq, "qst_oath_only_the_finest", slot_quest_current_state, OATH_QUEST_STAGE_GOAL_MET),
        (neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		(quest_get_slot, ":item_no", "qst_oath_only_the_finest", slot_quest_target_amount),
		(quest_get_slot, ":imod", "qst_oath_only_the_finest", slot_quest_temp_slot),
		(call_script, "script_cf_oath_player_has_item_with_modifier", ":item_no", ":imod"), # Returns reg1 (inventory slot item is in)
		(troop_set_inventory_slot, "trp_player", reg1, -1),
		(troop_set_inventory_slot_modifier, "trp_player", reg1, imod_plain),
		(call_script, "script_cci_describe_imod_to_s1", ":imod", 0), # cci_scripts.py
		(str_store_item_name, s22, ":item_no"),
		(str_store_string, s23, "@{s1} {s22}"),
		(troop_get_type, reg1, "$oathbound_master"),
    ], "My {reg1?Lady:Lord}, I have returned with your {s23}.", "oath_only_the_finest_turn_in",[]],
	## OATHBOUND QUEST-: ONLY THE FINEST (Quest #9)
	
	## OATHBOUND QUEST+: MAKE YOUR MARK (Quest #10)
	# Returning to turn in the quest with $oathbound_master.
	[anyone|plyr,"lord_talk",[
		(check_quest_active, "qst_oath_make_your_mark"),
		(eq, "$g_talk_troop", "$oathbound_master"),
		(quest_slot_eq, "qst_oath_make_your_mark", slot_quest_current_state, OATH_QUEST_STAGE_BEGUN),
        (neg|troop_slot_ge, "$g_talk_troop", slot_troop_prisoner_of_party, 0),
		# Make sure we have any of the requested troop types.
		(quest_get_slot, ":troop_base", "qst_oath_make_your_mark", slot_quest_object_troop),
		(party_count_companions_of_type, ":count", "p_main_party", ":troop_base"),
		# Check for upgrades
		(assign, ":troop_prev", ":troop_base"),
		(try_for_range, ":cycle", 1, 7),
			(ge, ":troop_prev", 1),
			(troop_get_upgrade_troop, ":troop_next", ":troop_prev", 0), #upgrade_path can be: 0 = get first node, 1 = get second node (returns -1 if not available)
			(assign, ":troop_prev", ":troop_next"),
			(ge, ":troop_next", 1),
			(party_count_companions_of_type, reg1, "p_main_party", ":troop_next"),
			(val_add, ":count", reg1),
		(try_end),
		(ge, ":count", 1),
		# Get how many we should at most turn in.
		(quest_get_slot, ":goal", "qst_oath_make_your_mark", slot_quest_target_amount), 
		(quest_get_slot, ":progress", "qst_oath_make_your_mark", slot_quest_temp_slot),
		(store_sub, ":goal_adjusted", ":goal", ":progress"), # Check for previous progress credit.
		(val_min, ":count", ":goal_adjusted"),
		(assign, reg21, ":count"),
		(str_store_troop_name_by_count, s23, ":troop_base"),
		(troop_get_type, reg1, "$oathbound_master"),
    ], "My {reg1?Lady:Lord}, I have returned with {reg21} {s23}.", "oath_make_your_mark_turn_in",
	[(call_script, "script_quest_oathbound_make_your_mark", OATH_QUEST_VICTORY_CONDITION),]],
	## OATHBOUND QUEST-: MAKE YOUR MARK (Quest #10)
	
]

dialogs	= [
	## OATHBOUND FUNCTION+: BEGINNING A CONTRACT.
	## Had some rank already.
	[anyone,"oath_request_contract", 
		[
			(ge, "$g_talk_troop_relation", 0),		
			(store_troop_faction, ":faction_no", "$g_talk_troop"),
			(faction_get_slot, ":rank", ":faction_no", slot_faction_oathbound_rank),
			(ge, ":rank", OATHBOUND_RANK_MILITIA),
			(faction_slot_ge, ":faction_no", slot_faction_oathbound_reputation, OATHBOUND_MIN_REPUTATION_ALLOWED),
			(ge, "$oathbound_reputation", OATHBOUND_MIN_REPUTATION_ALLOWED),
			(call_script, "script_oath_calculate_weekly_pay", "$g_talk_troop_faction"), # Returns reg1 (pay)
			(assign, reg23, reg1),
			(call_script, "script_oath_describe_oathbound_rank", ":rank"), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "My men inform me that you have served our cause before attaining the rank of {s1}.  You {reg2?and your men :}are welcome to enter my service.  I grant you the rank of {s1} with a weekly pay of {reg23} denars for a period of one month.", "oath_confirm_joining", []],		
	
	## Default (Yes): Green recruit.
	[anyone,"oath_request_contract", 
		[
			(ge, "$g_talk_troop_relation", 0),
			(store_troop_faction, ":faction_no", "$g_talk_troop"),
			(faction_slot_ge, ":faction_no", slot_faction_oathbound_reputation, OATHBOUND_MIN_REPUTATION_ALLOWED),
			(ge, "$oathbound_reputation", OATHBOUND_MIN_REPUTATION_ALLOWED),
			(call_script, "script_oath_calculate_weekly_pay", "$g_talk_troop_faction"), # Returns reg1 (pay)
			(assign, reg23, reg1),
			(call_script, "script_oath_describe_oathbound_rank", OATHBOUND_RANK_INITIATE), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "You {reg2?and your men :}are not known to me, but I am always in need of more swords.  You may enter my service at the rank of {s1} with a weekly pay of {reg23} denars for a period of one month.", "oath_confirm_joining", []],		
	
	## Default (No): Reputation or relation must have failed.
	[anyone,"oath_request_contract", 
		[], "I have no need for the service of you{reg2? or your men:}.", "lord_pretalk", []],		
	
	[anyone|plyr,"oath_confirm_joining", 
		[], "{reg2?My company vows:I vow} to serve you under these terms.", "close_window", 
		[
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),
			(eq, "$talk_context", tc_party_encounter),
			(assign, "$g_leave_encounter", 1),
		]],
	[anyone|plyr,"oath_confirm_joining",
		[], "That's a generous offer, but I think {reg2?we:I} will try our luck elsewhere.", "lord_pretalk",[]],
	# REJECTION - I don't like you.
    [anyone,"oath_request_contract", 
		[(lt, "$g_talk_troop_relation", 0)], "I do not trust you enough to allow you to serve for me.", "lord_pretalk",[]],
	## OATHBOUND FUNCTION-: BEGINNING A CONTRACT
	
	## OATHBOUND FUNCTION+: ENDING A CONTRACT.
	[anyone,"oath_request_retirement",
		[
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		], "Very well, {s2}{playername}.  I discharge you from my service.  May your future bring you good fortune!", "lord_pretalk",
		[
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_NOT_HIRED),
		]],
	## OATHBOUND FUNCTION-: ENDING A CONTRACT
	
	## OATHBOUND FUNCTION+: REJOINING LORD'S PARTY
	## Lord response: Status AWAY on leave.
	[anyone,"oath_ask_to_rejoin", 
		[
			(eq, "$oathbound_status", OATHBOUND_STATUS_AWAY),
			(eq, "$oathbound_leave_granted", 1),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "Welcome back, {s2}{playername}.  You {reg2?and your men :}have been missed.", "lord_pretalk",
		[(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),]],				
	
	## Lord response: Status AWAY on mission.
	[anyone,"oath_ask_to_rejoin", 
		[
			(eq, "$oathbound_status", OATHBOUND_STATUS_AWAY),
			(neq, "$oathbound_leave_granted", 1),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "You have my leave to rejoin us, {s2}{playername}.  It is good to have you {reg2?and your men :}back amongst our ranks.", "lord_pretalk",
		[
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_CONTRACTED),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		]],				
	## OATHBOUND FUNCTION-: REJOINING LORD'S PARTY
	
	## OATHBOUND FUNCTION+: REQUESTING LEAVE
	[anyone,"oath_request_leave", 
		[
			(eq, "$oathbound_exit_allowed", 1),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "A leave of duty, {s2}{playername}?  I suppose you {reg2?and your men :}have earned a little time to spend your gains.  I'll instruct my men that you are leaving our camp for a period of one month, but I'll need you back by then.", "lord_pretalk",
		[
			(assign, "$oathbound_leave_granted", 1),
			(assign, "$oathbound_time_since_leave", 0),
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_AWAY),
		]],				
	
	[anyone,"oath_request_leave", 
		[
			(neq, "$oathbound_exit_allowed", 1), # No one can leave.
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "A leave of duty, {s2}{playername}?  Right now I can't support having you {reg2?and your men :}missing from my ranks.  You will have to wait.", "lord_pretalk",
		[]],				
	## OATHBOUND FUNCTION-: REQUESTING LEAVE
	
	## OATHBOUND FUNCTION+: REQUESTING TO GO ON A MISSION
	[anyone,"oath_request_go_on_mission", 
		[
			(eq, "$oathbound_exit_allowed", 1),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "I see.  Yes, you have my leave, {s2}{playername}.  May good fortune guide your travels.", "lord_pretalk",
		[
			(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_AWAY),
		]],				
	
	[anyone,"oath_request_go_on_mission", 
		[
			(neq, "$oathbound_exit_allowed", 1), # No one can leave.
			(party_get_num_companion_stacks, reg2, "p_main_party"),
		], "Right now I can't support having you {reg2?and your men :}missing from my ranks.  You will have to wait.", "lord_pretalk",
		[]],				
	## OATHBOUND FUNCTION-: REQUESTING TO GO ON A MISSION
	
	## OATHBOUND QUEST+: THE SEALED LETTER (Quest #6)
	## Lord response to receiving the letter.
	[anyone,"oath_sealed_letter_delivered", 
		[(str_store_troop_name, s21, "$oathbound_master"),], 
		"Ah, very good.  Take this message back to {s21} with my regards.", "lord_pretalk", 
		[
			(call_script, "script_common_quest_change_state", "qst_oath_sealed_letter", OATH_SEALED_LETTER_DELIVERED),
			(call_script, "script_quest_oathbound_sealed_letter", OATH_QUEST_UPDATE),
		]],		
	
	## $oathbound_master's response to the player's return.
	[anyone,"oath_sealed_letter_turn_in", 
		[
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		], 
		"That's good, {s2}{playername}. I need men I can count upon.", "lord_pretalk", 
		[
			(call_script, "script_quest_oathbound_sealed_letter", OATH_QUEST_SUCCEED),
			(call_script, "script_oath_force_rejoin_if_no_active_missions"),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		]],		
	## OATHBOUND QUEST-: THE SEALED LETTER (Quest #6)
	
	## OATHBOUND QUEST+: SCOUTING AHEAD (Quest #8)
	## $oathbound_master's response to the player's return.
	[anyone,"oath_scouting_ahead_turn_in", 
		[
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		], 
		"That's good, {s2}{playername}. I need men I can count upon.", "lord_pretalk", 
		[
			(call_script, "script_quest_oathbound_scouting_ahead", OATH_QUEST_SUCCEED),
			(call_script, "script_oath_force_rejoin_if_no_active_missions"),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		]],		
	## OATHBOUND QUEST-: SCOUTING AHEAD (Quest #8)
	
	## OATHBOUND QUEST+: ONLY THE FINEST (Quest #9)
	## $oathbound_master's response to the player's return.
	[anyone,"oath_only_the_finest_turn_in", 
		[
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		], 
		"This quality craftsmanship, {s2}{playername}. Well done.  I need men I can count upon.", "lord_pretalk", 
		[
			(call_script, "script_quest_oathbound_only_the_finest", OATH_QUEST_SUCCEED),
			(call_script, "script_oath_force_rejoin_if_no_active_missions"),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		]],		
	## OATHBOUND QUEST-: ONLY THE FINEST (Quest #9)
	
	## OATHBOUND QUEST+: MAKE YOUR MARK (Quest #10)
	## $oathbound_master's response to the player's return.
	[anyone,"oath_make_your_mark_turn_in", 
		[
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
			(quest_get_slot, ":troop_no", "qst_oath_make_your_mark", slot_quest_object_troop),
			(troop_get_type, reg5, ":troop_no"),
		], 
		"This is good news, {s2}{playername}. Well done.  These {reg5?women:men} will do nicely.", "lord_pretalk", 
		[
			(call_script, "script_oath_force_rejoin_if_no_active_missions"),
			(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
			(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		]],		
	## OATHBOUND QUEST-: MARK YOUR MARK (Quest #10)
]




# companion_talk_addon	= [   
	
# ]

# village_elder_talk_addon	= [   

# ]

from util_common import *
from util_wrappers import *

# Used by modmerger framework version >= 200 to merge stuff
def modmerge(var_set):
    try:
		var_name_1 = "dialogs"
		orig_dialogs = var_set[var_name_1]
		orig_dialogs.extend(dialogs)
        # Insert Lord Dialog
		pos = FindDialog_i(orig_dialogs, anyone,"lord_start")
		OpBlockWrapper(orig_dialogs).InsertBefore(pos, lord_talk_addon)
		# Insert Initiation Dialog
		pos = FindDialog_i(orig_dialogs, anyone, "center_captured_rebellion_2") # anyone,"start")
		OpBlockWrapper(orig_dialogs).InsertBefore(pos, initiation_dialogs)
		# Insert Companion Dialog
		# pos = FindDialog_i(orig_dialogs, anyone|plyr, "companion_recruit_backstory_response")
		# OpBlockWrapper(orig_dialogs).InsertBefore(pos, companion_talk_addon)
		# Insert Village Elder Dialog
		# pos = FindDialog_i(orig_dialogs, anyone,"village_elder_deliver_cattle_thank")
		# OpBlockWrapper(orig_dialogs).InsertBefore(pos, village_elder_talk_addon)
		
		##ORIG_DIALOGS is a list, can use OpBlockWrapper and other list operations.
    except KeyError:
        errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
        raise ValueError(errstring)