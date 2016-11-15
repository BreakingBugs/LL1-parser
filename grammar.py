# -*- coding: utf-8 -*-

class Grammar:
    def __init__(self, productions=None, start=None, epsilon='ε', eof='$'):
        self.productions = productions if productions else []
        self.start = start
        self.nonterminals = {p.head for p in self.productions}
        self.epsilon = epsilon
        self.eof = eof

    def add_rule(self, rule):
        for i, p in enumerate(self.productions):
            if p.head == rule.head and p.body == rule.body:
                return
        self.productions.append(rule)
        self.nonterminals = self.nonterminals.union({rule.head})

    def remove_rule(self, rule):
        for i, p in enumerate(self.productions):
            if p.head == rule.head and p.body == rule.body:
                self.productions.pop(i)

    def is_terminal(self, s):
        return s not in self.nonterminals

    def is_start_symbol(self, symbol):
        return self.start == symbol

    def productions_for(self, a):
        """
        Get productions associated to a nonterminal
        :param a: the nonterminal
        :return: list of a-productions
        """
        a_productions = [r.body for r in self.productions if r.head == a]
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
            for p in self.productions_for(x):
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

        1.  For each production X -> aAb, put FIRST(b) − {ε} in FOLLOW(A)
        2.a For each production X -> aAb, if ε is in FIRST(b) then put FOLLOW(X) into FOLLOW(A)
        2.b For each production X -> aA, put FOLLOW(X) into FOLLOW(A)
        """
        f = set()
        if self.is_start_symbol(nonterminal):
            f.add(self.eof)

        for p in self.productions:
            if nonterminal in p.body:
                position = p.body.index(nonterminal)
                a = p.body[0:position]
                b = p.body[position + 1:]

                # Case 1
                if a and b:
                    f = f.union(self.first(b) - {self.epsilon})
                # Case 2.a
                if a and not b:
                    f = f.union(self.follow(p.head))
                    break
                # Case 2.b
                if a and b and self.epsilon in self.first(b):
                    f = f.union(self.follow(p.head))
                    break

        return f

    def parsing_table(self):
        table = {}
        ambigous = False
        for r in self.productions:
            terminals = self.first(r.body)
            for t in terminals:
                if not self.is_terminal(t):
                    continue
                if t == self.epsilon:
                    f = self.follow(r.head)
                    for ef in f:
                        if (table.get((r.head, ef))):
                            ls = []
                            ls.append(table[(r.head, ef)])
                            ls.append(r)
                            table[(r.head, ef)] = ls
                            ambigous = True
                        else:
                            table[(r.head, ef)] = r
                else:
                    if (table.get((r.head, t))):
                        ls = []
                        ls.append(table[(r.head, t)])
                        ls.append(r)
                        table[(r.head, t)] = ls
                        ambigous = True
                    else:
                        table[(r.head, t)] = r
        return (table, ambigous)

    def print_join_productions(self):
        for x in self.nonterminals:
            bodies = [' '.join(p) for p in self.productions_for(x)]
            print("{} -> {}".format(x, ' | '.join(bodies)))

    def __str__(self):
        return '\n'.join([str(p) for p in self.productions])

    def __repr__(self):
        return '\n'.join([repr(p) for p in self.productions])
