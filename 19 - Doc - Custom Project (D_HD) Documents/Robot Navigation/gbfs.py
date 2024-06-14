from utils import *
from visual import *
import numpy

class GBFS:
    """
    Implements the Greedy Best-First Search (GBFS) algorithm for solving search problems.

    Attributes:
        problem (object): The problem instance on which GBFS is performed.
        display (Visual, optional): A Visual instance for visualizing the search process.
        heuristic (function): The heuristic function used for estimating the cost to reach the goal.
        search (tuple): The result of the GBFS, including the solution node, the number of explored nodes, and the solution path.
        result (str): A string summarizing the search results.
        estimated_time (float): The estimated average runtime for GBFS over multiple runs, in milliseconds.
    """

    def __init__(self, prob, display=None):
        """
        Initialize the GBFS class with the problem instance and optional display for visualization.

        Parameters:
            prob (object): The problem instance to be solved.
            display (Visual, optional): The display object for visualizing the search.
        """
        self.problem = prob
        self.display = display
        self.heuristic = lambda n: prob.h(n, prob.goal)
        self.search = self.greedy_best_first_search(prob, self.heuristic)
        self.result = search_result(self.search, "GBFS")
        self.estimated_time = self.time_estimated()

    def greedy_best_first_search(self, problem, f):
        """
        Perform the Greedy Best-First Search on the given problem instance.

        Search the nodes with the lowest f scores  first.

        GBFS search is a best-first graph search with 
        f(n) = h(n)
            ** h(n) = cost to goal using manhattan distance.

        Does not get trapped by loops by checking explored nodes.

        Parameters:
            problem (object): The problem instance to be solved.
            f (function): The heuristic function to estimate the cost to reach the goal.

        Returns:
            tuple: A tuple containing the solution node, the count of explored nodes, and the solution path.
        """
        if self.display is None:
            time.sleep(0.01)  # Adding a delay to simulate processing runtime function
        count = 0
        f = memoize(f, 'f')
        nodes = []
        explored = []

        # Initialize GBFS for each initial state in the problem
        for initial in problem.initial:
            node = Node(initial)
            frontier = PriorityQueue('min', f)
            count += 1
            if problem.goal_test(node.state, problem.goal):
                if self.display is not None:
                    self.display.draw_update(node.path(), 'path')
                return node, count, node.path()
            nodes.append(node)
        
        # Process each node in the priority queue
        for node in nodes:
            frontier.append(node)
            while frontier:
                node = frontier.pop()
                explored.append(node.state)
                if self.display is not None:
                    self.display.draw_update(node.state, "node")
                    self.display.draw_update(explored, "explored")

                if problem.goal_test(node.state, problem.goal):
                    if self.display:
                        self.display.draw_update(node.path(), 'path')
                    return node, count, node.path()

                if self.display is not None:
                    self.display.draw_update(node.path(), 'path')

                # Expand the node and check goal state
                for child in node.expand(problem):
                    if child.state not in explored and child not in frontier:
                        count += 1
                        frontier.append(child)
                        if self.display is not None:
                            self.display.draw_update(child.state, 'frontier')
                    elif child in frontier:
                        if f(child) < frontier[child]:
                            del frontier[child]
                            count += 1
                            frontier.append(child)
                            if self.display is not None:
                                self.display.draw_update(child.state, 'frontier')

        if self.display is not None:
            self.display.draw_update(explored, "explored")
        return None, count, None

    def time_estimated(self):
        """
        Estimate the average runtime for GBFS over 10 times.

        This method temporarily disables the display to prevent visualization overhead,
        runs the GBFS algorithm multiple times, and calculates the average runtime.

        Returns:
            float: The average runtime for GBFS in milliseconds.
        """
        display_state = self.display  # Save the current display state
        self.display = None  # Disable display to avoid latency during timing
        average = []

        # Run GBFS multiple times and calculate average runtime
        for _ in range(10):
            start = 0.01 + time.time()
            self.greedy_best_first_search(self.problem, self.heuristic)
            end = time.time()
            estimated_time = (end - start) * 1000  # Convert to milliseconds
            average.append(estimated_time)

        self.estimated_time = numpy.average(average)
        print(f"Run time in average: {self.estimated_time:.2f} milliseconds")
        self.display = display_state  # Restore the original display state
        return self.estimated_time
