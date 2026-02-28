from __future__ import annotations

import colorsys
import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Protocol


GRID_SIZE = 8
DEFAULT_SCENE_NAME = "Untitled"
PALETTE_COLUMNS = 8
CANONICAL_PALETTE_PATH = Path(__file__).resolve().parent / "config" / "lpx_palette.json"
CALIBRATION_PATH = Path(__file__).resolve().parent / "config" / "velocity_colors.json"
DEFAULT_PALETTE_VALUES = list(range(128))
DEFAULT_SEMANTIC_COLORS = {
    "off": 0,
    "white": 1,
    "red": 69,
    "orange": 100,
    "yellow": 102,
    "green": 84,
    "cyan": 86,
    "blue": 66,
    "purple": 49,
    "pink": 63,
}
# Full 128-color velocity lookup table for Launchpad X.
# Velocities 0-51 follow a 4-shade-per-hue pattern: pastel, full, dark, dim.
# Velocities 52-127 are extended/mixed colors.
# Calibrated from hardware photos + Novation programmer reference.
VELOCITY_HEX = [
    # 0-3: Grayscale
    "#000000",  # 0  Off
    "#f2f4f7",  # 1  White
    "#a0a0a0",  # 2  Gray
    "#505050",  # 3  Dark gray
    # 4-7: Red
    "#ff6b60",  # 4  Pastel red
    "#ff0000",  # 5  Red
    "#590000",  # 6  Dark red
    "#1c0000",  # 7  Dim red
    # 8-11: Orange
    "#ffbd7f",  # 8  Pastel orange
    "#ff5400",  # 9  Orange
    "#591d00",  # 10 Dark orange
    "#1c0800",  # 11 Dim orange
    # 12-15: Yellow
    "#ffff3c",  # 12 Pastel yellow
    "#ffff00",  # 13 Yellow
    "#595900",  # 14 Dark yellow
    "#1c1c00",  # 15 Dim yellow
    # 16-19: Chartreuse
    "#80ff3c",  # 16 Pastel chartreuse
    "#3cff00",  # 17 Chartreuse
    "#165900",  # 18 Dark chartreuse
    "#041c00",  # 19 Dim chartreuse
    # 20-23: Green
    "#3cff3c",  # 20 Pastel green
    "#00ff00",  # 21 Green
    "#005900",  # 22 Dark green
    "#001c00",  # 23 Dim green
    # 24-27: Spring green
    "#3cff80",  # 24 Pastel spring green
    "#00ff3c",  # 25 Spring green
    "#005916",  # 26 Dark spring green
    "#001c04",  # 27 Dim spring green
    # 28-31: Cyan
    "#3cffff",  # 28 Pastel cyan
    "#00ffff",  # 29 Cyan
    "#005959",  # 30 Dark cyan
    "#001c1c",  # 31 Dim cyan
    # 32-35: Sky blue
    "#3c80ff",  # 32 Pastel sky blue
    "#003cff",  # 33 Sky blue
    "#001659",  # 34 Dark sky blue
    "#00041c",  # 35 Dim sky blue
    # 36-39: Blue
    "#3c3cff",  # 36 Pastel blue
    "#0000ff",  # 37 Blue
    "#000059",  # 38 Dark blue
    "#00001c",  # 39 Dim blue
    # 40-43: Violet
    "#803cff",  # 40 Pastel violet
    "#3c00ff",  # 41 Violet
    "#160059",  # 42 Dark violet
    "#04001c",  # 43 Dim violet
    # 44-47: Magenta
    "#ff3cff",  # 44 Pastel magenta
    "#ff00ff",  # 45 Magenta
    "#590059",  # 46 Dark magenta
    "#1c001c",  # 47 Dim magenta
    # 48-51: Rose
    "#ff3c80",  # 48 Pastel rose
    "#ff003c",  # 49 Rose / hot pink
    "#590016",  # 50 Dark rose
    "#1c0004",  # 51 Dim rose
    # 52-55: Extra warm
    "#ff1400",  # 52 Red-orange
    "#964c00",  # 53 Amber / brown
    "#593400",  # 54 Dark brown
    "#421c00",  # 55 Dark amber
    # 56-59: Extra darks
    "#003400",  # 56 Forest green
    "#005934",  # 57 Dark teal
    "#001934",  # 58 Dark navy-teal
    "#000000",  # 59 Off
    # 60-63: Extra colors
    "#ff4c16",  # 60 Orange-red
    "#f0a070",  # 61 Salmon
    "#f0d0a0",  # 62 Light peach
    "#ff0066",  # 63 Pink-magenta
    # 64-67
    "#000000",  # 64 Off
    "#3cff00",  # 65 Chartreuse
    "#2e6eff",  # 66 Sky blue
    "#ff5400",  # 67 Orange
    # 68-71
    "#00e5ff",  # 68 Cyan-sky
    "#ff2440",  # 69 Red
    "#3c3cff",  # 70 Blue
    "#ff5400",  # 71 Orange
    # 72-75
    "#ff0000",  # 72 Red
    "#80ff00",  # 73 Yellow-green
    "#00ff00",  # 74 Green
    "#00ff3c",  # 75 Spring green
    # 76-79
    "#003cff",  # 76 Blue
    "#ff8050",  # 77 Warm peach
    "#00ff00",  # 78 Green
    "#ff00ff",  # 79 Magenta
    # 80-83
    "#1c5900",  # 80 Dark chartreuse
    "#0050ff",  # 81 Blue
    "#003cff",  # 82 Blue
    "#ffff00",  # 83 Yellow
    # 84-87
    "#00ff00",  # 84 Green
    "#00ffa0",  # 85 Mint
    "#00ccc8",  # 86 Teal
    "#8040ff",  # 87 Violet
    # 88-91
    "#ff8000",  # 88 Amber
    "#00ff3c",  # 89 Spring green
    "#003cff",  # 90 Blue
    "#ff0000",  # 91 Red
    # 92-95
    "#8040ff",  # 92 Violet
    "#ea38d0",  # 93 Hot pink
    "#3cff00",  # 94 Chartreuse
    "#ff00ff",  # 95 Magenta
    # 96-99
    "#ff3400",  # 96 Red-orange
    "#ffff00",  # 97 Yellow
    "#ffff00",  # 98 Yellow
    "#80ff00",  # 99 Yellow-green
    # 100-103
    "#ff8000",  # 100 Orange
    "#00ccc8",  # 101 Teal
    "#ccff00",  # 102 Yellow-green
    "#00ffa0",  # 103 Cyan-green
    # 104-107
    "#1c1c00",  # 104 Dim olive
    "#00cccc",  # 105 Teal
    "#00ff00",  # 106 Green
    "#ff0000",  # 107 Red
    # 108-111
    "#003cff",  # 108 Blue
    "#ccff80",  # 109 Light yellow-green
    "#80ff80",  # 110 Light green
    "#00ff00",  # 111 Green
    # 112-115
    "#ff0000",  # 112 Red
    "#00ffff",  # 113 Cyan
    "#00ff00",  # 114 Green
    "#ffff00",  # 115 Yellow
    # 116-119
    "#003cff",  # 116 Blue
    "#8040ff",  # 117 Violet
    "#3c80ff",  # 118 Sky blue
    "#003cff",  # 119 Blue
    # 120-123
    "#000000",  # 120 Off
    "#ffe0a0",  # 121 Warm white
    "#ffd080",  # 122 Warm peach
    "#ffc060",  # 123 Warm amber
    # 124-127
    "#ffb040",  # 124 Amber
    "#806030",  # 125 Dark warm
    "#403020",  # 126 Very dark warm
    "#ff6060",  # 127 Light red
]


def load_velocity_calibration() -> None:
    """Overwrite VELOCITY_HEX from config/velocity_colors.json if it exists."""
    if not CALIBRATION_PATH.exists():
        return
    try:
        data = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
        colors = data.get("colors")
        if isinstance(colors, list) and len(colors) == 128:
            for i, hex_val in enumerate(colors):
                if isinstance(hex_val, str) and len(hex_val) == 7 and hex_val.startswith("#"):
                    VELOCITY_HEX[i] = hex_val
    except Exception:
        pass


load_velocity_calibration()


def clamp_color(value: int) -> int:
    return max(0, min(127, int(value)))


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        return 0, 0, 0
    return int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b))),
    )


def _mix_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(round(a[0] + (b[0] - a[0]) * t)),
        int(round(a[1] + (b[1] - a[1]) * t)),
        int(round(a[2] + (b[2] - a[2]) * t)),
    )


def velocity_to_hex(velocity: int) -> str:
    v = clamp_color(velocity)
    hex_color = VELOCITY_HEX[v]
    r, g, b = _hex_to_rgb(hex_color)
    # Ensure non-off colors have minimum visibility as UI swatches.
    peak = max(r, g, b)
    if 0 < peak < 48:
        factor = 48.0 / peak
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
    return _rgb_to_hex((r, g, b))


def _color_bucket_for_velocity(value: int) -> int:
    # Column order: white, red, orange, yellow, green, blue, purple, cyan.
    r, g, b = _hex_to_rgb(velocity_to_hex(value))
    h, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if s < 0.10:
        return 0  # white/neutral
    deg = h * 360.0
    if deg < 20 or deg >= 340:
        return 1  # red
    if deg < 45:
        return 2  # orange
    if deg < 70:
        return 3  # yellow
    if deg < 160:
        return 4  # green
    if deg < 210:
        return 7  # cyan
    if deg < 270:
        return 5  # blue
    return 6  # purple/pink


def arrange_palette_by_color(values: list[int]) -> list[int]:
    groups: list[list[int]] = [[] for _ in range(PALETTE_COLUMNS)]
    for value in values:
        groups[_color_bucket_for_velocity(value)].append(value)

    for idx, group in enumerate(groups):
        groups[idx] = sorted(
            group,
            key=lambda val: sum(_hex_to_rgb(velocity_to_hex(val))),
            reverse=True,
        )

    rows = max(len(group) for group in groups) if groups else 0
    ordered: list[int] = []
    used: set[int] = set()
    for row in range(rows):
        for col in range(PALETTE_COLUMNS):
            if row < len(groups[col]):
                val = groups[col][row]
                ordered.append(val)
                used.add(val)
    for value in values:
        if value not in used:
            ordered.append(value)
    return ordered


def xy_to_note(x: int, y: int) -> int:
    # Map app r1..r8 to Launchpad X 8x8 matrix rows (note rows 71..11).
    return (8 - y) * 10 + (x + 1)


@dataclass
class Scene:
    name: str
    rows: list[list[int]]

    @staticmethod
    def blank(name: str = DEFAULT_SCENE_NAME) -> "Scene":
        return Scene(name=name, rows=[[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)])

    @staticmethod
    def from_json(data: dict) -> "Scene":
        rows = data.get("rows")
        if not isinstance(rows, list) or len(rows) != GRID_SIZE:
            raise ValueError("Invalid scene rows")
        normalized: list[list[int]] = []
        for row in rows:
            if not isinstance(row, list) or len(row) != GRID_SIZE:
                raise ValueError("Invalid row shape")
            normalized.append([clamp_color(cell) for cell in row])
        return Scene(name=str(data.get("name") or DEFAULT_SCENE_NAME), rows=normalized)

    def to_json(self) -> dict:
        return {"name": self.name, "rows": self.rows}


class Backend(Protocol):
    name: str

    def connect(self) -> tuple[bool, str]:
        ...

    def send_pad(self, x: int, y: int, color: int) -> None:
        ...

    def send_frame(self, rows: list[list[int]]) -> None:
        ...

    def clear(self) -> None:
        ...

    def close(self) -> None:
        ...


class DryRunBackend:
    name = "dry-run"

    def connect(self) -> tuple[bool, str]:
        return True, "Dry-run backend active"

    def send_pad(self, x: int, y: int, color: int) -> None:
        _ = (x, y, color)

    def send_frame(self, rows: list[list[int]]) -> None:
        _ = rows

    def clear(self) -> None:
        pass

    def close(self) -> None:
        pass


class MidoBackend:
    name = "mido"

    def __init__(self) -> None:
        self._mido = None
        self._port = None
        self.port_name = ""

    def connect(self) -> tuple[bool, str]:
        try:
            import mido
        except Exception as exc:  # pragma: no cover
            return False, f"mido import failed: {exc}"
        self._mido = mido
        names = mido.get_output_names()
        if not names:
            return False, "No MIDI outputs found"

        def score_output(name: str) -> tuple[int, int]:
            lower = name.lower()
            score = 0
            if "launchpad x" in lower:
                score += 100
            elif "launchpad" in lower:
                score += 60
            if "lpx midi" in lower or "midi" in lower:
                score += 30
            if "daw" in lower:
                score -= 40
            return score, -len(name)

        ranked = sorted(names, key=score_output, reverse=True)
        target = ranked[0] if ranked else names[0]
        self._port = mido.open_output(target)
        self.port_name = target
        switches = self._set_programmer_mode(target, names)
        if switches:
            return True, f"Connected: {target} (programmer mode set)"
        return True, f"Connected: {target}"

    def _send_programmer_sysex(self, out_port: object) -> bool:
        if not self._mido:
            return False
        # Try Launchpad X and Mini MK3 family IDs.
        for device_id in (0x0D, 0x0C):
            try:
                out_port.send(
                    self._mido.Message("sysex", data=[0x00, 0x20, 0x29, 0x02, device_id, 0x0E, 0x01])
                )
                return True
            except Exception:
                continue
        return False

    def _set_programmer_mode(self, target: str, output_names: list[str]) -> int:
        switches = 0
        if self._port and self._send_programmer_sysex(self._port):
            switches += 1
        target_lower = target.lower()
        if "launchpad" not in target_lower:
            return switches
        for name in output_names:
            lower = name.lower()
            if name == target:
                continue
            if "launchpad" not in lower or "daw" in lower:
                continue
            try:
                extra_port = self._mido.open_output(name)
            except Exception:
                continue
            try:
                if self._send_programmer_sysex(extra_port):
                    switches += 1
            finally:
                extra_port.close()
        return switches

    def send_pad(self, x: int, y: int, color: int) -> None:
        if not self._mido or not self._port:
            return
        msg = self._mido.Message("note_on", note=xy_to_note(x, y), velocity=clamp_color(color), channel=0)
        self._port.send(msg)

    def send_frame(self, rows: list[list[int]]) -> None:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.send_pad(x, y, rows[y][x])

    def clear(self) -> None:
        if not self._mido or not self._port:
            return
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self._port.send(
                    self._mido.Message("note_on", note=xy_to_note(x, y), velocity=0, channel=0)
                )

    def close(self) -> None:
        if self._port:
            self._port.close()
            self._port = None


class LaunchpadPyBackend:
    name = "launchpad.py"

    def __init__(self) -> None:
        self.lp = None

    def connect(self) -> tuple[bool, str]:
        try:
            import launchpad_py as launchpad
        except Exception as exc:  # pragma: no cover
            return False, f"launchpad.py import failed: {exc}"
        candidates = ["LaunchpadX", "LaunchpadMiniMk3", "LaunchpadMk3", "Launchpad"]
        for cls_name in candidates:
            cls = getattr(launchpad, cls_name, None)
            if not cls:
                continue
            device = cls()
            if self._try_open(device):
                self.lp = device
                return True, f"Connected via {cls_name}"
        return False, "No compatible launchpad.py device opened"

    @staticmethod
    def _try_open(device: object) -> bool:
        open_fn = getattr(device, "Open", None)
        if not callable(open_fn):
            return False
        try:
            if open_fn():
                return True
        except TypeError:
            pass
        except Exception:
            return False
        try:
            if open_fn(0):
                return True
        except Exception:
            return False
        return False

    def send_pad(self, x: int, y: int, color: int) -> None:
        if not self.lp:
            return
        led_xy = getattr(self.lp, "LedCtrlXY", None)
        if callable(led_xy):
            led_xy(x + 1, GRID_SIZE - y, clamp_color(color))

    def send_frame(self, rows: list[list[int]]) -> None:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.send_pad(x, y, rows[y][x])

    def clear(self) -> None:
        if not self.lp:
            return
        reset = getattr(self.lp, "Reset", None)
        if callable(reset):
            reset()
            return
        self.send_frame([[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)])

    def close(self) -> None:
        if not self.lp:
            return
        close_fn = getattr(self.lp, "Close", None)
        if callable(close_fn):
            close_fn()
        self.lp = None


class DashboardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Launchpad Lightshow Dashboard")
        self.scene = Scene.blank()
        self.backend: Backend = DryRunBackend()
        self.palette_values = DEFAULT_PALETTE_VALUES.copy()
        self.semantic_colors = DEFAULT_SEMANTIC_COLORS.copy()
        self.selected_palette_index = tk.IntVar(value=3)
        self.probe_mode = tk.BooleanVar(value=False)
        self.auto_push = tk.BooleanVar(value=True)
        self.scene_name = tk.StringVar(value=self.scene.name)
        self.backend_choice = tk.StringVar(value="auto")
        self.status_text = tk.StringVar(value="Starting...")
        self.selected_semantic_key = tk.StringVar(value="")

        self.canvas_size = 420
        self.cell_size = self.canvas_size // GRID_SIZE
        self.rect_ids: list[list[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.palette_buttons: list[tk.Radiobutton] = []
        self.semantic_buttons: dict[str, tk.Button] = {}
        self.load_canonical_palette(startup=True)
        self.palette_values = arrange_palette_by_color(self.palette_values)

        self._build_ui()
        self.connect_backend("auto")
        self.redraw()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.grid(row=0, column=0, sticky="ew")
        self.root.columnconfigure(0, weight=1)

        ttk.Label(top, text="Backend").grid(row=0, column=0, sticky="w")
        backend_menu = ttk.Combobox(
            top, state="readonly", values=["auto", "launchpad.py", "mido", "dry-run"], width=16
        )
        backend_menu.set("auto")
        backend_menu.grid(row=0, column=1, padx=6)
        backend_menu.bind(
            "<<ComboboxSelected>>", lambda e: self.connect_backend(self.backend_choice_from_widget(backend_menu))
        )

        ttk.Button(top, text="Reconnect", command=lambda: self.connect_backend(backend_menu.get())).grid(
            row=0, column=2, padx=4
        )
        ttk.Checkbutton(top, text="Auto push", variable=self.auto_push).grid(row=0, column=3, padx=8)
        ttk.Button(top, text="Push frame", command=self.push_frame).grid(row=0, column=4, padx=4)
        ttk.Button(top, text="Clear", command=self.clear_scene).grid(row=0, column=5, padx=4)
        ttk.Button(top, text="Probe 0-63", command=lambda: self.load_probe_scene(0)).grid(row=0, column=6, padx=4)
        ttk.Button(top, text="Probe 64-127", command=lambda: self.load_probe_scene(64)).grid(row=0, column=7, padx=4)
        ttk.Button(top, text="Exit probe", command=self.disable_probe_mode).grid(row=0, column=8, padx=4)

        ttk.Label(top, text="Scene").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(top, textvariable=self.scene_name, width=24).grid(row=1, column=1, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(top, text="Save", command=self.save_scene).grid(row=1, column=3, pady=(8, 0))
        ttk.Button(top, text="Load", command=self.load_scene).grid(row=1, column=4, pady=(8, 0))
        ttk.Label(top, textvariable=self.status_text).grid(row=1, column=5, sticky="e", pady=(8, 0))

        content = ttk.Frame(self.root)
        content.grid(row=1, column=0, sticky="nsew")

        canvas_frame = ttk.Frame(content, padding=10)
        canvas_frame.grid(row=0, column=0, sticky="n")
        self.canvas = tk.Canvas(
            canvas_frame, width=self.canvas_size, height=self.canvas_size, bg="#111315", highlightthickness=0
        )
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self.on_canvas_paint)
        self.canvas.bind("<B1-Motion>", self.on_canvas_paint)

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                x0, y0 = x * self.cell_size, y * self.cell_size
                rect = self.canvas.create_rectangle(
                    x0 + 2,
                    y0 + 2,
                    x0 + self.cell_size - 2,
                    y0 + self.cell_size - 2,
                    fill=velocity_to_hex(0),
                    outline="#2c3135",
                    width=1,
                )
                self.rect_ids[y][x] = rect

        palette = ttk.Frame(content, padding=(10, 10, 10, 10))
        palette.grid(row=0, column=1, sticky="n")
        ttk.Label(palette, text="Palette Slots (0-127)").grid(row=0, column=0, sticky="w")

        swatch_frame = ttk.Frame(palette)
        swatch_frame.grid(row=1, column=0, sticky="w", pady=(4, 0))
        for idx, color in enumerate(self.palette_values):
            row = idx // PALETTE_COLUMNS
            col = idx % PALETTE_COLUMNS
            btn = tk.Radiobutton(
                swatch_frame,
                variable=self.selected_palette_index,
                value=idx,
                indicatoron=False,
                width=2,
                bg=velocity_to_hex(color),
                activebackground=velocity_to_hex(color),
                selectcolor=velocity_to_hex(color),
                relief=tk.RAISED,
                command=lambda i=idx: self.on_palette_select(i),
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
            self.palette_buttons.append(btn)

        palette_controls = ttk.Frame(palette)
        palette_controls.grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Button(palette_controls, text="Save Palette", command=self.save_palette).grid(row=0, column=0, padx=2)
        ttk.Button(palette_controls, text="Load Palette", command=self.load_palette).grid(row=0, column=1, padx=2)
        ttk.Button(palette_controls, text="Save Canonical", command=self.save_canonical_palette).grid(
            row=0, column=2, padx=2
        )
        ttk.Button(palette_controls, text="Load Canonical", command=self.load_canonical_palette).grid(
            row=0, column=3, padx=2
        )
        ttk.Button(palette_controls, text="Calibrate Colors", command=self.start_calibration).grid(
            row=0, column=4, padx=2
        )

        semantic_frame = ttk.Frame(palette)
        semantic_frame.grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Label(semantic_frame, text="Semantic Colors").grid(row=0, column=0, sticky="w")
        for idx, key in enumerate(self.semantic_colors.keys()):
            value = self.semantic_colors[key]
            btn = tk.Button(
                semantic_frame,
                text=f"{key} ({value})",
                width=11,
                relief=tk.RAISED,
                bg=velocity_to_hex(value),
                activebackground=velocity_to_hex(value),
                command=lambda name=key: self.select_semantic_color(name),
            )
            btn.grid(row=0, column=idx + 1, padx=2)
            self.semantic_buttons[key] = btn


    @staticmethod
    def backend_choice_from_widget(widget: ttk.Combobox) -> str:
        return widget.get().strip() or "auto"

    def connect_backend(self, requested: str) -> None:
        self.backend.close()
        requested = requested.strip().lower() if requested else "auto"
        self.backend_choice.set(requested)
        choices: list[Backend]
        if requested == "launchpad.py":
            choices = [LaunchpadPyBackend(), DryRunBackend()]
        elif requested == "mido":
            choices = [MidoBackend(), DryRunBackend()]
        elif requested == "dry-run":
            choices = [DryRunBackend()]
        else:
            choices = [LaunchpadPyBackend(), MidoBackend(), DryRunBackend()]

        for candidate in choices:
            ok, message = candidate.connect()
            if ok:
                self.backend = candidate
                self.status_text.set(f"{candidate.name}: {message}")
                self.push_frame()
                return
            self.status_text.set(f"{candidate.name}: {message}")

    def current_color(self) -> int:
        semantic_key = self.selected_semantic_key.get().strip().lower()
        if semantic_key and semantic_key in self.semantic_colors:
            return clamp_color(self.semantic_colors[semantic_key])
        idx = self.selected_palette_index.get()
        if idx < 0 or idx >= len(self.palette_values):
            idx = 0
            self.selected_palette_index.set(0)
        return self.palette_values[idx]

    def on_palette_select(self, idx: int) -> None:
        self.selected_semantic_key.set("")
        self.refresh_semantic_buttons()
        self.selected_palette_index.set(idx)
        self.status_text.set(f"Selected palette slot {idx + 1}: velocity {self.current_color()}")

    def set_palette_slot(self, idx: int, color: int) -> None:
        if idx < 0 or idx >= len(self.palette_values):
            return
        self.palette_values[idx] = clamp_color(color)
        self.refresh_palette_buttons()
        self.selected_palette_index.set(idx)

    def select_semantic_color(self, name: str) -> None:
        key = name.strip().lower()
        if key not in self.semantic_colors:
            return
        self.selected_semantic_key.set(key)
        self.refresh_semantic_buttons()
        self.status_text.set(f"Selected semantic color {key}: velocity {self.semantic_colors[key]}")

    def refresh_palette_buttons(self) -> None:
        for idx, btn in enumerate(self.palette_buttons):
            if idx >= len(self.palette_values):
                continue
            color_hex = velocity_to_hex(self.palette_values[idx])
            btn.configure(bg=color_hex, activebackground=color_hex, selectcolor=color_hex)

    def refresh_semantic_buttons(self) -> None:
        selected = self.selected_semantic_key.get().strip().lower()
        for key, btn in self.semantic_buttons.items():
            value = clamp_color(self.semantic_colors.get(key, 0))
            btn.configure(
                text=f"{key} ({value})",
                bg=velocity_to_hex(value),
                activebackground=velocity_to_hex(value),
                relief=tk.SUNKEN if key == selected else tk.RAISED,
                bd=3 if key == selected else 1,
            )

    def canonical_palette_data(self) -> dict:
        return {
            "version": 1,
            "device": "launchpad-x",
            "slots": [clamp_color(value) for value in self.palette_values],
            "semantic": {key: clamp_color(value) for key, value in self.semantic_colors.items()},
        }

    def redraw(self) -> None:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.canvas.itemconfig(self.rect_ids[y][x], fill=velocity_to_hex(self.scene.rows[y][x]))

    def on_canvas_paint(self, event: tk.Event) -> None:
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return
        if self.probe_mode.get():
            picked = self.scene.rows[y][x]
            slot = self.selected_palette_index.get()
            self.set_palette_slot(slot, picked)
            self.status_text.set(f"Probe picked velocity {picked} into slot {slot + 1}")
            return
        color = self.current_color()
        if self.scene.rows[y][x] == color:
            return
        self.scene.rows[y][x] = color
        self.canvas.itemconfig(self.rect_ids[y][x], fill=velocity_to_hex(color))
        if self.auto_push.get():
            self.backend.send_pad(x, y, color)

    def push_frame(self) -> None:
        self.backend.send_frame(self.scene.rows)

    def clear_scene(self) -> None:
        self.probe_mode.set(False)
        self.scene.rows = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.redraw()
        self.backend.clear()

    def disable_probe_mode(self) -> None:
        self.probe_mode.set(False)
        self.status_text.set("Probe mode disabled")

    def load_probe_scene(self, start: int) -> None:
        start = clamp_color(start)
        rows: list[list[int]] = []
        for y in range(GRID_SIZE):
            row: list[int] = []
            for x in range(GRID_SIZE):
                row.append(clamp_color(start + y * GRID_SIZE + x))
            rows.append(row)
        end = rows[-1][-1]
        self.scene = Scene(name=f"Probe {start}-{end}", rows=rows)
        self.scene_name.set(self.scene.name)
        self.probe_mode.set(True)
        self.redraw()
        self.push_frame()
        self.status_text.set(
            f"Probe mode active ({start}-{end}). Click a probe cell to copy its velocity into selected palette slot."
        )

    def save_palette(self) -> None:
        target = filedialog.asksaveasfilename(
            title="Save Palette",
            defaultextension=".json",
            initialfile="palette.json",
            filetypes=[("JSON files", "*.json")],
        )
        if not target:
            return
        data = {"colors": [clamp_color(value) for value in self.palette_values]}
        Path(target).write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.status_text.set(f"Saved palette: {target}")

    def load_palette(self) -> None:
        source = filedialog.askopenfilename(title="Load Palette", filetypes=[("JSON files", "*.json")])
        if not source:
            return
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            colors = data.get("colors", data.get("slots"))
            if not isinstance(colors, list) or not colors:
                raise ValueError("Palette must include a non-empty colors/slots list")
            expected = len(self.palette_buttons) if self.palette_buttons else len(self.palette_values)
            if len(colors) != expected:
                raise ValueError(f"Palette must contain exactly {expected} colors")
            self.palette_values = [clamp_color(value) for value in colors]
            self.palette_values = arrange_palette_by_color(self.palette_values)
            semantic = data.get("semantic")
            if isinstance(semantic, dict):
                self.semantic_colors = {
                    str(key): clamp_color(value)
                    for key, value in semantic.items()
                    if isinstance(key, str) and isinstance(value, int)
                } or self.semantic_colors
            self.refresh_palette_buttons()
            self.refresh_semantic_buttons()
            if self.selected_palette_index.get() >= len(self.palette_values):
                self.selected_palette_index.set(0)
            self.status_text.set(f"Loaded palette: {source}")
        except Exception as exc:
            messagebox.showerror("Invalid palette", str(exc))

    def save_canonical_palette(self) -> None:
        CANONICAL_PALETTE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CANONICAL_PALETTE_PATH.write_text(
            json.dumps(self.canonical_palette_data(), indent=2), encoding="utf-8"
        )
        self.status_text.set(f"Saved canonical palette: {CANONICAL_PALETTE_PATH}")

    def start_calibration(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Calibrate Velocity Colors")
        win.resizable(False, False)

        current_vel = tk.IntVar(value=0)
        colors = list(VELOCITY_HEX)  # working copy

        # --- Progress label ---
        progress_label = ttk.Label(win, text="Velocity 0 / 127", font=("TkDefaultFont", 12))
        progress_label.grid(row=0, column=0, columnspan=3, pady=(12, 4))

        # --- Color swatch ---
        swatch_canvas = tk.Canvas(win, width=120, height=120, highlightthickness=1, highlightbackground="#888")
        swatch_canvas.grid(row=1, column=0, columnspan=3, pady=8)
        swatch_rect = swatch_canvas.create_rectangle(0, 0, 120, 120, fill=colors[0], outline="")

        def update_display() -> None:
            v = current_vel.get()
            progress_label.config(text=f"Velocity {v} / 127")
            swatch_canvas.itemconfig(swatch_rect, fill=colors[v])

        def push_velocity_to_hardware(v: int) -> None:
            rows = [[v for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            self.backend.send_frame(rows)

        def on_pick() -> None:
            v = current_vel.get()
            result = colorchooser.askcolor(color=colors[v], title=f"Pick color for velocity {v}")
            if result and result[1]:
                colors[v] = result[1]
                update_display()

        def on_prev() -> None:
            v = current_vel.get()
            if v > 0:
                current_vel.set(v - 1)
                update_display()
                push_velocity_to_hardware(v - 1)

        def on_next() -> None:
            v = current_vel.get()
            if v < 127:
                current_vel.set(v + 1)
                update_display()
                push_velocity_to_hardware(v + 1)

        def on_save() -> None:
            for i, hex_val in enumerate(colors):
                VELOCITY_HEX[i] = hex_val
            CALIBRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {"version": 1, "colors": colors}
            CALIBRATION_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self.refresh_palette_buttons()
            self.redraw()
            self.status_text.set(f"Saved velocity calibration: {CALIBRATION_PATH}")
            win.destroy()

        # --- Buttons ---
        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=4)
        ttk.Button(btn_frame, text="Pick Color", command=on_pick).grid(row=0, column=0, padx=4)

        nav_frame = ttk.Frame(win)
        nav_frame.grid(row=3, column=0, columnspan=3, pady=4)
        ttk.Button(nav_frame, text="Prev", command=on_prev).grid(row=0, column=0, padx=4)
        ttk.Button(nav_frame, text="Next", command=on_next).grid(row=0, column=1, padx=4)

        ttk.Button(win, text="Save & Close", command=on_save).grid(row=4, column=0, columnspan=3, pady=(4, 12))

        # Show velocity 0 on hardware immediately.
        push_velocity_to_hardware(0)

    def load_canonical_palette(self, startup: bool = False) -> bool:
        if not CANONICAL_PALETTE_PATH.exists():
            if not startup:
                self.status_text.set(f"No canonical palette found at {CANONICAL_PALETTE_PATH}")
            return False
        try:
            data = json.loads(CANONICAL_PALETTE_PATH.read_text(encoding="utf-8"))
            slots = data.get("slots")
            if not isinstance(slots, list) or not slots:
                raise ValueError("Canonical palette requires a non-empty slots list")
            expected = len(self.palette_buttons) if self.palette_buttons else len(self.palette_values)
            if len(slots) != expected:
                raise ValueError(f"Canonical palette must contain exactly {expected} slots")
            self.palette_values = [clamp_color(value) for value in slots]
            self.palette_values = arrange_palette_by_color(self.palette_values)
            semantic = data.get("semantic")
            if isinstance(semantic, dict):
                self.semantic_colors = {
                    str(key): clamp_color(value)
                    for key, value in semantic.items()
                    if isinstance(key, str) and isinstance(value, int)
                } or DEFAULT_SEMANTIC_COLORS.copy()
            if self.palette_buttons:
                self.refresh_palette_buttons()
            if self.semantic_buttons:
                self.refresh_semantic_buttons()
            if self.selected_palette_index.get() >= len(self.palette_values):
                self.selected_palette_index.set(0)
            if not startup:
                self.status_text.set(f"Loaded canonical palette: {CANONICAL_PALETTE_PATH}")
            return True
        except Exception as exc:
            if not startup:
                messagebox.showerror("Invalid canonical palette", str(exc))
            return False

    def save_scene(self) -> None:
        self.scene.name = self.scene_name.get().strip() or DEFAULT_SCENE_NAME
        target = filedialog.asksaveasfilename(
            title="Save Scene",
            defaultextension=".json",
            initialfile=f"{self.scene.name.replace(' ', '_').lower()}.json",
            filetypes=[("JSON files", "*.json")],
        )
        if not target:
            return
        Path(target).write_text(json.dumps(self.scene.to_json(), indent=2), encoding="utf-8")
        self.status_text.set(f"Saved: {target}")

    def load_scene(self) -> None:
        source = filedialog.askopenfilename(title="Load Scene", filetypes=[("JSON files", "*.json")])
        if not source:
            return
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            self.scene = Scene.from_json(data)
            self.scene_name.set(self.scene.name)
            self.probe_mode.set(False)
            self.redraw()
            self.push_frame()
            self.status_text.set(f"Loaded: {source}")
        except Exception as exc:
            messagebox.showerror("Invalid scene", str(exc))


def main() -> None:
    root = tk.Tk()
    app = DashboardApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.backend.close(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
