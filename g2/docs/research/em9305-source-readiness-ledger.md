# EM9305 comprehensive source-readiness ledger

Status: residual concrete-source frontier production-routed; whole-source readiness blocked

Hardware activity: none

## Gate result

The authenticated EM9305 residual census is now accounted exactly once:

| Readiness state | Spans | Bytes | Meaning |
|---|---:|---:|---|
| Concrete source available | 23 | 1,240 | MIT MetaWare/runtime and tail spans are production-routed by checked ARCv2-EM entries |
| Typed unsupported external boundary | 25 | 8,348 | ownership/entry is accounted, but complete behavior is unavailable and the API fails closed |
| Unavailable proprietary controller code | 127 | 24,070 | authenticated controller/vendor retention with no redistributable replacement source or typed boundary |
| **Total** | **175** | **33,658** | complete residual code-or-mixed census |

Consequently:

- accounted spans: 175;
- accounted bytes: 33,658;
- unclassified spans after a readiness decision: 0;
- unclassified bytes after a readiness decision: 0;
- source complete: no;
- concrete-source frontier production-routed: yes;
- whole-component source ready: no;
- blocking spans: 152;
- blocking bytes: 32,418.

“Zero unclassified” means every residual byte has a deterministic readiness
decision. It does not mean every byte has community source. The gate keeps
those conditions separate and cannot report zero unless the ledger keys,
intervals, hashes, span count, and byte sum exactly match the authenticated
residual census.

## Composed inputs

The ledger composes ten independent evidence lanes:

1. The existing residual-provenance map supplies the closed 175-span / 33,658-byte
   accounting scope and the 130-span proprietary controller/vendor class.
2. The MetaWare lane promotes its two authenticated islands / 980 stock bytes
   to `concrete_source_available`. A checked GCC 16.1.1 ARCv2-EM build receipt
   routes eight external ABI entries to maintained C with zero undefined
   symbols and zero forbidden runtime imports; two now-private interior entries
   are deterministic NOP fill.
3. The exhaustive residual-tail lane production-routes 21 spans / 260 stock
   bytes through 23 four-byte entries, four direct C no-ops, and a 288-byte
   implementation cave; it also assigns 15 spans / 630 bytes to typed
   unsupported external boundaries.
4. The first-party hook candidate assigns all seven spans / 1,224 bytes to
   typed boundaries. Some control-flow shells are exact, but the complete
   application behavior is not, so the ledger does not overstate source
   completeness.
5. The QP/C audit authenticates the nine-entry hook table, release lineage,
   and complete QP/C cluster partition. A reviewed GCC 16.1.1 ARCv2-EM build
   now compiles the eight portable units plus two OpenCFW port units and links
   a deterministic relocatable component with zero undefined symbols and zero
   forbidden runtime imports. This closes the compiler and software-link gap,
   but not install placement, redirect ownership, or production routing.
6. The named QP/C hook-provider audit authenticates `PalUartResume` and
   `wsfOsRunIdleTasks` as exact identities in the pinned EM/Packetcraft
   controller/PML archives. The software-only WSF routine now has reviewed MIT
   source for its three-callback layout and one-bit activity reduction. The
   hook's retained 24-byte shell remains a typed boundary because
   `PalUartResume` and `VoltMon_DoMeasurement(0)` depend on unavailable physical
   platform evidence; the final edge is an exact no-op chain.
7. The slave-connection boundary converts the largest remaining 3,126-byte
   controller residual from an undifferentiated unavailable retention to one
   typed fail-closed boundary with six authenticated entry identities. This is
   an integration-readiness decision only: its provenance remains proprietary,
   exact source and redistribution authority remain unavailable, and production
   routing stays disabled.
8. The master periodic-scan/PAwR boundary applies the same conservative model
   to the second-largest 1,804-byte residual: four authenticated entry IDs and
   one exact NOP padding are exposed only through a typed fail-closed provider.
9. The master-connection boundary structurally decomposes the next 1,564-byte
   residual into three exact prologue/xref-delimited entries. Archive names are
   recorded only as probable correlations; address-derived IDs remain the
   enforceable contract until stronger source evidence exists.
10. The deployment-package audit authenticates the four-record stock container,
    124-byte metadata, 211,824-byte payload, 29 erase-sector IDs, canonical
    offsets, nonoverlapping target intervals, and zero alignment padding. The
    MIT parser/builder round-trips the 211,948-byte stock package byte-for-byte
    and emits the complete 212,984-byte mixed provider. This closes container
    generation and routes the 1,240-byte concrete-source frontier; QP/C
    placement and the retained controller replacement remain open.

The QP/C audit is supporting rather than additive. Its 22 portable functions
and 2,450 bytes overlap a separately defined application cluster, not the
residual ownership census. Adding them to 33,658 would double-count firmware
bytes. The ledger reports them as upstream-source evidence with selected tag
`v6.5.1` and also preserves that an exact vendor checkout has not been proven.

## Fail-closed invariants

The gate raises instead of producing a readiness report if any of these
conditions changes:

- residual-provenance file size or SHA-256;
- 175-span or 33,658-byte census;
- category counts or byte totals;
- interval size, overlap, or stock hash;
- MetaWare, first-party, tail, named hook-provider, or slave-connection
  candidate qualification status;
- an overlay range or hash mismatch;
- a missing or extra overlay span;
- QP/C cluster completeness or nine-entry hook table;
- each named provider's unique archive/object/address/normalized-body match;
- the WSF clean-room source identity, three-entry capacity, state offsets, and
  ARCv2-EM compile receipt;
- either named hook span's exact interval or stock hash;
- either controller boundary's segment/function/NOP tiling or stock hash;
- readiness counts `23 + 25 + 127`; or
- readiness bytes `1,240 + 8,348 + 24,070`.
- the exact EM9305 package receipt, four-record/29-sector shape, byte-exact
  stock rebuild, mixed-provider build, and fail-closed source/hardware policy.

Tests explicitly delete one tail decision, corrupt one MetaWare hash, corrupt
a named hook-provider hash, and mark the QP/C cluster incomplete. Each
mutation fails before the gate can claim zero unclassified bytes.

## Reproduction

```sh
python3 tools/analyze_em9305_source_readiness.py --json
make em9305-source-overlay
make em9305-arc-candidates
make em9305-qpc-component
make em9305-record-package
python3 tools/analyze_em9305_qpc_hook_provider_candidate.py --json
python3 tools/analyze_em9305_slave_connection_boundary.py --json
python3 tools/analyze_em9305_pawr_boundary.py --json
python3 tools/analyze_em9305_master_connection_boundary.py --json
python3 -m unittest -v tests.test_em9305_source_readiness
python3 -m unittest -v tests.test_em9305_qpc_hook_provider_candidate
python3 -m unittest -v tests.test_em9305_wsf_idle_tasks
python3 -m unittest -v tests.test_em9305_slave_connection_boundary
python3 -m unittest -v tests.test_em9305_pawr_boundary
python3 -m unittest -v tests.test_em9305_master_connection_boundary
```

The machine-readable report contains all 175 ledger records with exact stock
start, end, size, hash, readiness state, decision origin, and decision name.

## What remains before community-source firmware

Accounting opacity is closed for this residual census, but implementation
opacity remains material:

1. Provide independently derived behavior for the 25 typed boundary spans,
   including the first-party startup/MyApp paths and tail provider islands.
   For the resume/idle hook pair, the software-only WSF provider is implemented;
   the remaining provider work is hardware-specific UART resume and voltage
   measurement plus exact placement and ABI integration.
2. Replace or lawfully source the 24,070 unavailable controller/vendor bytes,
   plus the 6,494 typed controller-cluster bytes whose exact behavior is still
   unavailable.
3. Complete QP/C link placement, callback registration, and startup ordering;
   this is separate from the now-routed MetaWare/tail frontier.
4. Replace the retained record payload bytes with community source; the mixed
   provider wrapper cannot turn retained stock records into source.
5. Keep the whole-source gate blocked until every residual span is concrete
   source or an intentionally excluded optional feature with a reviewed
   public contract.

This ledger records the production-routed ARC overlay and mixed provider
receipt. It performs no hardware operation and does not claim the retained
controller bytes as community source.
