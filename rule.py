# -*- coding: utf-8 -*-


class Rule:
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def __str__(self):
        return "{} -> {}".format(self.head, ' '.join(self.body))

    def __repr__(self):
        return "{} -> {}".format(self.head, self.body)
