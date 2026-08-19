from __future__ import annotations

import os
import shlex
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

from lembrete_agua.config import user_config_dir

DESKTOP_FILENAME = "lembrete-agua.desktop"
APPLICATION_ID = "io.github.gustavomartinsdev.LembreteAgua"


def default_command() -> tuple[str, ...]:
    installed_command = shutil.which("lembrete-agua")
    if installed_command:
        return (installed_command,)
    return (sys.executable, "-m", "lembrete_agua")


class AutostartManager:
    def __init__(
        self,
        path: Path | None = None,
        command: Sequence[str] | None = None,
    ) -> None:
        self.path = path or user_config_dir().parent / "autostart" / DESKTOP_FILENAME
        self.command = tuple(command or default_command())

    def is_enabled(self) -> bool:
        return self.path.is_file()

    def set_enabled(self, enabled: bool) -> None:
        if enabled:
            self._enable()
        elif self.path.exists():
            self.path.unlink()

    def _enable(self) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        executable = shlex.join(self.command)
        content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Lembrete de Água\n"
            "Comment=Lembretes locais para beber água\n"
            f"Exec={executable}\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
        temporary = self.path.with_suffix(".desktop.tmp")
        try:
            temporary.write_text(content, encoding="utf-8")
            temporary.chmod(0o600)
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


class DesktopEntryManager:
    def __init__(
        self,
        path: Path | None = None,
        command: Sequence[str] | None = None,
    ) -> None:
        data_home = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
        self.path = path or data_home / "applications" / f"{APPLICATION_ID}.desktop"
        self.command = tuple(command or default_command())

    def install(self) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Lembrete de Água\n"
            "Comment=Acompanhamento local de hidratação\n"
            f"Exec={shlex.join(self.command)}\n"
            "Terminal=false\n"
            "StartupNotify=true\n"
            "DBusActivatable=true\n"
            "X-GNOME-UsesNotifications=true\n"
        )
        temporary = self.path.with_suffix(".desktop.tmp")
        try:
            temporary.write_text(content, encoding="utf-8")
            temporary.chmod(0o600)
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


class DbusServiceManager:
    def __init__(
        self,
        path: Path | None = None,
        command: Sequence[str] | None = None,
    ) -> None:
        data_home = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
        self.path = path or data_home / "dbus-1" / "services" / f"{APPLICATION_ID}.service"
        self.command = tuple(command or default_command())

    def install(self) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        content = (
            "[D-BUS Service]\n"
            f"Name={APPLICATION_ID}\n"
            f"Exec={shlex.join(self.command)}\n"
        )
        temporary = self.path.with_suffix(".service.tmp")
        try:
            temporary.write_text(content, encoding="utf-8")
            temporary.chmod(0o600)
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()
