# -*- coding: utf-8 -*-
from collections import Hashable


class Rule:
    def __init__(self, head, body):
        hash(head)
        hash(body)
        self.head = head
        self.body = body

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
        return "{} -> {}".format(self.head, ' '.join(self.body))

    def __repr__(self):
        return "{} -> {}".format(self.head, self.body)

    def __hash__(self):
        return hash((self.head, self.body))
