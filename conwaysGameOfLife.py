import pygame
import random

# set to True to invert the colours (black background, white cells)
INVERT_COLOURS = False

# chance of a cell spawning in a random location on the grid
SPAWN_CHANCE = 0.05

# the number of cells in each row/column
GRID_SIZE = 100


class Box(pygame.Surface):
    def __init__(self, x, y, width, height, colour):
        super().__init__((width, height))
        self.fill(colour)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, surface):
        surface.blit(self, (self.x, self.y))

cells = []
class Cell(Box):
    def __init__(self, x, y, size):
        if INVERT_COLOURS: super().__init__(x, y, size-2, size-2, (255,255,255))
        else: super().__init__(x, y, size-2, size-2, (0,0,0))
        cells.append(self)
    
    def draw(self, surface):
        surface.blit(self, (self.x+1, self.y+1))


class Grid:
    def __init__(self, n, size):
        self.n = n
        self.size = size
        self.cellSize = size/n
        self.grid = [[0 for i in range(n)] for j in range(n)]

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
                    Cell(j*self.cellSize, i*self.cellSize, self.cellSize)
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

        for i in range(self.n):
            for j in range(self.n):
                if newGrid[i][j] == 1 and self.grid[i][j] == 0:
                    Cell(j*self.cellSize, i*self.cellSize, self.cellSize)
        
        self.grid = [[value for value in row] for row in newGrid]


def main():
    assert 0 < SPAWN_CHANCE < 1, "Spawn chance must be between 0 and 1"
    pygame.init()
    size = 700    # size of the screen in pixels
    n = GRID_SIZE # number of boxes in each row/column
    screen = pygame.display.set_mode((size, size))
    clock = pygame.time.Clock()
    grid = Grid(n, size)
    grid.init()

    running = True
    while running:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        if INVERT_COLOURS: screen.fill((0,0,0))
        else: screen.fill((255,255,255))
        grid.draw(screen)
        pygame.display.flip()
        grid.step()
    pygame.quit()

if __name__ == "__main__":
    main()