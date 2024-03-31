import random
import pygame
import time


import os
import pathlib
PATH = pathlib.Path(__file__).parent.resolve()
os.chdir(PATH)


pygame.init()

#top, right, bottom, left

top = ['1', '3', '4', '7', '8', '10', '11']
right = ['2', '4', '5', '8', '9', '10', '11']
bottom = ['1', '5', '6', '7', '8', '9', '11']
left = ['2', '3', '6', '7', '9', '10', '11']

topNothing = ['0', '2', '5', '6', '9']
rightNothing = ['0', '1', '3', '6', '7']
bottomNothing = ['0', '2', '3', '4', '10']
leftNothing = ['0', '1', '4', '5', '8']

nothing = ['0']


allTiles = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

newRules = {
	'0': [topNothing, rightNothing, bottomNothing, leftNothing],
	'1': [top, rightNothing, bottom, leftNothing],
	'2': [topNothing, right, bottomNothing, left],
	'3': [topNothing, right, bottom, leftNothing],
	'4': [topNothing, rightNothing, bottom, left],
	'5': [top, rightNothing, bottomNothing, left],
	'6': [top, right, bottomNothing, leftNothing],
	'7': [top, right, bottom, leftNothing],
	'8': [top, rightNothing, bottom, left],
	'9': [top, right, bottomNothing, left],
	'10': [topNothing, right, bottom, left],
	'11': [top, right, bottom, left]
}


#print(newRules)

ROWS = 3
COLUMNS = 3

WIDTH = 600
HEIGHT = 600

surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Wave function collapse')



tileImgs = {}
tileSize = (int(WIDTH // ROWS), int(HEIGHT // COLUMNS))  
for i in range(12):
    imagePath = f'tiles/{i}.png'
    image = pygame.image.load(imagePath)
    tileImgs[str(i)] = pygame.transform.scale(image, tileSize)


class Cell:
    def __init__(self, x, y, tiles):
        self.x = x
        self.y = y
        self.collapsed = False
        self.options = tiles
        self.history = [] 

    def collapse(self):
        if not self.collapsed and self.options:
            self.history.append({'collapsed': self.collapsed, 'options': self.options.copy()})
            chosen = random.choice(self.options)
            self.options = [chosen]
            self.collapsed = True
            self.draw() 
            pygame.display.flip()  
            time.sleep(0.1)  

    def draw(self):
        if self.collapsed:
            tileImg = tileImgs[self.options[0]]
            surface.blit(tileImg, (self.x * myGrid.w, self.y * myGrid.h))


    def revert(self):
        if self.history:
            lastState = self.history.pop()
            self.collapsed = lastState['collapsed']
            self.options = lastState['options']


    def update(self, neighbors, newRules):
        if not self.collapsed:
            print(f"Updating cell at ({self.x}, {self.y}); initial options: {self.options}")
            newOptions = set(self.options)
            for direction, neighbor in enumerate(neighbors): 
                if neighbor.collapsed:
                    allowedNeighbors = set()
                    for option in neighbor.options:
                        allowedNeighbors.update(newRules[option][direction])
                    newOptions &= allowedNeighbors

            if newOptions != set(self.options):
                self.options = list(newOptions)
                print(f"Updated cell at ({self.x}, {self.y}); new options: {self.options}")
                return True
            return False

    def saveState(self):
        self.history.append({'collapsed': self.collapsed, 'options': self.options.copy()})



    def showCell(self):
        print(f"Cell ({self.x}, {self.y}): {'Collapsed' if self.collapsed else 'Open'}, Options: {self.options}")


class Grid:
    def __init__(self):
        self.w = WIDTH / ROWS
        self.h = HEIGHT / COLUMNS
        self.cells = [[Cell(x, y, allTiles[:]) for y in range(COLUMNS)] for x in range(ROWS)]
        self.margin = 2
        self.rules = newRules
        

    def show(self):
        for i in self.cells:
            for j in i:
                j.showCell()

    def collapseCell(self, x, y, rules):
        self.cells[x][y].collapse()
        for neighbor in self.getNeighbors(x, y):
            NeighborOfNeighbor = self.getNeighbors(neighbor.x, neighbor.y)
            neighbor.update(NeighborOfNeighbor, rules)
    
    def getNeighbors(self, x, y):
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)] 
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < ROWS and 0 <= ny < COLUMNS:  
                neighbors.append(self.cells[nx][ny]) 
        return neighbors
    
    
    
    def findLowestEntropyCell(self):
        nonCollapsedCells = [cell for row in self.cells for cell in row if not cell.collapsed]
        
        if not nonCollapsedCells:
            return None  

        minEntropy = min(len(cell.options) for cell in nonCollapsedCells)
        
        lowestEntropyCells = [cell for cell in nonCollapsedCells if len(cell.options) == minEntropy]
        
        if lowestEntropyCells:
            return random.choice(lowestEntropyCells)
        else:
            return None

    def isFullyCollapsed(self):
        fullyCollapsed = all(cell.collapsed for row in self.cells for cell in row)
        print(f"Grid fully collapsed: {fullyCollapsed}")
        return fullyCollapsed
    
    def backtrack(self):
        for cell in reversed([c for row in self.cells for c in row]):
            if cell.history:
                cell.revert()
                return True  
        return False  


    def performWfc(self, rules):
        while not self.isFullyCollapsed():
            print("Still more sqaures")
            cell = self.findLowestEntropyCell()
            if cell:
                self.collapseCell(cell.x, cell.y, rules)

                if self.detectContradiction():  
                    if not self.backtrack(): 
                        print("Failed to resolve contradiction")
                        break
            else:
                print("Grid completed")
                break

    def detectContradiction(self):

        for row in self.cells:
            for cell in row:
                if not cell.collapsed and not cell.options:
                    print(f"Contradiction detected at cell ({cell.x}, {cell.y})")
                    return True
        return False

    def drawConsole(self):
        for i in range(ROWS):
            for j in range(COLUMNS):
                cell = self.cells[i][j]
                if cell.collapsed:
                    print(f"{i} {j} {cell.options}", end=" ")
                else:
                    print(f"{i} {j} Open: {cell.options}", end=" ")
            print("") 

    def draw(self):
        for row in self.cells:
            for cell in row:
                if cell.collapsed:
                    tileImg = tileImgs[cell.options[0]]
                    surface.blit(tileImg, (cell.x * self.w, cell.y * self.h))


class WFC:
    def __init__(self, grid, tileType, adjancencyRules):
        self.grid = grid
        self.tileType = tileType
        self.rules = adjancencyRules
        self.initializeTiles()

    def initializeTiles(self):
        for cell_row in self.grid.cells:
            for cell in cell_row:
                cell.options = [tile for tile in newRules if tile in cell.options]



myGrid = Grid()
myGrid.performWfc(newRules)
myGrid.drawConsole()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
