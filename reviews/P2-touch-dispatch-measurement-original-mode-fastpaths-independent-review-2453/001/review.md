# Independent review 2453

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-dispatch-measurement-original-mode-fastpaths-2452/001`. Receipt SHA-256 `0c68e7c1265a4ac8d6e9c02858c467b1e0d4fb29ede7f17a622903886b104e9b`; all four declared evidence-file hashes match. Each of the 12 body ranges rehashes against the pinned 34,432-byte image `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87`.

I replayed the supplied harness into an isolated sibling output directory with only the output path changed. It passed all 64 cases. The Cartesian inputs cover dispatcher index 0/2, normal/type-7 layout, start 0/1, count 1/3, and four paired readiness/poll patterns. The original dispatcher and measurement chain, including 6AC0, runs without firmware-function interceptions. Assertions check the 6AC0 request arguments and optional cfg+115 clear, distinction between old-mode equality (2) and invalid old modes (3/255), preservation or replacement of status by poll timeout 256, sample-gated item effects, the ordered memory ledger, division/poll/delay observations, and R4–R11/SP.

The disassembly spans include the executed dispatcher, measurement, budget, poll, setup/reset, status wait, delay adapters/leaves, and divider entries. The mode-2 equal path does not clear cfg+115; modes 3 and 255 clear it and do not store a replacement mode. A nonzero retained mode status suppresses sample writes, while timeout replaces it with 256. These statements are supported by the harness assertions for the selected fixtures.

**Limits:** Old-mode values are paired with four readiness patterns rather than fully crossed; request 4 and valid prior modes that transition on request 2 are not covered. Port setup and deeper config paths remain outside this packet. Peripheral/status values are modeled, so physical register behavior and timing are not established. This is bounded private execution evidence, not canonical admission or full-chain completeness; accepted:false.
