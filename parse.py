#!/usr/bin/env python
import sys
import argparse

from parser.functions import parse_bnf, pprint_table, remove_left_recursion, remove_left_factoring


def do_the_whole_thing(grammar_text, output=None, verbose=True):
    file = None
    if output:
        file = open(output, 'w')
        sys.stdout = file

    vprint = print if verbose else lambda *a, **key: None  # Only print if verbose is True

    vprint("Original:")
    g = parse_bnf(grammar_text)
    vprint(g)

    vprint("\nAfter removing left-recursion:")
    g = remove_left_recursion(g)
    vprint(g)

    vprint("\nAfter removing left-factoring:")
    g = remove_left_factoring(g)
    vprint(g)

    vprint()
    for nt in g.nonterminals:
        vprint('FIRST({}) = {}'.format(nt, g.first(nt)))

    vprint()
    follow = [(nt, g.follow(nt)) for nt in g.nonterminals]

    for nt, f in follow:
        vprint('FOLLOW({}) = {}'.format(nt, f))

    vprint()
    table, ambiguous = g.parsing_table()
    vprint("Parsing Table: ")
    if ambiguous:
        vprint("El lenguaje de entrada no es LL(1) debido a que se encontraron ambigüedades.")

    vprint()
    pprint_table(g, table)

    if file:
        file.close()


def main(productions, input, output, verbose):
    if input:
        with open(input, 'r') as f:
            productions = [l.strip() for l in f.readlines()]

    do_the_whole_thing('\n'.join(productions), output=output, verbose=verbose)


if __name__ == '__main__':
    aparse = argparse.ArgumentParser(description='Generate Parsing Table for LL(1) grammars.')
    aparse.add_argument('productions', help='Productions for grammar', nargs='*', default=None)
    aparse.add_argument('-i', '--input', nargs='?', help='Input file with grammar description')

    aparse.add_argument('-o', '--output', nargs='?', help='Output file name')
    aparse.add_argument('-v', '--verbose', action='store_true')
    args = aparse.parse_args()

    if args.productions and args.input:
        print("{}: error: argument -i/--input: not allowed with argument productions".format(sys.argv[0]))
        sys.exit(1)

    main(**vars(args))
