import json
import re
from pprint import pprint


from reader.cocolReader import CocolReader
from utils.utils import *
from constants.CocolConstants import CocolConstants as clc
import constants.Constants as rec

cocol_constants = clc()
constants = rec.Operators()

identifier_chars = cocol_constants.identifier_chars
basic_set_operators = list(cocol_constants.basic_set_operators.values())
escaped_chars = cocol_constants.escape_chars
basic_set_quotes = cocol_constants.basic_set_quotes
operators = cocol_constants.operators
open_operators = [operators['oo'], operators['io']]
close_operators = [operators['oc'], operators['ic']]
esc_chars = [escaped_chars['quote'], escaped_chars['apostrophe']]
sub_operators = cocol_constants.subs_operators
chr_operators = cocol_constants.chr_operators

def validate_set_existence(char, i, linenum):
    if i == len(char):
        error('No se encontro el caracter "' + operators['equal'] + '"', linenum)

    if i == len(char) - 1:
        error('No se declaro ningún set para el identificador', linenum)


class Cocol(object):

    def __init__(self, file):
        self.cocol_reader = CocolReader(file=file)
        self.keywords = self.cocol_reader.keywords
        self.identifiers = []
        self.division = {}
        self.characters = {}
        self.f_keywords = {}
        self.tokens = {}

        self.init_division()

        self.make_division()

        self.process_characters()

        self.process_keywords()

        self.process_tokens()

        self.transform_characters()

        self.transform_tokens()

        self.save_tokens()

        self.generate_file()

    def init_division(self):
        for keyword in self.cocol_reader.d_keywords:
            self.division[keyword[1].split(' ')[0]] = []

    def make_division(self):
        prod = list(filter(lambda line: line[1].split(' ')[0] == self.keywords['productions'], self.cocol_reader.data))[
            0]
        top_limits = [keyword[0] for keyword in self.cocol_reader.d_keywords[1:] + [prod]]

        i = 0
        for nkeyword in self.cocol_reader.nd_keywords:
            if int(nkeyword[0]) < int(top_limits[i]):
                self.division[self.cocol_reader.d_keywords[i][1]].append(nkeyword)
            else:
                i += 1
                self.division[self.cocol_reader.d_keywords[i][1]].append(nkeyword)

    def extract_ident(self, char, linenum):
        char = char.replace(' ', '')
        i = 0
        identifier = ''
        while i < len(char) and char[i] != operators['equal']:
            if char[i] not in identifier_chars:
                error('Caracter inválido ' + char[i] + ' para identificador', linenum)

            identifier += char[i]
            i += 1

        if len(identifier) == 0:
            error('No se declaro un nombre para el identificador', linenum)

        if identifier[0].isdigit():
            error('El identificador no puede iniciar con un número', linenum)

        if identifier in self.keywords.values():
            error('Identificador reservado detectado: ' + identifier, linenum)

        return identifier, i

    def process_characters(self):
        for charac in self.division[self.keywords['characters']]:

            char = charac[1][:-1].replace(' ', '')
            identifier, i = self.extract_ident(char, charac[0])

            if identifier in self.identifiers:
                error('Identificador ya existente: ' + identifier, charac[0])

            validate_set_existence(char, i, charac[0])

            i += 1

            ident_set = char[i:]

            check_double_quotes(ident_set, charac[0])

            if ident_set[-1] in basic_set_operators:
                error('El set del identificador no debe terminar con uno de los siguientes operadores: ' + listate(
                    basic_set_operators), charac[0])

            basic_sets = []

            validate = False

            allow_char_operators = False

            while i < len(char):
                if validate:
                    if char[i] not in basic_set_operators:
                        error('Se esperaba uno de los siguientes operadores: ' + listate(basic_set_operators),
                              charac[0])
                    elif char[i + 1] in basic_set_operators:
                        error('No se puede repetir un operador', charac[0])
                    else:
                        basic_sets.append(char[i])
                        validate = False
                else:

                    substring = ''
                    if char[i] in basic_set_operators:
                        if char[i + 1] in basic_set_operators:
                            error('No se espera que se repita uno de los siguientes operadores: ' + listate(
                                basic_set_operators), charac[0])
                        elif not allow_char_operators:
                            error('No se espera que inicie con uno de los siguientes operadores: ' + listate(
                                basic_set_operators), charac[0])
                        else:
                            basic_sets.append(char[i])

                    elif char[i] == escaped_chars['quote']:
                        substring += char[i]
                        i += 1

                        while char[i] != escaped_chars['quote'] and i < len(char) - 1:
                            substring += char[i]
                            i += 1

                        substring += char[i]

                        if len(substring) == 2:
                            error('No se esperaba una cadena vacía', charac[0])

                        validate = True
                        allow_char_operators = True

                        basic_sets.append(substring)

                    elif char[i] == escaped_chars['apostrophe']:
                        substring += char[i]
                        i += 1

                        if char[i] == escaped_chars['apostrophe']:
                            error('No se esperaba un caracter vacío', charac[0])

                        substring += char[i]
                        i += 1

                        if char[i] != escaped_chars['apostrophe']:
                            error('Se esperaba una comilla simple', charac[0])

                        substring += char[i]

                        validate = True
                        allow_char_operators = True

                        basic_sets.append(substring)
                    else:
                        substring += char[i]
                        i += 1

                        validate_identifier = True

                        while i < len(char) and char[i] not in basic_set_operators + basic_set_quotes:

                            if substring == chr_operators['co']:
                                validate_identifier = False
                                while char[i] != chr_operators['cc'] and i < len(char):
                                    substring += char[i]
                                    i += 1

                            substring += char[i]

                            i += 1

                        i -= 1

                        validate = True
                        allow_char_operators = True

                        if any([c not in identifier_chars for c in substring]) and validate_identifier:
                            error('La cadena ' + substring + ' no es un identificador valido', charac[0])

                        if substring not in self.characters and validate_identifier:
                            error('El identificador ' + substring + ' no existe', charac[0])

                        basic_sets.append(substring)

                i += 1

            self.characters[identifier] = [charac[0], basic_sets]
            self.identifiers.append(identifier)

    def process_keywords(self):
        for keyword in self.division[self.keywords['keywords']]:

            key = keyword[1][:-1].replace(' ', '')

            identifier, i = self.extract_ident(key, keyword[0])

            if identifier in self.identifiers:
                error('Identificador ya existente: ' + identifier, keyword[0])

            validate_set_existence(key, i, keyword[0])

            i += 1

            ident_set = key[i:]

            check_keyword_quotes(ident_set, keyword[0])

            ident_set = ident_set[1:-1]

            self.f_keywords[identifier] = [keyword[0], ident_set]
            self.identifiers.append(identifier)
        #pprint(self.f_keywords)

    def process_tokens(self):
        for token in self.division[self.keywords['tokens']]:
            tok = token[1][:-1]

            tok = " ".join(tok.split()).rstrip().lstrip()

            has_keyword_exception = False

            if ' ' + self.keywords['except'] + ' ' + self.keywords['keywords'] in tok:
                has_keyword_exception = True
                i = tok.find(' ' + self.keywords['except'] + ' ' + self.keywords['keywords'])
                if i + len(' ' + self.keywords['except'] + ' ' + self.keywords['keywords']) != len(tok):
                    error('Se esperaba el token finalizará después de las palabras reservadas: ' +
                          self.keywords['except'] + ' ' + self.keywords['keywords'], token[0])
                tok = tok[:i]

            re_tok = re.sub(r"(\"(.*?)\")|(\'(.)\')", '', tok)

            if re_tok.count('=') == 0:
                error('Se esperaba un "="', token[0])

            if re_tok.count('=') > 1:
                error('Se esperaba un solo "="', token[0])

            prod_splited = tok.split('=', 1)

            tok = prod_splited[0].replace(' ', '') + '=' + prod_splited[1].strip()

            identifier, i = self.extract_ident(tok, token[0])

            if identifier in self.identifiers:
                error('Identificador ya existente: ' + identifier, token[0])

            validate_set_existence(tok, i, token[0])

            i += 1

            ident_set = tok[i:]

            check_dual_operators(ident_set, token[0])
            check_double_quotes(ident_set, token[0])

            self.tokens[identifier] = [token[0], [ident_set, has_keyword_exception]]
            self.identifiers.append(identifier)

    def transform_characters(self):
        for identifier in self.characters:
            transformed_set = []
            for basic_set in self.characters[identifier][1]:
                if any([basic_set.startswith(quote) and basic_set.endswith(quote) for quote in basic_set_quotes]):
                    transformed_set.append(basic_set[1:-1])
                elif chr_operators['co'] in basic_set:
                    try:
                        char = chr(int(basic_set[4:-1]))
                        transformed_set.append(char)
                    except:
                        error('La secuencia no es un número', self.characters[identifier][0])
                elif basic_set not in basic_set_operators:
                    if basic_set not in self.characters:
                        error('El identificador ' + basic_set + ' no existe en el conjunto de caracteres',
                              self.characters[identifier][0])
                    transformed_set += self.characters[basic_set][1]
                else:
                    transformed_set.append(basic_set)
            self.characters[identifier][1] = transformed_set

        for identifier in self.characters:
            universal_set = set(self.characters[identifier][1][0])
            is_plus = False
            for i in range(1, len(self.characters[identifier][1])):
                if self.characters[identifier][1][i] == cocol_constants.basic_set_operators['plus']:
                    is_plus = True
                elif self.characters[identifier][1][i] == cocol_constants.basic_set_operators['minus']:
                    is_plus = False
                else:
                    if is_plus:
                        universal_set = universal_set.union(set(self.characters[identifier][1][i]))
                    else:
                        universal_set = universal_set.symmetric_difference(set(self.characters[identifier][1][i]))
            self.characters[identifier][1] = constants.OR.join(list(universal_set))

    def rechange_dual_keywords(self, token, linenum):
        if len(token) == 0:
            error('Se esperaba dentro de los operadores una combinación de identificador, string o char', linenum)

        buffer = ''
        i = 0
        while i < len(token):

            if token[i] in open_operators:
                j = i

                close_operator = close_operators[open_operators.index(token[i])]
                i += 1
                while i < len(token) and token[i] != close_operator:
                    buffer += token[i]
                    i += 1

                extended_buffer = constants.OPEN_PARENTHESIS + self.rechange_dual_keywords(buffer,
                                                                                           linenum) + constants.CLOSE_PARENTHESIS + \
                                  sub_operators[close_operator]

                token = replace_index(token, j, extended_buffer, i)
                i = j + len(extended_buffer) + 1
            elif token[i] == operators['po']:
                token = replace_index(token, i, constants.OPEN_PARENTHESIS, i)
            elif token[i] == operators['pc']:
                token = replace_index(token, i, constants.CLOSE_PARENTHESIS, i)
            elif token[i] == operators['or']:
                token = replace_index(token, i, constants.OR, i)

            i += 1
            buffer = ''

        return token

    def replace_non_dual_keywords(self, token, linenum):
        if len(token) == 0:
            error('Se esperaba un identificador, string o char', linenum)

        buffer = ''
        i = 0
        while i < len(token):
            if token[i] in identifier_chars:
                # print('entre')
                j = i
                while i < len(token) and token[i] in identifier_chars:
                    buffer += token[i]
                    i += 1

                i -= 1

                if buffer in self.f_keywords:
                    error('No se pueden usar keywords dentro de tokens', linenum)

                if buffer not in self.characters:
                    error('El identificador ' + buffer + ' no está declarado', linenum)

                extended_buffer = constants.OPEN_PARENTHESIS + self.characters[buffer][1] + constants.CLOSE_PARENTHESIS

                token = replace_index(token, j, extended_buffer, i)
                # print(token)
                i = j + len(extended_buffer)
            elif token[i] in esc_chars:
                j = i
                close_esc_char = token[i]
                i += 1

                while i < len(token) and token[i] != close_esc_char:
                    buffer += token[i]
                    i += 1

                extended_buffer = constants.OPEN_PARENTHESIS + buffer + constants.CLOSE_PARENTHESIS
                token = replace_index(token, j, extended_buffer, i)
                i = j + len(extended_buffer) - 1
            else:
                if token[i] not in constants.COCOL_REGEX_OPERATORS + constants.PARENTHESIS_OPERATORS + [operators['space']]:
                    error('Set mal escrito', linenum)

            i += 1
            buffer = ''
        return token

    def transform_tokens(self):
        for identifier in self.tokens:
            token = self.tokens[identifier][1][0]
            token = self.rechange_dual_keywords(token, self.tokens[identifier][0])
            token = self.replace_non_dual_keywords(token, self.tokens[identifier][0])
            token = re.sub(constants.CLOSE_PARENTHESIS + ' ' + constants.OPEN_PARENTHESIS, constants.CLOSE_PARENTHESIS + constants.OPEN_PARENTHESIS, token)
            token = re.sub(constants.KLEENE + ' ', constants.KLEENE, token)
            token = re.sub(constants.INTERROGATION + ' ', constants.INTERROGATION, token)
            self.tokens[identifier] = [token, self.tokens[identifier][1][1]]
        pprint(self.tokens)

    def save_tokens(self):
        json_data = {'tokens': [], 'keywords': []}
        for identifier in self.tokens:
            json_block = {'identifier': identifier,
                          'exp': self.tokens[identifier][0],
                          'except_keywords': str(int(self.tokens[identifier][1]))
                        }
            json_data['tokens'].append(json_block)

        for identifier in self.f_keywords:
            json_block = {'identifier': identifier,
                          'exp': self.f_keywords[identifier][1]
                          }
            json_data['keywords'].append(json_block)

        with open('scaners/tokeys'+ self.cocol_reader.compiler_name + '.json', 'w') as f:
            json.dump(json_data, f)
            f.close()

        pprint(self.tokens)

    def generate_file(self):
        json_filename = 'tokeys' + self.cocol_reader.compiler_name + '.json'
        file_content = """
import json
import os
import tkinter as tk
from tkinter import filedialog

from dfa.direct import Direct
from utils.utils import error

keywords = {}
tokens = {}
line_to_eval = ''

file_tokens = '""" + json_filename + """'
no_token = '""" + cocol_constants.no_found_token + """'


def read_tokens():
    with open(file_tokens, 'r') as file:
        data = json.load(file)

        for token in data['tokens']:
            tokens[token['identifier']] = [token['exp'], bool(int(token['except_keywords']))]

        for keyword in data['keywords']:
            keywords[keyword['identifier']] = keyword['exp']


def generate_dfa():
    for identifier in keywords:
        keywords[identifier] = Direct(keywords[identifier])

    for identifier in tokens:
        dfa = Direct(tokens[identifier][0])
        tokens[identifier] = [dfa, tokens[identifier][1]]


def get_token(word):
    token = no_token
    for identifier in tokens:
        if tokens[identifier][1]:
            for identif in keywords:
                if keywords[identif].evaluate(word):
                    return identif
        if tokens[identifier][0].evaluate(word):
            token = identifier
    return token


def read_eval_file(filename):
    with open(filename, 'r') as file:
        line = file.readlines()[0]
        file.close()
    return line


def process_line(line):
    ob_tokens = []
    i = 0
    buffer = ''
    while i < len(line):
        if line[i] == ' ':
            obtained = get_token(buffer)
            if obtained != no_token:
                ob_tokens.append(obtained)
                buffer = ''
            else:
                buffer += line[i]
        else:
            buffer += line[i]
        i += 1

    obtained = get_token(buffer)
    if obtained != no_token:
        ob_tokens.append(obtained)
        buffer = ''

    if buffer != '':
        error('Error: No se pudo reconocer el token a partir de la cadena: ' + buffer)

    return ob_tokens


if __name__ == '__main__':
    read_tokens()
    generate_dfa()

    root = tk.Tk()
    root.withdraw()

    filepath = filedialog.askopenfilename(title='Seleccione el archivo de prueba',
                                          defaultextension='.txt',
                                          filetypes=[('text', '.txt')],
                                          initialdir=os.getcwd())

    line_to_eval = read_eval_file(filepath)

    print('Tokens detectados: ' + ' '.join(process_line(line_to_eval)))

        """
        with open('scaners/scanner'+ self.cocol_reader.compiler_name +'.py', 'w') as file:
            file.write(file_content)


if __name__ == '__main__':
    # root = tk.Tk()
    # root.withdraw()
    #
    # filepath = filedialog.askopenfilename(title='Seleccione el archivo .atg',
    #                                       defaultextension='.atg',
    #                                       filetypes=[('cocol', '.atg'), ('text', '.txt')],
    #                                       initialdir=os.getcwd())

    cocol = Cocol('./examples/ArchivoPrueba2.atg')
