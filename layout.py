import enum as Enum
from collections import deque

import numpy as np


class Tile(Enum.Enum):
    GRASS = 0
    TREE = 1
    PATH = 2

    @property
    def cost(self):
        if self == Tile.GRASS:
            return 0
        if self == Tile.TREE:
            return 1000
        if self == Tile.PATH:
            return 500
        raise ValueError(f"Unknown Tile: {self}")
    
    # the emoji representation of the tile
    @property
    def emoji(self):
        if self == Tile.GRASS:
            return "🌱"
        if self == Tile.TREE:
            return "🌲"
        if self == Tile.PATH:
            return "⬜"
        raise ValueError(f"Unknown Tile: {self}")
    

class Layout:
    def __init__(self, grid: list[list[Tile]]):
        self.grid = grid
        
        self.cost = 0
        for row in grid:
            for item in row:
                self.cost += item.cost

    # convert 2d array to multiline string with emojis
    def pretty(self) -> str:
        return "\n".join([" ".join([tile.emoji for tile in row]) for row in self.grid])


    # return number of cells in grid of type tile
    def count(self, tile: Tile) -> int:
        return sum(row.count(tile) for row in self.grid)




    #greenery

    # for each cell with a Tree or Grass, calculate return a score based on the number of Path cells in its 8-cell neighborhood, and consider the edge of the grid to be a Path as well
    def greenery(self) -> float:
        rows: int = len(self.grid)
        cols: int = len(self.grid[0])
        score: int = 0

        for row in range(rows):
            for col in range(cols):
                greeneryMultiplier: int
                if self.grid[row][col] == Tile.TREE:
                    greeneryMultiplier = 5
                    score += greeneryMultiplier
                elif self.grid[row][col] == Tile.GRASS:
                    greeneryMultiplier = 1
                    score += greeneryMultiplier
                else:
                    greeneryMultiplier = 0
                
                # if tree is on the edge of the grid, add 1 to the score
                if row == 0 or row == rows - 1:
                    score += greeneryMultiplier
                if col == 0 or col == cols - 1:
                    score += greeneryMultiplier
                score += self.count_neighbors(row, col, Tile.PATH) * greeneryMultiplier

        return score

    # count the number of neighbors of a cell with a given type
    def count_neighbors(self, row: int, col: int, tile: Tile) -> int:
        rows: int = len(self.grid)
        cols: int = len(self.grid[0])
        count: int = 0

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and self.grid[nr][nc] == tile:
                count += 1

        return count



    #accessibility
    def accessibility(self) -> float:
        size = len(self.grid)
        pathMultiplier = size^2

        verticalPath = self.hasVerticalPath()
        horizontalPath = self.hasHorizontalPath()
        pathTiles = self.count(Tile.PATH)

        verticalPathScore = size / verticalPath if verticalPath > 0 else 0
        horizontalPathScore = size / horizontalPath if horizontalPath > 0 else 0

        maximumScore = pathMultiplier*2 + pathTiles
        score = verticalPathScore*pathMultiplier + horizontalPathScore*pathMultiplier + pathTiles

        return score / maximumScore



    def hasVerticalPath(self) -> int:
        rows: int = len(self.grid)
        cols: int = len(self.grid[0])
        visited: set[tuple[int, int]] = set()

        # Initialize BFS with all possible starting points in the topmost row
        queue: deque[tuple[int, int, int]] = deque(
            [(0, col, 1) for col in range(cols) if self.grid[0][col] == Tile.PATH]
        )
        visited.update((0, col) for col in range(cols) if self.grid[0][col] == Tile.PATH)

        # BFS traversal
        while queue:
            row, col, path_length = queue.popleft()

            # Check if we reached the bottommost row
            if row == rows - 1:
                return path_length  # Shortest path found

            # Explore neighbors
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Down, Up, Right, Left
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited and self.grid[nr][nc] == Tile.PATH:
                    queue.append((nr, nc, path_length + 1))
                    visited.add((nr, nc))

        return 0  # No vertical path found

    def hasHorizontalPath(self) -> int:
        rows: int = len(self.grid)
        cols: int = len(self.grid[0])
        visited: set[tuple[int, int]] = set()

        # Initialize BFS with all possible starting points in the leftmost column
        queue: deque[tuple[int, int, int]] = deque(
            [(row, 0, 1) for row in range(rows) if self.grid[row][0] == Tile.PATH]
        )
        visited.update((row, 0) for row in range(rows) if self.grid[row][0] == Tile.PATH)

        # BFS traversal
        while queue:
            row, col, path_length = queue.popleft()

            # Check if we reached the rightmost column
            if col == cols - 1:
                return path_length  # Shortest path found

            # Explore neighbors
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Down, Up, Right, Left
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited and self.grid[nr][nc] == Tile.PATH:
                    queue.append((nr, nc, path_length + 1))
                    visited.add((nr, nc))

        return 0  # No horizontal path found