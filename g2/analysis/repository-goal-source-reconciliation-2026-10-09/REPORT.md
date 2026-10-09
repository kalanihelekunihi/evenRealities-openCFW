# Repository goal and source-ledger reconciliation

Date: 2026-10-09 UTC

## Result

The audio/UART/power static ledger is exhausted at its documented evidence
boundary. The broader G2 goal is not exhausted. The normative workflow remains
in `P2_EXECUTING`; `G2_PSEUDOCODE_COMPLETE` and `G3_CORPUS_FROZEN` have not run,
and no C implementation assignments exist. The next useful work is therefore
the current whole-firmware pseudocode campaign, not another audio source-family
search and not implementation work.

This conclusion is tied to the locked official `s200_v2.2.6.10` bundle:

- size: 4,301,227 bytes;
- SHA-256: `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`;
- payloads: `codec`, `ble_em9305`, `touch`, `case`, `apollo_bootloader`, and
  `apollo_main`;
- campaign: `g2/build/pseudocode-first/20260930T190500Z`.

## Live workflow evidence

`g2/workflow/state.json` records:

- G1 passed against six payloads, 33 images, 70 initial coverage rows, and 125
  exact-hash reviews;
- 14 inventory/analysis assignments: eight `partial`, two
  `ready_for_review`, one `dispatched`, two `reviewed_partial`, and one
  `reviewed_proposals_pending_admission`;
- three P2 pseudocode assignments, all `dispatched`;
- zero C implementation assignments;
- G2 through G6 have not run.

The explicit workflow next step is bounded ARM, C-SKY, and ARC startup recovery
and independent review across all 33 images and six payloads. Current campaign
analysis also contains continuing per-image code/data, fixed-library,
instruction-coverage, computed-dispatch, indirect-root, and literal-pool
records. Their presence is evidence of active recovery, not evidence that the
records have passed G2 or entered a frozen corpus.

Older subsystem `next lead` lists are historical hints. They must be checked
against current P2 ownership before use. In particular, they cannot override
the workflow state or turn a locally completed audio branch into a whole-image
completion claim.

## Reconciled source inventory

The repository already has the useful public families represented in its
source registry and reference ledger. Material G2 examples include Ambiq
Apollo510 HAL, FreeRTOS/CMSIS, Cordio, LVGL and the Ambiq draw backend,
FreeType, littlefs, FlashDB, LC3, nanopb, TinyFrame, TLSF, touch-controller
PDL/reference sources, STM32G0 HAL/reference sources, and NationalChip
KWS/DNN/reference material. Tooling pins include the decompilation and binary
comparison helpers already recorded under `third-party/`.

The initial repository-local scan identified no new public source. The parallel
discovery follow-up supersedes that bounded finding: it acquired two previously
unregistered public comparison sources, embARC OSP and NationalChip lvp_aiot.
They are useful leads, but neither is attributed to the locked firmware.
Adding a checkout alone does not close the live P2 gates. Existing selected
commits are reproducible baselines where the exact
private producing checkout cannot be proven; they must not be described as the
original build inputs merely because behavior or version intervals match.

## Inputs that remain unavailable

The following gaps cannot be closed by further repository-local public-source
searches:

- the exact private Ambiq producing checkout and first-party application
  source;
- IAR EWARM 9.60.2 runtime/source and the complete original compiler/linker
  configuration needed for byte identity;
- NemaGFX/NemaVG implementation source corresponding to the linked IAR
  objects;
- proprietary EM9305 SDK/controller and Packetcraft link-layer source;
- resident ROM and factory-only code/data absent from the OTA artifact;
- exact signing, packaging, and other private build inputs;
- live state needed for physical NVIC/PendSV/task selection, calibration,
  callback-table, GPIO/UART/clock/power, and device-timing claims.

The local simulator can test a stated image/profile, but its availability does
not supply missing source or prove device behavior or byte-identical output.

## Exact next evidence and work

### Newly reconciled source leads

- embARC OSP, `67ea926c6a62aa6e19efdc3b11cba3ea0b467e29`, is a BSD-3-Clause
  root-licensed ARC startup/exception/cache/timer comparator. It is not evidence
  that EM9305 linked embARC.
- NationalChip lvp_aiot, `d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b`, is a
  root-MIT alternate official GX8002 source comparator. Discovery reports 38
  new source/header/assembly paths and 68 differing files versus lvp_kws.
  Board/UART/audio/provider differences need image-bound mapping before use.
- Exact touch SDK/compiler/generated configuration remains an actionable
  attribution lead using existing sources. The sealed scan-preparation report
  retains a 24-byte PDL Configure loop-layout mismatch and missing generated
  cycfg. Semantic and selected byte matches do not identify the producing SDK.
  No new experiment was run: the auditor owns the read-only discrimination
  plan, and existing matching receipts must be reconciled first.

No top-level campaign contract scope found in the current scan explicitly names
touch Configure/compiler discrimination; this is not an assignment receipt or
proof that all historical experiment ownership is absent. Coordination with
the audit track is required before experimentation. Canonical firmware state
and ownership remain unchanged.

See the discovery and audit isolated reports for provenance and qualifications.
The registration proposal in this directory is reviewable text only; no root
`.gitmodules` or gitlink was changed.

Discovery's `STATIC-COMPARISON.md` further narrows the new references:
UART-message differences are copyright-only and cannot discriminate pins.
GX8002B PLL fallback/clock constants, SADC/PDM/I2SIN initialization and FFT/VAD
branches are useful differential leads. Thirteen selected target slices were
hash-verified, but not source-attributed. Locked VAD strings favor KWS-like
diagnostic source over unmodified AIoT; executable references are needed to
prove use, and private patches/configuration remain alternatives.

The touch execution track has authorization to install official tools. Existing
bootstrap records pin the three Linux archive hashes. Docker API access was
denied; no retry, escalation or alternate route around that socket was attempted.
Compiler execution remains blocked pending legitimate access resolution.

Subsequent user-authorized sandbox escalation succeeded without socket changes.
The isolated official GNU 10.3/11.3/12.2 matrix is complete in
`touch-compiler-matrix-2026-10-09`; none resolves Configure. All 27 consumed
noncompiler inputs match the prior 13.3 receipt, and Configure's normalized
preprocessed definition is identical across the three older builds. Generated
cycfg is not a consumed input of this standalone body. A genuinely different
authenticated source revision or original build environment is the next useful
discriminator; the preceding blocked status is historical.

1. Complete or explicitly bound every current P2 packet for executable extents
   in the six payloads, including ARM, C-SKY, and ARC startup paths.
2. Resolve conditional SRAM/XIP mappings, unsupported ISA semantics, unknown
   callees, computed/indirect targets, and the remaining code-versus-data
   classifications.
3. Reconcile the global byte ledger for all 33 images, including nested
   images, assets, metadata, padding, and external-ROM dependencies.
4. Independently review the accepted pseudocode and non-code accounting, then
   pass G2 and freeze the immutable corpus at G3.
5. Only after G3, derive shared interfaces and C implementation contracts at
   G4. Runtime or simulator traces may validate behavior but do not substitute
   for missing static coverage.

For unavailable-source claims, the exact new evidence would be an
authenticated producing source archive/checkout, matching proprietary library
objects or source, an authenticated ROM/factory dump where lawful and
available, or image-bound runtime traces for the specific dynamic claim.

## Scope boundary

### Follow-up static packet

The new isolated packet `g2/analysis/csky-indexed-word-accessor-2026-10-09`
recovers the 16-byte indexed word accessor at conditional XIP
`0x102058B4–0x102058C4`. A scan of 117 campaign contract scopes found no
declared extent overlap. It remains partial/unreviewed and does not modify
campaign ownership. Its original bytes, helper and direct caller are statically
validated; semantic fixtures are not original-instruction execution. The packet
also records a prior source-map payload-offset discrepancy for independent
review. This demonstrates useful unowned static work beyond the exhausted
audio branch without claiming completion or admission.

The three assignments listed in workflow state are an initial state summary,
not a complete live ownership census. The task directory contains 117 contracts
at this follow-up scan. Selection must inspect those contracts as well as state.

This report does not mutate `g2/workflow/state.json`, campaign tasks, receipts,
or coverage ledgers. It does not claim source completeness, executable
equivalence, physical behavior, or byte identity. It reconciles the completed
audio/UART/power branch with the repository's actual whole-firmware goal and
identifies where useful work remains.
