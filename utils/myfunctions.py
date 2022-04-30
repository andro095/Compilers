from constants.Constants import *

REGREX_OPERATORS = Operators.REGREX_OPERATORS

PARENTHESIS_OPERATORS = Operators.PARENTHESIS_OPERATORS

NO_CONCATENATE_OPERATORS = Operators.NO_CONCATENATE_OPERATORS

NO_CONCATENATED_OPERATORS = Operators.NO_CONCATENATED_OPERATORS


def check_parentheses(exp):
    """
    Check if the regrex expression has correct parenthesis collocation \n
    :param exp: regrex expression
    :return: True for correct parenthesis collocation. Otherwise False
    """
    b_parenteses = 0
    for char in exp:
        if char == Operators.OPEN_PARENTHESIS:
            b_parenteses += 1
        elif char == Operators.CLOSE_PARENTHESIS:
            b_parenteses -= 1

        if b_parenteses < 0:
            return False

    return b_parenteses == 0


def check_or(exp):
    """
    Check if or is correct by checking that or operands are not other operators \n
    :param exp:
    :return: True if or is correct. Otherwise, False.
    """
    return exp[0] != Operators.OR and exp[1] == Operators.OR and exp[2] not in REGREX_OPERATORS


def check_operator(exp):
    """
    Check if or is correct by checking that or operands are not other operators \n
    :param exp: part of regrex expression
    :return: True if operator usage is correct. Otherwise, False.
    """
    return exp[0] not in REGREX_OPERATORS and exp[1] in REGREX_OPERATORS and exp[2] not in REGREX_OPERATORS[1:]


def validate_regrex(exp):
    """
    Validate regrex expression \n
    :param exp: part of regrex expression
    :return: True if regrex expression is correct. Otherwise, False.
    """
    exp = exp.replace(' ', '')

    if not check_parentheses(exp):
        return False

    if len(exp) == 0:
        return False
    elif len(exp) == 1:
        return exp not in REGREX_OPERATORS and exp not in PARENTHESIS_OPERATORS
    elif len(exp) == 2:
        if all(char not in REGREX_OPERATORS for char in exp):
            return True

        if Operators.OR in exp:
            return False

        if exp[0] in PARENTHESIS_OPERATORS or exp[1] in PARENTHESIS_OPERATORS:
            return False

        if exp[0] not in REGREX_OPERATORS and exp[1] not in REGREX_OPERATORS:
            return False

        if not check_operator(exp + 'a'):
            return False

        return True
    else:
        i = 0

        if exp[0] in REGREX_OPERATORS:
            return False

        if exp[0] == Operators.OPEN_PARENTHESIS:
            sub_regrex = ''
            b_parenteses = 1
            while b_parenteses != 0:
                i += 1
                if exp[i] == Operators.OPEN_PARENTHESIS:
                    b_parenteses += 1
                elif exp[i] == Operators.CLOSE_PARENTHESIS:
                    b_parenteses -= 1

                sub_regrex += exp[i]

            if not validate_regrex(sub_regrex[:-1]):
                return False

        if exp[len(exp) - 1] == Operators.OR:
            return False

        if exp[len(exp) - 1] in REGREX_OPERATORS and not check_operator(exp[len(exp) - 2: len(exp)] + 'a'):
            return False

        while i < len(exp) - 2:
            i += 1
            if exp[i] not in REGREX_OPERATORS + PARENTHESIS_OPERATORS:
                continue

            if exp[i] not in PARENTHESIS_OPERATORS and not (
                    check_operator(exp[i - 1: i + 2]) or check_or(exp[i - 1: i + 2])):
                return False

            if exp[i] == Operators.OPEN_PARENTHESIS:
                sub_regrex = ''
                b_parenteses = 1
                while b_parenteses != 0:
                    i += 1
                    if exp[i] == Operators.OPEN_PARENTHESIS:
                        b_parenteses += 1
                    elif exp[i] == Operators.CLOSE_PARENTHESIS:
                        b_parenteses -= 1

                    sub_regrex += exp[i]

                if not validate_regrex(sub_regrex[:-1]):
                    return False

        return True


def rechange_regrex(exp):
    """
    Transform + operator to concatenation and * operator \n
    :param exp: Regrex expression
    :return: Changed regrex expression
    """
    exp = exp.replace(' ', '')

    i = 0

    reg = ''

    while i < len(exp):
        if exp[i] == Operators.OPEN_PARENTHESIS:
            sub_regrex = ''
            b_parenteses = 1

            while b_parenteses != 0:
                i += 1
                if exp[i] == Operators.OPEN_PARENTHESIS:
                    b_parenteses += 1
                elif exp[i] == Operators.CLOSE_PARENTHESIS:
                    b_parenteses -= 1

                sub_regrex += exp[i]

            new_sub_regrex = rechange_regrex(sub_regrex[:-1])

            exp = exp.replace(sub_regrex[:-1], new_sub_regrex, 1)

            reg = Operators.OPEN_PARENTHESIS + new_sub_regrex + Operators.CLOSE_PARENTHESIS

            i += len(new_sub_regrex) - len(sub_regrex[:-1])

        elif exp[i] not in [Operators.POSITIVE] + PARENTHESIS_OPERATORS:
            reg = exp[i]

        elif exp[i] == Operators.POSITIVE:
            exp = exp.replace(Operators.POSITIVE, Operators.KLEENE, 1)
            exp = exp[:i - len(reg)] + Operators.OPEN_PARENTHESIS + exp[i - len(reg):i] + reg + exp[i] + Operators.CLOSE_PARENTHESIS + exp[i + 1:]
            i += len(reg) + 2

        i += 1

    return exp


def shunting_yard(exp):
    """
    This function takes a regular expression and returns a postfix notation \n
    :param exp: The regular expression to be converted
    :return: The postfix notation of the regular expression
    """
    precedence = {Operators.OPEN_PARENTHESIS: 0, Operators.OR: 1, Operators.CONCAT: 2, Operators.KLEENE: 3, Operators.POSITIVE: 3, Operators.INTERROGATION: 3, Operators.CLOSE_PARENTHESIS: 4}
    # exp = exp.replace(' ', '')

    stack = []
    output = []

    for char in exp:
        if char in REGREX_OPERATORS + PARENTHESIS_OPERATORS:
            if char == Operators.OPEN_PARENTHESIS:
                stack.append(char)
            elif char == Operators.CLOSE_PARENTHESIS:
                while stack[-1] != Operators.OPEN_PARENTHESIS:
                    output.append(stack.pop())
                stack.pop()
            else:
                if len(stack) != 0 and precedence[stack[-1]] >= precedence[char]:
                    output.append(stack.pop())
                stack.append(char)
        else:
            output.append(char)

    while len(stack) > 0:
        output.append(stack.pop())

    return list(reversed(output))


def andres_method(exp):
    """
    This function takes the postfix regular and returns syntactic tree \n
    :param exp: postfix regular expression
    :return: syntactic tree
    """
    root = Node(exp[0])
    nodes = [root]
    focus = 0

    for char in exp[1:]:
        node = Node(char)
        nodes.append(node)
        node.father = focus

        if nodes[focus].max_child_len == 2:
            if nodes[focus].right is None:
                nodes[focus].right = node
                focus = len(nodes) - 1
            elif nodes[focus].left is None:
                nodes[focus].left = node
                focus = len(nodes) - 1
        elif nodes[focus].max_child_len == 1:
            if nodes[focus].left is None:
                nodes[focus].left = node
                focus = len(nodes) - 1

        while focus is not None and len(nodes[focus]) == nodes[focus].max_child_len:
            focus = nodes[focus].father

    return root


def add_concatenation(exp):
    """
    Add concatenation operator to regrex expression \n
    :param exp: Regrex expression
    :return: Regrex expression with concatenation operator
    """
    i = 0
    while i < len(exp) - 1:
        if exp[i] not in NO_CONCATENATE_OPERATORS and exp[i + 1] not in NO_CONCATENATED_OPERATORS:
            exp = exp[:i + 1] + Operators.CONCAT + exp[i + 1:]
            i += 1
        i += 1
    return exp



class Node(object):
    """
    Node class for syntactic tree
    """

    def __init__(self, value):
        self.father = None  # father node
        self.value = value  # value of node
        self.left = None  # left child node
        self.right = None  # right child node

        self.label = None  # value of enumeration
        self.nullable = None  # nullability of node

        self.first_position = set()  # first position of node
        self.last_position = set()  # last position of node

        # max number of children
        self.max_child_len = 2 if (
                self.value == Operators.OR or self.value == Operators.CONCAT) else 1 if self.value in REGREX_OPERATORS else 0

    def __len__(self):
        return 2 if self.left is not None and self.right is not None else 1 if self.left is not None or self.right is not None else 0

    def __str__(self):
        return self.value


def print_tree(node: Node):
    """
    Print the tree \n
    :param node: Node to be printed
    :param level: Level of the node
    :return: None
    """
    if node.left is not None:
        print_tree(node.left)


    print(node.value)

    if node.right is not None:
        print_tree(node.right)


if __name__ == '__main__':
    print('ケ"ゲゥケPゥ1ゥKゥkゥlゥgゥLゥrゥwゥjゥFゥmゥRゥuゥGゥTゥYゥiゥHゥXゥqゥQゥIゥUゥEゥbゥxゥAゥZゥWゥ	ゥCゥoゥpゥsゥSゥtゥNゥvゥ0ゥMゥyゥdゥaゥfゥOゥ ゥDゥBゥJゥcゥnゥVゥzゥhゥeゲケ"ゲ')
    # print(add_concatenation('ケ"ゲゥケPゥ1ゥKゥkゥlゥgゥLゥrゥwゥjゥFゥmゥRゥuゥGゥTゥYゥiゥHゥXゥqゥQゥIゥUゥEゥbゥxゥAゥZゥWゥ	ゥCゥoゥpゥsゥSゥtゥNゥvゥ0ゥMゥyゥdゥaゥfゥOゥ ゥDゥBゥJゥcゥnゥVゥzゥhゥeゲケ"ゲ'))
    print(shunting_yard(add_concatenation('ケ"ゲゥケPゥ1ゥKゥkゥlゥgゥLゥrゥwゥjゥFゥmゥRゥuゥGゥTゥYゥiゥHゥXゥqゥQゥIゥUゥEゥbゥxゥAゥZゥWゥ	ゥCゥoゥpゥsゥSゥtゥNゥvゥ0ゥMゥyゥdゥaゥfゥOゥ ゥDゥBゥJゥcゥnゥVゥzゥhゥeゲケ"ゲ')))
    #print_tree(andres_method(shunting_yard(add_concatenation('ケ\tゥ ゲケケ\tゥ ゲゲァ'))))