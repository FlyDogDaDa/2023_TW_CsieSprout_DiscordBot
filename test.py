from cmds.gamble import Renderable, rendering


class defor(Renderable):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    def content(self) -> list[list[str]]:
        return [["A", None, "C"]]


obj = [defor(1, 1), defor(2, 1)]

print(rendering(5, 3, obj))
