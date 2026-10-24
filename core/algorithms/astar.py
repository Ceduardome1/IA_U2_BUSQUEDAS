"""Implementación pura del algoritmo A* (A-Estrella)."""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple

from core.algorithms.base import SearchAlgorithm
from core.grid import GridMap
from core.heuristics import HeuristicFunction, manhattan_distance
from core.types import AlgorithmType, Position, StepResult


class AStarAlgorithm(SearchAlgorithm):
    """
    Algoritmo de búsqueda informada A*.
    Utiliza g(n) + h(n) para priorizar la exploración de nodos con menor costo estimado.
    """

    def __init__(
        self,
        grid: GridMap,
        heuristic: HeuristicFunction = manhattan_distance,
    ) -> None:
        super().__init__(grid)
        self._heuristic: HeuristicFunction = heuristic
        self._open_heap: List[Tuple[float, int, Position]] = []
        self._open_set_positions: Set[Position] = set()
        self._closed_set: Set[Position] = set()
        self._g_score: Dict[Position, float] = {}
        self._f_score: Dict[Position, float] = {}
        self._parent: Dict[Position, Optional[Position]] = {}
        self._counter: int = 0  # Desempate en el heap
        self.reset()

    @property
    def algorithm_type(self) -> AlgorithmType:
        return AlgorithmType.ASTAR

    @property
    def frontier(self) -> Set[Position]:
        return set(self._open_set_positions)

    def reset(self) -> None:
        self._open_heap.clear()
        self._open_set_positions.clear()
        self._closed_set.clear()
        self._g_score.clear()
        self._f_score.clear()
        self._parent.clear()
        self._explored.clear()
        self._path.clear()
        self._is_finished = False
        self._path_found = False
        self._counter = 0
        self._elapsed_time_ms = 0.0

        start_node = self._grid.start
        goal_node = self._grid.goal

        self._g_score[start_node] = 0.0
        h_start = self._heuristic(start_node, goal_node)
        self._f_score[start_node] = h_start

        self._parent[start_node] = None
        heapq.heappush(self._open_heap, (h_start, self._counter, start_node))
        self._open_set_positions.add(start_node)

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

        # Extraer el nodo con menor f_score no procesado
        current: Optional[Position] = None
        while self._open_heap:
            _, _, node = heapq.heappop(self._open_heap)
            if node in self._closed_set:
                continue
            current = node
            break

        # Si no encontramos ningún nodo válido en el heap, no hay camino
        if current is None:
            self._is_finished = True
            self._path_found = False
            self._open_set_positions.clear()
            return StepResult(
                algorithm_type=self.algorithm_type,
                current_node=None,
                frontier=set(),
                explored=self.explored,
                is_finished=True,
                path_found=False,
                path=[],
            )

        self._open_set_positions.discard(current)
        self._closed_set.add(current)
        self._explored.add(current)

        # Verificar si alcanzamos el objetivo
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

        # Evaluar vecinos
        current_g = self._g_score[current]
        for neighbor in self._grid.get_neighbors(current):
            if neighbor in self._closed_set:
                continue

            tentative_g = current_g + 1.0  # Costo ortogonal uniforme = 1

            if tentative_g < self._g_score.get(neighbor, float("inf")):
                self._parent[neighbor] = current
                self._g_score[neighbor] = tentative_g
                f_val = tentative_g + self._heuristic(neighbor, self._grid.goal)
                self._f_score[neighbor] = f_val

                self._counter += 1
                heapq.heappush(self._open_heap, (f_val, self._counter, neighbor))
                self._open_set_positions.add(neighbor)

        return StepResult(
            algorithm_type=self.algorithm_type,
            current_node=current,
            frontier=self.frontier,
            explored=self.explored,
            is_finished=False,
            path_found=False,
            path=[],
        )
