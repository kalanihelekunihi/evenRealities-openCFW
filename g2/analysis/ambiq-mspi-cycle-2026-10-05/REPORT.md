# Ambiq MSPI source reuse cycle — 2026-10-05

Implemented and linked four upstream interrupt helpers with a minimal,
explicit handle/register compatibility shim. The selected original bodies
are230 bytes total; three previously unnamed main-payload functions account for182 bytes.
The known48-byte interrupt-clear routine is a control, not new source attribution.

## Actual source/integration

- `g2/components/foundation/ambiq_mspi/ambiq_mspi_interrupts.c`: four unchanged
  pinned-source function bodies with original BSD-3-Clause notice.
- `ambiq_mspi_compat.h`: first8-byte handle ABI and interrupt register window;
  does not instantiate the SDK's complete private state.
- `ambiq_mspi_interrupts.h`: caller requirements and source API.
- `simulator/entry.c,module.ld,verify.py`: callable source-only Cortex-M55 ELF
  and authenticated original/source instruction comparisons.
- `g2/tests/test_ambiq_mspi.py`: four host/source-integrity/build/verifier tests;
  `g2/Makefile` registers them and provides simulator build/test targets.

Source identities, per-file license/version evidence and exact upstream
Git-blob verification are in `upstream/`; authenticated original bodies,
literals and consumer callsites are in `original/`. Independent review is
in `review/report.md`.

## New understanding and practical use

MSPI enable/disable are INTEN+0x200 read-modify-writes, requiring caller
serialization. Status reads INTSTAT+0x204 first and optionally masks it with
INTEN; pending disabled events remain visible to the raw-status API. Clear
writes INTCLR+0x208 followed by a volatile INTSTAT read. Retaining the readback
is an essential source contract, but physical posted-write completion is not
proved by the synthetic model. Handle validation uses magic0xbebebe and init
bit24; other flags do not affect validity. Invalid handles return2 before MMIO.

The authenticated NOR and display transport consumers use raw status, then
clear the same pending bits before service. The async NOR write path explicitly
clears and enables mask0x1a80 (DERR/CQUPD/CQERR/SCRERR). This supports reuse of
these helpers when integrating memory/display transports and explains why
enabled-only status is insufficient to infer all pending state. It does not
establish callback completion, NVIC ownership or DMA buffer lifetime.

## Validation and bounded incremental scan

`g2/build/foundation/ambiq-mspi-simulator/comparison-heldout.json`:68 cases pass
against complete original bodies without callee stubs, all3 module addresses,
zero/all-bit/complement/actual-consumer masks, raw/enabled status, output guard
preservation and invalid prefixes/NULL handles. Source/ELF/verifier/shared
parser hashes are recorded; `build-provenance.json` binds flags/tool versions
and final inputs. Synthetic W1C stimulus is explicit, not a hardware model.

Focused foundation:11 touch+4 MSPI+7 resource tests pass. Affected core suite:
30 modules,178 method invocations,172 passing methods,0 failures/errors,6
method skips plus1 class-setup skip. Skips still require reviewed CFW image,
authenticated Apollo Ghidra corpus, reachable font npm dependency and protoc.
Font negative-test passes may occur at an earlier dependency error; they do
not prove those intended local error branches.

`new-code-evidence.jsonl` maps all230 bytes to authenticated payload/bundle
coordinates; all were unresolved in the earlier code/non-code partition.
`knowledge-delta.json` separates230 new executed bytes,182 new bounded
source-behavior identifications,0 exact compiler-byte matches and0 new
resources. With the preceding touch cycle,464 unique bytes have this bounded
execution evidence. This does not change the broad receipt-based197000-byte
review footprint or490200-byte instruction-export count. No existing shared
partition, symbol file or campaign state was overwritten.

## Next boundary

The full MSPI service routine needs the private state/callback/command-queue
layout and clock-manager contracts to be recovered and checked before its
public implementation can be safely reused. Actual device bring-up requires
board GPIO/pin/clock/power/NVIC configuration and hardware traces; synthetic
interrupt helpers cannot establish that behavior. Full binary equality also
needs the producing toolchain/configuration, not just public HAL source.
Next bounded software work should verify a source-backed GPIO leaf or recover
one service-state interface rather than replace the full driver speculatively.
No commits, flashing, deployment or production-provider changes occurred.
