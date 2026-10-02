from tkinter import colorchooser
from typing import Callable

import customtkinter as ctk

from src.generator.config import (
    BORDER_MAX,
    BORDER_MIN,
    BOX_SIZE_MAX,
    BOX_SIZE_MIN,
    DEFAULT_BACK_COLOR,
    DEFAULT_BORDER,
    DEFAULT_BOX_SIZE,
    DEFAULT_DOT_STYLE,
    DEFAULT_ERROR_CORRECTION,
    DEFAULT_FILL_COLOR,
    DEFAULT_FORMAT,
)

from src.generator.qr_engine import DOT_STYLES

class SettingsPanel(ctk.CTkFrame):

    def __init__(self, parent, on_change: Callable):
        super().__init__(parent, fg_color="transparent")
        self._on_change = on_change

        # Current state variables
        self._data_var   = ctk.StringVar(value="https://www.example.com")
        self._fmt_var    = ctk.StringVar(value=DEFAULT_FORMAT)
        self._box_var    = ctk.IntVar(value=DEFAULT_BOX_SIZE)
        self._border_var = ctk.IntVar(value=DEFAULT_BORDER)
        self._dot_var    = ctk.StringVar(value=DEFAULT_DOT_STYLE)
        self._ec_var     = ctk.StringVar(value=DEFAULT_ERROR_CORRECTION)
        self._fill_color = DEFAULT_FILL_COLOR
        self._back_color = DEFAULT_BACK_COLOR

        # Track text changes
        self._data_var.trace_add("write", self._on_change)

        self._build()

    # Panel build
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        row = 0

        # Section title
        row = self._section_label("Contenido", row)

        # URL field
        ctk.CTkEntry(
            self,
            textvariable=self._data_var,
            placeholder_text="URL o texto a codificar",
            height=36,
        ).grid(row=row, column=0, sticky="ew", pady=(0, 12))
        row += 1

        row = self._divider(row)

        # Output format
        row = self._section_label("Formato de salida", row)
        row = self._segmented("fmt", ["PNG", "SVG"], self._fmt_var, row)

        row = self._divider(row)

        # Module size
        row = self._section_label("Tamaño de módulo", row)
        row = self._slider(
            var=self._box_var,
            from_=BOX_SIZE_MIN,
            to=BOX_SIZE_MAX,
            unit=" px",
            row=row,
        )

        # Margin
        row = self._section_label("Margen", row)
        row = self._slider(
            var=self._border_var,
            from_=BORDER_MIN,
            to=BORDER_MAX,
            unit="",
            row=row,
        )

        # Estilo de puntos
        row = self._section_label("Estilo de puntos", row)
        ctk.CTkOptionMenu(
            self,
            values=DOT_STYLES,
            variable=self._dot_var,
            command=lambda _:self._on_change(),
        ).grid(row=row, column=0, sticky="ew", pady=(0,10))
        row += 1

        # Error correction
        row = self._section_label("Corrección de error", row)
        row = self._segmented("ec", ["L ~7%", "M ~15%", "Q ~25%", "H ~30%"], self._ec_var, row)

        row = self._divider(row)

        # Colors
        row = self._section_label("Colores", row)
        row = self._color_pickers(row)

    # Reusable widgets

    def _section_label(self, text: str, row: int) -> int:
        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=(0, 4))
        return row + 1

    def _divider(self, row: int) -> int:
        ctk.CTkFrame(self, height=1, fg_color=("gray85", "gray25")).grid(
            row=row, column=0, sticky="ew", pady=8
        )
        return row + 1

    def _segmented(self, key: str, values: list, var: ctk.StringVar, row: int) -> int:
        """Botones segmentados que actúan como selector exclusivo."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        for i in range(len(values)):
            frame.grid_columnconfigure(i, weight=1)

        def make_handler(v):
            def handler():
                var.set(v.lower() if key == "fmt" else v)
                self._refresh_segmented(frame, values, var, key)
                self._on_change()
            return handler

        for i, val in enumerate(values):
            current = var.get().upper() if key == "fmt" else var.get()
            is_active = current == val
            btn = ctk.CTkButton(
                frame,
                text=val,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color=("gray75", "gray30") if not is_active else None,
                text_color=("gray20", "gray90") if not is_active else None,
                command=make_handler(val),
            )
            btn.grid(row=0, column=i, sticky="ew", padx=(0, 4) if i < len(values)-1 else 0)
        return row + 1

    def _refresh_segmented(self, frame, values, var, key):
        for i, widget in enumerate(frame.winfo_children()):
            val = values[i]
            current = var.get().upper() if key == "fmt" else var.get()
            is_active = current == val
            widget.configure(
                fg_color=("gray75", "gray30") if not is_active else ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                text_color=("gray20", "gray90") if not is_active else ctk.ThemeManager.theme["CTkButton"]["text_color"],
            )

    def _slider(self, var: ctk.IntVar, from_: int, to: int, unit: str, row: int) -> int:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)

        val_label = ctk.CTkLabel(
            frame,
            text=f"{var.get()}{unit}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=40,
            anchor="e",
        )
        val_label.grid(row=0, column=1, padx=(8, 0))

        def on_slide(v):
            val_label.configure(text=f"{int(float(v))}{unit}")
            var.set(int(float(v)))
            self._on_change()

        ctk.CTkSlider(
            frame,
            from_=from_,
            to=to,
            number_of_steps=to - from_,
            variable=var,
            command=on_slide,
        ).grid(row=0, column=0, sticky="ew")

        return row + 1

    def _color_pickers(self, row: int) -> int:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # Swatch + modules label
        self._fill_swatch = ctk.CTkButton(
            frame,
            text="",
            width=28,
            height=28,
            corner_radius=6,
            fg_color=self._fill_color,
            hover_color=self._fill_color,
            command=self._pick_fill,
        )
        self._fill_swatch.grid(row=0, column=0, padx=(0, 6))
        ctk.CTkLabel(
            frame,
            text="Módulos",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        # Swatch + background label
        self._back_swatch = ctk.CTkButton(
            frame,
            text="",
            width=28,
            height=28,
            corner_radius=6,
            fg_color=self._back_color,
            hover_color=self._back_color,
            border_width=1,
            command=self._pick_back,
        )
        self._back_swatch.grid(row=0, column=2, padx=(12, 6))
        ctk.CTkLabel(
            frame,
            text="Fondo",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w",
        ).grid(row=0, column=3, sticky="w")

        return row + 1

    # Color picker

    def _pick_fill(self):
        color = colorchooser.askcolor(
            color=self._fill_color,
            title="Color de módulos",
        )
        if color[1]:
            self._fill_color = color[1]
            self._fill_swatch.configure(fg_color=color[1], hover_color=color[1])
            self._on_change()

    def _pick_back(self):
        color = colorchooser.askcolor(
            color=self._back_color,
            title="Color de fondo",
        )
        if color[1]:
            self._back_color = color[1]
            self._back_swatch.configure(fg_color=color[1], hover_color=color[1])
            self._on_change()

    # Public API

    def get_params(self) -> dict:
        return {
            "data":             self._data_var.get(),
            "fmt":              self._fmt_var.get(),
            "box_size":         self._box_var.get(),
            "border":           self._border_var.get(),
            "dot_style":        self._dot_var.get(),
            "error_correction": self._ec_var.get(),
            "fill_color":       self._fill_color,
            "back_color":       self._back_color,
        }