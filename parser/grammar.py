# -*- coding: utf-8 -*-
from collections import OrderedDict

import itertools
from copy import copy
from functools import lru_cache

visited = set()


class InvalidGrammar(Exception):
    def __init__(self, message, bnf_text):
        super().__init__(message)
        self.bnf_text = bnf_text


class MemoHelper:
    """
    Wrapper to ignore param previous in follow method
    """

    def __init__(self, seq=()):
        self.tup = tuple(seq)

    def __eq__(self, other):
        return isinstance(self, type(other))

    def __hash__(self):
        return hash(type(self))

    def __add__(self, seq=()):
        return MemoHelper(self.tup + tuple(seq))

    def __iter__(self):
        return iter(self.tup)

    def __str__(self):
        return str(self.tup)


class Grammar:
    def __init__(self, productions=None, start=None, epsilon='ε', eof='$'):
        self.productions = productions if productions else OrderedDict()
        self.start = start
        self.epsilon = epsilon
        self.eof = eof
        self.__clear_cache()

    @property
    def nonterminals(self):
        return self.productions.keys()

    def iter_productions(self):
        """
        Return iterable of productions
        :return: Rule iterable
        """
        return itertools.chain.from_iterable(self.productions.values())

    def add_rule(self, rule):
        try:
            current_productions = self.productions[rule.head]
            if rule not in current_productions:
                current_productions.append(rule)
        except KeyError:
            self.productions[rule.head] = [rule]
        finally:
            self.__clear_cache()

    def remove_rule(self, rule):
        self.productions[rule.head].remove(rule)
        self.__clear_cache()

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
        return [p.body for p in self.productions[a]]

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
        if isinstance(x, tuple):
            f = self.first_multiple(x)
        elif self.is_terminal(x):
            f = {x}  # Rule 1 and 2
        else:
            for p in self.productions_for(x):
                f = f.union(self.first(p))

        return sorted(f)

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

    @lru_cache(maxsize=20)
    def follow(self, nonterminal, previous=MemoHelper()):
        """
        Compute FOLLOW(A)
        :param previous: track previous nonterminals
        :param nonterminal: the nonterminal A
        :return: set of terminals that can appear immediately to the right of A in some partial derivation

        1.  For each production X -> aAb, put FIRST(b) − {ε} in FOLLOW(A)
        2.a For each production X -> aAb, if ε is in FIRST(b) then put FOLLOW(X) into FOLLOW(A)
        2.b For each production X -> aA, put FOLLOW(X) into FOLLOW(A)
        """
        previous += (nonterminal,)

        f = set()
        if self.is_start_symbol(nonterminal):
            f.add(self.eof)

        subsets = set()
        for p in self.iter_productions():
            if nonterminal in p.body:
                position = p.body.index(nonterminal)
                a = p.body[0:position]
                b = p.body[position + 1:]

                # Case 1
                if a and b:
                    f = f.union(set(self.first(b)) - {self.epsilon})
                # Case 2.a
                if a and not b:
                    subsets.add(p.head)
                # Case 2.b
                elif a and b and self.epsilon in self.first(b):
                    subsets.add(p.head)

        subsets = subsets - {nonterminal}

        for x in subsets:
            if x not in previous:
                f = f.union(self.follow(x, previous))

        return sorted(f)

    def parsing_table(self, is_clean=True):
        """
        Compute LL(1) predictive parsing table
        :param is_clean: If False, will remove left factoring and left recursions.
        :return: parsing table
        """
        from parser.functions import remove_left_recursion, remove_left_factoring  # To avoid cyclic import

        equiv = self if is_clean else remove_left_recursion(remove_left_factoring(copy(self)))

        table = {}
        ambigous = False
        for r in equiv.iter_productions():
            terminals = equiv.first(r.body)
            for t in terminals:
                if not equiv.is_terminal(t):
                    continue
                if t == equiv.epsilon:
                    f = equiv.follow(r.head)
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
        print(self)

    def productions_for_string(self, x):
        s = [' '.join(p.body) for p in self.productions[x]]
        return s

    def __clear_cache(self):
        self.follow.cache_clear()

    def __str__(self):
        prod_strings = []
        for x in self.nonterminals:
            bodies = [' '.join(p.body) for p in self.productions[x]]
            prod_strings.append("{} -> {}".format(x, ' | '.join(bodies)))

        return '\n'.join(prod_strings)

    def __repr__(self):
        return '\n'.join([str(p) for p in self.iter_productions()])

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        strings = tuple(sorted([str(p) for p in self.iter_productions()]))
        return hash(strings)

    def __copy__(self):
        g = Grammar(start=self.start, epsilon=self.epsilon, eof=self.eof)
        for h, b in self.productions.items():
            g.productions[h] = copy(b)

        return g
