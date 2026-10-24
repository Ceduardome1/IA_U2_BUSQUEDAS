"""Punto de entrada principal para la aplicación de comparación de búsquedas."""

from __future__ import annotations

import sys
from core.grid import GridMap
from controller.search_controller import SearchController
from view.main_window import MainWindow


def create_initial_obstacles(grid: GridMap) -> None:
    """Configura un laberinto/patrón de obstáculos inicial interesante."""
    rows = grid.rows
    cols = grid.cols

    # Muro vertical con aperturas
    mid_col = cols // 2
    for r in range(2, rows - 2):
        if r not in (rows // 4, 3 * rows // 4):
            grid.add_obstacle((r, mid_col))

    # Muro secundario
    quarter_col = cols // 4
    for r in range(rows // 3, rows - 3):
        grid.add_obstacle((r, quarter_col))


def main() -> None:
    # 1. Instanciar Modelo
    grid = GridMap(rows=22, cols=32)
    create_initial_obstacles(grid)

    # 2. Instanciar Controlador
    controller = SearchController(grid)

    # 3. Instanciar Vista
    app = MainWindow(grid=grid, controller=controller)

    # 4. Iniciar Bucle de Eventos
    try:
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
