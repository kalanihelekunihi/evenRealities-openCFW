# Architectural interrupt-mask provider

This cycle selects the remaining critical-entry provider over a new GPIO family because it removes a directly exercised CMDQ dependency with a proven eight-byte upstream leaf. It does not introduce another broad driver model or infer queue ownership from timing. The architectural contract is testable with supplied instructions; elapsed physical delay is a separate contract.

The reusable declaration and caller contract are in `ambiq_interrupt_mask.h`.

`g2/components/foundation/ambiq_mspi/ambiq_interrupt_mask.c` retains the pinned public HAL GCC function `am_hal_interrupt_master_disable` unchanged, with a GNU alias for the CMDQ provider name. Its three instructions are `MRS r0, PRIMASK; CPSID i; BX LR`: return the prior mask and set the configurable-interrupt mask. Privileged execution is a caller precondition. The source compiles to exactly the eight original bytes at0x473940 (`eff3108072b67047`); this is a leaf byte match, not complete firmware equality.

`make -C g2 ambiq-critical-simulator` selects this real provider in a distinct callable simulator profile. The CMDQ index refresh still restores PRIMASK using its actual ARM instruction. Only delay is intercepted. Synthetic-critical and original synthetic-CQ profiles remain explicit alternatives. Build flags are recorded and the small CMDQ profile always rebuilds, preventing a stale ELF when callers reuse one output directory. The same-directory real/synthetic/real regression exposed and fixed a same-second timestamp cache issue.

## Fresh evidence

- Final real-critical comparison: 435 cases, all eight selected bodies fully executed (480 original bytes, including the eight new critical bytes). Initial PRIMASK0/1 is applied to actual CPU state. Protected queue index and address reads are observed at PRIMASK1; the prior mask is restored. Direct entry returns the old mask and leaves interrupts masked.
- The synthetic-critical CMDQ profile remains compatible: 372 fresh comparisons pass against the expanded verifier.
- Real-critical module interrupt regression: 68 original/source cases pass.
- Eleven focused Ambiq unittest methods pass, including source-excerpt hashes and profile switching.
- Aggregate: 185 method invocations, 179 passing, zero failures/errors; six method skips and one class setup skip remain dependency-related.
- Independent review found no critical blocker. See `review/report.md`.

The accepted report is `g2/build/foundation/ambiq-critical-simulator/comparison-interface-final.json`, bound to the current ELF, source files and verifier by `build-provenance.json`. Pinned public-source Git blob identity and exact GCC excerpt hash are in `INTERRUPT_MASK_PROVENANCE.json`. The distinct incremental evidence map adds eight previously unresolved stored instruction bytes without overwriting prior maps. Cumulative bounded original execution is944 bytes; whole-firmware reviewed coverage/source completion is not recomputed or advanced by that sum.

## Delay investigation and remaining limits

The call to0x40 in the delay wrapper must not be labeled absent ROM code merely because it is outside the linked flash address range. The authenticated scatter record at0x75d3e0 selects the stored handler0x43a11e and a packed22-byte stream at0x79430e, with destinationITCM0x40. Correctly mirroring the pre-decrement literal loop consumes13 literals then a3-byte backreference, followed by3 literals and a5-byte backreference: all22 input bytes are consumed in bounds and24 bytes result. The first six bytes are `0138fdd17047` (`subs r0,#1; bne0x40; bx lr`). Packed length0x2c encodes22 input bytes; it is not a44-byte output length.

This is a **static mirrored decode**. Both worker and independent root Unicorn attempts skipped the literal-copy loop and faulted; full scatter initialization is not dynamically validated. Failed diagnostics are retained and explicitly marked inconclusive, not counted as successful tests. The earlier suspected out-of-image read was an off-by-one interpretation error and has been corrected. No missing-ROM or missing-next-byte blocker is asserted. See `original/README.md` and `decode-crosscheck.py`.
The full delay wrapper uses floating-point conversion, clock-state selection and adjustment literals250.0/96.0 before calling the ITCM loop. It remains an explicit simulator seam in this cycle; replacing it requires validating those conversion/clock contracts and exact runtime initialization, not equating instruction counts with microseconds. No assertion that timing is blocked by missing ROM.

Serialized privileged Unicorn execution proves the tested instruction and MMIO-access contract. It does not demonstrate pending-interrupt delivery, real scheduler interleavings, unprivileged enforcement, cache/bus effects, oscillator calibration or whole-system shutdown safety. The initialized-handle/queue-buffer ownership contract remains separate. No firmware patch, commits, staging commands, flashing, deployment or shared campaign edits were performed. Protected packer, manifest, workflow state and official Apollo hashes remain unchanged.

The next ranked independent implementation target should be a directly consumed GPIO/bus or IPC primitive, while retaining the delay initialization/conversion gap as a bounded separate analysis item. There is no reason to expand the critical-entry leaf further without a concrete consumer contract.

Automatic approval review rejected deleting the worker's failed emulation script, citing preservation of existing artifacts. It remains clearly marked as failed; no cleanup is needed for this implementation.
