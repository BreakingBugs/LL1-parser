# -*- coding: utf-8 -*-
from os.path import commonprefix

class Rule:
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __str__(self):
        return "{} -> {}".format(self.head, ' '.join(self.body))

    def __repr__(self):
        return "{} -> {}".format(self.head, self.body)


class Grammar:
    def __init__(self, productions=None, start=None, epsilon='ε', eof='$'):
        self.productions = productions if productions else []
        self.start = start
        self.nonterminals = {p.head for p in self.productions}
        self.epsilon = epsilon
        self.eof = eof

    def add_rule(self, rule):
        self.productions.append(rule)
        self.nonterminals = self.nonterminals.union({rule.head})

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
                    f = f.union(self.first(b).difference({self.epsilon}))
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
        for r in self.productions:
            terminals = self.first(r.body)
            for t in terminals:
                if not self.is_terminal(t):
                    continue
                if t == self.epsilon:
                    pass  # TODO Add elements from FOLLOW
                else:
                    if (table.get((r.head, t))):
                        pass  # TODO Ambiguity found
                    else:
                        table[(r.head, t)] = r
        return table

    def print_join_productions(self):
        for x in self.nonterminals:
            bodies = [' '.join(p) for p in self.productions_for(x)]
            print("{} -> {}".format(x, ' | '.join(bodies)))

    def __str__(self):
        return '\n'.join([str(p) for p in self.productions])

    def __repr__(self):
        return '\n'.join([repr(p) for p in self.productions])


def parse_bnf(text):
    """
    Parse BNF from text

    Productions use the following format:

    Start -> A
    A -> ( A ) | Two
    Two -> a
    Two -> b

    Symbols are inferred as terminal by absence from the left hand side of production productions.
    "->" designates definition, "|" designates alternation, and newlines designate termination.
    x -> y | z is EBNF short-hand for
    x -> y
    x -> z
    Be certain to place spaces between things you don't want read as one symbol. ( A ) ≠ (A)
    """
    productions = text.strip().split('\n')
    start = productions[0].split('->')[0].strip()  # First rule as starting symbol
    g = Grammar(start=start)

    for r in productions:
        head, body = [x.strip() for x in r.split('->')]
        productions = [p.strip() for p in body.split('|')]
        productions_tokenized = [p.split() for p in productions]
        for p in productions_tokenized:
            g.add_rule(Rule(head, p))

    return g


def generate_key(grammar, x):
    new_x = '{}'.format(x)
    while new_x in grammar.nonterminals:
        new_x += '\''

    return new_x


def remove_immediate_left_recursion(grammar, x):
    """
    Remove immediante left-recursion for given nonterminal
    :param grammar: input grammar
    :param x: the nonterminal
    :return: list of equivalent productions. If there are no left-recursions, the productions aren't changed.
    """
    productions = grammar.productions_for(x)
    recursive = []
    nonrecursive = []
    new_productions = []
    for p in productions:
        if p and x == p[0]:
            recursive.append(p)
        else:
            nonrecursive.append(p)

    if not recursive:
        return [Rule(x, p) for p in productions]

    new_x = generate_key(grammar, x)
    for p in nonrecursive:
        body = p + [new_x]  # A -> bA'
        new_productions.append(Rule(x, body))

    for p in recursive:
        body = p[1:] + [new_x]  # A' -> aA' | ε
        new_productions.append(Rule(new_x, body))
        new_productions.append(Rule(new_x, grammar.epsilon))

    return new_productions


# TODO: remove indirect recursion
def remove_left_recursion(grammar):
    """
    Remove all left recursions from grammar
    :param grammar: input grammar
    :return: equivalent grammar with no left-recursion
    """
    new_grammar = Grammar(start=grammar.start, epsilon=grammar.epsilon, eof=grammar.eof)

    for nonterminal in grammar.nonterminals:
        new_productions = remove_immediate_left_recursion(grammar, nonterminal)
        for p in new_productions:
            new_grammar.add_rule(p)

    return new_grammar

def check_items_equal(l):
    return l[1:] == l[:-1]

def get_max_length(lst):
    return max(map(lambda l: len(l), lst))

def get_prefixes(grammar, productions):
    common = {}
    sorted_productions = sorted(productions)
    for x in sorted_productions:
        if x:
            common.setdefault(x[0], []).append(x)
    for k, v in common.items():
        common_index = 1
        sublist = map(lambda l: l[0:common_index+1], v)
        while check_items_equal(sublist) and common_index < get_max_length(v):
            common_index += 1
            sublist = map(lambda l: l[0:common_index+1], v)
        common_index = common_index - 1
        if(len(v)>1):
            common[k] = map(lambda l: l[common_index+1:], v)
        if common_index > 0:
            common[k] = map(lambda l: l[common_index+1:], v)
            final_key = ' '.join(v[0][0:common_index+1])
            common[final_key] = common[k]
            del common[k]

    return common

def are_there_factors(lst):
    first_elements = map(lambda l: l[0], lst)
    return check_items_equal(first_elements)

def check_left_factors(grammar):
    for nonterminal in grammar.nonterminals:
        productions = grammar.productions_for(nonterminal)
        if len(productions) > 1:
            first_elements = [l[0] for l in productions]
            result = check_items_equal(first_elements)
            diff_vals = set(first_elements)
            for i in diff_vals:
                if first_elements.count(i) > 1:
                    return True
    return False

def remove_left_factoring(grammar):
    g = grammar
    while(check_left_factors(g)):
        g = __remove_left_factoring(g)
    return g

def __remove_left_factoring(grammar):
    new_grammar = Grammar(start=grammar.start, epsilon=grammar.epsilon, eof=grammar.eof)

    new_productions = []

    for nonterminal in grammar.nonterminals:

        productions = grammar.productions_for(nonterminal)
        if len(productions) > 1:
            prefixes = get_prefixes(grammar, productions)
            for prefix, v in prefixes.items():
                if(len(v) == 1):
                    new_productions.append(Rule(nonterminal, v[0]))
                    continue
                new_x = generate_key(grammar, nonterminal)
                body = [prefix] + [new_x]
                new_productions.append(Rule(nonterminal, body))
                for prod in v:
                    if(prod == []):
                        new_productions.append(Rule(new_x, [grammar.epsilon]))
                    else:
                        new_productions.append(Rule(new_x, prod))
        else:
            new_productions.append(Rule(nonterminal, productions[0]))

    for prod in new_productions:
        new_grammar.add_rule(prod)
    return new_grammar
