

import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict, Any, Optional
from action_precondition import *
from sg_utilities import *
from knowledge import *


def handle_action_name_case(action):
    if action in act_tr_sim_act:
        return act_tr_sim_act[action]
    else:
        return action

class ActionSearchGraph:
    """
    Builds an executable action graph using ConditionActionTree.
    It can also visualize the available actions as a tree/graph.
    """

    def __init__(self, env_state, relevant_name_to_id, args):
        self.current_objects = None
        self.env_state = env_state
        self.relevant_name_to_id = relevant_name_to_id
        self.args = args
        self.planner_vlb = planner_vlb

    # ---------------------------------------------------------
    # Internal Helper
    # ---------------------------------------------------------
    def _is_action_executable(self, pre_cond, list_objects, state, knowledge, pre_variables=None):
        """Internal version of is_action_executable()."""
        root = ConditionActionTree.from_list(pre_cond)

        #print("\n=== Condition Tree for Action ===")
        #root.tree_print()

        if pre_variables:
            if not root.is_valid_variables(pre_variables, list_objects):
                #print("❌ Variable validation failed.")
                return None

        if not root.children:
            return True

        required_vars, self.optional_vars = root.get_variables()
        var_bindings = {}

        if len(list_objects) >= len(required_vars):   # TODO FIX variable binding
            for obj, vr in zip(list_objects, required_vars):
                var_bindings[vr] = obj
        else:
            #print("⚠️ Required variables are not fully defined!")
            return None

        relations = state['edges']
        objects = state['nodes']
        return root.evaluate(var_bindings, relations, knowledge,objects)

    # ---------------------------------------------------------
    # Build Action Graph
    # ---------------------------------------------------------
    def build_action_graph(self) -> Dict[str, List[str]]:
        """Compute which actions are executable for each object."""
        current_state = self.env_state
        self.current_objects = get_objects(self.relevant_name_to_id, current_state)
        do_able_actions = {}

        for obj in self.current_objects:
            list_actions = []

            for action in self.planner_vlb['tl_actions_to_vh'].keys():
                try:
                    pre_action_name = self.planner_vlb['tl_actions_to_vh'][action.upper()][0]
                    num_parm = self.planner_vlb['tl_actions_to_vh'][action.upper()][-1]
                    act_utl = get_action_pre_condition(pre_action_name, self.args)

                    if not act_utl:
                        continue

                    if agent_sp_action(num_parm, obj):
                        continue

                    pre_cond = parse_pddl(act_utl['action_preconditions'])
                    pre_parm = act_utl['action_parameters']
                    task_objs = selected_objects(num_parm, obj, self.current_objects, current_state, action=None)

                    if action_object_compatibility(action, self.current_objects):
                        if self._is_action_executable(pre_cond, task_objs, current_state,
                                                      self.planner_vlb['tl_predicates_to_vh'], pre_parm):
                            action = handle_action_name_case(action)
                            list_actions.append(action)
                except (TypeError, KeyError):
                    continue

            do_able_actions[obj['id']] = list_actions

        return do_able_actions

    # obj_node = [ob for ob in self.relevant_name_to_id if self.relevant_name_to_id[ob] == obj_id][0]
    # ---------------------------------------------------------
    # Visualization (Hierarchical Tree Layout)
    # ---------------------------------------------------------
    def visualize_action_graph(self, available_actions: Dict[str, List[str]], title: str = "Actions Tree"):
        """
        Visualizes available actions as a hierarchical (vertical) tree.
        Each object is a root node with actions branching downward.
        """
        G = nx.DiGraph()

        # Build the graph
        for obj_id, actions in available_actions.items():
            obj_node = [ob for ob in self.relevant_name_to_id if self.relevant_name_to_id[ob] == obj_id][0]
            G.add_node(obj_node, type="object")
            for action in actions:
                action_node = f"{action}"
                G.add_node(action_node, type="action")
                G.add_edge(obj_node, action_node)

        # Compute hierarchical layout manually
        pos = self._hierarchical_layout(G)

        # Separate node types
        object_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "object"]
        action_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "action"]

        # Draw graph
        plt.figure(figsize=(10, 8))
        nx.draw_networkx_nodes(G, pos, nodelist=object_nodes, node_color="#66b3ff", node_size=1200, label="Objects")
        nx.draw_networkx_nodes(G, pos, nodelist=action_nodes, node_color="#90ee90", node_size=900, label="Actions")
        nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>", arrowsize=12)
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold")

        plt.title(title, fontsize=14)
        plt.axis("off")
        plt.legend()
        plt.tight_layout()
        plt.show()

    # ---------------------------------------------------------
    # Layout Helper
    # ---------------------------------------------------------
    def _hierarchical_layout(self, G: nx.DiGraph(), x_spacing: float = 2.0, y_spacing: float = 2.0):
        """
        Custom layout for hierarchical vertical tree.
        Objects (roots) at the top, actions below.
        """
        pos = {}
        roots = [n for n, d in G.nodes(data=True) if d["type"] == "object"]

        # Distribute roots horizontally
        for i, root in enumerate(roots):
            pos[root] = (i * x_spacing, 0)  # y=0 for roots
            children = list(G.successors(root))
            for j, child in enumerate(children):
                pos[child] = (i * x_spacing + (j - len(children) / 2) * 0.8, -y_spacing)  # below parent

        return pos
