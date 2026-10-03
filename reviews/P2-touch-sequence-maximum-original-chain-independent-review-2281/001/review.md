# Independent review 2281

**Result:** PASS_SCOPED.

Isolated replay regenerated all 36 fixtures. Source, body [0x69C4,0x6A6C), literal span [0x6A6C,0x6A80), and artifact hashes match. All sequence and arithmetic children execute original instructions without interception. The base clock value 1,000,000 produces initial poll budget 350; the modeled-ready path reads status once, and the modeled timeout path reads 351 times. Exact setup scratch and poll arguments, maximum updates, sticky timeout result, and R4–R11/SP assertions pass. The maximum helper rereads row count and continues traversing after timeout as decoded.

**Limits:** The status/readiness behavior is supplied by RAM hooks, not hardware. The composition captures original child writes but does not fully assert those ledgers here; component packets carry that evidence. Only selected row counts, strides, patterns, and outcomes are tested. Physical timing, aliasing, and concurrent mutation remain unresolved; no canonical admission.
