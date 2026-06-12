import itertools
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd


DATASETS = {
    "BANC": "banc_626_edge_list.csv",
    "FAFB": "fafb_783_edge_list.csv",
    "MANC": "manc_1_2_1_edge_list.csv",
    "MAOL": "maol_1_1_edge_list.csv",
    "MCNS": "mcns_0.csv",
}


# ============================================================
# 1. FAST GRAPH LOADER (NO NETWORKX)
# ============================================================
def load_graph(csv_path, drop_self_loops=False):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")

    df = pd.read_csv(csv_path)
    if len(df.columns) < 2:
        raise ValueError(f"{csv_path} must have at least 2 columns")

    src_col, dst_col = df.columns[:2]

    adj_out = defaultdict(set)
    adj_in = defaultdict(set)
    nodes = set()

    for s, t in zip(df[src_col], df[dst_col]):
        s = str(s)
        t = str(t)
        if drop_self_loops and s == t:
            continue
        if t not in adj_out[s]:
            adj_out[s].add(t)
            adj_in[t].add(s)
        nodes.add(s)
        nodes.add(t)

    for u in nodes:
        adj_out[u]
        adj_in[u]

    return {
        "nodes": nodes,
        "adj_out": adj_out,
        "adj_in": adj_in,
        "num_nodes": len(nodes),
        "num_edges": sum(len(vs) for vs in adj_out.values()),
    }


def has_edge(G, u, v):
    return v in G["adj_out"][u]


def weakly_adjacent(G, u, v):
    return (v in G["adj_out"][u]) or (u in G["adj_out"][v])


# ============================================================
# 2. COARSER, GLOBALLY COMPARABLE STRUCTURAL COLOURS
# ============================================================
def reciprocal_degree(G, u):
    return sum(1 for v in G["adj_out"][u] if u in G["adj_out"][v])


def degree_bin(d):
    if d == 0:
        return 0
    if d == 1:
        return 1
    if d == 2:
        return 2
    if d <= 4:
        return 3
    if d <= 8:
        return 4
    if d <= 16:
        return 5
    if d <= 32:
        return 6
    if d <= 64:
        return 7
    if d <= 128:
        return 8
    return 9


def coarse_initial_signature(G, u):
    indeg = len(G["adj_in"][u])
    outdeg = len(G["adj_out"][u])
    rec = reciprocal_degree(G, u)

    return (
        degree_bin(indeg),
        degree_bin(outdeg),
        degree_bin(rec),
        1 if u in G["adj_out"][u] else 0,
    )


def directed_wl_colours_global(graphs, rounds=0):
    current = {
        name: {u: coarse_initial_signature(G, u) for u in G["nodes"]}
        for name, G in graphs.items()
    }

    for _ in range(rounds):
        raw_next = {}
        for name, G in graphs.items():
            raw_next[name] = {}
            colours = current[name]
            for u in G["nodes"]:
                in_hist = Counter(colours[v] for v in G["adj_in"][u])
                out_hist = Counter(colours[v] for v in G["adj_out"][u])

                in_summary = tuple(sorted(in_hist.items()))[:8]
                out_summary = tuple(sorted(out_hist.items()))[:8]

                raw_next[name][u] = (colours[u], in_summary, out_summary)

        all_sigs = {}
        next_id = 0
        for name in raw_next:
            for u, sig in raw_next[name].items():
                if sig not in all_sigs:
                    all_sigs[sig] = next_id
                    next_id += 1

        current = {
            name: {u: all_sigs[sig] for u, sig in raw_next[name].items()}
            for name in raw_next
        }

    return current


def invert_colours(colours):
    inv = defaultdict(list)
    for u, c in colours.items():
        inv[c].append(u)
    return inv


# ============================================================
# 3. TOLERANT VALIDITY CHECKS
# ============================================================
def triple_disagreement(e1, e2, e3):
    """
    0 if all three agree, else 1.
    """
    return 0 if (e1 == e2 == e3) else 1


def verify_mapping_tolerant(G1, G2, G3, M1, M2, M3,
                            max_total_mismatches=0,
                            max_disagreement_rate=None):
    """
    Tolerant induced directed check across all 3 graphs.

    Counts disagreement on each ordered pair (i, j):
    - 0 if all three graphs agree on edge presence
    - 1 otherwise

    Returns:
        ok, mismatches, disagreement_rate
    """
    n = len(M1)
    if n != len(M2) or n != len(M3):
        return False, None, None

    if len(set(M1)) != n or len(set(M2)) != n or len(set(M3)) != n:
        return False, None, None

    if n == 0:
        return True, 0, 0.0

    mismatches = 0
    total_pairs = n * n  # includes self-pairs

    for i in range(n):
        for j in range(n):
            e1 = has_edge(G1, M1[i], M1[j])
            e2 = has_edge(G2, M2[i], M2[j])
            e3 = has_edge(G3, M3[i], M3[j])

            mismatches += triple_disagreement(e1, e2, e3)
            if mismatches > max_total_mismatches:
                return False, mismatches, mismatches / total_pairs

    disagreement_rate = mismatches / total_pairs

    if max_disagreement_rate is not None and disagreement_rate > max_disagreement_rate:
        return False, mismatches, disagreement_rate

    return True, mismatches, disagreement_rate


def weakly_connected_subset(G, vertices):
    verts = list(vertices)
    if not verts:
        return False

    subset = set(verts)
    seen = set()
    stack = [verts[0]]

    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)

        for v in G["adj_out"][u]:
            if v in subset and v not in seen:
                stack.append(v)
        for v in G["adj_in"][u]:
            if v in subset and v not in seen:
                stack.append(v)

    return len(seen) == len(subset)


def verify_solution_triplet_tolerant(
    G1, G2, G3, M1, M2, M3,
    max_total_mismatches=0,
    max_disagreement_rate=None
):
    ok, mismatches, disagreement_rate = verify_mapping_tolerant(
        G1, G2, G3, M1, M2, M3,
        max_total_mismatches=max_total_mismatches,
        max_disagreement_rate=max_disagreement_rate
    )

    return (
        ok
        and weakly_connected_subset(G1, M1)
        and weakly_connected_subset(G2, M2)
        and weakly_connected_subset(G3, M3),
        mismatches,
        disagreement_rate
    )


# ============================================================
# 4. SHARED COLOUR ANALYSIS
# ============================================================
def shared_colour_summary(names, colours):
    n1, n2, n3 = names
    inv1 = invert_colours(colours[n1])
    inv2 = invert_colours(colours[n2])
    inv3 = invert_colours(colours[n3])

    shared = set(inv1) & set(inv2) & set(inv3)

    rows = []
    for c in shared:
        a = len(inv1[c])
        b = len(inv2[c])
        d = len(inv3[c])
        rows.append((c, a, b, d, min(a, b, d), a * b * d))

    rows.sort(key=lambda x: (x[4], x[5]))
    return rows, inv1, inv2, inv3


# ============================================================
# 5. GREEDY GROW WITH TOLERANCE
# ============================================================
def additional_mismatches_with_partial(G1, G2, G3, u, v, w, M1, M2, M3):
    """
    Count how many new disagreement units would be introduced by adding (u, v, w)
    to the existing partial match.

    Includes:
    - self-loop disagreement on (u, u) / (v, v) / (w, w)
    - new->old for each existing matched triple
    - old->new for each existing matched triple
    """
    mismatches = 0

    # self-loop of the new node
    mismatches += triple_disagreement(
        has_edge(G1, u, u),
        has_edge(G2, v, v),
        has_edge(G3, w, w)
    )

    for a, b, c in zip(M1, M2, M3):
        # new -> old
        mismatches += triple_disagreement(
            has_edge(G1, u, a),
            has_edge(G2, v, b),
            has_edge(G3, w, c)
        )
        # old -> new
        mismatches += triple_disagreement(
            has_edge(G1, a, u),
            has_edge(G2, b, v),
            has_edge(G3, c, w)
        )

    return mismatches


def connected_to_partial(G1, G2, G3, u, v, w, M1, M2, M3):
    """
    Keep this strict for now:
    require at least one already matched node such that weak adjacency agrees
    across all 3 graphs and is present.
    """
    if not M1:
        return True

    for a, b, c in zip(M1, M2, M3):
        adj1 = weakly_adjacent(G1, u, a)
        adj2 = weakly_adjacent(G2, v, b)
        adj3 = weakly_adjacent(G3, w, c)
        if adj1 == adj2 == adj3 and adj1:
            return True

    return False


def frontier_nodes(G, M, used):
    if not M:
        return set()

    out = set()
    for u in M:
        out.update(G["adj_out"][u])
        out.update(G["adj_in"][u])
    out -= used
    return out


def node_score(G, u, M):
    if not M:
        return 0
    return sum(1 for a in M if weakly_adjacent(G, u, a))


def sample_candidates(nodes, colour_map, wanted_colours, max_count):
    kept = []
    for u in nodes:
        if colour_map[u] in wanted_colours:
            kept.append(u)
            if len(kept) >= max_count:
                break
    return kept


def greedy_grow_from_seed(
    G1, G2, G3,
    colour_map1, colour_map2, colour_map3,
    inv1, inv2, inv3,
    seed_triple,
    max_total_mismatches=0,
    max_disagreement_rate=None,
    max_frontier_per_graph=40,
    max_nodes_per_colour=8,
):
    """
    Greedy tolerant grower.

    - starts from a seed triple
    - allows some disagreement budget
    - keeps connectivity strict
    - prefers candidates with strong attachment and low added mismatch cost

    Returns:
        M1, M2, M3, mismatch_count, disagreement_rate
    """
    u0, v0, w0 = seed_triple
    M1, M2, M3 = [u0], [v0], [w0]
    used1, used2, used3 = {u0}, {v0}, {w0}

    current_mismatches = triple_disagreement(
        has_edge(G1, u0, u0),
        has_edge(G2, v0, v0),
        has_edge(G3, w0, w0)
    )

    if current_mismatches > max_total_mismatches:
        return [], [], [], None, None

    current_rate = current_mismatches / 1.0
    if max_disagreement_rate is not None and current_rate > max_disagreement_rate:
        return [], [], [], None, None

    while True:
        f1 = list(frontier_nodes(G1, M1, used1))
        f2 = list(frontier_nodes(G2, M2, used2))
        f3 = list(frontier_nodes(G3, M3, used3))

        if not f1 or not f2 or not f3:
            break

        f1.sort(key=lambda x: -node_score(G1, x, M1))
        f2.sort(key=lambda x: -node_score(G2, x, M2))
        f3.sort(key=lambda x: -node_score(G3, x, M3))

        f1 = f1[:max_frontier_per_graph]
        f2 = f2[:max_frontier_per_graph]
        f3 = f3[:max_frontier_per_graph]

        c1 = {colour_map1[x] for x in f1}
        c2 = {colour_map2[x] for x in f2}
        c3 = {colour_map3[x] for x in f3}
        shared_frontier_colours = c1 & c2 & c3

        if not shared_frontier_colours:
            break

        colour_order = sorted(
            shared_frontier_colours,
            key=lambda c: (
                min(len(inv1[c]), len(inv2[c]), len(inv3[c])),
                len(inv1[c]) * len(inv2[c]) * len(inv3[c])
            )
        )

        added = False

        for colour in colour_order:
            cand1 = sample_candidates(f1, colour_map1, {colour}, max_nodes_per_colour)
            cand2 = sample_candidates(f2, colour_map2, {colour}, max_nodes_per_colour)
            cand3 = sample_candidates(f3, colour_map3, {colour}, max_nodes_per_colour)

            best_local = None
            best_key = None

            for u in cand1:
                for v in cand2:
                    for w in cand3:
                        if not connected_to_partial(G1, G2, G3, u, v, w, M1, M2, M3):
                            continue

                        add_cost = additional_mismatches_with_partial(
                            G1, G2, G3, u, v, w, M1, M2, M3
                        )

                        new_total_mismatches = current_mismatches + add_cost
                        if new_total_mismatches > max_total_mismatches:
                            continue

                        new_n = len(M1) + 1
                        new_rate = new_total_mismatches / (new_n * new_n)
                        if max_disagreement_rate is not None and new_rate > max_disagreement_rate:
                            continue

                        struct_score = (
                            node_score(G1, u, M1)
                            + node_score(G2, v, M2)
                            + node_score(G3, w, M3)
                        )

                        # Prefer:
                        # 1) more structurally attached nodes
                        # 2) lower added mismatch cost
                        # 3) lower total mismatch afterwards
                        key = (struct_score, -add_cost, -new_total_mismatches)

                        if best_key is None or key > best_key:
                            best_key = key
                            best_local = (u, v, w, add_cost)

            if best_local is not None:
                u, v, w, add_cost = best_local
                M1.append(u)
                M2.append(v)
                M3.append(w)
                used1.add(u)
                used2.add(v)
                used3.add(w)
                current_mismatches += add_cost
                added = True
                break

        if not added:
            break

    final_ok, final_mismatches, final_rate = verify_mapping_tolerant(
        G1, G2, G3,
        M1, M2, M3,
        max_total_mismatches=max_total_mismatches,
        max_disagreement_rate=max_disagreement_rate
    )

    if not final_ok:
        return [], [], [], None, None

    return M1, M2, M3, final_mismatches, final_rate


def search_one_triple(
    triple_names,
    graphs,
    colours,
    max_total_mismatches=0,
    max_disagreement_rate=None,
    max_seed_colours=30,
    max_seed_nodes_per_colour=6,
    max_frontier_per_graph=40,
    max_nodes_per_colour=8
):
    n1, n2, n3 = triple_names
    G1, G2, G3 = graphs[n1], graphs[n2], graphs[n3]
    colour_map1, colour_map2, colour_map3 = colours[n1], colours[n2], colours[n3]

    rows, inv1, inv2, inv3 = shared_colour_summary(triple_names, colours)

    if not rows:
        return [], [], [], None, None

    rows = rows[:max_seed_colours]

    best = {
        "M1": [],
        "M2": [],
        "M3": [],
        "mismatches": None,
        "rate": None,
    }

    for colour, a, b, d, mn, prod in rows:
        seeds1 = inv1[colour][:max_seed_nodes_per_colour]
        seeds2 = inv2[colour][:max_seed_nodes_per_colour]
        seeds3 = inv3[colour][:max_seed_nodes_per_colour]

        for u in seeds1:
            for v in seeds2:
                for w in seeds3:
                    M1, M2, M3, mismatches, rate = greedy_grow_from_seed(
                        G1, G2, G3,
                        colour_map1, colour_map2, colour_map3,
                        inv1, inv2, inv3,
                        (u, v, w),
                        max_total_mismatches=max_total_mismatches,
                        max_disagreement_rate=max_disagreement_rate,
                        max_frontier_per_graph=max_frontier_per_graph,
                        max_nodes_per_colour=max_nodes_per_colour
                    )

                    if not M1:
                        continue

                    ok, final_mismatches, final_rate = verify_solution_triplet_tolerant(
                        G1, G2, G3,
                        M1, M2, M3,
                        max_total_mismatches=max_total_mismatches,
                        max_disagreement_rate=max_disagreement_rate
                    )

                    if not ok:
                        continue

                    better = False
                    if len(M1) > len(best["M1"]):
                        better = True
                    elif len(M1) == len(best["M1"]) and best["mismatches"] is not None:
                        if final_mismatches < best["mismatches"]:
                            better = True
                        elif final_mismatches == best["mismatches"] and final_rate < best["rate"]:
                            better = True
                    elif len(M1) == len(best["M1"]) and best["mismatches"] is None:
                        better = True

                    if better:
                        best["M1"] = M1[:]
                        best["M2"] = M2[:]
                        best["M3"] = M3[:]
                        best["mismatches"] = final_mismatches
                        best["rate"] = final_rate
                        print(
                            f"  new best for {triple_names}: "
                            f"size={len(M1)}, mismatches={final_mismatches}, rate={final_rate:.4f}"
                        )

    return best["M1"], best["M2"], best["M3"], best["mismatches"], best["rate"]


# ============================================================
# 6. SAVE RESULT
# ============================================================
def save_solution_csv(triple_names, M1, M2, M3, out_csv="best_solution.csv"):
    n1, n2, n3 = triple_names
    df = pd.DataFrame({
        n1: M1,
        n2: M2,
        n3: M3,
    })
    df.to_csv(out_csv, index=False)
    print(f"Saved solution to: {out_csv}")


# ============================================================
# 7. MAIN
# ============================================================
def main():
    print("Loading graphs...")
    graphs = {}
    for name, path in DATASETS.items():
        G = load_graph(path)
        graphs[name] = G
        print(f"{name}: |V|={G['num_nodes']:,}, |E|={G['num_edges']:,}")

    print("\nComputing globally consistent coarse colours...")
    colours = directed_wl_colours_global(graphs, rounds=0)

    for name in DATASETS:
        num_colours = len(set(colours[name].values()))
        print(f"{name}: {num_colours:,} colour classes")

    print("\nShared-colour summary for each dataset triple:")
    triple_stats = []

    for triple in itertools.combinations(DATASETS.keys(), 3):
        rows, inv1, inv2, inv3 = shared_colour_summary(triple, colours)
        total_shared_colours = len(rows)
        max_possible_from_colours = sum(r[4] for r in rows)

        print(f"\nTriple {triple}:")
        print(f"  shared colour classes: {total_shared_colours:,}")
        print(f"  colour-count upper bound: {max_possible_from_colours:,}")

        if rows:
            print("  first 10 rare shared colours:")
            for r in rows[:10]:
                c, a, b, d, mn, prod = r
                print(f"    colour={c}, counts=({a},{b},{d}), min={mn}, product={prod}")
        else:
            print("  no shared colours at this colour depth")

        triple_stats.append((triple, total_shared_colours, max_possible_from_colours))

    triple_stats.sort(key=lambda x: (-x[2], -x[1]))

    # ========================================================
    # TOLERANCE SETTINGS
    # ========================================================
    # Set max_total_mismatches=0 for exact behaviour.
    max_total_mismatches = 10

    # Optional rate cap:
    # e.g. 0.05 means <= 5% of ordered pairs may disagree.
    # Set to None to disable.
    max_disagreement_rate = 0.05

    print("\nSearching most promising triples...")
    print(f"Tolerance: max_total_mismatches={max_total_mismatches}, "
          f"max_disagreement_rate={max_disagreement_rate}")

    best_global = {
        "triple": None,
        "M1": [],
        "M2": [],
        "M3": [],
        "mismatches": None,
        "rate": None,
    }

    for triple, shared_cnt, upper in triple_stats:
        if shared_cnt == 0:
            continue

        print(f"\n=== Searching triple {triple} ===")
        M1, M2, M3, mismatches, rate = search_one_triple(
            triple,
            graphs,
            colours,
            max_total_mismatches=max_total_mismatches,
            max_disagreement_rate=max_disagreement_rate,
            max_seed_colours=40,
            max_seed_nodes_per_colour=6,
            max_frontier_per_graph=50,
            max_nodes_per_colour=10
        )

        print(f"  best found size = {len(M1)}")
        if mismatches is not None:
            print(f"  mismatches      = {mismatches}")
            print(f"  disagreement    = {rate:.4f}")

        better = False
        if len(M1) > len(best_global["M1"]):
            better = True
        elif len(M1) == len(best_global["M1"]) and best_global["mismatches"] is not None:
            if mismatches is not None and mismatches < best_global["mismatches"]:
                better = True
            elif (
                mismatches is not None
                and mismatches == best_global["mismatches"]
                and rate is not None
                and best_global["rate"] is not None
                and rate < best_global["rate"]
            ):
                better = True
        elif len(M1) == len(best_global["M1"]) and best_global["mismatches"] is None:
            if M1:
                better = True

        if better:
            best_global["triple"] = triple
            best_global["M1"] = M1
            best_global["M2"] = M2
            best_global["M3"] = M3
            best_global["mismatches"] = mismatches
            best_global["rate"] = rate

    print("\n======================")
    print("OVERALL BEST")
    print("======================")
    print("Triple      :", best_global["triple"])
    print("Size        :", len(best_global["M1"]))
    print("Mismatches  :", best_global["mismatches"])
    print("DisagreeRate:", best_global["rate"])

    if best_global["triple"] is not None and len(best_global["M1"]) > 0:
        save_solution_csv(
            best_global["triple"],
            best_global["M1"],
            best_global["M2"],
            best_global["M3"],
            out_csv="best_solution.csv"
        )
    else:
        print("No non-empty tolerant solution found with this heuristic search.")


if __name__ == "__main__":
    main()
