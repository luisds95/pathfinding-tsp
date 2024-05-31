class Coin:
    def __init__(self, coords: tuple[int, int], i: int) -> None:
        self.coords = coords
        self.i = i
        self.step_distance: dict[tuple[int, int], int] = {}

    def __str__(self) -> str:
        return f"Coin{self.coords}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: "Coin") -> bool:
        return self.coords == other.coords

    def __hash__(self) -> int:
        return hash(self.coords)

    def set_step_distance(self, coords: tuple[int, int], distance: int) -> None:
        self.step_distance[coords] = distance

    def get_step_distance(self, coords: tuple[int, int]) -> int:
        return self.step_distance[coords]
