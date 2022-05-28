import re
from utils.utils import error
from constants.CocolConstants import *
from cocolTree import *

from pprint import pprint

clc = CocolConstants()

parameter_character = clc.parameter_character
code_character = clc.code_character
operators = clc.operators
check_operators = [operators['po'], operators['pc'], operators['oo'], operators['oc'], operators['io'], operators['ic'],
                   operators['or']]

operators_dic = {
    operators['po']: 'po',
    operators['pc']: 'pc',
    operators['oo']: 'oo',
    operators['oc']: 'oc',
    operators['io']: 'io',
    operators['ic']: 'ic',
    operators['or']: 'or',
    operators['equal']: 'eq',
}


class cocolSintatic(object):
    def __init__(self, an_tokens, tokens, productions, compiler_name):
        self.an_tokens = an_tokens
        self.tokens = tokens
        self.productions = productions
        self.compiler_name = compiler_name
        self.productions_names = []
        self.productions_line = ''
        self.parameters = []
        self.codes = []
        self.firsts = {}

        self.productions_preprocessed = []
        self.productions_processed = []
        self.functions_parameters = []
        self.productions_body = []

        self.get_productions_name()
        self.get_productions_line()
        self.replace_parameters()
        self.replace_code()
        self.replace_an_tokens()
        self.adjust_symbols()
        self.process_productions()
        self.get_tuples()
        self.separate()

        self.program = '''

class AnaSintac():
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.currentToken = None
        self.nextToken = self.tokens[self.pos]
        self.next()
        self.lastvalue = None

        self.main()

    def coincidir(self, terminal):
        if self.currentToken == terminal:
            self.next()
        else:
            self.reportar('Error de sintaxis')

    def next(self):
        if self.pos - 1 < 0:
            self.lastvalue = None
        else:
            self.lastvalue = self.tokens[self.pos - 1][1]

        if self.nextToken == None:
            self.currentToken = None
        else:
            self.currentToken = self.nextToken[0]
        self.pos += 1

        if self.pos >= len(self.tokens):
            self.nextToken = None
        else:
            self.nextToken = self.tokens[self.pos]
        

    def reportar(self, msg):
        print(msg)

    def main(self):
        '''

        self.process()

    def get_productions_name(self):
        productions = [prod[1] for prod in self.productions]
        productions = ''.join(productions)
        productions = re.sub(r"\(\..*?\.\)", '', productions)
        productions = re.sub(r"<[^(\")]*?>", '', productions)
        productions = re.sub(r"\".*?\"", '', productions)
        productions = re.sub(r"\s+", ' ', productions).strip()
        productions = productions.split('.')
        productions.pop()

        for production in productions:
            production_splitted = production.split('=')
            production_identifier = production_splitted[0].strip()
            if production_identifier in self.productions_names:
                error('Identificador de produccion duplicado ' + production_identifier)
            self.productions_names.append(production_identifier)

    def get_productions_line(self):
        self.productions_line = ''.join([prod[1] for prod in self.productions])

    def replace_parameters(self):
        parameters = [m.string[m.start(0):m.end(0)] for m in re.finditer(r"<[^(\")]*?>", self.productions_line)]

        for parameter in parameters:
            self.parameters.append(parameter[1:-1])

        productions_line_splited = re.split(r"<[^(\")]*?>", self.productions_line)

        replaced_line = productions_line_splited[0]

        for num_parameter in range(1, len(self.parameters) + 1):
            replaced_line += ' ' + parameter_character + str(num_parameter - 1) + ' ' + productions_line_splited[
                num_parameter]

        self.productions_line = replaced_line

    def replace_code(self):
        codes = [m.string[m.start(0):m.end(0)] for m in re.finditer(r"\(\..*?\.\)", self.productions_line)]

        for code in codes:
            self.codes.append(code[2:-2].replace(';', '; ').strip())

        productions_line_splited = re.split(r"\(\..*?\.\)", self.productions_line)

        replaced_line = productions_line_splited[0]

        for num_parameter in range(1, len(self.codes) + 1):
            replaced_line += ' ' + code_character + str(num_parameter - 1) + ' ' + productions_line_splited[
                num_parameter]

        self.productions_line = replaced_line

    def replace_an_tokens(self):
        for token in self.an_tokens:
            self.productions_line = self.productions_line.replace(self.an_tokens[token], ' ' + token + ' ')

    def adjust_symbols(self):
        for operator in check_operators:
            self.productions_line = self.productions_line.replace(operator, ' ' + operator + ' ')

        self.productions_line = re.sub(r"\s+", ' ', self.productions_line).strip()

    def process_productions(self):
        productions = self.productions_line.split('.')
        productions = [prod.strip() for prod in productions]
        productions.pop()

        self.productions_preprocessed = productions

    def get_tuples(self):
        for production in self.productions_preprocessed:
            production_processed = []
            production_splited = production.split(' ')
            for elem in production_splited:
                if elem in check_operators + [operators['equal']]:
                    production_processed.append((operators_dic[elem], elem))
                elif re.match(re.escape(parameter_character) + r'\d+', elem):
                    production_processed.append(('attr', self.parameters[int(elem[1:])]))
                elif re.match(re.escape(code_character) + r'\d+', elem):
                    production_processed.append(('code', self.codes[int(elem[1:])]))
                else:
                    production_processed.append(('ident', elem))

            self.productions_processed.append(production_processed)

    def separate(self):
        for production in self.productions_processed:
            eq_elem = production.index(('eq', '='))
            self.functions_parameters.append(production[1:eq_elem])
            self.productions_body.append(production[eq_elem + 1:])

    def process(self):
        self.program += 'self.' + self.productions_names[0] + '()'

        for index in range(len(self.productions_body) - 1, 0, -1):
            self.firsts[self.productions_names[index]] = self.get_first(self.productions_body[index])

        self.build_program()

        # print(self.an_tokens)
        # print(self.firsts)

    def get_first(self, production_body):
        first = []

        isParenthesis = False
        isSquare = False
        tok = False

        for elem in production_body:
            atribute, value = elem

            if atribute == 'pc':
                isParenthesis = False
                break
            elif atribute == 'oc':
                isSquare = False

            if isParenthesis:
                if tok:
                    if atribute == 'or':
                        tok = False
                else:
                    if atribute == 'ident' and value in self.productions_names:
                        tok = True
                        first += self.firsts[value]
                    elif atribute == 'ident' and value not in self.productions_names:
                        tok = True
                        first.append(value)
            elif isSquare:
                if atribute == 'ident' and value in self.productions_names:
                    first += self.firsts[value]
                elif atribute == 'ident' and value not in self.productions_names:
                    first.append(value)
            elif atribute == 'ident' and value in self.productions_names:
                first += self.firsts[value]
                break
            elif atribute == 'ident' and value not in self.productions_names:
                first.append(value)
                break

            if atribute == 'po':
                isParenthesis = True
            elif atribute == 'oo':
                isSquare = True

        return first

    def build_program(self):
        for index in range(len(self.productions_names)):
            my_cocol_tokens = [cocolToken(elem[0], elem[1]) for elem in self.productions_body[index]]

            cocolT = cocolTree(my_cocol_tokens, self.firsts)

            param_line = ''
            if len(self.functions_parameters[index]) > 0:
                param_line = ', ' + ', '.join([param[1] for param in self.functions_parameters[index]])

            self.program += '\n\n    def ' + self.productions_names[
                index] + '(self' + param_line + '):\n        ' + '\n        '.join(cocolT.root[0])

        print('----------------------------------------------------------------------------------------------------')

        print(self.program)

        with open('../scaners/parser' + self.compiler_name + '.py', 'w+', encoding='utf-8') as file:
            file.write(self.program)
            file.close()

        # f = open('scaners/parser' + self.compiler_name + '.py', 'w', encoding='utf-8')
        # f.write(self.program)
        # f.close()

        print('Fin del method\n')
        exit(6)
            # print(param_line)
            # print('----------------------')

            # print(self.functions_parameters[index])
