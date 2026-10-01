# 🛵 Rappi – Optimización de Rutas de Reparto (Backend)

Proyecto del curso de **Complejidad Algorítmica**. API en **FastAPI** que modela la red vial de **Miraflores y San Isidro (Lima)** como un grafo dirigido con tráfico dependiente de la hora y resuelve rutas de reparto con distintos algoritmos.

| Algoritmo | Uso | Óptimo | Máx. entregas | Complejidad |
|---|---|---|---|---|
| Dijkstra | Ruta punto a punto | Sí | — | O((V+E) log V) |
| Fuerza bruta | Orden de entregas (TSP) | Sí | 8 | O(N!) |
| Backtracking con poda | Orden de entregas (TSP) | Sí | 12 | O(N!) peor caso |
| Divide y vencerás | Orden de entregas (TSP) | **No** (heurística) | 30 | ≈ O(N log N) |

> Documentación técnica detallada del backend: [`BACKEND_DOCS.md`](./BACKEND_DOCS.md)

---

## Estado del proyecto

- ✅ **Backend listo para el parcial**: 4 algoritmos, 103 tests en verde.
- 🔜 **Frontend**: pendiente. Este README tiene todo lo necesario para empezar (secciones 3 a 8).
- 🔜 Futuro: UFDS (conectividad) y Held-Karp (programación dinámica).

---

## 1. Instalación y ejecución

```bash
git clone https://github.com/Marcoandres-Mc/Rappi-backend.git
cd Rappi-backend

python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt

uvicorn app.main:app --reload     # http://localhost:8000
```

- Swagger (probar endpoints sin escribir código): **http://localhost:8000/docs**
- El grafo se carga desde disco al recibir la primera petición (tarda un par de segundos); no se descarga nada de internet.

### Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

---

## 2. Dataset

| Dato | Valor |
|---|---|
| Fuente | OpenStreetMap vía OSMnx 2.1.1 |
| Zona | Miraflores y San Isidro, Lima, Perú |
| Archivo original | 2717 nodos, 5371 aristas |
| **Grafo usado (tras filtrar al componente fuertemente conectado)** | **2633 nodos, 5232 aristas** |
| Tipo | Dirigido (respeta calles de un solo sentido) |
| Peso de arista | `distancia_m × factor_de_tráfico` |

El filtro elimina 84 nodos inaccesibles (callejones y tramos aislados) para garantizar que exista camino entre cualquier par de puntos.

**Límites del mapa** (para centrar y restringir el mapa del frontend):

```
Latitud:   -12.1375  a  -12.0853
Longitud:  -77.0605  a  -77.0015
Centro:    lat -12.1099, lon -77.0315   (zoom inicial recomendado: 14)
```

---

## 3. 🎯 Guía para el encargado del frontend

### 3.1 Antes de empezar (importante)

1. **CORS**: el backend solo acepta peticiones desde `http://localhost:3000` y `http://127.0.0.1:3000`.
   - Con **Next.js / Create React App** el puerto por defecto ya es 3000. ✅
   - Con **Vite** el puerto por defecto es 5173 y **las peticiones serán bloqueadas**. Soluciones: arrancar con `npm run dev -- --port 3000`, o agregar `"http://localhost:5173"` a `allow_origins` en `app/main.py`.
2. Levanta el backend (sección 1) y confirma que `http://localhost:8000/health` devuelve `{"status":"ok"}`.
3. Prueba los endpoints desde `/docs` antes de programar para ver respuestas reales.

### 3.2 Stack sugerido

- **React o Next.js** (puerto 3000).
- **react-leaflet** + tiles de OpenStreetMap (no requiere API key):
  `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- Gráficos opcionales para el comparador: `recharts`.

### 3.3 Boceto de la interfaz

```
┌──────────────────────┬───────────────────────────────────────────┐
│ 🛵 OPTIMIZADOR       │                                           │
│ Miraflores/San Isidro│                                           │
├──────────────────────┤                                           │
│ TIPO DE RECORRIDO    │                                           │
│ (•) Entregas ( ) Dir.│            MAPA (Leaflet + OSM)           │
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
│ ALGORITMO            │                                           │
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

**Modo "Ruta directa"**: oculta destinos múltiples y "Volver al origen"; muestra un único destino y usa Dijkstra.

### 3.4 Reglas de la interfaz

| # | Regla |
|---|---|
| 1 | Modo **Ruta directa** → `POST /routes/calculate` con `algorithm: "dijkstra"`. |
| 2 | Modo **Entregas** → `POST /routes/deliveries` con `brute_force`, `backtracking` o `divide_conquer`. |
| 3 | El botón "+ Agregar destino" se deshabilita al llegar al límite: **8 / 12 / 30** según el algoritmo. Si el usuario cambia de algoritmo con más destinos que el nuevo límite, avisar o recortar. |
| 4 | Convertir la hora `"08:00"` a entero `8` para `traffic_hour` (0–23). |
| 5 | Origen y destinos se eligen **haciendo clic en el mapa** o desde la lista de lugares de ejemplo (3.8). Se envían como `{lat, lon}`. |
| 6 | Dibujar `path` como `Polyline`. Numerar los marcadores con `delivery_order` (3.6). |
| 7 | Mostrar el mensaje `detail` de los errores 400 tal cual (ya viene en español). |
| 8 | Mostrar un indicador de carga mientras se espera la respuesta (la primera petición es más lenta). |
| 9 | Si el algoritmo es `divide_conquer`, mostrar un aviso "solución aproximada" (`is_optimal === false`). |
| 10 | **Comparar todos**: lanzar las 3 peticiones con el mismo payload y mostrar tabla. Omitir `brute_force` si hay más de 8 destinos. |

### 3.5 Contrato de la API (tipos TypeScript)

```ts
export interface Coordinate { lat: number; lon: number; }

export type DeliveryAlgorithm = "brute_force" | "backtracking" | "divide_conquer";

// POST /routes/calculate
export interface RouteRequest {
  origin: Coordinate;
  destination: Coordinate;
  algorithm?: "dijkstra";        // por defecto "dijkstra"
  traffic_hour?: number;         // 0-23, por defecto 12
}

export interface RouteResponse {
  algorithm: string;
  execution_time_ms: number;
  nodos_visitados: number;
  distancia_total_m: number;     // metros reales
  weighted_cost: number;         // costo con tráfico
  path: Coordinate[];
}

// POST /routes/deliveries
export interface DeliveryRouteRequest {
  origin: Coordinate;
  destinations: Coordinate[];    // 1 a 30 (límite real según algoritmo)
  algorithm: DeliveryAlgorithm;  // obligatorio
  traffic_hour?: number;         // 0-23, por defecto 12
  return_to_origin?: boolean;    // por defecto false
}

export interface DeliveryRouteResponse {
  algorithm: string;
  execution_time_ms: number;     // solo el algoritmo TSP
  matrix_time_ms: number;        // construcción de la matriz con Dijkstra
  nodos_visitados: number;
  states_explored: number;
  branches_pruned: number;       // solo backtracking (0 en los demás)
  distancia_total_m: number;
  weighted_cost: number;
  delivery_order: number[];      // índices: 0 = origen, 1..N = destinos en el orden enviado
  is_optimal: boolean;
  path: Coordinate[];
}

// GET /routes/
export interface AlgorithmsInfo {
  message: string;
  algorithms: {
    direct_route: string[];
    deliveries: { name: DeliveryAlgorithm; max_deliveries: number; optimal: boolean }[];
  };
}
```

### 3.6 Cliente de API listo para copiar

```ts
const API = "http://localhost:8000";

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${url}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    // 400 → detail es string en español; 422 → detail es una lista (validación)
    const message =
      typeof err.detail === "string"
        ? err.detail
        : "Datos inválidos. Revisa los campos del formulario.";
    throw new Error(message);
  }
  return res.json();
}

export const calcularRuta = (req: RouteRequest) =>
  post<RouteResponse>("/routes/calculate", req);

export const calcularEntregas = (req: DeliveryRouteRequest) =>
  post<DeliveryRouteResponse>("/routes/deliveries", req);

export const obtenerAlgoritmos = () =>
  fetch(`${API}/routes/`).then((r) => r.json() as Promise<AlgorithmsInfo>);

// "08:00" -> 8
export const horaAEntero = (hhmm: string) => parseInt(hhmm.split(":")[0], 10);
```

**Numerar los marcadores** con `delivery_order`. Ejemplo: si el usuario puso 3 destinos y la respuesta trae `delivery_order = [0, 2, 3, 1]`, la visita es origen → destino 2 → destino 3 → destino 1:

```ts
// destinos[k-1] es el destino con índice k
// posición de visita (1, 2, 3...) de cada destino:
const posicion: Record<number, number> = {};
let n = 0;
res.delivery_order.forEach((i) => { if (i !== 0) posicion[i] = ++n; });
// marcador del destino k → etiqueta posicion[k]
```

Si `return_to_origin` es `true`, el último elemento de `delivery_order` es `0`: ya queda ignorado por el `if (i !== 0)`.

### 3.7 Ejemplo real de respuesta

Petición con 3 destinos (puntos de 3.8), `traffic_hour: 8`. Resultado de `backtracking`:

```json
{
  "algorithm": "backtracking",
  "execution_time_ms": 0.06,
  "matrix_time_ms": 7.46,
  "nodos_visitados": 8613,
  "states_explored": 9,
  "branches_pruned": 5,
  "distancia_total_m": 8886.49,
  "weighted_cost": 13401.35,
  "delivery_order": [0, 2, 3, 1],
  "is_optimal": true,
  "path": [ { "lat": -12.1223648, "lon": -77.0290937 }, "... 350 puntos" ]
}
```

Con `brute_force` el costo y el orden son idénticos (`states_explored: 6`, `branches_pruned: 0`). Con `divide_conquer` también coincide en este caso, pero `is_optimal` es `false`.

Ruta directa (`/routes/calculate`, depósito → San Isidro, hora 8):
`distancia_total_m: 4484.76`, `weighted_cost: 7118.80`, `path` de 210 puntos.

### 3.8 Puntos de ejemplo (para el selector de ubicaciones)

```ts
export const LUGARES = [
  { nombre: "Depósito Miraflores", lat: -12.1219, lon: -77.0297 },
  { nombre: "Entrega San Isidro",  lat: -12.0925, lon: -77.0365 },
  { nombre: "Entrega Reducto",     lat: -12.1328, lon: -77.0225 },
  { nombre: "Entrega Larcomar",    lat: -12.1317, lon: -77.0307 },
];
```

Con estos 4 puntos y `traffic_hour: 8` el resultado esperado es `delivery_order [0,2,3,1]` y `weighted_cost ≈ 13401.35`. Sirve para comprobar que el frontend está bien conectado.

### 3.9 Cosas que el frontend debe saber

- Cada coordenada se **ajusta al nodo vial más cercano**. El primer punto de `path` no coincide exactamente con el clic del usuario; es normal.
- Si dos puntos caen en el mismo nodo vial (muy cercanos entre sí) la API responde **400**: *"Dos o más ubicaciones corresponden al mismo nodo vial."* Mostrar el mensaje.
- Los costos son **dirigidos**: ir de A a B no cuesta lo mismo que de B a A (calles de un solo sentido).
- El tráfico depende de la hora y del tipo de vía. La misma ruta cuesta más en hora punta (7–10 y 17–20) que de madrugada. Probar horas 3 y 8 con los mismos puntos: el `weighted_cost` cambia (`≈ 8007` vs `≈ 13401` con el ejemplo anterior), pero `distancia_total_m` puede cambiar si el algoritmo elige otro recorrido.
- Tiempos de referencia: Dijkstra ≈ 2–3 ms; la matriz de 4 puntos ≈ 10 ms. Con 12 destinos en backtracking o 8 en fuerza bruta puede tardar más: mostrar el indicador de carga.

### 3.10 Checklist de entrega del frontend

- [ ] Mapa centrado en Miraflores/San Isidro con tiles de OSM.
- [ ] Selección de origen y destinos (clic en mapa y lista de lugares).
- [ ] Selector de modo, hora y algoritmo, con límite dinámico de destinos.
- [ ] Checkbox "Volver al origen".
- [ ] Botón "Calcular ruta" que dibuja la ruta y numera las paradas.
- [ ] Panel de resultados con: tiempo del algoritmo, tiempo de matriz, estados explorados, ramas podadas, distancia (m), costo con tráfico, ¿óptimo?, orden de entrega.
- [ ] Manejo de errores (400, 422, servidor caído) y estado de carga.
- [ ] Botón "Comparar todos" con tabla de los 3 algoritmos.
- [ ] Botón "Limpiar".

---

## 4. Endpoints (resumen)

Base URL: `http://localhost:8000` · Detalle completo en [`BACKEND_DOCS.md`](./BACKEND_DOCS.md)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Mensaje de bienvenida |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/routes/` | Algoritmos disponibles con sus límites |
| POST | `/routes/calculate` | Ruta punto a punto (solo `dijkstra`) |
| POST | `/routes/deliveries` | Orden óptimo de entregas (TSP) |

**Errores**

| Código | Cuándo |
|---|---|
| 400 | Excede el límite de entregas, dos puntos en el mismo nodo, algoritmo no válido en `/calculate`, no hay camino. `detail` es un texto en español |
| 422 | Validación de campos (hora fuera de 0–23, `destinations` vacía o > 30, algoritmo inexistente). `detail` es una lista |
| 500 | Error interno; el traceback queda en la consola del servidor |

---

## 5. Cómo funciona el tráfico

`peso de arista = distancia_m × factor`. El factor depende de la hora y del tipo de vía:

| Franja | Factor base |
|---|---|
| 07:00–09:59 y 17:00–19:59 | 2.5 |
| 10:00–16:59 y 20:00–21:59 | 1.5 |
| Resto | 1.0 |

Sensibilidad por tipo de vía: `trunk`/`primary` 1.0, `secondary` 0.7, `tertiary` 0.5, resto 0.2.
`factor_arista = 1 + (factor_base − 1) × sensibilidad`.

---

## 6. Estructura del proyecto

```
app/
├── main.py                      # FastAPI, CORS, /, /health
├── api/routes/route_routes.py   # Endpoints /routes/*
├── schemas/route.py             # Modelos de request/response
├── services/
│   ├── route_service.py         # Ruta punto a punto + caché de grafo
│   ├── delivery_service.py      # Orquesta el TSP
│   └── cost_matrix_service.py   # Matriz de costos con Dijkstra
├── algoritmos/
│   ├── dijkstra.py
│   ├── fuerza_bruta.py
│   ├── backtracking.py
│   └── divide_venceras.py
├── graph/
│   ├── graph_loader.py          # Carga el GraphML y filtra al componente conectado
│   ├── graph_builder.py         # Pesos con tráfico y lista de adyacencia
│   └── graph_utils.py           # Nodo más cercano, distancia de ruta
└── data/graph/                  # miraflores_san_isidro.graphml + metadata
scripts/                         # Verificaciones manuales de algoritmos
tests/                           # pytest (algoritmos y API)
```

### Scripts de verificación

```bash
python -m scripts.verificar_dijkstra
python -m scripts.verificar_matriz
python -m scripts.verificar_equivalencia
```

---

## 7. Pendientes

- [ ] Frontend (sección 3).
- [ ] Script de benchmark N = 4…12 para la tabla de tiempos del informe.
- [ ] Ampliar CORS al dominio del frontend desplegado.
- [ ] UFDS y Held-Karp (siguiente entrega).

---

## 8. Equipo

Proyecto del curso de Complejidad Algorítmica.