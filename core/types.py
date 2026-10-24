"""Definiciones de tipos y estructuras de datos para el dominio de búsqueda."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, List, Set, Optional, Dict

# Tipo para coordenadas (fila, columna)
Position = Tuple[int, int]


class CellType(Enum):
    """Representa el tipo o función de una celda en el mapa."""
    EMPTY = auto()
    OBSTACLE = auto()
    START = auto()
    GOAL = auto()


class AlgorithmType(Enum):
    """Identificador de los algoritmos de búsqueda soportados."""
    BFS = "BFS (Búsqueda en Anchura)"
    ASTAR = "A* (A-Estrella)"


class ExecutionMode(Enum):
    """Estados del ciclo de vida del controlador."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


@dataclass(frozen=True)
class AlgorithmMetrics:
    """Métricas finales o acumuladas de un algoritmo."""
    algorithm_type: AlgorithmType
    explored_states_count: int = 0
    path_length: int = 0
    path_found: bool = False
    execution_time_ms: float = 0.0


@dataclass
class StepResult:
    """Resultado emitido en cada iteración de un algoritmo."""
    algorithm_type: AlgorithmType
    current_node: Optional[Position]
    frontier: Set[Position]
    explored: Set[Position]
    is_finished: bool
    path_found: bool
    path: List[Position] = field(default_factory=list)


@dataclass(frozen=True)
class VisualTheme:
    """Colores base para la representación visual."""
    bfs_explored: str = "#80B3FF"        # Azul claro
    bfs_path: str = "#0044CC"            # Azul oscuro / intenso
    astar_explored: str = "#FFB366"      # Naranja claro
    astar_path: str = "#CC5500"          # Naranja oscuro / intenso
    overlap_explored: str = "#B380FF"    # Púrpura (mezcla BFS + A*)
    start: str = "#28A745"               # Verde
    goal: str = "#DC3545"                # Rojo
    obstacle: str = "#2B2D42"            # Gris oscuro / grafito
    empty: str = "#F8F9FA"               # Blanco hueso
    grid_line: str = "#DEE2E6"           # Gris claro para cuadrícula
