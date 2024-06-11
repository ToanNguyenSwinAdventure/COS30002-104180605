from utils import search_methods, test_file

class ReadMap:
    """
    Handles the user input for configuring search map options.

    The `ReadMap` class reads the input arguments provided by the user in main.py and sets the appropriate attributes
    for the search strategy, file name, display option, and runtime measurement.

    Attributes:
        input (list of str): The list of input arguments provided by the user.
        filename (str or None): The name of the file to be processed. Default is None.
        search_strat (str or None): The search strategy to be used. Default is None.
        display (bool or None): A flag indicating whether to enable display visualization. Default is None.
        runtime (bool or None): A flag indicating whether to measure and display runtime. Default is None.

    Methods:
        control_input(): Processes each argument from the user input and sets the appropriate class attributes.
    """

    def __init__(self, input):
        """
        Initialize the ReadMap class with the user input.

        The constructor sets the initial values of filename, search strategy, display, and runtime to None, 
        and then calls the `control_input` method to process the input arguments.

        Parameters:
            input (list of str): The list of input arguments provided by the user.
        """
        self.input = input
        self.filename = None
        self.search_strat = None
        self.display = None
        self.runtime = None
        self.control_input()

    def control_input(self):
        """
        Read and process each argument from the user input.

        This method iterates over each input argument provided by the user and determines if it matches
        a search strategy, a valid file name, the "DISPLAY" option, or the "RUNTIME" option. If no valid
        search strategy is found in the input, the default strategy is set to "BFS".

        - If the argument matches a search method from `search_methods`, it sets `self.search_strat`.
        - If the argument matches a file from `test_file`, it sets `self.filename`.
        - If the argument is "DISPLAY", it sets `self.display` to True.
        - If the argument is "RUNTIME", it sets `self.runtime` to True.
        - If no valid search strategy is found, it defaults to "BFS".

        **search_methods: this list of search methods located in utils.py
        **test_file: this list of file located in utils.py


        Prints:
            If no search strategy is specified, prints a message indicating to type 'display' for the display option.
        """
        for input in self.input:
            if input.upper() in search_methods:
                self.search_strat = input.upper()
            elif input in test_file:
                self.filename = input
            elif input.upper() == "DISPLAY":
                self.display = True
            elif input.upper() == "RUNTIME":
                self.runtime = True
            else:
                self.search_strat = "BFS"
                print("Type 'display' to the command prompt for the display")
