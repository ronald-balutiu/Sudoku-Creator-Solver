#!/usr/bin/python

# Imports for Python 3.X
try:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfile
    from random import randrange

# Imports for Python 2.X
except:
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfile
    import ttk
    from random import randrange


# Globals
# Here is board size, must be a multiple of 9 or else looks off in python 2
WIDTH = HEIGHT = 702
BUFFER = 20  # Set Margin Buffer
NORMAL_COLOR = '#f2f2f0'  # Background color when unchecked
CHECKED_COLOR = '#e0e0da'  # Box color when checked
EMPTY_SQUARES = 50 # Number of empty squares you wish to have. Above 55, preformance may vary!

# NOTE: All numbers in the grid are handled as strings.
# This is to make loading and saving simpler. Also, string manipulation is nice.

# Exception Handler for the Game
class SudokuError(Exception):
    pass


# Board Handler for the Game
class SudokuBoard:

    # Main board class
    def __init__(self):
        self.grid = None
        self.original = None

    # Sets all values to 0
    def set(self):
        self.grid = [['0' for x in range(9)] for y in range(9)]

    # Returns requested row.
    def get_row(self, row):
        return self.grid[row]

    # Returns requested column
    def get_column(self, column):
        values = []
        for y in self.grid:
            values.append(y[column])
        return values

    # Input coordinates, and returns all values in that portion
    # of the board.
    def get_section(self, row, column):
        rows = range((row // 3 * 3), ((row + 3) // 3 * 3))
        columns = range((column // 3 * 3), ((column + 3) // 3 * 3))
        values = []
        for r in rows:
            for c in columns:
                values.append(self.grid[r][c])
        return values

    # Sets value on board. Checks to see if valid move first.
    # Note that value passed in must be a digit due to check in GUI.
    def set_value(self, row, column, value):
        # Cannot be 0
        if value == '0':
            raise SudokuError('Value cannot be 0')
        # Cannot be in row
        for row_value in self.get_row(row):
            if value == row_value:
                raise SudokuError('Value already in row!')
        # Cannot be in column
        for column_value in self.get_column(column):
            if value == column_value:
                raise SudokuError('Value already in column!')
        # Cannot be in section
        for section_value in self.get_section(row, column):
            if value == section_value:
                raise SudokuError('Value already in section!')
        self.grid[row][column] = value

    # Randomly generates a new board
    # The board is not guaranteed to be unique nor have a singular solution
    def new_board(self):
        # Gets a random square on the board
        def get_random_sqr():
            sqr = randrange(1,81)
            x = sqr // 9
            y = sqr % 9
            return x,y

        # Clear the board to generate new one
        self.set()
        self.original = None

        # Runs the solver to generate and initialize a 'random' correct board
        xi, yi = get_random_sqr()
        number = str(randrange(1,10))
        self.grid[xi][yi] = number
        initial_solve = self.solve_board()
        for x in range(9):
            for y in range(9):
                self.grid[x][y] = initial_solve[(x,y)]

        # While we have more than 31 filled in squares, pick a random square and remove it
        # If u can replace that square and solve it with another number, solution is not unique
        # If you cannot, then leave it blank and keep going
        empty_count = 0
        while (empty_count < EMPTY_SQUARES):
            # Initialize checked squares on this run through
            checked_squares = set()

            old = '0'
            # Randomly get a square that is filled in and not checked before
            while old == '0':   
                xr,yr = get_random_sqr()
                if (xr,yr) not in checked_squares:
                    old = str(self.grid[xr][yr])
                ## If checked all filled in squares, try again
                if (81 - empty_count) == len(checked_squares):
                    return new_board()

            # Try all possible replacements
            for i in range(1,10):
                replace = str(i)
                # Make sure you don't try the same number
                if old != replace:
                    # Put in the replacement and see if you can solve the board    
                    self.grid[xr][yr] = replace
                    solved = self.solve_board()
                    if solved:
                        # Not unique, revert back to filled in square and try again
                        self.grid[xr][yr] = old
                        checked_squares.add((xr,yr))
                        break
                    else:
                        if old == '9' and replace == '8':
                            self.grid[xr][yr] = '0'
                            empty_count += 1
                            break
                        if replace == '9':
                            self.grid[xr][yr] = '0'
                            empty_count += 1
                            break

        return


    # Loads the board into the Class as a 2d array.
    # Inputs are passed through GUI (that is where we get the two lines)
    def load_board(self, original, numbers):
        self.original = original
        if not numbers:  # If loading a fresh board
            numbers = self.original
        if len(numbers) != 81:
            raise SudokuError('Not enough numbers in board')
        for i in range(len(numbers)):
            if not numbers[i].isdigit():
                raise SudokuError(
                    'Non valid character detected. Must be between 0-9')

        temp_board = [numbers[i * 9:(i + 1) * 9] for i in range(9)]
        for x in range(9):
            for y in range(9):
                self.grid[x][y] = temp_board[x][y]
        return

    # Returns the original board and current board as strings
    # GUI handles saving to file
    def save_board(self):
        original = self.original
        current = ''
        for x in range(9):
            for y in range(9):
                current += self.grid[x][y]
        return original, current

    # Resets the board back to the original state
    def clear_board(self):
        # Clearing from a loaded or created board
        if self.original:
            self.load_board(self.original, self.original)
        # Clearing from an empty board
        else:
            self.set()
        return

    def solve_board(self):
        def some(items):
            for item in items:
                if item:
                    return item
            return False

        def return_peers_dict():
            ## Format is {(Square):[peer1,peer2,...peerx]}
            ## Used to have a permanent list of a square's peers
            peers = {}
            # For every square
            for x in range(9):
                for y in range(9):
                    group = []
                    # Add the column
                    for row in range(9):
                        group.append((row, y))
                    # Add the row
                    for column in range(9):
                        if (x, column) not in group:
                            group.append((x, column))
                    # Add the section
                    rows = range((x // 3 * 3), ((x + 3) // 3 * 3))
                    columns = range((y // 3 * 3), ((y + 3) // 3 * 3))
                    for r in rows:
                        for c in columns:
                            if (r, c) not in group:
                                group.append((r, c))
                    if (x,y) in group:
                        group.remove((x,y))
                    peers[(x, y)] = group
            return peers

        def init_possible_values(peers):
            ## For each square, keeps track of the possible values it may have
            values = {}
            options = '123456789'
            # Put each spot into a values dict containing all the possible values of that sq
            for x in range(9):
                for y in range(9):
                        values[(x, y)] = options
            for x in range(9):
                for y in range(9):
                    if self.grid[x][y] in options and not assign_value(values, peers, (x,y), self.grid[x][y]):
                        return False
            return values

        def eliminate_possible_values(values, peers, square, value):
            # Go through the board, and eliminate values based on what is currently placed
            if value not in values[square]:
                return values
            values[square] = values[square].replace(str(value), '')
            if len(values[square]) == 0:
                return False
            elif len(values[square]) == 1:
                forced_value = values[square]
                if not all(eliminate_possible_values(values,peers,more_squares,forced_value) for more_squares in peers[square]):
                    return False
            return values

        def assign_value(values, peers, square, value):
            other_values = values[square].replace(value,'')
            if all(eliminate_possible_values(values, peers, square, value2) for value2 in other_values):
                return values
            else:
                return False

        def depth_first_search(values, peers):
            squares = []
            for x in range(9):
                for y in range(9):
                    squares.append((x,y))
            if values is False:
                return False
            if all(len(values[square]) == 1 for square in squares):
                return values
            n,square = min((len(values[square]), square) for square in squares if len(values[square]) > 1)
            return some(depth_first_search(assign_value(values.copy(), peers, square, value), peers) for value in values[square])

        peers = return_peers_dict()
        values = init_possible_values(peers)

        return depth_first_search(values, peers)


# Contains a Sudoku Board. Stores the state of the game.
# Used to allow user to reattampt board from scratch.
# Frame is gathered from tkinter
class SudokuGUI(Frame):

    def __init__(self, parent, board):
        Frame.__init__(self, parent)
        parent.title('Sudoku by Ronald Balutiu')  # Set title
        self.board = board
        self.current = None
        board_frame = Frame(self)

        # Buttons Logic Below
        # New Game
        self.new_game = Button(board_frame, command=self.new_game, text='New Game')
        self.new_game.pack(side='left', fill='x', expand='1')

        # Save Game
        self.save_game = Button(
            board_frame, command=self.save_game, text='Save Game')
        self.save_game.pack(side='left', fill='x', expand='1')

        # Load Game
        self.load_game = Button(
            board_frame, command=self.load_game, text='Load Game')
        self.load_game.pack(side='left', fill='x', expand='1')

        # Reset Game
        self.clear_board = Button(
            board_frame, command=self.clear_board, text='Clear Board')
        self.clear_board.pack(side='left', fill='x', expand='1')

        # Reset Game
        self.solve_board = Button(
            board_frame, command=self.solve_board, text='Solve Board')
        self.solve_board.pack(side='left', fill='x', expand='1')

        board_frame.pack(side='bottom', fill='x', expand='1')
        self.make_boxes()
        self.canvas.bind("<Button-1>", self.canvas_mouse_logic)
        self.canvas.bind("<Key>", self.canvas_keyboard_press)
        self.pack()

    # Begin Canvas Functions
    # Syncs Grid and Board
    # Also where we limit colors!
    def sync_grid(self):
        grid = self.board.grid
        original = self.board.original
        for x in range(9):
            for y in range(9):
                if int(grid[x][y]) > 0:
                    self.canvas.itemconfig(
                        self.sections[x][y][1][1], text=str(grid[x][y]), fill='sea green')
                if int(grid[x][y]) <= 0:
                    self.canvas.itemconfig(self.sections[x][y][1][1], text='')
                if original:
                    if original[x * 9 + y] != '0':
                        self.canvas.itemconfig(
                            self.sections[x][y][1][1], text=str(grid[x][y]), fill='black')

    # Creates Sudoku Grid
    def make_boxes(self):
        canvas = Canvas(self, bg=NORMAL_COLOR, width=str(
            WIDTH + BUFFER * 2), height=str(HEIGHT + BUFFER * 2), highlightthickness=0)

        canvas.pack(side='top', fill='both', expand='1')
        self.sections = [[[0 for z in range(2)]
                          for y in range(9)] for x in range(9)]

        # x and y are to be the grid location on the board
        # For z: 0 will contain the big rectangles, 1 contains a tuple where [0] is the small rectangle and [1] is its text
        row_size = WIDTH / 9
        section_size = WIDTH / 3

        # Make grid
        for x in range(9):
            for y in range(9):
                # Makes smaller boxes
                x_size = x * row_size + BUFFER
                y_size = y * row_size + BUFFER
                box = canvas.create_rectangle(
                    x_size, y_size, x_size + row_size, y_size + row_size, outline='light gray')
                canvas.tag_lower(box)
                text = canvas.create_text(
                    x_size + row_size / 2, y_size + row_size / 2, font =('TkDefaultFont', 18) , text='')
                self.sections[x][y][1] = (box, text)

        # Makes larger sections
        for x in range(3):
            for y in range(3):
                big_x = x * section_size + BUFFER
                big_y = y * section_size + BUFFER
                canvas.create_rectangle(
                    big_x, big_y, big_x + section_size, big_y + section_size, outline='black')

        self.canvas = canvas
        self.sync_grid()

    # Keyboard Logic
    def canvas_keyboard_press(self, event):
        if self.current:
            (x, y) = self.current
            # Prevents modifying original square
            if self.board.original:
                if self.board.original[x * 9 + y] != '0':
                    raise SudokuError('You cannot modify such a square!')
            # Checks to see if digit
            if event.char.isdigit():
                self.board.set_value(x, y, event.char)
                self.sync_grid()
            # On 'p', turns text red.
            elif event.char == 'p':
                self.canvas.itemconfig(
                    self.sections[x][y][1][1], fill='red')
            # On 'o', turns text back to green.
            elif event.char == 'o':
                self.canvas.itemconfig(
                    self.sections[x][y][1][1], fill='sea green')
            # On 'c', clears tile.
            elif event.char == 'c':
                self.board.grid[x][y] = '0'
                self.sync_grid()

    # Mouse Logic
    def canvas_mouse_logic(self, event):
        self.canvas.focus_set()
        if self.current:
            cx = self.current[0]
            cy = self.current[1]
            ## Gets around accidentally clicking outside the grid and bricking the game
            try:
                self.canvas.itemconfig(
                    self.sections[cx][cy][1][0], fill=NORMAL_COLOR)
            except:
                pass
        row_size = WIDTH / 9
        if event.x > row_size:
            x = int(event.x / row_size)
        else:
            x = 0
        if event.y > row_size:
            y = int(event.y / row_size)
        else:
            y = 0
        self.current = (x, y)
        self.canvas.itemconfig(self.sections[x][y][1][0], fill=CHECKED_COLOR)
        box_d = self.canvas.bbox(self.sections[x][y][0])

    # New Game
    def new_game(self):
        self.board.new_board()
        self.sync_grid()
        self.mainloop()

    # Saves Game
    def save_game(self):
        f = asksaveasfile(mode='w', defaultextension='.txt')
        # User hit cancel
        if f is None:
            return
        original, current = self.board.save_board()
        # User wants to save an unloaded board for some reason
        if original:
            f.write(original + '\n')
        f.write(current)
        f.close()
        self.mainloop()

    # Loads Game
    def load_game(self):
        filename = askopenfilename()
        if filename is '':
            return
        data = []
        # If possible, read first two lines
        with open(filename, 'r') as f:
            for i in range(2):
                data.append(f.readline().rstrip())
        # If no input, raise error
        if len(data) == 0:
            raise SudokuError('No input detected')
        # If only one line, say no current state
        if len(data) == 1:
            data.append(None)
        # first line will be original board, second line will be user's changes
        self.board.load_board(data[0], data[1])
        self.sync_grid()
        self.mainloop()

    # Clears board back to original state
    def clear_board(self):
        self.board.clear_board()
        self.sync_grid()

    # Solves board if possible
    def solve_board(self):
        solved = self.board.solve_board()
        if solved == False:
            raise SudokuError('Not able to solve board from this position!!!')
        else:
            for x in range(9):
                for y in range(9):
                    self.board.grid[x][y] = solved[(x,y)]
        self.sync_grid()
        self.mainloop()

board = SudokuBoard()
board.set()
tk = Tk()
gui = SudokuGUI(tk, board)
gui.mainloop()
