import myfunctions as mf
import graphviz as gv

REGREX_OPERATORS = ['|', '*', '+', '.', '?']


def get_next_position_table_row(num: int, value: str):
    """
    Get next position table row.
    :param num: number of row
    :param value: value of row
    :return: next position table row
    """
    return [num, value, set()]


class Direct(object):
    """
    Class for generating DFA by direct algorithm.
    """
    def __init__(self, exp):
        # Root node of syntatic tree
        self.root = mf.andres_method(mf.shunting_yard(mf.add_concatenation(mf.rechange_regrex(exp))))

        self.final_node_number = 0  # Number of final node

        # Operands that will be used in DFA for table
        self.operands = set(exp).difference({'(', ')', '|', '*', '+', '.', '?', 'ε'})

        # Next Position Table
        self.next_position_table = []

        # Final states
        self.final_states = []

        self.Table = []  # Table of transitions

        # Expand tree
        self.expand_tree()

        self.count = 1 # Number of state

        # Enumerate tree leafs
        self.enum_tree_leafs(self.root)

        # Calculate nullable
        self.nullable(self.root)

        # Calculate first
        self.first(self.root)

        # Calculate last
        self.last(self.root)

        # Calculate next
        self.next(self.root)

        # Build table
        self.build_table()

        # Graphviz object
        self.graph = gv.Digraph('DFA_direct', format='png')
        self.graph.attr(rankdir='LR')
        self.create_nodes()
        self.create_edges()
        self.graph.render(filename='images/DFA_direct ', view=True)

    def evaluate(self, word: str):
        """
        Evaluate word in DFA. \n
        :param word: word to evaluate.
        :return: True if word is accepted, False otherwise.
        """
        current_state = 0
        for char in word:
            if char not in self.operands:
                return False

            current_state = self.Table[current_state][list(self.operands).index(char) + 2]

        return current_state in self.final_states

    def create_nodes(self):
        """
        Create nodes for graphviz object. \n
        :return: None
        """
        for row in self.Table:
            if row[1] in self.final_states:
                self.graph.attr('node', shape='doublecircle')
                self.graph.node(name=str(row[1]), label=str(row[1]))
            else:
                self.graph.attr('node', shape='circle')
                self.graph.node(name=str(row[1]), label=str(row[1]))

    def create_edges(self):
        """
        Create edges for graphviz object. \n
        :return: None
        """
        for row in self.Table:
            for index, operand in enumerate(self.operands):
                self.graph.edge(str(row[1]), str(row[index + 2]), label=operand)

    def get_table_row(self):
        """
        Get row for DFA table. \n
        :return: DFA table row
        """
        return [[], -1] + [-1 for _ in range(len(self.operands))]

    def contains_final_state(self, state_numbers: list):
        """
        Check if state group contains final states. \n
        :param state_numbers: list of state numbers
        :return: True if state group contains final state number, False otherwise.
        """
        return str(self.final_node_number) in state_numbers

    def get_dfa_state(self, state_numbers: list):
        """
        Get states group from table. \n
        :param state_numbers: list of state numbers
        :return: list of states if found, None otherwise.
        """
        for row in self.Table:
            if row[0] == state_numbers:
                return row[1]

        return None

    def table_completed(self):
        """
        Check if table is completed. \n
        :return: True if table is completed, False otherwise.
        """
        for row in self.Table:
            if row[1] == -1:
                return False
            for index, operand in enumerate(self.operands):
                if row[index + 2] == -1:
                    return False
        return True

    def transition(self, state_numbers: list, value: str):
        """
        Get next state from table. \n
        :param state_numbers: list of state numbers
        :param value: value
        :return: list of state numbers if found, None otherwise.
        """

        x = set()

        for state in state_numbers:
            if self.next_position_table[int(state) - 1][1] == value:
                x = x.union(self.next_position_table[int(state) - 1][2])

        return list(x)

    def expand_tree(self):
        """
        Expand tree adding #. \n
        :return: None
        """
        root = mf.Node('.')
        right = mf.Node('#')
        root.right = right
        root.left = self.root
        self.root = root

    def enum_tree_leafs(self, node: mf.Node):
        """
        Enumerate tree leafs. \n
        :param node: node
        :return: None
        """
        if node.left is not None:
            self.enum_tree_leafs(node.left)
        if node.right is not None:
            self.enum_tree_leafs(node.right)
        if node.left is None and node.right is None:
            if node.value == 'ε':
                node.label = 'ε'
            else:
                node.label = str(self.count)
                self.next_position_table.append(get_next_position_table_row(self.count, node.value))
                if node.value == '#':
                    self.final_node_number = self.count
                self.count += 1

    def nullable(self, node: mf.Node):
        """
        Check if node is nullable. \n
        :param node: node
        :return: None
        """
        if node.left is not None:
            self.nullable(node.left)
        if node.right is not None:
            self.nullable(node.right)

        if node.value in REGREX_OPERATORS:
            if node.value == '|':
                node.nullable = node.left.nullable or node.right.nullable
            elif node.value == '.':
                node.nullable = node.left.nullable and node.right.nullable
            else:
                node.nullable = True
        elif node.value == 'ε':
            node.nullable = True
        else:
            node.nullable = False

    def first(self, node: mf.Node):
        """
        Get first set of node. \n
        :param node: node
        :return: None
        """
        if node.left is not None:
            self.first(node.left)
        if node.right is not None:
            self.first(node.right)

        if node.value in REGREX_OPERATORS:
            if node.value == '|':
                node.first_position = node.left.first_position.union(node.right.first_position)
            elif node.value == '.':
                if node.left.nullable:
                    node.first_position = node.left.first_position.union(node.right.first_position)
                else:
                    node.first_position = node.left.first_position
            else:
                node.first_position = node.left.first_position
        elif node.value == 'ε':
            node.first_position = set()
        else:
            node.first_position = {node.label}

    def last(self, node: mf.Node):
        """
        Get last set of node. \n
        :param node: node
        :return: None
        """
        if node.left is not None:
            self.last(node.left)
        if node.right is not None:
            self.last(node.right)

        if node.value in REGREX_OPERATORS:
            if node.value == '|':
                node.last_position = node.left.last_position.union(node.right.last_position)
            elif node.value == '.':
                if node.right.nullable:
                    node.last_position = node.left.last_position.union(node.right.last_position)
                else:
                    node.last_position = node.right.last_position
            else:
                node.last_position = node.left.last_position
        elif node.value == 'ε':
            node.last_position = set()
        else:
            node.last_position = {node.label}

    def next(self, node: mf.Node):
        """
        Get next set of node. \n
        :param node: node
        :return: None
        """
        if node.left is not None:
            self.next(node.left)
        if node.right is not None:
            self.next(node.right)

        if node.value == '.':
            for i in node.left.last_position:
                self.next_position_table[int(i) - 1][2].update(node.right.first_position)
        elif node.value == '*':
            for i in node.left.last_position:
                self.next_position_table[int(i) - 1][2].update(node.left.first_position)

    def build_table(self):
        """
        Build transition table. \n
        :return:
        """
        self.Table.append(self.get_table_row())
        self.Table[0][0] = list(self.root.first_position)
        self.Table[0][1] = 0
        if self.contains_final_state(self.Table[0][0]):
            self.final_states.append(0)

        i = 0
        j = 1

        while not self.table_completed():
            for index, operand in enumerate(self.operands):
                list_of_states = self.transition(self.Table[i][0], operand)
                state_number = self.get_dfa_state(list_of_states)
                if state_number is None:
                    self.Table.append(self.get_table_row())
                    self.Table[j][0] = list_of_states
                    self.Table[j][1] = j
                    self.Table[i][index + 2] = j
                    if self.contains_final_state(list_of_states):
                        self.final_states.append(j)
                    j += 1
                else:
                    self.Table[i][index + 2] = state_number
            i += 1
