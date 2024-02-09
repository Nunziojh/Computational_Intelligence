import random
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
        self.max_depth = 3
        #store the value of the states ( memoization )  
        

    def longest_sequence(self, game: 'Game') -> int:
        '''Longest sequence'''
        res = 0
        max_res = 0
        player_id = game.current_player_idx
        dim = game._board.shape[0]
        # for each row
        for i in range(dim):
            for j in range(dim):
                if game._board[i, j] == player_id:
                    res += 1
                else:
                    max_res = max(max_res, res)
                    res = 0
        # for each column
        for i in range(dim):
            for j in range(dim):
                if game._board[j, i] == player_id:
                    res += 1
                else:
                    max_res = max(max_res, res)
                    res = 0
        # for the principal diagonal
        for i in range(dim):
            if game._board[i, i] == player_id:
                res += 1
            else:
                max_res = max(max_res, res)
                res = 0
        # for the secondary diagonal
        for i in range(dim):
            if game._board[i, -(i + 1)] == player_id:
                res += 1
            else:
                max_res = max(max_res, res)
                res = 0
        return max_res
    
    def evaluation_function(self, game: 'Game') -> int:
        '''Estimate the value of the state of the game'''
        res = game.check_winner()
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
                return (self.longest_sequence(game)/game._board.shape[0])/2
            else:
                return (-self.longest_sequence(game)/game._board.shape[0])/2

    def minmax(self, game: 'Game', depth: int, alpha: int, beta: int, max: bool) -> list[int,tuple[int,int],Move]:
        '''Minmax algorithm'''
        # if the game is over or the depth is 0
        if depth == 0 or game.check_winner() >= 0:
            return self.evaluation_function(game)
        
        max_cube, max_slide, min_cube, min_slide = None, None, None, None

        if max:
            max_eval = -1000 # -inf
            for move in game.get_possible_moves():
                for slide in game.get_possible_slides(move): 
                    game_copy = game.copy()
                    game_copy.move(tuple(move), Move(slide))
                    eval = self.minmax(game_copy, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    max_cube, max_slide = move, slide
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return list[max_eval, max_cube, max_slide]

        else:
            min_eval = 1000 # +inf
            for move in game.get_possible_moves():
                for slide in game.get_possible_slides(move):
                    game_copy = game.copy()
                    game_copy.move(tuple(move), Move(slide))
                    eval = self.minmax(game_copy, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    min_cube, min_slide = move, slide
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return list[min_eval, min_cube, min_slide]

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move


if __name__ == '__main__':
    g = Game()
    g.print()
    player1 = My_MinMax_Player()
    player2 = RandomPlayer()
    winner = g.play(player1, player2)
    g.print()
    print(f"Winner: Player {winner}")
