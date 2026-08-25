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

        def __init__(self) -> None:
            self.actions: list[object] = []

        def AddAction(self, action: object) -> None:
            self.actions.append(action)

    class FakeToaster:
        def show_toast(self, toast: object) -> None:
            shown.append(toast)

    service = WindowsNotificationService(
        activated.append,
        toaster=FakeToaster(),
        toast_factory=FakeToast,
        toast_duration="long",
        toast_scenario="reminder",
    )
    service.send("record-1", 5, 125)

    toast = shown[0]
    assert toast.text_fields[0] == "Hora de beber água 💧"
    assert "125 mL" in toast.text_fields[1]
    assert toast.duration == "long"
    assert toast.scenario == "reminder"
    toast.on_activated(None)
    assert activated == ["record-1"]


def test_windows_confirm_now_button_accepts_without_opening_confirmation() -> None:
    shown: list[object] = []
    opened: list[str] = []
    accepted: list[str] = []

    class FakeToast:
        def AddAction(self, action: object) -> None:
            self.action = action

    class FakeToaster:
        def show_toast(self, toast: object) -> None:
            shown.append(toast)

    service = WindowsNotificationService(
        opened.append,
        accepted.append,
        toaster=FakeToaster(),
        toast_factory=FakeToast,
        button_factory=lambda label, action: (label, action),
    )
    service.send("record-1", 5, 125)
    toast = shown[0]

    toast.on_activated(type("Arguments", (), {"arguments": "accept:record-1"})())

    assert toast.action == ("Confirmar agora", "accept:record-1")
    assert accepted == ["record-1"]
    assert opened == []


def test_windows_notification_service_clears_app_toasts() -> None:
    class FakeToaster:
        def __init__(self) -> None:
            self.cleared = False

        def show_toast(self, _toast: object) -> None:
            pass

        def clear_toasts(self) -> None:
            self.cleared = True

    toaster = FakeToaster()
    service = WindowsNotificationService(
        lambda _record_id: None,
        toaster=toaster,
        toast_factory=lambda: type("Toast", (), {})(),
    )
    service.send("record-1", 5, 125)

    service.clear()

    assert toaster.cleared
    assert service._active_toasts == []
