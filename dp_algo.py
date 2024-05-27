def max_path_sum_with_path(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    path = [[None] * cols for _ in range(rows)]


    dp[0][0] = grid[0][0]
    path[0][0] = None


    for col in range(1, cols):
        dp[0][col] = dp[0][col - 1] + grid[0][col]
        path[0][col] = 'left'


    for row in range(1, rows):
        dp[row][0] = dp[row - 1][0] + grid[row][0]
        path[row][0] = 'up'


    for row in range(1, rows):
        for col in range(1, cols):
            if dp[row - 1][col] > dp[row][col - 1]:
                dp[row][col] = dp[row - 1][col] + grid[row][col]
                path[row][col] = 'up'
            else:
                dp[row][col] = dp[row][col - 1] + grid[row][col]
                path[row][col] = 'left'

    r, c = rows - 1, cols - 1
    result_path = [(r, c)]
    while path[r][c] is not None:
        if path[r][c] == 'up':
            r -= 1
        elif path[r][c] == 'left':
            c -= 1
        result_path.append((r, c))
    return result_path[::-1]


if __name__ == '__main__':
    map = [
    [1, 1, 1, 1, 1],
    [1, 2, 3, 4, 5],
    [1, 3, 6, 10, 15],
    [1, 4, 10, 20, 35],
    [1, 5, 15, 35, 70]
]

    import numpy as np

    # map = self.bot.dynamic_map

    # currentGrid = int(self.bot.y // 100), int(self.bot.x // 100)
    # targetGrid = self.find_most_dirt(map)

    currentGrid = 4, 2
    targetGrid = 2, 4

    mat = np.array(map)
    min_x, min_y = min(currentGrid[0], targetGrid[0]), min(currentGrid[1], targetGrid[1])
    max_x, max_y = max(currentGrid[0], targetGrid[0]), max(currentGrid[1], targetGrid[1])
    mat = mat[min_x:max_x + 1, min_y:max_y + 1]

    down = currentGrid[0] < targetGrid[0]
    right = currentGrid[1] < targetGrid[1]

    # anticlockwise
    if down:
        if right:
            k = 0
        else:
            k = 1
    else:
        if right:
            k = 3
        else:
            k = 2

    print("k =", k)
    mat = np.rot90(mat, k=k)
    print(mat)
    path = max_path_sum_with_path(mat)
    print(path)

    tmp = np.zeros(mat.shape)
    for i, pos in enumerate(path, start=1):
        tmp[*pos] = i

    final_path = []
    tmp = np.rot90(tmp, k=-k)
    for i in range(len(path)):
        pos = np.where(tmp == i + 1)
        final_path.append((pos[0][0], pos[1][0]))

    final_path = [(x + min_x, y + min_y) for x, y in final_path]

    print("currentGrid, targetGrid", currentGrid, targetGrid)
    print("path", final_path)
