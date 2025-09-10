class Player:
    def __init__(self, player_no: int, controll_keys):
        self.id = player_no

        self.key_up = controll_keys["up"]
        self.key_down = controll_keys["down"]
        self.key_left = controll_keys["left"]
        self.key_right = controll_keys["right"]
        self.key_interact = controll_keys["interact"]

    def controll_procces(self, game_lord_pawn_interact_func, game_lord_cursor_move_func, game_lord_quit_func, key_input_func):
        def try_controll():
            curr_key = key_input_func()

            if curr_key == self.key_up:
                game_lord_cursor_move_func("up", self.id)
            elif curr_key == self.key_down:
                game_lord_cursor_move_func("down", self.id)
            elif curr_key == self.key_left:
                game_lord_cursor_move_func("left", self.id)
            elif curr_key == self.key_right:
                game_lord_cursor_move_func("right", self.id)
            elif curr_key == self.key_interact:
                game_lord_pawn_interact_func(self.id)
            elif curr_key == ord("q"):
                game_lord_quit_func(self.id)

        return try_controll
