"""Modelo de datos de la cuadrícula para el espacio de búsqueda."""

from __future__ import annotations

from typing import List, Set, Optional
from core.types import Position, CellType


class GridMap:
    """Representa la cuadrícula de búsqueda, sus límites y obstáculos."""

    def __init__(
        self,
        rows: int = 25,
        cols: int = 35,
        start: Optional[Position] = None,
        goal: Optional[Position] = None,
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("Las filas y columnas deben ser enteros positivos.")

        self._rows: int = rows
        self._cols: int = cols
        self._obstacles: Set[Position] = set()

        self._start: Position = start if start is not None else (rows // 2, cols // 6)
        self._goal: Position = goal if goal is not None else (rows // 2, 5 * cols // 6)

        # Asegurar que el inicio y la meta sean válidos dentro del mapa
        self._validate_position(self._start)
        self._validate_position(self._goal)

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def start(self) -> Position:
        return self._start

    @start.setter
    def start(self, pos: Position) -> None:
        self._validate_position(pos)
        self._obstacles.discard(pos)
        self._start = pos

    @property
    def goal(self) -> Position:
        return self._goal

    @goal.setter
    def goal(self, pos: Position) -> None:
        self._validate_position(pos)
        self._obstacles.discard(pos)
        self._goal = pos

    @property
    def obstacles(self) -> Set[Position]:
        return set(self._obstacles)

    def is_valid_position(self, pos: Position) -> bool:
        """Determina si una posición cae dentro de los límites del mapa."""
        row, col = pos
        return 0 <= row < self._rows and 0 <= col < self._cols

    def is_obstacle(self, pos: Position) -> bool:
        return pos in self._obstacles

    def is_passable(self, pos: Position) -> bool:
        """Determina si una celda es transitable (dentro de límites y sin obstáculo)."""
        return self.is_valid_position(pos) and not self.is_obstacle(pos)

    def add_obstacle(self, pos: Position) -> bool:
        """Agrega un obstáculo si la posición no es inicio ni fin."""
        if not self.is_valid_position(pos) or pos == self._start or pos == self._goal:
            return False
        self._obstacles.add(pos)
        return True

    def remove_obstacle(self, pos: Position) -> bool:
        """Remueve un obstáculo si existe."""
        if pos in self._obstacles:
            self._obstacles.remove(pos)
            return True
        return False

    def toggle_obstacle(self, pos: Position) -> bool:
        """Alterna el estado de obstáculo de una celda."""
        if pos == self._start or pos == self._goal or not self.is_valid_position(pos):
            return False
        if pos in self._obstacles:
            self._obstacles.remove(pos)
            return False
        else:
            self._obstacles.add(pos)
            return True

    def clear_obstacles(self) -> None:
        """Elimina todos los obstáculos."""
        self._obstacles.clear()

    def get_cell_type(self, pos: Position) -> CellType:
        """Retorna el tipo de celda según su estado actual."""
        if pos == self._start:
            return CellType.START
        if pos == self._goal:
            return CellType.GOAL
        if pos in self._obstacles:
            return CellType.OBSTACLE
        return CellType.EMPTY

    def get_neighbors(self, pos: Position) -> List[Position]:
        """
        Obtiene los vecinos ortogonales válidos y transitables
        en orden estándar: Arriba, Derecha, Abajo, Izquierda.
        """
        row, col = pos
        candidates: List[Position] = [
            (row - 1, col),  # Arriba
            (row, col + 1),  # Derecha
            (row + 1, col),  # Abajo
            (row, col - 1),  # Izquierda
        ]
        return [c for c in candidates if self.is_passable(c)]

    def _validate_position(self, pos: Position) -> None:
        if not self.is_valid_position(pos):
            raise IndexError(f"La posición {pos} está fuera de los límites del mapa ({self._rows}x{self._cols}).")
