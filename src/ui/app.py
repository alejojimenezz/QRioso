import io
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from src.generator.config import (
    APP_COLOR_THEME,
    APP_APPEARANCE,
    APP_HEIGHT,
    APP_NAME,
    APP_WIDTH,
    DEFAULT_OUTPUT_DIR,
)
from src.generator.qr_engine import QRGenerator
from src.ui.settings import SettingsPanel


ctk.set_appearance_mode(APP_APPEARANCE)
ctk.set_default_color_theme(APP_COLOR_THEME)


class QRiosoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        self._output_dir = DEFAULT_OUTPUT_DIR
        self._preview_job = None

        self._build_layout()
        self._schedule_preview()

    # Layout

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left panel: Settings
        self.settings = SettingsPanel(
            self,
            on_change=self._schedule_preview,
        )
        self.settings.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        # Right panel: preview + output
        self._build_preview_panel()

    def _build_preview_panel(self):
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Image container
        self._preview_frame = ctk.CTkFrame(panel, corner_radius=12)
        self._preview_frame.grid(row=0, column=0, sticky="nsew")
        self._preview_frame.grid_rowconfigure(0, weight=1)
        self._preview_frame.grid_columnconfigure(0, weight=1)

        self._preview_label = ctk.CTkLabel(
            self._preview_frame,
            text="",
            image=None,
        )
        self._preview_label.grid(row=0, column=0, padx=16, pady=16)

        self._status_label = ctk.CTkLabel(
            self._preview_frame,
            text="Vista previa",
            text_color=("gray50", "gray60"),
            font=ctk.CTkFont(size=11),
        )
        self._status_label.grid(row=1, column=0, pady=(0, 6))

        # Output path
        path_frame = ctk.CTkFrame(panel, fg_color="transparent")
        path_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        path_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            path_frame,
            text="Guardar en",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self._path_entry = ctk.CTkEntry(
            path_frame,
            font=ctk.CTkFont(size=11),
            height=30,
        )
        self._path_entry.insert(0, str(self._output_dir))
        self._path_entry.configure(state="disabled")
        self._path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            path_frame,
            text="Examinar...",
            width=70,
            height=30,
            font=ctk.CTkFont(size=11),
            command=self._choose_directory,
        ).grid(row=1, column=1)

        # Action buttons
        ctk.CTkButton(
            panel,
            text="Guardar QR",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._generate_and_save,
        ).grid(row=2, column=0, sticky="ew", pady=(10, 4))

        ctk.CTkButton(
            panel,
            text="Abrir carpeta",
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            text_color=("gray30", "gray70"),
            command=self._open_output_folder,
        ).grid(row=3, column=0, sticky="ew")

    # Real-time preview

    def _schedule_preview(self, *_):
        if self._preview_job:
            self.after_cancel(self._preview_job)
        self._preview_job = self.after(400, self._render_preview)

    def _render_preview(self):
        params = self.settings.get_params()
        try:
            gen = QRGenerator(
                box_size=params["box_size"],
                border=params["border"],
                dot_style=params["dot_style"],
                error_correction=params["error_correction"],
                fill_color=params["fill_color"],
                back_color=params["back_color"],
            )
            # img = gen._build_qr(params["data"]).make_image(
            #     fill_color=params["fill_color"],
            #     back_color=params["back_color"],
            # ).get_image()
            img = gen.build_pil_image(params["data"]).get_image()

            img.thumbnail((200, 200), Image.LANCZOS)

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
            self._preview_label.configure(image=ctk_img, text="")
            self._status_label.configure(
                text="Vista previa",
                text_color=("gray50", "gray60"),
            )
        except Exception as e:
            self._preview_label.configure(image=None, text="—")
            self._status_label.configure(
                text=str(e),
                text_color=("red", "#FF6B6B"),
            )

    # Actions
    def _generate_and_save(self):
        params = self.settings.get_params()
        fmt = params["fmt"]

        # File name
        safe_name = self._safe_filename(params["data"])
        output_path = self._output_dir / f"{safe_name}.{fmt}"

        try:
            gen = QRGenerator(
                box_size=params["box_size"],
                border=params["border"],
                dot_style=params["dot_style"],
                error_correction=params["error_correction"],
                fill_color=params["fill_color"],
                back_color=params["back_color"],
            )
            saved = gen.generate(params["data"], output_path)
            messagebox.showinfo(
                "QR generado",
                f"Archivo guardado en:\n{saved}",
            )
        except Exception as e:
            messagebox.showerror("Error al generar", str(e))

    def _choose_directory(self):
        chosen = filedialog.askdirectory(
            initialdir=self._output_dir,
            title="Elegir carpeta para guardar QR",
        )
        if chosen:
            self._output_dir = Path(chosen)
            self._path_entry.configure(state="normal")
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, str(self._output_dir))
            self._path_entry.configure(state="disabled")

    def _open_output_folder(self):
        import subprocess, sys
        self._output_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(self._output_dir)])
        else:
            subprocess.Popen(["xdg-open", str(self._output_dir)])

    # Utilities
    @staticmethod
    def _safe_filename(data: str, max_len: int = 40) -> str:
        name = data.replace("https://", "").replace("http://", "")
        for ch in r'\/:*?"<>|. ':
            name = name.replace(ch, "_")
        return name[:max_len] or "qr_code"