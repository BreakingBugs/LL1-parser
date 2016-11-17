# -*- coding: utf-8 -*-
from parser.functions import InvalidGrammar
from parser.grammar import Grammar
from parser.rule import Rule, InvalidProduction
from parser import functions

from tests import test_data

import unittest


class TestGrammarEquality(unittest.TestCase):
    """Test Grammar equality."""

    def setUp(self):
        self.a = Grammar(start='X')
        self.b = Grammar(start='X')
        self.c = Grammar(start='X')

        self.a.add_rule(Rule('X', ('hello', 'Y')))
        self.a.add_rule(Rule('Y', ('world Z',)))
        self.a.add_rule(Rule('Z', ('?',)))
        self.a.add_rule(Rule('Z', ('!',)))

        # B will have productions in different order
        self.b.add_rule(Rule('Y', ('world Z',)))
        self.b.add_rule(Rule('Z', ('!',)))
        self.b.add_rule(Rule('Z', ('?',)))
        self.b.add_rule(Rule('X', ('hello', 'Y')))

        self.c.add_rule(Rule('X', ('bye', 'Y')))
        self.c.add_rule(Rule('Y', ('cruel world',)))

    def test_equal(self):
        self.assertEqual(self.a, self.b)
        self.assertEqual(self.b, self.a)

    def test_unequal(self):
        self.assertNotEqual(self.a, self.c)
        self.assertNotEqual(self.b, self.c)


class TestParseBNF(unittest.TestCase):
    """Basic test cases to parse BNF."""

    def test_simple(self):
        a = Grammar(start='E')
        a.add_rule(Rule('E', ('E', '+', 'T')))
        a.add_rule(Rule('E', ('T',)))
        a.add_rule(Rule('T', ('T', '*', 'F')))
        a.add_rule(Rule('T', ('F',)))
        a.add_rule(Rule('F', ('(', 'E', ')')))
        a.add_rule(Rule('F', ('id',)))
        text = str(a)
        g = functions.parse_bnf(text)
        self.assertEqual(a, g)

    def test_invalid_grammar(self):
        text = "INVALID"
        with self.assertRaises(InvalidGrammar):
            functions.parse_bnf(text)

    def test_invalid_production(self):
        text = "E -> E + T | E"  # Production is the same as nonterminal
        with self.assertRaises(InvalidProduction):
            functions.parse_bnf(text)

    def test_cases(self):
        for case in test_data.examples:
            g = functions.parse_bnf(case)
            text = str(g)
            self.assertEqual(g, functions.parse_bnf(text))


class TestRemoveLeftRecursion(unittest.TestCase):
    def test_immediate_recursion(self):
        p = Rule('E', ('E', '+' 'T'))
        self.assertTrue(p.is_left_recursive())

    def test_book_example(self):
        solved = functions.parse_bnf(test_data.solved_indirect_recursion_book_example)
        unsolved = functions.parse_bnf(test_data.unsolved_indirect_recursion_book_example)
        g = functions.remove_left_recursion(unsolved)
        self.assertEqual(solved, g)

    def test_simple_book_example(self):
        solved = functions.parse_bnf(test_data.solved_left_recursion)
        unsolved = functions.parse_bnf(test_data.unsolved_left_recursion)
        g = functions.remove_left_recursion(unsolved)
        self.assertEqual(solved, g)

    def test_cases(self):
        for case in test_data.examples:
            g = functions.parse_bnf(case)
            g = functions.remove_left_recursion(g)
            for p in g.iter_productions():
                self.assertFalse(p.is_left_recursive(), msg='{} is left-recursive'.format(p))


class TestRemoveLeftFactoring(unittest.TestCase):
    def test_book_example(self):
        """
        S -> i E t S | i E t S e S | a
        E -> b
        """
        solved = functions.parse_bnf(test_data.solved_left_factoring)
        unsolved = functions.parse_bnf(test_data.unsolved_left_factoring)
        g = functions.remove_left_factoring(unsolved)
        if solved != g:
            print('Not equal')
        print(solved)
        print()
        print(g)

        self.assertEqual(solved, g)

    def test_cases(self):
        for case in test_data.examples:
            g = functions.parse_bnf(case)
            g = functions.remove_left_factoring(g)
            self.assertFalse(functions.check_left_factors(g), msg='{} has left factors'.format(g))


if __name__ == '__main__':
    unittest.main()
