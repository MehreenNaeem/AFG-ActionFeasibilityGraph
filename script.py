import json

from action_sg_main import ActionSearchGraph
from afg_config import *

args = get_args()


with open(os.path.join(args.dataset_dir,args.env_file), "r") as f:
        graph = json.load(f)

current_state = graph['init_graph']
obj_names = ['couch','television'] + args.object_name
relevent_objs = {}
for obj in current_state['nodes']:
    if obj['class_name'] in obj_names:
        key_dict = f'{obj["class_name"]}_{obj["id"]}'
        relevent_objs[key_dict] = obj['id']

asg = ActionSearchGraph(current_state, relevent_objs, args)
available_actions = asg.build_action_graph()
asg.visualize_action_graph(available_actions)