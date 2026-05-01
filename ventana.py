import gi
import subprocess
import json
import os
import sys
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR


def log(level, message):
    if level == "DEBUG" and LOG_LEVEL != "DEBUG":
        return
    if level == "INFO" and LOG_LEVEL not in ["DEBUG", "INFO"]:
        return
    print(f"[{level}] {message}", file=sys.stderr)

APPS = [
    ("kitty", "Kitty", "utilities-terminal", "class", "kitty"),
    ("brave-browser", "Brave", "internet-web-browser", "class", "brave-browser"),
    ("whatsapp", "WhatsApp", "whatsapp", "class", "brave-web.whatsapp.com__-Default"),
    ("x-twitter", "X", "twitter", "title", ".*X.*"),
    ("youtube", "YouTube", "youtube", "title", ".*YouTube.*"),
    ("org.kde.dolphin", "Dolphin", "system-file-manager", "class", "org.kde.dolphin"),
    ("code", "VSCode", "accessories-text-editor", "class", "code"),
]

APP_INFO = {app_id: (match_type, match_value) for app_id, _, _, match_type, match_value in APPS}


def get_app_match(app_id):
    return APP_INFO.get(app_id, ("class", app_id))


CONFIG_DIR = os.path.expanduser("~/.config/ventana_gtk")
CONFIG_FILE = os.path.join(CONFIG_DIR, "transparencias.json")

SLIDER_MIN = 0.3
SLIDER_MAX = 1.0
SLIDER_STEP = 0.05


def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                for app_class, value in data.items():
                    if value is not None and isinstance(value, (int, float)) and SLIDER_MIN <= float(value) <= SLIDER_MAX:
                        data[app_class] = float(value)
                    else:
                        data[app_class] = None
                log("DEBUG", f"Config cargada: {data}")
                return data
        except (json.JSONDecodeError, IOError, ValueError) as e:
            log("WARNING", f"Error al cargar config: {e}")
            pass
    log("DEBUG", "Usando config por defecto")
    return {app_id: None for app_id, _, _, _, _ in APPS}


def guardar_config(data):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log("DEBUG", f"Config guardada: {data}")
    except IOError as e:
        log("ERROR", f"Error al guardar config: {e}")


def format_alpha_value(alpha):
    return "1.0" if alpha is None else str(alpha)


def is_hyprland_available():
    try:
        result = subprocess.run(['which', 'hyprctl'], capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


HYPRLAND_AVAILABLE = is_hyprland_available()


import threading


def aplicar_windowrule(app_id, alpha):
    def _run():
        if not HYPRLAND_AVAILABLE:
            return
        try:
            match_type, match_value = get_app_match(app_id)
            opacity_value = format_alpha_value(alpha)
            rule = f"opacity {opacity_value}, match:{match_type} {match_value}"
            subprocess.run(['hyprctl', 'keyword', 'windowrule', rule], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    threading.Thread(target=_run, daemon=True).start()


def aplicar_setprop_inmediato(app_id, alpha):
    def _run():
        if not HYPRLAND_AVAILABLE:
            return
        try:
            result = subprocess.run(['hyprctl', 'clients', '-j'], capture_output=True, text=True, timeout=5)
            try:
                clients = json.loads(result.stdout)
            except json.JSONDecodeError:
                return
            
            match_type, match_value = get_app_match(app_id)
            alpha_val = format_alpha_value(alpha)
            
            for client in clients:
                if match_type == "title":
                    if re.search(match_value, client.get('title', '')):
                        addr = client.get('address')
                        if addr:
                            subprocess.run(['hyprctl', 'dispatch', f'setprop address:{addr}', 'opacity', alpha_val], capture_output=True, timeout=5)
                else:
                    if client.get('class') == match_value:
                        addr = client.get('address')
                        if addr:
                            subprocess.run(['hyprctl', 'dispatch', f'setprop address:{addr}', 'opacity', alpha_val], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    threading.Thread(target=_run, daemon=True).start()


class Ventana(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mi ventana en Wayland")
        self.set_role("ventanaGTK")
        self.set_default_size(480, 380)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.connect("key-press-event", self._on_key_press)

        self.config = cargar_config()
        self.css_provider = Gtk.CssProvider()
        self._aplicar_estilos()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        header = Gtk.Label(label="Control de Transparencia")
        header.set_margin_top(15)
        header.set_margin_bottom(10)
        main_box.pack_start(header, False, False, 0)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        self.box.set_margin_bottom(15)
        main_box.pack_start(self.box, True, True, 0)

        self.controles = {}
        self._crear_controles_transparencia()

    def _aplicar_estilos(self):
        css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estilo.css")
        if os.path.exists(css_path):
            self.css_provider.load_from_path(css_path)
        screen = Gdk.Screen.get_default()
        if screen is not None:
            style_context = Gtk.StyleContext()
            style_context.add_provider_for_screen(
                screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _crear_controles_transparencia(self):
        for i, (app_id, app_name, icon_name, _, _) in enumerate(APPS):
            fila = self._crear_fila_app(app_id, app_name, icon_name)
            self.box.pack_start(fila, False, False, 0)
            
            if i < len(APPS) - 1:
                separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
                separator.set_margin_top(8)
                separator.set_margin_bottom(8)
                self.box.pack_start(separator, False, False, 0)

    def _crear_fila_app(self, app_id, app_name, icon_name):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.set_margin_top(8)
        container.set_margin_bottom(8)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        try:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        except GLib.Error:
            icon = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        
        label = Gtk.Label(label=app_name)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        
        switch = Gtk.Switch()
        switch.set_tooltip_text(f"Activar transparencia para {app_name}")

        header.pack_start(icon, False, False, 0)
        header.pack_start(label, False, False, 8)
        header.pack_end(switch, False, False, 0)

        slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, SLIDER_MIN, SLIDER_MAX, SLIDER_STEP)
        slider.set_hexpand(True)
        slider.set_draw_value(False)
        slider.set_sensitive(False)
        slider.set_tooltip_text(f"Ajustar transparencia de {app_name}")

        percentage_label = Gtk.Label(label="0%")
        percentage_label.set_width_chars(5)
        percentage_label.set_halign(Gtk.Align.END)
        percentage_label.set_margin_end(8)

        slider_box.pack_start(slider, True, True, 0)
        slider_box.pack_start(percentage_label, False, False, 0)

        saved_alpha = self.config.get(app_id)
        if saved_alpha is not None:
            switch.set_active(True)
            slider.set_sensitive(True)
            slider.set_value(saved_alpha)
            percentage_label.set_text(f"{int(saved_alpha * 100)}%")
        
        self.controles[app_id] = {
            "switch": switch,
            "slider": slider,
            "percentage_label": percentage_label,
            "app_id": app_id,
            "enabled": saved_alpha is not None
        }

        switch.connect("notify::active", self._on_toggle, app_id)
        slider.connect("value-changed", self._on_slider_update, app_id)
        slider.connect("button-release-event", self._on_slider_release, app_id)

        container.pack_start(header, False, False, 0)
        container.pack_start(slider_box, False, False, 0)

        return container

    def _on_toggle(self, switch, gparam, app_id):
        controles = self.controles[app_id]
        is_active = switch.get_active()
        
        controles["enabled"] = is_active
        controles["slider"].set_sensitive(is_active)
        
        if is_active:
            alpha = controles["slider"].get_value()
            if self.config.get(app_id) is None:
                self.config[app_id] = alpha
                guardar_config(self.config)
            self._aplicar_transparencia(app_id, alpha)
        else:
            controles["percentage_label"].set_text("0%")
            self.config[app_id] = None
            guardar_config(self.config)
            aplicar_windowrule(app_id, None)
            aplicar_setprop_inmediato(app_id, None)

    def _on_slider_update(self, slider, app_id):
        controles = self.controles[app_id]
        if not controles["enabled"]:
            return
        alpha = controles["slider"].get_value()
        controles["percentage_label"].set_text(f"{int(alpha * 100)}%")

    def _on_slider_release(self, widget, event, app_id):
        controles = self.controles[app_id]
        if not controles["enabled"]:
            return
        alpha = controles["slider"].get_value()
        self._aplicar_transparencia(app_id, alpha)

    def _aplicar_transparencia(self, app_id, alpha):
        controles = self.controles[app_id]
        controles["percentage_label"].set_text(f"{int(alpha * 100)}%")
        self.config[app_id] = alpha
        guardar_config(self.config)
        aplicar_windowrule(app_id, alpha)
        aplicar_setprop_inmediato(app_id, alpha)

    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        elif event.keyval == Gdk.KEY_Tab:
            current = self.get_focus()
            if current is None:
                first = next((c["switch"] for c in self.controles.values()), None)
                if first:
                    first.grab_focus()
            return True
        return False


win = Ventana()
if not HYPRLAND_AVAILABLE:
    print("Advertencia: Hyprland no detectado. La aplicación puede no funcionar correctamente.")
win.connect("destroy", lambda w: guardar_config(win.config))
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
