# CMDQ disable and termination implementation

The new `g2/components/foundation/ambiq_mspi/ambiq_cmdq.c` replaces both queue providers in a separate real-CMDQ simulator profile. The ARM32 contract is in `ambiq_cmdq.h`; pinned unchanged function text and reconstructed helpers are distinguished in `CMDQ_PROVENANCE.json`. `make -C g2 ambiq-cmdq-simulator` builds this profile. The old synthetic lifecycle profile remains available for its return-propagation fixtures.

## Recovered and implemented behavior

- `am_hal_cmdq_disable` (0x538e8c, 66 bytes): validate init/magic; return success if already disabled; otherwise clear hardware CQEN and handle enable bit. No wait, index check or free.
- `am_hal_cmdq_term` (0x53909a, 98 bytes): refresh current index/head; when not forced, reject unequal current/end indices; otherwise clear init, CQEN and configured pause-enable mask. Force bypasses the busy comparison, not index refresh. It does not clear the enable bit directly, drain, or free.
- `update_indices` (0x538d18, 64 bytes): use hardware index low eight bits and end-index epoch; subtract 256 when signed modular comparison indicates wrap; refresh queue head from hardware address; restore the saved PRIMASK. Queue-size/index invariants remain caller preconditions.
- `mspi_cq_disable` (0x4bfd62, 12 bytes): use caller-local queue slot +0x828.
- `mspi_cq_term` (0x4bfc86, 58 bytes): use the global module state at 0x200523d8, stride0x8d0, queue slot+0x828; call forced termination, ignore its status, clear the global slot and return success. Tests deliberately use separate caller/global storage; this does not establish invalid-handle aliasing on hardware.

## Fresh validation

The hardened verifier `simulator/verify_cmdq.py` passed 372 original/source comparisons against the final linked module. All instructions in the seven selected bodies execute: 472 bytes, including 174 previously covered lifecycle bytes and 298 new CMDQ bytes. Tests compare return values, complete sparse MSPI/CMDQ state, global slot, MMIO read/write values and order, critical/delay calls and final PRIMASK. Independent leaf checks assert disable validity and termination index/status behavior. Cases cover all three modules, invalid/init/disabled states, nulls within valid API contracts, index wrap, nonforced busy/idle, pause masks, pending MSPI work and XIP selection.

Only critical-enter 0x473940 and delay 0x4807a0 are intercepted on both sides. **No CQ function is stubbed in this profile.** Critical-enter returns a synthetic prior mask; the source contains an actual PRIMASK restore instruction. This does not prove real masking, concurrency, elapsed delay, hardware MMIO behavior, valid queue allocation or whole-system shutdown safety. No byte-identical compiler claim.

Fresh regressions: 68 interrupt original/source cases pass using the real-CMDQ linked module; the preserved synthetic profile passes its 102 lifecycle cases after rebuilding. Nine MSPI focused unittest methods pass, including build/link, provenance excerpts and optimized-verifier rejection. Final aggregate: 32 modules, 183 method invocations, 177 passing, zero failures/errors, six method skips and one class setup skip. Independent review closed both hardening findings with no critical blocker; see `review/report.md`. Aggregate results are in `g2/build/foundation/ambiq-cmdq-simulator/aggregate.json`; dependency-related skips remain explicit. The first aggregate attempt used system Python without Capstone and failed import; it was rerun using the installed OpenCFW environment.

Reports are in `g2/build/foundation/ambiq-cmdq-simulator/comparison-reviewed.json` and `interrupt-regression.json`. Hash bindings are in `build-provenance.json`; the distinct nonoverlapping map in `new-code-evidence.jsonl` leaves prior maps unchanged. Cumulative bounded original execution is 936 bytes, separate from whole-firmware coverage or source completion.

## Practical boundary and next work

A forced termination call is not evidence of a drained queue or released buffer. Preserve stock local/global slot selection and ignored termination status when integrating this subset. A memory-ownership patch still needs the actual interrupt-critical entry/valid initialization, hardware queue completion and allocator ownership contracts; this implementation intentionally does not fix stock behavior or invent a release path.

The next bounded software target is critical-enter 0x473940 and its privilege/masking behavior, followed by actual delay semantics or queue initialization as evidence permits. No external blocker prevents analyzing those supplied instructions. Production deployment remains outside this offline module's scope. Packer, manifest, workflow state and official Apollo hashes are unchanged. No commits, staging, flashing, deployment or shared campaign edits were performed.
