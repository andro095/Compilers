import graphviz as gv
import myfunctions as mf

REGREX_OPERATORS = ['|', '*', '+', '.']

PARENTHESIS_OPERATORS = ['(', ')']

NO_CONCATENATE_OPERATORS = ['|', '(']

NO_CONCATENATED_OPERATORS = ['|', '*', '+', ')']


class StateNode(object):
    """
    Class for a state node.
    """

    def __init__(self):
        self.transitions = []  # List of transitions

        self.state_num = None  # State number

        self.is_final = False  # Is acceptation state

        self.is_join_node = False  # Is join node
        self.track_num = 0  # Track number

        self.has_image_node = False  # Has image node
        self.has_edges_created = False  # Has edges created

    def add_transition(self, transition):
        """
        Add transition to the state node. \n
        :param transition: Transition to add.
        :return: None.
        """
        self.transitions.append(transition)

    def __str__(self):
        return str(self.state_num)


class Transition(object):
    """
    Helper class for a transition.
    """

    def __init__(self):
        self.initial_state = None  # Initial state
        self.final_state = None  # Final state


class NFA(object):
    def __init__(self, exp, from_DFA=False):
        # Root node of syntatic tree
        self.root = mf.andres_method(mf.shunting_yard(mf.add_concatenation(exp)))

        # Transition class for root node
        self.transition: Transition = self.build(self.root)

        # States of NFA
        self.states = []

        self.count = 0  # Count of states
        self.set_number_state(self.transition.initial_state)  # Set number of state

        if not from_DFA: # If NFA is from DFA
            # Graphviz object
            self.graph = gv.Digraph('NFA', format='png')
            self.graph.attr(rankdir='LR')
            self.create_nodes(self.transition.initial_state)
            self.create_edges(self.transition.initial_state)
            self.graph.render(filename='images/NFA', view=True)

    def evaluate(self, word, state: StateNode = None):
        """
        Evaluate word in NFA. \n
        :param word: Word to evaluate.
        :param state: State to evaluate.
        :return: True if word is accepted, False otherwise.
        """
        evaluate = False

        if state is None:
            state = self.transition.initial_state

        if state.is_final:
            return True

        for transition in state.transitions:
            if len(word) != 0 and transition[0] == word[0]:
                evaluate = self.evaluate(word[1:], transition[1])
            elif transition[0] == 'ε':
                evaluate = self.evaluate(word, transition[1])

            if evaluate:
                return True

        return False

    def create_edges(self, state: StateNode):
        """
        Create edges in graphviz object. \n
        :param state: state to create edges.
        :return: None.
        """
        if state.has_edges_created:
            return

        for transition in state.transitions:
            self.graph.edge(str(state.state_num), str(transition[1]), label=str(transition[0]))

        state.has_edges_created = True

        if state.is_join_node:
            if state.track_num == 0:
                state.track_num += 1
                return
            else:
                state.track_num = 0

        if not state.is_final:
            for transition in state.transitions:
                self.create_edges(transition[1])

    def create_nodes(self, state: StateNode):
        """
        Create nodes in graphviz object. \n
        :param state: state to create node.
        :return: None.
        """
        if state.has_image_node:
            return

        state.has_image_node = True

        if state.is_final:
            self.graph.attr('node', shape='doublecircle')
            self.graph.node(name=str(state.state_num), label=str(state.state_num))
        else:
            self.graph.attr('node', shape='circle')
            self.graph.node(name=str(state.state_num), label=str(state.state_num))

        for transition in state.transitions:
            self.create_nodes(transition[1])

    def set_number_state(self, state: StateNode):
        """
        Set number of state. \n
        :param state: state to set number.
        :return: None.
        """
        if state.is_join_node:
            if state.track_num == 0:
                state.track_num += 1
                return
            else:
                state.track_num = 0

        if state.state_num is not None:
            return

        state.state_num = self.count
        self.count += 1

        if not state.is_final:
            for transition in state.transitions:
                self.set_number_state(transition[1])

    def build(self, node: mf.Node):
        """
        Build transition. \n
        :param node: Node to build transition.
        :return: Transition object.
        """
        transition_left = None
        transition_right = None

        if node.left is not None:
            transition_left = self.build(node.left)
        if node.right is not None:
            transition_right = self.build(node.right)

        if node.value not in REGREX_OPERATORS:
            transition = Transition()

            initial_state = StateNode()
            self.states.append(initial_state)

            final_state = StateNode()
            self.states.append(final_state)
            final_state.is_final = True

            initial_state.add_transition((node.value, final_state))

            transition.initial_state = initial_state
            transition.final_state = final_state

            return transition

        else:
            if node.value == '*' or node.value == '+':
                transition = Transition()

                initial_state = StateNode()
                self.states.append(initial_state)

                final_state = StateNode()
                self.states.append(final_state)
                final_state.is_final = True

                initial_state.add_transition(('ε', transition_left.initial_state))
                if node.value == '*':
                    initial_state.add_transition(('ε', final_state))

                transition_left.final_state.add_transition(('ε', transition_left.initial_state))
                transition_left.final_state.add_transition(('ε', final_state))

                transition_left.final_state.is_final = False

                transition.initial_state = initial_state
                transition.final_state = final_state

                return transition

            elif node.value == '|':
                transition = Transition()

                initial_state = StateNode()
                self.states.append(initial_state)

                final_state = StateNode()
                self.states.append(final_state)

                final_state.is_final = True
                final_state.is_join_node = True

                transition_left.final_state.is_final = False
                transition_right.final_state.is_final = False

                initial_state.add_transition(('ε', transition_left.initial_state))
                initial_state.add_transition(('ε', transition_right.initial_state))

                transition_left.final_state.add_transition(('ε', final_state))
                transition_right.final_state.add_transition(('ε', final_state))

                transition.initial_state = initial_state
                transition.final_state = final_state

                return transition

            elif node.value == '.':
                transition = Transition()

                transition_left.final_state.transitions = transition_right.initial_state.transitions
                transition_left.final_state.is_final = False

                transition.initial_state = transition_left.initial_state
                transition.final_state = transition_right.final_state

                return transition
