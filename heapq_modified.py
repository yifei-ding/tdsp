# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 12:33:23 2022

@author: yifei
"""

from heapq import *

import itertools

hq = []  # list of entries arranged in a heap
entry_finder = {}  # mapping of states to entries
REMOVED = '<removed-state>'  # placeholder for a removed state
counter = itertools.count()  # unique sequence count


def add_state(state):
    """Add a new state or update the cost of an existing state"""
    node = state.get_node()
    f = state.get_f()
    if node in entry_finder:
        remove_state(node)
    count = next(counter)
    entry = [f, count, state]
    entry_finder[node] = entry
    heappush(hq, entry)


def remove_state(node):
    """Mark an existing state as REMOVED.  Raise KeyError if not found."""
    entry = entry_finder.pop(node)
    entry[-1] = REMOVED


def pop_state():
    """Remove and return the lowest priority state. Raise KeyError if empty."""
    while hq:
        priority, count, state = heappop(hq)
        if state is not REMOVED:
            del entry_finder[state.get_node()]
            return state
    raise KeyError('pop from an empty priority queue')
