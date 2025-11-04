import re
from typing import Any, List, Union, Optional, Set, Tuple


def get_linked_objects(object_id,relations,objects):
    unique_ids = []
    linked_objects = []
    src_relations = []
    for ed in relations:
        if ed['from_id'] == object_id or ed['to_id'] == object_id:
            src_relations.append(ed)
    for rel in src_relations:
        # Add from_id if not already in list
        if rel['from_id'] not in unique_ids:
            unique_ids.append(rel['from_id'])
        # Add to_id if not already in list
        if rel['to_id'] not in unique_ids:
            unique_ids.append(rel['to_id'])

    unique_ids.remove(object_id)
    if unique_ids:
        for nd in objects:
            if nd['id'] in unique_ids:
                linked_objects.append(nd)
    return linked_objects


class ConditionActionTree:
    """
    Represents a logical condition tree node for action preconditions.
    Handles parsing, printing, variable analysis, and evaluation.
    """

    def __init__(self, node_type: str, children: Optional[List['ConditionActionTree']] = None, value: Optional[List[Any]] = None):
        self.node_type = node_type        # 'and', 'or', 'not', 'exists', or 'predicate'
        self.children = children or []    # sub-nodes
        self.value = value                # for predicates or variable defs in 'exists'

    # ---------------------------------------------------
    # Build tree from nested list
    # ---------------------------------------------------
    @staticmethod
    def from_list(data: Union[List, str]) -> 'ConditionActionTree':
        if not data:
            #print('WARNING: Cannot build ConditionActionTree from empty data')
            return ConditionActionTree("predicate", value=[])
        if isinstance(data, str):
            return ConditionActionTree("predicate", value=[data])

        op = data[0]

        if op in {"and", "or", "not", "exists"}:
            if op == "not":
                return ConditionActionTree("not", [ConditionActionTree.from_list(data[1])])
            elif op == "exists":
                var_def = data[1]
                body = ConditionActionTree.from_list(data[2])
                return ConditionActionTree("exists", [body], value=var_def)
            else:
                return ConditionActionTree(op, [ConditionActionTree.from_list(x) for x in data[1:]])

        return ConditionActionTree("predicate", value=data)

    # ---------------------------------------------------
    # Tree Printer
    # ---------------------------------------------------
    def tree_print(self, indent: int = 0):
        prefix = "  " * indent
        if self.node_type == "predicate":
            print(f"{prefix}- Predicate: {self.value}")
        else:
            label = self.node_type.upper()
            extra = f" {self.value}" if self.value else ""
            print(f"{prefix}- {label}{extra}")
            for child in self.children:
                child.tree_print(indent + 1)

    # ---------------------------------------------------
    # Extract variables (required vs optional)
    # ---------------------------------------------------
    def get_variables(self) -> Tuple[Set[str], Set[str]]:
        """
        Returns (required_vars, optional_vars)
        - required_vars: appear in predicates and are not bound by 'exists'
        - optional_vars: appear only within 'exists'
        """
        required, optional = set(), set()

        def _traverse(node: 'ConditionActionTree', bound_vars: Set[str]):
            nonlocal required, optional

            if node.node_type == "predicate":
                vars_in_pred = {tok for tok in node.value if isinstance(tok, str) and tok.startswith("?")}
                for v in vars_in_pred:
                    if v in bound_vars:
                        optional.add(v)
                    else:
                        required.add(v)

            elif node.node_type == "exists":
                var_defs = [v for v in node.value if isinstance(v, str) and v.startswith("?")]
                new_bound = bound_vars | set(var_defs)
                for child in node.children:
                    _traverse(child, new_bound)

            else:
                for child in node.children:
                    _traverse(child, bound_vars)

        _traverse(self, set())
        return required, optional

    # ---------------------------------------------------
    # Validate required variables
    # ---------------------------------------------------
    # ---------------------------------------------------
    def is_valid_variables(self,preconditions: str, list_objects: List[dict]) -> bool:
        """
        Check if all required preconditions are satisfied by the given list of objects.

        Rules:
            ?char  -> requires a category 'Characters'
            ?room  -> requires a category 'Rooms'
            ?obj, ?obj1, ?obj2... -> requires at least one object whose category is NOT 'Characters' or 'Rooms'

        Args:
            preconditions (str): Preconditions string (e.g. '(?char - character ?obj1 - object ?obj2 - object)')
            list_objects (List[Dict]): List of objects with a 'category' field.

        Returns:
            bool: True if preconditions are satisfied, False otherwise.
        """

        # Extract all ?variables from preconditions
        variables = re.findall(r'\?\w+', preconditions)

        # Determine expected categories
        expected_categories = []
        for var in variables:
            if var.startswith('?char'):
                expected_categories.append('Characters')
            elif var.startswith('?room'):
                expected_categories.append('Rooms')
            else:
                expected_categories.append('Other')  # e.g. ?obj, ?obj1, ?obj2...

        # Get all categories present in the list
        categories_in_list = [obj['category'] for obj in list_objects]

        # Check each expected category against available categories
        for expected in expected_categories:
            if expected == 'Other':
                # Need at least one object not in Characters or Rooms
                if not any(c not in ['Characters', 'Rooms'] for c in categories_in_list):
                    return False
            elif expected not in categories_in_list:
                return False

        return True


    # ---------------------------------------------------
    # Evaluation helpers
    # ---------------------------------------------------
    def _get_obj_by_var(self, var: str, var_bindings: dict):
        return var_bindings.get(var)

    def _check_relation(self, pred: str, args: List[str], var_bindings, relations, knowledge):
        """Check if relation/predicate holds between given bound objects."""
        pred_upper = pred.upper()
        vh_pred = knowledge.get(pred_upper)

        objs = [self._get_obj_by_var(a, var_bindings) for a in args if a.startswith("?")]
        if any(o is None for o in objs):
            return False

        # Unary predicate (property)
        if len(objs) == 1:
            obj = objs[0]
            props = [p.upper() for p in obj.get("properties", []) + obj.get("states", [])]
            return vh_pred in props

        # Binary relation
        if len(objs) == 2:
            o1, o2 = objs
            for r in relations:
                if ((r["from_id"] == o1["id"] and r["to_id"] == o2["id"]) or
                    (r["from_id"] == o2["id"] and r["to_id"] == o1["id"])):
                    if r["relation_type"].upper() == vh_pred.upper():
                        return True
            return False

        # Complex predicates (not supported yet)
        return False

    # ---------------------------------------------------
    # Evaluation
    # ---------------------------------------------------
    def evaluate(self, var_bindings: dict, relations: list, knowledge: dict, objects: List) -> bool:
        """Recursively evaluate preconditions."""
        t = self.node_type

        if t == "predicate":
            pred = self.value[0]
            args = self.value[1:]
            return self._check_relation(pred, args, var_bindings, relations, knowledge)

        elif t == "and":
            return all(c.evaluate(var_bindings, relations, knowledge,objects) for c in self.children)

        elif t == "or":
            return any(c.evaluate(var_bindings, relations, knowledge,objects) for c in self.children)

        elif t == "not":
            return not self.children[0].evaluate(var_bindings, relations, knowledge,objects)

        elif t == "exists":
            # Simulate existential quantifier by testing all objects in the world (var_bindings + extra if provided)
            var_name = [v for v in self.value if isinstance(v, str) and v.startswith("?")]
            if not var_name:
                return False
            v = var_name[0]

            try:
                object_id = var_bindings['?obj']['id']
                all_objs = get_linked_objects(object_id, relations, objects)
            except ValueError:
                    all_objs = list(var_bindings.values())
            for obj in all_objs:
                new_bindings = var_bindings.copy()
                new_bindings[v] = obj
                if self.children[0].evaluate(new_bindings, relations, knowledge,objects):
                    return True
            return False

        else:
            raise ValueError(f"Unknown node type: {t}")





