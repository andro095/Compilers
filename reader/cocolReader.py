import constants.CocolConstants as clc
from utils.utils import error


class CocolReader(object):
    """
    Reader for the cocol file.
    """

    def __init__(self, file):
        self.file = file
        self.compiler_name = ''
        self.keywords = clc.CocolConstants().keywords
        self.data = []
        self.d_keywords = []
        self.ignore_line = ''
        self.nd_keywords = []

        essential_keywords = [self.keywords['compiler'], self.keywords['end']]

        self.read()

        self.check_keywords()
        list(map(self.check_essential_keyword, essential_keywords))
        self.check_compiler_name()

        self.get_non_keywords()

        self.check_final_point()

        list(map(self.remove_keyword, essential_keywords))

    def read(self):
        """
        Reads the file and stores the lines in a list of tuples.\n
        :return: None
        """
        with open(self.file, 'r') as f:
            for index, line in enumerate(f.readlines()):
                if line.strip() != '':
                    self.data.append([str(index + 1), line.strip()])

    def check_essential_keyword(self, keyword):
        """
        Checks if the keyword is in the file. If not, displays error message.\n
        :param keyword: The keyword to check.
        :return: None
        """
        for line in self.data:
            if keyword in line[1]:
                return
        error('Palabra reservada ' + keyword + ' no encontrada')

    def check_keywords(self):
        """
        Checks if the keywords is correct. If not, displays error message.\n
        :return: None
        """
        for line in self.data:
            if any(keyword in line[1] for keyword in self.keywords.values()):
                validation = clc.validate(line)
                if validation == self.keywords['ignore']:
                    self.ignore_line = line[1].split('=')[1].strip()[:-1]
                elif type(validation) == str:
                    error(validation, line[0])
                elif validation:
                    self.d_keywords.append(line)




    def check_compiler_name(self):
        """
        Checks if the compiler name is correct set. If not, displays error message.\n
        :return: None
        """
        words = list(filter(lambda line: any(
            keyword in line[1].split(' ')[0] for keyword in [self.keywords['compiler'], self.keywords['end']]),
                            self.d_keywords))

        if len(words) != 2:
            error('Tiene que haber solo una instancia de ' + self.keywords['compiler'] + ' y de ' + self.keywords['end'])

        if words[0][1].split(' ')[1] != words[1][1].split(' ')[1]:
            error('El nombre del compilador no es el mismo en ' + self.keywords['compiler'] + ' que en ' + self.keywords['end'])

        self.compiler_name = words[0][1].split(' ')[1]

    def get_non_keywords(self):
        """
        Gets the non-keywords.\n
        :return: None
        """
        self.nd_keywords = list(filter(lambda line: line not in self.d_keywords and self.keywords['ignore'] not in line[1], self.data))


    def check_final_point(self):
        """
        Checks if point is at the end of all non-keywords lines. If not, displays error message.\n
        :return:
        """

        productions_line = list(filter(lambda line: self.keywords['productions'] in line[1], self.d_keywords))[0][0]

        for line in self.nd_keywords:
            if int(line[0]) > int(productions_line):
                break

            if not line[1].endswith('.'):
                error('La línea ' + line[0] + ' no termina con punto')

    def remove_keyword(self, keyword):
        for key in self.d_keywords:
            if keyword in key[1]:
                self.d_keywords.remove(key)
                return

