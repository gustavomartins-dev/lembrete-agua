from lembrete_agua.notifications import reminder_message


def test_reminder_message_uses_singular_and_plural() -> None:
    assert reminder_message(1) == "Beba 1 gole de água"
    assert reminder_message(5) == "Beba 5 goles de água"
