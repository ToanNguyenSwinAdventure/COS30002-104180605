
class Node:
    """
    Represents a node in a search tree.

    The `Node` class encapsulates a state, its parent node, the action that led to this state, 
    the path cost to reach this state, and the depth of the node in the search tree. It also 
    provides methods to expand the node by generating child nodes and to retrieve the path 
    from the root node to the current node.

    Attributes:
        state: The state represented by this node.
        parent (Node, optional): The parent node of this node. Default is None.
        action: The action that led to this state. Default is None.
        path_cost (float): The cost of the path from the initial state to this node. Default is 0.
        depth (int): The depth of the node in the search tree. Default is 0 for the root node.

    Methods:
        expand(problem): Expands this node by generating its children.
        child_node(problem, action): Creates a child node from this node by applying an action.
        solution(): Returns the sequence of actions to reach this node from the root node.
        path(): Returns the sequence of nodes from the root to this node.
        __lt__(node): Less-than comparison based on the state.
        __eq__(other): Equality comparison based on the state.
        __hash__(): Returns a hash value for the node, based on its state.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """
        Initialize a `Node` instance.

        Parameters:
            state: The state represented by this node.
            parent (Node, optional): The parent node of this node. Default is None.
            action: The action that led to this state. Default is None.
            path_cost (float): The cost of the path from the initial state to this node. Default is 0.

        Sets the depth of the node, which is one more than its parent's depth if the parent exists.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        """
        Return a string representation of the node.

        Returns:
            str: A string representing the node's state.
        """
        return f"<Node {self.state}>"

    def expand(self, problem):
        """
        Generate the child nodes of this node.

        Expands this node by applying each action available in the given problem to the node's state.

        Parameters:
            problem: The problem instance that provides the actions and transition model.

        Returns:
            list of Node: The list of child nodes.
        """
        child_nodes = []
        for action in problem.actions(self.state):
            child_node = self.child_node(problem, action)
            child_nodes.append(child_node)
        return child_nodes

    def child_node(self, problem, action):
        """
        Create a child node from this node by applying an action.

        Parameters:
            problem: The problem instance that provides the transition model.
            action: The action to apply to the node's state.

        Returns:
            Node: The resulting child node.
        """
        next_state = problem.result(self.state, action)
        next_node = Node(
            next_state,
            self,
            action,
            problem.path_cost(self.path_cost, self.state, action, next_state)
        )
        return next_node

    def solution(self):
        """
        Return the sequence of actions to reach this node from the root node.

        Returns:
            list: The list of actions from the root node to this node.
        """
        return [node.action for node in self.path()[1:]]

    def path(self):
        """
        Return the sequence of nodes from the root to this node.

        Constructs the path by following the parent links from this node back to the root node.

        Returns:
            list of Node: The list of nodes from the root to this node.
        """
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __lt__(self, node):
        """
        Compare two nodes based on their state.

        Parameters:
            node: The other node to compare to.

        Returns:
            bool: True if this node's state is less than the other node's state.
        """
        return self.state < node.state

    def __eq__(self, other):
        """
        Check if two nodes are equal based on their state.

        Parameters:
            other: The other node to compare to.

        Returns:
            bool: True if the nodes' states are equal.
        """
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        """
        Return a hash value for the node based on its state.

        Returns:
            int: The hash value of the node's state.
        """
        return hash(self.state)
