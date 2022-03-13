# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 12:33:23 2022

@author: yifei
"""

from heapq import *

import itertools

REMOVED = '<removed-state>'  # placeholder for a removed state


class modified_heapq(object):
    def __init__(self):
        self.hq = []  # list of entries arranged in a heap
        self.entry_finder = {}  # mapping of states to entries
        self.counter = itertools.count()  # unique sequence count

    def add_state(self, state):
        """Add a new state or update the cost of an existing state"""
        node = state.get_node()
        f = state.get_f()
        if node in self.entry_finder:
            self.remove_state(node)

        count = next(self.counter)
        entry = [f, count, state]
        self.entry_finder[node] = entry
        heappush(self.hq, entry)

    def remove_state(self, node):
        """Mark an existing state as REMOVED.  Raise KeyError if not found."""
        entry = self.entry_finder.pop(node)
        entry[-1] = REMOVED

    def pop_state(self):
        """Remove and return the lowest priority state. Raise KeyError if empty."""
        while self.hq:
            priority, count, state = heappop(self.hq)
            if state is not REMOVED:
                del self.entry_finder[state.get_node()]
                return state
        raise KeyError('pop from an empty priority queue')
