import constants.CocolConstants as clc

constants = clc.CocolConstants()

operators = constants.operators

check_operators = [operators['po'], operators['pc'], operators['oo'], operators['oc'], operators['io'], operators['ic'],
                   operators['or']]



class cocolToken():
    def __init__(self, attr, value):
        self.Atributo = attr
        self.Valor = value

class cocolTree():
    def __init__(self, regrex, firsts):
        self.firsts = firsts
        self.regrex = regrex
        self.tabs = 0
        self.root = None
        self.operators_funcs = {
            'or': self.oor,
            'ct': self.concat,
            'io': self.kleene,
            'ic': self.kleene_c,
            'oo': self.square,
            'oc': self.square_c,
        }
        self.precedences = {
            'ct': 3,
            'or': 2,
            'io': 1,
            'oo': 1,
            'ic': 0,
            'oc': 0,
        }


        self.add_contatenation()

        self.build_tree()


    def add_contatenation(self):
        new_regrex = []
        option1 = operators['po'] + operators['io'] + operators['oo'] + operators['oc'] + operators['ic']
        option2 = operators['po'] + operators['oo']
        index = 0

        for index in range(len(self.regrex)):
            if index + 1 >= len(self.regrex):
                new_regrex.append(self.regrex[-1])
                break

            new_regrex.append(self.regrex[index])

            if self.regrex[index].Valor == operators['ic'] and self.regrex[index + 1].Valor in option1:
                new_regrex.append(cocolToken('ct', '.'))
            elif self.regrex[index].Valor not in check_operators and self.regrex[index + 1].Valor not in check_operators:
                new_regrex.append(cocolToken('ct', '.'))
            elif self.regrex[index].Valor not in check_operators and self.regrex[index + 1].Valor in option2:
                new_regrex.append(cocolToken('ct', '.'))
            elif self.regrex[index].Valor == operators['pc'] and self.regrex[index + 1].Valor not in check_operators:
                new_regrex.append(cocolToken('ct', '.'))

        self.regrex = new_regrex

    def peek(self, stack):
        return stack[-1] if stack else None

    def check_cocol_token(self, cocolToken):
        tokens = ['ident', 'attr', 'code', 'string', 'ignore']
        if cocolToken.Atributo in tokens:
            return True
        return False

    def build_first(self, value):
        return self.firsts[value] if value in self.firsts.keys() else [value]

    def first(self, l, r, op):
        if op == 'ct':
            if l.Atributo == 'ident':
                return self.build_first(l.Valor)
            elif r.Atributo == 'ident':
                return self.build_first(r.Valor)
            else:
                return []
        elif op == 'or':
            return self.build_first(l.Valor) + self.build_first(r.Valor)

    def operator(self, ops, vals):
        op = ops.pop()

        r = ([], []) if len(vals) == 1 and op.Atributo == 'ic' else vals.pop()
        l = ([], []) if len(vals) == 0 else vals.pop()

        if op.Atributo in self.operators_funcs.keys():
            return self.operators_funcs[op.Atributo](l, r)


    def oor(self, left, right):
        operator = 'or'
        # print(operator)

        if isinstance(left, tuple) and isinstance(right, tuple):
            self.tabs -= 1
            root = left[0] + ['else:'] + right[0]
            self.tabs -= 1
            return (root, left[1] + right[1])

        elif not isinstance(left, tuple) and not isinstance(right, tuple):
            root = []
            first = self.first(left, right, operator)

            # LEFT
            if left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']

            # RIGHT
            if right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'elif self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'elif self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']

            self.tabs -= 1
            return (root, first)

        elif isinstance(left, tuple) and not isinstance(right, tuple):
            root = left[0] + ['else:']
            first = left[1]

            # RIGHT
            if right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
                first += self.firsts[right.Valor]
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                first += [right.Valor]

            self.tabs -= 1
            return (root, first)

        elif not isinstance(left, tuple) and isinstance(right, tuple):
            root = []
            first = right[1]
            self.tabs -= 1

            # LEFT
            if left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
                first += self.firsts[left.Valor]
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
                first += [left.Valor]

            root += ['else:'] + ['\t' + r for r in right[0]]

            self.tabs -= 1
            return (root, first)

    def concat(self, left, right):
        operator = 'ct'
        # print(operator)
        first = []
        if isinstance(left, tuple) and isinstance(right, tuple):
            root = left[0] + right[0]
            first = left[1]
            return (root, first)

        elif not isinstance(left, tuple) and not isinstance(right, tuple):
            root = []

            first = self.first(left, right, operator)
            # LEFT
            if left.Atributo == 'code':
                root += ['\t' * self.tabs + left.Valor]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
                self.tabs += 1

            # RIGHT
            if right.Atributo == 'code':
                root += ['\t' * self.tabs + right.Valor]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'self.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                self.tabs += 1
            elif right.Atributo == 'attr':
                x = root[-1][:-2].rfind('\t')
                root[-1] = root[-1][:-2][:x + 1] + right.Valor + ' = ' + root[-1][:-2][x + 1:] + '(' + right.Valor + ')'

            return (root, first)

        elif isinstance(left, tuple) and not isinstance(right, tuple):
            root = left[0]
            first = left[1]

            # RIGHT
            if right.Atributo == 'code':
                root += ['\t' * self.tabs + right.Valor]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'self.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                self.tabs += 1
            elif right.Atributo == 'attr':
                x = root[-1][:-2].rfind('\t')
                root[-1] = root[-1][:-2][:x + 1] + right.Valor + ' = ' + root[-1][:-2][x + 1:] + '(' + right.Valor + ')'

            return (root, first)

        elif not isinstance(left, tuple) and isinstance(right, tuple):
            root = right[0]

            # LEFT
            if left.Atributo == 'code':
                root = ['\t' * self.tabs + left.Valor[2:-2]] + root
                first = right[1]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()'] + right[0]
                self.tabs += 1
                first = self.build_first(left.Valor)
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")'] + right[0]
                first = [left.Valor]
                self.tabs += 1
            return (root, first)

    def kleene(self, left, right):
        operator = 'io'
        # print(operator)
        first = []
        root = []

        if isinstance(left, tuple):
            root = left[0]
        else:
            self.tabs -= 1
            if left.Atributo == 'code':
                root = ['\t' * self.tabs + left.Valor]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root = ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
            self.tabs += 1

        if isinstance(right, tuple):
            self.tabs -= 2
            root += ['\t' * self.tabs + 'while self.currentToken in ' + repr(right[1]) + ':'] + ['\t' + i for i in
                                                                                                 right[0]]
            self.tabs += 1
        else:
            root += ['\t' * self.tabs + 'while self.currentToken in ["' + right.Valor + '"]:'] + [
                '\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
        return (root, first)

    def kleene_c(self, left, right):
        operator = 'ic'
        # print(operator)
        first = []
        self.tabs -= 1

        # RIGHT
        if isinstance(right, tuple):
            root = left[0] + right[0]
        else:
            root = left[0]
            if right.Atributo == 'code':
                root += ['\t' * self.tabs + right.Valor]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']

        return (root, first)

    def square(self, left, right):
        operator = 'oo'
        # print(operator)
        first = root = []

        if isinstance(left, tuple):
            root = left[0]
        else:
            self.tabs -= 1
            if left.Atributo == 'code':
                root = ['\t' * self.tabs + left.Valor]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']

        if isinstance(right, tuple):
            self.tabs -= 1
            root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(right[1]) + ':'] + ['\t' + i for i in right[0]]
        else:
            root += ['\t' * self.tabs + 'if self.currentToken in ["' + right.Valor + '"]:'] + [
                '\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
        return (root, first)

    def square_c(self, left, right):
        operator = 'oc'
        # print(operator)
        first = []
        self.tabs -= 1

        # RIGHT
        if isinstance(right, tuple):
            root = left[0] + right[0]
        else:
            root = left[0]
            if right.Atributo == 'code':
                root += ['\t' * self.tabs + right.Valor]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs + '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']

        return (root, first)

    def build_tree(self):
        vals = []
        ops = []

        for cocolToken in self.regrex:
            if self.check_cocol_token(cocolToken):
                vals.append(cocolToken)
            elif cocolToken.Atributo == 'po':
                ops.append(cocolToken)
            elif cocolToken.Atributo == 'pc':
                top = self.peek(ops)

                while top is not None and top.Atributo != 'po':
                    vals.append(self.operator(ops, vals))
                    top = self.peek(ops)

                ops.pop()
                self.tabs -= 1

            else:
                top = self.peek(ops)

                while top is not None and top.Atributo not in ['po', 'pc'] and self.precedences[top.Atributo] >= self.precedences[cocolToken.Atributo]:
                    vals.append(self.operator(ops, vals))
                    top = self.peek(ops)

                ops.append(cocolToken)

        while self.peek(ops) is not None:
            vals.append(self.operator(ops, vals))

        self.root = vals.pop()
        print(self.root)
