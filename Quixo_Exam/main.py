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
        '''Evaluation function'''
        res = game.check_winner()
        # if the game is over
        if res >= -1:
            if res == 0:
                # if the player 0 is the winner
                return 1
            elif res == 1:
                # if the player 1 is the winner
                return -1
            elif res == -1:
                # if it is a draw 
                return 0
        # if the game is not over
        else:
            # return a value based on the longest sequence between +/- [0;0.5]
            if game.current_player_idx == 0:
                return (self.longest_sequence(game)/game._board.shape[0])/2
            else:
                return (-self.longest_sequence(game)/game._board.shape[0])/2

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
