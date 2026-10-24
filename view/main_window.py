"""Ventana principal que integra Modelo, Vista y Controlador (MVC)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from controller.search_controller import SearchController
from core.grid import GridMap
from core.types import AlgorithmMetrics, AlgorithmType, ExecutionMode, StepResult, VisualTheme
from view.components.control_panel import ControlPanel
from view.components.grid_canvas import GridCanvas
from view.components.stats_panel import StatsPanel


class MainWindow(tk.Tk):
    """
    Ventana principal de la aplicación.
    Estructura la vista y orquesta la comunicación con el controlador.
    """

    def __init__(
        self,
        grid: Optional[GridMap] = None,
        controller: Optional[SearchController] = None,
        theme: VisualTheme = VisualTheme(),
    ) -> None:
        super().__init__()
        self.title("Comparador de Búsquedas en Cuadrícula: BFS vs A*")
        self.geometry("980x740")
        self.minsize(750, 550)

        self._theme = theme
        self._grid = grid if grid is not None else GridMap(rows=22, cols=32)
        self._controller = controller if controller is not None else SearchController(self._grid)

        # Inyectar mecanismo de temporizador de Tkinter en el controlador
        self._controller.set_scheduler(self.after, self.after_cancel)

        self._build_layout()
        self._bind_controller_events()

    def _build_layout(self) -> None:
        """Construye y empaqueta los componentes de la interfaz de usuario."""
        # 1. Zona Norte: Panel de Control
        self._control_panel = ControlPanel(
            self,
            theme=self._theme,
            on_toggle_algo=self._controller.set_algorithm_enabled,
            on_start_pause=self._controller.toggle_start_pause,
            on_skip=self._controller.skip,
            on_reset=self._controller.reset,
            on_next_step=self._controller.manual_step,
            on_speed_change=self._handle_speed_change,
            on_clear_obstacles=self._handle_clear_obstacles,
        )
        self._control_panel.pack(side="top", fill="x", padx=6, pady=(4, 0))

        # Separador visual
        ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=4)

        # 2. Zona Central: Mapa / Canvas responsivo
        self._canvas_container = ttk.Frame(self)
        self._canvas_container.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        self._grid_canvas = GridCanvas(
            self._canvas_container,
            grid=self._grid,
            theme=self._theme,
        )
        self._grid_canvas.pack(fill="both", expand=True)

        # 3. Zona Sur: Panel de Métricas y Estadísticas
        self._stats_panel = StatsPanel(self, theme=self._theme)
        self._stats_panel.pack(side="bottom", fill="x", padx=6, pady=(0, 4))

        # Barra de ayuda rápida en el pie de página
        help_bar = ttk.Frame(self, padding=(8, 2))
        help_bar.pack(side="bottom", fill="x")
        ttk.Label(
            help_bar,
            text="💡 Tip: Haz clic o arrastra el cursor en el mapa para colocar/quitar obstáculos. Clic derecho para borrar.",
            font=("TkDefaultFont", 8),
            foreground="#6C757D",
        ).pack(side="left")

    def _bind_controller_events(self) -> None:
        """Conecta los eventos del controlador con la actualización visual."""
        self._controller.on_state_change = self._on_state_change
        self._controller.on_step_update = self._on_step_update
        self._controller.on_metrics_update = self._on_metrics_update
        self._controller.on_reset_view = self._on_reset_view

    # ---- Callbacks del Controlador ----

    def _on_state_change(self, mode: ExecutionMode) -> None:
        self._control_panel.update_execution_state(mode)
        # Solo permitir editar obstáculos cuando no esté corriendo activamente
        self._grid_canvas.is_editable = (mode in (ExecutionMode.IDLE, ExecutionMode.PAUSED, ExecutionMode.FINISHED))

    def _on_step_update(
        self,
        bfs_step: Optional[StepResult],
        astar_step: Optional[StepResult],
    ) -> None:
        bfs_exp = set()
        astar_exp = set()
        bfs_path = []
        astar_path = []

        if self._controller.is_bfs_enabled and self._controller._bfs_algo:
            bfs_exp = self._controller._bfs_algo.explored
            bfs_path = self._controller._bfs_algo.path

        if self._controller.is_astar_enabled and self._controller._astar_algo:
            astar_exp = self._controller._astar_algo.explored
            astar_path = self._controller._astar_algo.path

        self._grid_canvas.set_explored(bfs_exp, astar_exp)
        if bfs_path or astar_path:
            self._grid_canvas.set_paths(bfs_path, astar_path)

    def _on_metrics_update(
        self,
        bfs_m: Optional[AlgorithmMetrics],
        astar_m: Optional[AlgorithmMetrics],
    ) -> None:
        self._stats_panel.update_metrics(bfs_m, astar_m)

    def _on_reset_view(self) -> None:
        self._grid_canvas.clear_search_visuals()
        self._stats_panel.reset()

    # ---- Callbacks de Usuario ----

    def _handle_speed_change(self, delay_ms: int) -> None:
        self._controller.step_delay_ms = delay_ms

    def _handle_clear_obstacles(self) -> None:
        if self._controller.mode in (ExecutionMode.RUNNING,):
            return
        self._grid.clear_obstacles()
        self._controller.reset()
        self._grid_canvas.redraw()
