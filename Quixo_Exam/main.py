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
    def __init__(self, depth: int = 2, max_player: int = 0) -> None:
        super().__init__()
        self.max_cube, self.max_slide, self.min_cube, self.min_slide = None, None, None, None
        self.max_depth = depth
        self.max_player = max_player
        # Memoization
        self.cache = dict() # universal cache for both players
        # (hash(cube, slide, board)) -> (value)

    # USEFUL FUNCTIONS THAT EXPLOIT THE SIMMETRIES OF THE BOARD

    def rotate_board(self, board: np.ndarray) -> tuple[ np.ndarray, np.ndarray, np.ndarray ]:
        '''Rotate the board of 90' 180' 270' '''
        return np.rot90(board, -1), np.rot90(board, -2), np.rot90(board, -3)
      
    def rotate_cube(self, cube: tuple[int, int]) -> tuple[ tuple[int, int], tuple[int, int], tuple[int, int] ]:
        '''Rotate the cube of 90' 180' 270' '''
        return (cube[1], -cube[0]), (-cube[0], -cube[1]), (-cube[1], cube[0])

    def transform_slide(self, slide: MyMove, rotation: int) -> MyMove:
        return MyMove((slide.value - rotation) % 4)
    
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

    def evaluation_function(self, game: 'MyGame', mark_player_opt: int = None, board_opt: np.ndarray = None) -> float:
        '''Estimate the value of the state of the game'''
        res = game.check_winner()
        board = game.get_board() if board_opt is None else board_opt
        mark_player = game.current_player_idx if mark_player_opt is None else mark_player_opt
        # if the game is over
        if res >= 0:
            if res == self.max_player:
                # if the max player is the winner
                return 10.0
            else:
                # if the min player is the winner
                return -10.0
        # if the game is not over
        else:
            val = self.longest_sequence(board, mark_player)/5
            # return a value based on the longest sequence between +/- [0;0.4]
            # +/- 1 if is a winning move
            if mark_player == self.max_player:
                if val == 1:
                    return val
                return val/2
            else:
                if val == 1:
                    return -val
                return -val/2

    # MINMAX ALGORITHM

    def minmax(self, game: 'MyGame', depth: int, alpha: int, beta: int, is_max: bool) -> tuple[float, tuple[ int, int ], MyMove]:
        '''Minmax algorithm'''
        
        player_mark = game.current_player_idx
        board = game.get_board()
        u_board = self.universal_board(board, player_mark)
        
        # if the game is over or the depth is 0
        if depth == 0 or game.check_winner() >= 0:
            return (self.evaluation_function(game, player_mark, board), self.max_cube, self.max_slide)
            
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
                        game_copy.current_player_idx += 1
                        game_copy.current_player_idx %= 2
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, False)
                        self.cache[hash((cube, slide, str(u_board)))] = eval
                    if max(max_eval, eval) == eval:
                        max_eval, self.max_cube, self.max_slide = eval, cube, slide
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
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
                        game_copy.current_player_idx += 1
                        game_copy.current_player_idx %= 2
                        eval, _, _ = self.minmax(game_copy, depth - 1, alpha, beta, True)
                        self.cache[hash((cube, slide, str(u_board)))] = eval
                    if min(min_eval, eval) == eval:
                        min_eval, self.min_cube, self.min_slide = eval, cube, slide
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return ( min_eval, self.min_cube, self.min_slide)

    def make_move(self, game: 'MyGame') -> tuple[tuple[int, int], MyMove]:
        alpha, beta = -math.inf, math.inf
        _, max_cube, max_slide = self.minmax(game, self.max_depth, alpha, beta, True)
        return max_cube, max_slide
    
GAMES = 100

if __name__ == '__main__':
    counter1 = 0
    counter2 = 0
    
    start_time = time.time()
    for _ in tqdm(range(GAMES)):
        g = MyGame()
        print()
        g.print()

        player1 = My_MinMax_Player(2, 0)
        player2 = RandomPlayer()
        
        winner = g.play(player1, player2)
        if winner == 0:
            counter1 += 1
        if winner == 1:
            counter2 += 1
        g.print()
        print(f"Winner: Player {winner}")
        print("Win: ", counter1, "/", counter2)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Win: ", counter1, "/", GAMES)
    print("Losses ", counter2, "/", GAMES)
    print("Time for: ", GAMES, "--> ", elapsed_time)
