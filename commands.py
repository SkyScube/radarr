from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List


class RemoteCommand(ABC):
    """Abstract command executed over SSH."""

    @abstractmethod
    def build(self) -> str:
        """Return the raw command string to send through SSH."""

    def parse(self, raw_output: str) -> object:
        """Parse raw output; subclasses may override."""
        return raw_output


class PowerShellCommand(RemoteCommand):
    def __init__(self, command: str, modules: Iterable[str] | None = None, force_utf8: bool = True):
        self.command = command
        self.modules = list(modules or [])
        self.force_utf8 = force_utf8

    def build(self) -> str:
        prefix_parts: List[str] = []
        if self.force_utf8:
            prefix_parts.append("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8")
        if self.modules:
            modules_to_import = '; '.join(f"Import-Module {module}" for module in self.modules)
            prefix_parts.append(modules_to_import)
        prefix = ''
        if prefix_parts:
            prefix = '; '.join(prefix_parts) + '; '
        return (
            'powershell -NoProfile -Command "'
            + prefix
            + self.command
            + '"'
        )


class RawCommand(RemoteCommand):
    def __init__(self, command: str):
        self.command = command

    def build(self) -> str:
        return self.command
