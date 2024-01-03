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
