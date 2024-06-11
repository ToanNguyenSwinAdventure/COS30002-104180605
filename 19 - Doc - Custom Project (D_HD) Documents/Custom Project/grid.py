import sys
import time
from utils import *

class Grid:
    """Represents a grid environment.

    Args:
        filename (str): The name of the file containing the grid map. Default is None.
        grid_manual (list): A list specifying the grid manually. Default is None.

    Attributes:
        rows (int): The number of rows in the grid.
        columns (int): The number of columns in the grid.
        grid (list): A 2D list representing the grid environment.
        initial_state (list): A list of initial state coordinates.
        goal_state (list): A list of goal state coordinates.
        grid_block (list): A list of grid block coordinates.

    Methods:
        initial_map(): Initializes the grid map based on the provided information.
    """

    def __init__(self, filename=None, grid_manual=None):
        """
        Initializes the Grid object.

        If `filename` is provided, the grid map will be read from the file.
        If `grid_manual` is provided, the grid map will be initialized manually.

        Args:
            filename (str): The name of the file containing the grid map. Default is None.
            grid_manual (list): A list specifying the grid manually. Default is None.
        """
        # Initialization based on filename or grid_manual
        if filename is None:
            grid_size = get_num('[5,11]')
            self.initial_state = get_state_from_file('(0,1)')
            self.goal_state = get_state_from_file('(7,0) | (10,3)')
            self.grid_block = ['(2,0,2,2)\n', '(8,0,1,2)\n', '(10,0,1,1)\n', '(2,3,1,2)\n', '(3,4,3,1)\n', '(9,3,1,1)\n', '(8,4,2,1)\n', '\n']
        else:
            try:
                dir = f"maps/{filename}"
                with open(dir) as f:
                    grid_size = get_num(f.readline())
                    self.initial_state = get_state_from_file((f.readline()))
                    self.goal_state = get_state_from_file((f.readline()))
                    self.grid_block = f.readlines()
            except:
                print("No file in directory")
                sys.exit()
        if grid_manual is not None:
            grid_size = get_num('[{},{}]'.format(grid_manual[0], grid_manual[1]))
            self.initial_state = get_state_from_file("({},{})".format(grid_manual[2], grid_manual[3]))
            self.goal_state = get_state_from_file("({},{})".format(grid_manual[4], grid_manual[5]))
            self.grid_block = grid_manual[6]

        self.rows = grid_size[0]
        self.columns = grid_size[1]
        self.grid = [[0 for _ in range(self.rows)] for _ in range(self.columns)]

        self.initial_map()

        self.grid_block = set()

    def initial_map(self):
        """Initializes the grid map based on the provided information."""
        try:
            for i in self.initial_state:
                self.grid[i[0]][i[1]] = 'A'
            for g in self.goal_state:
                self.grid[g[0]][g[1]] = 'B'

            for line in self.grid_block:
                if grid_block_format(line):
                    try:
                        a = get_num(line)
                        for i in range(a[0], a[0] + a[2]):
                            for j in range(a[1], (a[1] + a[3])):
                                self.grid[i][j] = 1
                    except:
                        continue
        except:
            for i in range(1, 4):
                print('.' * i)
                time.sleep(1)
            print("File for Map Initialize Error\nPlease try again with another file")
            sys.exit()
