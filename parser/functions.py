# -*- coding: utf-8 -*-
from copy import copy

from parser.rule import Rule

from parser.grammar import Grammar


def parse_bnf(text, epsilon='ε', eof='$'):
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
    g = Grammar(start=start, epsilon=epsilon, eof=eof)

    for r in productions:
        head, body = [x.strip() for x in r.split('->')]
        productions = [p.strip() for p in body.split('|')]
        productions_tokenized = [tuple(p.split()) for p in productions]
        for p in productions_tokenized:
            g.add_rule(Rule(head, p))

    return g


def __normalize_productions(grammar):
    """
    Remove empty symbols from productions
    :param grammar: input grammar
    :return: normalized grammar
    """
    normalized_grammar = copy(grammar)

    for x in grammar.nonterminals:
        for p in grammar.productions[x]:
            if len(p.body) > 1:  # exclude productions of the form X -> ε
                p.body = tuple([x for x in p.body if x != grammar.epsilon])

    return normalized_grammar


# TODO: Definir un ordenamiento
def nonterminal_ordering(grammar):
    return [x for x in grammar.nonterminals]


def __generate_key(grammar, x):
    new_x = x
    while new_x in grammar.nonterminals:
        new_x += "'"

    return new_x


def remove_immediate_left_recursion(grammar, A):
    """
    Remove immediate left-recursion for given nonterminal
    :param grammar: input grammar
    :param A: the nonterminal
    :return: list of equivalent productions. If there are no left-recursions, the productions aren't changed.

    For each production:
    A -> A a1 | A a2 | ... | A am | b1 | b2 | ... | bn

    Replace with:
    A -> b1 A' | b2 A' | ... | bn A'
    A' -> a1 A' | a2 A' | ... | am A' | ε
    """
    productions = grammar.productions[A]
    recursive = []
    nonrecursive = []
    new_productions = []

    for p in productions:
        if p.is_left_recursive():
            recursive.append(p.body)
        else:
            nonrecursive.append(p.body)

    if not recursive:
        return productions

    new_A = __generate_key(grammar, A)
    for b in nonrecursive:
        # A -> b1 A' | ... | bn A'
        new_productions.append(Rule(A, b + (new_A,)))

    for a in recursive:
        # A' -> a1 A' | a2 A' | ... | am A'
        new_productions.append(Rule(new_A, a[1:] + (new_A,)))

    # A' -> ε
    new_productions.append(Rule(new_A, (grammar.epsilon,)))

    return new_productions


def remove_left_recursion(grammar):
    """
    Remove all left recursions from grammar
    :param grammar: input grammar
    :return: equivalent grammar with no left-recursions
    """
    temp_grammar = copy(grammar)
    new_grammar = Grammar(start=grammar.start, epsilon=grammar.epsilon, eof=grammar.eof)
    nonterminals = nonterminal_ordering(grammar)

    for i in range(0, len(nonterminals)):
        ai = nonterminals[i]
        for j in range(0, i):
            aj = nonterminals[j]
            for p_ai in temp_grammar.productions[ai]:
                # For each production of the form Ai -> Aj y
                if p_ai.body and aj == p_ai.body[0]:
                    replaced_productions = [Rule(ai, p_aj.body + p_ai.body[1:]) for p_aj in
                                            temp_grammar.productions[aj]]
                    can_remove_productions = any(map(lambda x: x.is_left_recursive(), replaced_productions))
                    # Replace productions only if there were left-recursive ones
                    if can_remove_productions:
                        temp_grammar.remove_rule(p_ai)
                        for p in replaced_productions:
                            temp_grammar.add_rule(p)

        new_productions = remove_immediate_left_recursion(temp_grammar, ai)
        for p in new_productions:
            new_grammar.add_rule(p)

    return __normalize_productions(new_grammar)


def check_items_equal(l):
    """
    Check if all items from a list are equal
    :param grammar: input list
    :return: True if all items are equal. False otherwise
    """
    return l[1:] == l[:-1]


def get_max_length(lst):
    """
    For a list of lists returns the maximum length found
    :param grammar: input list
    :return: Length of largest sublist
    """
    return max([len(l) for l in lst])


def get_prefixes(grammar, productions):
    common = {}
    sorted_productions = sorted(productions)
    for x in sorted_productions:
        if x:
            common.setdefault(x[0], []).append(x)
    for k, v in common.items():
        common_index = 1
        sublist = [l[0:common_index + 1] for l in v]
        while check_items_equal(sublist) and common_index < get_max_length(v):
            common_index += 1
            sublist = [l[0:common_index + 1] for l in v]
        common_index = common_index - 1
        if (len(v) > 1):
            common[k] = [l[common_index + 1:] for l in v]
        if common_index > 0:
            common[k] = [l[common_index + 1:] for l in v]
            final_key = ' '.join(v[0][0:common_index + 1])
            common[final_key] = common[k]
            del common[k]

    return common


def check_left_factors(grammar):
    """
    Check if grammar have common left factors that appears in two or more productions of the same non-terminal
    :param grammar: input grammar
    :return: True if grammar have common left factors. False otherwise
    """
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
    """
    Remove all the common left factors that appears in two or more productions of the same non-terminal from grammar
    :param grammar: input grammar
    :return: equivalent grammar with no left-factors
    """
    g = grammar
    while (check_left_factors(g)):
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
                if (len(v) == 1):
                    new_productions.append(Rule(nonterminal, tuple(v[0])))
                    continue
                new_x = __generate_key(grammar, nonterminal)
                body = [prefix] + [new_x]
                new_productions.append(Rule(nonterminal, tuple(body)))
                for prod in v:
                    if not prod:
                        new_productions.append(Rule(new_x, tuple([grammar.epsilon])))
                    else:
                        new_productions.append(Rule(new_x, tuple(prod)))
        else:
            new_productions.append(Rule(nonterminal, tuple(productions[0])))

    for prod in new_productions:
        new_grammar.add_rule(prod)
    return __normalize_productions(new_grammar)


# WARNING: code is a mess
def pprint_table(g, table, padding=4):
    terminals = sorted(set([t for n, t in table.keys()]) - {g.eof}) + [g.eof]  # put EOF at end of list
    nonterminals = [nt for nt in g.nonterminals]

    width_nt = max([len(x) for x in nonterminals])  # non_terminals width
    width = max([len(str(p)) for p in g.iter_productions()]) + padding
    if width % 2 == 0:
        width += 1

    print('{:{width}}'.format('', width=width_nt + 2), end='')
    for t in terminals:
        print('{:^{width}}'.format(t, width=width), end='')

    print()
    print('-' * ((len(terminals)) * width + width_nt))

    print()
    for x in nonterminals:
        print('{:{width}} |'.format(x, width=width_nt), end='')
        for t in terminals:
            print('{:^{width}}'.format(str(table.get((x, t), '-')), width=width), end='')

        print()
    print()
