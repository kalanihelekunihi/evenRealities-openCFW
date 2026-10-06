# P2-15953 independent review

Fresh static replay passes over the selected 2,446-byte envelope: 959 unique instruction rows, 106 direct calls to 30 targets, all direct branch targets at decoded instruction starts, and one saved-context return. Call continuation edges remain conditional on each child returning. The raw Ghidra metadata, selected map inputs, literal pins, and consolidated draft are hash-bound.

This is a static CFG consistency check only. It does not establish path feasibility, complete function boundaries, alternate-entry absence, child behavior, semantic closure, or the cause of the original Ghidra error. Status remains partial and unaccepted.
