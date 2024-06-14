from utils import *
from visual import *
import numpy

class Bidirectional_BFS:
    """
    Implements the bidirectional breadth-first search (BFS) algorithm for solving search problems.

    Attributes:
        problem (object): The problem instance on which bidirectional BFS is performed.
        display (Visual, optional): A Visual instance for visualizing the search process.
        search (tuple): The result of the bidirectional BFS, including the solution nodes, 
                        the number of explored nodes, and the solution path.
        result (str): A string summarizing the search results.
        estimated_time (float): The estimated average runtime for bidirectional BFS over multiple runs, in milliseconds.
    """

    def __init__(self, prob, display=None):
        """
        Initialize the Bidirectional_BFS class with the problem instance and optional display for visualization.

        Parameters:
            prob (object): The problem instance to be solved.
            display (Visual, optional): The display object for visualizing the search.
        """
        self.problem = prob
        self.display = display
        self.search = self.bidirectional_search_bfs(prob)
        self.result = search_result(self.search, "Bidirectional BFS")
        self.estimated_time = self.time_estimated()

    def bidirectional_search_bfs(self, problem):
        """
        Perform the bidirectional breadth-first search (BFS) on the given problem instance.

        The BFS is performed from both the initial state and the goal state, searching the shallowest nodes in the
        search tree first using a FIFO queue. The search is completed when both trees intersect.

        Parameters:
            problem (object): The problem instance to be solved.

        Returns:
            tuple: A tuple containing the solution nodes, the count of explored nodes, and the solution path.
        """
        if self.display is None:
            time.sleep(0.01)  # Adding a delay to simulate processing runtime function
        count = 0
        initial_nodes = []
        goal_nodes = []
        initial_frontier = deque()
        goal_frontier = deque()
        explored = []

        # Initialize BFS search from the initial state
        for initial_state in problem.initial:
            initial_node = Node(initial_state)
            initial_nodes.append(initial_node)
            count += 1
            if problem.goal_test(initial_node.state, problem.goal):
                if self.display is not None:
                    self.display.draw_update(initial_node.path(), 'path')
                return [initial_node], count, initial_node.path()
            initial_frontier.append(initial_node)

        # Initialize BFS search from the goal state
        for goal_state in problem.goal:
            goal_node = Node(goal_state)
            goal_nodes.append(goal_node)
            goal_frontier.append(goal_node)

        # Bidirectional search loop
        while initial_frontier and goal_frontier:
            node_ini = initial_frontier.popleft()
            append_unique(explored, [node_ini.state])
            node_goal = goal_frontier.popleft()
            append_unique(explored, [node_goal.state])

            if self.display is not None:
                self.display.draw_update(node_ini.state, "node")
                self.display.draw_update(explored, "explored")
                self.display.draw_update(node_goal.state, "node")
                self.display.draw_update(explored, "explored")

            # Expand nodes from the initial frontier
            for child_ini in node_ini.expand(problem):
                if child_ini.state not in explored and child_ini not in initial_frontier:
                    append_unique(initial_frontier, [child_ini])
                    count += 1
                    if self.display is not None:
                        self.display.draw_update(child_ini.state, 'frontier')

            # Check for intersection between initial and goal frontiers
            intersection_ini = find_intersection([node_ini], goal_frontier)
            if intersection_ini:
                path_from_initial = intersection_ini.path()
                path_from_goal = node_goal.path()
                final_path = path_from_initial + path_from_goal[::-1]
                if self.display is not None:
                    self.display.draw_update(find_intersection([node_ini], goal_frontier).path(), 'path')
                    self.display.draw_update(find_intersection([node_ini], goal_frontier, False).path(), 'path')
                return [find_intersection([node_ini], goal_frontier), find_intersection([node_ini], goal_frontier, False)], count, final_path

            # Expand nodes from the goal frontier
            for child_goal in node_goal.expand(problem):
                if child_goal.state not in explored and child_goal not in goal_frontier:
                    append_unique(goal_frontier, [child_goal])
                    count += 1
                    if self.display is not None:
                        self.display.draw_update(child_goal.state, 'frontier')

            intersection_goal = find_intersection(initial_frontier, [node_goal])
            if intersection_goal:
                path_from_initial = intersection_goal.path()
                path_from_goal = node_goal.path()
                final_path = path_from_initial + path_from_goal[::-1]
                if self.display is not None:
                    self.display.draw_update(find_intersection(initial_frontier, [node_goal]).path(), 'path')
                    self.display.draw_update(find_intersection(initial_frontier, [node_goal], False).path(), 'path')
                return [find_intersection(initial_frontier, [node_goal]), find_intersection(initial_frontier, [node_goal], False)], count, final_path

            if self.display is not None:
                self.display.draw_update(node_ini.path(), 'path')
                self.display.draw_update(node_goal.path(), 'path')

        if self.display is not None:
            self.display.draw_update(explored, "explored")
        return None, count, None  # No path found

    def time_estimated(self):
        """
        Estimate the average runtime for bidirectional BFS over 10 times.

        This method temporarily disables the display to prevent visualization overhead,
        runs the bidirectional BFS algorithm multiple times, and calculates the average runtime.

        Returns:
            float: The average runtime for bidirectional BFS in milliseconds.
        """
        display_state = self.display  # Save the current display state
        self.display = None  # Disable display to avoid latency during timing
        average = []

        # Run bidirectional BFS multiple times and calculate average runtime
        for _ in range(10):
            start = 0.01 + time.time()
            self.bidirectional_search_bfs(self.problem)
            end = time.time()
            estimated_time = (end - start) * 1000  # Convert seconds to milliseconds
            average.append(estimated_time)

        self.estimated_time = numpy.average(average)
        print(f"Run time in average: {self.estimated_time:.2f} milliseconds")
        self.display = display_state  # Restore the original display state
        return self.estimated_time

class Bidirectional_Astar:
    """
    Implements the bidirectional A* search algorithm for solving search problems.

    Attributes:
        problem (object): The problem instance on which bidirectional A* search is performed.
        display (Visual, optional): A Visual instance for visualizing the search process.
        initial_heuristic (function): The heuristic function for the initial frontier, estimating the cost to the goal.
        goal_heuristic (function): The heuristic function for the goal frontier, estimating the cost to the initial state.
        search (tuple): The result of the bidirectional A* search, including the solution nodes, 
                        the number of explored nodes, and the solution path.
        result (str): A string summarizing the search results.
        estimated_time (float): The estimated average runtime for bidirectional A* search over multiple runs, in milliseconds.
    """

    def __init__(self, prob, display=None):
        """
        Initialize the Bidirectional_Astar class with the problem instance and optional display for visualization.

        Parameters:
            prob (object): The problem instance to be solved.
            display (Visual, optional): The display object for visualizing the search.
        """
        self.problem = prob
        self.display = display

        self.initial_heuristic = lambda i: i.path_cost + prob.h(i, prob.goal)
        self.goal_heuristic = lambda g: g.path_cost + prob.h(g, prob.initial)

        self.search = self.bidirectional_search_a_star(prob, self.initial_heuristic, self.goal_heuristic)
        self.result = search_result(self.search, "Bidirectional Astar")
        self.time_estimated()

    def bidirectional_search_a_star(self, problem, h_i, h_g):
        """
        Perform the bidirectional A* search on the given problem instance.

        The A* search is performed from both the initial state and the goal state, searching the nodes with
        the lowest f scores first. The f(n) score is the sum of g(n) and h(n), where g(n) is the cost to reach
        the node and h(n) is the heuristic estimate of the cost to reach the goal.

        Parameters:
            problem (object): The problem instance to be solved.
            h_i (function): The heuristic function for the initial frontier.
            h_g (function): The heuristic function for the goal frontier.

        Returns:
            tuple: A tuple containing the solution nodes, the count of explored nodes, and the solution path.
        """
        if self.display is None:
            time.sleep(0.01)  # Adding a delay to simulate processing runtime function
        count = 0
        h_i = memoize(h_i or problem.h, 'h')
        h_g = memoize(h_g or problem.h, 'h')

        initial_nodes = []
        goal_nodes = []
        initial_frontier = PriorityQueue('min', h_i)
        goal_frontier = PriorityQueue('min', h_g)
        ini_explored = []
        goal_explored = []
        explored = []

        # Initialize A* search from the initial state
        for initial_state in problem.initial:
            initial_node = Node(initial_state)
            initial_nodes.append(initial_node)
            count += 1
            if problem.goal_test(initial_node.state, problem.goal):
                if self.display is not None:
                    self.display.draw_update(initial_node.path(), 'path')
                return [initial_node], count, initial_node.path()
            initial_frontier.append(initial_node)

        # Initialize A* search from the goal state
        for goal_state in problem.goal:
            goal_node = Node(goal_state)
            goal_nodes.append(goal_node)
            goal_frontier.append(goal_node)

        node_ini = None
        node_goal = None

        # Bidirectional A* search loop
        while initial_frontier and goal_frontier:
            node_ini = initial_frontier.pop()
            append_unique(ini_explored, [node_ini.state])
            append_unique(explored, [ini_explored])

            # Expand nodes from the initial frontier
            for child_ini in node_ini.expand(problem):
                if child_ini.state not in ini_explored and child_ini not in initial_frontier:
                    append_unique(initial_frontier, [child_ini])
                    count += 1
                    if self.display is not None:
                        self.display.draw_update(child_ini.state, 'frontier')
                elif child_ini in initial_frontier:
                    if h_i(child_ini) < initial_frontier[child_ini]:
                        del initial_frontier[child_ini]
                        append_unique(initial_frontier, [child_ini])
                        count += 1
                        if self.display is not None:
                            self.display.draw_update(child_ini.state, 'frontier')
            if self.display is not None:
                self.display.draw_update(node_ini.state, "node")
                self.display.draw_update(ini_explored, "explored")

            if node_goal is not None:
                if self.display is not None:
                    self.display.draw_update(node_goal.state, "node")
                    self.display.draw_update(goal_explored, "explored")

            # Check for intersection between initial and goal frontiers
            intersection_ini = find_intersection([node_ini], goal_frontier.get_list())
            if intersection_ini:
                path_from_initial = intersection_ini.path()
                path_from_goal = node_goal.path()
                final_path = path_from_initial + path_from_goal[::-1]
                if self.display is not None:
                    self.display.draw_update(find_intersection([node_ini], goal_frontier.get_list()).path(), 'path')
                    self.display.draw_update(find_intersection([node_ini], goal_frontier.get_list(), False).path(), 'path')
                return [find_intersection([node_ini], goal_frontier.get_list()), find_intersection([node_ini], goal_frontier.get_list(), False)], count, final_path

            node_goal = goal_frontier.pop()
            append_unique(goal_explored, [node_goal.state])
            append_unique(explored, [goal_explored])
            if self.display is not None:
                self.display.draw_update(node_goal.state, "node")
                self.display.draw_update(goal_explored, "explored")

            # Expand nodes from the goal frontier
            for child_goal in node_goal.expand(problem):
                if child_goal.state not in goal_explored and child_goal not in goal_frontier:
                    append_unique(goal_frontier, [child_goal])
                    count += 1
                    if self.display is not None:
                        self.display.draw_update(child_goal.state, 'frontier')
                elif child_goal in goal_frontier:
                    if h_g(child_goal) < goal_frontier[child_goal]:
                        del goal_frontier[child_goal]
                        append_unique(goal_frontier, [child_goal])
                        count += 1
                        if self.display is not None:
                            self.display.draw_update(child_goal.state, 'frontier')

            intersection_goal = find_intersection(initial_frontier.get_list(), [node_goal])
            if intersection_goal:
                path_from_initial = intersection_goal.path()
                path_from_goal = node_goal.path()
                final_path = path_from_initial + path_from_goal[::-1]
                if self.display is not None:
                    self.display.draw_update(find_intersection(initial_frontier.get_list(), [node_goal]).path(), 'path')
                    self.display.draw_update(find_intersection(initial_frontier.get_list(), [node_goal], False).path(), 'path')
                return [find_intersection(initial_frontier.get_list(), [node_goal]), find_intersection(initial_frontier.get_list(), [node_goal], False)], count, final_path

            if self.display is not None:
                self.display.draw_update(node_ini.path(), 'path')
                self.display.draw_update(node_goal.path(), 'path')

        if self.display is not None:
            self.display.draw_update(ini_explored, "explored")
            self.display.draw_update(goal_explored, "explored")
        return None, count, None  # No path found

    def time_estimated(self):
        """
        Estimate the average runtime for bidirectional A* search over 10 iterations.

        This method temporarily disables the display to prevent visualization overhead,
        runs the bidirectional A* search algorithm multiple times, and calculates the average runtime.

        Returns:
            float: The average runtime for bidirectional A* search in milliseconds.
        """
        display_state = self.display  # Save the current display state
        self.display = None  # Disable display to avoid latency during timing
        average = []

        # Run bidirectional A* search multiple times and calculate average runtime
        for _ in range(10):
            start = 0.01 + time.time()
            self.bidirectional_search_a_star(self.problem, self.initial_heuristic, self.goal_heuristic)
            end = time.time()
            estimated_time = (end - start) * 1000  # Convert seconds to milliseconds
            average.append(estimated_time)

        self.estimated_time = numpy.average(average)
        print(f"Run time in average: {self.estimated_time:.2f} milliseconds")
        self.display = display_state  # Restore the original display state
        return self.estimated_time

