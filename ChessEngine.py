import copy as c

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
        self.boards = [c.deepcopy(self.board)]
        self.position_counts = {self._board_key(self.board) : 1} #using hashmaps to store the board state posion and count the appearances of them
        self.moveFunctions = {"p" : self.getPawnMoves, "R": self.getRookMoves, "N" : self.getKnightMoves,
                              "Q" : self.getQueenMoves, "K" : self.getKingMoves, "B": self.getBishopMoves}
        self.WhiteToMove = True
        self.MoveLog = []
        self.WhiteKingLocation = (7, 4)
        self.BlackKingLocation = (0, 4)
        self.EnpassantPossible = ()
        self.inCheck = False
        self.pins = []
        self.check = []
        self.CurrentCastleRights = CastleRights(True, True, True, True)
        self.CastleRightLog = [CastleRights(self.CurrentCastleRights.wks, self.CurrentCastleRights.wqs, 
                                            self.CurrentCastleRights.bks, self.CurrentCastleRights.bqs)]
        self.checkmate = False#flag variable for checkmate
        self.stalemate = False#flag variable for stalemate
        self.CounterFiftyMoveRule = 0
        self.FiftyMoveRule = False#flag variable for fiftymoverule
        self.ThreeFoldrepetiton = False#flag variabke for threefold repetiton

    def MakeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.MoveLog.append(move)
        self.WhiteToMove = not self.WhiteToMove #swap turn
        # update the king's location
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)

        #Pawn promotion
        if move.isPawnPromotion: 
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

        #Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #Signify to the program as there is potentially an enpassant move
            self.EnpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.EnpassantPossible = ()
        
        #Castlemove
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #King side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][7] = "--"
            else: #Queen Side Castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 1] = "--"
                self.board[move.endRow][move.endCol - 2] = "--"

        self.updatingCastleRights(move)
        self.CastleRightLog.append(CastleRights(self.CurrentCastleRights.wks, self.CurrentCastleRights.wqs, 
                                            self.CurrentCastleRights.bks, self.CurrentCastleRights.bqs))
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)
        #ThreeFold Repetition
        self.boards.append(c.deepcopy(self.board))
        key = self._board_key(self.board)
        self.position_counts[key] = self.position_counts.get(key, 0) + 1
        self.isThreeFoldRepetition(key)
        #FiftyMoveRule
        self.FiftyMoveRuleCounter(move)
        self.isFiftyMoveRule()
        

    def undoMove(self):
        if len(self.MoveLog) != 0 :
            if len(self.boards) > 1:
                last_board = self.boards.pop()
                key = self._board_key(last_board)
                if self.position_counts.get(key, 0) > 0:
                    self.position_counts[key] -= 1
            move = self.MoveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            if move.pieceMoved == "wK":
                self.WhiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.BlackKingLocation = (move.startRow, move.startCol)

            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] == "--"
                if self.board[move.startRow][move.startCol][0] == "w":
                    self.board[move.startRow][move.endCol] = "bp"
                elif self.board[move.startRow][move.startCol][0] == "b":
                    self.board[move.startRow][move.endCol] = "wp"
                self.EnpassantPossible = (move.endRow, move.endCol)

            # reset enpassantPossible for 2 squares advances
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.EnpassantPossible = ()

            # undoing castlingrights
            self.CastleRightLog.pop() #remove previous CastleRight of the move we are undoing
            self.CurrentCastleRights = self.CastleRightLog[-1] #updating the CastleRights of the previous move

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    print(move.endCol + 1)
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.WhiteToMove = not self.WhiteToMove
            #updating after undo
            current_key = self._board_key(self.boards[-1])
            self.isThreeFoldRepetition(current_key)
            #updating counter for 50-move rule
            self.CounterFiftyMoveRule -= 1

            self.checkmate = False
            self.stalemate = False
            self.FiftyMoveRule = False
            self.ThreeFoldrepetiton = False

    '''
    Updating the Castling Rights for each move
    '''
    def updatingCastleRights(self, move):
        if move.pieceMoved == "wk":
            self.CurrentCastleRights.wks = False
            self.CurrentCastleRights.wqs = False
        elif move.pieceMoved == "bk":
            self.CurrentCastleRights.bqs = False
            self.CurrentCastleRights.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # leftRook
                    self.CurrentCastleRights.wqs = False
                elif move.startCol == 7: # RightRook
                    self.CurrentCastleRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.CurrentCastleRights.bqs = False
                elif move.startCol == 7:
                    self.CurrentCastleRights.bks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.CurrentCastleRights.bqs = False
                elif move.endCol == 7:
                    self.CurrentCastleRights.bks = False
        elif move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.CurrentCastleRights.wqs = False
                elif move.endCol == 7:
                    self.CurrentCastleRights.wks = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = []

        if self.WhiteToMove:
            KingRow = self.WhiteKingLocation[0]
            KingCol = self.WhiteKingLocation[1]
        else:
            KingRow = self.BlackKingLocation[0]
            KingCol = self.BlackKingLocation[1]

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks(KingRow, KingCol)

        if self.inCheck:
            if len(self.checks) == 1: #Have to either move the king block or capture that enemy piece
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                ValidSquares = []
                if pieceChecking == "N":
                    ValidSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        ValidSquare = (KingRow + check[2]*i, KingCol + check[3]*i)
                        ValidSquares.append(ValidSquare)
                        if ValidSquare[0] == checkRow and ValidSquare[1] == checkCol: #once you get to piece end checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K": #moves do not move King , block check or capture the checking piece have to be removed
                        if not (moves[i].endRow, moves[i].endCol) in ValidSquares:
                            moves.remove(moves[i])
            else: #double check king has to move
                self.getKingMoves(KingRow, KingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        self.isCheckmateOrStalemate(moves)
        return moves
    
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
    
    def checkForPinsAndChecks(self, r, c):
        pins = []
        checks = []
        inCheck = False

        if self.WhiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = r
            startCol = c
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = r
            startCol = c
        directions = ((-1 , 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, -1), (1, 1))
        for j in range(8):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        if endPiece[1] == "K":
                            continue
                        else:
                            if possiblePin == ():
                                possiblePin = ((endRow, endCol, d[0],  d[1]))
                            else: #2nd allied pice, so no pin or check possible in this direction
                                break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possiblities here in this complex conditional
                        #1.) Orthogonally away from the king and piece is a rook
                        #2.) Diagonally away from the king and piece is a bishop
                        #3.) Diagonally away from the king and piece is a pawn
                        #4.) Any direction is a queen
                        #5.) Any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == "R") or (4 <= j <= 7 and type == "B") or (i == 1 and type == "p" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (type == "Q") or (i == 1 and type =="K"):
                            if possiblePin == (): #no piece blocking, so its a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0],  d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy not applying check
                            break
                else: #out of index
                    break
        #Checking the knight moves
        knightMoves = [(2, -1), (2, 1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
        for k in knightMoves:
            endRow = startRow + k[0]
            endCol = startCol + k[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endpiece = self.board[endRow][endCol]
                if endpiece[0] == enemyColor and endpiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, k[0], k[1]))

        return inCheck, pins, checks
               
    def isCheckmateOrStalemate(self, moves):
        if not moves:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            return

    '''
    Check for three-fold repetition
    '''
    def _board_key(self, board):
        return str(board)
    
    def isThreeFoldRepetition(self, key):
        self.ThreeFoldrepetiton = self.position_counts[key] >= 3

    '''
    Check for 50 move rule
    '''
    def FiftyMoveRuleCounter (self, move):
        if (move.pieceCaptured == "--") and (move.pieceMoved[1] != "p"):
            self.CounterFiftyMoveRule += 1
        else:
            self.CounterFiftyMoveRule = 0
    
    def isFiftyMoveRule(self):
        if self.CounterFiftyMoveRule == 100:
            self.FiftyMoveRule = True
        else:
            return
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        jumps = [(2, -1), (2, 1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for j in jumps:
            endRow = r + j[0]
            endCol = c + j[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if not piecePinned:
                    if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 1, 0, 1, -1, 1, -1, 0)
        AllyColor = "w" if self.WhiteToMove else "b"
        for i in range(len(rowMoves)):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != AllyColor:
                    inCheck = self.checkForPinsAndChecks(endRow, endCol)[0]
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
        self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):  
        if self.inCheck:
            return
        if (self.WhiteToMove and self.CurrentCastleRights.wks) or (not self.WhiteToMove and self.CurrentCastleRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.WhiteToMove and self.CurrentCastleRights.wqs) or (not self.WhiteToMove and self.CurrentCastleRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if 0 <= c + 1 < 8 and 0 <= c + 2 < 8:
            if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
                if not self.checkForPinsAndChecks(r, c + 1)[0] and not self.checkForPinsAndChecks(r, c + 2)[0]:
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if 0 <= c - 1 < 8 and 0 <= c - 2 < 8 and 0 <= c - 3 < 8:
            if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
                if not self.checkForPinsAndChecks(r, c - 1)[0] and not self.checkForPinsAndChecks(r, c - 2)[0]:
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # Friendly troops
                            break
                else:
                    break

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1 , 0), (1, 0), (0, -1), (0, 1)]
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.WhiteToMove:
            if self.board[r - 1][c] == "--" and (not piecePinned or pinDirection == (-1, 0)): # One square pawn advance
                moves.append(Move ((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--": #Two squares advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if (self.board[r - 1][c - 1][0] == "b") and (not piecePinned or pinDirection == (-1, -1)): #Enemy piece
                    moves.append(Move ((r, c), (r - 1, c - 1), self.board))
                elif self.EnpassantPossible == ((r - 1),(c - 1)) and (not piecePinned or pinDirection == (-1, -1)): #Enpassant
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove = True))
            if c + 1 <= len(self.board[0]) - 1:
                if (self.board[r - 1][c + 1][0] == "b") and (not piecePinned or pinDirection == (-1, 1)):
                    moves.append(Move ((r, c), (r - 1, c + 1), self.board))
                elif self.EnpassantPossible == ((r - 1),(c + 1)) and (not piecePinned or pinDirection == (-1, 1)):#Enpassant
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove = True))
        else:
            if self.board[r + 1][c] == "--" and (not piecePinned or pinDirection == (1, 0)): # One square pawn advance
                moves.append(Move ((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--": # Two squares advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w" and (not piecePinned or pinDirection == (1, -1)):
                    moves.append(Move ((r, c), (r + 1, c - 1), self.board))
                elif self.EnpassantPossible == ((r + 1), (c - 1)) and (not piecePinned or pinDirection == (1, -1)):#Enpassant
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove = True))
            if c + 1 <= len(self.board) - 1 and (not piecePinned or pinDirection == (1, 1)):
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move ((r, c), (r + 1, c + 1), self.board))
                elif self.EnpassantPossible == ((r + 1), (c + 1)) and (not piecePinned or pinDirection == (1, 1)):#Enpassant
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove = True))

class CastleRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    
    rowsToRanks = {v : k for k, v in ranksToRows.items()}

    filesToCols = {"h" : 7, "g" : 6, "f" : 5, "e" : 4,
                   "d" : 3, "c" : 2, "b" : 1, "a" : 0} 
    colToFiles = {v : k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        
        #en passant
        self.isEnpassantMove = isEnpassantMove

        #Castling
        self.isCastleMove = isCastleMove

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
