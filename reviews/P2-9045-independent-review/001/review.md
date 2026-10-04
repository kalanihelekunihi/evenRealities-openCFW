# P2-9045 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 36 original-byte cases over lengths 0, 1, 65535, 65536, and 65537, nesting/mask variants, and disjoint queue/node regions.
- Independent low-16-bit count expectations matched; list state, preserved registers, return residue, mask, SP, and PC checks passed.

Limitations:

- The replay uses short acyclic synthetic queues; it does not test cycles, malformed pointers, concurrent mutation, or physical lock/preemption semantics.
