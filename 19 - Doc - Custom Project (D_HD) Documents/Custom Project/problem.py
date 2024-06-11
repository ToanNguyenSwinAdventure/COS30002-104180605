
from utils import *
from collections import deque
from grid import *
from node import *
import time

class GridProblem():
    """
    Represents a problem for navigating a grid to reach a goal state.

    The `GridProblem` class encapsulates the initial state, goal state(s), and a grid representing 
    the environment. The grid is assumed to be a 2D list where `0` represents a free cell and `1` 
    represents an obstacle. The class provides methods for determining possible actions from a state, 
    generating the result of an action, calculating path cost, and estimating the heuristic distance 
    to the goal.

    Attributes:
        initial (tuple): The initial state represented by coordinates (x, y).
        goal (list of tuples): The goal state(s) represented by coordinates [(x1, y1), (x2, y2), ...].
        grid (list of list of int): The grid environment where `0` is a free cell and `1` is an obstacle.

    Methods:
        goal_test(state, goals): Checks if a given state is a goal state.
        actions(state): Returns a list of possible actions from a given state.
        result(state, action): Returns the resulting state from applying an action to a given state.
        path_cost(cost_so_far, A, action, B): Calculates the cost to reach state B from state A.
        h(node, goal): Estimates the heuristic distance from a node to the closest goal.
    """

    def __init__(self, initial, goal, grid):
        """
        Initialize a `GridProblem` instance.

        Parameters:
            initial (tuple): The initial state represented by coordinates (x, y).
            goal (list of tuples): The goal state(s) represented by coordinates [(x1, y1), (x2, y2), ...].
            grid (list of list of int): The grid environment where `0` is a free cell and `1` is an obstacle.
        """
        self.initial = initial
        self.goal = goal
        self.grid = grid

    def goal_test(self, state, goals):
        """
        Check if a given state is one of the goal states.

        Parameters:
            state (tuple): The state to be tested, represented by coordinates (x, y).
            goals (list of tuples): The goal state(s) to be checked against.

        Returns:
            bool: `True` if the state is a goal state, `False` otherwise.
        """
        for g in goals:
            if state == g:
                return True
        return False

    def actions(self, state):
        """
        Returns a list of possible actions from a given state.

        The method checks for possible movements (up, down, left, right) from the current state 
        considering the boundaries and obstacles in the grid.

        Parameters:
            state (tuple): The current state, represented by coordinates (x, y).

        Returns:
            list of str: A list of possible actions from the current state.
        """
        possible_actions = []
        max_row, max_col = len(self.grid), len(self.grid[0])
        
        if state[0] < 0 or state[0] >= max_row or state[1] < 0 or state[1] >= max_col:
            return possible_actions  # State is out of grid bounds

        if self.grid[state[0]][state[1]] == 1:
            return possible_actions  # State is blocked by an obstacle

        # Check possible moves considering boundaries and obstacles
        if state[1] > 0 and self.grid[state[0]][state[1] - 1] != 1:  # Move Up
            possible_actions.append('up')
        if state[0] > 0 and self.grid[state[0] - 1][state[1]] != 1:  # Move Left
            possible_actions.append('left')
        if state[1] < max_col - 1 and self.grid[state[0]][state[1] + 1] != 1:  # Move Down
            possible_actions.append('down')
        if state[0] < max_row - 1 and self.grid[state[0] + 1][state[1]] != 1:  # Move Right
            possible_actions.append('right')
        
        return possible_actions

    def result(self, state, action):
        """
        Return a new state that results from applying the given action to the current state.

        Assumes the action is valid for the current state and grid configuration.

        Parameters:
            state (tuple): The current state, represented by coordinates (x, y).
            action (str): The action to be applied ('up', 'down', 'left', 'right').

        Returns:
            tuple: The resulting state after applying the action, represented by coordinates (x, y).
        """
        if action == 'up' and state[1] > 0 and self.grid[state[0]][state[1] - 1] != 1:
            return (state[0], state[1] - 1)
        if action == 'down' and state[1] < len(self.grid[0]) - 1 and self.grid[state[0]][state[1] + 1] != 1:
            return (state[0], state[1] + 1)
        if action == 'left' and state[0] > 0 and self.grid[state[0] - 1][state[1]] != 1:
            return (state[0] - 1, state[1])
        if action == 'right' and state[0] < len(self.grid) - 1 and self.grid[state[0] + 1][state[1]] != 1:
            return (state[0] + 1, state[1])
        return state  # No change if the action is invalid or results in an obstacle

    def path_cost(self, cost_so_far, A, action, B):
        """
        Calculate the cost to reach state B from state A.

        Assumes a constant cost of 1 per move.

        Parameters:
            cost_so_far (int): The cost to reach state A.
            A (tuple): The starting state, represented by coordinates (x, y).
            action (str): The action taken to move from state A to state B.
            B (tuple): The resulting state after applying the action, represented by coordinates (x, y).

        Returns:
            int: The updated path cost to reach state B.
        """
        return cost_so_far + 1

    def h(self, node, goal):
        """
        Heuristic function to estimate the distance from a node to the closest goal.

        Uses Manhattan distance to calculate the estimated distance from the node's state to each 
        goal and returns the minimum distance.

        Parameters:
            node: The current node in the search tree.
            goal (list of tuples): The list of goal states to calculate the heuristic against.

        Returns:
            int: The minimum Manhattan distance from the node's state to the closest goal.
        """

        goal_distances = [manhattan_distance(node.state, g) for g in goal]
        return min(goal_distances)
    