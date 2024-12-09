import enum as Enum
from collections import deque

import numpy as np
import pandas as pd


class Tile(Enum.Enum):
    GRASS = 0
    TREE = 1
    PATH = 2
    BENCH = 3

    @property
    def cost_upfront(self):
        if self == Tile.GRASS:
            return 0
        if self == Tile.TREE:
            return 1000
        if self == Tile.PATH:
            return 400
        if self == Tile.BENCH:
            return 2000
        raise ValueError(f"Unknown Tile: {self}")
    
    @property
    def cost_yearly(self):
        if self == Tile.GRASS:
            return 100
        if self == Tile.TREE:
            return 400
        if self == Tile.PATH:
            return 50
        if self == Tile.BENCH:
            return 100
        raise ValueError(f"Unknown Tile: {self}")
    
    @property
    def co2_cost_upfront(self):
        if self == Tile.GRASS:
            return 0
        if self == Tile.TREE:
            return 150
        if self == Tile.PATH:
            return 110
        if self == Tile.BENCH:
            return 140
        raise ValueError(f"Unknown Tile: {self}")
    
    @property
    def co2_cost_yearly(self):
        if self == Tile.GRASS:
            return 10
        if self == Tile.TREE:
            return 25
        if self == Tile.PATH:
            return 10
        if self == Tile.BENCH:
            return 20
        raise ValueError(f"Unknown Tile: {self}")

    @property
    def co2_absorption_yearly(self):
        if self == Tile.GRASS:
            return -8
        if self == Tile.TREE:
            return -30
        if self == Tile.PATH:
            return 0
        if self == Tile.BENCH:
            return 0
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
        if self == Tile.BENCH:
            return "🪑"
        raise ValueError(f"Unknown Tile: {self}")
    
    # the emoji representation of the tile
    @property
    def letter(self):
        if self == Tile.GRASS:
            return "G"
        if self == Tile.TREE:
            return "T"
        if self == Tile.PATH:
            return "P"
        if self == Tile.BENCH:
            return "B"
        raise ValueError(f"Unknown Tile: {self}")
    

class Layout:
    def __init__(self, grid: list[list[Tile]]):
        self.grid = grid
        
        self.cost_upfront = 0
        self.cost_yearly = 0
        self.co2_cost_upfront = 0
        self.co2_cost_yearly = 0
        self.co2_absorption_yearly = 0
        pretty_rows: list[str] = []
        letter_rows: list[str] = []

        for row in grid:
            pretty_rows.append("".join([tile.emoji for tile in row]))
            letter_rows.append("".join([tile.letter for tile in row]))
            for item in row:
                self.cost_upfront += item.cost_upfront
                self.cost_yearly += item.cost_yearly
                self.co2_cost_upfront += item.co2_cost_upfront
                self.co2_cost_yearly += item.co2_cost_yearly
                self.co2_absorption_yearly += item.co2_absorption_yearly
        
        self.pretty = "\n".join(pretty_rows)
        self.pretty_flat = "_".join(letter_rows)


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
                # if row == 0 or row == rows - 1:
                #     score += greeneryMultiplier
                # if col == 0 or col == cols - 1:
                #     score += greeneryMultiplier
                score += self.count_neighbors(row, col, Tile.PATH) * greeneryMultiplier
                score += self.count_neighbors(row, col, Tile.BENCH) * greeneryMultiplier

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
        wholeGrid = pow(size, 2)
        pathMultiplier = wholeGrid
        grassTileMultiplier = 1/size
        benchScoreMultiplier = size

        verticalPath = self.verticalPathLength()
        horizontalPath = self.horizontalPathLength()
        pathTiles = self.pretty_flat.count("P")
        grassTiles = self.pretty_flat.count("G")
        benchScore = self.benchScore()

        verticalPathScore = size / verticalPath if verticalPath > 0 else 0
        horizontalPathScore = size / horizontalPath if horizontalPath > 0 else 0

        score = verticalPathScore*pathMultiplier + horizontalPathScore*pathMultiplier + pathTiles + grassTiles*grassTileMultiplier + benchScoreMultiplier*benchScore

        return score

    # for each bench, add 2 to score if there is a path cell in its 8-cell neighborhood or if the bench is on the edge of the grid, otherwise add 1
    def benchScore(self) -> float:
        rows: int = len(self.grid)
        cols: int = len(self.grid[0])
        score: float = 0

        for row in range(rows):
            for col in range(cols):
                if self.grid[row][col] == Tile.BENCH:
                    on_vertical_edge = row == 0 or row == rows - 1
                    on_horizontal_edge = col == 0 or col == cols - 1
                    next_to_path = self.count_neighbors(row, col, Tile.PATH) > 0
                    if (on_vertical_edge or on_horizontal_edge) and next_to_path:
                        score += 1.5
                    elif on_vertical_edge or on_horizontal_edge or next_to_path:
                        score += 1
                    else:
                        score += 0.5

        return score


    def verticalPathLength(self) -> int:
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

    def horizontalPathLength(self) -> int:
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
    

import itertools


def generate_unique_combinations(tiles: list[Tile], size: int) -> list[Layout]:
    """
    Generate all combinations of tiles for a grid of size x size, excluding symmetrically equivalent layouts.

    Args:
        tiles (list[Tile]): List of Tile objects to use in the combinations.
        size (int): The size of the grid (size x size).

    Returns:
        list[Layout]: List of Layout objects with unique symmetrical configurations.
    """
    def get_canonical_form(grid: tuple[tuple[Tile, ...], ...]) -> tuple[tuple[str, ...], ...]:
        """Compute the canonical form of a grid based on its rotations and reflections."""
        transformations = [
            grid,                              # Original
            grid[::-1],                        # Vertical flip
            tuple(row[::-1] for row in grid),  # Horizontal flip
            tuple(zip(*grid)),                 # 90-degree rotation
            tuple(zip(*grid[::-1])),           # 90-degree rotation + vertical flip
            tuple(zip(*tuple(row[::-1] for row in grid))),  # 90-degree rotation + horizontal flip
            grid[::-1][::-1],                  # 180-degree rotation
            tuple(zip(*grid[::-1][::-1]))      # 270-degree rotation
        ]
        # Convert each transformation to a comparable form (e.g., string representation)
        transformed_as_str = [tuple(tuple(str(tile) for tile in row) for row in t) for t in transformations]
        return min(transformed_as_str)  # Choose the lexicographically smallest transformation

    combos = itertools.product(tiles, repeat=size * size)
    seen: set[tuple[tuple[str, ...], ...]] = set()
    layouts: list[Layout] = []

    for combo in combos:
        # Create the grid as a tuple of tuples
        grid = tuple(tuple(combo[i * size:(i + 1) * size]) for i in range(size))
        # Compute the canonical form
        canonical = get_canonical_form(grid)
        if canonical not in seen:
            seen.add(canonical)
            layouts.append(Layout(grid))

    return layouts



def generate_combinations(tiles: list[Tile], size: int) -> list[Layout]:
    """
    Generate all combinations of tiles for a grid of size x size and return Layout objects.

    Args:
        tiles (list[Tile]): List of Tile objects to use in the combinations.
        size (int): The size of the grid (size x size).

    Returns:
        list[Layout]: List of Layout objects representing all generated combinations.
    """
    combos = itertools.product(tiles, repeat=size * size)
    layouts: list[Layout] = []

    for combo in combos:
        # Create the grid as a tuple of tuples
        grid = tuple(tuple(combo[i * size:(i + 1) * size]) for i in range(size))
        # Create and append the Layout object
        layouts.append(Layout(grid))

    return layouts



def layoutsToCSV(layouts: list[Layout]) -> None:
    # Convert layouts to a pandas DataFrame
    data = []
    for layout in layouts:
        data.append({
            "pretty": layout.pretty,
            "cost_upfront": layout.cost_upfront,
            "cost_yearly": layout.cost_yearly,
            "co2_cost_upfront": layout.co2_cost_upfront,
            "co2_cost_yearly": layout.co2_cost_yearly,
            "co2_absorption_yearly": layout.co2_absorption_yearly,
            # "greenery": layout.greenery(),
            # "accessibility": layout.accessibility(),
        })

    df = pd.DataFrame(data)

    # Save to CSV
    csv_file = f"layouts{len(layouts[0].grid)}.csv"
    df.to_csv(csv_file, index=False)

    print(f"Layouts saved to {csv_file}")