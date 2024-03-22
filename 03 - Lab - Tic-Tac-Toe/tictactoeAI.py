from random import randrange

class TicTacToe(object):

    def __init__(self):
        self.board = [' '] * 9
        self.winner = None
        
        if randrange(0,2) == 1:
            self.current_player = 'x'
        else:
            self.current_player = 'o'

        print('Welcome to Tik-Tac-Toe')
        self.instruction()
        self.draw_board()
        self.bot = input('Choose your bot || 1 - AI || 2 - Random Bot || 3 - AI battle || else - PvP : ')
        while self.winner == None:
            self.get_move(self.bot)
            self.check_result()
            self.update_board()
            self.draw_board()
        self.show_gameresult()

    def show_gameresult(self):
        '''Show the game result winner/tie details'''
        # print(self.draw_board())
        if self.winner == 'x':
            if self.bot == '3':
                print('Winner is AI')
            else:
                print('Winner is Human')
        elif self.winner == 'o':
            print('Winner is AI')
        elif self.winner == 'tie':
            print('TIE')
        else:
            print('Of course, AI is the WINNERs' )

        
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

    def get_move(self, bot):
        print('Current Player: %s' % self.current_player)
        if self.bot != '3':
            if bot == '1' and self.current_player == 'o':
                self.move = self.get_ai_move()
            elif self.bot == '2' and self.current_player == 'o':
                self.move = self.get_random_move()
            else:
                self.move = input('Place your move by a number between 0 - 8: ')
        else:
            if self.current_player == 'x':
                self.move = self.get_ai_move()
            else:
                self.move = self.get_random_move()
        

    def get_random_move(self):
        move = randrange(0,9)
        return move


    def get_ai_move(self):
        
        depth = self.board.count(' ')
        print('AI MOVEEEEEEEEEEEE', self.minmax(depth, True))
        val, move = self.minmax(depth, True)
        
        return move

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
            # print('The Winner is'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[0] == board[4] == board[8] != ' ':
            # print('Have Winner'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[0] == board[3] == board[6] != ' ':
            # print('Have Winner'+ board[0])
            return board[0] # return an 'x' or 'o' to indicate winner 
        elif board[2] == board[5] == board[8] != ' ':
            # print('Have Winner'+ board[2])
            return board[2] # return an 'x' or 'o' to indicate winner
        elif board[3] == board[4] == board[5] != ' ':
            # print('Have Winner'+ board[3])
            return board[3] # return an 'x' or 'o' to indicate winner
        elif board[6] == board[7] == board[8] != ' ':
            # print('Have Winner'+ board[6])
            return board[6] # return an 'x' or 'o' to indicate winner
        elif board[1] == board[4] == board[7] != ' ':
            # print('Have Winner'+ board[1])
            return board[1] # return an 'x' or 'o' to indicate winner
        elif board[2] == board[4] == board[6] != ' ':
            # print('Have Winner')
            return board[2] # return an 'x' or 'o' to indicate winner
            

        if ' ' not in board:
            return 'tie'
        return None
        

    def update_board(self):
        if self.check_move():
            self.board[self.move] = self.current_player
            self.winner = self.check_result()
            if self.current_player == 'x':
                self.current_player = 'o'
            else:
                self.current_player = 'x'
        else:
            print('Try again')

    def minmax(self, depth, player):
        check_for_result = self.check_result()
        depth = self.board.count(' ')
        board = self.board
        # self.draw_board()

        #utility
        #Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
        if check_for_result == 'x':
            return -1* depth, None
        elif check_for_result == 'o':
            return 1* depth, None
        elif check_for_result == 'tie' or depth == 0:
            return 0*depth, None
        
        if player:
            val = -float('inf')
            for i in range(len(board)):
                if board[i] == ' ':
                    board[i] = 'o'
                    alpha, m = self.minmax(depth -1,False)
                    board[i] = ' '
                    if alpha > val:
                        val = alpha
                        move = i
            return val, move
        else:
            val = float('inf')
            for i in range(len(board)):
                if board[i] == ' ':
                    board[i] = 'x'
                    beta, m = self.minmax(depth -1,True)
                    board[i] = ' '
                    if beta < val:
                        val = beta
                        move = i
            return val, move
        
        
if __name__ == '__main__':
    # create instance (~ "new") object of type TicTacToe class
    game = TicTacToe()


