# -*- coding: utf-8 -*-
from parser import functions as f
from parser.grammar import Grammar, InvalidGrammar
from parser.rule import Rule, InvalidProduction
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
        g = f.parse_bnf(text)
        self.assertEqual(a, g)

    def test_invalid_grammar(self):
        text = "INVALID"
        with self.assertRaises(InvalidGrammar):
            f.parse_bnf(text)

    def test_invalid_production(self):
        text = "E -> E + T | E"  # Production is the same as nonterminal
        with self.assertRaises(InvalidProduction):
            f.parse_bnf(text)

    def test_cases(self):
        for case in test_data.examples:
            g = f.parse_bnf(case)
            text = str(g)
            self.assertEqual(g, f.parse_bnf(text))


class TestRemoveLeftRecursion(unittest.TestCase):
    def test_immediate_recursion(self):
        p = Rule('E', ('E', '+' 'T'))
        self.assertTrue(p.is_left_recursive())

    def test_book_example(self):
        solved = f.parse_bnf(test_data.solved_indirect_recursion_book_example)
        unsolved = f.parse_bnf(test_data.unsolved_indirect_recursion_book_example)
        g = f.remove_left_recursion(unsolved)
        self.assertEqual(solved, g)

    def test_simple_book_example(self):
        solved = f.parse_bnf(test_data.solved_left_recursion)
        unsolved = f.parse_bnf(test_data.unsolved_left_recursion)
        g = f.remove_left_recursion(unsolved)
        self.assertEqual(solved, g)

    def test_cases(self):
        for case in test_data.examples:
            g = f.parse_bnf(case)
            g = f.remove_left_recursion(g)
            for p in g.iter_productions():
                self.assertFalse(p.is_left_recursive(), msg='{} is left-recursive'.format(p))


class TestRemoveLeftFactoring(unittest.TestCase):
    def test_check_left_factor(self):
        solved = f.parse_bnf(test_data.solved_left_factoring)
        unsolved = f.parse_bnf(test_data.unsolved_left_factoring)
        self.assertTrue(f.check_left_factors(unsolved))
        self.assertFalse(f.check_left_factors(solved))

    def test_book_example(self):
        """
        S -> i E t S | i E t S e S | a
        E -> b
        """
        solved = f.parse_bnf(test_data.solved_left_factoring)
        unsolved = f.parse_bnf(test_data.unsolved_left_factoring)
        g = f.remove_left_factoring(unsolved)
        self.assertEqual(solved, g)

    def test_cases(self):
        for case in test_data.examples:
            g = f.parse_bnf(case)
            g = f.remove_left_factoring(g)
            self.assertFalse(f.check_left_factors(g), msg='{} has left factors'.format(g))


class TestFirst(unittest.TestCase):
    def test_book_example(self):
        g = f.parse_bnf(test_data.book_example)
        answers = {
            'E': {'(', 'id'},
            'E\'': {'+', 'ε'},
            'T': {'(', 'id'},
            'T\'': {'*', 'ε'},
            'F': {'(', 'id'}
        }

        for x, first in answers.items():
            self.assertEqual(first, set(g.first(x)))

    def test_cases(self):
        try:
            for case in test_data.examples:
                g = f.parse_bnf(case)
                h = f.remove_left_recursion(g)
                i = f.remove_left_factoring(h)
                for x in i.nonterminals:
                    i.first(x)
        except Exception as e:
            self.fail(str(e))


class TestFollow(unittest.TestCase):
    def test_book_example(self):
        g = f.parse_bnf(test_data.book_example)
        answers = {
            'E': {'$', ')'},
            'E\'': {'$', ')'},
            'T': {'$', ')', '+'},
            'T\'': {'$', ')', '+'},
            'F': {'$', ')', '*', '+'}
        }

        for x, first in answers.items():
            self.assertEqual(first, set(g.follow(x)))

    def test_cases(self):
        try:
            for case in test_data.examples:
                g = f.remove_left_factoring(f.remove_left_recursion(f.parse_bnf(case)))
                for x in g.nonterminals:
                    g.follow(x)
        except Exception as e:
            self.fail(str(e))


class TestParsingTable(unittest.TestCase):
    def test_book_example(self):
        g = f.parse_bnf(test_data.unsolved_left_recursion)
        # Trust me, this is the answer
        answer = {
            ("T'", '+'): Rule("T'", ('ε',)), ('F', 'id'): Rule('F', ('id',)),
            ("E'", '+'): Rule("E'", ('+', 'T', "E'")), ('E', '('): Rule('E', ('T', "E'")),
            ('T', '('): Rule('T', ('F', "T'")), ("E'", '$'): Rule("E'", ('ε',)),
            ("T'", '*'): Rule("T'", ('*', 'F', "T'")), ("T'", ')'): Rule("T'", ('ε',)),
            ("T'", '$'): Rule("T'", ('ε',)), ("E'", ')'): Rule("E'", ('ε',)), ('T', 'id'): Rule('T', ('F', "T'")),
            ('E', 'id'): Rule('E', ('T', "E'")), ('F', '('): Rule('F', ('(', 'E', ')'))
        }

        table, amb = g.parsing_table(is_clean=False)

        self.assertFalse(amb)
        self.assertEqual(table, answer)

    def test_ambiguous(self):
        for case in test_data.ambiguous:
            g = f.parse_bnf(case)
            table, amb = g.parsing_table(is_clean=False)

            self.assertTrue(amb)

    def test_cases(self):
        try:
            for case in test_data.examples:
                g = f.parse_bnf(case)
                g.parsing_table(is_clean=False)
        except Exception as e:
            self.fail(str(e))


class TestComplete(unittest.TestCase):
    def setUp(self):
        self.g = f.parse_bnf(test_data.exam_exercise)

    def test_parsing(self):
        h = Grammar(start='P')
        h.add_rule(Rule('P', ('D',)))
        h.add_rule(Rule('D', ('T', ':', 'id', ';', 'D')))
        h.add_rule(Rule('D', ('ε',)))
        h.add_rule(Rule('T', ('real',)))
        h.add_rule(Rule('T', ('int',)))
        self.assertEqual(self.g, h)

    def test_terminals(self):
        correct = {':', 'id', ';', 'ε', 'real', 'int'}
        terminals = set(self.g.terminals)
        self.assertEqual(terminals, correct)

    def test_nonterminals(self):
        correct = {'P', 'D', 'T'}
        nonterminals = set(self.g.nonterminals)
        self.assertEqual(nonterminals, correct)

    def test_first(self):
        correct = {
            'P': {'real', 'int', 'ε'},
            'D': {'real', 'int', 'ε'},
            'T': {'real', 'int'}
        }

        for x in self.g.nonterminals:
            self.assertEqual(set(self.g.first(x)), correct[x])

    def test_follow(self):
        correct = {
            'P': {'$'},
            'D': {'$'},
            'T': {':'}
        }

        for x in self.g.nonterminals:
            self.assertEqual(set(self.g.follow(x)), correct[x])

    def test_parsing_table(self):
        correct = {
            ('P', 'real'): Rule('P', ('D',)),
            ('P', 'int'): Rule('P', ('D',)),
            ('P', '$'): Rule('P', ('D',)),
            ('D', 'int'): Rule('D', ('T', ':', 'id', ';', 'D')),
            ('D', 'real'): Rule('D', ('T', ':', 'id', ';', 'D')),
            ('D', '$'): Rule('D', ('ε',)),
            ('T', 'int'): Rule('T', ('int',)),
            ('T', 'real'): Rule('T', ('real',))
        }

        table, amb = self.g.parsing_table()
        self.assertFalse(amb)
        self.assertEqual(table, correct)


if __name__ == '__main__':
    unittest.main()
