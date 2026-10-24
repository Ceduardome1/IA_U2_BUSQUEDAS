# Comparador de Búsquedas en Cuadrícula (BFS vs A*)

Aplicación interactiva de escritorio desarrollada en Python bajo el patrón arquitectónico Modelo-Vista-Controlador (MVC). Permite comparar empíricamente y visualizar la ejecución de los algoritmos de búsqueda no informada (BFS) e informada (A* con heurística de Manhattan).

---

## Requisitos del Sistema

* **Python 3.8 o superior**
* **Tkinter** (módulo estándar de interfaz gráfica para Python).
  * *En distribuciones basadas en Debian o Ubuntu:*
    ```bash
    sudo apt update && sudo apt install -y python3-tk
    ```
  * *En distribuciones basadas en Fedora o RHEL:*
    ```bash
    sudo dnf install -y python3-tkinter
    ```
* **Dependencias externas:** Ninguna. El proyecto utiliza exclusivamente módulos pertenecientes a la biblioteca estándar de Python (`tkinter`, `heapq`, `dataclasses`, `collections`, entre otros).

---

## Configuración e Instalación

### 1. Ubicación en el directorio del proyecto
```bash
cd /ruta/al/proyecto/Busquedas
```

### 2. Creación opcional de entorno virtual
Para aislar el entorno de ejecución, puede inicializar un entorno virtual con el módulo estándar `venv`:

```bash
# Creación del entorno
python3 -m venv .venv

# Activación en sistemas Linux o macOS
source .venv/bin/activate

# Activación en sistemas Windows
.venv\Scripts\activate
```

---

## Ejecución del Programa

Para iniciar la interfaz gráfica, ejecute el archivo principal [`main.py`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/main.py):

```bash
python3 main.py
```

---

## Controles de la Interfaz

* **Iniciar / Pausar:** Alterna el ciclo continuo de ejecución de los algoritmos en tiempo real.
* **Paso a Paso:** Ejecuta una única iteración de exploración de nodos, facilitando el análisis detallado del avance de la frontera.
* **Saltar al final:** Ejecuta el algoritmo hasta su conclusión de forma inmediata.
* **Selección de algoritmos:** Permite alternar la visualización independiente o simultánea de BFS y A*.
* **Control de velocidad:** Ajusta el intervalo de tiempo entre cada paso de la simulación.
* **Edición de la cuadrícula:**
  * **Clic izquierdo o arrastre:** Inserta nodos de obstáculo en las coordenadas seleccionadas.
  * **Clic derecho:** Elimina obstáculos existentes.
  * **Limpiar:** Restablece la cuadrícula eliminando todos los obstáculos.
* **Panel de estadísticas:** Reporta métricas en tiempo real respecto al total de nodos explorados, la longitud de la ruta óptima calculada y el tiempo transcurrido en milisegundos.

---

## Estructura del Proyecto

* [`main.py`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/main.py): Punto de entrada de la aplicación y parametrización inicial del entorno.
* [`core/`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/core): Lógica de dominio, representación del mapa en cuadrícula ([`GridMap`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/core/grid.py)), definiciones de tipos y módulos de búsqueda ([`BFSAlgorithm`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/core/algorithms/bfs.py), [`AStarAlgorithm`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/core/algorithms/astar.py) y funciones heurísticas).
* [`controller/`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/controller): Controlador de eventos, temporización y despacho de estados ([`SearchController`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/controller/search_controller.py)).
* [`view/`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/view): Capa de presentación desarrollada sobre Tkinter ([`MainWindow`](file:///mnt/datos/Code/Pyton/IA/U2/Busquedas/view/main_window.py), lienzo gráfico y paneles de control y métricas).
