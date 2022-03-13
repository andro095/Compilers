import thompson as th
from tabulate import tabulate


class Subsets(object):
    def __init__(self, exp: str):
        self.NFA: th.NFA = th.NFA(exp, True)
        self.operands = set(exp).difference({'(', ')', '|', '*', '+', '.', 'ε'})
        self.Table = []
        self.final_states = []
        self.test_funcs()

    def test_funcs(self):
        self.build_table()
        print(tabulate(self.Table, headers=['States', 'DFA State'] + list(self.operands)))
        print('Estados de aceptación en el DFA: ', self.final_states)

        # epsilon_states = self.transition([4], 'b')
        # for state in epsilon_states:
        #     print(state)

    def get_table_row(self):
        return [[], -1] + [-1 for _ in range(len(self.operands))]

    def get_states(self, state_numbers: list):
        return [state for state in self.NFA.states_nodes if state.state_num in state_numbers]

    def epsilon(self, state_numbers: list):
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
        states = self.get_states(state_numbers)
        next_states = set()

        for state in states:
            for transition in state.transitions:
                if transition[0] == symbol:
                    next_states.add(int(str(transition[1])))

        return list(next_states)

    def transition(self, state_numbers: list, symbol: str):
        return list(self.epsilon(self.move(state_numbers, symbol)))

    def get_dfa_state(self, state_numbers: list):
        for row in self.Table:
            if row[0] == state_numbers:
                return row[1]

        return None

    def contains_final_state(self, state_numbers: list):
        for state in self.get_states(state_numbers):
            if state.is_final:
                return True
        return False

    def table_completed(self):
        for row in self.Table:
            if row[1] == -1:
                return False
            for index, operand in enumerate(self.operands):
                if row[index + 2] == -1:
                    return False
        return True

    def build_table(self):
        self.Table.append(self.get_table_row())
        self.Table[0][0] = list(self.epsilon([0]))
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

