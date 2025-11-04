import json
import os
import re
from knowledge import *

def get_objects(relevant_obj,env_states):
    objs_id = list(relevant_obj.values())
    objects = []
    for id in objs_id:
        for node in env_states['nodes']:
            if node['id'] == id:
                objects.append(node)
                break
    return objects

def get_action_pre_condition(action,args):
    dir_path = args.dataset_dir
    file_path = os.path.join(dir_path,args.action_pred)
    with open(file_path, "r") as f:
        data = json.load(f)
    try:
        return data[action.lower()]
    except KeyError:
        return None

def agent_sp_action(num_para,obj):
    if obj['class_name'] == 'character' and num_para == 0:
        return False
    elif obj['class_name'] != 'character' and num_para == 0:
        return True
    return None

def tokenize(expr: str):
    """Split expression into tokens (parens, symbols, vars)."""
    return re.findall(r'\(|\)|[^\s()]+', expr)

def parse(tokens):
    """Recursive descent parser for Lisp-like expressions."""
    if not tokens:
        return None
    token = tokens.pop(0)

    if token == '(':
        subexpr = []
        while tokens[0] != ')':
            subexpr.append(parse(tokens))
        tokens.pop(0)  # remove ')'
        return subexpr
    elif token == ')':
        return None
    else:
        return token

def parse_pddl(expr: str):
    tokens = tokenize(expr)
    return parse(tokens)

def char_holds(env_states,agent_id):
    holds_obj = []
    for ed in env_states['edges']:
        if ed['from_id'] == agent_id:  # or ed['to_id'] == agent_id:
            from_cl_name = [node['class_name'] for node in env_states['nodes'] if node['id'] == ed['from_id']]
            to_cl_name = [node['class_name'] for node in env_states['nodes'] if node['id'] == ed['to_id']]
            if ed['relation_type'] in ['HOLDS_RH', 'HOLDS_RH']:
                holds_obj.append(to_cl_name[0])
    return holds_obj

def selected_objects(num_param,current_object,objects_list,state,action=None):
    task_obj = []
    char = [ob for ob in objects_list if ob['class_name'] == 'character']
    if num_param == 0:
        task_obj.append(char[0])
        return task_obj
    if num_param == 1:
        task_obj.append(char[0])
        task_obj.append(current_object)
        return task_obj
    if num_param == 2:
        task_obj.append(char[0])
        src_obj =  char_holds(state,char[0]['id'])
        if src_obj:
            for src in src_obj:
                task_obj.append(src)
        task_obj.append(current_object) # target obj
        return task_obj
    return None

def action_object_compatibility(action,object):
    for cat in action_for_obj_cat.keys():
        if cat == action.upper():
            if action_for_obj_cat[cat] == object['category']:
                return True
            else:
                return False
    for sp_act in action_for_sp_objects.keys():
        if sp_act == action.upper():
            if action_for_sp_objects[sp_act] in object['class_name']:
                return True
            else:
                return False
    return True