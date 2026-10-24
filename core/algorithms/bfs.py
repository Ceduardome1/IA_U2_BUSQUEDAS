"""Implementación pura del algoritmo de Búsqueda en Anchura (BFS)."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Optional, Set

from core.algorithms.base import SearchAlgorithm
from core.grid import GridMap
from core.types import AlgorithmType, Position, StepResult


class BFSAlgorithm(SearchAlgorithm):
    """
    Algoritmo de Búsqueda en Anchura (Breadth-First Search).
    Garantiza el camino con menor número de pasos en grafos no ponderados.
    """

    def __init__(self, grid: GridMap) -> None:
        super().__init__(grid)
        self._queue: Deque[Position] = deque()
        self._visited: Set[Position] = set()
        self._parent: Dict[Position, Optional[Position]] = {}
        self.reset()

    @property
    def algorithm_type(self) -> AlgorithmType:
        return AlgorithmType.BFS

    @property
    def frontier(self) -> Set[Position]:
        return set(self._queue)

    def reset(self) -> None:
        self._queue.clear()
        self._visited.clear()
        self._parent.clear()
        self._explored.clear()
        self._path.clear()
        self._is_finished = False
        self._path_found = False
        self._elapsed_time_ms = 0.0

        # Inicializar con el nodo de inicio
        start_node = self._grid.start
        self._queue.append(start_node)
        self._visited.add(start_node)
        self._parent[start_node] = None

    def step(self) -> StepResult:
        if self._is_finished:
            return StepResult(
                algorithm_type=self.algorithm_type,
                current_node=None,
                frontier=self.frontier,
                explored=self.explored,
                is_finished=True,
                path_found=self._path_found,
                path=self.path,
            )

        # Si no hay más nodos en la frontera, no hay camino
        if not self._queue:
            self._is_finished = True
            self._path_found = False
            return StepResult(
                algorithm_type=self.algorithm_type,
                current_node=None,
                frontier=set(),
                explored=self.explored,
                is_finished=True,
                path_found=False,
                path=[],
            )

        current = self._queue.popleft()
        self._explored.add(current)

        # Verificar si llegamos a la meta
        if current == self._grid.goal:
            self._is_finished = True
            self._path_found = True
            self._path = self._reconstruct_path(self._parent, current)
            return StepResult(
                algorithm_type=self.algorithm_type,
                current_node=current,
                frontier=self.frontier,
                explored=self.explored,
                is_finished=True,
                path_found=True,
                path=self.path,
            )

        # Expandir vecinos
        for neighbor in self._grid.get_neighbors(current):
            if neighbor not in self._visited:
                self._visited.add(neighbor)
                self._parent[neighbor] = current
                self._queue.append(neighbor)

        return StepResult(
            algorithm_type=self.algorithm_type,
            current_node=current,
            frontier=self.frontier,
            explored=self.explored,
            is_finished=False,
            path_found=False,
            path=[],
        )
