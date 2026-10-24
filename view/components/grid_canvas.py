"""Canvas responsivo para la visualización del mapa y exploración de rutas."""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional, Set, Tuple

from core.grid import GridMap
from core.types import Position, VisualTheme


class GridCanvas(tk.Canvas):
    """
    Componente visual que renderiza la cuadrícula compartida y
    permite interactuar con obstáculos mediante clics y arrastre.
    """

    def __init__(
        self,
        master: tk.Misc,
        grid: GridMap,
        theme: VisualTheme = VisualTheme(),
        **kwargs,
    ) -> None:
        super().__init__(master, bg="#FFFFFF", highlightthickness=0, **kwargs)
        self._grid = grid
        self._theme = theme

        # Estados de visualización
        self._bfs_explored: Set[Position] = set()
        self._astar_explored: Set[Position] = set()
        self._bfs_path: List[Position] = []
        self._astar_path: List[Position] = []

        # Estado de edición de obstáculos
        self._is_editable: bool = True
        self._draw_obstacle_mode: Optional[bool] = None  # True para agregar, False para borrar

        # Dimensiones calculadas dinámicamente
        self._cell_size: float = 20.0
        self._offset_x: float = 0.0
        self._offset_y: float = 0.0

        # Eventos del ratón
        self.bind("<Configure>", self._on_resize)
        self.bind("<ButtonPress-1>", self._on_mouse_down)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.bind("<ButtonPress-3>", self._on_right_click)

    @property
    def is_editable(self) -> bool:
        return self._is_editable

    @is_editable.setter
    def is_editable(self, editable: bool) -> None:
        self._is_editable = editable

    def set_explored(self, bfs_explored: Set[Position], astar_explored: Set[Position]) -> None:
        """Actualiza los conjuntos de celdas exploradas y redibuja."""
        self._bfs_explored = set(bfs_explored)
        self._astar_explored = set(astar_explored)
        self.redraw()

    def set_paths(self, bfs_path: List[Position], astar_path: List[Position]) -> None:
        """Actualiza las rutas encontradas y redibuja."""
        self._bfs_path = list(bfs_path)
        self._astar_path = list(astar_path)
        self.redraw()

    def clear_search_visuals(self) -> None:
        """Limpia explorados y rutas, manteniendo obstáculos."""
        self._bfs_explored.clear()
        self._astar_explored.clear()
        self._bfs_path.clear()
        self._astar_path.clear()
        self.redraw()

    def _on_resize(self, event: tk.Event) -> None:
        """Recalcula el tamaño de las celdas para que quepa en el canvas disponible."""
        width = event.width
        height = event.height
        if width <= 10 or height <= 10:
            return

        cols = self._grid.cols
        rows = self._grid.rows

        # Calcular tamaño uniforme de celda
        cell_w = (width - 20) / cols
        cell_h = (height - 20) / rows
        self._cell_size = max(10.0, min(cell_w, cell_h))

        # Centrar la cuadrícula en el Canvas
        grid_width = self._cell_size * cols
        grid_height = self._cell_size * rows
        self._offset_x = (width - grid_width) / 2.0
        self._offset_y = (height - grid_height) / 2.0

        self.redraw()

    def _pos_from_coords(self, x: float, y: float) -> Optional[Position]:
        """Convierte coordenadas de píxeles del Canvas a posición (fila, columna)."""
        col = int((x - self._offset_x) // self._cell_size)
        row = int((y - self._offset_y) // self._cell_size)
        if 0 <= row < self._grid.rows and 0 <= col < self._grid.cols:
            return (row, col)
        return None

    def _on_mouse_down(self, event: tk.Event) -> None:
        if not self._is_editable:
            return
        pos = self._pos_from_coords(event.x, event.y)
        if pos and pos != self._grid.start and pos != self._grid.goal:
            is_obs = self._grid.is_obstacle(pos)
            self._draw_obstacle_mode = not is_obs  # Si era obstáculo, el trazo borra; si no, coloca
            if self._draw_obstacle_mode:
                self._grid.add_obstacle(pos)
            else:
                self._grid.remove_obstacle(pos)
            self.redraw()

    def _on_mouse_drag(self, event: tk.Event) -> None:
        if not self._is_editable or self._draw_obstacle_mode is None:
            return
        pos = self._pos_from_coords(event.x, event.y)
        if pos and pos != self._grid.start and pos != self._grid.goal:
            if self._draw_obstacle_mode:
                if not self._grid.is_obstacle(pos):
                    self._grid.add_obstacle(pos)
                    self.redraw()
            else:
                if self._grid.is_obstacle(pos):
                    self._grid.remove_obstacle(pos)
                    self.redraw()

    def _on_mouse_up(self, _event: tk.Event) -> None:
        self._draw_obstacle_mode = None

    def _on_right_click(self, event: tk.Event) -> None:
        if not self._is_editable:
            return
        pos = self._pos_from_coords(event.x, event.y)
        if pos:
            self._grid.remove_obstacle(pos)
            self.redraw()

    def redraw(self) -> None:
        """Redibuja completamente la cuadrícula, explorados, rutas y puntos clave."""
        self.delete("all")

        cs = self._cell_size
        ox = self._offset_x
        oy = self._offset_y
        rows = self._grid.rows
        cols = self._grid.cols

        # 1. Dibujar Celdas de la cuadrícula
        for r in range(rows):
            y1 = oy + r * cs
            y2 = y1 + cs
            for c in range(cols):
                x1 = ox + c * cs
                x2 = x1 + cs
                pos: Position = (r, c)

                # Determinar color de relleno según prioridad
                if pos == self._grid.start:
                    color = self._theme.start
                elif pos == self._grid.goal:
                    color = self._theme.goal
                elif self._grid.is_obstacle(pos):
                    color = self._theme.obstacle
                else:
                    in_bfs = pos in self._bfs_explored
                    in_astar = pos in self._astar_explored

                    if in_bfs and in_astar:
                        color = self._theme.overlap_explored
                    elif in_bfs:
                        color = self._theme.bfs_explored
                    elif in_astar:
                        color = self._theme.astar_explored
                    else:
                        color = self._theme.empty

                self.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=self._theme.grid_line,
                    width=1,
                )

        # 2. Etiquetas de Inicio y Fin
        sr, sc = self._grid.start
        self.create_text(
            ox + sc * cs + cs / 2,
            oy + sr * cs + cs / 2,
            text="S",
            fill="#FFFFFF",
            font=("Arial", int(max(8, cs * 0.5)), "bold"),
        )

        gr, gc = self._grid.goal
        self.create_text(
            ox + gc * cs + cs / 2,
            oy + gr * cs + cs / 2,
            text="G",
            fill="#FFFFFF",
            font=("Arial", int(max(8, cs * 0.5)), "bold"),
        )

        # 3. Dibujar Rutas
        # Para que ambas rutas sean visibles sobre las mismas celdas cuando se solapen,
        # trazamos líneas centrales con ligero desplazamiento o grosor.
        self._draw_path(self._bfs_path, self._theme.bfs_path, offset_y=-1.5, width=3.5)
        self._draw_path(self._astar_path, self._theme.astar_path, offset_y=1.5, width=3.5)

    def _draw_path(
        self,
        path: List[Position],
        color: str,
        offset_y: float = 0.0,
        width: float = 3.0,
    ) -> None:
        """Dibuja una línea continua que une las celdas de la ruta."""
        if len(path) < 2:
            return

        cs = self._cell_size
        ox = self._offset_x
        oy = self._offset_y

        coords: List[float] = []
        for r, c in path:
            cx = ox + c * cs + cs / 2.0
            cy = oy + r * cs + cs / 2.0 + offset_y
            coords.extend([cx, cy])

        self.create_line(
            coords,
            fill=color,
            width=width,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=False,
        )
