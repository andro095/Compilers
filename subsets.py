import thompson as th
import graphviz as gv


class Subsets(object):
    """
    Class for generating DFA by subsets algorithm.
    """

    def __init__(self, exp: str):
        self.NFA: th.NFA = th.NFA(exp, True)  # Create NFA

        # Operands that will be used in DFA for table
        self.operands = set(exp).difference({'(', ')', '|', '*', '+', '.', '?', 'ε'})

        self.Table = []  # DFA table
        self.final_states = []  # Final states of DFA

        # Build table
        self.build_table()

        # Graphviz object
        self.graph = gv.Digraph('DFA_subsets', format='png')
        self.graph.attr(rankdir='LR')
        self.create_nodes()
        self.create_edges()
        self.graph.render(filename='images/DFA_subsets', view=True)

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
                self.graph.node(name=str(row[1]), label=str(row[1] + int(str(self.NFA.transition.initial_state))))
            else:
                self.graph.attr('node', shape='circle')
                self.graph.node(name=str(row[1]), label=str(row[1] + int(str(self.NFA.transition.initial_state))))

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

    def get_states(self, state_numbers: list):
        """
        Get states from state numbers. \n
        :param state_numbers: list of state numbers
        :return: list of states
        """
        return [state for state in self.NFA.states_nodes if state.state_num in state_numbers]

    def epsilon(self, state_numbers: list):
        """
        Get epsilon closure of states. \n
        :param state_numbers: list of state numbers
        :return: set of states
        """
        states = self.get_states(state_numbers)

        epsilon_states = set()

        for state in states:
            epsilon_states.add(int(str(state)))
            for transition in state.transitions:
                if transition[0] == 'ε':
                    epsilon_states.add(int(str(transition[1])))
                    child_epsilon_states = self.epsilon([int(str(transition[1]))])
                    epsilon_states.update(child_epsilon_states)

        return epsilon_states

    def move(self, state_numbers: list, symbol: str):
        """
        Get states that can be reached from states with given symbol. \n
        :param state_numbers: list of state numbers
        :param symbol: symbol to move
        :return: list of states
        """
        states = self.get_states(state_numbers)
        next_states = set()

        for state in states:
            for transition in state.transitions:
                if transition[0] == symbol:
                    next_states.add(int(str(transition[1])))

        return list(next_states)

    def transition(self, state_numbers: list, symbol: str):
        """
        Get list of states that can be reached from states with given symbol. \n
        :param state_numbers: list of state numbers
        :param symbol: symbol to move
        :return: list of states
        """
        return list(self.epsilon(self.move(state_numbers, symbol)))

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

    def contains_final_state(self, state_numbers: list):
        """
        Check if state group contains final states. \n
        :param state_numbers: list of state numbers
        :return: True if state group contains final states, False otherwise.
        """
        for state in self.get_states(state_numbers):
            if state.is_final:
                return True
        return False

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

    def build_table(self):
        """
        Build DFA table. \n
        :return: None
        """
        self.Table.append(self.get_table_row())
        self.Table[0][0] = list(self.epsilon([int(str(self.NFA.transition.initial_state))]))
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
