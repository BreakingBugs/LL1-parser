# -*- coding: utf-8 -*-

from functions import Grammar, parse_bnf, remove_left_recursion, remove_left_factoring, check_left_factors

bnf_text = "E -> T E'\n" \
           "E' -> + T E' | ε\n" \
           "T -> F T'\n" \
           "T' -> * F T' | ε\n" \
           "F -> ( E ) | id"

bnf_recursive = "E -> E + T | T\n" \
                "T -> T * F | F\n" \
                "F -> ( E ) | id"

g = parse_bnf(bnf_recursive)
g = remove_left_recursion(g)

print(bnf_text)
print()
g.print_join_productions()
print()

for nt in g.nonterminals:
    print('FIRST({}) = {}'.format(nt, g.first(nt)))
print()

for nt in g.nonterminals:
    print('FOLLOW({}) = {}'.format(nt, g.follow(nt)))
print()

table = g.parsing_table()
print("Parsing Table: ")
for k, v in table.items():
    print("{}: {}".format(k, v))


second_text = "E -> pa Q R | pa Q S | pa T\n" \
             "U -> e"

third_text = "S -> i E t S | i E t S e S | a\n" \
               "E -> b"
print("\n\nBefore left factoring: \n\n")
print(second_text)
print("\n\nLeft factoring: \n\n")
g2 = parse_bnf(second_text)
g2 = remove_left_factoring(g2)
g2.print_join_productions()
