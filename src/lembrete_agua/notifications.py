from __future__ import annotations

NOTIFICATION_TITLE = "Hora de beber água 💧"


def reminder_message(sips: int) -> str:
    noun = "gole" if sips == 1 else "goles"
    return f"Beba {sips} {noun} de água"
