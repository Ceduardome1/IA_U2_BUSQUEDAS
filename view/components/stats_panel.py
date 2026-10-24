"""Panel inferior o lateral para comparar métricas de desempeño entre algoritmos."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.types import AlgorithmMetrics, VisualTheme


class StatsPanel(ttk.Frame):
    """Componente que presenta la comparativa de estados explorados y costos."""

    def __init__(
        self,
        master: tk.Misc,
        theme: VisualTheme = VisualTheme(),
        **kwargs,
    ) -> None:
        super().__init__(master, padding=(10, 6), **kwargs)
        self._theme = theme

        self._bfs_explored_val = tk.StringVar(value="-")
        self._bfs_length_val = tk.StringVar(value="-")
        self._bfs_status_val = tk.StringVar(value="Listo")

        self._astar_explored_val = tk.StringVar(value="-")
        self._astar_length_val = tk.StringVar(value="-")
        self._astar_status_val = tk.StringVar(value="Listo")

        self._comparison_val = tk.StringVar(value="Esperando ejecución...")

        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # ---- Tarjeta BFS ----
        bfs_card = ttk.LabelFrame(self, text=" Métricas BFS ", padding=6)
        bfs_card.grid(row=0, column=0, padx=6, pady=2, sticky="nsew")

        ttk.Label(bfs_card, text="Estados Explorados:").grid(row=0, column=0, sticky="w")
        ttk.Label(bfs_card, textvariable=self._bfs_explored_val, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, sticky="e")

        ttk.Label(bfs_card, text="Longitud del Camino:").grid(row=1, column=0, sticky="w")
        ttk.Label(bfs_card, textvariable=self._bfs_length_val, font=("TkDefaultFont", 9, "bold")).grid(row=1, column=1, sticky="e")

        ttk.Label(bfs_card, text="Estado:").grid(row=2, column=0, sticky="w")
        ttk.Label(bfs_card, textvariable=self._bfs_status_val, foreground=self._theme.bfs_path).grid(row=2, column=1, sticky="e")

        # ---- Tarjeta A* ----
        astar_card = ttk.LabelFrame(self, text=" Métricas A* ", padding=6)
        astar_card.grid(row=0, column=1, padx=6, pady=2, sticky="nsew")

        ttk.Label(astar_card, text="Estados Explorados:").grid(row=0, column=0, sticky="w")
        ttk.Label(astar_card, textvariable=self._astar_explored_val, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, sticky="e")

        ttk.Label(astar_card, text="Longitud del Camino:").grid(row=1, column=0, sticky="w")
        ttk.Label(astar_card, textvariable=self._astar_length_val, font=("TkDefaultFont", 9, "bold")).grid(row=1, column=1, sticky="e")

        ttk.Label(astar_card, text="Estado:").grid(row=2, column=0, sticky="w")
        ttk.Label(astar_card, textvariable=self._astar_status_val, foreground=self._theme.astar_path).grid(row=2, column=1, sticky="e")

        # ---- Tarjeta Comparación Resumen ----
        comp_card = ttk.LabelFrame(self, text=" Comparativa ", padding=6)
        comp_card.grid(row=0, column=2, padx=6, pady=2, sticky="nsew")

        lbl_comp = ttk.Label(
            comp_card,
            textvariable=self._comparison_val,
            wraplength=280,
            justify="center",
            font=("TkDefaultFont", 9, "italic"),
        )
        lbl_comp.pack(expand=True, fill="both")

    def update_metrics(
        self,
        bfs_m: Optional[AlgorithmMetrics],
        astar_m: Optional[AlgorithmMetrics],
    ) -> None:
        """Actualiza los valores mostrados en pantalla."""
        if bfs_m is not None:
            self._bfs_explored_val.set(str(bfs_m.explored_states_count))
            self._bfs_length_val.set(str(bfs_m.path_length) if bfs_m.path_found else "Sin ruta")
            self._bfs_status_val.set("Meta encontrada" if bfs_m.path_found else "En proceso...")
        else:
            self._bfs_explored_val.set("Desactivado")
            self._bfs_length_val.set("-")
            self._bfs_status_val.set("-")

        if astar_m is not None:
            self._astar_explored_val.set(str(astar_m.explored_states_count))
            self._astar_length_val.set(str(astar_m.path_length) if astar_m.path_found else "Sin ruta")
            self._astar_status_val.set("Meta encontrada" if astar_m.path_found else "En proceso...")
        else:
            self._astar_explored_val.set("Desactivado")
            self._astar_length_val.set("-")
            self._astar_status_val.set("-")

        # Comparativa cuantitativa
        if bfs_m and astar_m and bfs_m.explored_states_count > 0 and astar_m.explored_states_count > 0:
            diff = bfs_m.explored_states_count - astar_m.explored_states_count
            if diff > 0:
                pct = (diff / bfs_m.explored_states_count) * 100.0
                self._comparison_val.set(
                    f"A* exploró {diff} estados menos ({pct:.1f}% de ahorro frente a BFS)."
                )
            elif diff < 0:
                self._comparison_val.set(
                    f"BFS exploró {-diff} estados menos que A* en este escenario."
                )
            else:
                self._comparison_val.set("Ambos exploraron la misma cantidad de estados.")
        elif bfs_m or astar_m:
            self._comparison_val.set("Ejecutando algoritmo seleccionado...")
        else:
            self._comparison_val.set("Seleccione al menos un algoritmo.")

    def reset(self) -> None:
        """Restablece los indicadores de métricas."""
        self._bfs_explored_val.set("-")
        self._bfs_length_val.set("-")
        self._bfs_status_val.set("Listo")

        self._astar_explored_val.set("-")
        self._astar_length_val.set("-")
        self._astar_status_val.set("Listo")

        self._comparison_val.set("Listo para iniciar.")
