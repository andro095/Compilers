from constants.CocolConstants import CocolConstants as clc
from colorama import Fore

cocol_constants = clc()

operators = cocol_constants.operators
open_operators = [operators['po'], operators['oo'], operators['io']]
close_operators = [operators['pc'], operators['oc'], operators['ic']]

basic_set_quotes = cocol_constants.basic_set_quotes


def error(message, linenum = None):
    """
    Prints an error message and exits the program.
    :param linenum: Error line to be displayed
    :param message: The error message to be printed.
    :return: None (exit)
    """
    if linenum is not None:
        print(Fore.RED + 'Error en la línea: ' + linenum + ':\n\t' + message + '.')
    else:
        print(Fore.RED + 'Error: ' + message + '.')
    exit(3)


def check_dual_operators(exp, linenum):
    """
    Check if the regrex expression has correct parenthesis collocation \n
    :param exp: regrex expression
    :return: None
    """
    stack = []

    for char in exp:
        if char in open_operators:
            stack.append(close_operators[open_operators.index(char)])
        elif char in close_operators:
            if len(stack) == 0:
                error('Hay un ' + char + ' que no tiene un ' + open_operators[close_operators.index(char)] + ' correspondiente', linenum)

            if stack.pop() != char:
                error('Los operadores no están bien colocados', linenum)

    if len(stack) != 0:
        error('Hay un ' + open_operators[close_operators.index(stack[-1])] + ' que no tiene un ' + stack[-1] + ' correspondiente', linenum)


def listate(arr):
    """
    Prints a list in a string
    :param arr: The list to be printed
    :return: Message list transformed to string
    """
    return ''.join(
        [str(elem) if index == 0 else ' ó ' + str(elem) if index == len(arr) - 1 else ', ' + str(elem) for index, elem
         in enumerate(arr)])


def replace_index(string, start, new_char, finish=None):
    """
    Replace a character in a string
    :param string: The string to be modified
    :param start: The inital index of the character to be replaced
    :param finish: The final index of the character to be replaced
    :param new_char: The new character
    :return: The modified string
    """
    if finish is None:
        finish = start

    return string[:start] + new_char + string[finish + 1:]


def check_double_quotes(exp, linenum):
    """
    Check if the set has correct single and double quotes collocation \n
    :param exp: expression to be checked
    :param linenum: The file line number
    :return: None
    """
    stack = []
    is_open = True
    for char in exp:
        if char in basic_set_quotes:
            if is_open:
                stack.append(char)
                is_open = False
            else:
                if len(stack) == 0:
                    error('Hay un ' + char + ' de cierre que no tiene un ' + basic_set_quotes[basic_set_quotes.index(char)] + ' de apertura correspondiente', linenum)

                if stack.pop() != char:
                    error('Los operadores no están bien colocados', linenum)

                is_open = True

    if len(stack) != 0:
        error('Hay un ' + basic_set_quotes[basic_set_quotes.index(stack[-1])] + ' de apertura que no tiene un ' + stack[-1] + ' de cierre correspondiente', linenum)


def check_keyword_quotes(exp: str, linenum):
    """
    Check if the keyword set is written correctly
    :param exp: The keyword set to be checked
    :param linenum: The file line number
    :return: None
    """
    if exp.count('"') != 2:
        error('La expresión debe contener exactamente dos comillas', linenum)

    if not exp.startswith('"'):
        error('La expresión debe comenzar con una comilla', linenum)

    if not exp.endswith('"'):
        error('La expresión debe terminar con una comilla', linenum)



if __name__ == '__main__':
    print(replace_index('abcdef', 4, '3'))
