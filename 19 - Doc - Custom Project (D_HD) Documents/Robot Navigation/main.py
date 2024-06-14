"""
Student name: Khanh Toan Nguyen
Student ID: 104180605
Custom Project: Robot Navigation
Due Date: 14/06/2024

The robot navigation project focuses on creating algorithms and structures for a 
robot to navigate a grid-based environment. It involves implementing search algorithms 
like BFS, DFS, GBFS, A*, Bidirectional BFS(CUS1) and Bidirectional A*(CUS2).
"""

import sys, math
from utils import *
from grid import *
from problem import *
from visual import *
from read_map import ReadMap

from bfs import BFS
from dfs import DFS
from gbfs import GBFS
from astar import Astar
from bidirectional import Bidirectional_BFS, Bidirectional_Astar

def main(): 
    """
    Type of execution:
        - display: To display the GUI of the program (optional - if not it only print results)
        
        - filename: The filename of the map (optional) (List of maps located in utils.py)

        - search strategy: The search strategy used (optional or default as BFS)
            + Type of search strategy: [bfs, dfs, gbfs, astar, cus1, cus2]

    To execute the program, please run the following command
        python(py) main.py 'type of execution in any order'

        examples: 
            python main.py bfs map1.txt display
            python main.py display map8.txt
            python main.py display

    """
    #Read and process the user's input command
    map = ReadMap(sys.argv)

    display = map.display
    search_strat = map.search_strat
    g = Grid(map.filename)
    prob = GridProblem(g.initial_state, g.goal_state, g.grid)

    if map.display == True:
        display = Visual(g.grid,prob)

    if search_strat.upper() == "BFS":
        bfs = BFS(prob,display)
        bfs.result
    elif search_strat.upper() == "DFS":
        dfs = DFS(prob,display)
        dfs.result
    elif search_strat.upper() == "GBFS":
        gbfs = GBFS(prob,display)
        gbfs.result        
    elif search_strat.upper() == "ASTAR":
        astar = Astar(prob,display)
        astar.result
    elif search_strat.upper() == "CUS1":
        bi_bfs = Bidirectional_BFS(prob,display)
        bi_bfs.result
    elif search_strat.upper() == "CUS2":
        bi_astar = Bidirectional_Astar(prob,display)
        bi_astar.result     
    else:
        print("Please try again")
        sys.exit()
    if display is not None:
        display.display_search()

main()