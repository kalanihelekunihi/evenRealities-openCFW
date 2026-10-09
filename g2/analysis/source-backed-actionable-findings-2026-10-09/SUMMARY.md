# Two actionable source-backed findings

Both findings concern the locked G2 2.2.6.10 artifact. They establish software behavior under stated conditions, not an observed physical failure. No application, emulator, production firmware or hardware modification is proposed or performed by this summary.

## BQ27427: full-byte CC Gain update — independent review pending

[Descriptor binding and tests](../bq27427-descriptor-binding-2026-10-09/REPORT.md) resolve initialized RAM table `0x200006EC` through the authenticated compressed startup record. Entry 6 at `0x2000071C` selects subclass 105/block 0/offset 5/type 1. Configure passes value `0x28` at `0x53BCB6` and commits this buffer at `0x53BCCE`. The generic update replaces the entire byte and sets dirty when buffer valid is nonzero; it does not test bit7 or preserve the lower seven bits. The normal commit writes the block and recomputes its checksum.

Zephyr's newly acquired reference instead conditionally clears bit7 and XOR-adjusts checksum. They agree for prior 0xA8, but differ for prior 0x80 (stock 0x28 versus Zephyr 0x00) and 0x7F (stock 0x28 versus unchanged 0x7F). Emulator zero defaults cannot prove stock skips its update. This gives a concrete interoperability/testing target: distinguish selective sign correction from stock's full-byte constant write and retain original byte/checksum provenance in any future investigation. Physical calibration correctness and fitted-board execution remain unknown.

Validation: original startup decoder versus independent Python over 17,752 bytes; 12 original update cases using actual initialized descriptors; one original commit/checksum fixture. The latter stubs mode, transport and delay success; it does not establish a physical transaction. **Independent review is pending.** This summary does not promote the mapping to reviewed status; any audit result should be recorded additively without rewriting these sealed packets.

## Flash: mixed-return predicate and ignored enclosing return — independently reviewed

[Independent review](../coverage-audit-parallel-2026-10-09/FLASH-ERROR-PATH-INDEPENDENT-REVIEW.md) verifies the corrected instruction windows and refines the exact error path. RDCR predicate returns HAL read errors unchanged at `0x47042C`; successful reads return boolean 0/1. Caller `0x4705C4–0x4705C6` tests only zero/nonzero, so a nonzero error that returns normally takes the true branch to `0x470610`.

The subsequent helper `0x4706E0` sends **WRDI opcode 0x04** at `0x4706EC–0x4706EE`, not another mode readback. Its status is checked at `0x470616–0x470618`: if the original read error returns normally and WRDI succeeds, this local mode routine can return zero at `0x470662` without validating the original mode result. Outer initialization calls the mode routine at `0x46FF40`, overwrites r0 with 1 at `0x46FF44`, and proceeds to QE `0x470AAC`; the selected tail does not accept/check the mode return.

This gives a specific future failure-injection target: a returning readback transport error followed by successful WRDI, plus the enclosing ignored result. It is a conditional static finding; diagnostics might halt under unknown configuration, and no such error was observed on hardware. Stack storage/count1/address0 are valid at this callsite, so generic helper argument errors must not be presented as ordinarily reachable here. The withdrawn mask discrepancy remains withdrawn: RDCR 0x20 agrees with the vendor mask; RDSCUR 0x40 is a different register.

## Preservation and scope

Evidence hashes and review status are recorded in evidence-references.json. Existing seals, all 110 audit inputs, four checkpoints and observed index stability are checked in preservation.json. Whole-image P2, source completeness and byte equality remain separate open claims. Matching public protocol does not authorize changing these behaviors in the byte-identical reconstruction target.
