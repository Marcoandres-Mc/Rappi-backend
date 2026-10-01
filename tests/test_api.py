"""
Tests de integración de la API con el grafo real.
La primera ejecución tarda unos segundos (carga el GraphML).
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

DEPOSITO = {"lat": -12.1219, "lon": -77.0297}
SAN_ISIDRO = {"lat": -12.0925, "lon": -77.0365}
REDUCTO = {"lat": -12.1328, "lon": -77.0225}
LARCOMAR = {"lat": -12.1317, "lon": -77.0307}
DESTINOS = [SAN_ISIDRO, REDUCTO, LARCOMAR]


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def deliveries(client, algorithm, destinos=DESTINOS, **extra):
    payload = {
        "origin": DEPOSITO,
        "destinations": destinos,
        "algorithm": algorithm,
        "traffic_hour": 8,
        **extra,
    }
    return client.post("/routes/deliveries", json=payload)


# ---------- básicos ----------

def test_root_y_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_lista_de_algoritmos(client):
    body = client.get("/routes/").json()
    assert body["algorithms"]["direct_route"] == ["dijkstra"]
    nombres = {a["name"] for a in body["algorithms"]["deliveries"]}
    assert nombres == {"brute_force", "backtracking", "divide_conquer"}


# ---------- /routes/calculate ----------

def test_calculate_dijkstra(client):
    response = client.post("/routes/calculate", json={
        "origin": DEPOSITO,
        "destination": SAN_ISIDRO,
        "algorithm": "dijkstra",
        "traffic_hour": 8,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["algorithm"] == "dijkstra"
    assert len(body["path"]) >= 2
    assert body["distancia_total_m"] > 0
    assert body["distancia_total_m"] <= body["weighted_cost"] <= body["distancia_total_m"] * 2.5 + 1e-6


def test_calculate_en_hora_punta_cuesta_mas_que_en_hora_valle(client):
    def costo(hour):
        return client.post("/routes/calculate", json={
            "origin": DEPOSITO, "destination": SAN_ISIDRO,
            "algorithm": "dijkstra", "traffic_hour": hour,
        }).json()["weighted_cost"]

    assert costo(8) > costo(3)


def test_calculate_rechaza_otros_algoritmos(client):
    response = client.post("/routes/calculate", json={
        "origin": DEPOSITO, "destination": SAN_ISIDRO,
        "algorithm": "backtracking",
    })
    assert response.status_code == 400


def test_calculate_hora_invalida(client):
    response = client.post("/routes/calculate", json={
        "origin": DEPOSITO, "destination": SAN_ISIDRO, "traffic_hour": 24,
    })
    assert response.status_code == 422


# ---------- /routes/deliveries ----------

@pytest.mark.parametrize("algorithm", ["brute_force", "backtracking", "divide_conquer"])
def test_deliveries_estructura_de_respuesta(client, algorithm):
    response = deliveries(client, algorithm)
    assert response.status_code == 200
    body = response.json()
    assert body["algorithm"] == algorithm
    assert body["delivery_order"][0] == 0
    assert sorted(body["delivery_order"]) == [0, 1, 2, 3]
    assert len(body["path"]) >= 2
    assert body["execution_time_ms"] >= 0
    assert body["matrix_time_ms"] >= 0


def test_fuerza_bruta_y_backtracking_dan_el_mismo_costo(client):
    brute = deliveries(client, "brute_force").json()
    back = deliveries(client, "backtracking").json()
    assert back["weighted_cost"] == pytest.approx(brute["weighted_cost"])
    assert brute["is_optimal"] is True
    assert back["is_optimal"] is True


def test_divide_venceras_no_es_mejor_que_el_optimo(client):
    optimo = deliveries(client, "backtracking").json()
    dc = deliveries(client, "divide_conquer").json()
    assert dc["weighted_cost"] >= optimo["weighted_cost"] - 1e-6
    assert dc["is_optimal"] is False


def test_return_to_origin_termina_en_el_deposito(client):
    body = deliveries(client, "backtracking", return_to_origin=True).json()
    assert body["delivery_order"][0] == 0
    assert body["delivery_order"][-1] == 0


def test_limite_de_fuerza_bruta(client):
    nueve = [{"lat": -12.10 - i * 0.003, "lon": -77.03 + i * 0.002} for i in range(9)]
    response = deliveries(client, "brute_force", destinos=nueve)
    assert response.status_code == 400
    assert "máximo" in response.json()["detail"]


def test_destino_en_el_mismo_nodo_que_el_origen(client):
    response = deliveries(client, "backtracking", destinos=[DEPOSITO])
    assert response.status_code == 400


def test_sin_destinos_o_demasiados(client):
    assert deliveries(client, "backtracking", destinos=[]).status_code == 422
    treinta_y_uno = [{"lat": -12.1, "lon": -77.03}] * 31
    assert deliveries(client, "divide_conquer", destinos=treinta_y_uno).status_code == 422


def test_algoritmo_invalido(client):
    assert deliveries(client, "dijkstra").status_code == 422