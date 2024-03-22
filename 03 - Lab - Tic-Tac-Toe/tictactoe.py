from random import randrange

class TicTacToe(object):

    def __init__(self):
        self.board = [' '] * 9
        self. players = {'x': 'Human', 'o': 'AI'}
        self.winner = None

        if randrange(0,1) == 1:
            self.current_player = 'x'
        else:
            self.current_player = 'o'
        
        print('Welcome to Tik-Tac-Toe')
        self.instruction()
        self.draw_board()

        while self.winner == None:
            self.get_move()
            self.check_result()
            self.update_board()
            self.draw_board()

    
    def draw_board(self):
        board = self.board
        print('     %s | %s | %s' % (board[0], board[1], board[2]))
        print('    ------------')
        print('     %s | %s | %s' % (board[3], board[4], board[5]))
        print('    ------------')
        print('     %s | %s | %s' % (board[6], board[7], board[8]))

    def instruction(self):
        '''Show the player help/instructions. '''
        draw_board = '''\
    To make a move enter a number between 0 - 8 and press enter.
    The number corresponds to a board position as illustrated:

     0 | 1 | 2
     ----------
     3 | 4 | 5
     ----------
     6 | 7 | 8
        '''
        print(draw_board)

    def get_move(self):
        self.move = input('Place your move by a number between 0 - 8: ')


    def check_move(self):
        try:
            self.move = int(self.move)
            if self.board[self.move] == ' ':
                return True
            else:
                print('That position is already on the board')
        except:
            print('>> %s is not a valid position! Must be int between 0 and 8.' % self.move)
            return False

    def check_result(self):
        board = self.board
        if board[0] == board[1] == board[2] != ' ': 
            print('The Winner is'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[0] == board[4] == board[8] != ' ':
            print('Have Winner'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[0] == board[3] == board[6] != ' ':
            print('Have Winner'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[2] == board[5] == board[8] != ' ':
            print('Have Winner'+ board[2])
            return board[2] # return an 'x' or 'o' to indicate winner
        elif board[3] == board[4] == board[5] != ' ':
            print('Have Winner'+ board[3])
            return board[3] # return an 'x' or 'o' to indicate winner
        elif board[6] == board[7] == board[8] != ' ':
            print('Have Winner'+ board[6])
            return board[6] # return an 'x' or 'o' to indicate winner
        elif board[1] == board[4] == board[7] != ' ':
            print('Have Winner'+ board[1])
            return board[1] # return an 'x' or 'o' to indicate winner
        elif board[2] == board[4] == board[6] != ' ':
            print('Have Winner')
            return board[2] # return an 'x' or 'o' to indicate winner
            

        if ' ' not in board:
            print('Tie')
            return 'tie'
        return None
        

    def update_board(self):
        if self.check_move():
            self.board[self.move] = self.current_player
            self.winner = self.check_result()
            print('The game', self.winner)
            if self.current_player == 'x':
                self.current_player = 'o'
            else:
                self.current_player = 'x'
        



if __name__ == '__main__':
    # create instance (~ "new") object of type TicTacToe class
    game = TicTacToe()

