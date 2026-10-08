# OpenCFW change scan — 2026-10-07 18:58 UTC

Compared with the 15:26 UTC saved scan. Read-only inspection of existing source and test artifacts; no generators, builds, emulators, firmware edits, index or campaign changes. Only this scan report and snapshot were added.

## Actual new source

Bootloader component inventory increased from **295 to 302** C/header/assembly files; foundation remains **89**. All **384 prior files have identical hashes**, with no removals. Seven additions are presently untracked and have **no matching Git ignore rule**:

- `initializer_callbacks/startup_pcm22_sequence1.c`
- `initializer_callbacks/startup_pcm22_sequence3.c`
- `initializer_callbacks/startup_pcm22_sequence17.c`
- `initializer_callbacks/startup_pcm22_sequences.h`
- `thread_creation/thread_termination.c`
- `thread_creation/thread_termination.h`
- `thread_creation/idle_cleanup.c`

Paths above are relative to `g2/components/bootloader/`. These are source bodies/interfaces, not script-only bookkeeping. Build products remain separately ignored; that does not hide these additions.

## Validation that advanced

The standalone **c711fbf4** runtime-integrated candidate now has a PASS final summary: **207 objects, seven integration cases, 54 additional receipt files**. Its successor **8e255c6e** adds installed selector1 and native idle cleanup: **209 objects, seven integration cases, 59 additional receipt files**, with exact frozen-object ELF reproduction recorded. This scan independently checked candidate ELF hashes and every listed receipt hash: zero mismatches. It did not rerun tests or repeat the object rebuild.

The successor evidence includes 1,400 initialized-root comparisons, 260 runtime comparisons, 512 teardown comparisons, 24 idle cleanup fixtures, actual allocator/drain fixtures and basic/FP-high-register PendSV comparisons. Counts represent bounded fixtures, not firmware coverage percentages. Native idle cleanup establishes deferred ownership release for the tested queues; the stock idle entry at `0x4189ac` remains an original-address dependency in this candidate.

Separately recovered tickless body `0x41b754..0x41b818` has **192 passing instruction comparisons covering all 196 bytes**. Timer, sleep hooks and wake remain modeled; this body is not linked into the 209-object candidate.

## New architectural test is partial

The existing QEMU Cortex-M55 harness reports **three PASS basic-frame ownership scenarios**, exercising actual modeled SVC/IRQ/PendSV exception entry/return and idle reclamation. The first FP scenario **FAILS** with CFSR `0x00020000`, HFSR `0x40000000`; subsequent FP ownership scenarios have no completed result in the receipt. Overall status is `PARTIAL_OR_FAILED`, not PASS. This is a reconstructed-source MPS3 core harness, not execution of the locked firmware on an Apollo510 model. Static-stack placement and extended-frame fault diagnostics require review before expanding the claim; the current receipt alone cannot identify a firmware defect.

## Preserved limits

Shared offline ELF remains `129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9`; neither validated successor is promoted. The historical selector17 verifier copy remains unavailable; new receipt reconciliation does not repair that old source-manifest discrepancy. Actual idle entry, FP/lazy architectural behavior, timer/IRQ concurrency, peripheral timing, resident ROM and whole-bundle source/byte equality remain unresolved.

Useful next work is to diagnose the bounded FP harness failure and verify full idle/tickless dependencies. No further inventory expansion is necessary to establish that new source is being produced. Exact source identities, receipt/ELF checks and the observed partial QEMU result are in [snapshot.json](snapshot.json).
