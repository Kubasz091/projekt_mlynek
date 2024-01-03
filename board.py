def guess_what_user_meant(number: int, possible_numbers: list):
    '''
    Given a number and a list of possible numbers, returns the number
    in the list that is closest to the given number.

    Parameters:
    number (int): The number to compare against.
    possible_numbers (list): A list of numbers to compare.

    Returns:
    int: The number in the list that is closest to the given number.
    '''
    guess = 0
    i = 0
    for num in possible_numbers:
        if abs(number - num) < abs(number - possible_numbers[guess]):
            guess = i
        i += 1
    return possible_numbers[guess]


def calc_terminal_board_size(no_of_sqr: int):
    '''
    Given the number of squares on a board,
    returns the size of the board in terminal characters.

    Parameters:
    no_of_sqr (int): The number of squares on the board.

    Returns:
    tuple: A tuple containing the x and y sizes of the board 
    in terminal characters.
    '''
    return ((15 + (12 * (no_of_sqr - 1))) * 2, 15 + (12 * (no_of_sqr - 1)))


class WrongBoardSize(Exception):
    '''
    Exception raised when an invalid board size is given.

    Parameters:
    number (int): The invalid board size.
    possible_numbers (list): A list of valid board sizes.

    Returns:
    None
    '''
    def __init__(self, number: int, possible_numbers: list):
        guess = guess_what_user_meant(number, possible_numbers)
        super().__init__(self, f"Wrong board size given, did you mean: {guess}?")


class Board:
    def __init__(self, size: int):
        '''
        Initializes a Board object with the given size.

        Parameters:
        size (int): The size of the board.

        Returns:
        None
        '''
        possible_sizes = [3, 6, 9, 12]

        if size not in possible_sizes:
            raise WrongBoardSize(number=size, possible_numbers=possible_sizes)
        no_of_sqr = [1, 2, 3, 3][possible_sizes.index(size)]
        self._size = size
        self._terminal_size = calc_terminal_board_size(no_of_sqr)
        self._no_of_sqr = no_of_sqr

    def __str__(self):
        '''
        Returns a string representation of the Board object.

        Parameters:
        None

        Returns:
        str: A string representation of the Board object.
        '''
        return f'Board of size: {self._size}'

    @property
    def size(self):
        '''
        Returns the size of the Board object.

        Parameters:
        None

        Returns:
        int: The size of the Board object.
        '''
        return self._size

    @property
    def terminal_size(self):
        '''
        Returns the terminal size of the Board object.

        Parameters:
        None

        Returns:
        tuple: A tuple containing the x and y sizes of the Board object in terminal characters.
        '''
        return self._terminal_size

    @property
    def no_of_sqr(self):
        '''
        Returns the number of squares on the Board object.

        Parameters:
        None

        Returns:
        int: The number of squares on the Board object.
        '''
        return self._no_of_sqr


class Pawn:
    def __init__(self, position: list, player_no_1: bool):
        '''
        Initializes a Pawn object with the given position and player number.

        Parameters:
        position (list): The position of the pawn on the board.
        player_no_1 (bool): The player number of the pawn.

        Returns:
        None
        '''
        self._player_no_1 = player_no_1
        self._position = list(position)
        self._pawns_in_mill_with = []
        self._has_been_moved = False
        self._dot_below = None

    def __str__(self):
        '''
        Returns a string representation of the Pawn object.

        Parameters:
        None

        Returns:
        str: A string representation of the Pawn object.
        '''
        return f'This is pawn of player {self._player_no_1}, at position: x:{int(self._position[0]/2)}, y:{self._position[1]}'

    def set_position(self, position: list):
        '''
        Sets the position of the Pawn object.

        Parameters:
        position (list): The new position of the pawn.

        Returns:
        None
        '''
        self._position = position

    def pawn_was_moved(self):
        '''
        Sets the has_been_moved attribute of the Pawn object to True.

        Parameters:
        None

        Returns:
        None
        '''
        self._has_been_moved = True

    def set_dot_below(self, dot):
        '''
        Sets the dot_below attribute of the Pawn object.

        Parameters:
        dot (Dot): The dot below the pawn.

        Returns:
        None
        '''
        self._dot_below = dot

    def make_mill(self, pawn1, pawn2):
        '''
        Adds two pawns to the pawns_in_mill_with attribute of the Pawn object.

        Parameters:
        pawn1 (Pawn): The first pawn in the mill.
        pawn2 (Pawn): The second pawn in the mill.

        Returns:
        None
        '''
        self._pawns_in_mill_with.append(pawn1)
        self._pawns_in_mill_with.append(pawn2)

    def destroy_mill(self):
        '''
        Clears the pawns_in_mill_with attribute of the Pawn object.

        Parameters:
        None

        Returns:
        None
        '''
        self._pawns_in_mill_with = []

    @property
    def has_been_moved(self):
        '''
        Returns the has_been_moved attribute of the Pawn object.

        Parameters:
        None

        Returns:
        bool: The has_been_moved attribute of the Pawn object.
        '''
        return self._has_been_moved

    @property
    def player_no_1(self):
        '''
        Returns the player_no_1 attribute of the Pawn object.

        Parameters:
        None

        Returns:
        bool: The player_no_1 attribute of the Pawn object.
        '''
        return self._player_no_1

    @property
    def position(self):
        '''
        Returns the position attribute of the Pawn object.

        Parameters:
        None

        Returns:
        list: The position attribute of the Pawn object.
        '''
        return (self._position)

    @property
    def dot_below(self):
        '''
        Returns the dot_below attribute of the Pawn object.

        Parameters:
        None

        Returns:
        Dot: The dot_below attribute of the Pawn object.
        '''
        return self._dot_below

    @property
    def pawns_in_mill_with(self):
        '''
        Returns the pawns_in_mill_with attribute of the Pawn object.

        Parameters:
        None

        Returns:
        list: The pawns_in_mill_with attribute of the Pawn object.
        '''
        return self._pawns_in_mill_with


class Dot:
    def __init__(self, position: list):
        '''
        Initializes a Dot object with the given position.

        Parameters:
        position (list): The position of the dot on the board.

        Returns:
        None
        '''
        self._position = position
        self._dots_connected_with = []
        self._pawn_on_top = None

    def set_connection(self, dot):
        '''
        Adds a dot to the dots_connected_with attribute of the Dot object.

        Parameters:
        dot (Dot): The dot to connect.

        Returns:
        None
        '''
        self._dots_connected_with.append(dot)

    def set_pawn_on_top(self, pawn):
        '''
        Sets the pawn_on_top attribute of the Dot object.

        Parameters:
        pawn (Pawn): The pawn on top of the dot.

        Returns:
        None
        '''
        self._pawn_on_top = pawn

    @property
    def position(self):
        '''
        Returns the position attribute of the Dot object.

        Parameters:
        None

        Returns:
        list: The position attribute of the Dot object.
        '''
        return self._position

    @property
    def pawn_on_top(self):
        '''
        Returns the pawn_on_top attribute of the Dot object.

        Parameters:
        None

        Returns:
        Pawn: The pawn_on_top attribute of the Dot object.
        '''
        return self._pawn_on_top

    @property
    def connected_dots(self):
        '''
        Returns the dots_connected_with attribute of the Pawn object.

        Parameters:
        None

        Returns:
        list: The Dots that are connected with this Dot
        '''
        return self._dots_connected_with
