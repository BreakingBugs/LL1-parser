# -*- coding: utf-8 -*-


class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "{} -> {}".format(self.lhs, ' '.join(self.rhs))

    def __repr__(self):
        return "{} -> {}".format(self.lhs, self.rhs)


class Grammar:
    def __init__(self, productions=None, start=None, epsilon='ε'):
        self.rules = productions if productions else []
        self.start = start
        self.nonterminals = {p.lhs for p in self.rules}
        self.epsilon = epsilon

    def add_rule(self, rule):
        self.rules.append(rule)
        self.nonterminals = self.nonterminals.union({rule.lhs})

    def is_terminal(self, s):
        return s not in self.nonterminals

    def is_start_symbol(self, symbol):
        return self.start == symbol

    def productions(self, a):
        """
        Get productions associated to a nonterminal
        :param a: the nonterminal
        :return: list of a-productions
        """
        a_productions = [r.rhs for r in self.rules if r.lhs == a]
        return a_productions

    def first(self, x):
        """
        Compute FIRST(X)
        1- If X is a terminal, FIRST(X) = {X}
        2- If there exists a production X -> ε, FIRST(X) = {ε}
        3- If there exists a production X -> Y1Y2...Yk, FIRST(X) = {Y1Y2...Yk}
        :param x:
        :return: FIRST set
        """
        f = set()
        if isinstance(x, list):
            f = self.first_multiple(x)
        elif self.is_terminal(x):
            f = {x}  # Rule 1 and 2
        else:
            for p in self.productions(x):
                f = f.union(self.first(p))

        return f

    def first_multiple(self, tokens):
        """
        Compute FIRST(Y1Y2...Yk)
        :param tokens: list of symbols
        :return: FIRST set
        """
        f = set()

        for t in tokens:
            ft = self.first(t)
            f = f.union(ft)
            if self.epsilon not in ft:
                break

        return f

    # TODO: test edge cases
    def follow(self, nonterminal):
        """
        Compute FOLLOW(A)
        :param nonterminal: the nonterminal A
        :return: set of terminals that can appear immediately to the right of A in some partial derivation

        1.  For each production X -> aAb, put FIRST (b) − {ε} in FOLLOW(A)
        2.a For each production X -> aAb, if ε is in FIRST(b) then put FOLLOW(X) into FOLLOW(A)
        2.b For each production X -> aA, put FOLLOW(X) into FOLLOW(A)
        """
        f = set()
        if self.is_start_symbol(nonterminal):
            f.add('$')

        for production in self.rules:
            if nonterminal in production.rhs:
                position = production.rhs.index(nonterminal)
                a = production.rhs[0:position]
                b = production.rhs[position + 1:]

                # Case 1
                if len(a) > 0 and len(b) > 0:
                    f = f.union(self.first(b).difference({self.epsilon}))
                # Case 2.a
                if len(a) > 0 and len(b) == 0:
                    f = f.union(self.follow(production.lhs))
                    break
                # Case 2.b
                if len(a) > 0 and len(b) > 0 and self.epsilon in self.first(b):
                    f = f.union(self.follow(production.lhs))
                    break

        return f

    def parsing_table(self):
        table = {}
        for r in self.rules:
            terminals = self.first(r.rhs)
            for t in terminals:
                if not self.is_terminal(t):
                    continue
                if t == self.epsilon:
                    pass  # TODO Add elements from FOLLOW
                else:
                    if (table.get((r.lhs, t))):
                        pass  # TODO Ambiguity found
                    else:
                        table[(r.lhs, t)] = r
        return table

    def __str__(self):
        return '\n'.join([str(p) for p in self.rules])

    def __repr__(self):
        return '\n'.join([repr(p) for p in self.rules])


def parse_bnf(text):
    """
    Parse BNF from text

    Productions use the following format:

    Start -> A
    A -> ( A ) | Two
    Two -> a
    Two -> b

    Symbols are inferred as terminal by absence from the left hand side of production rules.
    "->" designates definition, "|" designates alternation, and newlines designate termination.
    x -> y | z is EBNF short-hand for
    x -> y
    x -> z
    Be certain to place spaces between things you don't want read as one symbol. ( A ) ≠ (A)
    """
    rules = text.strip().split('\n')
    start = rules[0].split('->')[0].strip()  # First rule as starting symbol
    g = Grammar(start=start)

    for r in rules:
        head, body = [x.strip() for x in r.split('->')]
        productions = [p.strip() for p in body.split('|')]
        productions_tokenized = [p.split() for p in productions]
        for p in productions_tokenized:
            g.add_rule(Rule(head, p))

    return g
