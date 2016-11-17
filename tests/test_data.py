# -*- coding: utf-8 -*-

examples = []
ambiguous = []

examples.append("E -> T E'\n"
                "E' -> + T E' | ε\n"
                "T -> F T'\n"
                "T' -> * F T' | ε\n"
                "F -> ( E ) | id")

book_example = examples[-1]

solved_left_recursion = examples[-1]

examples.append("S -> A a | b\n"
                "A -> A c | S d | ε")

unsolved_indirect_recursion_book_example = examples[-1]
ambiguous.append(examples[-1])

examples.append("S -> A a | b\n"
                "A -> A' | b d A'\n"
                "A' -> c A' | a d A' | ε")

solved_indirect_recursion_book_example = examples[-1]

examples.append("E -> E + T | T\n"
                "T -> T * F | F\n"
                "F -> ( E ) | id")
unsolved_left_recursion = examples[-1]

examples.append("S -> A | B\n"
                "A -> a A b | ε\n"
                "B -> a B b b | ε")

ambiguous.append(examples[-1])

examples.append("E -> pa Q R | pa Q S | pa T\n"
                "U -> e")

examples.append("S -> i E t S | i E t S e S | a\n"
                "E -> b")

unsolved_left_factoring = examples[-1]

examples.append("S -> i E t S S' | a\n"
                "S' -> ε | e S\n"
                "E -> b")

solved_left_factoring = examples[-1]

examples.append("X -> a A\n"
                "A -> x X")

examples.append("S -> ( A ) | ε\n"
                "A -> T E\n"
                "E -> & T E | ε\n"
                "T -> ( A ) | a | b | c")

examples.append("L -> % w D | U#\n"
                "U -> ! w D U | ε\n"
                "D -> : w D | w L")

examples.append("S -> A B e\n"
                "A -> d B | a S | c\n"
                "B -> a S | c")

examples.append("Exp -> Exp + Exp2 | Exp - Exp2 | Exp2\n"
                "Exp2 -> Exp2 * Exp3 | Exp2 / Exp3 | Exp3\n"
                "Exp3 -> num | ( Exp )")

examples.append("E -> T + E | T\n"
                "T -> int | int * T | ( E )")
