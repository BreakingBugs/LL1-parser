from collections import OrderedDict

EPS = 'ε'


class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs.strip().split(' ')

    def __str__(self):
        return "{} -> {}".format(self.lhs, ' '.join(self.rhs))

    def __repr__(self):
        return "{} -> {}".format(self.lhs, self.rhs)


class Grammar:
    def __init__(self, productions=None, start=None):
        self.rules = productions if productions else []
        self.start = start
        self.nonterminals = {p.lhs for p in self.rules}

    def add_rule(self, rule):
        self.rules.append(rule)
        self.nonterminals = self.nonterminals.union({rule.lhs})

    def is_terminal(self, s):
        return s not in self.nonterminals

    @staticmethod
    def from_array(array):
        g = Grammar()
        for lhs, rhs in array:
            r = rhs if isinstance(rhs, list) else [rhs]
            for x in r:
                rule = Rule(lhs, x)
                g.add_rule(rule)

        return g

    # TODO: group all productions in a single dict element, better performance
    def productions(self, a):
        a_productions = [r.rhs for r in self.rules if r.lhs == a]
        return a_productions

    def first(self, x):
        f = set()
        if isinstance(x, list):
            f = self.first_multiple(x)
        elif self.is_terminal(x):
            f = {x}
        else:
            for p in self.productions(x):
                f = f.union(self.first(p))

        return sorted(f)

    def first_multiple(self, tokens):
        f = set()

        for t in tokens:
            ft = self.first(t)
            f = f.union(ft)
            if EPS not in ft:
                break

        return f

    def __str__(self):
        return '\n'.join([str(p) for p in self.rules])

    def __repr__(self):
        return '\n'.join([repr(p) for p in self.rules])


bnf = [
    ("E", "T E'"),
    ("E'", ["+ T E'", EPS]),
    ("T", "F T'"),
    ("T'", ["* F T'", EPS]),
    ("F", ["( E )", "id"])
]

grammar = Grammar.from_array(bnf)

# print(grammar)
print()

for nt in grammar.nonterminals:
    print('FIRST({}) = {}'.format(nt, grammar.first(nt)))
# grammar.find_first('E\'')
# grammar.find_first('T')
# grammar.find_first('T\'')
# grammar.find_first('F')
