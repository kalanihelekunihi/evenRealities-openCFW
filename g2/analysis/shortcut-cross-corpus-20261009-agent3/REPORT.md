# Registered cross-corpus scan, 2026-10-09

This finite P2 pass found reusable exact provider identifications outside the
eleven-object NationalChip inventory, and reauthenticated existing dependency
families. It changes no campaign evidence, firmware source, tool installation,
submodule, or gate. Exact provider bytes, relocation candidates, lexical source
anchors, target body boundaries, and admitted pseudocode coverage remain separate.

## Scope and authentication

All six locked payloads passed their target.json size and SHA-256 checks. The
33 image registry records reduce to 32 distinct content hashes after alias
deduplication. Every scanned image is rehashed against its registry; codec
candidate runtime mappings retain their existing conditional status. Some
images are containers or models: repeated occurrences in their nested children
are explicitly not additive code discoveries.

`scope.json` fixes the finite filesystem corpus: 2,557 `.a/.o/.elf/.axf`
artifacts and 34,282 C/header/assembly sources under `third-party`, including
registered vendor and compiler packages. Git metadata is excluded. Binary
artifacts have fresh full hashes; positive source anchors carry full source
hashes. `submodule-pins.json` compares each initialized checkout HEAD to its
recorded gitlink. These hashes authenticate the locally available inputs;
matching a newer compiler package does not identify the producing compiler.

The independently replayed default unified scan examined 287,285 ELF members
and 570,457 sized ARM/older-ARC/ARCv2/C-SKY functions, skipping 474,276 duplicate
function/relocation fingerprints. Its current receipt is `summary.json`.
Historically, the initial scan examined 476,959 non-ARCv2 functions and skipped
391,195 duplicates. Native inspection exposed ARCv2 ELF machine 195; a separate
supplement examined 93,498 functions and skipped 83,081 duplicates. Its
`arc2-summary.json` now reports ARCv2-only matches (61 exact, zero masked),
with the combined result separately named. The historical function counts sum
to the unified count; ELF member counts describe two visits to the same corpus
and must not be added. The reusable scanner includes all four families. Accepted search
anchors are at least 24 bytes and have at least five distinct byte values.
ELF64, big-endian, unsized symbols and non-ELF proprietary objects do not receive
function attribution from this scanner.

## Results and useful discriminators

Final inventory: 545 exact byte occurrences and 462 C-SKY relocation-mask
candidates. These are occurrence counts, including container aliases, not a
firmware coverage denominator. Independent native `ar` and `readelf` extraction
reproduced all 168 unique exact provider functions, including archives with
duplicate member names. Every selected exact extent rejects a single-bit
mutation; shifted placements are recorded independently in `validation.json`.

Useful exact identifications include:

| Family | Examples | Target occurrence |
| --- | --- | --- |
| IAR DLIB | `_GetN` (34 bytes), `_UngetN` (26), `ranmatch` (70) | Apollo main `0x004D15FA`, `0x004D161C`, `0x004D2112` |
| IAR shared runtime | `strcspn`, `strspn`, `_PutcharsDefault`, `__iar_zero_init3` | Exact occurrences in main and bootloader, individually recorded |
| C-SKY DSP archive | `csky_cos_f32`, `csky_sin_f32`, forward/inverse radix4 butterfly, Q15 split/shift/copy/fill helpers | `binh_b_stage2` image offsets `0xBE64`, `0xBEE4`, `0xC3FC`, `0xC610`, etc. |
| NationalChip VUI archive | `LvpCTCModelInitSnpuTask` (52 bytes) | Codec image occurrences recorded without admitting a runtime/body boundary |
| ARCv2 vendor/runtime | `PML_SetDcdcTimingConst`, protocol/sleep timer leaves, QPC queue initialization, libc helpers | 58 record-3 and three record-1 exact occurrences |

`_GetN` and `ranmatch` overlap historical body entries with no scoped pass in
the existing rescan ledger. The full such shortlist is saved separately. This
is a concrete priority discriminator for future bounded pseudocode review;
the historical catalogue is not an independently admitted canonical ledger.
Other identifications can overlap prior runtime/DSP/vendor evidence, so this
report does not count them as newly recovered code. The EM9305 consolidated
reference already records 1,494 relocation-normalized archive functions;
these new raw comparisons do not add that historical figure to this scan.

C-SKY masking is restricted to recorded four-byte relocations of known types
1 and 19. These 462 occurrences remain candidates. No masked call is accepted
without destination validation; the prior `npu_dis_interrupt` versus
`npu_en_interrupt` branch-target contradiction remains authoritative. This
scan's longer anchor cutoff excludes that misleading short-anchor case.
ARM/ARC relocation bytes are never masked here. A failed raw match cannot prove
absence of the library after relocation or a different compiler/configuration.

Source scanning found 247 long literal anchors, concentrated in Cordio-bearing
AmbiqSuite and LVGL sources. Each stores the original source path/line/hash and
authenticated stock image/offset. These are lexical lineage evidence. Shared
logs, assertion messages and copied source text do not establish producing
source identity or control-flow equivalence. Structural relationships remain
the already reviewed TLSF/provider analyses; this scan adds no structural oracle.
Ghidra-MCP, Ablation and REA offer no independent exact-byte comparator beyond
the native archive/ELF index used here, so this pass uses the reproducible index.

## Finite boundary

All enumerated local artifacts were visited; native extraction validated every
unique exact provider result. No new repository acquisition is justified by
these positives: they come from registered IAR, C-SKY, NationalChip, Ambiq and
EM9305 families. No submodule edit or repinning was made. A narrower producing
package, unsized/proprietary object parser, genuinely new source artifact, or
new authenticated target-body discriminator can reopen a bounded comparison.
The unsupported formats and relocation obligations are explicit limitations,
not a claim that all firmware semantics have been exhausted.

Reproduce with `python3 scan.py`, `python3 validate.py`, then
`python3 finalize.py` from this directory. The retained ARCv2 supplement was
run as `python3 scan.py --arc2-only` following the initial historical scan;
the default scanner now performs the corrected unified pass directly, and its
independent replay is the current `summary.json`. `final-summary.json` embeds
the supplement as historical evidence with an explicit scope, rather than
mixing its ARCv2-only function counts with combined match counts.
`authentication.json`, `binary-artifacts.json`, `classified-matches.json`,
`string-anchors.json`, `validation.json`, and `SHA256MANIFEST.json` retain the
reviewable evidence. No cybersecurity classifier blocked this work.
