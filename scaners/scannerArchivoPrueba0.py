
import json
import os
import tkinter as tk
from tkinter import filedialog

from dfa.direct import Direct
from utils.utils import error
from parserArchivoPrueba0 import AnaSintac
from colorama import Fore

keywords = {}
tokens = {}
line_to_eval = ''

file_tokens = 'tokeysArchivoPrueba0.json'
no_token = 'NEL'
ignore_token = 'IGNORE'


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
        line = file.readlines()
        file.close()
    return line


def process_line(line):
    ob_tokens = []
    i = 0
    buffer = ''
    centinel = False
    actual_match = False
    initialized = False
    past_match = False
    nel_times = 0
    past_token = ''
    token = ''
    while i < len(line):
        if centinel:
            if past_token != ignore_token:
                print((past_token, buffer[:-1]))
                ob_tokens.append((past_token, buffer[:-1]))
            buffer = ''
            i -= 2
            centinel = False
            nel_times = 0
        else:
            buffer += line[i]
            token = get_token(buffer)

            if token != no_token:
                past_token = token
                nel_times = 0
                if not initialized:
                    actual_match = True
                    past_match = True
                    initialized = True

            else:
                actual_match = False
                nel_times += 1

            if nel_times > 1:
                print(Fore.YELLOW, 'Warning: algunos carecters no validos en la cadena ' + buffer)
                print(Fore.RESET)
                i -= len(buffer) - 1
                buffer = ''
                nel_times = 0

            if past_match != actual_match:
                actual_match = False
                past_match = False
                centinel = True
                initialized = False
        i += 1

    token = get_token(buffer)
    if token != no_token:
        if token != ignore_token:
            ob_tokens.append((token, buffer))
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

    line_to_eval = ''.join(line_to_eval)

    AnaSintac(process_line(line_to_eval))
    
        