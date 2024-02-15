import math
import random
import time
import numpy as np
from copy import deepcopy
from game import MyGame, MyMove, Player
from tqdm import tqdm


class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'MyGame') -> tuple[tuple[int, int], MyMove]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([MyMove.TOP, MyMove.BOTTOM, MyMove.LEFT, MyMove.RIGHT])
        return from_pos, move

class My_MinMax_Player(Player):
    def __init__(self) -> None:
        super().__init__()
        self.max_cube, self.max_slide, self.min_cube, self.min_slide = None, None, None, None
        # Memoization
        self.cache = dict() # universal cache for both players
        # (cube, slide, board) -> (value)

    # USEFUL FUNCTIONS THAT EXPLOIT THE SIMMETRIES OF THE BOARD

    def rotate_board(self, board: np.ndarray) -> tuple[ np.ndarray, np.ndarray, np.ndarray ]:
        '''Rotate the board of 90' 180' 270' '''
        return np.rot90(board, -1), np.rot90(board, -2), np.rot90(board, -3)
      
    def rotate_cube(self, cube: tuple[int, int]) -> tuple[ tuple[int, int], tuple[int, int], tuple[int, int] ]:
        '''Rotate the cube of 90' 180' 270' '''
        return (cube[1], -cube[0]), (-cube[0], -cube[1]), (-cube[1], cube[0])

    def transform_slide(self, slide: MyMove, rotation: int) -> MyMove:
        return MyMove((slide.value - rotation) % 4)
    
    def change_players_marks(self, board: np.ndarray, mark_player: int) -> np.ndarray:
        '''Change the marks of the players'''
        return np.where((board == mark_player) & (board != -1), 1, 0)
    
    def universal_board(self, board: np.ndarray, mark_player: int) -> np.ndarray:
        '''Universal board'''
        return np.where((board == mark_player) & (board != -1), '+', '-')

    def check_rotations(self, cube: tuple[int, int], slide: MyMove, board: np.ndarray) -> float:
        '''Check if the cube rotations are already in the cache'''
        c90, c180, c270 = self.rotate_cube(cube)
        s90 = self.transform_slide(slide, 1)
        s180 = self.transform_slide(slide, 2)
        s270 = self.transform_slide(slide, 3)
        b90, b180, b270 = self.rotate_board(board)
        val = None
        if self.cache != {}:
            if hash((c90, b90.tobytes())) in self.cache:
                val = self.cache[hash((c90, s90, b90.tobytes()))]
            elif hash((c180, b180.tobytes())) in self.cache:
                val = self.cache[hash((c180, s180, b180.tobytes()))]
            elif hash((c270, b270.tobytes())) in self.cache:
                val = self.cache[hash((c270, s270, b270.tobytes()))]
        return val

    # FUNCTIONS TO EVALUATE THE STATE OF THE GAME

    def longest_sequence(self, board, player_id) -> int:
        '''
            Longest sequence
        '''
        max_res = 0
        dim = 5 #board.shape[0]
        row_count = [0] * dim
        col_count = [0] * dim
        diag_count = [0] * 2
        # for each row
        for i in range(dim):
            for j in range(dim):
                if board[i, j] == player_id:
                    row_count[i] += 1
                if board[j, i] == player_id:
                    col_count[i] += 1
                if i == j and board[i, j] == player_id:
                    diag_count[0] += 1
                if i + j == dim - 1 and board[i, j] == player_id:
                    diag_count[1] += 1
        max_res = max(max_res, max(row_count), max(col_count), max(diag_count))
        return max_res

    def evaluation_function(self, game: 'MyGame', board_opt: np.ndarray = None, mark_player_opt: int = None) -> float:
        '''Estimate the value of the state of the game'''
        res = game.check_winner()
        board = game.get_board() if board_opt is None else board_opt
        mark_player = game.current_player_idx if mark_player_opt is None else mark_player_opt
        # if the game is over
        if res >= 0:
            if res == 0:
                # if the player 0 is the winner
                return 1.0
            else:
                # if the player 1 is the winner
                return -1.0
        # if the game is not over
        else:
            val = self.longest_sequence(board, mark_player)/5
            # return a value based on the longest sequence between +/- [0;0.4]
            # and +/- 0.9 if the move is a winning move
            if game.current_player_idx == 0:
                if val == 1:
                    return 0.9
                else: 
                    return val/2
            else:
                if val == 1:
                    return -0.9
                else:
                    return -val/2

    # MINMAX ALGORITHM

    def minmax(self, game: 'MyGame', depth: int, alpha: int, beta: int, is_max: bool) -> tuple[float, tuple[ int, int ], MyMove]:
        '''Minmax algorithm'''
        # if the game is over or the depth is 0
        if depth == 0 or game.check_winner() >= 0:
            if is_max:
                return (self.evaluation_function(game), self.max_cube, self.max_slide)
            else: 
                return (self.evaluation_function(game), self.min_cube, self.max_slide)
            
        player_mark = game.current_player_idx
        board = game.get_board()
        u_board = self.universal_board(board, player_mark)

        if is_max:
            max_eval = - math.inf # -inf
            for cube in game.get_possible_cubes(player_mark):
                for slide in MyMove:
                    if not game.is_acceptable_slide(cube, slide):
                        continue
                    if hash((cube, slide, str(u_board))) in self.cache:
                        eval = self.cache[hash((cube, slide, str(u_board)))]
                    elif self.check_rotations(cube, slide, u_board) is not None:
                        eval = self.check_rotations(cube, slide, u_board)
                    else:   
                        game_copy = deepcopy(game)
                        game_copy._MyGame__move(tuple(cube), MyMove(slide), player_mark)
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, False)
                    if max(max_eval, eval) == eval:
                        max_eval, self.max_cube, self.max_slide = eval, cube, slide
                        if max_eval == 0.9:
                            return (max_eval, self.max_cube, self.max_slide)
                    self.cache[hash((cube, slide, str(u_board)))] = eval
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            print(board)
            print(self.max_cube, self.max_slide, max_eval)
            return (max_eval, self.max_cube, self.max_slide)
        else:
            min_eval = math.inf # +inf
            for cube in game.get_possible_cubes(player_mark):
                 for slide in MyMove:
                    if not game.is_acceptable_slide(cube, slide):
                        continue
                    if hash((cube, slide, str(u_board))) in self.cache:
                        eval = self.cache[hash((cube, slide, str(u_board)))]
                    elif self.check_rotations(cube, slide, u_board) is not None:
                        eval = self.check_rotations(cube, slide, u_board)
                    else:
                        game_copy = deepcopy(game)
                        game_copy._MyGame__move(tuple(cube), MyMove(slide), player_mark)
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, True)
                    if min(min_eval, eval) == eval:
                        min_eval, self.min_cube, self.min_slide = eval, cube, slide
                        if min_eval == -0.9:
                            return (min_eval, self.min_cube, self.min_slide)
                    self.cache[hash((cube, slide, str(u_board)))] = eval
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            print(board)
            print(self.min_cube, self.min_slide)
            return (min_eval, self.min_cube, self.min_slide)

    def make_move(self, game: 'MyGame') -> tuple[tuple[int, int], MyMove]:
        max_depth, alpha, beta = 1, -math.inf, math.inf
        _, max_cube, max_slide = self.minmax(game, max_depth, alpha, beta, True)
        return max_cube, max_slide
'''
if __name__ == '__main__':
    g = MyGame()
    g.print()
    player1 = My_MinMax_Player()
    player2 = RandomPlayer()
    winner = g.play(player1, player2)
    g.print()
    print(f"Winner: Player {winner}")
'''

'''
if __name__ == '__main__':
    count_0 = 0
    count_1 = 0

    for i in range(100):
        game = MyGame()
        player1 = RandomPlayer()
        player2 = My_MinMax_Player()
        
        game.print()
        winner = game.play(player1, player2)
        game.print()

        if winner == 0:
            count_0 += 1
        else:
            count_1 += 1

        print(f"{i+1} -> First Player won {count_0} matches")
        print(f"{i+1} -> Second Player won {count_1} matches\n")
'''

GAMES = 100

if __name__ == '__main__':
    counter1 = 0
    counter2 = 0
    start_time = time.time()
    for _ in tqdm(range(GAMES)):
        g = MyGame()
        g.print()

        player1 = My_MinMax_Player() 
        player2 = RandomPlayer()
        winner = g.play(player1, player2)
        if winner == 0:
            counter1 += 1
        if winner == 1:
            counter2 += 1
        g.print()
        print(f"Winner: Player {winner}")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Win: ", counter1, "/", GAMES)
    print("Losses ", counter2, "/", GAMES)
    print("Time for: ", GAMES, "--> ", elapsed_time)