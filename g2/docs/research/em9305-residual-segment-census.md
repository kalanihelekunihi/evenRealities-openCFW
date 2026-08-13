# EM9305 residual segment census

Status date: 2026-08-08

## Result

The authenticated exact and link-order maps now identify function provenance
for 167,684 of the 210,888 EM9305 application bytes (79.513296%). The
remaining 43,204 bytes are no longer represented as one opaque remainder.
`tools/analyze_em9305_residual_segments.py` partitions them into 1,083
non-overlapping, hash-identified segments:

| Segment state | Segments | Bytes | Application share | Interpretation |
|---|---:|---:|---:|---|
| Stock-retained vector table | 1 | 264 | 0.125184% | Format and all 66 words identified; no source replacement |
| Stock-retained ARC `nop_s` alignment | 906 | 1,812 | 0.859223% | Fully classified linker/function-boundary padding |
| Stock-retained post-text tables/data | 1 | 7,470 | 3.542166% | Non-code linker tail identified; individual table semantics partial |
| Stock-retained unresolved code or mixed content | 175 | 33,658 | 15.960130% | Remaining reverse-engineering queue |
| **Residual total** | **1,083** | **43,204** | **20.486704%** | All bytes remain cut forward |

Thus 9,546 residual bytes (4.526573% of the application) are structurally
classified non-code. The unresolved code-or-mixed search space is 33,658
bytes, not the earlier 55,922-byte exact-match complement. This is a
classification improvement only: no EM9305 application byte is yet emitted
from recreated source.

## Structural boundaries

### Vector table

`[0x00302400,0x00302508)` is a 264-byte, 66-word vector table, SHA-256
`8a75d411f79f380a21da285778a62241d3b2acc236244ac46c51bbd814d82779`.
Its first word is stack value `0x001003D0`; the remaining 65 words contain 58
application handlers and seven EM ROM handlers in `[0x00100000,0x00110000)`.
The following 16 bytes remain in the unresolved executable/mixed tier rather
than being folded into the table.

### Alignment

The ARCv2 EM instruction `nop_s` encodes as little-endian bytes `E0 78`.
Only complete runs at the beginning or end of a gap between authenticated
function-provenance intervals are classified as alignment. Interior NOPs are
left with their surrounding code. The census finds 906 boundary segments /
1,812 bytes; every segment carries its own SHA-256 in the dynamic report.

### Post-text tables and data

The final exact SDK function is `wsfTimerUpdateTicks` at
`[0x00333E4C,0x00333E9A)`. The immediately following
`[0x00333E9A,0x00335BC8)` range is the 7,470-byte post-text linker tail,
SHA-256
`802191f5b086b2a3c66f2775cd3686d31faead39e929372b70f1462d824eca45`.
It contains dense fixed-width tables plus the authenticated QP/WSF module
strings `MyApp`, `qf_dyn`, `qf_act`, `qep_hsm`, `qf_actq`, `qf_mem`, and
`WsfOs`. The range is confidently non-code, but table-by-table behavioral
semantics remain partial, so it is not marked fully reverse engineered.

## NOP-aware function-provenance increment

After the strict 36-range link-order result, a second pass removes only the
authenticated boundary NOPs before applying exact-neighbor ordering. It
permits up to eight unique intervening archive symbols when their sizes
exactly tile the trimmed stock gap. A single intervening symbol may differ by
at most 32 bytes and must be at least half of the stock span; this identifies
a modified upstream function but does not claim its exact internal boundaries
from archive size.

The extension identifies 120 ranges / 156 functions / 9,818 stock bytes:

| Evidence state | Functions | Stock bytes |
|---|---:|---:|
| Newly byte-exact archive bodies | 34 | 774 |
| Low-compared-byte placements | 48 | 480 |
| Relocation-only placements | 32 | 128 |
| Same-size modified upstream functions | 29 | 4,496 |
| Singleton modified functions with 2–32-byte size delta | 13 | 3,940 |

Together with the strict pass, link order identifies 202 functions / 11,934
bytes. Four vector-ABI placements add 760 identified bytes, including three
exact handlers / 574 bytes. Six authenticated archive-order prefix leaves add
24 exact bytes. Exact coverage is now 1,494 functions / 157,122 bytes in 875
merged intervals (74.504950%). Function provenance, including non-exact
placements, is 167,684 bytes in 879 intervals (79.513296%).

Lorelei independently compared all 29 same-size functions after masking ARC
relocations. Of 3,868 meaningful bytes, 3,815 match and 53 differ (98.630%
aggregate). Per-function similarity ranges from 93.750% to 99.451%; every
function differs, so none was incorrectly promoted to exact coverage. The
comparison report SHA-256 is
`320d5a03455fc7fac0e60c237834d3e475dd7491e959724633fc9fc7cf30063f`.

GNU ARC opcode-sequence comparison separately validates all 13 accepted
size-delta functions. It aligns 1,225 instructions across 1,256 archive and
1,298 stock instructions; per-function sequence ratios range from 86.364% to
99.387%. The pinned report SHA-256 is
`252f5993438fec92c82f99945e9b5a5f5c0b54e9c6a6ea196c76623343a0c2d7`.
The size-ratio guard rejects `lctrActPeerPhyReqWithCollision`, whose four-byte
archive relocation stub is too small to establish the 36-byte stock span.

## Lorelei round-three result

`tools/manifests/em9305-ghidra-residual-round3.tsv` assigns 16 individual
entries from the newly identified sleep-manager, NVM, HCI, periodic-data,
crypto, connection-allocation, master-init, path-loss, and PAwR/BIG gaps.
Lorelei completed all isolated projects in 16.766–17.023 seconds (16.901-second
mean) with no process failure. The returned `results.tsv`, `INPUTS.tsv`,
`CONFIG.tsv`, and `SHA256SUMS` hashes are:

- `8ac5db441830be8a84c4e5c449ebeab14f3eadcbd7e8ad4976b169db2edbea6e`;
- `b07aa83a1ad6c7c5e63dfd794b4ce1cac8d62ca0d281d9857a82c90d8529e577`;
- `e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`;
- `a295af90486b1ce08cd2e4cdc54114081e88f6b08409df96641f083aa63904bc`.

The experimental ARCompact processor produced constructor/p-code failures for
15 entries and a function-creation failure for the remaining crypto entry.
None is semantic evidence. GNU ARC, archive identity, and link order produced
the accepted findings; the failed Ghidra outputs remain useful negative
evidence about that processor module. The verified return is preserved under
`opencfw-em9305-ghidra-residual-round3-return.B1XMm7/output` in the
repository-owned Lorelei corpus at `research/corpus/`; the remote directory
is now a disposable working copy.

Round four assigns 16 previously unprocessed residual spans / 5,922 bytes via
`tools/manifests/em9305-ghidra-residual-round4.tsv`. Lorelei completed every
isolated project in 17.217–17.502 seconds (17.341-second mean). Thirteen entry
decompilations hit the known constructor defect; three coherent outputs expose
a return-12 leaf and two interrupt-context wrappers. Vector ABI plus normalized
archive matching now resolves the sampled wrappers and their paired timer/radio
entries; the return-12 leaf remains candidate-only. The
returned results/input/configuration/SHA-ledger hashes are `a7630016…8097`,
`85ec123b…becb`, `e7a730cf…75ae`, and `403d6da1…76a` respectively; full paths
and identities are in the [Lorelei benchmark](lorelei-re-acceleration-benchmark.md).

## Reproduction identities

The extended link-order JSON hashes to
`3551b7cfec594daaa627e2e2587dd276c956a241f1758b53b5c848d2d31fb4da`.
The complete 1,083-segment residual JSON hashes to
`7ccc95f55845f9619bc39503dfd255f9fd5f5269040fe464c8067677a08b3ac1`.
Both are regenerated from authenticated archive reports, the official
firmware, and the whole-application GNU ARC disassembly. The checked-in tools
enforce all totals, structural hashes, archive identities, compiler anchors,
and non-overlap invariants; temporary JSON files are not independent sources
of truth.
