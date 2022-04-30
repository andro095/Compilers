
import json
import os
import tkinter as tk
from tkinter import filedialog

from dfa.direct import Direct
from utils.utils import error

keywords = {}
tokens = {}
line_to_eval = ''

file_tokens = 'tokeysArchivoPrueba3.json'
no_token = 'NEL'


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

        