from utils import *
from visual import *
import numpy


class BFS:
    """
    Implements the Breadth-First Search (BFS) algorithm for solving search problems.

    Attributes:
        problem (object): The problem instance on which BFS is performed.
        display (Visual, optional): A Visual instance for visualizing the search process.
        search (tuple): The result of the BFS, including the solution node, the number of explored nodes, and the solution path.
        result (str): A string summarizing the search results.
        estimated_time (float): The estimated average runtime for BFS over multiple runs, in milliseconds.
    """

    def __init__(self, prob, display=None):
        """
        Initialize the BFS class with the problem instance and optional display for visualization.

        Parameters:
            prob (object): The problem instance to be solved.
            display (Visual, optional): The display object for visualizing the search.
        """
        self.problem = prob
        self.display = display
        self.search = self.breadth_first_search(prob)
        self.result = search_result(self.search, "BFS")
        self.estimated_time = self.time_estimated()
        

    def breadth_first_search(self, problem):
        """
        Perform the Breadth-First Search on the given problem instance.

        Search for the shallowest nodes in the search tree first using FIFO. 
        Search through the successors of a problem to find a goal. 
        Does not get trapped by loops by checking explored nodes. 

        Parameters:
            problem (object): The problem instance to be solved.

        Returns:
            tuple: A tuple containing the solution node, the count of explored nodes, and the solution path.
        """
        if self.display is None:
            time.sleep(0.01)  # Adding a delay to simulate processing runtime function
        count = 0
        nodes = []

        # Initialize BFS for each initial state in the problem
        for initial in problem.initial:
            node_ini = Node(initial)
            count += 1
            node = {
                'node': node_ini,
                'frontier': deque([node_ini]),
                'explored': []
            }
            if problem.goal_test(node['node'].state, problem.goal):
                if self.display is not None:
                    self.display.draw_update(node['node'].path(), 'path')
                return node['node'], count, node['node'].path()
            nodes.append(node)

        # Iterate through nodes in the BFS frontier
        for node in nodes:
            while any(node['frontier']):
                if not node['frontier']:
                    continue
                node['node'] = node['frontier'].popleft()
                append_unique(node['explored'], [node['node'].state])

                if self.display is not None:
                    self.display.draw_update(node['node'].state, "node")
                    self.display.draw_update(node['explored'], "explored")

                # Expand the node and check goal state
                for child in node['node'].expand(problem):
                    if child.state not in node['explored'] and not child in node['frontier']:
                        count += 1
                        if problem.goal_test(child.state, problem.goal):
                            if self.display is not None:
                                self.display.draw_update(child.path(), 'path')
                            return child, count, child.path()
                        append_unique(node['frontier'], [child])
                        if self.display is not None:
                            self.display.draw_update(child.path(), 'path')
                            self.display.draw_update(child.state, 'frontier')

        return None, count, None
    

    def time_estimated(self):
        """
        Estimate the average runtime for BFS over 10 times.

        Returns:
            float: The average runtime for BFS in milliseconds.
        """
        display_state = self.display  # Save the current display state
        self.display = None  # Disable display to avoid latency during timing
        average = []

        # Run BFS multiple times and calculate average runtime
        for _ in range(10):
            start = 0.01 + time.time()
            self.breadth_first_search(self.problem)
            end = time.time()
            estimated_time = (end - start) * 1000  # Convert to milliseconds
            average.append(estimated_time)

        self.estimated_time = numpy.average(average)
        print(f"Run time in average: {self.estimated_time:.2f} milliseconds")
        self.display = display_state  # Restore the original display state
        return self.estimated_time
