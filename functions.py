# -*- coding: utf-8 -*-
from grammar import Grammar
from rule import Rule


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


def __normalize_productions(grammar):
    """
    Remove empty symbols from productions
    :param grammar: input grammar
    :return: normalized grammar
    """
    normalized_grammar = Grammar(productions=grammar.productions[::], start=grammar.start,
                                 epsilon=grammar.epsilon, eof=grammar.eof)

    for p in grammar.productions:
        if len(p.body) > 1:  # exclude productions of the form X -> ε
            p.body = [x for x in p.body if x != grammar.epsilon]

    return normalized_grammar


# TODO: Definir un ordenamiento
def nonterminal_ordering(grammar):
    return [grammar.start] + list(grammar.nonterminals - {grammar.start})


def __generate_key(grammar, x):
    new_x = x
    while new_x in grammar.nonterminals:
        new_x += '\''

    return new_x


def is_left_recursive(head, body):
    """
    Check if production is left-recursive (immediate)
    :param head: right side of production
    :param body: left side of production
    :return: True if production is left-recursive, False otherwise
    """
    return body and head == body[0]


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
    productions = grammar.productions_for(A)
    recursive = []
    nonrecursive = []
    new_productions = []

    for p in productions:
        if is_left_recursive(A, p):
            recursive.append(p)
        else:
            nonrecursive.append(p)

    if not recursive:
        return [Rule(A, p) for p in productions]  # Return same productions

    new_A = __generate_key(grammar, A)
    for b in nonrecursive:
        # A -> b1 A' | ... | bn A'
        new_productions.append(Rule(A, b + [new_A]))

    for a in recursive:
        # A' -> a1 A' | a2 A' | ... | am A'
        new_productions.append(Rule(new_A, a[1:] + [new_A]))

    # A' -> ε
    new_productions.append(Rule(new_A, grammar.epsilon))

    return new_productions


def remove_left_recursion(grammar):
    """
    Remove all left recursions from grammar
    :param grammar: input grammar
    :return: equivalent grammar with no left-recursions
    """
    temp_grammar = Grammar(productions=grammar.productions[::], start=grammar.start,
                           epsilon=grammar.epsilon, eof=grammar.eof)
    new_grammar = Grammar(start=grammar.start, epsilon=grammar.epsilon, eof=grammar.eof)
    nonterminals = nonterminal_ordering(grammar)

    for i in range(0, len(nonterminals)):
        ai = nonterminals[i]
        for j in range(0, i):
            aj = nonterminals[j]
            for p_ai in temp_grammar.productions_for(ai):
                # For each production of the form Ai -> Aj y
                if p_ai and aj == p_ai[0]:
                    replaced_productions = [Rule(ai, p_aj + p_ai[1:]) for p_aj in temp_grammar.productions_for(aj)]
                    can_remove_productions = any(map(lambda x: is_left_recursive(x.head, x.body), replaced_productions))
                    # Replace productions only if there were left-recursive ones
                    if can_remove_productions:
                        temp_grammar.remove_rule(Rule(ai, p_ai))
                        for p in replaced_productions:
                            temp_grammar.add_rule(p)

        new_productions = remove_immediate_left_recursion(temp_grammar, ai)
        for p in new_productions:
            new_grammar.add_rule(p)

    return __normalize_productions(new_grammar)


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
        sublist = map(lambda l: l[0:common_index + 1], v)
        while check_items_equal(sublist) and common_index < get_max_length(v):
            common_index += 1
            sublist = map(lambda l: l[0:common_index + 1], v)
        common_index = common_index - 1
        if (len(v) > 1):
            common[k] = map(lambda l: l[common_index + 1:], v)
        if common_index > 0:
            common[k] = map(lambda l: l[common_index + 1:], v)
            final_key = ' '.join(v[0][0:common_index + 1])
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
                    new_productions.append(Rule(nonterminal, v[0]))
                    continue
                new_x = __generate_key(grammar, nonterminal)
                body = [prefix] + [new_x]
                new_productions.append(Rule(nonterminal, body))
                for prod in v:
                    if (prod == []):
                        new_productions.append(Rule(new_x, [grammar.epsilon]))
                    else:
                        new_productions.append(Rule(new_x, prod))
        else:
            new_productions.append(Rule(nonterminal, productions[0]))

    for prod in new_productions:
        new_grammar.add_rule(prod)
    return new_grammar
