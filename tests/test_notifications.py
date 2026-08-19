import subprocess

from lembrete_agua.notifications import (
    NOTIFICATION_TITLE,
    NotificationService,
    reminder_message,
)


def test_reminder_message_uses_singular_and_plural() -> None:
    assert reminder_message(1) == "Beba 1 gole de água"
    assert reminder_message(5) == "Beba 5 goles de água"


def test_notification_uses_native_command() -> None:
    calls: list[tuple[object, object]] = []

    def runner(command: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess([], 0)

    assert NotificationService(runner).send(3) is True
    command, kwargs = calls[0]
    assert command[-2:] == (NOTIFICATION_TITLE, "Beba 3 goles de água")
    assert kwargs == {"check": False, "timeout": 10, "text": True}


def test_notification_failure_does_not_crash() -> None:
    def runner(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError

    assert NotificationService(runner).send(1) is False

