"""Funciones heurísticas puras para algoritmos de búsqueda informada."""

from __future__ import annotations

import math
from typing import Callable
from core.types import Position

# Definición del tipo de una función heurística
HeuristicFunction = Callable[[Position, Position], float]


def manhattan_distance(a: Position, b: Position) -> float:
    """Calcula la distancia de Manhattan entre dos coordenadas."""
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def euclidean_distance(a: Position, b: Position) -> float:
    """Calcula la distancia Euclidiana entre dos coordenadas."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
