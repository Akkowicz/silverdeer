# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_common import *
from header_presentations import *
from header_mission_templates import *
from ID_meshes import *
from header_operations import *
from header_triggers import *
from module_constants import *
from header_items import *
from header_skills import *
import string

####################################################################################################################
#  Each presentation record contains the following fields:
#  1) Presentation id: used for referencing presentations in other files. The prefix prsnt_ is automatically added before each presentation id.
#  2) Presentation flags. See header_presentations.py for a list of available flags
#  3) Presentation background mesh: See module_meshes.py for a list of available background meshes
#  4) Triggers: Simple triggers that are associated with the presentation
####################################################################################################################

presentations = [
###########################################################################################################################
#####                                             CONTRACT INFORMATION                                                #####
###########################################################################################################################

("oathbound_contract_info", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		######################################
		### SECTION - CONTRACT INFORMATION ###
		######################################
		
		## OBJ - PORTRAIT - $OATHBOUND_MASTER
		(assign, ":pos_x", 265),
		(assign, ":pos_y", 445),
		(try_begin),
			(ge, "$oathbound_master", 1),
			(call_script, "script_gpu_create_portrait", "$oathbound_master", ":pos_x", ":pos_y", 400, oath1_obj_portrait_oathbound_master),
			# "In Service To:" (above the portrait)
			(store_add, ":pos_x_temp", ":pos_x", 70),
			(store_add, ":pos_y_temp", ":pos_y", 150),
			(str_store_string, s21, "@In Service To:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_center),
			(call_script, "script_gpu_resize_object", 0, 75),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_center),
			(call_script, "script_gpu_resize_object", 0, 75),
			# Name of $oathbound_master. (below the portrait)
			(store_add, ":pos_x_temp", ":pos_x", 70),
			(store_add, ":pos_y_temp", ":pos_y", -10),
			(str_store_troop_name, s21, "$oathbound_master"),
			(str_store_string, s21, "@{s21}"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_center),
			(call_script, "script_gpu_resize_object", 0, 75),
			# Name of $oathbound_master. (below $oathbound_master name)
			(val_sub, ":pos_y_temp", 20),
			(store_troop_faction, ":faction_no", "$oathbound_master"),
			(str_store_faction_name, s21, ":faction_no"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_center),
			(call_script, "script_gpu_resize_object", 0, 75),
		(else_try),
			(assign, reg31, "$oathbound_master"),
			(display_message, "@ERROR - $oathbound_master is invalid = {reg31}.", gpu_red),
			(str_store_string, s21, "@ERROR^^No Oathbound Master^^Selected"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", 335, 540, 0, gpu_center),
			(call_script, "script_gpu_resize_object", 0, 75),
		(try_end),
		
		(assign, ":pox_x_col_1", 425),
		(assign, ":pos_x_col_2", 555),
		(assign, ":pos_y", 580),
		(assign, ":y_line_step", 25),
		
		## OBJ - TEXT - RANK
		(str_store_string, s21, "@Rank:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pox_x_col_1", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
		(str_store_string, s21, s1),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - TEXT - RATING
		(val_sub, ":pos_y", ":y_line_step"),
		(call_script, "script_oath_get_rating_to_next_rank"), # Stores reg1 (remaining rating), reg2 (next rank)
		(assign, ":needed", reg1),
		(call_script, "script_oath_describe_oathbound_rank", reg2), # Stores s1 (rank name), s2 (rank title)
		(assign, reg21, ":needed"),
		(str_store_string, s21, "@{reg21} rating needed for {s1}"),
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(try_begin),
			(ge, reg1, OATHBOUND_RANK_VASSAL_KNIGHT),
			(str_store_string, s21, "@Maximum Rank Achieved"),
		(try_end),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - TEXT - WEEKLY PAY
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Weekly Pay:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pox_x_col_1", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_oath_calculate_weekly_pay"), # Returns reg1 (pay)
		(str_store_string, s21, "@{reg1} denars"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - TEXT - CONTRACT DURATION
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Contract Duration:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pox_x_col_1", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_oath_convert_hours_to_description", "$oathbound_remaining_hours", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
		(str_store_string, s21, "@{s1}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - TEXT - NEXT LEAVE PERIOD
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Next Leave:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pox_x_col_1", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(store_sub, ":leave_hours", OATHBOUND_MIN_TIME_BETWEEN_LEAVE, "$oathbound_time_since_leave"),
		(try_begin),
			(store_troop_faction, ":faction_no", "$oathbound_master"),
			(faction_slot_eq, ":faction_no", slot_faction_oathbound_rank, OATHBOUND_RANK_INITIATE),
			(call_script, "script_oath_describe_oathbound_rank", OATHBOUND_RANK_MILITIA), # Stores s1 (rank name), s2 (rank title)
			(str_store_string, s1, "@You must be at least a {s1} to take leave."),
		(else_try),
			(ge, ":leave_hours", 1),
			(call_script, "script_oath_convert_hours_to_description", ":leave_hours", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
			(str_store_string, s1, "@{s1}"),
		(else_try),
			(str_store_string, s1, "@You may take leave."),
		(try_end),
		(str_store_string, s21, "@{s1}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - TEXT - REPUTATION
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Reputation:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pox_x_col_1", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_oath_describe_reputation_with_faction", ":faction_no"), # Stores s1 (reputation text), reg1 (reputation value)
		(str_store_string, s21, "@{s1} ({reg1})"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_col_2", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		
		
		###################################
		### SECTION - CURRENT SITUATION ###
		###################################
		
		(assign, ":y_bottom", 100),
		(assign, ":x_left",   250),
		(assign, ":x_width",  675),
		(assign, ":y_width",  245),
		
		(str_store_string, s21, "@Current Situation:"),
		(store_add, ":pos_y_temp", ":y_bottom", ":y_width"),
		(val_add, ":pos_y_temp", 15),
		(store_add, ":pos_x_temp", ":x_left", 0),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
		# (call_script, "script_gpu_resize_object", 0, 75),
		
		## OBJ - CONTAINER+ - CURRENT SITUATION
		# (call_script, "script_gpu_draw_line", ":x_width", ":y_width", ":x_left", ":y_bottom", gpu_white), # - Footer
		(call_script, "script_gpu_container_heading", ":x_left", ":y_bottom", ":x_width", ":y_width", grt4_obj_container_1),
		
			(assign, ":pos_y", ":y_width"),
			(assign, ":y_line_step", 20),
			(assign, ":x_desc", 5),
			
			(str_store_string, s60, "@^"), # This is our final output.
			(assign, ":total_lines", 0),
			
			## CURRENT STATUS
			(call_script, "script_oath_describe_oathbound_party_actions"), # Stores s11 (description)
			(str_store_string, s42, s11),
			(call_script, "script_oath_describe_party_health", "$oathbound_party"), # Stores s1 (description)
			(str_store_string, s42, "@{s42}  {s1}"),
			(str_store_string, s1, s42),
			(call_script, "script_oath_word_wrap_text", 75), # Input s1, Returns s1 (wrapped text), reg1 (# lines)
			(str_store_string, s60, "@{s60}{s1}"),
			(val_add, ":total_lines", reg1),
			
			## OBJ - TEXT - STATUS OF PERMISSIBLE EXITS
			(call_script, "script_oath_lord_decides_if_leave_is_okay"), # Stores s41 (reason to block)
			(str_store_troop_name, s22, "$oathbound_master"),
			(try_begin),
				(eq, "$oathbound_exit_allowed", 1),
				(str_store_string, s60, "@{s60}^^{s22} is currently allowing people to go on leave."),
			(else_try),
				(str_store_string, s60, "@{s60}^^{s22} {s41}"),
			(try_end),
			(val_add, ":total_lines", 2),
			
			## OBJ - TEXT - CURRENT TASKS IN THE ARMY:
			(str_store_string, s29, "@^^Current Tasks:"),
			(assign, ":task_lines", 3),
			(try_begin),
				(assign, ":active_missions", 0),
				(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
					(check_quest_active, ":quest_no"),
					(store_sub, ":string_desc", ":quest_no", OATHBOUND_QUESTS_BEGIN),
					(val_add, ":string_desc", "str_oath_quest_short_desc_01"),
					(str_store_string, s1, ":string_desc"),
					(neg|str_equals, s1, "@N/A"),
					(val_add, ":active_missions", 1),
					(val_add, ":task_lines", 1),
					(str_store_string, s29, "@{s29}^ * {s1}"),
				(try_end),
				(ge, ":active_missions", 1),
				(val_add, ":total_lines", ":task_lines"),
				(str_store_string, s60, "@{s60}{s29}"),
			(try_end),
			
			## OUTPUT DESCRIPTION
			(store_mul, ":pos_y_offset", ":y_line_step", ":total_lines"),
			(val_sub, ":pos_y", ":pos_y_offset"),
			(str_store_string, s21, s60),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_desc", ":pos_y", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
		(set_container_overlay, -1), ## CONTAINER- - CURRENT SITUATION

      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
    ]),
  ]),
  

###########################################################################################################################
#####                                        QUEST SELECTION PRESENTATION                                             #####
###########################################################################################################################

("oathbound_quest_selector", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		## Clean out our button / quest slots on each reload.
		(try_for_range, ":button_slot_no", oath10_obj_button_quest_no, oath10_val_button_quest_no),
			(troop_set_slot, PRES_OBJECTS, ":button_slot_no", 0),
			# Get our quest slot #.
			(store_sub, ":quest_slot_no", ":button_slot_no", oath10_obj_button_quest_no),
			(val_add, ":quest_slot_no", oath10_val_button_quest_no),
			(troop_set_slot, PRES_OBJECTS, ":quest_slot_no", 0),
		(try_end),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		## OBJ - HEADER REPLACEMENT - "Tasks X Needs Done"
		(str_store_troop_name, s22, "$oathbound_master"),
		(str_store_string, s21, "@Tasks {s22} Needs Done"),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title),
		(overlay_set_text, ":obj_no", s21),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title2),
		(overlay_set_text, ":obj_no", s21),
		
		(assign, ":y_bottom", 100),
		(assign, ":x_left",   250),
		(assign, ":x_width",  700),
		(assign, ":y_width",  495),
		
		## OBJ - CONTAINER+ - QUEST SELECTION LIST
		# (call_script, "script_gpu_draw_line", ":x_width", ":y_width", ":x_left", ":y_bottom", gpu_white), # - Footer
		(call_script, "script_gpu_container_heading", ":x_left", ":y_bottom", ":x_width", ":y_width", grt4_obj_container_1),
			
			(assign, ":pos_y_min", 0),
			(assign, ":records", 0),
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_cf_oath_quest_allowed_for_selection", ":quest_no"),
				(call_script, "script_cf_oath_player_meets_minimum_rank_for_quest", ":quest_no"),
				(neg|check_quest_active, ":quest_no"),
				(neg|quest_slot_ge, ":quest_no", slot_quest_dont_give_again_remaining_days,	1),
				(quest_get_slot, ":script_no", ":quest_no", slot_quest_unique_script),
				(call_script, ":script_no", OATH_QUEST_PREREQUISITES), # reg1 returns as 1 on pass.
				(val_add, ":pos_y_min", 110),
				(val_add, ":records", 1),
			(try_end),
			
			(assign, ":pos_y", 520),
			(val_max, ":pos_y", ":pos_y_min"),
			(assign, ":pos_x", 0),
			
			# ### DIAGNOSTIC+ ###
			# (assign, reg31, ":pos_y"),
			# (assign, reg32, ":pos_y_min"),
			# (assign, reg33, ":records"),
			# (display_message, "@DEBUG (Oathbound): Pos_Y = {reg31}, Pos_Y_min = {reg32}, Quest Records = {reg33}.", gpu_debug),
			# ### DIAGNOSTIC- ###
			
			# (assign, ":y_line_step", 20),
			# (assign, ":x_desc", 110),
			# (assign, ":y_option_step", 70),
			
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(call_script, "script_cf_oath_quest_allowed_for_selection", ":quest_no"),
				(call_script, "script_cf_oath_player_meets_minimum_rank_for_quest", ":quest_no"),
				(neg|check_quest_active, ":quest_no"),
				(neg|quest_slot_ge, ":quest_no", slot_quest_dont_give_again_remaining_days,	1),
				(val_sub, ":pos_y", 75),
				
				### QUEST STAMP+ ### (Expected Inputs: Pos_X, Pos_Y, Quest #
				
				## OBJ - TEXT - Quest Title
				(str_store_quest_name, s21, ":quest_no"),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x", ":pos_y", 0, gpu_left),
				# (overlay_set_color, reg1, gpu_blue),
				(store_sub, ":pos_x_temp", ":pos_x", 1),
				(store_add, ":pos_y_temp", ":pos_y", 1),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
				(overlay_set_color, reg1, gpu_blue),
				
				## OBJ - TEXT - Rank Requirement
				(store_add, ":pos_x_temp", ":pos_x", 490),
				(call_script, "script_oath_quest_get_minimum_rank_requirement", ":quest_no"), # Returns reg1 (minimum rank)
				(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title)
				(str_store_string, s21, "@Rank: {s1}+"),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y", 0, gpu_right),
				# (call_script, "script_gpu_resize_object", 0, 75),
				
				## OBJ - TEXT - Quest Description
				(store_add, ":pos_x_temp", ":pos_x", 0),
				(val_sub, ":pos_y", -5),
				(store_sub, ":string_offset", ":quest_no", OATHBOUND_QUESTS_BEGIN),
				(store_add, ":string_no", "str_oath_quest_desc_01", ":string_offset"),
				(str_store_string, s1, ":string_no"),
				(call_script, "script_oath_word_wrap_text", 75), # Input s1, Returns s1 (wrapped text), reg1 (# lines)
				(store_mul, ":y_offset", reg1, 10),
				(val_sub, ":pos_y", ":y_offset"),
				(str_store_string, s21, s1),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y", 0, gpu_left),
				(call_script, "script_gpu_resize_object", 0, 75),
				
				## OBJ - TEXT - Quest Type
				(store_add, ":pos_x_temp", ":pos_x", 615),
				(store_add, ":pos_y_temp", ":pos_y", -25),
				(store_sub, ":string_offset", ":quest_no", OATHBOUND_QUESTS_BEGIN),
				(store_add, ":string_no", "str_oath_quest_type_01", ":string_offset"),
				(str_store_string, s21, ":string_no"),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_center),
				(call_script, "script_gpu_resize_object", 0, 75),
				
				## OBJ - BUTTON - Begin Quest
				(store_add, ":pos_x_temp", ":pos_x", 615),
				(store_add, ":pos_y_temp", ":pos_y", -10),
				# Find the first unused button object slot.
				(assign, ":button_slot_no", -1),
				(try_for_range, ":slot_no", oath10_obj_button_quest_no, oath10_val_button_quest_no),
					(neg|troop_slot_ge, PRES_OBJECTS, ":slot_no", 1), # Not currently in use.
					(eq, ":button_slot_no", -1),
					(assign, ":button_slot_no", ":slot_no"),
				(try_end),
				# Determine our associated quest slot #.
				(store_sub, ":quest_slot_no", ":button_slot_no", oath10_obj_button_quest_no),
				(val_add, ":quest_slot_no", oath10_val_button_quest_no),
				(troop_set_slot, PRES_OBJECTS, ":quest_slot_no", ":quest_no"),
				# Create our button.
				(str_store_string, s21, "@Accept Task"),
				(call_script, "script_gpu_create_game_button", "str_hub_s21", ":pos_x_temp", ":pos_y_temp", ":button_slot_no"),
				
				### QUEST STAMP- ###
				
			(try_end),
			
		(set_container_overlay, -1), ## CONTAINER- - QUEST SELECTION LIST
      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
		
		(try_begin),
			## BUTTON - ACCEPT TASK
			(assign, ":button_slot_no", -1),
			(try_for_range, ":slot_no", oath10_obj_button_quest_no, oath10_val_button_quest_no),
				(troop_slot_eq, PRES_OBJECTS, ":slot_no", ":object"),
				(eq, ":button_slot_no", -1),
				(assign, ":button_slot_no", ":slot_no"),
			(try_end),
			(neq, ":button_slot_no", -1),
			# Get our quest slot #.
			(store_sub, ":quest_slot_no", ":button_slot_no", oath10_obj_button_quest_no),
			(val_add, ":quest_slot_no", oath10_val_button_quest_no),
			(troop_get_slot, ":quest_no", PRES_OBJECTS, ":quest_slot_no"),
			(str_store_quest_name, s21, ":quest_no"),
			# Get the quest's specific script and begin it.
			(quest_get_slot, ":unique_script", ":quest_no", slot_quest_unique_script),
			(call_script, ":unique_script", OATH_QUEST_BEGIN),
			# Restart our presentation.
			(start_presentation, "prsnt_oathbound_quest_selector"),
			
		(try_end),
    ]),
  ]),
  

###########################################################################################################################
#####                                         PAY BREAKDOWN PRESENTATION                                              #####
###########################################################################################################################

("oathbound_compensation", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		## OBJ - HEADER REPLACEMENT - "Tasks X Needs Done"
		(str_store_string, s21, "@Weekly Pay Breakdown"),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title),
		(overlay_set_text, ":obj_no", s21),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title2),
		(overlay_set_text, ":obj_no", s21),
		
		(assign, ":x_col_heading",    275), # left justified
		(assign, ":x_col_factor",     300), # left justified
		(assign, ":x_col_desc",       525), # left justified
		(assign, ":x_col_value",      825), # right justified
		(assign, ":x_col_value_type", 830), # left justified
		(assign, ":pos_y",            590),
		(assign, ":y_line_step",       22), # space for each line.
		(assign, ":y_header_step",     28), # space for each header.
		
		########################
		### BASE PAY FACTORS ###
		########################
		(assign, ":total_base_pay", 0),
		
		## Header
		(str_store_string, s21, "@Base Pay Factors:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		
		## LINE 1 - Base Pay
		(val_sub, ":pos_y", ":y_header_step"),
		# Name
		(str_store_string, s21, "@Base Pay:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		# Value
		(call_script, "script_oath_convert_value_to_denars_string", OATHBOUND_BASE_PAY_VALUE, "str_oath_denar"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, OATHBOUND_BASE_PAY_VALUE),
		(assign, ":color", reg20),
		(val_add, ":total_base_pay", OATHBOUND_BASE_PAY_VALUE),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		## LINE 2 - Character Level
		(val_sub, ":pos_y", ":y_line_step"),
		# Name
		(store_character_level, ":level", "trp_player"),
		(assign, reg1, ":level"),
		(str_store_string, s21, "@Level {reg1}:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(str_store_string, s21, "@(Level - 5) / 3 * 25"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(store_sub, ":pay", ":level", 5),
		(val_div, ":pay", 3),
		(val_mul, ":pay", 25),
		(val_add, ":total_base_pay", ":pay"),
		(call_script, "script_oath_convert_value_to_denars_string", ":pay", "str_oath_denar"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":pay"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		## LINE 3 - Squad Bounty
		(val_sub, ":pos_y", ":y_line_step"),
		# Name
		(store_character_level, ":level", "trp_player"),
		(str_store_string, s21, "@Squad Kills:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(assign, reg21, OATHBOUND_BOUNTY_PAY),
		(assign, reg22, "$oathbound_bounty_count"),
		(store_sub, reg23, reg22, 1),
		(str_store_string, s21, "@+{reg21} base pay * {reg22} squad kill{reg23?s:}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(store_mul, ":pay", "$oathbound_bounty_count", OATHBOUND_BOUNTY_PAY),
		(val_add, ":total_base_pay", ":pay"),
		(call_script, "script_oath_convert_value_to_denars_string", ":pay", "str_oath_denar"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":pay"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		## TOTAL BASE PAY
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Total Base Pay:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(call_script, "script_oath_convert_value_to_denars_string", ":total_base_pay", "str_oath_denar"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":total_base_pay"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		
		###########################
		### PERCENT PAY FACTORS ###
		###########################
		(assign, ":total_percent_pay", 0),
		
		## Header
		(val_sub, ":pos_y", ":y_line_step"),
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Percent Pay Bonuses:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		
		## LINE 1 - RANK
		(val_sub, ":pos_y", ":y_header_step"),
		# Name
		(call_script, "script_oath_get_current_oathbound_rank"), # Stores reg1 (rank)
		(call_script, "script_oath_describe_oathbound_rank", reg1), # Stores s1 (rank name), s2 (rank title), reg0 (pay boost)
		(assign, ":bonus", reg0),
		(str_store_string, s21, "@Rank ({s1}):"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(str_store_string, s21, "@Rank varies from +0% to +400%"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(call_script, "script_oath_convert_value_to_denars_string", ":bonus", "str_oath_percent"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":bonus"),
		(assign, ":color", reg20),
		(val_add, ":total_percent_pay", ":bonus"),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_percent", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
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
				(str_store_string, s22, "@Personal"),
			(else_try),
				(party_get_skill_level, ":skill_level", "p_main_party", ":skill_no"),
				(str_store_string, s22, "@Party"),
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
			
			## LINE ? - SKILL ENTRY
			(val_sub, ":pos_y", ":y_line_step"),
			# Name
			(str_store_skill_name, s23, ":skill_no"),
			(assign, reg1, ":skill_level"),
			(str_store_string, s21, "@{s23} ({reg1}):"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			# Desc
			(assign, reg21, ":factor"),
			(str_store_string, s21, "@Grants +{reg21}% per {s22} rank"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			# Value
			(store_mul, ":bonus", ":skill_level", ":factor"),
			(call_script, "script_oath_convert_value_to_denars_string", ":bonus", "str_oath_percent"), # Returns s20 (value), reg20 (color code)
			(assign, reg21, ":bonus"),
			(assign, ":color", reg20),
			(val_add, ":total_percent_pay", ":bonus"),
			(str_store_string, s21, "@{reg21}"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
			(call_script, "script_gpu_resize_object", 0, 75),
			(overlay_set_color, reg1, ":color"),
			(str_store_string, s21, s20),
			(call_script, "script_gpu_create_text_label", "str_oath_percent", ":x_col_value_type", ":pos_y", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			(overlay_set_color, reg1, ":color"),
		(try_end),
		
		## LINE 10 - RENEWAL BONUS
		(val_sub, ":pos_y", ":y_line_step"),
		# Name
		(str_store_string, s21, "@Renewal Bonus:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(assign, reg21, "$oathbound_contract_periods"),
		(assign, reg22, OATHBOUND_RENEWAL_PAY_BOOST),
		(str_store_string, s21, "@{reg21} renewals for +{reg22}% each"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(store_mul, ":bonus", "$oathbound_contract_periods", OATHBOUND_RENEWAL_PAY_BOOST),
		(call_script, "script_oath_convert_value_to_denars_string", ":bonus", "str_oath_percent"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":bonus"),
		(assign, ":color", reg20),
		(val_add, ":total_percent_pay", ":bonus"),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_percent", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		## TOTAL PERCENT BONUS
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Total Percent Bonus:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(call_script, "script_oath_convert_value_to_denars_string", ":total_percent_pay", "str_oath_percent"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":total_percent_pay"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_percent", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		####################
		### FINAL TOTALS ###
		####################
		## Header
		(val_sub, ":pos_y", ":y_line_step"),
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Total Pay:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_heading", ":pos_y", 0, gpu_left),
		
		## LINE 2 - REPUTATION MULTIPLIER
		(val_sub, ":pos_y", ":y_line_step"),
		# Name
		(store_troop_faction, ":faction_no", "$oathbound_master"),
		(call_script, "script_oath_describe_reputation_with_faction", ":faction_no"), # Stores s1 (reputation text), reg1 (reputation value)
		(str_store_string, s29, s1),
		(assign, ":reputation", reg1),
		(call_script, "script_oath_get_reputation_pay_factor", ":reputation"), # Returns reg1 (value)
		(assign, ":reputation_multiplier", reg1),
		(str_store_string, s21, "@Reputation ({s29}):"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(str_store_string, s21, "@Reputation varies from -50% to +100%"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(call_script, "script_oath_convert_value_to_denars_string", ":reputation_multiplier", "str_oath_percent"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":reputation_multiplier"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_percent", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
		## TOTAL PAY
		(val_sub, ":pos_y", ":y_line_step"),
		(str_store_string, s21, "@Final Weekly Pay:"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_factor", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Desc
		(assign, reg21, ":total_base_pay"),
		(assign, reg22, ":total_percent_pay"),
		(str_store_string, s21, "@[({reg21} * {reg22}%) + {reg21}] * Reputation"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_desc", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		# Value
		(store_mul, ":bonus_pay", ":total_base_pay", ":total_percent_pay"),
		(val_div, ":bonus_pay", 100),
		(store_add, ":total_pay", ":total_base_pay", ":bonus_pay"),
		# Now tie in the reputation multiplier
		(store_mul, ":reputation_bonus", ":total_pay", ":reputation_multiplier"),
		(val_div, ":reputation_bonus", 100),
		(val_add, ":total_pay", ":reputation_bonus"),
		(call_script, "script_oath_convert_value_to_denars_string", ":total_pay", "str_oath_denar"), # Returns s20 (value), reg20 (color code)
		(assign, reg21, ":total_pay"),
		# Create global total_pay variable for payment system
		(assign, "$total_pay", ":total_pay"),
		(assign, ":color", reg20),
		(str_store_string, s21, "@{reg21}"),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value", ":pos_y", 0, gpu_right),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		(str_store_string, s21, s20),
		(call_script, "script_gpu_create_text_label", "str_oath_s21", ":x_col_value_type", ":pos_y", 0, gpu_left),
		(call_script, "script_gpu_resize_object", 0, 75),
		(overlay_set_color, reg1, ":color"),
		
      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
    ]),
  ]),
  
  
###########################################################################################################################
#####                                           EVENT LOG PRESENTATION                                                #####
###########################################################################################################################

("oathbound_event_log", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		## OBJ - HEADER REPLACEMENT - "History of Events"
		(str_store_string, s21, "@History of Events"),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title),
		(overlay_set_text, ":obj_no", s21),
		(troop_get_slot, ":obj_no", PRES_OBJECTS, oath_obj_main_title2),
		(overlay_set_text, ":obj_no", s21),
		
		(assign, ":y_bottom", 80),
		(assign, ":x_left",  250),
		(assign, ":x_width", 700),
		(assign, ":y_width", 515),
		
		## OBJ - CONTAINER+ - EMBLEM OPTIONS
		# (call_script, "script_gpu_draw_line", ":x_width", ":y_width", ":x_left", ":y_bottom", gpu_white), # - Footer
		(call_script, "script_gpu_container_heading", ":x_left", ":y_bottom", ":x_width", ":y_width", grt4_obj_container_1),
			
			(assign, ":pos_y", 475),
			(assign, ":y_line_step", 20),
			
			# Set minimum ":pos_y" based on event count.
			(store_mul, ":event_minimum", "$oathbound_events", ":y_line_step"),
			(val_max, ":pos_y", ":event_minimum"),
			
			(try_for_range, ":entry_no", 0, "$oathbound_events"),
				(call_script, "script_oath_get_log_entry", ":entry_no"), # returns s1 (event description)
				(str_store_string, s21, s1),
				(call_script, "script_gpu_create_text_label", "str_oath_s21", 5, ":pos_y", 0, gpu_left),
				(call_script, "script_gpu_resize_object", 0, 75),
				(val_sub, ":pos_y", ":y_line_step"),
			(try_end),
		(set_container_overlay, -1), ## CONTAINER- - EMBLEM OPTIONS

      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
    ]),
  ]),
  
  
###########################################################################################################################
#####                                           UNDEFINED PRESENTATION                                                #####
###########################################################################################################################

("oathbound_backup", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		# (assign, ":y_bottom", 80),
		# (assign, ":x_left",  250),
		# (assign, ":x_width", 700),
		# (assign, ":y_width", 515),
		
		# ## OBJ - CONTAINER+ - EMBLEM OPTIONS
		# # (call_script, "script_gpu_draw_line", ":x_width", ":y_width", ":x_left", ":y_bottom", gpu_white), # - Footer
		# (call_script, "script_gpu_container_heading", ":x_left", ":y_bottom", ":x_width", ":y_width", grt4_obj_container_1),
			
			# (assign, ":pos_y", 475),
			# (assign, ":y_line_step", 20),
			# (assign, ":x_desc", 110),
			# (assign, ":y_option_step", 70),
			
		# (set_container_overlay, -1), ## CONTAINER- - EMBLEM OPTIONS

      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
    ]),
  ]),
  

###########################################################################################################################
#####                                                  DEBUGGING                                                      #####
###########################################################################################################################

("oathbound_debugging", 0, mesh_load_window, [
    (ti_on_presentation_load,
      [
        (presentation_set_duration, 999999),
        (set_fixed_point_multiplier, 1000),
		
		(call_script, "script_oath_create_mode_switching_buttons"),
		
		(assign, ":y_bottom", 100),
		(assign, ":x_left",   250),
		(assign, ":x_width",  700),
		(assign, ":y_width",  495),
		
		## OBJ - CONTAINER+ - DEBUGGING OPTIONS
		# (call_script, "script_gpu_draw_line", ":x_width", ":y_width", ":x_left", ":y_bottom", gpu_white), # - Footer
		(call_script, "script_gpu_container_heading", ":x_left", ":y_bottom", ":x_width", ":y_width", grt4_obj_container_1),
		
			(assign, ":pos_y", 565),
			(val_sub, ":pos_y", 10),
			
			# Buttons
			(assign, ":x_left_button", 200),
			(assign, ":x_right_button", 400),
			(assign, ":y_button_step", 70),
			(assign, ":x_label_offset", -200),
			(assign, ":y_label_offset", 20),
			
			# Checkboxes
			(assign, ":x_checkboxes", 500),
			(assign, ":y_checkboxes", ":pos_y"),
			(assign, ":y_checkbox_step", 35),
			
			#############################
			# OPTION - RATING           #
			#############################
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Rating:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Rating
			(str_store_string, s21, "@+50"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_rating),
			
			# Option - Lose Rating
			(str_store_string, s21, "@-50"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_rating),
			
			
			#############################
			# OPTION - REPUTATION       #
			#############################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Reputation:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Reputation
			(str_store_string, s21, "@+5"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_reputation),
			
			# Option - Lose Reputation
			(str_store_string, s21, "@-5"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_reputation),
			
			################################
			# OPTION - CONTRACT TIME       #
			################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Contract Time:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Contract Time
			(str_store_string, s21, "@+5 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_contract_time),
			
			# Option - Lose Contract Time
			(str_store_string, s21, "@-5 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_contract_time),
			
			################################
			# OPTION - LEAVE TIME          #
			################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Time Since Leave:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Leave Time
			(str_store_string, s21, "@+4 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_leave_time),
			
			# Option - Lose Leave Time
			(str_store_string, s21, "@-4 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_leave_time),
			
			################################
			# OPTION - QUEST TIME          #
			################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Quest Durations:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Quest Time
			(str_store_string, s21, "@+5 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_quest_time),
			
			# Option - Lose Quest Time
			(str_store_string, s21, "@-5 Days"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_quest_time),
			
			#################################
			# OPTION - CANCEL ACTIVE QUESTS #
			#################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Cancel Quests:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Contract Time
			(str_store_string, s21, "@Cancel All"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_cancel_quests),
			
			################################
			# OPTION - BOUNTY COUNT        #
			################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Bounty Count:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Quest Time
			(str_store_string, s21, "@+5 Kills"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_kill_bounty),
			
			# Option - Lose Quest Time
			(str_store_string, s21, "@-5 Kills"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_kill_bounty),
			
			################################
			# OPTION - RENEWAL COUNT       #
			################################
			(val_sub, ":pos_y", ":y_button_step"),
			(store_add, ":pos_x_temp", ":x_left_button", ":x_label_offset"),
			(store_add, ":pos_y_temp", ":pos_y", ":y_label_offset"),
			(str_store_string, s21, "@Contract Renewals:"),
			(call_script, "script_gpu_create_text_label", "str_oath_s21", ":pos_x_temp", ":pos_y_temp", 0, gpu_left),
			(call_script, "script_gpu_resize_object", 0, 75),
			
			# Option - Gain Quest Time
			(str_store_string, s21, "@+1 Period"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_left_button", ":pos_y", oath7_obj_option_gain_contract_periods),
			
			# Option - Lose Quest Time
			(str_store_string, s21, "@-1 Period"),
			(call_script, "script_gpu_create_game_button", "str_oath_s21", ":x_right_button", ":pos_y", oath7_obj_option_lose_contract_periods),
			
			############################
			# CHECKBOX - LEAVE GRANTED #
			############################
			(str_store_string, s21, "@On Leave"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_leave_granted, "$oathbound_leave_granted"),
			(call_script, "script_gpu_create_checkbox", ":x_checkboxes", ":y_checkboxes", "str_oath_s21", oath7_obj_checkbox_leave_granted, oath7_val_checkbox_leave_granted),
			
			###########################
			# CHECKBOX - EXIT ALLOWED #
			###########################
			(val_sub, ":y_checkboxes", ":y_checkbox_step"),
			(str_store_string, s21, "@Exit Allowed"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_exit_allowed, "$oathbound_exit_allowed"),
			(call_script, "script_gpu_create_checkbox", ":x_checkboxes", ":y_checkboxes", "str_oath_s21", oath7_obj_checkbox_exit_allowed, oath7_val_checkbox_exit_allowed),
			
			###########################
			# CHECKBOX - FIEF PAUSING #
			###########################
			(val_sub, ":y_checkboxes", ":y_checkbox_step"),
			(str_store_string, s21, "@Pause at Fiefs"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_fief_pausing, "$oathbound_pause_at_fiefs"),
			(call_script, "script_gpu_create_checkbox", ":x_checkboxes", ":y_checkboxes", "str_oath_s21", oath7_obj_checkbox_fief_pausing, oath7_val_checkbox_fief_pausing),
			
			
		(set_container_overlay, -1), ## CONTAINER- - DEBUGGING OPTIONS

      ]),

    (ti_on_presentation_run,
	  [
		(try_begin),
			(key_clicked, key_escape),
			(call_script, "script_cf_oath_allow_return_to_map"),
			(assign, "$oathbound_mode", OATH_MODE_RETURN_TO_MAP),
			(presentation_set_duration, 0),
			(jump_to_menu, "mnu_oathbound_switch_modes"),
		(try_end), 
	  ]),  
	
    (ti_on_presentation_event_state_change,
      [
        (store_trigger_param_1, ":object"),
        (store_trigger_param_2, ":value"),
		
		(call_script, "script_oath_handle_mode_switching_buttons", ":object", ":value"),
		
		(try_begin), ### BUTTON - GAIN 50 RATING ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_rating, ":object"),
			(call_script, "script_oath_change_oathbound_rating", 50),
			
		(else_try), ### BUTTON - LOSE 50 RATING ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_rating, ":object"),
			(call_script, "script_oath_change_oathbound_rating", -50),
			
		(else_try), ### BUTTON - GAIN 5 REPUTATION ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_reputation, ":object"),
			(call_script, "script_oath_change_oathbound_reputation", 5),
			
		(else_try), ### BUTTON - LOSE 5 REPUTATION ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_reputation, ":object"),
			(call_script, "script_oath_change_oathbound_reputation", -5),
			
		(else_try), ### BUTTON - GAIN 5 DAYS CONTRACT TIME ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_contract_time, ":object"),
			(val_add, "$oathbound_remaining_hours", 24*5),
			(call_script, "script_oath_convert_hours_to_description", "$oathbound_remaining_hours", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
			(display_message, "@DEBUG (Oathbound): Your remaining contract time is now: {s1}", gpu_debug),
			
		(else_try), ### BUTTON - LOSE 5 DAYS CONTRACT TIME ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_contract_time, ":object"),
			(val_sub, "$oathbound_remaining_hours", 24*5),
			(val_max, "$oathbound_remaining_hours", 1), # So we don't have a negative time.
			(call_script, "script_oath_convert_hours_to_description", "$oathbound_remaining_hours", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
			(display_message, "@DEBUG (Oathbound): Your remaining contract time is now: {s1}", gpu_debug),
			
		(else_try), ### BUTTON - GAIN 4 DAYS LEAVE TIME ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_leave_time, ":object"),
			(val_add, "$oathbound_time_since_leave", 24*4),
			(call_script, "script_oath_convert_hours_to_description", "$oathbound_time_since_leave", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
			(display_message, "@DEBUG (Oathbound): Your since you last returned from leave is now: {s1}", gpu_debug),
			(try_begin),
				(ge, "$oathbound_time_since_leave", OATHBOUND_MIN_TIME_BETWEEN_LEAVE),
				(display_message, "@DEBUG (Oathbound): You may now go on leave.", gpu_green),
			(try_end),
			
		(else_try), ### BUTTON - LOSE 4 DAYS LEAVE TIME ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_leave_time, ":object"),
			(val_sub, "$oathbound_time_since_leave", 24*4),
			(val_max, "$oathbound_time_since_leave", 0), # So we don't have a negative time.
			(call_script, "script_oath_convert_hours_to_description", "$oathbound_time_since_leave", OATHBOUND_CONTRACT_TIME), # Stores s1 (remaining time)
			(display_message, "@DEBUG (Oathbound): Your since you last returned from leave is now: {s1}", gpu_debug),
			
		(else_try), ### BUTTON - GAIN 5 DAYS QUEST DURATION ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_quest_time, ":object"),
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(check_quest_active, ":quest_no"),
				(quest_slot_ge, ":quest_no", slot_quest_expiration_days, 1), # It actually has duration.
				(quest_get_slot, ":days_left", ":quest_no", slot_quest_expiration_days),
				(val_add, ":days_left", 5),
				(quest_set_slot, ":quest_no", slot_quest_expiration_days, ":days_left"),
				## Display
				(str_store_quest_name, s21, ":quest_no"),
				(assign, reg21, ":days_left"),
				(display_message, "@DEBUG (Oathbound): Quest '{s21}' expiration now set to {reg21} day(s). (Added Time)", gpu_debug),
			(try_end),
			
		(else_try), ### BUTTON - LOSE 5 DAYS QUEST DURATION ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_quest_time, ":object"),
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(check_quest_active, ":quest_no"),
				(str_store_quest_name, s21, ":quest_no"),
				(try_begin),
					(neg|quest_slot_ge, ":quest_no", slot_quest_expiration_days, 1), # It has no duration.
					(display_message, "@DEBUG (Oathbound): Quest '{s21}' ignored.  It has no duration.", gpu_debug),
				(try_end),
				(quest_slot_ge, ":quest_no", slot_quest_expiration_days, 1), # It actually has duration.
				(quest_get_slot, ":days_left", ":quest_no", slot_quest_expiration_days),
				(val_sub, ":days_left", 5),
				(val_max, ":days_left", 1), # I still want the normal failure code to kick in.
				(quest_set_slot, ":quest_no", slot_quest_expiration_days, ":days_left"),
				## Display
				(assign, reg21, ":days_left"),
				(display_message, "@DEBUG (Oathbound): Quest '{s21}' expiration now set to {reg21} day(s). (Removed Time)", gpu_debug),
			(try_end),
			
		(else_try), ### BUTTON - CANCEL ACTIVE QUESTS ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_cancel_quests, ":object"),
			(display_message, "@DEBUG (Oathbound): All active quests are being cancelled.", gpu_debug),
			(try_for_range, ":quest_no", OATHBOUND_QUESTS_BEGIN, OATHBOUND_QUESTS_END),
				(check_quest_active, ":quest_no"),
				(call_script, "script_oath_cancel_quest_if_active", ":quest_no"),
				(quest_set_slot, ":quest_no", slot_quest_dont_give_again_period, 0),
				(quest_set_slot, ":quest_no", slot_quest_dont_give_again_remaining_days, 0),
			(try_end),
			
		(else_try), ### BUTTON - GAIN 5 CONTRACT KILLS ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_kill_bounty, ":object"),
			(val_add, "$oathbound_bounty_count", 5),
			(assign, reg21, "$oathbound_bounty_count"),
			(display_message, "@DEBUG (Oathbound): Your bounty count is now set to: {reg21}", gpu_debug),
			
		(else_try), ### BUTTON - LOSE 5 CONTRACT KILLS ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_kill_bounty, ":object"),
			(val_sub, "$oathbound_bounty_count", 5),
			(val_max, "$oathbound_bounty_count", 1), # So we don't have a negative value.
			(assign, reg21, "$oathbound_bounty_count"),
			(display_message, "@DEBUG (Oathbound): Your bounty count is now set to: {reg21}", gpu_debug),
			
		(else_try), ### BUTTON - GAIN 1 CONTRACT PERIOD ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_gain_contract_periods, ":object"),
			(val_add, "$oathbound_contract_periods", 1),
			(assign, reg21, "$oathbound_contract_periods"),
			(display_message, "@DEBUG (Oathbound): Your consecutive contract periods is set to: {reg21}", gpu_debug),
			
		(else_try), ### BUTTON - LOSE 1 CONTRACT PERIOD ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_option_lose_contract_periods, ":object"),
			(val_sub, "$oathbound_contract_periods", 1),
			(val_max, "$oathbound_contract_periods", 0), # So we don't have a negative value.
			(assign, reg21, "$oathbound_contract_periods"),
			(display_message, "@DEBUG (Oathbound): Your consecutive contract periods is set to: {reg21}", gpu_debug),
			
		(else_try), ### CHECKBOX - LEAVE GRANTED ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_checkbox_leave_granted, ":object"),
			(assign, "$oathbound_leave_granted", ":value"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_leave_granted, ":value"),
			(start_presentation, "prsnt_oathbound_debugging"),
			(assign, reg1, "$oathbound_leave_granted"),
			(display_message, "@DEBUG (Oathbound): Your leave status is now {reg1?APPROVED:DENIED}.", gpu_debug),
			
		(else_try), ### CHECKBOX - EXIT ALLOWED ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_checkbox_exit_allowed, ":object"),
			(assign, "$oathbound_exit_allowed", ":value"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_exit_allowed, ":value"),
			(start_presentation, "prsnt_oathbound_debugging"),
			(assign, reg1, "$oathbound_exit_allowed"),
			(display_message, "@DEBUG (Oathbound): Permission to leave the army is {reg1?ALLOWED:DENIED}.", gpu_debug),
			
		(else_try), ### CHECKBOX - FIEF PAUSING ###
			(troop_slot_eq, PRES_OBJECTS, oath7_obj_checkbox_fief_pausing, ":object"),
			(assign, "$oathbound_pause_at_fiefs", ":value"),
			(troop_set_slot, PRES_OBJECTS, oath7_val_checkbox_fief_pausing, ":value"),
			(start_presentation, "prsnt_oathbound_debugging"),
			(assign, reg1, "$oathbound_pause_at_fiefs"),
			(display_message, "@DEBUG (Oathbound): Triggering the oathbound interface when visiting fiefs has been {reg1?ENABLED:disabled}.", gpu_debug),
			
		(try_end),
    ]),
  ]),
 ]
	
def modmerge_presentations(orig_presentations, check_duplicates = False):
    if( not check_duplicates ):
        orig_presentations.extend(presentations) # Use this only if there are no replacements (i.e. no duplicated item names)
    else:
    # Use the following loop to replace existing entries with same id
        for i in range (0,len(presentations)-1):
          find_index = find_object(orig_presentations, presentations[i][0]); # find_object is from header_common.py
          if( find_index == -1 ):
            orig_presentations.append(presentations[i])
          else:
            orig_presentations[find_index] = presentations[i]

# Used by modmerger framework version >= 200 to merge stuff
def modmerge(var_set):
    try:
        var_name_1 = "presentations"
        orig_presentations = var_set[var_name_1]
        modmerge_presentations(orig_presentations)
    except KeyError:
        errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
        raise ValueError(errstring)