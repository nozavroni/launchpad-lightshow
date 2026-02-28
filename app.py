from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Protocol


GRID_SIZE = 8
DEFAULT_SCENE_NAME = "Untitled"


def clamp_color(value: int) -> int:
    return max(0, min(127, int(value)))


def velocity_to_hex(velocity: int) -> str:
    # Fast visual approximation for editor buttons.
    v = clamp_color(velocity)
    if v == 0:
        return "#0f1214"
    hue_bucket = v % 6
    sat = 180 + (v // 6) % 76
    val = 120 + (v // 2) % 136
    channels = [0, 0, 0]
    channels[hue_bucket % 3] = val
    channels[(hue_bucket + 1) % 3] = sat
    channels[(hue_bucket + 2) % 3] = 40 + (v % 40)
    return "#{:02x}{:02x}{:02x}".format(*channels)


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
        self.selected_color = tk.IntVar(value=21)
        self.auto_push = tk.BooleanVar(value=True)
        self.scene_name = tk.StringVar(value=self.scene.name)
        self.backend_choice = tk.StringVar(value="auto")
        self.status_text = tk.StringVar(value="Starting...")

        self.canvas_size = 420
        self.cell_size = self.canvas_size // GRID_SIZE
        self.rect_ids: list[list[int]] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

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

        ttk.Label(top, text="Scene").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(top, textvariable=self.scene_name, width=24).grid(row=1, column=1, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(top, text="Save", command=self.save_scene).grid(row=1, column=3, pady=(8, 0))
        ttk.Button(top, text="Load", command=self.load_scene).grid(row=1, column=4, pady=(8, 0))
        ttk.Label(top, textvariable=self.status_text).grid(row=1, column=5, sticky="e", pady=(8, 0))

        palette = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        palette.grid(row=1, column=0, sticky="ew")
        ttk.Label(palette, text="Palette").grid(row=0, column=0, sticky="w")

        color_values = [0, 5, 13, 21, 29, 37, 45, 53, 61, 69, 77, 85, 93, 101, 109, 127]
        for idx, color in enumerate(color_values):
            btn = tk.Radiobutton(
                palette,
                variable=self.selected_color,
                value=color,
                indicatoron=False,
                width=3,
                bg=velocity_to_hex(color),
                activebackground=velocity_to_hex(color),
                selectcolor=velocity_to_hex(color),
                relief=tk.RAISED,
            )
            btn.grid(row=0, column=idx + 1, padx=1)

        canvas_frame = ttk.Frame(self.root, padding=10)
        canvas_frame.grid(row=2, column=0)
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

    def redraw(self) -> None:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.canvas.itemconfig(self.rect_ids[y][x], fill=velocity_to_hex(self.scene.rows[y][x]))

    def on_canvas_paint(self, event: tk.Event) -> None:
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return
        color = self.selected_color.get()
        if self.scene.rows[y][x] == color:
            return
        self.scene.rows[y][x] = color
        self.canvas.itemconfig(self.rect_ids[y][x], fill=velocity_to_hex(color))
        if self.auto_push.get():
            self.backend.send_pad(x, y, color)

    def push_frame(self) -> None:
        self.backend.send_frame(self.scene.rows)

    def clear_scene(self) -> None:
        self.scene.rows = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.redraw()
        self.backend.clear()

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
