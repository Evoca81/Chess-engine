
class GameState():
    def __init__(self):
        # Board is 2 dimensional list, each element of the list has 2 characters
        # The first character show which color is it
        # The second character show which piece is it
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"p" : self.getPawnMoves, "R": self.getRookMoves, "N" : self.getKnightMoves,
                              "Q" : self.getQueenMoves, "K" : self.getKingMoves, "B": self.getBishopMoves}
        self.WhiteToMove = True
        self.MoveLog = []
        self.WhiteKingLocation = (7, 4)
        self.BlackKingLocation = (0, 4)
        self.checkMate = False
        self.stalemate = False
        self.BlackCatsle = False
        self.WhiteCatsle = False

    def MakeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.MoveLog.append(move)
        # update the king's location
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)
        self.WhiteToMove = not self.WhiteToMove
        
    def undoMove(self):
        if len(self.MoveLog) != 0 :
            move = self.MoveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            if move.pieceMoved == "wK":
                self.WhiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.BlackKingLocation = (move.startRow, move.startCol)
            self.WhiteToMove = not self.WhiteToMove

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        # Naive Algorithm
        # 1) Generate all possible moves
        moves = self.getAllPossibleMoves()
        self.getCastleMoves(moves)
        # 2) For each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.MakeMove(moves[i])
            #print("All possible moves are " + str(moves[i].moveID))
        # 4) For each of your opponent's moves
        # 5) For each of your opponent's moves, see if they attack your king
        # 6) If they attack your king, not a valid one
            self.WhiteToMove = not self.WhiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.WhiteToMove = not self.WhiteToMove
            self.undoMove()
        if len(moves) == 0: #Either stalemate or checkmate
            if self.inCheck():
                self.checkMate = True
            else:
                self.stalemate = True
        else:
            self.checkMate = True
            self.stalemate = True
        return moves
    
    def inCheck(self): # Check if the player is in check
        if self.WhiteToMove:
            return self.squaredUnderAttack(self.WhiteKingLocation[0], self.WhiteKingLocation[1])
        else:
            return self.squaredUnderAttack(self.BlackKingLocation[0], self.BlackKingLocation[1])

    def squaredUnderAttack(self, r, c):
        self.WhiteToMove = not self.WhiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.WhiteToMove = not self.WhiteToMove     
        for move in oppMoves:
            if (move.endRow == r) and (move.endCol == c): #square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                turn = self.board[r][c][0]
                if (turn == "w" and self.WhiteToMove) or (turn == "b" and not self.WhiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getKnightMoves(self, r, c, moves):
        jumps = [(2, -1), (2, 1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for j in jumps:
            endRow = r + j[0]
            endCol = c + j[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if self.board[endRow][endCol] == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                elif self.board[endRow][endCol][0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, moves):
        if self.WhiteToMove and (self.WhiteKingLocation == (7 , 4)) and (self.WhiteCatsle == False):
            if self.board[7][5] == "--" and self.board[7][6] == "--" and self.squaredUnderAttack(7, 5) == False and self.squaredUnderAttack(7, 6) == False:
                move = Move((7, 4) , (7, 6) , self.board)
                moves.append(move)
            if self.board[7][3] == "--" and self.board[7][2] == "--" and self.board[7][1] == "--" and self.squaredUnderAttack(7, 3) == False and self.squaredUnderAttack(7, 2) == False:
                move = Move((7, 4) , (7, 2) , self.board)
                moves.append(move)
        if not self.WhiteToMove and (self.BlackKingLocation == (0, 4)) and (self.BlackCatsle == False):
            if self.board[0][5] == "--" and self.board[0][6] == "--" and self.squaredUnderAttack(0, 5) == False and self.squaredUnderAttack(0, 6) == False:
                move = Move((0, 4) , (0, 6) , self.board)
                moves.append(move)
            if self.board[0][3] == "--" and self.board[0][2] == "--" and self.board[0][1] == "--" and self.squaredUnderAttack(0, 3) == False and self.squaredUnderAttack(0, 2) == False:
                move = Move((0, 4) , (0, 2) , self.board)
                moves.append(move)
    
    def getQueenMoves(self, r, c, moves):
        directions = [(-1 , 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if self.board[endRow][endCol] == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKingMoves(self, r, c, moves):
        directions = [(-1 , 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        if self.WhiteToMove:
            r = self.WhiteKingLocation[0]
            c = self.WhiteKingLocation[1]
        else:
            r = self.BlackKingLocation[0]
            c = self.BlackKingLocation[1]
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if self.board[endRow][endCol] == "--":
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                elif self.board[endRow][endCol][0] == enemyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if self.board[endRow][endCol] == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getRookMoves(self, r, c, moves):
        directions = [(-1 , 0), (1, 0), (0, -1), (0, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if self.board[endRow][endCol] == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly troops
                        break
                else: # Out of index
                    break
        
    def getPawnMoves(self, r, c, moves):
        if self.WhiteToMove:
            if self.board[r - 1][c] == "--": # One square pawn advance
                moves.append(Move ((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b": #Enemy piece
                        moves.append(Move ((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= len(self.board[0]) - 1:
                if self.board[r - 1][c + 1][0] == "b":
                        moves.append(Move ((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r + 1][c] == "--": # One square pawn advance
                moves.append(Move ((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w": #Enemy piece
                        moves.append(Move ((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= len(self.board) - 1:
                if self.board[r + 1][c + 1][0] == "w":
                        moves.append(Move ((r, c), (r + 1, c + 1), self.board))
        
        # En passant


class Move():
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    
    rowsToRanks = {v : k for k, v in ranksToRows.items()}

    filesToCols = {"h" : 7, "g" : 6, "f" : 5, "e" : 4,
                   "d" : 3, "c" : 2, "b" : 1, "a" : 0} 
    colToFiles = {v : k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
    '''
    Overiding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colToFiles[c] + self.rowsToRanks[r]
