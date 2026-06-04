import pygame as p
import copy as c
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_Images():
    pieces = ["wp", "bp", "wK", "bK", "wQ", "bQ", "wB", "bB", "wN", "bN", "wR", "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Pictures/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    ValidMoves = gs.getValidMoves()
    MoveMade = False #flag variable for when a move is made
    animate = False #flag for animation
    gameOver = False #flag for detecting when the game is over
    load_Images()
    running = True
    sqSelected = () # Keep track of the last click of the user (tuple :(row, col))
    playerClicks = [] # Keep track of player clicks (two tuples :(6, 4), (4, 4))
    playerOne = True #If a Human is playing White --> True
    PlayerTwo = False # Same as above but for black
    while running:
        humanTurn = (gs.WhiteToMove and playerOne) or (not gs.WhiteToMove and PlayerTwo) 
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse inputs
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn: #not allowing players to make move if the game is over
                    location = p.mouse.get_pos() #(x, y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col): # The user clicked the square twice
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: #after the 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())  
                        for i in range(len(ValidMoves)):
                            if move == ValidMoves[i]:
                                gs.MakeMove(ValidMoves[i])
                                MoveMade = True
                                animate = True
                                
                        sqSelected = ()
                        playerClicks = []
                # Keyboard inputs
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    MoveMade = True
                    animate = False
                    gameOver = False
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    sqSelected = ()
                    playerClicks = []
                    MoveMade = False
                    animate = False
                    gameOver = False
                    ValidMoves = gs.getValidMoves()

        #AI move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMoveMinMax(gs, ValidMoves)
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(ValidMoves)
            gs.MakeMove(AIMove)
            MoveMade = True
            animate = True
        

        if MoveMade:
            if animate:
                animateMoves(gs.MoveLog[-1], screen, gs.board, clock)
            ValidMoves = gs.getValidMoves()
            MoveMade = False
            animate = False

        drawGameState(screen, gs, ValidMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.WhiteToMove:
                DrawText(screen, 'Black wins by checkmate')
            else:
                DrawText(screen, 'White wins by checkmate')
        
        if gs.stalemate:
            gameOver = True
            DrawText(screen, 'Stalemate')
        
        if gs.ThreeFoldrepetiton:
            gameOver = True
            DrawText(screen, 'Draw by Three-fold repetition')
        
        if gs.FiftyMoveRule:
            gameOver = True
            DrawText(screen, 'Draw by 50-Move rule')
        
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Animate moves
'''
def animateMoves(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FramePerMove = 10 #Frames to move one square
    FrameCount = (abs(dR) + abs(dC)) * FramePerMove
    for frame in range(FrameCount + 1):
        r, c = (move.startRow + dR*frame/FrameCount, move.startCol + dC*frame/FrameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moving from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw the captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(360)

'''
Highlight square selected and possible moves on the board
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.WhiteToMove else 'b'): #sqSelected is a piece can be move
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transperancy value -> 0; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
'''
Draw the squares on the board
'''

def drawBoard(screen):
    global colors
    colors = [p.Color(238, 238, 210), p.Color(105, 146, 62)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(r*SQ_SIZE, c*SQ_SIZE, SQ_SIZE, SQ_SIZE))
'''
Draw the pieces according to its position
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece  != "--":
                screen.blit(IMAGES[piece],  p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw Text when the game ends
'''
def DrawText(screen, text):
    font = p.font.SysFont("Calibri", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject= font.render(text, 0, p.Color('Gray') )
    screen.blit(textObject, textLocation.move(2, 2))
'''
Responsible for all of the graphic in a game
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw squares
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces
    

if __name__ == "__main__":
    main()
