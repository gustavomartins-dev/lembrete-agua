from pathlib import Path

from lembrete_agua.autostart import AutostartManager


def test_enable_and_disable_autostart(tmp_path: Path) -> None:
    path = tmp_path / "autostart" / "lembrete-agua.desktop"
    manager = AutostartManager(path, ("/opt/Lembrete Água/bin/app", "--quiet"))

    manager.set_enabled(True)

    content = path.read_text(encoding="utf-8")
    assert "Type=Application" in content
    assert "Exec='/opt/Lembrete Água/bin/app' --quiet" in content
    assert manager.is_enabled()

    manager.set_enabled(False)
    assert not manager.is_enabled()

