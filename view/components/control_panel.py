"""Panel de control superior (Zona Norte) para la gestión de la búsqueda."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from core.types import AlgorithmType, ExecutionMode, VisualTheme


class ControlPanel(ttk.Frame):
    """
    Componente visual reutilizable para los controles de ejecución y configuración.
    """

    def __init__(
        self,
        master: tk.Misc,
        theme: VisualTheme = VisualTheme(),
        on_toggle_algo: Optional[Callable[[AlgorithmType, bool], None]] = None,
        on_start_pause: Optional[Callable[[], None]] = None,
        on_skip: Optional[Callable[[], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        on_next_step: Optional[Callable[[], None]] = None,
        on_speed_change: Optional[Callable[[int], None]] = None,
        on_clear_obstacles: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, padding=(10, 8), **kwargs)
        self._theme = theme

        # Callbacks
        self._on_toggle_algo = on_toggle_algo
        self._on_start_pause = on_start_pause
        self._on_skip = on_skip
        self._on_reset = on_reset
        self._on_next_step = on_next_step
        self._on_speed_change = on_speed_change
        self._on_clear_obstacles = on_clear_obstacles

        # Variables de control
        self._bfs_var = tk.BooleanVar(value=True)
        self._astar_var = tk.BooleanVar(value=True)
        self._speed_var = tk.IntVar(value=50)

        self._build_ui()

    def _build_ui(self) -> None:
        # Contenedor principal con distribución horizontal fluida
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # ---- SECCIÓN 1: Selección de Algoritmos (Checkboxes + Muestra de Color) ----
        algo_frame = ttk.LabelFrame(self, text=" Algoritmos a Ejecutar ", padding=(8, 4))
        algo_frame.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")

        # BFS Checkbox + Muestra de color
        bfs_box = ttk.Frame(algo_frame)
        bfs_box.pack(anchor="w", pady=2)

        self._bfs_color_sample = tk.Label(
            bfs_box,
            text="  ",
            bg=self._theme.bfs_explored,
            relief="solid",
            borderwidth=1,
            width=2,
            height=1,
        )
        self._bfs_color_sample.pack(side="left", padx=(0, 6))

        self._bfs_check = ttk.Checkbutton(
            bfs_box,
            text="BFS (Búsqueda en Anchura)",
            variable=self._bfs_var,
            command=self._handle_bfs_toggle,
        )
        self._bfs_check.pack(side="left")

        # A* Checkbox + Muestra de color
        astar_box = ttk.Frame(algo_frame)
        astar_box.pack(anchor="w", pady=2)

        self._astar_color_sample = tk.Label(
            astar_box,
            text="  ",
            bg=self._theme.astar_explored,
            relief="solid",
            borderwidth=1,
            width=2,
            height=1,
        )
        self._astar_color_sample.pack(side="left", padx=(0, 6))

        self._astar_check = ttk.Checkbutton(
            astar_box,
            text="A* (A-Estrella)",
            variable=self._astar_var,
            command=self._handle_astar_toggle,
        )
        self._astar_check.pack(side="left")

        # Leyenda de intersección
        overlap_box = ttk.Frame(algo_frame)
        overlap_box.pack(anchor="w", pady=2)
        tk.Label(
            overlap_box,
            text="  ",
            bg=self._theme.overlap_explored,
            relief="solid",
            borderwidth=1,
            width=2,
            height=1,
        ).pack(side="left", padx=(0, 6))
        ttk.Label(overlap_box, text="Explorados por ambos", font=("TkDefaultFont", 8, "italic")).pack(side="left")

        # ---- SECCIÓN 2: Acciones Principales (Iniciar/Pausa, Omitir, Reiniciar) ----
        action_frame = ttk.LabelFrame(self, text=" Control de Ejecución ", padding=(8, 4))
        action_frame.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")

        btn_row = ttk.Frame(action_frame)
        btn_row.pack(fill="x", expand=True, pady=4)

        self._btn_start_pause = ttk.Button(
            btn_row,
            text="▶ Iniciar",
            command=self._handle_start_pause,
            width=10,
        )
        self._btn_start_pause.pack(side="left", padx=3)

        self._btn_skip = ttk.Button(
            btn_row,
            text="⏭ Omitir",
            command=self._handle_skip,
            width=9,
        )
        self._btn_skip.pack(side="left", padx=3)

        self._btn_reset = ttk.Button(
            btn_row,
            text="↺ Reiniciar",
            command=self._handle_reset,
            width=10,
        )
        self._btn_reset.pack(side="left", padx=3)

        if self._on_clear_obstacles:
            self._btn_clear_map = ttk.Button(
                action_frame,
                text="🧹 Limpiar Obstáculos",
                command=self._on_clear_obstacles,
            )
            self._btn_clear_map.pack(fill="x", padx=3, pady=(2, 0))

        # ---- SECCIÓN 3: Velocidad y Control Manual Paso a Paso ----
        speed_frame = ttk.LabelFrame(self, text=" Velocidad y Paso Manual ", padding=(8, 4))
        speed_frame.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")

        slider_box = ttk.Frame(speed_frame)
        slider_box.pack(fill="x", pady=2)

        ttk.Label(slider_box, text="Rápido").pack(side="left", padx=2)
        # Invertimos visualmente para que la izquierda sea rápido (10ms) y derecha lento (300ms)
        self._speed_slider = ttk.Scale(
            slider_box,
            from_=10,
            to=300,
            orient="horizontal",
            variable=self._speed_var,
            command=self._handle_speed_slider,
        )
        self._speed_slider.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Label(slider_box, text="Lento").pack(side="right", padx=2)

        self._btn_next = ttk.Button(
            speed_frame,
            text="⏭ Siguiente Paso",
            command=self._handle_next_step,
        )
        self._btn_next.pack(fill="x", padx=3, pady=(4, 0))

    # ---- Manejadores de Eventos ----

    def _handle_bfs_toggle(self) -> None:
        if self._on_toggle_algo:
            self._on_toggle_algo(AlgorithmType.BFS, self._bfs_var.get())

    def _handle_astar_toggle(self) -> None:
        if self._on_toggle_algo:
            self._on_toggle_algo(AlgorithmType.ASTAR, self._astar_var.get())

    def _handle_start_pause(self) -> None:
        if self._on_start_pause:
            self._on_start_pause()

    def _handle_skip(self) -> None:
        if self._on_skip:
            self._on_skip()

    def _handle_reset(self) -> None:
        if self._on_reset:
            self._on_reset()

    def _handle_next_step(self) -> None:
        if self._on_next_step:
            self._on_next_step()

    def _handle_speed_slider(self, val_str: str) -> None:
        delay = int(float(val_str))
        if self._on_speed_change:
            self._on_speed_change(delay)

    # ---- Métodos de Estado para el Controlador ----

    def update_execution_state(self, mode: ExecutionMode) -> None:
        """Actualiza el texto y habilitación de controles según el modo."""
        if mode == ExecutionMode.RUNNING:
            self._btn_start_pause.config(text="⏸ Pausar", state="normal")
            self._btn_next.config(text="⏸ Siguiente (Pausa)")
            self._bfs_check.config(state="disabled")
            self._astar_check.config(state="disabled")
            self._btn_skip.config(state="normal")
            self._btn_reset.config(state="normal")

        elif mode == ExecutionMode.PAUSED:
            self._btn_start_pause.config(text="▶ Reanudar", state="normal")
            self._btn_next.config(text="⏭ Siguiente Paso", state="normal")
            self._bfs_check.config(state="disabled")
            self._astar_check.config(state="disabled")
            self._btn_skip.config(state="normal")
            self._btn_reset.config(state="normal")

        elif mode == ExecutionMode.IDLE:
            self._btn_start_pause.config(text="▶ Iniciar", state="normal")
            self._btn_next.config(text="⏭ Siguiente Paso", state="normal")
            self._bfs_check.config(state="normal")
            self._astar_check.config(state="normal")
            self._btn_skip.config(state="normal")
            self._btn_reset.config(state="normal")

        elif mode == ExecutionMode.FINISHED:
            self._btn_start_pause.config(text="↺ Reiniciar", state="normal")
            self._btn_next.config(text="⏭ Siguiente Paso", state="disabled")
            self._bfs_check.config(state="normal")
            self._astar_check.config(state="normal")
            self._btn_skip.config(state="disabled")
            self._btn_reset.config(state="normal")
