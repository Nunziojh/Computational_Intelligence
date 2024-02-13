import math
import random
import numpy as np
from copy import deepcopy
from game import Game, Move, Player


class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move

class My_MinMax_Player(Player):
    def __init__(self) -> None:
        super().__init__()
        self.max_cube, self.max_slide, self.min_cube, self.min_slide = None, None, None, None
        #cache_max_moves_0, cache_min_moves_0 = dict(), dict()
        #cache_max_moves_1 = dict()
        # Memoization
        self.cache = dict() # universal cache for both players

    # USEFUL FUNCTIONS THAT EXPLOIT THE SIMMETRIES OF THE BOARD

    def rotate_board(self, board: np.ndarray) -> tuple[ np.ndarray, np.ndarray, np.ndarray ]:
        '''Rotate the board of 90' 180' 270' '''
        return np.rot90(board, -1), np.rot90(board, -2), np.rot90(board, -3)
      
    def rotate_cube(self, cube: tuple[int, int]) -> tuple[ tuple[int, int], tuple[int, int], tuple[int, int] ]:
        '''Rotate the cube of 90' 180' 270' '''
        return (cube[1], -cube[0]), (-cube[0], -cube[1]), (-cube[1], cube[0])

    def transform_slide(self, slide: Move, rotation: int) -> Move:
        return Move((slide.value - rotation) % 4)
    
    def change_players_marks(board: np.ndarray) -> np.ndarray:
        '''Change the marks of the players'''
        return np.where(board == 0 and not board == -1, 1, 0)
    
    def universal_board(self, board: np.ndarray, mark_player: int) -> np.ndarray:
        '''Universal board'''
        return np.where((board == mark_player) & (board != -1), '+', '-')

    #def check_rotations(self, cube: tuple[int, int], board: np.ndarray, level: int, is_max: bool) -> tuple[ Move, float ]:
    def check_rotations(self, cube: tuple[int, int], board: np.ndarray) -> tuple[ float, Move ]:
        '''Check if the cube rotations are already in the cache'''
        c90, c180, c270 = self.rotate_cube(cube)
        b90, b180, b270 = self.rotate_board(board)
        slide = None
        val = None
        #cache_name = f"cache_{max if is_max else min}_moves_{level}"
        if self.cache != {}:
            cache_name = "cache"
            if hash((c90, b90.tobytes())) in getattr(self, cache_name):
                val, slide = getattr(self, cache_name)[hash((c90, b90.tobytes()))]
                slide = self.transform_slide(slide, 1)
            elif hash((c180, b180.tobytes())) in getattr(self, cache_name):
                val, slide = getattr(self, cache_name)[hash((c180, b180.tobytes()))]
                slide = self.transform_slide(slide, 2)
            elif hash((c270, b270.tobytes())) in getattr(self, cache_name):
                val, slide = getattr(self, cache_name)[hash((c270, b270.tobytes()))]
                slide = self.transform_slide(slide, 3)
        return (val, slide)

    # FUNCTIONS TO EVALUATE THE STATE OF THE GAME

    def longest_sequence(self, board, player_id) -> int:
        '''Longest sequence'''
        res = 0
        max_res = 0
        dim = board.shape[0]
        # for each row
        for i in range(dim):
            for j in range(dim):
                if board[i, j] == player_id:
                    res += 1
                else:
                    max_res = max(max_res, res)
                    res = 0
        # for each column
        for i in range(dim):
            for j in range(dim):
                if board[j, i] == player_id:
                    res += 1
                else:
                    max_res = max(max_res, res)
                    res = 0
        # for the principal diagonal
        for i in range(dim):
            if board[i, i] == player_id:
                res += 1
            else:
                max_res = max(max_res, res)
                res = 0
        # for the secondary diagonal
        for i in range(dim):
            if board[i, -(i + 1)] == player_id:
                res += 1
            else:
                max_res = max(max_res, res)
                res = 0
        return max_res
    
    def evaluation_function(self, game: 'Game', board_opt: np.ndarray = None, mark_player_opt: int = None) -> float:
        '''Estimate the value of the state of the game'''
        res = game.check_winner()
        board = game.get_board() if board_opt is None else board_opt
        mark_player = game.current_player_idx if mark_player_opt is None else mark_player_opt
        # if the game is over
        if res >= 0:
            if res == 0:
                # if the player 0 is the winner
                return 1
            else:
                # if the player 1 is the winner
                return -1
        # if the game is not over
        else:
            # return a value based on the longest sequence between +/- [0;0.5]
            if game.current_player_idx == 0:
                return (self.longest_sequence(board, mark_player)/game._board.shape[0])/2
            else:
                return (-self.longest_sequence(board, mark_player)/game._board.shape[0])/2

    # MINMAX ALGORITHM

    def minmax(self, game: 'Game', depth: int, alpha: int, beta: int, is_max: bool) -> tuple[float, tuple[ int, int ], Move]:
        '''Minmax algorithm'''
        # if the game is over or the depth is 0
        if depth == 0 or game.check_winner() >= 0:
            if is_max:
                return (self.evaluation_function(game), self.max_cube, self.max_slide)
            else: 
                return (self.evaluation_function(game), self.min_cube, self.max_slide)
            
        board = game.get_board()
        u_board = self.universal_board(board, game.current_player_idx)

        if is_max:
            max_eval = - math.inf # -inf
            for cube in game.get_possible_cubes(0):
                if hash((cube, u_board.tobytes())) in self.cache:
                    eval, slide = self.cache[hash((cube, u_board.tobytes()))]
                    if max(max_eval, eval) == eval:
                        max_eval, self.max_cube, self.max_slide = eval, cube, slide
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                elif self.check_rotations(cube, u_board) != (None, None):
                    eval, slide = self.check_rotations(cube, u_board)
                    if max(max_eval, eval) == eval:
                        max_eval, self.max_cube, self.max_slide = eval, cube, slide
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                else:
                    for slide in Move: 
                        if not game.is_acceptable_slide(cube, slide):
                            continue
                        game_copy = deepcopy(game)
                        game_copy._Game__move(tuple(cube), Move(slide), game_copy.current_player_idx)
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, False)
                        if max(max_eval, eval) == eval:
                            max_eval, self.max_cube, self.max_slide = eval, cube, slide
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
                        self.cache[hash((cube, u_board.tobytes()))] = (eval, slide)
            
            return (max_eval, self.max_cube, self.max_slide)
        else:
            min_eval = math.inf # +inf
            for cube in game.get_possible_cubes(1):
                if hash((cube, u_board.tobytes())) in self.cache:
                    eval, slide = self.cache[hash((cube, u_board.tobytes()))]
                    if min(min_eval, eval) == eval:
                            min_eval, self.min_cube, self.min_slide = eval, cube, slide
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                elif self.check_rotations(cube, u_board) != (None, None):
                    eval, slide = self.check_rotations(cube, u_board)
                    if min(min_eval, eval) == eval:
                            min_eval, self.min_cube, self.min_slide = eval, cube, slide
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                else:
                    for slide in Move:
                        if not game.is_acceptable_slide(cube, slide):
                            continue
                        game_copy = deepcopy(game)
                        game_copy._Game__move(tuple(cube), Move(slide), game_copy.current_player_idx)
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, True)
                        if min(min_eval, eval) == eval:
                            min_eval, self.min_cube, self.min_slide = eval, cube, slide
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
                        self.cache[hash((cube, u_board.tobytes()))] = (eval, slide)
            return (min_eval, self.min_cube, self.min_slide)

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        max_depth, alpha, beta = 2, -math.inf, math.inf
        _, max_cube, max_slide = self.minmax(game, max_depth, alpha, beta, True)
        return max_cube, max_slide

'''
if __name__ == '__main__':
    g = Game()
    g.print()
    player1 = My_MinMax_Player()
    player2 = RandomPlayer()
    winner = g.play(player1, player2)
    g.print()
    print(f"Winner: Player {winner}")
'''
if __name__ == '__main__':
    count_0 = 0
    count_1 = 0

    for i in range(100):
        game = Game()

        player1 = RandomPlayer()
        player2 = My_MinMax_Player()
        
        winner = game.play(player1, player2)

        if winner == 0:
            count_0 += 1
        else:
            count_1 += 1

        print(f"{i+1} -> First Player won {count_0} matches")
        print(f"{i+1} -> Second Player won {count_1} matches\n")