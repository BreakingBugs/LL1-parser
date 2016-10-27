from collections import OrderedDict

EPS = 'ε'


class Rule:
    def __init__(self, lhs, rhs, is_start=False):
        self.lhs = lhs
        self.rhs = rhs
        self.is_start = is_start

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
    def from_array(array, start=None):
        start = start if start else array[0][0]
        g = Grammar(start=start)
        for lhs, rhs in array:
            r = rhs if isinstance(rhs, list) else [rhs]
            for x in r:
                is_start = (lhs == start)
                rule = Rule(lhs, x, is_start)
                g.add_rule(rule)

        return g

    # TODO: group all productions in a single dict element, better performance
    def productions(self, a):
        a_productions = [r.rhs for r in self.rules if r.lhs == a]
        return a_productions

    '''
    Compute FIRST(X)
    '''
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

    '''
    Compute FIRST(Y1Y2...Yk)
    '''
    def first_multiple(self, tokens):
        f = set()

        for t in tokens:
            ft = self.first(t)
            f = f.union(ft)
            if EPS not in ft:
                break

        return f

    @staticmethod
    def parse_bnf(text):
        rules = text.strip().split('\n')
        g = Grammar()

        for r in rules:
            head, body = [x.strip() for x in r.split('->')]
            productions = [p.strip() for p in body.split('|')]
            productions_tokenized = [p.split() for p in productions]
            for p in productions_tokenized:
                g.add_rule(Rule(head, p))

        return g

    def __str__(self):
        return '\n'.join([str(p) for p in self.rules])

    def __repr__(self):
        return '\n'.join([repr(p) for p in self.rules])


bnf_text = "E -> T E'\n" \
           "E' -> + T E' | ε\n" \
           "T -> F T'\n" \
           "T' -> * F T' | ε\n" \
           "F -> ( E ) | id"

g = Grammar.parse_bnf(bnf_text)

print(bnf_text)
print()
print(g)

for nt in g.nonterminals:
    print('FIRST({}) = {}'.format(nt, g.first(nt)))
