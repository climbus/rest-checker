import sys
from typing import cast

from requests import request
from rich import box
from rich.json import JSON
from rich.align import Align
from rich.panel import Panel
from textual.app import App
from textual.views import GridView
from textual.widget import Reactive
from textual.widgets import Button, ButtonPressed, ScrollView
from textual_inputs import TextInput


class URLField(TextInput):
    def __init__(self, url):
        super().__init__(value=url, title="URL")

    @property
    def url(self):
        return self.value


class URLButton(Button, can_focus=True):
    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)

    def render(self):
        return Panel(
            Align.center(self.label),
            box=box.HEAVY if self.mouse_over else box.ROUNDED,
            style="black on white" if self.has_focus else "white on black",
            height=3,
        )

    async def on_focus(self) -> None:
        self.has_focus = True

    async def on_blur(self) -> None:
        self.has_focus = False

    async def on_enter(self) -> None:
        self.mouse_over = True

    async def on_leave(self) -> None:
        self.mouse_over = False


class URLView(GridView):
    url_field: URLField

    def __init__(self, url: str = "") -> None:
        super().__init__()
        self.url_field = URLField(url)

    async def on_mount(self):
        self.grid.add_column("url")
        self.grid.add_column("button", size=10)
        self.grid.add_row("main", size=3)
        self.grid.add_areas(url="url,main", button="button,main")
        self.grid.place(url=self.url_field)
        self.grid.place(button=URLButton(label="GO"))

    @property
    def url(self):
        return self.url_field.url


class RestChecker(App):
    async def on_mount(self):
        self.url_view = URLView(self.url)
        self.body = ScrollView()
        await self.view.dock(self.url_view, size=3, edge="top")
        await self.view.dock(self.body, edge="bottom")

    async def load_url(self, url):
        self.log(f"Loading url {url}")
        content = self._get_url_content(url)
        self.log(f"Response: {content}")
        await self.body.update(JSON(content.text))

    async def on_load(self):
        await self.bind("q", "quit")

        self.url = self._get_url_from_attrs()

        self.body = ScrollView()
        self.url_field = URLField(self.url)

    async def handle_button_pressed(self, message: ButtonPressed) -> None:
        button = cast(URLButton, message.sender)
        button.has_focus = False
        await self.load_url(self.url_view.url)

    def _get_url_content(self, url):
        return request("get", url)

    def _get_url_from_attrs(self) -> str:
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return ""


if __name__ == "__main__":
    RestChecker.run(title="Rest Checker", log="textual.log")