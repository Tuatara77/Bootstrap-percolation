import pygame
import random
import cv2
import numpy as np

# probability of a random cell initially being infected
SPAWN_CHANCE = 0.05

# the number of cells in each row/column
GRID_SIZE = 700

# the name of the image file to save the output to
OUTPUT_FILENAME = "output.png"


class Box(pygame.Surface):
    def __init__(self, x, y, width, height, colour):
        super().__init__((width, height))
        self.colour = colour
        self.fill(colour)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, surface):
        surface.blit(self, (self.x, self.y))

    def getData(self):
        return (self.x, self.y, self.colour)


cells = []
class Cell(Box):
    def __init__(self, x:int, y:int, size:int, colour:tuple[int,int,int]):
        self.size = size-2 if size>2 else 1
        super().__init__(x, y, self.size, self.size, colour)
        cells.append(self)
    
    def draw(self, surface):
        surface.blit(self, (self.x+1 if self.size!=1 else self.x, self.y+1 if self.size!=1 else self.y))


class Grid:
    def __init__(self, n, size):
        self.n = n
        self.size = size
        self.stepCount = 0
        self.cellSize = size/n
        self.cellColourR = 0
        self.cellColourG = 0
        self.cellColourB = 0
        self.grid = [[0 for i in range(n)] for j in range(n)]
        self.colourGrid = np.array([[[192,192,192] for i in range(n)] for j in range(n)])

    def draw(self, surface):
        for i in range(1, self.n):
            pygame.draw.line(surface, (192,192,192), (0, i*self.cellSize), (self.size, i*self.cellSize))
            pygame.draw.line(surface, (192,192,192), (i*self.cellSize, 0), (i*self.cellSize, self.size))
        
        for cell in cells:
            cell.draw(surface)
        
    def init(self):
        for i in range(self.n):
            for j in range(self.n):
                if random.random() < SPAWN_CHANCE:
                    self.grid[i][j] = 1
                    Cell(j*self.cellSize, i*self.cellSize, self.cellSize, (255,0,0))
                    self.colourGrid[i][j] = [0,0,255] # for some reason cv2 uses BGR instead of RGB
                else:
                    self.grid[i][j] = 0
        # a = [print(row) for row in self.grid] # for debugging/looking at the raw grid
    
    def step(self):
        """Moves the simulation to the next generation"""
        # newGrid = [[0 for i in range(self.n)] for j in range(self.n)]
        newGrid = [[value for value in row] for row in self.grid] # the only way to create a fully independent copy of a list (and list of lists)

        for i in range(self.n):
            for j in range(self.n):  # extra != conditions are to prevent edge cells from wrapping around / causing index errors
                if self.grid[i][j-1] == 1 and self.grid[i-1][j] == 1 and i != 0 and j != 0:
                    newGrid[i][j] = 1 # left and top

                if i != self.n-1:
                    if self.grid[i-1][j] == 1 and self.grid[i+1][j] == 1 and i != 0:
                        newGrid[i][j] = 1 # top and bottom
                    if self.grid[i][j-1] == 1 and self.grid[i+1][j] == 1 and j != 0:
                        newGrid[i][j] = 1 # left and bottom
                    if j != self.n-1:
                        if self.grid[i][j+1] == 1 and self.grid[i+1][j] == 1:
                            newGrid[i][j] = 1 # right and bottom
                
                if j != self.n-1:
                    if self.grid[i][j-1] == 1 and self.grid[i][j+1] == 1 and j != 0:
                        newGrid[i][j] = 1 # left and right
                    if self.grid[i][j+1] == 1 and self.grid[i-1][j] == 1 and i != 0: 
                        newGrid[i][j] = 1 # right and top
        
        if self.cellColourR == 0 and self.cellColourG == 0 and self.cellColourB < 255:
            self.cellColourB += 5
        elif self.cellColourR == 0 and self.cellColourB == 255 and self.cellColourG < 255:
            self.cellColourG += 5
        elif self.cellColourR == 0 and self.cellColourG == 255 and self.cellColourB > 0:
            self.cellColourB -= 5
        elif self.cellColourR < 255 and self.cellColourG == 255 and self.cellColourB == 0:
            self.cellColourR += 5
        elif self.cellColourR > 192 and self.cellColourG > 192 and self.cellColourB < 192:
            self.cellColourR -= 1
            self.cellColourG -= 1
            self.cellColourB += 3
        elif self.cellColourR == 192 and self.cellColourG == 192 and self.cellColourB < 192:
            self.cellColourB += 3

        for i in range(self.n):
            for j in range(self.n):
                if newGrid[i][j] == 1 and self.grid[i][j] == 0:
                    Cell(j*self.cellSize, i*self.cellSize, self.cellSize, (self.cellColourR, self.cellColourG, self.cellColourB))
                    self.colourGrid[i][j] = [self.cellColourB, self.cellColourG, self.cellColourR] # for some reason cv2 uses BGR instead of RGB
        
        if newGrid != self.grid:
            self.stepCount += 1
            self.grid = [[value for value in row] for row in newGrid]
        else: print(f"Infection stopped after {self.stepCount} steps")


def main():
    assert 0 < SPAWN_CHANCE < 1, "Infection chance must be between 0 and 1"
    pygame.init()
    size = 700    # size of the screen in pixels
    n = GRID_SIZE # number of boxes in each row/column
    assert n <= size, "Cannot have more cells in each row/column than the width of the window"
    screen = pygame.display.set_mode((size, size))
    clock = pygame.time.Clock()
    grid = Grid(n, size)
    grid.init()

    running = True
    while running:
        clock.tick(10000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        screen.fill((255,255,255))
        grid.draw(screen)
        pygame.display.flip()
        grid.step()
    pygame.quit()

    cv2.imwrite(OUTPUT_FILENAME, grid.colourGrid)


if __name__ == "__main__":
    main()
