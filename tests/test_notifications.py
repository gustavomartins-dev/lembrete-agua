from lembrete_agua.notifications import WindowsNotificationService, reminder_message


def test_reminder_message_uses_singular_and_plural() -> None:
    assert reminder_message(1) == "Beba 1 gole de água"
    assert reminder_message(5) == "Beba 5 goles de água"


def test_windows_notification_opens_corresponding_confirmation() -> None:
    shown: list[object] = []
    activated: list[str] = []

    class FakeToast:
        text_fields: list[str]
        on_activated: object

    class FakeToaster:
        def show_toast(self, toast: object) -> None:
            shown.append(toast)

    service = WindowsNotificationService(
        activated.append,
        toaster=FakeToaster(),
        toast_factory=FakeToast,
    )
    service.send("record-1", 5, 125)

    toast = shown[0]
    assert toast.text_fields[0] == "Hora de beber água 💧"
    assert "125 mL" in toast.text_fields[1]
    toast.on_activated(None)
    assert activated == ["record-1"]
