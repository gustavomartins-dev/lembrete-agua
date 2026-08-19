from __future__ import annotations

import sys
from dataclasses import replace

import gi

from lembrete_agua.autostart import AutostartManager
from lembrete_agua.config import ConfigStore
from lembrete_agua.models import IntervalUnit, Preferences
from lembrete_agua.notifications import NotificationService
from lembrete_agua.scheduler import ReminderScheduler, SchedulerState
from lembrete_agua.validation import ValidationError, parse_preferences

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402

APPLICATION_ID = "io.github.gustavomartinsdev.LembreteAgua"


class ReminderWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application, title="Lembrete de Água")
        self.set_default_size(420, 390)
        self.set_resizable(False)
        self.connect("close-request", self._on_close_request)

        self._store = ConfigStore()
        self._autostart = AutostartManager()
        self._notifications = NotificationService()
        self._scheduler = ReminderScheduler(GLib.timeout_add, GLib.source_remove)
        self._preferences = self._store.load()
        self._building = True

        self._build_interface()
        self._fill_preferences(self._preferences)
        self._building = False
        self._update_state()

    def _build_interface(self) -> None:
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        self.set_child(content)

        heading = Gtk.Label()
        heading.set_markup("<span size='x-large' weight='bold'>Lembrete de Água 💧</span>")
        heading.set_xalign(0)
        content.append(heading)

        description = Gtk.Label(label="Configure lembretes locais para beber água.")
        description.set_xalign(0)
        description.set_wrap(True)
        content.append(description)

        grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        content.append(grid)

        interval_label = Gtk.Label(label="Intervalo:", xalign=0)
        self._interval = Gtk.SpinButton.new_with_range(1, 1440, 1)
        self._interval.set_hexpand(True)
        self._interval.set_accessible_role(Gtk.AccessibleRole.SPIN_BUTTON)
        interval_label.set_mnemonic_widget(self._interval)
        grid.attach(interval_label, 0, 0, 1, 1)
        grid.attach(self._interval, 1, 0, 1, 1)

        unit_label = Gtk.Label(label="Unidade:", xalign=0)
        self._unit = Gtk.DropDown.new_from_strings(["Minutos", "Horas"])
        self._unit.set_hexpand(True)
        unit_label.set_mnemonic_widget(self._unit)
        grid.attach(unit_label, 0, 1, 1, 1)
        grid.attach(self._unit, 1, 1, 1, 1)

        sips_label = Gtk.Label(label="Quantidade de goles:", xalign=0)
        self._sips = Gtk.SpinButton.new_with_range(1, 100, 1)
        self._sips.set_hexpand(True)
        sips_label.set_mnemonic_widget(self._sips)
        grid.attach(sips_label, 0, 2, 1, 1)
        grid.attach(self._sips, 1, 2, 1, 1)

        autostart_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        autostart_label = Gtk.Label(label="Iniciar com a sessão", xalign=0)
        autostart_label.set_hexpand(True)
        self._autostart_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        autostart_label.set_mnemonic_widget(self._autostart_switch)
        self._autostart_switch.connect("notify::active", self._on_autostart_changed)
        autostart_box.append(autostart_label)
        autostart_box.append(self._autostart_switch)
        content.append(autostart_box)

        self._status = Gtk.Label(xalign=0)
        self._status.set_wrap(True)
        self._status.set_selectable(True)
        content.append(self._status)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        actions.set_halign(Gtk.Align.END)
        self._start_button = Gtk.Button(label="Iniciar")
        self._start_button.add_css_class("suggested-action")
        self._start_button.connect("clicked", self._on_start)
        self._pause_button = Gtk.Button(label="Pausar")
        self._pause_button.connect("clicked", self._on_pause_resume)
        actions.append(self._start_button)
        actions.append(self._pause_button)
        content.append(actions)

        health_note = Gtk.Label(
            label="Este aplicativo é apenas um lembrete e não oferece orientação médica.",
            xalign=0,
        )
        health_note.set_wrap(True)
        health_note.add_css_class("dim-label")
        content.append(health_note)

    def _fill_preferences(self, preferences: Preferences) -> None:
        self._interval.set_value(preferences.interval)
        self._unit.set_selected(0 if preferences.unit is IntervalUnit.MINUTES else 1)
        self._sips.set_value(preferences.sips)
        enabled = preferences.autostart and self._autostart.is_enabled()
        self._autostart_switch.set_active(enabled)
        if enabled != preferences.autostart:
            self._preferences = replace(preferences, autostart=enabled)
            self._save_preferences()

    def _read_preferences(self) -> Preferences:
        unit = IntervalUnit.MINUTES if self._unit.get_selected() == 0 else IntervalUnit.HOURS
        return parse_preferences(
            self._interval.get_text(),
            unit.value,
            self._sips.get_text(),
            autostart=self._autostart_switch.get_active(),
        )

    def _on_start(self, _button: Gtk.Button) -> None:
        try:
            self._preferences = self._read_preferences()
            self._save_preferences()
            self._scheduler.start(
                self._preferences.interval_seconds,
                self._send_reminder,
            )
        except (ValidationError, OSError) as error:
            self._show_error(str(error))
            return
        self._update_state()

    def _on_pause_resume(self, _button: Gtk.Button) -> None:
        if self._scheduler.state is SchedulerState.RUNNING:
            self._scheduler.pause()
        elif self._scheduler.state is SchedulerState.PAUSED:
            self._scheduler.resume()
        self._update_state()

    def _on_close_request(self, _window: Gtk.Window) -> bool:
        if self._scheduler.state is SchedulerState.RUNNING:
            self.set_visible(False)
            return True
        return False

    def _on_autostart_changed(self, switch: Gtk.Switch, _parameter: object) -> None:
        if self._building:
            return
        enabled = switch.get_active()
        try:
            self._autostart.set_enabled(enabled)
            self._preferences = replace(self._preferences, autostart=enabled)
            self._save_preferences()
        except OSError as error:
            self._building = True
            switch.set_active(not enabled)
            self._building = False
            self._show_error(f"Não foi possível alterar o início automático: {error}")

    def _save_preferences(self) -> None:
        self._store.save(self._preferences)

    def _send_reminder(self) -> None:
        if not self._notifications.send(self._preferences.sips):
            self._status.set_text(
                "Ativo — não foi possível exibir a última notificação. "
                "Verifique se notify-send está instalado."
            )

    def _update_state(self) -> None:
        state = self._scheduler.state
        if state is SchedulerState.STOPPED:
            self._status.set_text("Estado: parado. Configure os valores e selecione Iniciar.")
            self._pause_button.set_sensitive(False)
            self._pause_button.set_label("Pausar")
            return

        if self._preferences.interval == 1:
            unit = "minuto" if self._preferences.unit is IntervalUnit.MINUTES else "hora"
        else:
            unit = self._preferences.unit.value
        details = (
            f"{self._preferences.interval} {unit}; "
            f"{self._preferences.sips} "
            f"{'gole' if self._preferences.sips == 1 else 'goles'}"
        )
        self._status.set_text(f"Estado: {state.value.lower()} — {details}.")
        self._pause_button.set_sensitive(True)
        self._pause_button.set_label(
            "Retomar" if state is SchedulerState.PAUSED else "Pausar"
        )

    def _show_error(self, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.ERROR,
            text="Não foi possível salvar a configuração",
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda current, _response: current.destroy())
        dialog.present()


class WaterReminderApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)

    def do_activate(self) -> None:
        window = self.get_active_window()
        if window is None:
            window = ReminderWindow(self)
        window.present()


def main() -> int:
    application = WaterReminderApplication()
    return application.run(sys.argv)
