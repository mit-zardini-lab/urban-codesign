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


    def hasVerticalPath(self) -> int | None:
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

        return None  # No vertical path found

    def hasHorizontalPath(self) -> int | None:
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

        return None  # No horizontal path found