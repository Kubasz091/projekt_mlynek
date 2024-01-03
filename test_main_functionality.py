from unittest.mock import patch
from main import ProgramRunner


def test_init():
    with patch('builtins.input', side_effect=['3', '0']):
        program_runner = ProgramRunner()
        assert program_runner._size == 3
        assert program_runner._bot is False
        assert program_runner._bot_mode is None


def test_init_2():
    with patch('builtins.input', side_effect=['3', '1', '0']):
        program_runner = ProgramRunner()
        assert program_runner._size == 3
        assert program_runner._bot is True
        assert program_runner._bot_mode is False


def test_init_3():
    with patch('builtins.input', side_effect=['9', '1', '1']):
        program_runner = ProgramRunner()
        assert program_runner._size == 9
        assert program_runner._bot is True
        assert program_runner._bot_mode is True
