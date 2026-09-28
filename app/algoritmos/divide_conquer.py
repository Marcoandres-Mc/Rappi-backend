def divide_conquer(graph, origin, destination):
    """
    Divide el problema en dos zonas y resuelve
    cada parte de forma independiente.

    Esta es una versión inicial que luego
    conectaremos con el grafo real.
    """

    nodes = list(graph.nodes)

    if len(nodes) <= 1:
        return {
            "path": nodes,
            "cost": 0
        }

    middle = len(nodes) // 2

    zone_a = nodes[:middle]
    zone_b = nodes[middle:]

    result_a = solve_zone(graph, zone_a)
    result_b = solve_zone(graph, zone_b)

    return combine_results(result_a, result_b)


def solve_zone(graph, zone):
    """
    Resuelve una subzona del grafo.
    """

    return {
        "nodes": zone,
        "cost": 0
    }


def combine_results(result_a, result_b):
    """
    Combina las soluciones obtenidas
    de las dos subzonas.
    """

    return {
        "nodes": result_a["nodes"] + result_b["nodes"],
        "cost": result_a["cost"] + result_b["cost"]
    }