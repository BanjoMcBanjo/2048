import pygame, sys, random, time
from pygame.locals import *

# Create the constants
BOARDWIDTH = 4  # number of columns in the board
BOARDHEIGHT = 4  # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)
RED = (255, 0, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = RED
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, UNDO_SURF, UNDO_RECT, NEW_SURF, NEW_RECT, SCORE_SURF, SCORE_RECT, scoreNum, prevScoreNum

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('20 48')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    # FIX - turn Reset button into an Undo button (only after basic game works)
    UNDO_SURF, UNDO_RECT = makeText('Undo', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    SCORE_SURF, SCORE_RECT = makeText('Total Score:', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 140, WINDOWHEIGHT - 400)

    boardData = [[BLANK, BLANK, BLANK, BLANK], [BLANK, BLANK, BLANK, BLANK], [BLANK, BLANK, BLANK, BLANK],
                 [2, BLANK, BLANK, 2]]
    # starting board data

    # Should represent past incarnation of board
    prevBoard = [[BLANK, BLANK, BLANK, BLANK], [BLANK, BLANK, BLANK, BLANK], [BLANK, BLANK, BLANK, BLANK],
                 [2, BLANK, BLANK, 2]]

    # Starting score value
    scoreNum = 0

    # Score value for undoing
    prevScoreNum = 0

    while True:  # main game loop
        slideTo = None  # the direction, if any, a tile should slide
        msg = 'Press arrow keys to slide.'  # contains the message to show in the upper left corner.
        scoreText = str(scoreNum)
        gameWonText = 'YOU WIN!!!'
        gameLostText = 'YOU LOSE!!!'

        drawBoard(boardData, msg)

        theScoreText = BASICFONT.render(scoreText, True, WHITE)
        theGameWonText = BASICFONT.render(gameWonText, True, WHITE)
        theGameLostText = BASICFONT.render(gameLostText, True, WHITE)

        DISPLAYSURF.blit(theScoreText, (520, 120))

        checkForQuit()
        for event in pygame.event.get():  # event handling loop

            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(boardData, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if UNDO_RECT.collidepoint(event.pos):
                        for i in range(4):
                            for a in range(4):
                                boardData[i][a] = prevBoard[i][a]
                        scoreNum = prevScoreNum

            elif event.type == KEYUP:
                # Check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s):
                    slideTo = DOWN

        if slideTo:
            # Strategy - move > merge > move again
            xBlockLocations1, yBlockLocations1 = getBlockPositions(boardData)
            if slideTo == LEFT or slideTo == UP:
                for a in range(4):
                    for b in range(4):
                        prevBoard[a][b] = boardData[a][b]
                for i in range(len(xBlockLocations1)):
                    makeMove(boardData, slideTo, i)
            else:
                for a in range(4):
                    for b in range(4):
                        prevBoard[a][b] = boardData[a][b]
                for i in range(len(xBlockLocations1) - 1, -1, -1):
                    makeMove(boardData, slideTo, i)

            prevScoreNum = scoreNum
            mergeMethod(boardData, slideTo)

            xBlockLocations2, yBlockLocations2 = getBlockPositions(boardData)
            if slideTo == LEFT or slideTo == UP:
                for a in range(len(xBlockLocations2)):
                    makeMove(boardData, slideTo, a)

            else:
                for a in range(len(xBlockLocations2) - 1, -1, -1):
                    makeMove(boardData, slideTo, a)


            xBlockLocations1, yBlockLocations1 = getBlockPositions(boardData)
            if slideTo == LEFT or slideTo == UP:
                for i in range(len(xBlockLocations1)):
                    makeMove(boardData, slideTo, i)
            else:
                for i in range(len(xBlockLocations1) - 1, -1, -1):
                    makeMove(boardData, slideTo, i)

            addNewBlock(boardData)

            if gameWon(boardData) == True:
                DISPLAYSURF.blit(theGameWonText, (520, 120))
                pygame.display.update()
                time.sleep(1)
            elif gameLost(boardData) == True:
                DISPLAYSURF.blit(theGameLostText, (520, 120))
                pygame.display.update()
                time.sleep(10000)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def getBlockPositions(board):
    # Returns an array of the x and y of board coordinates of every block on the board (coordinates go from 0 to 4)
    # "blockLocations" is a 1D array representing the locations of blocks
    # Recording of tiles starts in top left corner and moves down each column (y) until reaching bottom right corner
    xBlockLocations = []
    yBlockLocations = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] != BLANK:
                xBlockLocations.append(x)
                yBlockLocations.append(y)
    return xBlockLocations, yBlockLocations


def makeMove(board, move, i):
    # This function does not check if the move is valid.
    # Recursion to make the block move all the way to one side
    xBlockLocations, yBlockLocations = getBlockPositions(board)

    message = 'Press arrow keys to slide.'

    if move == UP and yBlockLocations[i] > 0 and board[xBlockLocations[i]][yBlockLocations[i] - 1] == BLANK:
        slideAnimation(board, UP, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
        board[xBlockLocations[i]][yBlockLocations[i] - 1] = board[xBlockLocations[i]][yBlockLocations[i]]
        board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
        print(board)
        makeMove(board, UP, i)
    elif move == DOWN and yBlockLocations[i] < 3 and board[xBlockLocations[i]][yBlockLocations[i] + 1] == BLANK:
        slideAnimation(board, DOWN, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
        board[xBlockLocations[i]][yBlockLocations[i] + 1] = board[xBlockLocations[i]][yBlockLocations[i]]
        board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
        print(board)
        makeMove(board, DOWN, i)
    elif move == LEFT and xBlockLocations[i] > 0 and board[xBlockLocations[i] - 1][yBlockLocations[i]] == BLANK:
        slideAnimation(board, LEFT, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
        board[xBlockLocations[i] - 1][yBlockLocations[i]] = board[xBlockLocations[i]][yBlockLocations[i]]
        board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
        print(board)
        makeMove(board, LEFT, i)
    elif move == RIGHT and xBlockLocations[i] < 3 and board[xBlockLocations[i] + 1][yBlockLocations[i]] == BLANK:
        slideAnimation(board, RIGHT, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
        board[xBlockLocations[i] + 1][yBlockLocations[i]] = board[xBlockLocations[i]][yBlockLocations[i]]
        board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
        print(board)
        makeMove(board, RIGHT, i)


def getLeftTopOfTile(tileX, tileY):
    # converts board coordinates into pixel coordinates
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tileColor, tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, tileColor, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def drawTileGreen(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    #
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    # "board" is a 2D array
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(RED, tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(UNDO_SURF, UNDO_RECT)
    DISPLAYSURF.blit(SCORE_SURF, SCORE_RECT)


def slideAnimation(board, direction, message, animationSpeed, x, y ,movementRange):
    # x and y are coordinates from the board to specify a tile
    # Note: This function does not check if the move is valid.
    # Current functionality: Animates individual tile movements
    # movementRange should be given in multiples of 80

    left, top = getLeftTopOfTile(x, y)

    movex = x
    movey = y

    # prepare the base surface
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    # *top left of tile is needed for drawing rectangles
    pygame.draw.rect(baseSurf, BGCOLOR, (left, top, TILESIZE, TILESIZE))

    for i in range(0, movementRange, animationSpeed):
        # animate the tile sliding over
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(RED, movex, movey, board[x][y], 0, -i)
        if direction == DOWN:
            drawTile(RED, movex, movey, board[x][y], 0, i)
        if direction == LEFT:
            drawTile(RED, movex, movey, board[x][y], -i, 0)
        if direction == RIGHT:
            drawTile(RED, movex, movey, board[x][y], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mergeMethod(board, move):
    global scoreNum
    # Merges adjacent identical tiles
    xBlockLocations, yBlockLocations = getBlockPositions(board)

    message = 'Merge'

    if move == LEFT or move == UP:
        for i in range(len(xBlockLocations)):
            if move == UP:
                if yBlockLocations[i] > 0 and board[xBlockLocations[i]][yBlockLocations[i]] == board[xBlockLocations[i]][
                    yBlockLocations[i] - 1] \
                        and board[xBlockLocations[i]][yBlockLocations[i]] != BLANK:
                    slideAnimation(board, UP, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
                    board[xBlockLocations[i]][yBlockLocations[i] - 1] = board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    scoreNum = scoreNum + board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
            elif move == LEFT:
                if xBlockLocations[i] > 0 and board[xBlockLocations[i]][yBlockLocations[i]] == \
                        board[xBlockLocations[i] - 1][yBlockLocations[i]] \
                        and board[xBlockLocations[i]][yBlockLocations[i]] != BLANK:
                    slideAnimation(board, LEFT, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
                    board[xBlockLocations[i] - 1][yBlockLocations[i]] = board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    scoreNum = scoreNum + board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
    else:
        for i in range(len(xBlockLocations) - 1, -1, -1):
            if move == DOWN:
                if yBlockLocations[i] < 3 and board[xBlockLocations[i]][yBlockLocations[i]] == board[xBlockLocations[i]][
                    yBlockLocations[i] + 1] \
                        and board[xBlockLocations[i]][yBlockLocations[i]] != BLANK:
                    slideAnimation(board, DOWN, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
                    board[xBlockLocations[i]][yBlockLocations[i] + 1] = board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    scoreNum = scoreNum + board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    board[xBlockLocations[i]][yBlockLocations[i]] = BLANK
            elif move == RIGHT:
                if xBlockLocations[i] < 3 and board[xBlockLocations[i]][yBlockLocations[i]] == \
                        board[xBlockLocations[i] + 1][yBlockLocations[i]] \
                        and board[xBlockLocations[i]][yBlockLocations[i]] != BLANK:
                    slideAnimation(board, RIGHT, message, 40, xBlockLocations[i], yBlockLocations[i], 80)
                    board[xBlockLocations[i] + 1][yBlockLocations[i]] = board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    scoreNum = scoreNum + board[xBlockLocations[i]][yBlockLocations[i]] * 2
                    board[xBlockLocations[i]][yBlockLocations[i]] = BLANK

def gameWon(board):
    # Should return 'True' if a 2048 block appears on the board
    for i in range(4):
        for a in range(4):
            if board[i][a] != BLANK and board[i][a] == 2048:
                return True

def somethingIsPossible(board, x, y):
    # Checks to see if anything is possible w/adjacent tiles
    canDo = True

    if x == 0 and y == 0:
        if board[x+1][y] != board[x][y] and board[x][y+1] != board[x][y]:
            canDo = False
    elif x == 0 and y == 3:
        if board[x+1][y] != board[x][y] and board[x][y-1] != board[x][y]:
            canDo = False
    elif x == 3 and y == 0:
        if board[x-1][y] != board[x][y] and board[x][y+1] != board[x][y]:
            canDo = False
    elif x == 3 and y == 3:
        if board[x-1][y] != board[x][y] and board[x][y-1] != board[x][y]:
            canDo = False
    elif x == 0:
        if board[x][y-1] != board[x][y] and board[x+1][y] != board[x][y] and board[x][y+1] != board[x][y]:
            canDo = False
    elif x == 3:
        if board[x][y-1] != board[x][y] and board[x-1][y] != board[x][y] and board[x][y+1] != board[x][y]:
            canDo = False
    elif y == 0:
        if board[x-1][y] != board[x][y] and board[x][y+1] != board[x][y] and board[x+1][y] != board[x][y]:
            canDo = False
    elif y == 3:
        if board[x-1][y] != board[x][y] and board[x][y-1] != board[x][y] and board[x+1][y] != board[x][y]:
            canDo = False
    else:
        if board[x-1][y] != board[x][y] and board[x][y-1] != board[x][y] and board[x+1][y] != board[x][y] and board[x][y+1] != board[x][y]:
            canDo = False

    return canDo


def gameLost(board):
    # Should return 'True' if no moves are possible
    canMoveList = []
    ultimateDecision = False
    counter = 0

    for i in range(4):
        for a in range(4):
            canMoveList.append(somethingIsPossible(board, i, a))

    for b in range(16):
        if canMoveList[b] == True:
            counter = counter + 1

    if counter != 0:
        return False
    else:
        return True


def addNewBlock(board):
    # Randomly places new block(s) on the board after a move has been performed
    numBlocks = 1
    randX = random.randint(0, 3)
    theY = 0

    for i in range(numBlocks):
        if board[randX][theY] == BLANK:
            board[randX][theY] = 2
            drawTile(GREEN, randX, theY, 2)


def resetAnimation(board, allMoves):
    # make all of the moves in allMoves in reverse.
    revAllMoves = allMoves[:]  # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()
