# Independent review: bounded Ambiq MSPI lifecycle subset

## Result

The lifecycle subset matches the authenticated original disable/deinitialize behavior across the saved 102-case linked-original comparison. No critical implementation or verifier defect found in the current snapshot. One documentation inconsistency remains: the component README still describes the earlier four-function interrupt-only scope, even though the component now includes six upstream function texts and lifecycle evidence.

## Behavioral and verifier checks

- `am_hal_mspi_disable` and `am_hal_mspi_deinitialize` are exact function-text matches to the locally cached pinned Ambiq 5.1.0 source. Their excerpt hashes are now present in `SOURCE_PROVENANCE.json` with function-to-file mapping. BSD-3 notice is retained. The sparse compatibility state has static assertions for the proven stock offsets (`pTCB +0x18`, CQ count `+0x20`, HP count `+0x840`, XIP delay `+0x8cc`, extent `0x8d0`); unproven bytes remain opaque and the full public SDK state is explicitly not substituted.
- Current `lifecycle-comparison-reviewed.json` is `PASS`, 102 cases, 174 unique original instruction bytes. Script, ELF, parser and source manifest hashes match the current files. For original and source runs, the verifier compares returns, complete final handle bytes, synthetic provider call order/arguments/results, XIP-read timeline, and raw state writes; raw writes must match exactly and be 32-bit stores at prefix/module words.
- The expanded matrix spans modules 0–2 and covers invalid/null handles, disabled handles with and without pending counts, CQ/HP busy returns, CQ provider success/failure, failure with XIP set, XIP delay including `UINT32_MAX`, no TCB and queue term/delay order. The deinitialize case confirms the original's unusual behavior: it ignores disable failure/busy status, clears initialized state and module, and returns success. This is faithful evidence, not an endorsement of shutdown safety.
- The CQ-disable, CQ-term, and delay providers are synthetic on both sides. They record call arguments/order and return configured outcomes; they do not drain/free a real queue, delay time, or establish safe hardware shutdown. No powered hardware, IRQ timing, or concurrency is validated.
- The earlier shared-report-path issue is resolved: lifecycle has `AMBIQ_LIFECYCLE_REPORT` defaulting to a separate `lifecycle-comparison.json` path, avoiding exclusive-create collision with the interrupt verifier.
- `python3 -m unittest g2.tests.test_ambiq_mspi g2.tests.test_ambiq_mspi_lifecycle -v` passed all six tests on the reviewed snapshot, including host lifecycle provider ordering, exact source excerpt/license checks, M55 linked symbol bounds, and optimized-mode fail-closed checks.

## Remaining limits and docs

Lifecycle public-upstream identity does not prove the unavailable private firmware build revision or compiler flags. Queue and delay integration, valid mapped/powered module state, concurrency, and product-level shutdown safety remain outside this subset. The component README is stale at this review: it opens with “four unchanged function texts” and still presents only interrupt coverage. It should describe both lifecycle functions, the `deinitialize` ignored-error behavior, synthetic seams, and current lifecycle validation before this component is presented as a six-function snapshot.

## Snapshot identities

- `ambiq_mspi_lifecycle.c`: `c55c3e163097e0112b11eb9fc4192b6a25de8cdaf28da41b1e3a6c8f2272ad0d`
- `simulator/verify_lifecycle.py`: `636837d152dc69b797b89626d1d85d18b79482cf2e1679a8e0682e7753d437f9`
- `simulator/lifecycle_seams.c`: `ab0a32d4c7868181351d6e727dd1e032d264da49711d7848150699818d149db9`
- `test_ambiq_mspi_lifecycle.py`: `12618871c31ebf10b2752e15498881687c79889edd52d7d1ce3b04d3e4a7e2d8`
- `Makefile`: `9681a00c504c76770b1320c1a3e711cc99719f695d820ff198f3936e77e553d6`
- lifecycle comparison: `9ae5b2768715682ab3e7e6cf6c89fa5a4650f42853db87a23cde88e74483144e`
