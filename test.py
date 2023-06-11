from cmds.gamble import Renderable, Renderer


class defor(Renderable):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    def content(self) -> list[list[str]]:
        return [["A", "B", "C"]]


s = Renderer(Renderer.creat_empty_screen(5, 3))
s.add_object(defor(1, 1))
s.add_object(defor(2, 1))
print(s.content())
