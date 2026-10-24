"""Controlador para orquestar la ejecución sincronizada de las búsquedas."""

from __future__ import annotations

from typing import Callable, Optional, Set
import time

from core.algorithms.astar import AStarAlgorithm
from core.algorithms.base import SearchAlgorithm
from core.algorithms.bfs import BFSAlgorithm
from core.grid import GridMap
from core.types import AlgorithmMetrics, AlgorithmType, ExecutionMode, StepResult


class SearchController:
    """
    Controlador MVC. Gestiona el ciclo de vida de la ejecución,
    el paso a paso, la velocidad y la sincronización de uno o dos algoritmos.
    """

    def __init__(self, grid: GridMap) -> None:
        self._grid: GridMap = grid
        self._mode: ExecutionMode = ExecutionMode.IDLE

        # Selección de algoritmos
        self._enabled_algorithms: Set[AlgorithmType] = {AlgorithmType.BFS, AlgorithmType.ASTAR}

        # Instancias de algoritmos
        self._bfs_algo: Optional[BFSAlgorithm] = None
        self._astar_algo: Optional[AStarAlgorithm] = None

        # Tiempos de ejecución acumulados
        self._bfs_start_time: float = 0.0
        self._bfs_elapsed_ms: float = 0.0
        self._astar_start_time: float = 0.0
        self._astar_elapsed_ms: float = 0.0

        # Velocidad en milisegundos entre pasos automáticos
        self._step_delay_ms: int = 50

        # Callbacks para la Vista (Observadores)
        self.on_state_change: Optional[Callable[[ExecutionMode], None]] = None
        self.on_step_update: Optional[Callable[[Optional[StepResult], Optional[StepResult]], None]] = None
        self.on_metrics_update: Optional[Callable[[Optional[AlgorithmMetrics], Optional[AlgorithmMetrics]], None]] = None
        self.on_reset_view: Optional[Callable[[], None]] = None

        # Callback programador del bucle temporal (proporcionado por la GUI o loop externo)
        self._schedule_callback: Optional[Callable[[int, Callable[[], None]], object]] = None
        self._cancel_schedule_callback: Optional[Callable[[object], None]] = None
        self._scheduled_task_id: Optional[object] = None

        self._init_algorithms()

    @property
    def mode(self) -> ExecutionMode:
        return self._mode

    @property
    def grid(self) -> GridMap:
        return self._grid

    @property
    def step_delay_ms(self) -> int:
        return self._step_delay_ms

    @step_delay_ms.setter
    def step_delay_ms(self, delay: int) -> None:
        self._step_delay_ms = max(5, min(1000, delay))

    @property
    def is_bfs_enabled(self) -> bool:
        return AlgorithmType.BFS in self._enabled_algorithms

    @property
    def is_astar_enabled(self) -> bool:
        return AlgorithmType.ASTAR in self._enabled_algorithms

    def set_scheduler(
        self,
        schedule_fn: Callable[[int, Callable[[], None]], object],
        cancel_fn: Callable[[object], None],
    ) -> None:
        """Inyecta el mecanismo de temporizador (ej. Tk.after y Tk.after_cancel)."""
        self._schedule_callback = schedule_fn
        self._cancel_schedule_callback = cancel_fn

    def set_algorithm_enabled(self, algo_type: AlgorithmType, enabled: bool) -> None:
        """Activa o desactiva un algoritmo. Solo permitido cuando está en IDLE."""
        if self._mode not in (ExecutionMode.IDLE, ExecutionMode.FINISHED):
            return

        if enabled:
            self._enabled_algorithms.add(algo_type)
        else:
            self._enabled_algorithms.discard(algo_type)

        self._init_algorithms()
        self._emit_metrics()

    def _set_mode(self, mode: ExecutionMode) -> None:
        self._mode = mode
        if self.on_state_change:
            self.on_state_change(mode)

    def _init_algorithms(self) -> None:
        """Inicializa las instancias de los algoritmos seleccionados."""
        self._bfs_algo = BFSAlgorithm(self._grid) if self.is_bfs_enabled else None
        self._astar_algo = AStarAlgorithm(self._grid) if self.is_astar_enabled else None
        self._bfs_elapsed_ms = 0.0
        self._astar_elapsed_ms = 0.0

    def toggle_start_pause(self) -> None:
        """Inicia en modo automático o pausa si ya está corriendo."""
        if not self._enabled_algorithms:
            return

        if self._mode == ExecutionMode.RUNNING:
            self.pause()
        elif self._mode in (ExecutionMode.IDLE, ExecutionMode.PAUSED):
            self.start()
        elif self._mode == ExecutionMode.FINISHED:
            self.reset()
            self.start()

    def start(self) -> None:
        """Arranca el ciclo de ejecución continua automática."""
        if not self._enabled_algorithms:
            return

        if self._mode == ExecutionMode.FINISHED:
            self.reset()

        self._set_mode(ExecutionMode.RUNNING)
        self._schedule_next_step()

    def pause(self) -> None:
        """Pausa la ejecución automática."""
        if self._scheduled_task_id is not None and self._cancel_schedule_callback:
            self._cancel_schedule_callback(self._scheduled_task_id)
            self._scheduled_task_id = None
        self._set_mode(ExecutionMode.PAUSED)

    def manual_step(self) -> None:
        """
        Avanza exactamente un paso. Si estaba en modo automático,
        lo pausa para pasar al control manual.
        """
        if self._mode == ExecutionMode.RUNNING:
            self.pause()

        if self._mode in (ExecutionMode.IDLE, ExecutionMode.PAUSED):
            if self._mode == ExecutionMode.IDLE:
                self._set_mode(ExecutionMode.PAUSED)
            self._execute_single_step()

    def skip(self) -> None:
        """Ejecuta instantáneamente hasta que todos los algoritmos activos finalicen."""
        if self._scheduled_task_id is not None and self._cancel_schedule_callback:
            self._cancel_schedule_callback(self._scheduled_task_id)
            self._scheduled_task_id = None

        if self._mode == ExecutionMode.FINISHED:
            return

        # Resolver BFS si está activo
        bfs_step: Optional[StepResult] = None
        if self._bfs_algo and not self._bfs_algo.is_finished:
            t0 = time.perf_counter()
            while not self._bfs_algo.is_finished:
                bfs_step = self._bfs_algo.step()
            self._bfs_elapsed_ms += (time.perf_counter() - t0) * 1000.0

        # Resolver A* si está activo
        astar_step: Optional[StepResult] = None
        if self._astar_algo and not self._astar_algo.is_finished:
            t0 = time.perf_counter()
            while not self._astar_algo.is_finished:
                astar_step = self._astar_algo.step()
            self._astar_elapsed_ms += (time.perf_counter() - t0) * 1000.0

        self._set_mode(ExecutionMode.FINISHED)

        if self.on_step_update:
            self.on_step_update(bfs_step, astar_step)

        self._emit_metrics()

    def reset(self) -> None:
        """Detiene cualquier tarea y reinicia el estado conservando los obstáculos."""
        if self._scheduled_task_id is not None and self._cancel_schedule_callback:
            self._cancel_schedule_callback(self._scheduled_task_id)
            self._scheduled_task_id = None

        self._init_algorithms()
        self._set_mode(ExecutionMode.IDLE)

        if self.on_reset_view:
            self.on_reset_view()

        self._emit_metrics()

    def _execute_single_step(self) -> None:
        """Avanza una iteración en ambos algoritmos activos y actualiza la vista."""
        bfs_step: Optional[StepResult] = None
        astar_step: Optional[StepResult] = None

        if self._bfs_algo and not self._bfs_algo.is_finished:
            t0 = time.perf_counter()
            bfs_step = self._bfs_algo.step()
            self._bfs_elapsed_ms += (time.perf_counter() - t0) * 1000.0

        if self._astar_algo and not self._astar_algo.is_finished:
            t0 = time.perf_counter()
            astar_step = self._astar_algo.step()
            self._astar_elapsed_ms += (time.perf_counter() - t0) * 1000.0

        if self.on_step_update:
            self.on_step_update(bfs_step, astar_step)

        self._emit_metrics()

        # Comprobar si todos los activos finalizaron
        bfs_done = self._bfs_algo.is_finished if self._bfs_algo else True
        astar_done = self._astar_algo.is_finished if self._astar_algo else True

        if bfs_done and astar_done:
            self._set_mode(ExecutionMode.FINISHED)

    def _auto_step(self) -> None:
        """Paso invocado por el bucle del temporizador."""
        if self._mode != ExecutionMode.RUNNING:
            return

        self._execute_single_step()

        if self._mode == ExecutionMode.RUNNING:
            self._schedule_next_step()

    def _schedule_next_step(self) -> None:
        if self._schedule_callback:
            self._scheduled_task_id = self._schedule_callback(self._step_delay_ms, self._auto_step)

    def _emit_metrics(self) -> None:
        if not self.on_metrics_update:
            return

        bfs_m: Optional[AlgorithmMetrics] = None
        astar_m: Optional[AlgorithmMetrics] = None

        if self._bfs_algo:
            bfs_m = AlgorithmMetrics(
                algorithm_type=AlgorithmType.BFS,
                explored_states_count=len(self._bfs_algo.explored),
                path_length=len(self._bfs_algo.path),
                path_found=self._bfs_algo.path_found,
                execution_time_ms=self._bfs_elapsed_ms,
            )

        if self._astar_algo:
            astar_m = AlgorithmMetrics(
                algorithm_type=AlgorithmType.ASTAR,
                explored_states_count=len(self._astar_algo.explored),
                path_length=len(self._astar_algo.path),
                path_found=self._astar_algo.path_found,
                execution_time_ms=self._astar_elapsed_ms,
            )

        self.on_metrics_update(bfs_m, astar_m)
