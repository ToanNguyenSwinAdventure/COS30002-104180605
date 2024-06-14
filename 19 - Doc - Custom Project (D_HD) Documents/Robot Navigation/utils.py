import functools
import ast
import heapq
import re
import time
from statistics import mean
import numpy as np

search_methods = ['BFS', 'DFS', 'GBFS', 'ASTAR', 'CUS1', 'CUS2']

test_file = [
    "map0.txt", "map1.txt", "map2.txt", "map3.txt", "map4.txt", "map5.txt",
    "map6.txt", "map7.txt", "map8.txt", "map9.txt", "map10.txt"
]

def get_num(string):
    """Extracts only numbers from a string using ast.literal_eval."""
    numbers = ast.literal_eval(string)
    return numbers

def grid_block_format(input_string):
    """Identifies the format of a grid block."""
    pattern = r'^\(\d+(,\d+){3}\)$'
    match = re.match(pattern, input_string)
    return bool(match)

def manhattan_distance(state, goal):
    """Calculates the Manhattan distance between two points."""
    x = abs(state[0] - goal[0])
    y = abs(state[1] - goal[1])
    return x + y

def get_state_from_file(line):
    """Extracts states from a file line."""
    states_list = []
    states = line.split('|')
    for state in states:
        a = get_num(state)
        states_list.append(a)
    return states_list

def get_integer_input(prompt):
    """Prompts the user for integer input."""
    while True:
        try:
            user_input = int(input(prompt))
            return user_input
        except ValueError:
            print("Invalid input! Please enter a valid integer.")

def append_unique(target_list, elements):
    """Appends unique elements to a list."""
    for element in elements:
        if element not in target_list:
            target_list.append(element)
    return target_list

def find_intersection(frontier_ini, frontier_goal, flow=True):
    """Finds the intersection between two frontiers of bi-directional nodes."""
    for i in range(len(frontier_ini)):
        for j in range(len(frontier_goal)):
            if frontier_ini[i] == frontier_goal[j]:
                if flow:
                    return frontier_ini[i]
                else:
                    return frontier_goal[j]

def memoize(fn, slot=None, maxsize=32):
    """Memoizes a function."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot) 
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)
    return memoized_fn

class PriorityQueue:
    """A priority queue implementation."""

    def __init__(self, order='min', f=lambda x: x):
        """Initializes the PriorityQueue."""
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':
            self.f = lambda x: -f(x)
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    def append(self, item):
        """Inserts item at its correct position."""
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        """Inserts each item in items at its correct position."""
        for item in items:
            self.append(item)

    def pop(self):
        """Pops and returns the item depending on the order."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def get_list(self):
        """Returns the list of items in the PriorityQueue."""
        return [item[1] for item in self.heap]

    def __len__(self):
        """Returns the current capacity of the PriorityQueue."""
        return len(self.heap)

    def __contains__(self, key):
        """Returns True if the key is in the PriorityQueue."""
        return any([item == key for _, item in self.heap])

    def __getitem__(self, key):
        """Returns the first value associated with key in the PriorityQueue."""
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")

    def __delitem__(self, key):
        """Deletes the first occurrence of key."""
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)

def search_result(result, search_strat):
    """Prints out the result of a search algorithm."""
    path_action = []
    path_node = []
    pNode, explored, path = result
    search_strat = search_strat.upper()
    child = pNode
    if pNode == None:
        print("No goal is reachable; ", explored)
    else:
        for p in path:
                path_node.append(p.state)
        if search_strat == "BIDIRECTIONAL BFS" or search_strat == "BIDIRECTIONAL ASTAR":
            for i in range(len(pNode)):
                if i % 2 == 0:
                    path_test = []
                    while pNode[i].parent:
                        path_test.insert(0, pNode[i].action)
                        pNode[i] = pNode[i].parent
                    for pt in path_test:
                        path_action.append(pt.title())
                if i % 2 == 1:
                    path_test = []
                    while pNode[i].parent:
                        action = pNode[i].action
                        if pNode[i].action == "up":
                            action = "down"
                        if pNode[i].action == "left":
                            action = "right"
                        if pNode[i].action == "right":
                            action = "left"
                        if pNode[i].action == "down":
                            action = "up"
                        path_test.insert(0, action.title())
                        pNode[i] = pNode[i].parent
                    path_test.reverse()
                    for pt in path_test:
                        path_action.append(pt)
        else:
            while pNode.parent:
                path_action.insert(0, pNode.action.title())
                pNode = pNode.parent

        print(f"\nSearch Strategy: {search_strat.upper()}")
        print(f"Final Node: {child} \nNumber of Explored nodes: {explored}")
        print(f"Robot Instructions:\n{path_action}")
