import asyncio
from io import StringIO
from unittest.mock import MagicMixin, MagicMock, patch

import pytest
from rich.console import Console
from textual.app import App
from textual.events import Key
from rest_checker.api_reader import APIReader

from rest_checker.app import RestChecker


def run_on_app(func):
    async def wrapper(self):
        with patch("textual._context.active_app"):

            async def run_test():
                await asyncio.sleep(0.2)
                try:
                    await func(self)
                finally:
                    await self.press_ctrl_c()

            await asyncio.gather(self.current_app.process_messages(), run_test())

    return wrapper


class TestAsyncCase:
    current_app: App
    snapshot: str

    @pytest.fixture(autouse=True)
    def app(self):
        self.api_reader = MagicMock()
        self.console = Console(file=StringIO())
        self.current_app = RestChecker(console=self.console, api_reader=self.api_reader)

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_go_button(self):
        assert "GO" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_error_when_url_is_empty(self):
        await self.press("ctrl+l")
        await self.press("enter")
        assert "Url is required" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_error_when_url_is_not_valid(self):
        await self.press("ctrl+l")
        await self.write("htt")
        await self.press("enter")
        assert "Invalid URL" in self.screen

    @property
    def screen(self):
        return self.current_app.console.file.getvalue()

    async def press_ctrl_c(self):
        await self.current_app.press("ctrl+c")

    async def press(self, key):
        await self.current_app.post_message(Key(self.current_app, key=key))
        await asyncio.sleep(0.1)

    async def write(self, text):
        for char in text:
            await self.press(char)
