#Imports pygame and all other libraries used in this program
import random, pygame, sys
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program
windowWidth = 640 # size of window's width in pixels
windowHeight = 480 # size of windows' height in pixels
revealSpeed = 8 # speed boxes' sliding reveals and covers
boxSize = 40 # size of box height & width in pixels
gapSize = 10 # size of gap between boxes in pixels
boardWidth = 6 # number of columns of icons
boardHeight = 4 # number of rows of icons

assert (boardWidth * boardHeight) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'

##creates a margin in between the cards
xMargin = int((windowWidth - (boardWidth * (boxSize + gapSize))) / 2)
yMargin = int((windowHeight - (boardHeight * (boxSize + gapSize))) / 2)

##colors used in the program, used the RGB colors and indexes to find the right tint
gray     = (100, 100, 100)
darkBlue = (60, 60, 100)
white    = (255, 255, 255)
red      = (255, 0, 0)
green    = (0, 255, 0)
blue     = (0, 0, 255)
yellow   = (255, 255, 0)
orange   = (255, 128, 0)
purple   = (255, 0, 255)
cyan     = (0, 255, 255)
backgroundC = darkBlue
backgroundCLight = gray
boxColor = white
highlightColor = blue

#the different shapes' names used in the different functions
donut = 'donut'
square = 'square'
diamond = 'diamond'
lines = 'lines'
oval = 'oval'

#Lists to store every color and shape
allColors = (red, green, blue, yellow, orange, purple, cyan)

allShapes = (donut, square, diamond, lines, oval)

assert len(allColors) * len(allShapes) * 2 >= boardWidth * boardHeight, "Board is too big for the number of shapes/colors defined."

def main():
    #initializes the program Pygame
    global FPSClock, displaySurface

    pygame.init()

    FPSClock = pygame.time.Clock()

    displaySurface = pygame.display.set_mode((windowWidth, windowHeight))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event

    pygame.display.set_caption('Memory Game')

    mainBoard = get_randomized_board()

    revealedBoxes = generate_reveal_boxes_data(False)

    firstSelection = None # stores the (x, y) of the first box clicked.
    displaySurface.fill(backgroundC)

    start_game_animation(mainBoard)

    while True: # main game loop that allows Pygame to run
        mouseClicked = False
        displaySurface.fill(backgroundC) # draws the window
 

        draw_board(mainBoard, revealedBoxes) #Creates a board with the width and length set previously
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE): 
                pygame.quit()

                sys.exit()
            


            elif event.type == MOUSEMOTION: #Searches for the mouse position

                mousex, mousey = event.pos

            elif event.type == MOUSEBUTTONUP: #Click input

                mousex, mousey = event.pos
                mouseClicked = True
        
        boxx, boxy = get_box(mousex, mousey) #Creates many animations when boxes are hovered upon or clicked
        if boxx != None and boxy != None:
            if not revealedBoxes[boxx][boxy]:
                draw_highlight_box(boxx, boxy) #Highlights box using a function created later
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                reveal_box_animation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                else: # the current box was the second box clicked
                    icon1shape, icon1color = get_shape(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = get_shape(mainBoard, boxx, boxy)
                    #shows the current icon that's being selected and compares
                    if icon1shape != icon2shape or icon1color != icon2color: #Statement that turns back the cards because they don't match
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        cover_boxes_animation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection [1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif has_won(revealedBoxes): # check if all pairs found
                        win_game(mainBoard) 
                        pygame.time.wait(2000)
                        mainBoard = get_randomized_board()
                        revealedBoxes = generate_reveal_boxes_data(False)
                        draw_board(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        start_game_animation(mainBoard)
                    firstSelection = None # reset firstSelection variable
         # Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSClock.tick(FPS) #FPS set



#Generates the box's data
def generate_reveal_boxes_data(val):
    revealedBoxes = []
    for i in range(boardWidth):
        revealedBoxes.append([val] * boardHeight) 
    return revealedBoxes



#randomizes a board in the width and height of the game
def get_randomized_board():
    icons = []
    for color in allColors:
        for shape in allShapes:
            icons.append( (shape, color) )
    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(boardWidth * boardHeight / 2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)
    board = []
    for x in range(boardWidth):
        column = []
        for y in range(boardHeight):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board



#Function used to create the list and split it into the various groups
def split_into_groups_of(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
        return result



#Defines the left top coordinates of the game
def left_top_coordinates(boxx, boxy):
    left = boxx * (boxSize + gapSize) + xMargin
    top = boxy * (boxSize + gapSize) + yMargin
    return (left, top)



#Function used to get the box selected
def get_box(x, y):
    for boxx in range(boardWidth):
        for boxy in range(boardHeight):
            left, top = left_top_coordinates(boxx, boxy)
            boxRect = pygame.Rect(left, top, boxSize, boxSize)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)



#Draws the shapes of the cards
#Author: carlossilva2 @ GitHub
def draw_icon(shape, color, boxx, boxy):
    quarter = int(boxSize * 0.25) 
    half =    int(boxSize * 0.5)  
    left, top = left_top_coordinates(boxx, boxy) 
    if shape == donut:
        pygame.draw.circle(displaySurface, color, (left + half, top + half), half - 5)
        pygame.draw.circle(displaySurface, backgroundC, (left + half, top + half), quarter - 5)
    elif shape == square:
        pygame.draw.rect(displaySurface, color, (left + quarter, top + quarter, boxSize - half, boxSize - half))
    elif shape == diamond:
        pygame.draw.polygon(displaySurface, color, ((left + half, top), (left + boxSize - 1, top + half), (left + half, top + boxSize - 1), (left, top + half)))
    elif shape == lines:
        for i in range(0, boxSize, 4):
            pygame.draw.line(displaySurface, color, (left, top + i), (left + i, top))
            pygame.draw.line(displaySurface, color, (left + i, top + boxSize - 1), (left + boxSize - 1, top + i))
    elif shape == oval:
        pygame.draw.ellipse(displaySurface, color, (left, top + quarter, boxSize, half))




#Gets the shape of the card selected
def get_shape(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]




#When hovered about, box has a cover
def draw_box_cover(board, boxes, coverage):
    for box in boxes:
        left, top = left_top_coordinates(box[0], box[1])
        pygame.draw.rect(displaySurface, backgroundC, (left, top, boxSize, boxSize))
        shape, color = get_shape(board, box[0], box[1])
        draw_icon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(displaySurface, boxColor, (left, top, coverage, boxSize))
    pygame.display.update()
    FPSClock.tick(FPS)



#Creates a reveal animation for box 
def reveal_box_animation(board, boxesToReveal):
    for coverage in range(boxSize, (-revealSpeed) - 1, - revealSpeed):
        draw_box_cover(board, boxesToReveal, coverage)



#Creates a covering animation for box
def cover_boxes_animation(board, boxesToCover):
    for coverage in range(0, boxSize + revealSpeed, revealSpeed):
        draw_box_cover(board, boxesToCover, coverage)



#Draws the board
def draw_board(board, revealed):
    for boxx in range(boardWidth):
        for boxy in range(boardHeight):
            left, top = left_top_coordinates(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(displaySurface, boxColor, (left, top, boxSize, boxSize))
            else:
                shape, color = get_shape(board, boxx, boxy)
                draw_icon(shape, color, boxx, boxy)


#Highlights the box when hovered about
def draw_highlight_box(boxx, boxy):
    left, top = left_top_coordinates(boxx, boxy)
    pygame.draw.rect(displaySurface, highlightColor, (left - 5, top - 5, boxSize + 10, boxSize + 10), 4)



#An animation used to start the game animation
def start_game_animation(board):
    coveredBoxes = generate_reveal_boxes_data(False)
    boxes = []
    for x in range(boardWidth):
        for y in range(boardHeight):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = split_into_groups_of(8, boxes)
    draw_board(board, coveredBoxes)
    for boxGroup in boxGroups:
        reveal_box_animation(board, boxGroup)
        cover_boxes_animation(board, boxGroup)

#Creates a win animation
def win_game(board):
    coveredBoxes = generate_reveal_boxes_data(True)
    color1 = backgroundCLight
    color2 = backgroundC
    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        displaySurface.fill(color1)
        draw_board(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


#Confirms the user won the game
def has_won(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True


if __name__ == '__main__':

     main()
