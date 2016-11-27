# -*- coding: utf-8 -*-


class InvalidProduction(Exception):
    def __init__(self, message, production):
        super().__init__(message)
        self.production = production


class Rule:
    def __init__(self, head, body):
        hash(head)
        hash(body)
        self.head = head
        self.body = body
        if not isinstance(self.body, tuple):
            raise ValueError("Body of production must be a tuple")
        if (head,) == body:
            raise InvalidProduction("Invalid production. Head is the same as body.", self)

    def is_left_recursive(self):
        """
        Check if production is left-recursive (immediate)
        :param head: right side of production
        :param body: left side of production
        :return: True if production is left-recursive, False otherwise
        """
        return self.body and self.head == self.body[0]

    def __eq__(self, other):
        return self.head == other.head and self.body == other.body

    def __str__(self):
        return "{} → {}".format(self.head, ' '.join(self.body))

    def __repr__(self):
        return "Rule({}, {})".format(repr(self.head), self.body)

    def __hash__(self):
        return hash((self.head, self.body))
