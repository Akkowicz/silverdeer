# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from module_constants import *

##################################
###      GLOBAL VARIABLES      ###
##################################

## OATHBOUND STATUS
# $oathbound_status 			= (Const)	- This tracks the main status of your contract via a constant.
OATHBOUND_STATUS_NOT_HIRED  = 0				# No contract in effect.
OATHBOUND_STATUS_CONTRACTED = 1				# On contract, within the lord's party.
OATHBOUND_STATUS_AWAY       = 2				# Away from the party on a mission or during periods of leave.
OATHBOUND_STATUS_SEPARATED  = 3				# Separated due to lord being captured.
OATHBOUND_STATUS_DESERTER   = 4				# Desertion status.
OATHBOUND_STATUS_END        = 5				# This needs to be +1 from the last status used.

# $oathbound_master 			= (Troop #)	- Tracks the lord you have entered into a contract with.
# $oathbound_party				= (Party #) - Tracks the party number you have joined.
# $oathbound_exit_allowed 		= (Boolean)	- Tracks if you can leave the party at all.
# $oathbound_reputation         = (Int)		- Measures how well you hold up to your contracts across all factions.
# $oathbound_contract_started	= (Int)		- The hour in game you began your contract.
# $oathbound_remaining_hours	= (Int)		- The number of hours remaining on your contract.  Constantly works towards 0 unless away.
# $oathbound_debugging          = (Boolean) - Turns on or off oathbound related debugging messages.
# $oathbound_leave_granted		= (Boolean) - Tracks if you were granted vacation or not to differentiation leave vs. mission in AWAY status.
# $oathbound_betrayed_faction	= (Boolean)	- Tracks if you have betrayed your current contracted faction.
# $oathbound_time_since_leave	= (Boolean)	- Tracks the hours since you last returned from leave.
# $oathbound_pause_at_fiefs		= (Boolean)	- Mod Option: Causes the Oathbound Interface to pop up if $oathbound_party is visiting somewhere.
# $oathbound_hours_since_visit	= (Int)		- Tied to the "pause_at_fiefs" option.  This timer prevents us constantly trying to trigger the Oathbound interface.
# $oathbound_mode				= (Const)	- Tracks the current mode from the constants below for our oathbound interface hub.
OATH_MODE_CONTRACT_INFO			= 0			# Display general contract information for the current faction.
OATH_MODE_COMMANDER_AUDIENCE	= 1			# Setup a conversation with $oathbound_master.
OATH_MODE_JOIN_BATTLE			= 2			# Join $oathbound_party in battle.
OATH_MODE_ENTER_LOCATION		= 3			# Enter $current_town where $oathbound_party is attached.
OATH_MODE_OATHBOUND_REFERENCE	= 4			# Reference information for the system on things like ranking.
OATH_MODE_PAY_INFORMATION		= 5			# Breakdown why you get paid what you do.
OATH_MODE_DESERT				= 6			# Abandon the $oathbound_party.
OATH_MODE_DEBUGGING				= 7			# Entering a debugging interface.
OATH_MODE_MANAGE_COMPANIONS		= 8			# Manage companion dialogs while on map.
OATH_MODE_RETURN_TO_MAP			= 9			# Returns to following $oathbound_party.
OATH_MODE_QUEST_SELECTION		= 10		# Quest Selector
OATH_MODE_EVENT_LOG				= 11		# Event log interface.

# $oathbound_waypoint_1			= (Party #)	- Tracks the first waypoint in quest "oath_scouting_ahead".
# $oathbound_waypoint_2			= (Party #)	- Tracks the second waypoint in quest "oath_scouting_ahead".
# $oathbound_waypoint_3			= (Party #)	- Tracks the third waypoint in quest "oath_scouting_ahead".
# $oathbound_waypoint_1_visited	= (Boolean)	- Tracks if you have scouted the first waypoint in quest "oath_scouting_ahead".
# $oathbound_waypoint_2_visited	= (Boolean)	- Tracks if you have scouted the second waypoint in quest "oath_scouting_ahead".
# $oathbound_waypoint_3_visited	= (Boolean)	- Tracks if you have scouted the third waypoint in quest "oath_scouting_ahead".
# $oathbound_events				= (Int)		- Tracks how many events are captured in the Oathbound Event Log.
# $oathbound_bounty_count		= (Int)		- Tracks how many enemies you or your men dispatch within a pay cycle for bonuses.
# $oathbound_contract_periods	= (Int)		- This counts up each time you renew your contract with the same lord.  It alters your pay.


####################################
###      SLOT DECLARATIONS       ###
####################################
## FACTION SLOTS
slot_faction_oathbound_rank			= 280	# (Int) 	- Represents your current rank within that faction.
# Ranks
OATHBOUND_RANK_NONE					= 0
OATHBOUND_RANK_INITIATE				= 1
OATHBOUND_RANK_MILITIA				= 2
OATHBOUND_RANK_SERGEANT				= 3
OATHBOUND_RANK_CAPTAIN				= 4
OATHBOUND_RANK_GREAT_CAPTAIN		= 5
OATHBOUND_RANK_HEDGE_KNIGHT			= 6
OATHBOUND_RANK_ELDER_KNIGHT			= 7
OATHBOUND_RANK_VASSAL_KNIGHT		= 8
OATHBOUND_RANK_END					= 9

slot_faction_oathbound_rating		= 281	# (Int)		- Your rating determines your rank.  Think of it like experience versus your level.
# Rating Requirements
OATHBOUND_RATING_INITIATE			= 0
OATHBOUND_RATING_MILITIA			= 30
OATHBOUND_RATING_SERGEANT			= 80
OATHBOUND_RATING_CAPTAIN			= 190
OATHBOUND_RATING_GREAT_CAPTAIN		= 300
OATHBOUND_RATING_HEDGE_KNIGHT		= 500
OATHBOUND_RATING_ELDER_KNIGHT		= 1000
OATHBOUND_RATING_VASSAL_KNIGHT		= 1500

slot_faction_oathbound_reputation	= 282	# (Int)		- This tracks how a faction feels about your trustworthiness.
slot_faction_oathbound_betrayals	= 283	# (Int)		- This is how many times you have betrayed this faction.
slot_faction_oathbound_renewals		= 284	# (Int)		- This is how many times you renewed your contract with this faction.
slot_faction_oathbound_high_rank	= 285	# (Int)		- This mirrors your faction rank to prevent demotion/promotion exploits for emblems.


## TROOP SLOTS
slot_troop_in_player_merc_group		= 159	# (Boolean) - Tracks if companions were part of the player's party so they aren't lost when joined.

## QUEST SLOTS
slot_quest_unique_script			= 40	# (Script)	- Holds the script ID of the unique script that handles this quest's functions.m


####################################
###       MISC CONSTANTS         ###
####################################
# PLAYER_PARTY_BACKUP					= "p_Freelancer_Reserved_1"
OATHBOUND_TROOP_COMPENSATION_RATE	= 50	# (Int, %)	- The percentage of a troop's cost you'll get back when your troops are absorbed.
OATHBOUND_PRISONER_COMPENSATION		= 50	# (Int, %)	- The percentage of a prisoner's value you'll get when your prisoners are absorbed.
OATHBOUND_CONTRACT_DURATION			= 24*30	# (Int)		- The number of hours each contract period represents.
OATHBOUND_BATTLE_DESERTION_CHANCE   = 55    # (Int, %)	- This is the cumulative percent chance that you'll be branded a deserter if you attack your oathbound faction.
OATHBOUND_VALUE_RESET				= 99999 # (Int)		- Used in the change rating / reputation scripts to reset them back to 0.
OATHBOUND_BASE_PAY_VALUE			= 150	# (Int)		- This is the most basic rate of pay that you'll receive.
OATHBOUND_MIN_TIME_BETWEEN_LEAVE	= 24*8	# (Int)		- This sets the minimum time required in service before you can go on leave again.
OATHBOUND_BOUNTY_PAY				= 4		# (Int)		- This is how much your weekly base pay is increased per troop you and your men kill off while CONTRACTED.  Works with $oathbound_bounty_count.
OATHBOUND_BOUNTY_RATING_DIVISOR		= 10	# (Int)		- This is how many enemies you and your men must dispatch per +1 rating increase.
OATHBOUND_RENEWAL_PAY_BOOST			= 20	# (Int)		- This is how much % bonus you get to your pay for each consecutive contract period.
OATHBOUND_MIN_REPUTATION_ALLOWED	= -74	# (Int)		- You cannot be hired below this reputation.  You will be fired below this reputation.

# SCRIPT FUNCTIONS: script_oath_player_faction_relations
OATHBOUND_FACTION_CLEAR_RELATIONS	= 1		# Clears your relations with other factions when leaving service or going AWAY.
OATHBOUND_ESTABLISH_MASTER_RELATIONS= 2		# Sets your faction relations so that you can join battles for $oathbound_party.

# SCRIPT FUNCTIONS: script_oath_convert_hours_to_description
OATHBOUND_CONTRACT_HOURS			= 0		# 
OATHBOUND_CONTRACT_DAYS				= 1		# 
OATHBOUND_CONTRACT_MONTHS			= 2		# 
OATHBOUND_CONTRACT_TIME				= 3		# 

# SCRIPT FUNCTIONS: script_oath_get_random_lord
OATHBOUND_LORD_PREF_ENEMY_LORD		= 1
OATHBOUND_LORD_PREF_FRIENDLY_LORD	= 2
OATHBOUND_LORD_PREF_ANY_LORD		= 3
OATHBOUND_LORD_PREF_ENEMY_RULER		= 4
OATHBOUND_LORD_PREF_FRIENDLY_RULER	= 5
OATHBOUND_LORD_PREF_ANY_RULER		= 6

# SCRIPT FUNCTIONS: script_cf_oath_kingdom_status_is
OATHBOUND_KINGDOM_STATUS_WAR		= 1
OATHBOUND_KINGDOM_STATUS_PEACE		= 2


##############################################################################################################################################
####################                                           OATHBOUND QUESTS                                           ####################
##############################################################################################################################################

OATHBOUND_QUESTS_BEGIN				= "qst_oath_desertion"
OATHBOUND_QUESTS_END				= "qst_oath_quests_end"
# General Script Parameter
OATH_QUEST_BEGIN					= 1  # Initializes quest parameters and begins the quest.
OATH_QUEST_UPDATE					= 2  # Used to update the quest log.
OATH_QUEST_SUCCEED					= 3  # Will cause specific quest to succeed with rewards.
OATH_QUEST_FAIL						= 4  # Will cause specific quest to fail with consequences.
OATH_QUEST_CANCEL					= 5  # Will cause specific quest to fail without consequence.
OATH_QUEST_STORY_ARC_CHECK			= 6  # Will check to see if the main story arc quest should fail or continue.  Intended for use as a check after failing any sub-quest.
OATH_QUEST_RESET_DURATION			= 7  # Will reset the main story arc quest's duration whenever a sub-quest is completed.
OATH_QUEST_STORYLINE_FAILURE		= 8  # Triggered by simple trigger whenever story line has failed.  Sets up companion leaving.
OATH_QUEST_SETUP					= 9  # Used for initializing parameters prior to starting a quest.
OATH_QUEST_VICTORY_CONDITION		= 10 # Used by some quests to verify victory conditions met.
OATH_QUEST_FAILURE_CONDITION		= 11 # Used by some quests to verify failure conditions met.
OATH_QUEST_PREREQUISITES			= 12 # Used by some quests to establish prerequisite conditions before they can be listed.

###########################################################
# COMMON QUEST STATES FOR SIMPLE QUESTS                   #
###########################################################
# Relevant quests: qst_oath_desertion, qst_oath_separation, qst_oath_prisoners_of_war, qst_oath_leave
# Active states
OATH_QUEST_STAGE_INACTIVE			= 0
OATH_QUEST_STAGE_BEGUN				= 1
OATH_QUEST_STAGE_GOAL_MET			= 2

# ###########################################################
# # QUEST #6: The Sealed Letter                             #
# ###########################################################
# # Active states
OATH_SEALED_LETTER_INACTIVE			= 0
OATH_SEALED_LETTER_BEGUN			= 1
OATH_SEALED_LETTER_DELIVERED		= 2


##############################################################################################################################################
####################                                  OATHBOUND PRESENTATION CONSTANTS                                    ####################
##############################################################################################################################################
PRES_OBJECTS						= "trp_tpe_presobj"

### UI - CORE ELEMENTS ###
oath_obj_main_title					= 1
oath_obj_button_return_to_map		= 2
oath_obj_main_title2				= 3
oath_obj_container_left_buttons		= 4
oath_obj_button_debugging			= 5
oath_obj_button_contract_info		= 6
oath_obj_button_commander_audience	= 7
oath_obj_button_join_battle			= 8
oath_obj_button_enter_location		= 9
oath_obj_button_manage_companions	= 10
oath_obj_button_reference			= 11
oath_obj_button_pay_info			= 12
oath_obj_button_desert				= 13
oath_obj_label_hit_escape			= 14
oath_obj_button_quest_selector		= 15
oath_obj_button_event_log			= 16


### UI #1 - CONTRACT INFORMATION ###
oath1_obj_portrait_oathbound_master	= 100


### UI #7 - DEBUGGING ###
oath7_obj_option_gain_rating		= 100
oath7_obj_option_lose_rating		= 101
oath7_obj_option_gain_reputation	= 102
oath7_obj_option_lose_reputation	= 103
oath7_obj_option_gain_contract_time	= 104
oath7_obj_option_lose_contract_time = 105
oath7_obj_checkbox_leave_granted	= 106
oath7_val_checkbox_leave_granted	= 107
oath7_obj_checkbox_exit_allowed		= 108
oath7_val_checkbox_exit_allowed		= 109
oath7_obj_option_gain_leave_time	= 110
oath7_obj_option_lose_leave_time	= 111
oath7_obj_option_gain_quest_time	= 112
oath7_obj_option_lose_quest_time	= 113
oath7_obj_checkbox_fief_pausing		= 114
oath7_val_checkbox_fief_pausing		= 115
oath7_obj_option_cancel_quests		= 116
oath7_obj_option_gain_kill_bounty	= 117
oath7_obj_option_lose_kill_bounty	= 118
oath7_obj_option_gain_contract_periods = 119
oath7_obj_option_lose_contract_periods = 120


### UI #10 - QUEST SELECTION ###
oath10_obj_button_quest_no			= 200	# These slots hold the button object # for each quest.
oath10_val_button_quest_no			= 300	# These slots hold the quest # associated with that button.


##############################################################################################################################################
####################                                         OATHBOUND EVENT LOG                                          ####################
##############################################################################################################################################
OATHBOUND_EVENT_LOG					= "str_oath_file_event_log"

# EVENT TYPES:
OATHBOUND_EVENT_UNDEFINED			= 0
OATHBOUND_EVENT_QUEST_COMPLETION	= 1		# (Focus = Quest #)
OATHBOUND_EVENT_QUEST_FAILURE		= 2		# (Focus = Quest #)
OATHBOUND_EVENT_REPUTATION_CHANGE	= 3		# (Focus = Change Value)
OATHBOUND_EVENT_RATING_CHANGE		= 4		# (Focus = Change Value)
OATHBOUND_EVENT_RANK_CHANGE			= 5		# (Focus = Change Value)
OATHBOUND_EVENT_STATUS_CHANGE		= 6		# (Focus = New Status)
OATHBOUND_EVENT_CONTRACT_RENEWAL	= 7		# (Focus = N/A)
OATHBOUND_EVENT_JOINED_SIEGE		= 8		# (Focus = Party #)
OATHBOUND_EVENT_DEFENDED_SIEGE		= 9		# (Focus = Party #)
OATHBOUND_EVENT_GLOBAL_REPUTATION	= 10	# (Focus = Change Value)
