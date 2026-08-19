from __future__ import annotations

import math
import sys
import uuid
from dataclasses import replace
from datetime import datetime

import gi

from lembrete_agua.analytics import period_stats
from lembrete_agua.autostart import (
    APPLICATION_ID,
    AutostartManager,
    DbusServiceManager,
    DesktopEntryManager,
    IconManager,
)
from lembrete_agua.config import ConfigStore
from lembrete_agua.history import HistoryStore, ReminderRecord, ReminderStatus
from lembrete_agua.models import (
    DurationUnit,
    HydrationPlan,
    Preferences,
    build_hydration_plan,
)
from lembrete_agua.notifications import NOTIFICATION_TITLE, reminder_message
from lembrete_agua.scheduler import ReminderScheduler, SchedulerState
from lembrete_agua.validation import ValidationError, parse_preferences

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk  # noqa: E402


def format_duration(seconds: float) -> str:
    remaining = max(0, math.ceil(seconds))
    hours, remainder = divmod(remaining, 3_600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


class TimerRing(Gtk.Overlay):
    def __init__(self) -> None:
        super().__init__()
        self._fraction = 0.0
        self._drawing = Gtk.DrawingArea(width_request=190, height_request=190)
        self._drawing.set_draw_func(self._draw)
        self.set_child(self._drawing)
        self._label = Gtk.Label()
        self._label.set_markup("<span size='xx-large' weight='bold'>--:--</span>")
        self.add_overlay(self._label)

    def update(self, remaining: float | None, total: float | None) -> None:
        if remaining is None or not total:
            self._fraction = 0.0
            text = "--:--"
        else:
            self._fraction = min(1.0, max(0.0, remaining / total))
            text = format_duration(remaining)
        self._label.set_markup(f"<span size='xx-large' weight='bold'>{text}</span>")
        self._drawing.queue_draw()

    def _draw(self, _area: Gtk.DrawingArea, context: object, width: int, height: int) -> None:
        radius = min(width, height) / 2 - 12
        center_x, center_y = width / 2, height / 2
        context.set_line_width(12)
        context.set_source_rgba(0.3, 0.4, 0.5, 0.18)
        context.arc(center_x, center_y, radius, 0, 2 * math.pi)
        context.stroke()
        context.set_source_rgb(0.12, 0.55, 0.9)
        context.arc(
            center_x,
            center_y,
            radius,
            -math.pi / 2,
            -math.pi / 2 + 2 * math.pi * self._fraction,
        )
        context.stroke()


class ReminderWindow(Gtk.ApplicationWindow):
    def __init__(self, application: WaterReminderApplication) -> None:
        super().__init__(application=application, title="Lembrete de Água")
        self.set_default_size(680, 650)
        self.connect("close-request", self._on_close_request)

        self._application = application
        self._store = ConfigStore()
        self._history = HistoryStore()
        self._autostart = AutostartManager()
        self._scheduler = ReminderScheduler(GLib.timeout_add, GLib.source_remove)
        self._preferences = self._store.load()
        if self._preferences.autostart:
            self._autostart.set_enabled(True)
        self._plan: HydrationPlan | None = None
        self._session_id: str | None = None
        self._reminder_number = 0
        self._selected_record_id: str | None = None
        self._building = True

        self._build_interface()
        self._fill_preferences(self._preferences)
        self._building = False
        self._update_plan_preview()
        self._update_dashboard()
        GLib.timeout_add_seconds(1, self._on_clock_tick)

    def _build_interface(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(18)
        root.set_margin_bottom(18)
        root.set_margin_start(20)
        root.set_margin_end(20)
        self.set_child(root)

        heading = Gtk.Label(xalign=0)
        heading.set_markup("<span size='x-large' weight='bold'>Lembrete de Água 💧</span>")
        root.append(heading)

        self._stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self._stack.set_vexpand(True)
        switcher = Gtk.StackSwitcher(stack=self._stack, halign=Gtk.Align.CENTER)
        root.append(switcher)
        root.append(self._stack)

        self._stack.add_titled(self._build_plan_page(), "plan", "Plano")
        self._stack.add_titled(self._build_dashboard_page(), "dashboard", "Dashboard")
        self._stack.add_titled(self._build_confirmation_page(), "confirmation", "Confirmação")

    def _build_plan_page(self) -> Gtk.Widget:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_margin_top(18)

        intro = Gtk.Label(
            label=(
                "Informe quanto deseja beber e em quanto tempo. "
                "O aplicativo calcula os goles e os intervalos."
            ),
            xalign=0,
            wrap=True,
        )
        page.append(intro)

        grid = Gtk.Grid(column_spacing=14, row_spacing=14)
        page.append(grid)
        amount_label = Gtk.Label(label="Quantidade (mL):", xalign=0)
        self._target_ml = Gtk.SpinButton.new_with_range(25, 10_000, 25)
        self._target_ml.set_hexpand(True)
        self._target_ml.connect("value-changed", self._on_preview_changed)
        amount_label.set_mnemonic_widget(self._target_ml)
        grid.attach(amount_label, 0, 0, 1, 1)
        grid.attach(self._target_ml, 1, 0, 1, 1)

        duration_label = Gtk.Label(label="Prazo:", xalign=0)
        self._duration = Gtk.SpinButton.new_with_range(1, 1440, 1)
        self._duration.set_hexpand(True)
        self._duration.connect("value-changed", self._on_preview_changed)
        duration_label.set_mnemonic_widget(self._duration)
        grid.attach(duration_label, 0, 1, 1, 1)
        grid.attach(self._duration, 1, 1, 1, 1)

        unit_label = Gtk.Label(label="Unidade do prazo:", xalign=0)
        self._unit = Gtk.DropDown.new_from_strings(["Minutos", "Horas"])
        self._unit.set_hexpand(True)
        self._unit.connect("notify::selected", self._on_preview_changed)
        unit_label.set_mnemonic_widget(self._unit)
        grid.attach(unit_label, 0, 2, 1, 1)
        grid.attach(self._unit, 1, 2, 1, 1)

        self._preview = Gtk.Label(xalign=0, wrap=True)
        self._preview.add_css_class("card")
        self._preview.set_margin_top(8)
        self._preview.set_margin_bottom(8)
        self._preview.set_margin_start(12)
        self._preview.set_margin_end(12)
        page.append(self._preview)

        autostart_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        autostart_label = Gtk.Label(label="Iniciar com a sessão", xalign=0, hexpand=True)
        self._autostart_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self._autostart_switch.connect("notify::active", self._on_autostart_changed)
        autostart_box.append(autostart_label)
        autostart_box.append(self._autostart_switch)
        page.append(autostart_box)

        self._status = Gtk.Label(xalign=0, wrap=True, selectable=True)
        page.append(self._status)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        actions.set_halign(Gtk.Align.END)
        self._start_button = Gtk.Button(label="Iniciar plano")
        self._start_button.add_css_class("suggested-action")
        self._start_button.connect("clicked", self._on_start)
        self._pause_button = Gtk.Button(label="Pausar")
        self._pause_button.connect("clicked", self._on_pause_resume)
        actions.append(self._start_button)
        actions.append(self._pause_button)
        page.append(actions)
        return page

    def _build_dashboard_page(self) -> Gtk.Widget:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page.set_margin_top(16)
        self._timer_ring = TimerRing()
        self._timer_ring.set_halign(Gtk.Align.CENTER)
        page.append(self._timer_ring)
        self._next_label = Gtk.Label(label="Nenhum plano ativo", wrap=True)
        page.append(self._next_label)

        metrics = Gtk.Grid(column_spacing=12, row_spacing=8, column_homogeneous=True)
        self._week_metric = Gtk.Label()
        self._month_metric = Gtk.Label()
        self._pending_metric = Gtk.Label()
        for column, (title, widget) in enumerate(
            (
                ("7 dias", self._week_metric),
                ("30 dias", self._month_metric),
                ("Pendentes", self._pending_metric),
            )
        ):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            box.add_css_class("card")
            title_label = Gtk.Label(label=title)
            title_label.add_css_class("dim-label")
            box.append(title_label)
            box.append(widget)
            metrics.attach(box, column, 0, 1, 1)
        page.append(metrics)

        history_title = Gtk.Label(xalign=0)
        history_title.set_markup("<b>Histórico recente</b>")
        page.append(history_title)
        scroll = Gtk.ScrolledWindow(vexpand=True, min_content_height=180)
        self._history_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self._history_list.add_css_class("boxed-list")
        scroll.set_child(self._history_list)
        page.append(scroll)
        return page

    def _build_confirmation_page(self) -> Gtk.Widget:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        page.set_margin_top(40)
        page.set_halign(Gtk.Align.CENTER)
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>Você bebeu a água?</span>")
        page.append(title)
        self._confirmation_details = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        page.append(self._confirmation_details)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        yes = Gtk.Button(label="Sim, eu bebi")
        yes.add_css_class("suggested-action")
        yes.connect("clicked", lambda _button: self._answer_reminder(True))
        no = Gtk.Button(label="Não bebi")
        no.connect("clicked", lambda _button: self._answer_reminder(False))
        actions.append(no)
        actions.append(yes)
        page.append(actions)
        self._confirmation_status = Gtk.Label(wrap=True)
        page.append(self._confirmation_status)
        return page

    def _fill_preferences(self, preferences: Preferences) -> None:
        self._target_ml.set_value(preferences.target_ml)
        self._duration.set_value(preferences.duration)
        self._unit.set_selected(0 if preferences.unit is DurationUnit.MINUTES else 1)
        enabled = self._autostart.is_enabled()
        self._autostart_switch.set_active(enabled)
        if enabled != preferences.autostart:
            self._preferences = replace(preferences, autostart=enabled)
            self._store.save(self._preferences)

    def _read_preferences(self) -> Preferences:
        unit = DurationUnit.MINUTES if self._unit.get_selected() == 0 else DurationUnit.HOURS
        return parse_preferences(
            self._target_ml.get_text(),
            self._duration.get_text(),
            unit.value,
            autostart=self._autostart_switch.get_active(),
        )

    def _on_preview_changed(self, *_args: object) -> None:
        if not self._building:
            self._update_plan_preview()

    def _update_plan_preview(self) -> None:
        try:
            plan = build_hydration_plan(self._read_preferences())
        except ValidationError as error:
            self._preview.set_text(str(error))
            return
        interval = format_duration(plan.interval_seconds)
        self._preview.set_markup(
            f"<b>Plano recomendado</b>\n{plan.total_sips} goles estimados em "
            f"{plan.reminder_count} lembretes, a cada {interval}.\n"
            "Estimativa usada: 25 mL por gole, até 5 goles por lembrete."
        )

    def _on_start(self, _button: Gtk.Button) -> None:
        try:
            self._preferences = self._read_preferences()
            self._store.save(self._preferences)
            self._plan = build_hydration_plan(self._preferences)
            self._session_id = str(uuid.uuid4())
            self._reminder_number = 0
            self._scheduler.start(self._plan.interval_seconds, self._create_reminder)
        except (ValidationError, OSError) as error:
            self._show_error(str(error))
            return
        self._update_state()
        self._stack.set_visible_child_name("dashboard")
        self._update_dashboard()

    def _create_reminder(self) -> None:
        if self._plan is None or self._session_id is None:
            return
        self._reminder_number += 1
        record = ReminderRecord.create(
            self._session_id,
            self._plan.sips_for_reminder(self._reminder_number),
            self._plan.milliliters_for_reminder(self._reminder_number),
        )
        try:
            self._history.add(record)
        except OSError as error:
            self._show_error(f"Não foi possível registrar o lembrete: {error}")
            return
        self._application.send_reminder_notification(record)
        if self._reminder_number >= self._plan.reminder_count:
            self._scheduler.stop()
        self._update_state()
        self._update_dashboard()

    def show_confirmation(self, record_id: str) -> None:
        record = self._history.get(record_id)
        self.present()
        if record is None:
            self._confirmation_details.set_text("Este lembrete não foi encontrado no histórico.")
            self._confirmation_status.set_text("")
        else:
            self._selected_record_id = record.id
            self._confirmation_details.set_text(
                f"Confirme o lembrete de {record.milliliters} mL "
                f"({record.sips} {'gole' if record.sips == 1 else 'goles'})."
            )
            self._confirmation_status.set_text(
                "Resposta já registrada: " + record.status.value
                if record.status is not ReminderStatus.PENDING
                else ""
            )
        self._stack.set_visible_child_name("confirmation")

    def _answer_reminder(self, drank: bool) -> None:
        if self._selected_record_id is None:
            self._confirmation_status.set_text("Nenhum lembrete selecionado.")
            return
        try:
            record = self._history.respond(self._selected_record_id, drank)
        except OSError as error:
            self._show_error(f"Não foi possível salvar a resposta: {error}")
            return
        if record is None:
            self._confirmation_status.set_text("Este lembrete não existe mais.")
            return
        self._application.withdraw_notification(record.id)
        self._confirmation_status.set_text("Resposta salva no seu histórico.")
        self._update_dashboard()
        self._stack.set_visible_child_name("dashboard")

    def _on_pause_resume(self, _button: Gtk.Button) -> None:
        if self._scheduler.state is SchedulerState.RUNNING:
            self._scheduler.pause()
        elif self._scheduler.state is SchedulerState.PAUSED:
            self._scheduler.resume()
        self._update_state()
        self._update_dashboard()

    def _on_autostart_changed(self, switch: Gtk.Switch, _parameter: object) -> None:
        if self._building:
            return
        enabled = switch.get_active()
        try:
            self._autostart.set_enabled(enabled)
            self._preferences = replace(self._preferences, autostart=enabled)
            self._store.save(self._preferences)
        except OSError as error:
            self._building = True
            switch.set_active(not enabled)
            self._building = False
            self._show_error(f"Não foi possível alterar o início automático: {error}")

    def _on_clock_tick(self) -> bool:
        self._update_timer()
        return True

    def _update_timer(self) -> None:
        total = self._plan.interval_seconds if self._plan else None
        remaining = self._scheduler.remaining_seconds
        self._timer_ring.update(remaining, total)
        if remaining is not None:
            self._next_label.set_text(f"Próximo lembrete em {format_duration(remaining)}")
        elif self._scheduler.state is SchedulerState.PAUSED:
            self._next_label.set_text("Plano pausado")
        else:
            self._next_label.set_text("Nenhum lembrete agendado")

    def _update_dashboard(self) -> None:
        records = self._history.load()
        week = period_stats(records, 7)
        month = period_stats(records, 30)
        pending = sum(record.status is ReminderStatus.PENDING for record in records)
        self._week_metric.set_markup(
            f"<b>{week.consumed_ml} mL</b> · {week.performance_percent}%"
        )
        self._month_metric.set_markup(
            f"<b>{month.consumed_ml} mL</b> · {month.performance_percent}%"
        )
        self._pending_metric.set_markup(f"<b>{pending}</b>")
        self._update_timer()
        while child := self._history_list.get_first_child():
            self._history_list.remove(child)
        for record in reversed(records[-30:]):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_margin_top(8)
            row.set_margin_bottom(8)
            row.set_margin_start(10)
            row.set_margin_end(10)
            date = datetime.fromisoformat(record.scheduled_at).astimezone()
            label = Gtk.Label(
                label=f"{date:%d/%m %H:%M} · {record.milliliters} mL · {record.status.value}",
                xalign=0,
                hexpand=True,
            )
            row.append(label)
            if record.status is ReminderStatus.PENDING:
                button = Gtk.Button(label="Responder")
                button.connect(
                    "clicked",
                    lambda _button, record_id=record.id: self.show_confirmation(record_id),
                )
                row.append(button)
            self._history_list.append(row)
        if not records:
            self._history_list.append(Gtk.Label(label="Ainda não há lembretes no histórico."))

    def _update_state(self) -> None:
        state = self._scheduler.state
        if state is SchedulerState.STOPPED:
            self._status.set_text("Estado: plano concluído ou parado.")
            self._pause_button.set_sensitive(False)
            self._pause_button.set_label("Pausar")
            return
        self._status.set_text(
            f"Estado: {state.value.lower()} · lembrete {self._reminder_number + 1} "
            f"de {self._plan.reminder_count if self._plan else 0}."
        )
        self._pause_button.set_sensitive(True)
        self._pause_button.set_label("Retomar" if state is SchedulerState.PAUSED else "Pausar")

    def _on_close_request(self, _window: Gtk.Window) -> bool:
        if self._scheduler.state is SchedulerState.RUNNING:
            self.set_visible(False)
            return True
        return False

    def _show_error(self, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.ERROR,
            text="Não foi possível concluir a operação",
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda current, _response: current.destroy())
        dialog.present()


class WaterReminderApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APPLICATION_ID)
        IconManager().install()
        Gtk.Window.set_default_icon_name(APPLICATION_ID)
        DesktopEntryManager().install()
        DbusServiceManager().install()
        action = Gio.SimpleAction.new("confirm-reminder", GLib.VariantType.new("s"))
        action.connect("activate", self._on_confirm_action)
        self.add_action(action)

    def do_activate(self) -> None:
        window = self.get_active_window()
        if window is None:
            window = ReminderWindow(self)
        window.present()

    def _on_confirm_action(self, _action: Gio.SimpleAction, target: GLib.Variant) -> None:
        window = self.get_active_window()
        if window is None:
            window = ReminderWindow(self)
        window.show_confirmation(target.get_string())

    def send_reminder_notification(self, record: ReminderRecord) -> None:
        notification = Gio.Notification.new(NOTIFICATION_TITLE)
        notification.set_icon(Gio.ThemedIcon.new(APPLICATION_ID))
        notification.set_body(
            f"{reminder_message(record.sips)} ({record.milliliters} mL). Clique para confirmar."
        )
        target = GLib.Variant("s", record.id)
        notification.set_default_action_and_target("app.confirm-reminder", target)
        notification.add_button_with_target("Confirmar agora", "app.confirm-reminder", target)
        self.send_notification(record.id, notification)


def main() -> int:
    application = WaterReminderApplication()
    return application.run(sys.argv)
