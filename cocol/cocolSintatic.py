import re
from utils.utils import error
from constants.CocolConstants import *

from pprint import pprint

clc = CocolConstants()

parameter_character = clc.parameter_character
code_character = clc.code_character


class cocolSintatic(object):
    def __init__(self, an_tokens, tokens, productions):
        self.an_tokens = an_tokens
        self.tokens = tokens
        self.productions = productions
        self.productions_names = []
        self.productions_line = ''
        self.parameters = []
        self.codes = []
        self.productions_preprocessed = []

        self.get_productions_name()
        self.get_productions_line()
        self.replace_parameters()
        self.replace_code()
        self.replace_an_tokens()
        self.process_productions()
        # self.preprocess_productions()

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
        print(self.productions_line)

        self.parameters = [(m.start(0), m.end(0), m.string[m.start(0):m.end(0)]) for m in
                           re.finditer(r"<[^(\")]*?>", self.productions_line)]

        productions_line_splited = re.split(r"<[^(\")]*?>", self.productions_line)

        replaced_line = productions_line_splited[0]

        for num_parameter in range(1, len(self.parameters) + 1):
            replaced_line += ' ' + parameter_character + str(num_parameter - 1) + ' ' + productions_line_splited[
                num_parameter]

        self.productions_line = replaced_line

    def replace_code(self):
        self.codes = [(m.start(0), m.end(0), m.string[m.start(0):m.end(0)]) for m in
                      re.finditer(r"\(\..*?\.\)", self.productions_line)]

        productions_line_splited = re.split(r"\(\..*?\.\)", self.productions_line)

        replaced_line = productions_line_splited[0]

        for num_parameter in range(1, len(self.codes) + 1):
            replaced_line += ' ' + code_character + str(num_parameter - 1) + ' ' + productions_line_splited[
                num_parameter]

        self.productions_line = replaced_line

    def replace_an_tokens(self):
        for token in self.an_tokens:
            self.productions_line = self.productions_line.replace(self.an_tokens[token], ' ' + token + ' ')

        self.productions_line = re.sub(r"\s+", ' ', self.productions_line).strip()

    def process_productions(self):
        productions = self.productions_line.split('.')
        pprint(productions)

    def preprocess_productions(self):
        productions = [prod[1] for prod in self.productions]
        productions = ''.join(productions)
        productions = re.sub(r"\(\..*?\.\)", '', productions)
        productions = re.sub(r"<[^(\")]*?>", '', productions)
        productions = re.sub(r"\".*?\"", '', productions)
        productions = re.sub(r"\s+", ' ', productions).strip()
        productions = productions.split('.')
        productions.pop()

        productions_preprocessed = []
        for production in productions:
            production_splitted = production.split('=')
            production_identifier = production_splitted[0].strip()
            production_splitted[1] = production_splitted[1].strip()
            production_splitted[1] = re.sub(r"\s+", ' ', production_splitted[1])
            production_splitted[1] = production_splitted[1].split(' ')
            production_splitted[1] = [prod.strip() for prod in production_splitted[1]]
            productions_preprocessed.append([production_identifier, production_splitted[1]])

        print(productions_preprocessed)
