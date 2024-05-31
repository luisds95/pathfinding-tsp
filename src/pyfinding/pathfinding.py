from itertools import combinations

from pyfinding.coin import Coin
from pyfinding.memo import Memo


def get_expected_length(board: list[str], K: int) -> float:
    """
    Approximates a solution to a variant of the Travelling Salesman Problem.

    A player faces a grid board game with multiple coins. At random, a number
    K of coins will be selected. Find the expected number of steps the player
    will need to take to collect all coins. The player may start at any coin
    and can only move up, down, right or left. All coins are guaranteed to be
    reachable from all other coins.

    The board is a list of strings where each character in the string
    represents a field type. “.” is a space the agent can walk into, “*” is a
    coin and “#” is a wall (thus the agent can’t step into it).
    """
    # Isolate the coins from the board
    coins = []
    for row_idx, row in enumerate(board):
        for column_idx, column in enumerate(row):
            if column == "*":
                coins.append(Coin((row_idx, column_idx), len(coins)))

    # Find the shortest path from each coin to each other
    set_coin_distances(coins, board)

    # Calculate the distance that collects all subsets of K coins
    memo = Memo(len(coins))
    path_lenghts = []
    for combination in combinations(coins, K):
        # Traverse the graph and approximate the shortest distance that collects all coins
        best_len = min(
            traverse_graph_with_nn(
                current=combination[idx],
                remaining=list(combination[:idx]) + list(combination[idx + 1 :]),
                depth=2,
                memo=memo,
            )
            for idx in range(K)
        )
        path_lenghts.append(best_len)

    # Calculate the expected distance
    return sum(path_lenghts) / len(path_lenghts)


def set_coin_distances(coins: list[Coin], board: list[str]) -> None:
    for idx, coin_a in enumerate(coins):
        for coin_b in coins[idx + 1 :]:
            distance = find_path_len_with_a_star(coin_a.coords, coin_b.coords, board)
            coin_a.set_step_distance(coin_b.coords, distance)
            coin_b.set_step_distance(coin_a.coords, distance)


def find_path_len_with_a_star(
    a: tuple[int, int],
    b: tuple[int, int],
    board: list[str],
) -> int:
    n_movements = {
        a: 0
    }  # Keep track of the distance from each cell to a (the original cell)
    open = [a]  # Cells that need to be explored
    close = []  # Cells that have already been explored

    while open:  # While there are cells to explore
        node = open.pop()
        next_move_distance = n_movements[node] + 1  # Each move costs 1
        close.append(node)  # Mark the cell as explored

        # Find the valid movement that is closest to b (the goal) according to the euclidean distance
        movements = get_movements(node, board)
        movements = sorted(movements, key=lambda x: get_euclidean_distance(b, x))

        # If we reach the goal in this movement, congrats! Return the distance
        if b == movements[0]:
            return next_move_distance

        # Otherwise, add the next movements to the open list if not already explored
        for movement in movements:
            n_movements[movement] = next_move_distance
            if movement in close or movement in open:
                continue
            open.append(movement)

    # If we got here, there is no path
    raise ValueError("No path!")


def get_movements(position: tuple[int, int], board: list[str]) -> list[tuple[int, int]]:
    """
    Get the possible movements from a given position.
    """
    movements = []
    for row_offset, col_offset in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        new_row = position[0] + row_offset
        is_row_out_of_bounds = new_row < 0 or new_row >= len(board)
        if is_row_out_of_bounds:
            continue

        new_col = position[1] + col_offset
        is_col_out_of_bounds = (
            new_col < 0 or new_col >= len(board[0]) or board[new_row][new_col] == "#"
        )
        if is_col_out_of_bounds:
            continue

        movements.append((new_row, new_col))

    return movements


def get_euclidean_distance(a: tuple[int, int], b: tuple[int, int]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** (1 / 2)


def traverse_graph_with_nn(
    current: Coin,
    remaining: list[Coin],
    memo: Memo | None = None,
    depth=1,
    best_distance=float("inf"),
) -> int:
    """
    Use Nearest Neighbours algorithm to traverse the graph and approximate the
    shortest distance that collects all remaining coins.
    """
    distance = 0
    path = [current]
    while remaining:
        if memo:
            memoized = memo.get(current, remaining)
            if memoized is not None:
                # If we have already computed the distance, return it
                return distance + memoized  # type: ignore

        # Find the nearest neighbour
        min_idx = 0
        min_distance = float("inf")
        min_step_distance = min_distance
        for idx, node in enumerate(remaining):
            node_distance = node.get_step_distance(current.coords)
            if node_distance >= best_distance:
                continue

            sub_distance = 0
            if depth > 1 and len(remaining) > 1:
                # Recurse until we've exhausted the depth or the graph
                sub_distance = traverse_graph_with_nn(
                    current=node,
                    remaining=remaining[:idx] + remaining[idx + 1 :],
                    memo=memo,
                    depth=depth - 1,
                    best_distance=min_step_distance,
                )

            step_distance = node_distance + sub_distance
            if step_distance < min_step_distance:
                # Update the nearest neighbour
                min_step_distance = step_distance
                min_distance = node_distance
                min_idx = idx

        distance += min_distance
        current = remaining.pop(min_idx)

        if memo:
            path.append(current)

    if memo:
        memo.set(path[0], path[1:], distance)

    return distance  # type: ignore
