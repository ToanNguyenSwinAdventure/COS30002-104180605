from utils import *
from collections import deque
from grid import *
from problem import *
import time, pygame

from bfs import BFS
from dfs import DFS
from gbfs import GBFS
from astar import Astar
from bidirectional import Bidirectional_BFS, Bidirectional_Astar

pygame.font.init() 
my_font = pygame.font.Font(None, 20) #Set universal font for visualisation

class Button:
    """
    A class to represent a button in the Pygame interface.

    Attributes:
        screen (pygame.Surface): The Pygame surface to draw the button on.
        xPos (int): The x-coordinate of the button's position.
        yPos (int): The y-coordinate of the button's position.
        width (int): The width of the button.
        height (int): The height of the button.
        padding (int): The padding inside the button.
        text (str): The text displayed on the button.
        text_surface (pygame.Surface): The Pygame surface of the rendered text.
        prob (object): The problem instance related to the button.
        test_file (str, optional): The test file name associated with the button.
        manual (bool, optional): Flag indicating if manual grid setting is enabled.
        func (callable, optional): The algorithm function associated with the button.
    """

    def __init__(self, screen, x, y, width, height, text, prob, test_file=None, manual=None):
        """
        Initialize the button with the given parameters.

        Parameters:
            screen (pygame.Surface): The Pygame surface to draw the button on.
            x (int): The x-coordinate of the button's position.
            y (int): The y-coordinate of the button's position.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str): The text displayed on the button.
            prob (object): The problem instance related to the button.
            test_file (str, optional): The test file name associated with the button.
            manual (bool, optional): Flag indicating if manual grid setting is enabled.
        """
        self.screen = screen
        self.xPos = x
        self.yPos = y
        self.width = width
        self.height = height
        self.padding = 5
        self.text = text
        self.text_surface = my_font.render(self.text, True, (0, 0, 0))
        self.prob = prob
        self.test_file = test_file
        self.manual = manual
        self.func = None

    def draw_button(self):
        """
        Draw the button on the Pygame surface.
        """
        pygame.draw.rect(self.screen, (0, 0, 0), (self.xPos, self.yPos, self.width, self.height))
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.xPos + self.padding, self.yPos + self.padding,
                          self.width - self.padding * 2, self.height - self.padding * 2))
        text_width = self.text_surface.get_width()
        text_height = self.text_surface.get_height()
        x = (self.width - text_width) / 2 + self.xPos
        y = (self.height - text_height) / 2 + self.yPos
        self.screen.blit(self.text_surface, (x, y))

    def onPoint(self, coord):
        """
        Check if the given coordinates are within the button's area.

        Parameters:
            coord (tuple): The (x, y) coordinates to check.

        Returns:
            bool: True if the coordinates are within the button's area, False otherwise.
        """
        return self.xPos <= coord[0] <= self.xPos + self.width and self.yPos <= coord[1] <= self.yPos + self.height

    def set_algorithm(self, func):
        """
        Set the search algorithm for the button.

        Parameters:
            func (callable): The search algorithm function.
        """
        self.func = func

    def search_algorithm(self):
        """
        Execute the search algorithm associated with the button.

        Returns:
            callable: The search algorithm function.
        """
        return self.func

           
class Visual:
    """
    A class to handle the visualization of the search algorithms in a grid.

    Attributes:
        grid (list): The grid data structure representing the search space.
        prob (object): The problem instance for the search algorithms.
        screen_width (int): The width of the Pygame display window.
        screen_height (int): The height of the Pygame display window.
        screen (pygame.Surface): The Pygame display surface.
        clock (pygame.time.Clock): Pygame clock for managing frame rate.
        rows (int): Number of rows in the grid.
        columns (int): Number of columns in the grid.
        cell_size (int): Size of each cell in the grid.
        buttons (list): List of Button instances for user interaction.
    """

    def __init__(self, grid, prob, set=None):
        """
        Initialize the visual interface with the grid and problem.

        Parameters:
            grid (list): The grid data structure.
            prob (object): The problem instance.
            set (optional): Additional settings or configurations.
        """
        self.grid = grid
        self.prob = prob
        self.draw_screen()

        self.screen_width = 1100
        self.screen_height = 600
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill((255, 255, 255))
        pygame.display.set_caption("Robot Navigation")
        self.clock = pygame.time.Clock()

    def draw_screen(self):
        """
        Calculate and set the dimensions for the grid display.
        """
        self.rows = len(self.grid[1])
        self.columns = len(self.grid)
        if self.rows > 20 or self.columns > 20:
            if self.columns > self.rows:
                self.width = 800
                self.cell_size = self.width // self.columns
                self.height = self.cell_size * self.rows
            else:
                self.height = 600
                self.cell_size = self.height // self.rows
                self.width = self.cell_size * self.columns
        else:
            self.cell_size = 30
            self.width = self.columns * 30
            self.height = self.rows * 30

    def draw_grid(self):
        """
        Draw the grid lines on the Pygame surface.
        """
        for x in range(0, self.width + 1, self.cell_size):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, self.height))
            for y in range(0, self.height + 1, self.cell_size):
                pygame.draw.line(self.screen, (0, 0, 0), (0, y), (self.width, y))

    def fill_obstacle(self):
        """
        Fill the cells in the grid that represent obstacles or special states.
        """
        for x in range(self.columns):
            for y in range(self.rows):
                if self.grid[x][y] == 1:
                    self.fill_cell(x, y, (128, 128, 128))
                elif self.grid[x][y] == "A":
                    self.fill_cell(x, y, (255, 0, 0))
                elif self.grid[x][y] == "B":
                    self.fill_cell(x, y, (0, 255, 0))

    def reset_grid(self):
        """
        Reset the grid display to the default state.
        """
        for x in range(self.columns):
            for y in range(self.rows):
                if self.grid[x][y] == 0:
                    self.fill_cell(x, y, (255, 255, 255))

    def choose_algo(self, type):
        """
        Set and execute the chosen search algorithm based on the button type.

        Parameters:
            type (str): The type of the search algorithm ("BFS", "DFS", "GBFS", "A*", "CUS1", "CUS2").

        Returns:
            callable: The search algorithm function.
        """
        for button in self.buttons:
            if type == "BFS":
                button.set_algorithm(BFS(self.prob, self))
            elif type == "DFS":
                button.set_algorithm(DFS(self.prob, self))
            elif type == "GBFS":
                button.set_algorithm(GBFS(self.prob, self))
            elif type == "ASTAR":
                button.set_algorithm(Astar(self.prob, self))
            elif type == "CUS1":
                button.set_algorithm(Bidirectional_BFS(self.prob, self))
            elif type == "CUS2":
                button.set_algorithm(Bidirectional_Astar(self.prob, self))
            time.sleep(0.5)
            return button.search_algorithm()

    def set_grid(self, file_name=None):
        """
        Load a new grid from a file and update the display.

        Parameters:
            file_name (str, optional): The name of the file containing the grid data.
        """
        if file_name is not None:
            self.screen.fill((255, 255, 255))
            for button in self.buttons:
                if button.test_file == file_name:
                    new_grid = Grid(file_name)
                    new_prob = GridProblem(new_grid.initial_state, new_grid.goal_state, new_grid.grid)
                    self.grid = new_grid.grid
                    self.prob = new_prob
                    self.draw_screen()
                    self.fill_obstacle()
                    self.draw_grid()
                    self.draw_buttons()
                    pygame.time.delay(300)
                    pygame.display.flip()

    def fill_cell(self, x, y, color):
        """
        Fill a specific cell in the grid with the given color.

        Parameters:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            color (tuple): The RGB color to fill the cell with.
        """
        pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

    def grid_manual(self, manual=None):
        """
        Set up the grid manually through user input.
        User input through the terminal
        Instructions to insert new grid:\n
            1. Set the number of rows.
            2. Set the number of columns.
            3. Set the initial state of x coordinate
            4. Set the initial state of y coordinate
            5. Set the goal state of x coordinate
            6. Set the goal state of y coordinate
            7. Set the wall for the grid following this format:
                '(x,y,width,height)'
            If setting wall is done, type 'none'

        Parameters:
            manual (bool, optional): Flag indicating if manual grid setting is enabled.
        """
        if manual is not None:
            self.screen.fill((255, 255, 255))
            file = []
            rows = get_integer_input("Please enter Row Size: ")
            columns = get_integer_input("Please enter Column Size: ")
            ini_x = get_integer_input("Please enter Initial X coordinate: ")
            ini_y = get_integer_input("Please enter Initial Y coordinate: ")
            goal_x = get_integer_input("Please enter Goal X coordinate: ")
            goal_y = get_integer_input("Please enter Goal Y coordinate: ")
            get_block_grid = True
            blocks = []
            while get_block_grid:
                block_grid = input("Please enter block grid in this format (x, y, width, height) or 'none' to discard: ")

                if grid_block_format(block_grid):
                    block_grid += "\n"
                    blocks.append(block_grid)
                elif block_grid.upper() == "NONE":
                    get_block_grid = False
                else:
                    print("Please enter the correct format (x,y,w,h)")
            file.append(rows)
            file.append(columns)
            file.append(ini_x)
            file.append(ini_y)
            file.append(goal_x)
            file.append(goal_y)
            file.append(blocks)
            g = Grid(grid_manual=file)
            p = GridProblem(g.initial_state, g.goal_state, g.grid)
            self.grid = g.grid
            self.prob = p
            self.draw_screen()
            self.fill_obstacle()
            self.draw_grid()
            self.draw_buttons()
            pygame.display.flip()

    def draw_buttons(self):
        """
        Draw the buttons for selecting algorithms, choosing maps, and creating new grid.
        """
        self.buttons = []
        count = len(search_methods)
        padding = 25
        for i in range(count):
            button = Button(self.screen, 650, ((self.screen_height - padding) / count * i) + padding, 70, 30,
                            search_methods[i], self.prob)
            self.buttons.append(button)

        for t in range(len(test_file)):
            test_button = Button(self.screen, 650 + 70 + padding, ((self.screen_height - padding) / len(test_file) * t) + padding,
                                 160, 30, test_file[t], self.prob, test_file=test_file[t])
            self.buttons.append(test_button)

        grid_manual_button = Button(self.screen, 650 + 70 + 160 + 2 * padding, (self.screen_height - padding) / 2,
                                    170, 30, "New Grid Creation", self.prob, manual=True)
        self.buttons.append(grid_manual_button)
        for button in self.buttons:
            button.draw_button()

    def draw_update(self, cord, type):
        """
        Update the display with the latest state in search algorithm progress.

        Parameters:
            cord (tuple or list): The coordinates or path to update.
            type (str): The type of update ('node', 'explored', 'frontier', 'path').
        """
        if type == 'node':
            x = cord[0]
            y = cord[1]
            self.fill_cell(x, y, (64, 64, 255))
        elif type == 'explored':
            for e in cord:
                x = e[0]
                y = e[1]
                self.fill_cell(x, y, (0, 0, 255))
        elif type == 'frontier':
            x = cord[0]
            y = cord[1]
            self.fill_cell(x, y, (76, 0, 153))
        elif type == 'path':
            path = []
            for p in cord:
                path.append(p.state)
            for p in path:
                x = p[0]
                y = p[1]
                self.fill_cell(x, y, (170, 255, 170))

        self.fill_obstacle()
        self.draw_grid()
        self.draw_buttons()
        pygame.time.delay(30)
        pygame.display.flip()

    def display_search(self):
        """
        Main loop for displaying the search visualization and handling events.
        """
        running = True
        while running:
            for event in pygame.event.get():
                #Allow to exit the program
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                else:
                    #Checking if the Mouse Left is clicking the button
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for button in self.buttons:
                            if button.onPoint(pygame.mouse.get_pos()):
                                self.reset_grid()
                                self.fill_obstacle()
                                self.draw_grid()
                                pygame.time.delay(300)
                                pygame.display.flip()
                                self.choose_algo(button.text)
                                self.set_grid(button.test_file)
                                self.grid_manual(button.manual)
