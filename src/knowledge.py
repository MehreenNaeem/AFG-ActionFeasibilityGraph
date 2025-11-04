squeezable_objects = [
            "cleaning_solution",
            "tooth_paste",
            "shampoo",
            "food_peanut_butter",
            "dish_soap",
            "soap",
            "towel",
            "rag",
            "paper",
            "sponge",
            "food_lemon",
            "check",
        ]
action_for_sp_objects = {
    'SQUEEZE': squeezable_objects
}
action_for_obj_cat = {
    'TYPE': 'electronics'
}

planner_vlb= {
    "tl_predicates_to_vh": {
        "GRABBABLE": "GRABBABLE",
        "CUTTABLE": "CUTTABLE",
        "CAN_OPEN": "CAN_OPEN",
        "READABLE": "READABLE",
        "HAS_PAPER": "HAS_PAPER",
        "MOVABLE": "MOVABLE",
        "POURABLE": "POURABLE",
        "CREAM": "CREAM",
        "HAS_SWITCH": "HAS_SWITCH",
        "LOOKABLE": "LOOKABLE",
        "HAS_PLUG": "HAS_PLUG",
        "DRINKABLE": "DRINKABLE",
        "BODY_PART": "BODY_PART",
        "RECIPIENT": "RECIPIENT",
        "CONTAINERS": "CONTAINERS",
        "COVER_OBJECT": "COVER_OBJECT",
        "SURFACES": "SURFACES",
        "SITTABLE": "SITTABLE",
        "LIEABLE": "LIEABLE",
        "PERSON": "PERSON",
        "HANGABLE": "HANGABLE",
        "CLOTHES": "CLOTHES",
        "EATABLE": "EATABLE",
        "CLOSED": "CLOSED",
        "OPEN": "OPEN",
        "ON": "ON",
        "OFF": "OFF",
        "SITTING": "SITTING",
        "DIRTY": "DIRTY",
        "CLEAN": "CLEAN",
        "LYING": "LYING",
        "PLUGGED_IN": "PLUGGED_IN",
        "PLUGGED_OUT": "PLUGGED_OUT",
        "ONTOP": "ON",
        "OBJ_INSIDE": "INSIDE",
        "BETWEEN": "BETWEEN",
        "NEXT_TO": "CLOSE",
        "FACING": "FACING",
        "HOLDS_RH": "HOLDS_RH",
        "HOLDS_LH": "HOLDS_LH"
    },
    'tl_actions_to_vh':{
    "DRINK": ("DRINK", 1),  # executable : (pred_cond_name,num_parm)
    "EAT": ("EAT", 1),
    "CUT": ("CUT", 1),
    "TOUCH": ("TOUCH", 1),
    "LOOKAT": ("LOOK_AT", 1),
    "WATCH": ("WATCH", 1),
    "READ": ("READ", 1),
    "TYPE": ("TYPE", 1),
    "SQUEEZE": ("SQUEEZE", 1),
    "SLEEP": ("SLEEP", 1),
    "WAKEUP": ("WAKEUP", 1),
    "WASH": ("WASH", 1),
    "GRAB": ("GRAB", 1),
    "SWITCHOFF": ("SWITCH_OFF", 1),
    "SWITCHON": ("SWITCH_ON", 1),
    "CLOSE": ("CLOSE", 1),
    "FIND": ("FIND", 1),
    "WALK": ("WALK_TOWARDS", 1),
    "OPEN": ("OPEN", 1),
    "POINTAT": ("LOOK_AT", 1),
    "PUTBACK": ("PUT_ON", 2),
    "PUTIN": ("PUT_INSIDE", 2),
    "SIT": ("SIT", 1),
    "STANDUP": ("STANDUP", 0),
    "TURNTO": ("TURN_TO", 1),
    "WIPE": ("WIPE", 2), # TODO CHECK
    "PUTON": ("PUT_ON_CHARACTER", 1),
    "LIE": ("LIE", 1),
    "POUR": ("POUR", 2),
    "PLUGIN": ("PLUG_IN", 1),
    "PLUGOUT": ("PLUG_OUT", 1)
}
}

act_tr_sim_act ={
    "PUTON" : 'PUT_ON_CHARACTER',
    "PUTBACK" : 'PUTON'
}

