# Flywire-Summer-Internship-
This is by Avani Khanwalkar for the flywire summer intership qualification challenge about neuron connectomics in flybrains
Multiple approaches were used to get to the final subgraph. This still isnt the most optimal number but is one of the lower bounds.  
Having to take into consideration the time complexity and running time.  
This is essentially a Maximum common induced subgraph problem (NP-hard)
Challenges:
combinatorial explosion,
noisy biological data,
missing edges,
structural variation

Evolution of Our Approach:
We did not arrive at the final method immediately — we iteratively improved it.

**Phase 1 — Exact Matching (FAILED)**
Idea:
Require perfect structural equality:
Pythone1 == e2 == e3Show more lines  
Result:
-Almost no matches found  
-Extremely brittle  
Insight:
  Real connectomes are noisy — exact matching is unrealistic.

**Phase 2 — WL Colouring + Exact Matching**
Idea:
  Use Weisfeiler–Lehman (WL) colouring to group similar nodes.
each node gets a structural signature,
match only nodes with same colour  
Result:
-reduced search space  
-still too strict — matches were tiny  
Insight:  
WL helps prune, but strict equality still kills growth.

**Phase 3 — Global Colouring Across Graphs**
Improvement->
Instead of colouring graphs independently:
colour all graphs jointly,
ensure colours are directly comparable  
Result:  
-more shared candidate nodes  
-better seeding

**Phase 4 — Greedy Seed-and-Grow (Exact)**
Idea:  
pick seed triple (u, v, w),
grow match outward,
enforce exact consistency at each step  
Result:
-larger structures  
-still stops early due to tiny mismatches  
Insight:
Small local disagreements block global structure discovery


**Phase 5 — TOLERANT MATCHING (BREAKTHROUGH)**
Key change:
Allow controlled structural disagreement  
Instead of:
Pythone1 == e2 == e3Show more lines  
we define:
Pythondisagreement = 0 or 1Show more lines
and track total mismatch.

Disagreement Rate
_disagreement rate = mismatched pairs/n^2_  
Interpretation:
0.00 → perfect match,
0.04 → 96% agreement   
higher → noisier  
Intuition:
We compare all node pairs:
i → j,
across all graphs.
If graphs disagree → count 1  

Why this works->
This allows:
missing edges,
noisy data,
slight biological differences ,while still enforcing global structure  


MAIN TECHNICAL APPROACH  
# Connectome Consensus Motif Discovery

## Overview

This project identifies **large, weakly connected directed motifs shared across multiple connectome datasets** (FlyWire).  

Rather than solving the exact maximum common induced subgraph problem (which is computationally intractable at this scale), this implementation uses a **coarse-structured, tolerance-aware heuristic search** that balances:

- motif **size**
- structural **consistency**
- computational **feasibility**

The method searches for **node correspondences across three datasets at a time** and returns the largest valid circuit found.

---

## Datasets

The following directed connectomes are used:

- BANC
- FAFB
- MANC
- MAOL
- MCNS

Each dataset is represented as a directed graph:
- nodes = neurons  
- edges = directed synaptic connections  

---

## High-Level Approach

The pipeline consists of five main stages:

1. **Graph construction**
2. **Coarse structural colouring**
3. **Shared-colour filtering**
4. **Greedy motif growth**
5. **Tolerant validation and selection**

---

## 1. Graph Representation

Each dataset is loaded into a lightweight adjacency structure:

- `adj_out[u]` = outgoing neighbours  
- `adj_in[u]` = incoming neighbours  

This avoids heavy graph libraries and enables fast edge lookups.

---

## 2. Coarse Structural Colouring

Each neuron is assigned a **coarse structural signature** based on:

- binned in-degree  
- binned out-degree  
- reciprocal degree  
- self-loop indicator  

These features are discretised into bins (log-scale) to ensure:

- structural similarity is preserved  
- cross-dataset overlap is maintained  

An optional Weisfeiler–Lehman refinement step can be applied, but is typically disabled to avoid over-fragmentation.

---

## 3. Shared Colour Filtering

For every triple of datasets:

- identify colour classes present in all three graphs  
- compute how many neurons belong to each class  
- prioritise **rare shared colours** for seeding  

This step dramatically reduces the search space and provides a rough upper bound on motif size.

---

## 4. Greedy Motif Growth

The core search algorithm builds a motif incrementally.

### Seed selection
- choose triples of nodes (one per dataset) with matching colour

### Iterative expansion
At each step:

1. Compute the **frontier** (neighbours of current motif)
2. Restrict candidates to nodes with shared colours
3. Evaluate candidate triples using:
   - structural connectivity to current motif
   - mismatch cost introduced
4. Select the **best candidate** based on:
   - strong attachment (connectivity)
   - low additional disagreement
   - minimal total mismatches

### Connectivity constraint
- every new node must connect (weakly) to the existing motif in a consistent way across all datasets

---

## 5. Tolerant Validation

Instead of requiring exact isomorphism during growth, the algorithm allows **controlled disagreement**.

### Disagreement definition
For each ordered node pair `(i, j)`:
- compare edge presence across all three graphs
- count 1 mismatch if they do not agree exactly

### Constraints
A candidate motif is accepted if:

- total mismatches ≤ `max_total_mismatches`
- disagreement rate ≤ `max_disagreement_rate`
- node mapping is one-to-one across datasets
- motif is **weakly connected** in all three graphs

---

## Objective Function

Solutions are ranked using:

1. **Motif size (primary objective)**
2. **Total mismatches**
3. **Disagreement rate**

---

## Output

The best discovered motif is saved as: network.csv  

**Final Algorithm:  **
1. Load graphs
adjacency sets
fast edge lookup  

2. Compute coarse structural colours->
Features:
indegree
outdegree
reciprocal edges
self-loops  

3. WL-style refinement (1 round):
aggregate neighbour colours
build structural fingerprints  

4. Shared-colour filtering:
Only consider nodes appearing in all graphs  

5. Seed selection:
Start from rare shared colours  

6. Greedy growth->
At each step:
expand along frontier
enforce connectivity
minimise disagreement  


7. Scoring function->
We prioritise:
1. low new mismatch  
2. low total mismatch  
3. low disagreement rate  
4. strong connectivity  


8. Pruning
Reject candidates if:

too many new mismatches,
total mismatch > threshold,
disagreement rate too high  


**Results**
Final result:
disagreement rate ≈ 0.04  
meaning:
96% structural agreement,
large connected shared subgraph,
robust to noise  

**Biological Meaning:**  
This suggests: strong conserved connectivity patterns
mismatches likely due to:  
-measurement noise
-missing edges
-biological variability

Abstract  
We study the problem of identifying conserved structural patterns across multiple connectomes by formulating it as a tolerant common subgraph discovery task. Each connectome is represented as a directed graph, where nodes correspond to neurons and edges to synaptic connections. We aim to identify a connected induced subgraph that is shared across multiple datasets while allowing for limited structural disagreement to account for biological variability and measurement noise.
Our approach combines coarse structural node representations with a Weisfeiler–Lehman-style colouring scheme to generate globally comparable node signatures. These are used to restrict the search space and identify candidate correspondences across graphs. We then employ a greedy seed-and-grow strategy, expanding partial matches along graph frontiers while enforcing connectivity constraints.
Unlike traditional exact graph matching methods, we introduce a tolerance mechanism that quantifies disagreement across edge relations and optimises for both size and structural consistency. This enables the discovery of significantly larger shared substructures in noisy graphs. Experiments on connectome datasets demonstrate that our method identifies large connected subgraphs with approximately 96% structural agreement, highlighting strong conservation of connectivity patterns across datasets.
