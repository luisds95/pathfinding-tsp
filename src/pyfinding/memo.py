from pyfinding.coin import Coin


class Memo:
    def __init__(self, total: int) -> None:
        self.total = total
        self.base = 1 << total
        self.memo = {}

    def get(self, coin: Coin, remaining: list[Coin]) -> float | None:
        state = self._get_state(coin, remaining)
        if state in self.memo:
            return self.memo[state]
        return None

    def _get_state(self, coin: Coin, remaining: list[Coin]) -> tuple[int, int]:
        state = self.base
        for rem_coin in remaining:
            state |= 1 << rem_coin.i
        return (coin.i, state)

    def set(self, coin: Coin, remaining: list[Coin], distance: float) -> None:
        state = self._get_state(coin, remaining)
        self.memo[state] = distance
