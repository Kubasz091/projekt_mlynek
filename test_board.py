import pytest
from unittest.mock import patch
from board import (Board, WrongBoardSize, calc_terminal_board_size, Pawn,
                   guess_what_user_meant, Dot)


def test_board_size():
    with pytest.raises(WrongBoardSize):
        Board(4)


def test_board_terminal_size():
    assert calc_terminal_board_size(3) == (78, 39)


def test_guess_what_user_meant():
    assert guess_what_user_meant(5, [1, 2, 3, 4, 7, 8, 9]) == 4


def test_board_str():
    assert str(Board(3)) == 'Board of size: 3'


def test_pawn_str():
    assert str(Pawn([2, 3], True)) == 'This is pawn of player True, at position: x:1, y:3'


def test_pawn_set_position():
    p = Pawn([2, 3], True)
    p.set_position([4, 5])
    assert p.position == [4, 5]


def test_pawn_was_moved():
    p = Pawn([2, 3], True)
    p.pawn_was_moved()
    assert p.has_been_moved is True


def test_pawn_set_dot_below():
    p = Pawn([2, 3], True)
    p.set_dot_below('dot')
    assert p.dot_below == 'dot'


def test_pawn_make_mill():
    p1 = Pawn([2, 3], True)
    p2 = Pawn([4, 5], False)
    p = Pawn([6, 7], True)
    p.make_mill(p1, p2)
    p.make_mill(p2, p)
    assert p.pawns_in_mill_with == [p1, p2, p2, p]


def test_pawn_destroy_mill():
    p1 = Pawn([2, 3], True)
    p2 = Pawn([4, 5], False)
    p = Pawn([6, 7], True)
    p.make_mill(p1, p2)
    p.make_mill(p2, p)
    p.destroy_mill()
    assert p.pawns_in_mill_with == []


def test_dot_position():
    assert Dot([2, 3]).position == [2, 3]


def test_dot_set_connection():
    d1 = Dot([2, 3])
    d2 = Dot([4, 5])
    d1.set_connection(d2)
    assert d1.connected_dots == [d2]


def test_dot_set_pawn_on_top():
    d = Dot([2, 3])
    d.set_pawn_on_top('pawn')
    assert d.pawn_on_top == 'pawn'
