# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_game_menus import *
from header_parties import *
from header_items import *
from header_mission_templates import *
from header_music import *
from header_terrain_types import *

from module_constants import *

game_menus = [

###########################################################################################################################
#####                                              INTERFACE HUB MENUS                                                #####
###########################################################################################################################
	
	# Presentation modes controlled by $oath_mode
	# OATH_MODE_CONTRACT_INFO			= 0		# Display general contract information for the current faction.
	# OATH_MODE_COMMANDER_AUDIENCE		= 1		# Setup a conversation with $oathbound_master.
	# OATH_MODE_JOIN_BATTLE				= 2		# Join $oathbound_party in battle.
	# OATH_MODE_ENTER_LOCATION			= 3		# Enter $current_town where $oathbound_party is attached.
	# OATH_MODE_OATHBOUND_REFERENCE		= 4		# Reference information for the system on things like ranking.
	# OATH_MODE_PAY_INFORMATION			= 5		# Breakdown why you get paid what you do.
	# OATH_MODE_DESERT					= 6		# Abandon the $oathbound_party.
	# OATH_MODE_DEBUGGING				= 7		# Entering a debugging interface.
	# OATH_MODE_MANAGE_COMPANIONS		= 8		# Manage companion dialogs while on map.
	# OATH_MODE_RETURN_TO_MAP			= 9		# Returns to following $oathbound_party.
	# OATH_MODE_QUEST_SELECTION			= 10	# Quest Selector
	
	# mnu_oathbound_switch_modes
	("oathbound_switch_modes", mnf_scale_picture|mnf_disable_all_keys,
		"I shouldn't see this.  This should automatically be hidden by a new presentation.",
		"none",
		[
			# Wipe clean PRES_OBJECTS
			(try_for_range, ":slot", 0, 400),
				(troop_set_slot, PRES_OBJECTS, ":slot", 0),
			(try_end),
			
			(try_begin),
				####### MODE : CONTRACT INFORMATION #######
				(eq, "$oathbound_mode", OATH_MODE_CONTRACT_INFO),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_contract_info"),
			
			(else_try),
				####### MODE : COMMANDER AUDIENCE #######
				(eq, "$oathbound_mode", OATH_MODE_COMMANDER_AUDIENCE),
				(jump_to_menu, "mnu_oathbound_commander_audience"),
				
			(else_try),
				####### MODE : JOIN BATTLE #######
				(eq, "$oathbound_mode", OATH_MODE_JOIN_BATTLE),
				(start_encounter, "$oathbound_party"),
				(change_screen_map),
				(try_begin),
					(store_troop_faction, ":commanders_faction", "$oathbound_master"),
					(faction_slot_eq, ":commanders_faction", slot_faction_oathbound_rank, OATHBOUND_RANK_INITIATE),
					(call_script, "script_oath_change_oathbound_rating", 3),
				(else_try),
					(call_script, "script_oath_change_oathbound_rating", 1),
				(try_end),
				
			(else_try),
				####### MODE : ENTER LOCATION #######
				(eq, "$oathbound_mode", OATH_MODE_ENTER_LOCATION),
				(party_get_attached_to, ":party_attached", "$oathbound_party"),
				(gt, ":party_attached", 0),
				(start_encounter, ":party_attached"),
				(change_screen_map),
				
			(else_try),
				####### MODE : REFERENCE GUIDE #######
				(eq, "$oathbound_mode", OATH_MODE_OATHBOUND_REFERENCE),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_contract_info"),
				
			(else_try),
				####### MODE : PAY INFORMATION #######
				(eq, "$oathbound_mode", OATH_MODE_PAY_INFORMATION),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_compensation"),
				
			(else_try),
				####### MODE : DESERT #######
				(eq, "$oathbound_mode", OATH_MODE_DESERT),
				(change_screen_return),
				(jump_to_menu, "mnu_oathbound_confirm_desert"),
				
			(else_try),
				####### MODE : DEBUGGING #######
				(eq, "$oathbound_mode", OATH_MODE_DEBUGGING),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_debugging"),
				
			(else_try),
				####### MODE : MANAGE COMPANIONS #######
				(eq, "$oathbound_mode", OATH_MODE_MANAGE_COMPANIONS),
				(change_screen_return),
				(assign, "$cms_display", CMS_MODE_MAIN),
				(assign, "$cms_return_location", CMS_RETURN_OATHBOUND),
				(jump_to_menu, "mnu_companion_settings"),
				
			(else_try),
				####### MODE : QUEST SELECTOR #######
				(eq, "$oathbound_mode", OATH_MODE_QUEST_SELECTION),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_quest_selector"),
				
			(else_try),
				####### MODE : EVENT LOG #######
				(eq, "$oathbound_mode", OATH_MODE_EVENT_LOG),
				(change_screen_return),
				(start_presentation, "prsnt_oathbound_event_log"),
				
			(else_try),
				####### MODE : RETURN TO MAP #######
				(eq, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
				(change_screen_map),
				(assign, "$g_infinite_camping", 1),
				(rest_for_hours_interactive, 24 * 365, 5, 1),
				
			(try_end),
			],
		[
			("continue",[], "Return to Map...",	
				[
					(change_screen_map),
					(assign, "$g_infinite_camping", 1),
					(rest_for_hours_interactive, 24 * 365, 5, 1),
				]),
			
		]),
		
###########################################################################################################################
#####                                              STANDARD MENU CODE                                                 #####
###########################################################################################################################	
	
	## OATHBOUND FUNCTION+: COMMANDER AUDIENCE
	## mnu_oathbound_commander_audience
	("oathbound_commander_audience",0,
    "Your request for a meeting is relayed to your commander's camp, and finally {s6} appears from his tent to speak with you.",
    "none",
    [
		# (set_background_mesh, "mesh_pic_soldier_world_map"),
		(str_store_troop_name, s6, "$oathbound_master"),
	],
    [
		("continue",[],
			"Continue...",
			[
				(try_begin),
					(party_get_attached_to, reg0, "$oathbound_party"),
					(lt, reg0, 0),
					(start_encounter, "$oathbound_party"),
					(change_screen_map),
				(else_try),
					#Fake that it is a party encounter when enlisted party in a town (lines taken from script_game_event_party_encounter)
					(assign, "$g_encountered_party", "$oathbound_party"),
					(store_faction_of_party, "$g_encountered_party_faction","$g_encountered_party"),
					(store_relation, "$g_encountered_party_relation", "$g_encountered_party_faction", "fac_player_faction"),
					(party_get_slot, "$g_encountered_party_type", "$g_encountered_party", slot_party_type),
					(party_get_template_id,"$g_encountered_party_template","$g_encountered_party"),
					(assign, "$talk_context", tc_party_encounter),
					(call_script, "script_setup_party_meeting", "$g_encountered_party"),
				(try_end),
			]),
			
		("reject_talk_lord",[],"No, never mind.",
			[(start_presentation, "prsnt_oathbound_contract_info"),]),
    ]),
	## OATHBOUND FUNCTION-: COMMANDER AUDIENCE
	
	## OATHBOUND FUNCTION+: CONTRACT RENEWAL
	## mnu_oathbound_renew_contract
	("oathbound_renew_contract",0,
    "Your contract period has expired.^^Currently:^You hold the rank of {s23}.^{s21}{s22}^^Do you wish to renew your contract for another {reg21} days?",
    "none",
    [
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(assign, ":rank", reg1),
		(call_script, "script_oath_describe_oathbound_rank", ":rank"), # Stores s1 (rank name), s2 (rank title)
		(str_store_string, s23, s1),
		(try_begin),
			(neg|str_is_empty, s2),
			(str_store_string, s21, "@You carry the title of {s2}."),
		(else_try),
			(str_store_string, s21, "@You carry no title."),
		(try_end),
		(try_begin),
			(eq, ":rank", OATHBOUND_RANK_INITIATE),
			(call_script, "script_oath_describe_oathbound_rank", OATHBOUND_RANK_MILITIA), # Stores s1 (rank name), s2 (rank title)
			(str_store_string, s22, "@^^You are being offered the rank of {s1} upon renewal."),
		(else_try),
			(str_clear, s22),
		(try_end),
		(store_div, reg21, OATHBOUND_CONTRACT_DURATION, 24),
	],
	[
		("oathbound_renew_yes",
			[],"These terms are agreeable.",
			[
				(call_script, "script_oath_add_log_entry", "$oathbound_events", OATHBOUND_EVENT_CONTRACT_RENEWAL, -1),
				(val_add, "$oathbound_remaining_hours", OATHBOUND_CONTRACT_DURATION),
				(val_add, "$oathbound_contract_periods", 1),
				(display_message, "@You have chosen to extend your contract.", gpu_green),
				(call_script,"script_change_player_relation_with_troop", "$oathbound_master", 2, 0),
				# Advance Initiates to Militia
				(try_begin),
					(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
					(eq, reg1, OATHBOUND_RANK_INITIATE),
					(call_script, "script_oath_get_rating_to_next_rank"), # Stores reg1 (remaining rating), reg2 (next rank)
					(call_script, "script_oath_change_oathbound_rating", reg1),
				(try_end),
				(call_script, "script_oath_change_oathbound_reputation", 3),
				# Update faction renewals
				(store_troop_faction, ":faction_no", "$oathbound_master"),
				(faction_get_slot, ":renewals", ":faction_no", slot_faction_oathbound_renewals),
				(val_add, ":renewals", 1),
				(faction_set_slot, ":faction_no", slot_faction_oathbound_renewals, ":renewals"),
				(change_screen_map),
				(assign, "$g_infinite_camping", 1),
				(rest_for_hours_interactive, 24 * 365, 5, 1),
			]),
		
		("oathbound_renew_no",
			[],"I wish to be released from service.",
			[
				(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_NOT_HIRED),
				(change_screen_map),
			]),
    ]),
	## OATHBOUND FUNCTION-: CONTRACT RENEWAL
	
	## OATHBOUND FUNCTION+: DESERTION
	## mnu_oathbound_confirm_desert
	("oathbound_confirm_desert",0,
    "You {reg2?:and your friends }have started considering the idea of abandoning {s21}'s service and striking out on your own.  Once you leave, however, you'll be branded a deserter with a price on your head.",
    "none",
    [
		(str_store_troop_name, s21, "$oathbound_master"),
		(party_get_num_companion_stacks, reg2, "p_main_party"),
	],
	[
		("oathbound_desert_yes",
			[(str_store_troop_name, s21, "$oathbound_master"),],
			"I've had enough of {s21}'s leadership.  It's time to go.",
			[
				(call_script, "script_oath_set_contract_status", OATHBOUND_STATUS_DESERTER),
				(change_screen_map),
			]),
		
		("oathbound_desert_no",
			[],"On second thought I'd better rethink this.",
			[
				(start_presentation, "prsnt_oathbound_contract_info"),
			]),
    ]),
	## OATHBOUND FUNCTION-: DESERTION
	
	## OATHBOUND QUEST+: FRESH MEAT (Quest #13)
	## mnu_oathbound_fresh_meat
	("oathbound_fresh_meat",0,
    "Oathbound Quest Event^^As the army comes to a halt for the evening and tents are raised around the camp, the men picked by {s21} seek you out bringing a barrel full of training equipment with them.  After a brief inspection of the contents they pull out {s22}{s23} and offer the same to you.^^One challenges, 'We are ready for the next lesson, {s2}{s24}.'",
	"none",
    [
		## Setup preferred weaponry.
		(assign, ":highest_prof", 0),
		(assign, ":item_1", -1),
		(assign, ":item_2", -1),
		(store_proficiency_level, ":prof", "trp_player", wpt_one_handed_weapon),
		(try_begin),
			(ge, ":prof", ":highest_prof"),
			(assign, ":highest_prof", ":prof"),
			(assign, ":item_1", "itm_practice_sword"),
			(assign, ":item_2", "itm_practice_shield"),
		(try_end),
		(store_proficiency_level, ":prof", "trp_player", wpt_two_handed_weapon),
		(try_begin),
			(ge, ":prof", ":highest_prof"),
			(assign, ":highest_prof", ":prof"),
			(assign, ":item_1", "itm_heavy_practice_sword"),
			(assign, ":item_2", -1),
		(try_end),
		(store_proficiency_level, ":prof", "trp_player", wpt_polearm),
		(try_begin),
			(ge, ":prof", ":highest_prof"),
			(assign, ":highest_prof", ":prof"),
			(assign, ":item_1", "itm_practice_staff"),
			(assign, ":item_2", -1),
		(try_end),
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		(str_store_troop_name, s21, "$oathbound_master"),
		(str_store_item_name, s22, ":item_1"),
		(str_clear, s23),
		(try_begin),
			(ge, ":item_2", 1),
			(str_store_item_name, s23, ":item_2"),
			(str_store_string, s23, "@ and {s23}"),
		(try_end),
		(quest_get_slot, ":goal", "qst_oath_fresh_meat", slot_quest_target_amount),
		(quest_get_slot, ":progress", "qst_oath_fresh_meat", slot_quest_temp_slot),
		(store_sub, reg21, ":goal", ":progress"),
		(store_sub, reg22, reg21, 1),
		(str_store_troop_name, s24, "trp_player"),
	],
	[
		("oathbound_fresh_meat_train",
			[],
			"You reply, 'Ready for another lesson so soon?  On with it then!'",
			[
				## Setup preferred weaponry.
				(assign, ":highest_prof", 0),
				(assign, ":item_1", -1),
				(assign, ":item_2", -1),
				(store_proficiency_level, ":prof", "trp_player", wpt_one_handed_weapon),
				(try_begin),
					(ge, ":prof", ":highest_prof"),
					(assign, ":highest_prof", ":prof"),
					(assign, ":item_1", "itm_practice_sword"),
					(assign, ":item_2", "itm_practice_shield"),
				(try_end),
				(store_proficiency_level, ":prof", "trp_player", wpt_two_handed_weapon),
				(try_begin),
					(ge, ":prof", ":highest_prof"),
					(assign, ":highest_prof", ":prof"),
					(assign, ":item_1", "itm_heavy_practice_sword"),
					(assign, ":item_2", -1),
				(try_end),
				(store_proficiency_level, ":prof", "trp_player", wpt_polearm),
				(try_begin),
					(ge, ":prof", ":highest_prof"),
					(assign, ":highest_prof", ":prof"),
					(assign, ":item_1", "itm_practice_staff"),
					(assign, ":item_2", -1),
				(try_end),
				
				## Setup regional recruits.
				(store_troop_faction, ":faction_no", "$oathbound_master"),
				(faction_get_slot, ":troop_recruit", ":faction_no", slot_faction_tier_1_troop),
				(try_begin),
					(lt, ":troop_recruit", 1),
					(assign, ":troop_recruit", "trp_trainee_peasant"),
				(try_end),
				
				## Setup mission parameters.
				(set_jump_mission,"mt_oathbound_army_training"),
				(party_get_slot, ":village_scene", "p_village_13", slot_castle_exterior),
				(modify_visitors_at_site, ":village_scene"),
				(reset_visitors),
				(set_visitor, 0, "trp_player"),
				(set_visitors, 1, ":troop_recruit", 2),
				(mission_tpl_entry_add_override_item, "mt_oathbound_army_training", 0, ":item_1"),
				(mission_tpl_entry_add_override_item, "mt_oathbound_army_training", 1, ":item_1"),
				(try_begin),
					(ge, ":item_2", 1),
					(mission_tpl_entry_add_override_item, "mt_oathbound_army_training", 0, ":item_2"),
					(mission_tpl_entry_add_override_item, "mt_oathbound_army_training", 1, ":item_2"),
				(try_end),
				(set_jump_entry, 11),
				(jump_to_scene, ":village_scene"),
				# (jump_to_menu, "mnu_oathbound_fresh_meat_result"),
				(music_set_situation, 0),
				(change_screen_mission),
			]),
		
		("oathbound_fresh_meat_unwell",
			[
				(store_troop_health, reg5, "trp_player"),
				(lt, reg5, 50),
			],"You reply, 'I am yet healing.'  ({reg5}% Health)",
			[
				(change_screen_map),
				(assign, "$g_infinite_camping", 1),
				(rest_for_hours_interactive, 24 * 365, 5, 1),
			]),
		
		("oathbound_fresh_meat_delay",
			[],"You reply, 'Not tonight.  Tomorrow perhaps.'",
			[
				(call_script, "script_oath_change_oathbound_rating", -1),
				(change_screen_map),
				(assign, "$g_infinite_camping", 1),
				(rest_for_hours_interactive, 24 * 365, 5, 1),
			]),
		
		("oathbound_fresh_meat_abandon_task",
			[],"You reply, 'There is nothing I can teach you.' (Abandon Task)",
			[
				(jump_to_menu, "mnu_oathbound_fresh_meat_abandon"),
			]),
    ]),
	
	## mnu_oathbound_fresh_meat_result
	("oathbound_fresh_meat_result",mnf_disable_all_keys,
    "{s0}",
    "none",
    [
		## Match Outcome
		(try_begin),
			## PLAYER WON
			(quest_slot_eq, "qst_oath_fresh_meat", slot_quest_object_state, 1),
			(call_script, "script_oath_quest_change_slot", "qst_oath_fresh_meat", slot_quest_temp_slot, 1),
			(call_script, "script_oath_quest_set_slot", "qst_oath_fresh_meat", slot_quest_object_state, 0),
			(call_script, "script_quest_oathbound_fresh_meat", OATH_QUEST_VICTORY_CONDITION),
			(str_store_string, s0, "@After beating your last opponent, you explain to the recruits how to better defend themselves against such an attack. Hopefully they'll take the experience on board and will be prepared next time."),
		(else_try),
			## PLAYER LOST
			(str_store_string, s0, "@You were beaten. The recruits are heartened by their success, but the lesson you wanted to teach them probably didn't get through..."),
		(try_end),
		(call_script, "script_oath_quest_set_slot", "qst_oath_fresh_meat", slot_quest_target_state, 0),
	],
    [
		("continue", [], "Continue...",
			[
				(change_screen_map),
				(assign, "$g_infinite_camping", 1),
				(rest_for_hours_interactive, 24 * 365, 5, 1),
			]),
    ]),
	
	## mnu_oathbound_fresh_meat_abandon
	("oathbound_fresh_meat_abandon",mnf_disable_all_keys,
    "{s23} would be greatly displeased if you were to abandon this task.  Are you certain?",
    "none",
    [(str_store_troop_name, s21, "$oathbound_master"),],
    [
		("oathbound_fresh_meat_abandon_yes", [], "Yes.  My efforts here are pointless.",
			[
				(call_script, "script_quest_oathbound_fresh_meat", OATH_QUEST_FAIL),
			]),
		
		("oathbound_fresh_meat_abandon_no", [], "No.  I will stick with it.",
			[
				(jump_to_menu, "mnu_oathbound_fresh_meat"),
			]),
    ]),
	## OATHBOUND QUEST-: FRESH MEAT (Quest #13)
 ]

oathbound_pre_join = [
	(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
	(try_begin),
		(party_get_attached_to, ":attached", "$oathbound_party"),
		(this_or_next|eq, "$oathbound_party", "$g_encountered_party_2"),
		(eq, ":attached", "$g_encountered_party_2"),
		(select_enemy, 0),
		(assign,"$g_enemy_party","$g_encountered_party"),
		(assign,"$g_ally_party","$g_encountered_party_2"),
	(else_try),
		(select_enemy, 1),
		(assign,"$g_enemy_party","$g_encountered_party_2"),
		(assign,"$g_ally_party","$g_encountered_party"),
	(try_end),
	(jump_to_menu,"mnu_join_battle"),
]	

oathbound_join_siege_outside = [
	(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
	(try_begin),
		(store_troop_faction, ":commanders_faction", "$oathbound_master"),
		(store_relation, ":relation", ":commanders_faction", "$g_encountered_party_faction"),
		(this_or_next|eq, ":commanders_faction", "$g_encountered_party_faction"), #encountered party is always the castle/town sieged
		(ge, ":relation", 0),
		(assign, "$g_defending_against_siege", 1),
		(assign, "$g_siege_first_encounter", 1),
		(jump_to_menu, "mnu_siege_started_defender"),
	(else_try),
		(jump_to_menu, "mnu_besiegers_camp_with_allies"),
	(try_end),
]

oathbound_join_battle_collect_others = [
	(try_begin),
		(eq, "$oathbound_status", OATHBOUND_STATUS_CONTRACTED),
		(call_script, "script_let_nearby_parties_join_current_battle", 0, 0),
		(str_store_party_name, 1,"$g_enemy_party"), #to prevent bug'd text from the above script (which also uses s1)
	(try_end),
]		
# hook_assessment_quest_initiation = [
	# (call_script, "script_qp2_hook_assessment_initiations"), # Floris 2.6 : Quest Pack 2 Initialization - Windyplains
# ]

from util_common import *
from util_wrappers import *

def modmerge_game_menus(orig_game_menus, check_duplicates = False):
	try: #battle joining
		find_i = list_find_first_match_i( orig_game_menus, "pre_join" )
		codeblock = GameMenuWrapper(orig_game_menus[find_i]).GetOpBlock()
		codeblock.Append(oathbound_pre_join)	
		find_i = list_find_first_match_i( orig_game_menus, "join_battle" )
		codeblock = GameMenuWrapper(orig_game_menus[find_i]).GetOpBlock()
		pos = codeblock.FindLineMatching( (call_script, "script_encounter_init_variables") )
		codeblock.InsertBefore(pos, oathbound_join_battle_collect_others)	
		find_i = list_find_first_match_i( orig_game_menus, "join_siege_outside" )
		codeblock = GameMenuWrapper(orig_game_menus[find_i]).GetOpBlock()
		codeblock.Append(oathbound_join_siege_outside)			
	except:
		import sys
		print "Injecton 1 failed:", sys.exc_info()[1]
		raise

	if( not check_duplicates ):
		orig_game_menus.extend(game_menus) # Use this only if there are no replacements (i.e. no duplicated item names)
	else:
	# Use the following loop to replace existing entries with same id
		for i in range (0,len(game_menus)-1):
			find_index = find_object(orig_game_menus, game_menus[i][0]); # find_object is from header_common.py
			if( find_index == -1 ):
				orig_game_menus.append(game_menus[i])
			else:
				orig_game_menus[find_index] = game_menus[i]
			
	# # splice this into camp menu to call the mod options presentation
    # find_index = find_object(orig_game_menus, "camp")
    # orig_game_menus[find_index][5].insert(0,
            # ("qp3_debugging",[(ge, DEBUG_QUEST_PACK_3, 1),],"Quest Pack 3 Debugging Menus", [(jump_to_menu, "mnu_qp3_debug_menu")]),
          # )
		  
# Used by modmerger framework version >= 200 to merge stuff
def modmerge(var_set):
	try:
		var_name_1 = "game_menus"
		orig_game_menus = var_set[var_name_1]
		modmerge_game_menus(orig_game_menus)
		# Inside menu "bandit_lair" -> menu option "leave_victory" consequence block -> Add insertion for "qst_destroy_the_lair" above [ (assign, "$g_leave_encounter", 0), ].
		# find_i = list_find_first_match_i( orig_game_menus, "bandit_lair" )
		# menu = GameMenuWrapper(orig_game_menus[find_i])
		# menuoptions = menu.GetMenuOptions()
		# submenu_index = list_find_first_containing_i(menuoptions, "leave_victory")
		# submenu = GameMenuOptionWrapper(menuoptions[submenu_index])
		# submenu.GetConsequenceBlock().InsertBefore(0,[ (call_script, "script_qp3_quest_destroy_the_lair", floris_quest_victory_condition), ])
        # codeblock = GameMenuWrapper(orig_game_menus[find_i]).GetOpBlock()
        # line_i = codeblock.GetLength() - 2
        # codeblock.InsertBefore(line_i, hook_assessment_quest_initiation)
	except KeyError:
		errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
		raise ValueError(errstring)