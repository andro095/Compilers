import thompson as th

class Subsets(object):
    def __init__(self, exp: str):
        self.NFA: th.NFA = th.NFA(exp, True)
        self.num_operands = set(exp).difference({'(', ')', '|', '*', '+', '.'})
        self.Table = []
