 # -*- coding: utf-8 -*-

from functions import Grammar, parse_bnf

bnf_text = "E -> T E'\n" \
           "E' -> + T E' | ε\n" \
           "T -> F T'\n" \
           "T' -> * F T' | ε\n" \
           "F -> ( E ) | id"

g = parse_bnf(bnf_text)

print(bnf_text)
print()
print(g)

for nt in g.nonterminals:
    print('FIRST({}) = {}'.format(nt, g.first(nt)))

table = g.parsing_table()
print("Parsing Table: ")
for k, v in table.items():
    print("{}: {}".format(k, v))
