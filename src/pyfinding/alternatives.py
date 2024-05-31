from itertools import combinations, permutations

from pathfinding import Coin


def brute_force_find_graph_subset_distance(coins: tuple[Coin, ...]) -> int:
    """
    Test all possible permutations of the coins to find the shortest distance.
    This is O(n!) where n is the number of coins.
    """
    best_distance = float("inf")
    for permutation in permutations(coins):
        distance = sum(
            permutation[i].get_step_distance(permutation[i + 1].coords)
            for i in range(len(permutation) - 1)
        )
        if distance < best_distance:
            best_distance = distance

    return best_distance  # type: ignore


def held_karp_algorithm_for_shortest_distance(start: Coin, coins: list[Coin]) -> int:
    """
    Implements a variation of the Held-Karp algorithm to find the shortest distance.
    See https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm
    """
    base_state = 1 << len(coins)
    coin_idxs = list(range(len(coins)))
    distance_by_state = {}

    # Start by setting the distance from the start to each coin
    for coin_idx, coin in enumerate(coins):
        state = base_state | (1 << coin_idx)
        distance_by_state[(state, coin_idx)] = coin.get_step_distance(start.coords)

    # Build a matrix to easily access the distance for each pair of coins
    transition_matrix = [
        [
            coin_a.get_step_distance(coin_b.coords) if coin_a != coin_b else 0
            for coin_b in coins
        ]
        for coin_a in coins
    ]

    # Incrementally build all the shortest paths
    for n_coins in range(2, len(coins) + 1):
        for coin_idx_subset in combinations(coin_idxs, n_coins):

            # The final state of this subset is the one where all were visited
            final_state = base_state
            for coin_idx in coin_idx_subset:
                final_state |= 1 << coin_idx

            # The shortest distance will be the previous shortest distance that ends in node X
            # plus the distance from X to the last node in the subset
            for coin_idx in coin_idx_subset:
                subset_state = final_state & ~(1 << coin_idx)
                other_idxs = [idx for idx in coin_idx_subset if idx != coin_idx]
                distance_by_state[(final_state, coin_idx)] = min(
                    distance_by_state[(subset_state, terminal_idx)]
                    + transition_matrix[terminal_idx][coin_idx]
                    for terminal_idx in other_idxs
                )

    # The final state is the one where all coins were visited
    final_state = (1 << (len(coins) + 1)) - 1

    # Return the best way to reach the final state
    return min(distance_by_state[(final_state, idx)] for idx in coin_idxs)


def find_starting_node(coins: tuple[Coin, ...] | list[Coin]) -> Coin:
    """
    Find the node that both belongs to the shortest edge and has the
    the longest edge.

    This is an heuristic to find the most promising starting node.

    For example, given edges
        [A, B, 2]
        [A, C, 1]
        [A, D, 2]
        [B, C, 2]
        [B, D, 1]
        [C, D, 3]

    This will return C or D because they belong to the one of the shortest edges
        [A, C, 1]
        [B, D, 1]

    But also has the longest edge across A, B, C, D
        [C, D, 3]
    """
    smallest_distance = float("inf")
    edges = []
    for idx, ch_a in enumerate(coins):
        for ch_b in coins[idx + 1 :]:
            distance = ch_a.get_step_distance(ch_b.coords)
            if distance < smallest_distance:
                smallest_distance = distance
                edges = [(ch_a, ch_b)]
            elif distance == smallest_distance:
                edges.append((ch_a, ch_b))

    max_cost_node = edges[0][0]
    max_cost = 0
    for edge in edges:
        other_nodes = [node for node in coins if node not in edge]
        for coin in edge:
            coin_min_cost = float("inf")
            for node in other_nodes:
                cost = coin.get_step_distance(node.coords)
                if cost < coin_min_cost:
                    coin_min_cost = cost
            if coin_min_cost > max_cost:
                max_cost = coin_min_cost
                max_cost_node = coin

    return max_cost_node
