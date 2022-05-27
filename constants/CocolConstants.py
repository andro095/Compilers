import constants.Constants as rec

constants = rec.Operators()

class CocolConstants:
    keywords = {
        'any': "ANY",
        'characters': "CHARACTERS",
        'comments': "COMMENTS",
        'compiler': "COMPILER",
        'context': "CONTEXT",
        'end': "END",
        'except': "EXCEPT",
        'from': "FROM",
        'if': "IF",
        'ignore': "IGNORE",
        'ignorecase': "IGNORECASE",
        'keywords': 'KEYWORDS',
        'nested': "NESTED",
        'out': "out",
        'pragmas': "PRAGMAS",
        'productions': "PRODUCTIONS",
        'sync': "SYNC",
        'to': "TO",
        'tokens': "TOKENS",
        'weak': "WEAK"
    }

    non_alone_keywords = [keywords['compiler'], keywords['end']]

    escape_chars = {
        'backslash': '\\',
        'apostrophe': "\'",
        'quote': '\"',
        'nullCharacter': '\0',
        'carriageReturn': '\r',
        'newLine': '\n',
        'horizontalTab': '\t',
        'verticalTab': '\v',
        'formFeed': '\f',
        'bell': '\a',
        'backspace': '\b'

    }

    operators = {
        'equal': "=",
        'point': ".",
        'or': "|",
        'po': "(",
        'pc': ")",
        'oo': "[",
        'oc': "]",
        'io': "{",
        'ic': "}",
        'space': " "
    }

    subs_operators = {
        operators['oc']: constants.INTERROGATION,
        operators['ic']: constants.KLEENE,
    }

    chr_operators = {
        'co': 'CHR(',
        'cc': ')',
    }


    identifier_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    basic_set_operators = {
        'plus': '+',
        'minus': '-',
    }

    basic_set_quotes = [escape_chars['apostrophe'], escape_chars['quote']]

    ignore_token = 'IGNORE'

    no_found_token = 'NEL'

    parameter_character = '\u30E4'

    code_character = '\u30AD'




def validate(line):
    if CocolConstants.keywords['ignore'] in line[1]:
        line_splited = line[1].split('=', 1)
        if len(line_splited) != 2:
            return 'Error en la linea ' + line[0] + ': ' + line[1] + '\n' + 'El token ' + CocolConstants.keywords['ignore'] + ' debe tener un solo signo de igualdad'

        if line_splited[0].strip() != CocolConstants.keywords['ignore']:
            return 'Error en la linea ' + line[0] + ': ' + line[1] + '\n' + 'El token ' + CocolConstants.keywords['ignore'] + ' debe tener el nombre ' + CocolConstants.keywords['ignore']

        if not line_splited[1].strip().endswith('.'):
            return 'Error en la linea ' + line[0] + ': ' + line[1] + '\n' + 'El token ' + CocolConstants.keywords['ignore'] + ' debe tener un punto al final'

        return CocolConstants.keywords['ignore']

    if '=' in line[1] or '.' in line[1]:
        return False

    splitted_line = line[1].split(' ')

    if not splitted_line[0].isupper():
        return "La primera palabra debe ser una keyword en mayúsculas"

    if splitted_line[0] not in CocolConstants.keywords.values():
        return "Palabra reservada inválida: " + splitted_line[0]

    is_alone = splitted_line[0] not in CocolConstants.non_alone_keywords

    message = "Palabra " + splitted_line[0] + " sin identificador" if not is_alone else "La keyword " + splitted_line[
        0] + " no lleva más palabras"

    if len(splitted_line) != (1 if is_alone else 2):
        return message

    count_keywords = 0
    for word in splitted_line:
        if word in CocolConstants.keywords.values():
            count_keywords += 1

    if count_keywords > 1:
        return "La linea contiene mas de una keyword"

    return True
