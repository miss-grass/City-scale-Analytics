import networkx as nx
import entwiner as ent
import math


# An edge generator - takes input edges and creates transformed (and lower-memory) ones
def edge_gen(G):
    for u, v, d in G.edges_iter():
        yield u, v, cost_fun(d)


BASE_SPEED = 0.6
IDEAL_INCLINE = -0.0087
DIVISOR = 5


def find_k(g, m, n):
    return math.log(n) / abs(g - m)


k_up = find_k(0.08, IDEAL_INCLINE, DIVISOR)
k_down = find_k(0.1, IDEAL_INCLINE, DIVISOR)


def cost_fun(d, ideal_incline=IDEAL_INCLINE, base=BASE_SPEED):
    def tobler(grade, k=3.5, m=-0.0087, base=0.6):
        return base * math.exp(-k * abs(grade - m))

    if "curbramps" in d:
        if d["curbramps"] == 0:
            return None

    distance = d.get("length", 0)  # FIXME: no paths should have length zero

    if "incline" in d:
        incline = d["incline"] / 1000.
        if incline > ideal_incline:
            k = k_up
        else:
            k = k_down
        speed = tobler(incline, k=k, m=ideal_incline, base=base)
    else:
        speed = base

    time = distance / speed
    d["time"] = time

    if "art" in d:
        art = str(d["art"]).strip("[]\'").split(",")
        d["art_num"] = len(art)
    else:
        d["art_num"] = 0

    return time


# Walksheds:
def walkshed(G, node, max_cost=600, sum_columns=["length", "art_num"]):
    # Use Dijkstra's method to get the below-400 walkshed paths
    distances, paths = nx.algorithms.shortest_paths.single_source_dijkstra(
        G,
        node,
        weight="time",
        cutoff=max_cost
    )

    # We need to do two things:
    # 1) Grab any additional reachable fringe edges. The user cannot traverse them in their
    #    entirety, but if they are traversible at all we still want to sum up their attributes
    #    in the walkshed. In particular, we're using "length" in this example. It is not obvious
    #    how we should assign "partial" data to these fringes, we will will just add the fraction
    #    to get to max_cost.
    #
    # 2) Sum up the attributes of the walkshed, assigning partial data on the fringes proportional
    #    to the fraction of marginal cost / edge cost.

    # Enumerate the fringes along with their fractional costs.
    fringe_edges = {}
    for n, distance in distances.items():
        for successor in G.successors(n):
            if successor not in distances:
                cost = G[n][successor]["time"]
                if cost is not None:
                    marginal_cost = max_cost - distance
                    fraction = marginal_cost / cost
                    fringe_edges[(n, successor)] = fraction

    # Create the sum total of every attribute in sum_columns
    edges = []
    for destination, path in paths.items():
        for node1, node2 in zip(path, path[1:]):
            edges.append((node1, node2))

    # All unique edges for which to sum attributes
    edges = set(edges)

    sums = {k: 0 for k in sum_columns}
    for n1, n2 in edges:
        d = G[n1][n2]
        for column in sum_columns:
            sums[column] += d.get(column, 0)

    # TODO: add in fringes!
    for (n1, n2), fraction in fringe_edges.items():
        d = G[n1][n2]
        for column in sum_columns:
            sums[column] += d.get(column, 0) * fraction

    return sums, list(zip(*paths))[1]


def main():
    G = ent.graphs.digraphdb.digraphdb('raw data/sidewalks.db')
    edge_gen(G)
    sums, paths = walkshed(G, "-122.3129257, 47.5567878")
    print(sums["art_num"])
    print(sums["length"])


if __name__ == "__main__":
    main()
