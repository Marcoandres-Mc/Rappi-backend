# Rappi – Optimización de Rutas · Documentación del Backend

Backend en **FastAPI** que modela la red vial de **Miraflores y San Isidro (Lima)** como un grafo dirigido y calcula rutas de reparto con Dijkstra, fuerza bruta, backtracking y divide y vencerás.

---

## 1. Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload     # http://localhost:8000
```

- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- CORS permitido solo para `http://localhost:3000` y `http://127.0.0.1:3000` (editar en `app/main.py` al desplegar el frontend).
- El grafo se carga **desde disco** (`app/data/graph/miraflores_san_isidro.graphml`); no se descarga nada al iniciar.

> ⚠️ Pendiente: `requirements.txt` está codificado en UTF-16 y `pip install -r` puede fallar. Re-guardarlo en UTF-8 (`pip freeze` desde CMD, no PowerShell).

---

## 2. Dataset

| Dato | Valor |
|---|---|
| Fuente | OpenStreetMap vía OSMnx 2.1.1 |
| Zona | Miraflores y San Isidro, Lima, Perú |
| Tipo de red | `drive`, simplificada |
| Nodos | **2717** |
| Aristas | **5371** |
| Tipo | `MultiDiGraph` dirigido (respeta calles de un solo sentido) |

Cada nodo es una intersección con `x` (longitud) e `y` (latitud). Cada arista tiene `length` (metros), `highway` (tipo de vía) y otros atributos de OSM.

> Nota para el informe: el texto original del enunciado menciona 1580 nodos y 3420 aristas; los valores reales del dataset son los de la tabla.

---

## 3. Arquitectura

```
app/
├── main.py                      # App FastAPI, CORS, /, /health
├── core/config.py               # Settings (hoy sin uso activo)
├── api/routes/route_routes.py   # Endpoints /routes/*
├── schemas/
│   ├── route.py                 # Modelos Pydantic de request/response (los que usa la API)
│   ├── grafo.py                 # Modelos de nodo/arista/grafo (sin uso en endpoints)
│   ├── pedido.py, repartidor.py, usuario.py   # Stubs para futuro
├── services/
│   ├── route_service.py         # Ruta punto a punto + caché del grafo
│   ├── delivery_service.py      # Orquesta el problema de entregas (TSP)
│   ├── cost_matrix_service.py   # Matriz de costos NxN con Dijkstra
│   └── pedido_service.py        # Stub
├── algoritmos/
│   ├── dijkstra.py              # dijkstra() y dijkstra_to_targets()
│   ├── fuerza_bruta.py          # TSP exacto por permutaciones
│   ├── backtracking.py          # TSP exacto con poda
│   └── divide_venceras.py       # TSP aproximado por partición geográfica
├── graph/
│   ├── graph_loader.py          # Carga y valida el GraphML
│   ├── graph_builder.py         # Pesos con tráfico + lista de adyacencia
│   └── graph_utils.py           # Nodo más cercano, coordenadas, distancia de ruta
└── data/graph/                  # Dataset (.graphml)
scripts/                         # Scripts de verificación (ver sección 8)
```

### Flujo de una petición de entregas

```
Request ─► validar límite por algoritmo
       ─► get_prepared_graph(hora)           (grafo con pesos, en caché por hora)
       ─► find_nearest_node por cada punto   (Haversine, O(V))
       ─► build_cost_matrix                  (1 Dijkstra por origen → matriz NxN)
       ─► algoritmo TSP sobre la matriz      (fuerza bruta / backtracking / D&C)
       ─► reconstruir camino completo        (concatena caminos mínimos entre paradas)
       ─► Response (métricas + path lat/lon)
```

---

## 4. Modelo de costos y tráfico

Cada arista tiene `weight = distancia_m × factor_arista`.

**Factor base por hora** (`get_traffic_factor`):

| Franja | Factor base |
|---|---|
| 07:00–09:59 y 17:00–19:59 (hora punta) | 2.5 |
| 10:00–16:59 y 20:00–21:59 | 1.5 |
| Resto (madrugada/noche) | 1.0 |

**Factor por arista** (`get_edge_factor`): depende del tipo de vía (`highway`):

```
factor_arista = 1 + (factor_base − 1) × sensibilidad
```

| Tipo de vía | Sensibilidad |
|---|---|
| `trunk`, `primary` | 1.0 |
| `secondary` | 0.7 |
| `tertiary` | 0.5 |
| Otras (residential, service…) | 0.2 |

Así, en hora punta una avenida cuesta ×2.5 pero una calle residencial solo ×1.3, y Dijkstra puede elegir rutas distintas según la hora.

Consecuencias para el frontend:
- `distancia_total_m` es la distancia **real** en metros del recorrido.
- `weighted_cost` es el costo **con tráfico** (unidades ≈ "metros equivalentes"); siempre cumple `distancia ≤ weighted_cost ≤ distancia × 2.5`.

---

## 5. Endpoints

Base URL: `http://localhost:8000`

### 5.1 `GET /`
```json
{ "message": "Backend conectado y funcionando" }
```

### 5.2 `GET /health`
```json
{ "status": "ok" }
```

### 5.3 `GET /routes/`
Verifica que el módulo funciona y lista los algoritmos disponibles con sus límites. El frontend puede leer este endpoint para llenar el selector de algoritmos.

**Response 200**
```json
{
  "message": "Módulo de rutas funcionando",
  "algorithms": {
    "direct_route": ["dijkstra"],
    "deliveries": [
      { "name": "brute_force",    "max_deliveries": 8,  "optimal": true  },
      { "name": "backtracking",   "max_deliveries": 12, "optimal": true  },
      { "name": "divide_conquer", "max_deliveries": 30, "optimal": false }
    ]
  }
}
```

| Campo | Significado |
|---|---|
| `direct_route` | Algoritmos válidos para `POST /routes/calculate` |
| `deliveries` | Algoritmos válidos para `POST /routes/deliveries`, con su máximo de entregas y si garantizan el óptimo |

### 5.4 `POST /routes/calculate` — ruta punto a punto

**Request**
```json
{
  "origin":      { "lat": -12.1219, "lon": -77.0297 },
  "destination": { "lat": -12.0925, "lon": -77.0365 },
  "algorithm": "dijkstra",
  "traffic_hour": 8
}
```

| Campo | Tipo | Reglas |
|---|---|---|
| `origin`, `destination` | `{lat, lon}` | lat ∈ [-90, 90], lon ∈ [-180, 180]. Se ajustan al nodo vial más cercano |
| `algorithm` | string | Valor por defecto `"dijkstra"`. **Solo `dijkstra` está implementado aquí**; los demás valores (`brute_force`, `backtracking`, `divide_conquer`) devuelven 400 |
| `traffic_hour` | int | 0–23, por defecto 12 |

**Response 200**
```json
{
  "algorithm": "dijkstra",
  "execution_time_ms": 3.33,
  "nodos_visitados": 2128,
  "distancia_total_m": 4484.76,
  "weighted_cost": 7118.80,
  "path": [ { "lat": -12.1223648, "lon": -77.0290937 }, "..." ]
}
```

| Campo | Significado |
|---|---|
| `execution_time_ms` | Tiempo solo de Dijkstra (sin preparar grafo) |
| `nodos_visitados` | Nodos extraídos de la cola de prioridad (medida de esfuerzo) |
| `distancia_total_m` | Metros reales del camino |
| `weighted_cost` | Costo con tráfico |
| `path` | Polilínea ordenada lista para dibujar en el mapa |

### 5.5 `POST /routes/deliveries` — múltiples entregas (TSP)

**Request**
```json
{
  "origin": { "lat": -12.1219, "lon": -77.0297 },
  "destinations": [
    { "lat": -12.0925, "lon": -77.0365 },
    { "lat": -12.1328, "lon": -77.0225 },
    { "lat": -12.1317, "lon": -77.0307 }
  ],
  "algorithm": "backtracking",
  "traffic_hour": 8,
  "return_to_origin": false
}
```

| Campo | Tipo | Reglas |
|---|---|---|
| `origin` | `{lat, lon}` | Depósito / punto de partida |
| `destinations` | lista | 1 a 30 elementos (el límite real depende del algoritmo) |
| `algorithm` | string | `brute_force` \| `backtracking` \| `divide_conquer` (**obligatorio**) |
| `traffic_hour` | int | 0–23, por defecto 12 |
| `return_to_origin` | bool | Si `true`, la ruta termina volviendo al depósito. Por defecto `false` |

**Límites por algoritmo**

| Algoritmo | Máx. entregas | Óptimo | Complejidad |
|---|---|---|---|
| `brute_force` | **8** | Sí | O(N!) |
| `backtracking` | **12** | Sí | O(N!) en el peor caso, con poda (cota greedy inicial) |
| `divide_conquer` | **30** | **No** (heurística) | ≈ O(N log N) + permutaciones de grupos de ≤3 |

La matriz de costos se construye con N+1 corridas de Dijkstra (una por punto), y cada algoritmo trabaja sobre esa matriz.

**Response 200**
```json
{
  "algorithm": "backtracking",
  "execution_time_ms": 0.05,
  "matrix_time_ms": 41.2,
  "nodos_visitados": 8757,
  "states_explored": 9,
  "branches_pruned": 5,
  "distancia_total_m": 9120.4,
  "weighted_cost": 13401.35,
  "delivery_order": [0, 2, 3, 1],
  "is_optimal": true,
  "path": [ { "lat": -12.12, "lon": -77.03 }, "..." ]
}
```

| Campo | Significado |
|---|---|
| `execution_time_ms` | Tiempo **solo del algoritmo TSP** (sin la matriz) |
| `matrix_time_ms` | Tiempo de construir la matriz con Dijkstra |
| `nodos_visitados` | Suma de nodos explorados por todas las corridas de Dijkstra de la matriz |
| `states_explored` | Estados/permutaciones evaluados por el algoritmo TSP |
| `branches_pruned` | Ramas descartadas por poda (solo `backtracking`; en los demás es 0) |
| `weighted_cost` | Costo total con tráfico del orden elegido |
| `delivery_order` | **Índices** de visita: `0` = origen, `1..N` = destinos en el orden en que se enviaron. Ej.: `[0, 2, 3, 1]` = origen → destino 2 → destino 3 → destino 1. Con `return_to_origin=true` termina en `0` |
| `is_optimal` | `true` para fuerza bruta y backtracking, `false` para divide y vencerás |
| `path` | Polilínea completa del recorrido (concatena los caminos mínimos entre paradas) |

> Para numerar marcadores en el mapa: el marcador del destino `k` (1-indexado según el request) recibe el número `posición de k dentro de delivery_order`.

### 5.6 Errores

| Código | Cuándo | Cuerpo |
|---|---|---|
| 400 | Algoritmo no disponible en `/calculate`; excede el límite de entregas; dos puntos caen en el mismo nodo vial; no existe camino dirigido entre dos puntos; hora/coordenada inválida | `{"detail": "mensaje en español"}` |
| 422 | Validación de Pydantic (campo faltante, tipo incorrecto, rango, `algorithm` inválido, `destinations` vacía o > 30) | Formato estándar de FastAPI |
| 500 | Error inesperado. En `/routes/calculate`: `"Error interno al calcular la ruta"`. En `/routes/deliveries`: `"Error interno al optimizar las entregas"` | `{"detail": "..."}` (el traceback completo queda en el log del servidor con `logger.exception`) |

Mensajes de ejemplo del 400:
- `"'brute_force' admite como máximo 8 entregas; se recibieron 9."`
- `"Dos o más ubicaciones corresponden al mismo nodo vial."`
- `"El algoritmo 'backtracking' todavía no está disponible."` (en `/calculate`)

---

## 6. Detalle de los algoritmos

### Dijkstra (`algoritmos/dijkstra.py`)
- Lista de adyacencia `dict[nodo, list[(vecino, peso)]]` y cola de prioridad con `heapq`.
- `dijkstra(adj, origen, destino)`: se detiene al llegar al destino. Devuelve `ShortestPathResult(path, total_cost, nodes_visited)`. Lanza `PathNotFoundError` (subclase de `ValueError`) si no hay camino dirigido.
- `dijkstra_to_targets(adj, origen, targets)`: una sola corrida que se detiene cuando alcanzó **todos** los destinos pedidos; usada para la matriz.
- Complejidad: O((V + E) log V). Rechaza pesos negativos.

### Fuerza bruta (`algoritmos/fuerza_bruta.py`)
- Prueba todas las permutaciones de los destinos (el índice 0 es el depósito).
- Complejidad O(N!·N). `states_explored` = N! permutaciones.

### Backtracking (`algoritmos/backtracking.py`)
- Búsqueda recursiva con **poda**: se descarta cualquier rama cuyo costo parcial ya iguale o supere la mejor solución conocida.
- Cota superior inicial con heurística greedy (vecino más cercano).
- Explora primero los candidatos más cercanos.
- Siempre encuentra el mismo costo óptimo que fuerza bruta, con menos estados.

### Divide y vencerás (`algoritmos/divide_venceras.py`)
- Divide los destinos por el eje (latitud o longitud) de mayor extensión, a la mitad.
- Caso base: grupos de ≤3 puntos se resuelven por permutaciones.
- Combina probando ambos órdenes de grupos y ambas orientaciones internas.
- **Heurística**: no garantiza el óptimo (`is_optimal=false`). Con pocos puntos suele coincidir con el óptimo; la diferencia aparece con N grande.

### Matriz de costos (`services/cost_matrix_service.py`)
- `build_cost_matrix(adjacency, nodes)` → `CostMatrixResult(nodes, costs, paths, nodes_visited)`.
- `costs[i][j]` = costo mínimo dirigido de `nodes[i]` a `nodes[j]`. **Es asimétrica** (calles de un solo sentido).
- `paths[i][j]` = lista de ids de nodos del camino.

---

## 7. Caché y rendimiento

- `get_base_graph()` (`lru_cache`): carga el GraphML una sola vez.
- `get_prepared_graph(hora)` (`lru_cache`, 24 entradas): devuelve `(grafo con pesos, lista de adyacencia)` para cada hora. **No modificar el grafo devuelto**: es compartido entre peticiones.
- `find_nearest_node` recorre todos los nodos (O(V)); suficiente para este tamaño.
- Referencia medida: Dijkstra punto a punto ≈ 3 ms sobre 2717 nodos.

---

## 8. Scripts de verificación

Ejecutar desde la raíz del proyecto con el venv activo:

| Comando | Qué valida |
|---|---|
| `python -m scripts.verificar_dijkstra` | Dijkstra punto a punto y que `distancia ≤ costo ≤ distancia×2.5` |
| `python -m scripts.verificar_matriz` | Matriz 4×4, y compara fuerza bruta vs backtracking vs D&C |
| `python -m scripts.verificar_equivalencia` | La matriz coincide con Dijkstra punto a punto |

Puntos de prueba usados en los scripts:

| Nombre | lat | lon |
|---|---|---|
| Depósito Miraflores | -12.1219 | -77.0297 |
| Entrega San Isidro | -12.0925 | -77.0365 |
| Entrega Reducto | -12.1328 | -77.0225 |
| Entrega Larcomar | -12.1317 | -77.0307 |

Resultado esperado con estos 4 puntos (hora 8, sin volver al origen): orden `[0, 2, 3, 1]`, costo ≈ 13401.35, idéntico en los tres algoritmos.

---

## 9. Guía para el frontend

### Ejemplo con `fetch`
```js
const API = "http://localhost:8000";

export async function calcularEntregas(payload) {
  const res = await fetch(`${API}/routes/deliveries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(
      typeof err.detail === "string" ? err.detail : "Datos inválidos"
    );
  }
  return res.json();
}
```

### Reglas que la interfaz debe aplicar
1. Modo **Ruta directa** → `/routes/calculate` con `algorithm: "dijkstra"`.
2. Modo **Entregas** → `/routes/deliveries` con uno de los 3 algoritmos.
3. Limitar el botón "Agregar destino" según el algoritmo: **8 / 12 / 30**.
4. Enviar `traffic_hour` como entero 0–23 (convertir "08:00" → `8`).
5. Dibujar `path` como polilínea; numerar las paradas según `delivery_order`.
6. Mostrar siempre: `execution_time_ms`, `matrix_time_ms`, `states_explored`, `branches_pruned`, `distancia_total_m`, `weighted_cost`, `is_optimal`.
7. Mostrar `detail` de los errores 400 tal cual (ya vienen en español).
8. Si dos destinos están muy cerca pueden caer en el mismo nodo vial → error 400; avisar al usuario.

### Modo "Comparar algoritmos"
Ejecutar las 3 peticiones con el mismo payload (cambiando solo `algorithm`) y mostrar tabla: tiempo, estados, ramas podadas, costo, óptimo. Si hay más de 8 destinos, omitir `brute_force`.

### Boceto de la interfaz
```
┌──────────────────────┬───────────────────────────────────────────┐
│ 🛵 OPTIMIZADOR       │                                           │
│ Miraflores/San Isidro│                                           │
├──────────────────────┤                                           │
│ TIPO DE RECORRIDO    │                                           │
│ (•) Entregas ( ) Dir.│                MAPA (Leaflet + OSM)       │
├──────────────────────┤        marcadores numerados + ruta        │
│ ORIGEN               │                                           │
│ [Seleccionar ▼] o clic en mapa                                   │
├──────────────────────┤                                           │
│ DESTINOS (n/12)      │                                           │
│ 1 [Entrega ▼]  [✕]   │                                           │
│ [+ Agregar destino]  │                                           │
│ [x] Volver al origen │                                           │
├──────────────────────┤                                           │
│ HORA DE SALIDA [08:00▼]                                          │
│ ALGORITMO                                                        │
│ (•) Fuerza bruta (≤8)│                                           │
│ ( ) Backtracking (≤12)                                           │
│ ( ) Divide y vencerás (≤30)                                      │
├──────────────────────┤                                           │
│ [ CALCULAR RUTA ]    ├───────────────────────────────────────────┤
│ [ COMPARAR TODOS ]   │ RESULTADOS                                │
│ [ Limpiar ]          │ Tiempo · Estados · Podas · Distancia ·    │
│                      │ Costo c/tráfico · ¿Óptimo? · Orden        │
└──────────────────────┴───────────────────────────────────────────┘
```

---

## 10. Pendientes y mejoras conocidas

- [ ] Re-guardar `requirements.txt` en UTF-8.
- [ ] `core/config.py`, `schemas/grafo.py`, `pedido`, `repartidor`, `usuario` aún no se usan en los endpoints.
- [ ] Agregar tests con `pytest` (fuerza bruta = backtracking; D&C ≥ óptimo).
- [ ] Script de benchmark N = 4…12 para la tabla de tiempos del informe.
- [ ] Ampliar CORS al dominio del frontend desplegado.
- [ ] Futuro: UFDS (conectividad) y Held-Karp, no incluidos en este parcial.