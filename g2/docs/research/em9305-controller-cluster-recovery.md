# EM9305 modern-controller cluster function recovery

Status date: 2026-08-13

Current readiness supersession: the later
[`em9305-slave-connection-boundary.md`](em9305-slave-connection-boundary.md)
adds an MIT typed fail-closed integration seam for the first 3,126-byte
cluster. The proprietary provenance and source-unavailable conclusions below
remain unchanged; the new seam does not admit or relicense vendor source.
The subsequent [`em9305-pawr-boundary.md`](em9305-pawr-boundary.md) applies
the same readiness treatment to the second 1,804-byte cluster.

## Result

The two largest high-confidence modern-controller residual segments from the
[residual provenance audit](em9305-residual-provenance-audit.md) are now
function-resolved.  `tools/analyze_em9305_controller_clusters.py` pins ten
functions / 4,920 bytes plus ten interior `nop_s` padding bytes, exactly
tiling both segments with zero remainder.  The machine-readable map is
`tools/manifests/em9305-controller-cluster-map.tsv`, SHA-256
`5f9c7aa69a12345da365491f09849277778e88abc4eb632600d23dcaf426209a`.

| Recovery tier | Functions | Bytes | Meaning |
|---|---:|---:|---|
| `opcode_sequence_exact_size_exact` | 3 | 70 | mnemonic stream and size match the SDK archive body |
| `vendor_modified_opcode_aligned` | 5 | 4,300 | sequence ratio ≥ 0.85 at the pinned link-order position |
| `vendor_modified_divergent` | 2 | 550 | role pinned by bracket anchors and shared constants; implementation substantially extended |

Every identification rests on three independent legs: the authenticated
`lib_emb_controller_iso.a` link order (sorted `.text.*` section placement
between exact stock anchors), GNU ARCv2 EM mnemonic-stream alignment (the
acceptance method of
`compare_em9305_size_delta_sdk_functions.py`), and raw-byte/NOP tiling
against the official blob.  The archive side was exported on Lorelei from the
hash-pinned ISO archive (SHA-256 `87af23b9…6cfa`, Git blob `b9433012…`) with
GNU binutils 2.46; the deterministic return is repository-owned at
`research/corpus/em9305/cluster-recovery/return/cluster-objects.json`,
SHA-256 `0d3d7aebedbbba034bedd430d932047719df12bedd35133c82cd245967bf71c3`,
with compiler-comment anchors `LLVM 14.0.6/T-2022.09. (build 004)`,
`(EM-Micro)`, `-arcv2em`, `-Os` verified on every candidate object.

## Cluster 1: slave connection, `[0x00329888,0x0032A4BE)` — 3,126 bytes

Bracket anchors: `lctrSlvConnDisp` (left, exact stock body) and
`lctrSlvConnUpdateOp` (right).  Six intervening archive symbols tile the
segment in link order:

| Stock span | Size | Identity | Archive size | Ratio (matched) | Tier |
|---|---:|---|---:|---|---|
| `[0x00329888,0x00329FD6)` | 1,870 | `lctrSlvConnEndOp` | 1,866 | 0.9652 (569/588) | modified |
| `[0x00329FD8,0x00329FFE)` | 38 | `lctrSlvConnExecute` | 38 | 1.0000 (13/13) | opcode-exact |
| `[0x0032A000,0x0032A216)` | 534 | `lctrSlvConnExecuteSm` | 554 | 0.8895 (165/187) | modified |
| `[0x0032A218,0x0032A22E)` | 22 | `lctrSlvConnResetHandler` | 22 | 1.0000 (7/7) | opcode-exact |
| `[0x0032A230,0x0032A47C)` | 588 | `lctrSlvConnRxCompletion` | 554 | 0.9424 (180/185) | modified |
| `[0x0032A47C,0x0032A4BE)` | 66 | `lctrSlvConnTxCompletion` | 38 | 0.5789 (11/14) | divergent |

Four interior `nop_s` paddings at `0x00329FD6`, `0x00329FFE`, `0x0032A216`,
and `0x0032A22E` are verified raw bytes (`E0 78`); bodies plus padding total
exactly 3,126 bytes.

`lctrSlvConnTxCompletion` is the second documented divergent-implementation
case (after `lctrCenSendPendingRspRptHandler`).  Its role is pinned by the
link-order position and by shared connection-context offsets `341` and `630`
present in both bodies, plus the same counter-increment tail pattern; the
stock body adds a completion-event case `0xA` (branch to a `910`-stride
counter leaf) and a second counter global `0x0080568C`.  It is not claimed as
the same implementation, and it is excluded from any exact-coverage account.

## Cluster 2: master periodic scan / PAwR, `[0x00321C30,0x0032233C)` — 1,804 bytes

Bracket anchors: `lctrMstPerScanRxPerAdvPktHandler` (left, exact) and
`lctrMstPerScanWithRspEndOp` (right).  Four intervening symbols tile the
segment:

| Stock span | Size | Identity | Archive size | Ratio (matched) | Tier |
|---|---:|---|---:|---|---|
| `[0x00321C30,0x00321E14)` | 484 | `lctrMstPerScanRxPerAdvPktPostHandler` | 500 | 0.8204 (137/170) | divergent |
| `[0x00321E14,0x00322178)` | 868 | `lctrMstPerScanTransferOpCommit` | 868 | 0.9435 (267/283) | modified |
| `[0x00322178,0x00322182)` | 10 | `lctrMstPerScanWithRspAbortOp` | 10 | 1.0000 (3/3) | opcode-exact |
| `[0x00322184,0x0032233C)` | 440 | `lctrMstPerScanWithRspCommitOp` | 432 | 0.9231 (132/141) | modified |

One interior `nop_s` at `0x0032182` is raw-verified.  The `WithRspAbortOp`
leaf is a three-instruction tail stub (`ld_s r1,[r0,0x24]; b.d; stb 1,[r1,8]`)
whose stock `b.d` targets `0x0032233C` — exactly the right anchor
`lctrMstPerScanWithRspEndOp`, the relocation analogue of the archive's
zero-relocated branch.  `lctrMstPerScanRxPerAdvPktPostHandler` falls below
the 0.85 modified floor (0.8204) and is recorded as divergent: its role is
link-order-pinned between exact anchors, and its call frontier
(`BbGetClockAccuracy`, `LmgrBuildRemapTable`, `PalFrcDeltaUs`,
`SchBleCalcAdv*`) matches the periodic-advertising post-processing role, but
the body is vendor-modified beyond the alignment floor.

## Effect on the retention recommendation

Function-level identity **strengthens and sharpens** the proprietary-retention
recommendation; it does not weaken it.  Concretely:

- Provenance confidence rises from segment-level call-frontier inference to
  per-function link-order + opcode evidence for 4,930 of the 33,658 residual
  bytes (two clusters, padding included).
- The ownership category is unchanged: all ten functions remain
  `proprietary_modern_controller_source_unavailable`.  The SDK oracle that
  supplies the identities has no repository-level license; opcode-sequence
  identity with a license-gated archive is provenance evidence, not source
  availability.  The residual map rows for both clusters still read
  category 4 / `packetcraft_modern_controller` / high, and a fail-closed
  test now pins that join.
- The three opcode-exact functions (70 bytes) are *not* promoted to
  byte-exact coverage: this lane compares mnemonic streams only and does not
  re-run relocation-masked byte comparison.  A follow-up through
  `compare_em9305_sdk_archive.py`'s masking lane could add them to the exact
  map if the bytes agree after masking.
- The two divergent bodies (550 bytes) are the sharpest evidence yet that the
  stock controller is a **newer/differently-configured Packetcraft build**
  rather than the SDK v4.2 profile: same symbols, same link order, extended
  implementations.  That reinforces that authoritative modern source is
  unavailable and that retention behind the controller boundary is the
  correct disposition until licensed source is obtained.

## Reproduction

```sh
python3 tools/analyze_em9305_controller_clusters.py --json
python3 tools/analyze_em9305_controller_clusters.py \
  --tsv tools/manifests/em9305-controller-cluster-map.tsv
python3 -m unittest tests.test_analyze_em9305_controller_clusters
```

Inputs are the official blob, the authenticated whole-application objdump,
and the repository-owned Lorelei object-disassembly return; all three are
hash-pinned in the analyzer.  The Lorelei extractor used for the return is
preserved at `research/corpus/em9305/cluster-recovery/cluster_extract.py`
(SHA-256 `edd498a0a9aea5f87332f9e8fcdf234fb61d7b6702c96c23acd7ea14bfb07be7`);
it authenticates the ISO archive and objdump before exporting deterministic
GNU ARC disassemblies and is re-runnable on any host with ARC binutils 2.46
and the pinned archive.  No Ghidra ARC lane was used: per the
[Lorelei benchmark](lorelei-re-acceleration-benchmark.md), the experimental
ARCompact processor's constructor/p-code failures give it low expected
semantic value for this target, and GNU ARC plus authenticated archives is
the higher-confidence semantic path.

## What remains gated

1. The other 173 residual segments (28,728 bytes) keep their segment-level
   classification; the same link-order bracket lane applies wherever exact
   anchors surround a gap, which is the natural next tranche.
2. Byte-level (relocation-masked) verification of the three opcode-exact
   functions is a bounded follow-up in the existing masking lane.
3. Behavioral semantics of the five modified and two divergent bodies are
   only partially recovered; the 912-byte stock `lctrConnCtx_t` stride and
   connection-event bookkeeping deltas documented in the link-order ledger
   are consistent with, but do not complete, their reverse engineering.
4. Licensed modern Packetcraft/EM source remains the only path from
   identification to source ownership; every byte here stays hash-pinned
   stock retention.
