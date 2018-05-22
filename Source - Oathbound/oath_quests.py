# Oathbound by Windyplains
# Basis from Freelancer by Taragoth & Caba'drin.

from header_quests import *

quests = [

###########################################################################################################################
#####                                               OATHBOUND QUESTS                                                  #####
###########################################################################################################################

  # ### QUEST: A FREEMAN'S RETURN ###
  # # Trigger: Dialog triggered if you pay to free the fugitive in "qst_hunt_down_fugitive" and agree to escort him home.
  # # Desc:    Simple escort to location & drop off.
  # ("qp7_freemans_return", "A Freeman's Return", 0,
  # "{!}You have agreed to escort your freed prisoner back to his home village."),
  
  ### QUEST: DESERTION ###
  # Trig: You actively choose to leave your lord without leave via the main menu.
  # Trig: You fail to return from granted leave before time expires.
  # Trig: You fail to return from a mission before time expires.
  # Desc: You're now branded as a deserter until you either agree to finish your contracted time, pay off your contract
  #       or completely desert for further penalties.
  ("oath_desertion", 	"Desertion", 0,
  "{!}You have been branded a deserter and must choose to return or evade capture."),
  
  ### QUEST: SEPARATED ###
  # Trig: Your lord's army is defeated while you are in it.
  # Trig: Your lord is held captive when your leave or mission expires.
  # Desc: No expiration is used.  This simply tracks the status so the player can see it.
  ("oath_separated", 	"Separated", 0,
  "{!}You have been separated from your lord's party."),
  
  ### QUEST: PRISONERS OF WAR ###
  # Trig: Oathbound Quest - Rank 1+
  ("oath_prisoners_of_war", "Prisoners of War", 0,
  "{!}Your lord wishes to gather a number of prisoners for a future exchange and wishes you to incapacitate 25 troops from a specific faction.  You must use a blunt weapon to ensure they are merely incapacitated."),
  
  ### QUEST: LEAVE OF DUTY ###
  # Trig: You ask for and are granted permission to leave the army on vacation.
  # Desc: This quest gives the player a way of seeing how much time he has left while on leave before desertion status kicks in.
  ("oath_leave", "Leave of Duty", 0,
  "{!}You have been granted permission to take a leave of duty travelling the world freely."),
  
  ### QUEST: THE BUTCHER'S BILL ###
  # Trig: Oathbound Quest - Rank 2+
  ("oath_butchers_bill", "The Butcher's Bill", 0,
  "{!}You have been sent with funds to purchase cattle from a nearby village and return with the herd to resupply the army."),
  
  ### QUEST: THE SEALED LETTER ###
  # Trig: Oathbound Quest - Rank 2+
  ("oath_sealed_letter", "The Sealed Letter", 0,
  "{!}You have been tasked with delivering a sealed letter to another lord and then returning with the response."),
  
  ### QUEST: COURAGE COMES IN CASKS ###
  # Trig: Oathbound Quest - Rank 2+
  ("oath_courage_casks", "Courage Comes in Casks", 0,
  "{!}You have been sent with coin to purchase ale from a nearby village and return with the casks to resupply the army."),
  
  ### QUEST: SCOUTING AHEAD ###
  # Trig: Oathbound Quest - Rank 2+
  ("oath_scouting_ahead", "Scouting Ahead", 0,
  "{!}You have been tasked with scouting ahead of the main army."),
  
  ### QUEST: ONLY THE FINEST ###
  # Trig: Oathbound Quest - Rank 2+
  ("oath_only_the_finest", "Only the Finest", 0,
  "{!}You have been tasked with having an item commissioned for your lord and returning with it once it is complete."),
  
  ### QUEST: MAKE YOUR MARK ###
  # Trig: Oathbound Quest - Rank 3+
  ("oath_make_your_mark", "Make Your Mark", 0,
  "{!}You have been tasked with gathering several new recruits for your lord's army."),
  
  ("oath_reserved_11", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_12", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  
  ### QUEST: FRESH MEAT ###
  # Trig: Oathbound Quest - Rank 3+
  ("oath_fresh_meat", "Fresh Meat", 0,
  "{!}You have been tasked with training several of our new recruits when we stop for camp at night."),
  
  ("oath_reserved_14", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_15", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_16", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_17", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_18", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_19", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_20", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_21", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_22", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_23", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_24", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_25", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_26", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_27", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_28", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_29", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ("oath_reserved_30", "Reserved Oathbound Quest", 0,
  "{!}Quest Description"),
  ## END OF OATHBOUND QUESTS
  ("oath_quests_end", "END OF OATHBOUND QUESTS", 0,
  "{!}Quest Description"),
  
]

from util_common import *
from util_wrappers import *
def modmerge_quests(orig_quests):
	## QUEST PACKS 2, 3, 4 & 6
	pos = list_find_first_match_i(orig_quests, "quests_end")
	OpBlockWrapper(orig_quests).InsertBefore(pos, quests)
	# ## QUEST PACK 5 - VILLAGE QUESTS
	# pos = list_find_first_match_i(orig_quests, "eliminate_bandits_infesting_village")
	# OpBlockWrapper(orig_quests).InsertBefore(pos, quest_pack_5)	
	
def modmerge(var_set):
    try:
        var_name_1 = "quests"
        orig_quests = var_set[var_name_1]
        modmerge_quests(orig_quests)
    except KeyError:
        errstring = "Variable set does not contain expected variable: \"%s\"." % var_name_1
        raise ValueError(errstring)