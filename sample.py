# -*- coding: utf-8 -*-

from functions import parse_bnf, remove_left_recursion, remove_left_factoring, pprint_table


def do_it(grammar_text):
    print("Original:")
    g = parse_bnf(grammar_text)
    g.print_join_productions()

    print("\nAfter removing left-recursion:")
    g = remove_left_recursion(g)
    g.print_join_productions()

    print("\nAfter removing left-factoring:")
    g = remove_left_factoring(g)
    g.print_join_productions()

    print()
    for nt in g.nonterminals:
        print('FIRST({}) = {}'.format(nt, g.first(nt)))

    print()
    follow = [(nt, g.follow(nt)) for nt in g.nonterminals]
    print()
    for nt, f in follow:
        print('FOLLOW({}) = {}'.format(nt, f))

    print()
    table, ambigous = g.parsing_table()
    print("Parsing Table: ")
    for k, v in table.items():
        print("{}: {}".format(k, v))
    if ambigous:
        print("El lenguaje de entrada no es LL(1) debido a que se encontraron ambigüedades.")

    print()
    pprint_table(g, table)


bnf_text = "E -> T E'\n" \
           "E' -> + T E' | ε\n" \
           "T -> F T'\n" \
           "T' -> * F T' | ε\n" \
           "F -> ( E ) | id"

indirect_recursive = "S -> A a | b\n" \
                     "A -> A c | S d | ε"

bnf_recursive = "E -> E + T | T\n" \
                "T -> T * F | F\n" \
                "F -> ( E ) | id"

ambigous_text = "S -> A | B\n" \
                "A -> a A b | ε\n" \
                "B -> a B b b | ε"

second_text = "E -> pa Q R | pa Q S | pa T\n" \
              "U -> e"

third_text = "S -> i E t S | i E t S e S | a\n" \
             "E -> b"

final_test = "X -> a A\n" \
             "A -> x X"

do_it(bnf_recursive)

do_it(third_text)

do_it(indirect_recursive)

do_it(final_test)