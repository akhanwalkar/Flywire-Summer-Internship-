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
