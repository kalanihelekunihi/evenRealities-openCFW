# Ambiq MSPI lifecycle/state-layout cycle — 2026-10-05

Implemented exact public-source disable/deinitialize bodies and linked them
into the existing callable Cortex-M55 simulator. The selected original bodies
are118+56=174 bytes. Public source is Ambiq Apollo5105.1.0 replay commit
5efc0228528a8adce5eae0d226fac85d2551eb3b, file revision
release_sdk5p1p0-366b80e084, BSD-3-Clause. Original notice/conditions/disclaimer
are preserved. Function excerpt hashes are in the component SOURCE_PROVENANCE.
This is source-level behavioral correspondence, not a new compiler-byte match
or proof of the unavailable private producing checkout.

## New source and integration

- `g2/components/foundation/ambiq_mspi/ambiq_mspi_lifecycle.c`: two unchanged
  upstream function texts.
- `ambiq_mspi_compat.h`: sparse STOCK view with static offset assertions for
  TCB address slot0x18, CQ count0x20, HP count0x840, XIP delay0x8cc; unproven
  fields remain opaque. This differs from the full public SDK state layout.
- `simulator/lifecycle_seams.c`: synthetic link providers for CQ-disable,
  CQ-term and delay; logs/configured status only, no real teardown/time effect.
- `simulator/entry.c,verify_lifecycle.py` and Makefile: new callable entry points
  and separate lifecycle evidence output.
- `g2/tests/test_ambiq_mspi_lifecycle.py`: host lifecycle/error/provider tests;
  existing MSPI test also checks all6 exact source excerpts and link entries.

## Proven bounded behavior

Disable rejects invalid handles with2. Already disabled returns0 without
checking pending counts. Enabled with nonzero CQ/HP counts returns3 unchanged.
If TCB slot is nonzero, CQ-disable is called first; its error is propagated,
without CQ-term, enable clearing, XIP read or delay. On success CQ-term precedes
enable-bit clearing. DEV0XIP bit0 then selects the external delay call.

Deinitialize invokes disable when enabled but ignores busy/provider errors,
clears init bit24 and module index, and returns0. A synthetic busy case leaves
enable bit25 and pending counts intact even though the handle becomes invalid.
A successful return therefore is not a quiesce/drain guarantee. These original
function instructions were executed, but no hardware occurrence of the
synthetic state is asserted. No speculative ownership/free patch was made.

## Actual consumers and practical implications

Authenticated NOR/display reconfigure consumers0x470d7c and0x59c876 call disable
and gate configure/restart on its result. JBD4010 power-off sequence0x593200
calls disable at0x59326a. Initialization/configuration error cleanup0x46fb0c
uses deinitialize at0x46fc20/96/f6. Callsite instruction bytes and caller
hashes are in original/results.json; no application success-path timing was
traced. CFW/client code must preserve disable errors and maintain lifecycle
serialization rather than interpret deinitialize success as buffer release.

## Validation and incremental map

Final evidence:
`g2/build/foundation/ambiq-mspi-lifecycle-final/lifecycle-comparison-reviewed.json`
passes102 cases and executes all174 original instruction bytes. Both lifecycle
bodies are fully executed; original deinitialize's disable callee is not
stubbed. Only external CQ-disable/term/delay calls are stubbed on both sides.
Expected calls, arguments, return codes, complete sparse-state bytes/guards,
MMIO32-bit XIP reads, and exact32-bit prefix/module stores and ordering match.
All3 module indices, invalid prefixes/NULL, disabled-with-work, busy counts,
CQ success/error with XIP enabled, reserved XIP bits and zero/max delay
arguments are checked. Physical delay units/timing are not measured.

The SAME final ELF also passes68 interrupt-family comparisons without
original callee stubs. Focused checks:11 touch+6 MSPI+7 resources=24 pass.
Affected aggregate:31 modules,180 methods invoked,174 passing methods,0
failures/errors,6 method skips plus1 class setup skip. Optional missing
inputs/dependencies remain reviewed CFW image, authenticated Apollo corpus,
reachable font npm dependency and protoc; negative font tests can pass at an
earlier dependency failure.

The new174-byte ranges do not overlap earlier touch234B or MSPI230B. The
combined bounded original execution footprint is638B. These174 bytes were
unresolved in the earlier byte-map partition; knowledge-delta.json and
new-code-evidence.jsonl preserve separate coordinates and attribution. Exact
compiled upstream match delta0; typed resource delta0. Broad receipt-based
review/instruction-export metrics and full source completion remain separate.

## Exact remaining boundary

Real command-queue teardown lives at external functions0x4bfd62/0x4bfc86
(wrapping0x538e8c/0x53909a), and delay provider0x4807a0. Their lifetime, wait,
clock and global CQ-state effects are not implemented/proved by these stubs.
Proving physical drain also requires hardware/IRQ/DMA behavior and runtime
queue state. The software provider bodies are available for the next bounded
analysis; this batch does not claim an external input blocks their analysis.
No firmware flash/deploy/commit, production-provider or shared campaign edit.
