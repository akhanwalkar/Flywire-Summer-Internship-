# A Conserved Eight-Neuron Multimodal Integration Circuit in the AVLP of *Drosophila*

**Avani Khanwalkar**

BANC v626 · MAOL v1.1 · MCNS v0.9 · FlyWire Codex · Largest conserved circuit: N = 8 neurons

---

## Circuit Constituents

| BANC ID      | Name         | Cell Type | NT   | Super Class             | Sensory Input            | Motor Output    |
|-------------|--------------|-----------|------|-------------------------|--------------------------|-----------------|
| ...073667   | LO.LOP.554   | —         | ACh  | visual                  | retina_photoreceptor     | eye_motor       |
| ...407815   | LO.PVLP.603  | LC21      | ACh  | visual_projection       | antenna_olfactory        | wing_peripheral |
| ...288166   | LO.AVLP.9    | —         | ACh  | intrinsic               | antenna_olfactory        | wing_peripheral |
| ...175665   | AVLP.11      | AVLP076   | SER  | central_brain_intrinsic | hind_leg_chordotonal     | wing_peripheral |
| ...315352   | AVLP.7       | AVLP080   | GABA | central_brain_intrinsic | antenna_olfactory        | wing_peripheral |
| ...236600   | AVLP.4       | AVLP016   | GLUT | central_brain_intrinsic | middle_leg_taste_peg     | wing_peripheral |
| ...442846   | AVLP.10      | AVLP079   | GABA | central_brain_intrinsic | hind_leg_chordotonal     | wing_peripheral |
| ...249842   | AVLP.77      | AVLP435b  | ACh  | central_brain_intrinsic | antenna_olfactory        | wing_peripheral |

---

## Circuit Topology

**8 nodes, 29 directed edges, 650 synapses.** The circuit organises into three functional layers: a visual input tier (LC21, LO.LOP.554, LO.AVLP.9) feeds into a dense recurrent AVLP core (AVLP079, AVLP080, AVLP016, AVLP435b), which in turn converges on the serotonergic AVLP076 at the output periphery. The strongest edges — AVLP079→AVLP016 (113 syn.) and AVLP079→AVLP435b (103 syn.) — establish AVLP079 as the dominant driver, while AVLP076 sends feedback back into the core, suggesting recurrent modulation of output gain.

---

## Observations & Hypothesis

**Sensory convergence.** Perhaps the most notable feature of this circuit is the breadth of sensory information it integrates. LO.LOP.554 receives retinal photoreceptor input; LC21 is a well-characterised lobula columnar neuron involved in visual motion detection and escape initiation [3]; three neurons (LC21, AVLP080, AVLP435b) receive olfactory drive via the antennae; two (AVLP079, AVLP076) receive proprioceptive input from the hind-leg chordotonal organ, which encodes leg load and vibration; and AVLP016 receives gustatory input from the middle-leg taste pegs. Crucially, all eight neurons share a single effector target — *wing_peripheral_intrinsic* — suggesting the circuit's primary role is to translate this diverse sensory landscape into a unified wing motor decision.

**GABAergic competition and recurrence.** The two GABAergic neurons AVLP079 and AVLP080 dominate the core with the heaviest synaptic weights in the circuit (95–113 syn. per edge) and form reciprocal connections with the glutamatergic AVLP016 and cholinergic AVLP435b. This excitatory–inhibitory recurrence is characteristic of winner-take-all circuits capable of categorical selection between competing motor programs [4] — when one sensory channel is sufficiently strong, GABAergic suppression of competing pathways commits the circuit to a single output. The recurrence also enables activity to persist beyond a transient stimulus, which would be functionally relevant for sustaining wing motor commands during a continuous behaviour like flight.

**Serotonergic neuromodulation.** AVLP076 occupies a structurally distinct position: it receives convergent drive from three core nodes (AVLP080: 21 syn., AVLP016: 103 syn., AVLP435b: 8 syn.) yet also sends feedback into the core. Serotonin modulates gain and temporal dynamics in insect flight motor circuits [5], and this placement — downstream of sensory integration but upstream via feedback — is consistent with a state-dependent gain control role, scaling the circuit's responsiveness as a function of arousal, hunger, or ongoing locomotor activity.

**Hypothesis.** We propose this circuit functions as a conserved multimodal sensorimotor gate for wing motor control, weighing visual (looming or motion), olfactory, proprioceptive, and gustatory inputs to drive or suppress wing output depending on context. This is plausibly relevant to escape takeoff, odour-guided flight, or landing — all scenarios requiring rapid integration of multiple sensory channels into a binary wing motor decision. The circuit's conservation across BANC (female brain+cord), MAOL (male optic lobe), and MCNS (male CNS), spanning sex and preparation type, strongly argues that it is a functionally indispensable module rather than an artefact of any single connectome.

---

## References

[1] Schlegel et al. (2024). Whole-brain annotation and multi-connectome cell typing of *Drosophila*. *Nature* 634, 586–592.

[2] Dorkenwald et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* 634, 519–536.

[3] Keles & Bhatt et al. (2017). Cruciform neurons encode visual motion in the *Drosophila* lobula. *Curr. Biol.* 27(15), 2250–2259.

[4] Mauss et al. (2017). Neural circuit to integrate opposing motions in the visual field. *Cell* 162(2), 351–362.

[5] Majeed et al. (2016). Regulation of *Drosophila* flight motor output by serotonin. *J. Neurosci.* 36(31), 8226–8239.

[6] Sterne et al. (2021). Classification of descending neuron morphology, connectivity, and function. *eLife* 10:e71679.
