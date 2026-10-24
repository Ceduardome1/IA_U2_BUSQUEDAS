"""Interfaz base abstracta para algoritmos de búsqueda sobre cuadrículas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Set, Optional, Tuple
import time

from core.grid import GridMap
from core.types import Position, AlgorithmType, StepResult, AlgorithmMetrics


class SearchAlgorithm(ABC):
    """Contrato base para algoritmos de búsqueda paso a paso y por lote."""

    def __init__(self, grid: GridMap) -> None:
        self._grid: GridMap = grid
        self._is_finished: bool = False
        self._path_found: bool = False
        self._path: List[Position] = []
        self._explored: Set[Position] = set()
        self._start_time: float = 0.0
        self._elapsed_time_ms: float = 0.0

    @property
    @abstractmethod
    def algorithm_type(self) -> AlgorithmType:
        """Tipo de algoritmo."""
        pass

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def path_found(self) -> bool:
        return self._path_found

    @property
    def path(self) -> List[Position]:
        return list(self._path)

    @property
    def explored(self) -> Set[Position]:
        return set(self._explored)

    @property
    @abstractmethod
    def frontier(self) -> Set[Position]:
        """Conjunto actual de nodos en la frontera."""
        pass

    @property
    def metrics(self) -> AlgorithmMetrics:
        """Métricas acumuladas del algoritmo."""
        return AlgorithmMetrics(
            algorithm_type=self.algorithm_type,
            explored_states_count=len(self._explored),
            path_length=len(self._path),
            path_found=self._path_found,
            execution_time_ms=self._elapsed_time_ms,
        )

    @abstractmethod
    def step(self) -> StepResult:
        """
        Ejecuta exactamente un paso de la búsqueda.
        Retorna el estado actual de la frontera, explorados y si finalizó.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reinicia el estado del algoritmo para una nueva búsqueda."""
        pass

    def solve(self) -> Tuple[List[Position], AlgorithmMetrics]:
        """
        Ejecuta el algoritmo hasta completarse de manera síncrona.
        Útil para omitir la animación o pruebas unitarias directas.
        """
        start = time.perf_counter()
        while not self._is_finished:
            self.step()
        self._elapsed_time_ms = (time.perf_counter() - start) * 1000.0
        return self._path, self.metrics

    def _reconstruct_path(self, parent_map: dict[Position, Optional[Position]], end_pos: Position) -> List[Position]:
        """Reconstruye el camino desde el nodo inicial hasta la meta usando el mapa de padres."""
        path: List[Position] = []
        current: Optional[Position] = end_pos
        while current is not None:
            path.append(current)
            current = parent_map.get(current)
        path.reverse()
        return path
