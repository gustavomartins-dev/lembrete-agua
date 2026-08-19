from pathlib import Path
from typing import Self

from lembrete_agua.autostart import (
    AutostartManager,
    DbusServiceManager,
    DesktopEntryManager,
    IconManager,
    WindowsAutostartManager,
)


def test_enable_and_disable_autostart(tmp_path: Path) -> None:
    path = tmp_path / "autostart" / "lembrete-agua.desktop"
    manager = AutostartManager(path, ("/opt/Lembrete Água/bin/app", "--quiet"))

    manager.set_enabled(True)

    content = path.read_text(encoding="utf-8")
    assert "Type=Application" in content
    assert "Exec='/opt/Lembrete Água/bin/app' --quiet" in content
    assert "Icon=io.github.gustavomartinsdev.LembreteAgua" in content
    assert manager.is_enabled()

    manager.set_enabled(False)
    assert not manager.is_enabled()


def test_install_desktop_entry_for_notification_activation(tmp_path: Path) -> None:
    path = tmp_path / "applications" / "app.desktop"
    manager = DesktopEntryManager(path, ("/opt/Lembrete Água/bin/app",))

    manager.install()

    content = path.read_text(encoding="utf-8")
    assert "Exec='/opt/Lembrete Água/bin/app'" in content
    assert "X-GNOME-UsesNotifications=true" in content
    assert "DBusActivatable=true" in content


def test_install_dbus_service_for_notification_actions(tmp_path: Path) -> None:
    path = tmp_path / "services" / "app.service"
    manager = DbusServiceManager(path, ("/opt/Lembrete Água/bin/app",))

    manager.install()

    content = path.read_text(encoding="utf-8")
    assert "Name=io.github.gustavomartinsdev.LembreteAgua" in content
    assert "Exec='/opt/Lembrete Água/bin/app'" in content


def test_install_original_svg_icon(tmp_path: Path) -> None:
    path = tmp_path / "icons" / "app.svg"

    IconManager(path).install()

    content = path.read_text(encoding="utf-8")
    assert content.startswith("<?xml")
    assert "Gota de água" in content


def test_windows_autostart_uses_current_user_registry() -> None:
    values: dict[str, str] = {}

    class Key:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

    class Registry:
        HKEY_CURRENT_USER = "HKCU"
        KEY_READ = 1
        REG_SZ = 1

        @staticmethod
        def CreateKey(*_args: object) -> Key:
            return Key()

        OpenKey = CreateKey

        @staticmethod
        def SetValueEx(_key: Key, name: str, _reserved: int, _kind: int, value: str) -> None:
            values[name] = value

        @staticmethod
        def QueryValueEx(_key: Key, name: str) -> tuple[str, int]:
            if name not in values:
                raise FileNotFoundError
            return values[name], 1

        @staticmethod
        def DeleteValue(_key: Key, name: str) -> None:
            values.pop(name)

    command = (r"C:\Program Files\Lembrete\python.exe", "-m", "lembrete_agua")
    manager = WindowsAutostartManager(command, Registry())
    manager.set_enabled(True)

    assert manager.is_enabled()
    assert '"C:\\Program Files\\Lembrete\\python.exe"' in values["Lembrete de Água"]
    manager.set_enabled(False)
    assert not manager.is_enabled()
