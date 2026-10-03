# Independent review 2911

**PASS_SCOPED**; `accepted` remains false.

The source image hash and both body digests (predicate plus query leaf) match inventory/receipt; artifact hashes match. Independent isolated original-instruction replay passed all 1,580 fixtures. The corpus covers all 16 scan slots crossed with 12 kind values, active/selected bits and PRIMASK; 28 query-enabled/mode cases; and 16 early-input guard cases, including top-two-bits-only input that does not satisfy the low-30-bit guard. The assertion oracle and execution agree on output flag byte, query call selection, incoming-R7 return, preserved high-register set, SP, PRIMASK and stop PC. MMIO read events are retained as traces, not asserted against a complete read oracle; the scan’s expected predicate uses stable fixture values. No interception is used. Changing reads, arbitrary aliasing, exception behavior, physical hardware, full flags, and caller ownership remain unresolved. accepted:false.

Candidate receipt SHA-256: `d08392eb3e753e68b863d1bae2ed9c2bcc5f0db7aed010e51e02936ded8ef268`.
