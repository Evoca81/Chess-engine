import random

pieceScore = {"K" : 0, "Q" : 9, "R": 5, "B": 3, "N": 3, "p" : 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
'''
Picks and returns a random move
'''
def findRandomMove(ValidMoves):
    return ValidMoves[random.randint(0, len(ValidMoves) - 1)]

'''
Find the best move based solely on material
'''

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.WhiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.MakeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for opponentMove in opponentMoves:
            gs.MakeMove(opponentMove)
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE 
            elif gs.stalemate or gs.FiftyMoveRule or gs.ThreeFoldrepetiton:
                score = STALEMATE
            else:
                score = -turnMultiplier * getMaterialScore(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findBestMoveMinMax(gs, ValidMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, ValidMoves, DEPTH, gs.WhiteToMove)
    return nextMove

def findMoveMinMax(gs, ValidMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return getMaterialScore(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in ValidMoves:
            gs.MakeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in ValidMoves:
            gs.MakeMove(move)
            nextMoves= gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def scoreBoard(gs):
    if gs.checkmate:
        if gs.WhiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate or gs.FiftyMoveRule or gs.ThreeFoldrepetiton:
        return STALEMATE
    
'''
Score the board based on material
'''

def getMaterialScore(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score