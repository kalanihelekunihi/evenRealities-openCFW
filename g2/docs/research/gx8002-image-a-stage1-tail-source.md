# GX8002 image-A boot-region tail: pad, CRC trailer, XIP length word

Work item CD-009 (package `[0x0000B58C, 0x0000C650)`, 4,292 bytes). Status:
**partial**. 4,100 of those bytes (95.5%) are now reviewed, source-generated
BINH container bookkeeping; the remaining 192 bytes (the first instructions
of the image-A stage-2 XIP text) are unchanged and still an opaque,
externally-supplied span.

## What this closes

`gx8002-image-a-sram-stage1-boundaries.md` (Wave 5) and
`gx8002-image-a-xip-boundary.md` (Wave 4) previously treated the whole
12,288-byte image-A BINH stage-1 block (package `[0x0000958C, 0x0000C58C)`)
and the whole 36,484-byte stage-2 XIP text (package `[0x0000C590,
0x00015414)`) as single opaque spans, each behind one `authenticated_
segment_load` typed provider (`runtime_gx8002_image_a_stage1_boundary.c`,
`runtime_gx8002_image_a_xip_boundary.c`), because "the header load field and
vector-address space do not alone prove the complete ROM copy/remap
behavior."

Inspecting the actual bytes inside that stage-1 block shows it is not
uniformly opaque: its real vector table and boot code occupy only its first
part (well inside CD-008's assigned span, package `[0x0000958C,
0x0000B58C)`); package `[0x0000A837, 0x0000C588)` — which includes all of
this item's stage-1-block bytes — is a contiguous run of zero bytes, and the
block's own trailing 4-byte word is not further opaque code but the block's
own CRC-32/MPEG-2 checksum. Immediately after the block sits the public
BINH stage-2 XIP-text length word, also pure format metadata.

Both facts are already independently authenticated in this repository:
`tools/analyze_g2_codec_fwpk_segments.py`'s `parse_binh_image` computes and
checks the same CRC-32/MPEG-2 trailer (`crc32_mpeg2(blk[24:STAGE1_BLOCK-4])
== stored`) and reads the same XIP-length word, for both image A and image
B, as part of its existing fail-closed BINH parser. This item adds no new
trust assumption; it packages that already-verified arithmetic as
production-routable reviewed source instead of leaving it folded into the
monolithic opaque span.

### Byte accounting for this item's range

| Package range | Size | Content | Disposition |
|---|---:|---|---|
| `[0x0000B58C, 0x0000C588)` | 4,092 B | BINH stage-1 block zero-fill pad | now `generated_source_data` |
| `[0x0000C588, 0x0000C58C)` | 4 B | BINH stage-1 block CRC-32/MPEG-2 trailer, `0x21C58EDB` LE | now `generated_source_data` |
| `[0x0000C58C, 0x0000C590)` | 4 B | BINH stage-2 XIP-text length word, `0x00008E84` LE | now `generated_source_data` |
| `[0x0000C590, 0x0000C650)` | 192 B | first 192 bytes of image-A stage-2 XIP text | **unchanged**, still `retained_stock` behind `runtime_gx8002_image_a_xip_boundary.c` |

The 192-byte remainder is genuinely dense, varied executable content (not
padding); it was not decompiled by this item and remains covered end-to-end
by the existing 36,484-byte XIP typed boundary.

## Implementation

- `components/shared/gx8002/runtime_gx8002_image_a_stage1_tail.[ch]`: a
  4,100-byte `.data.open_cfw_gx8002_image_a_stage1_tail` array. Bytes
  `[0, 4092)` are implicit-zero (C99 leaves non-designated initializer
  elements zero); bytes `[4092, 4096)` and `[4096, 4100)` are the CRC
  trailer and length word as C99 designated initializers. No instruction,
  model weight, or command byte is present; this is data placement, not
  code.
- `tools/verify_gx8002_image_a_stage1_tail.py`: compiles that source with
  the project's standard GX8002 `FLAGS`, extracts the compiled `.data`
  section, and independently recomputes the expected trailer/length word
  from the authenticated stock image via
  `analyze_g2_codec_fwpk_segments.parse_fwpk`/`parse_main_image` (which runs
  the CRC algorithm itself, not the literal in the C source). It requires
  the compiled bytes to equal *both* that independent recomputation and the
  raw stock bytes at package offset `0x0000B58C`, and separately asserts the
  4,092-byte pad span is all-zero in the stock image. `ownership_kind` is
  `generated_source_data`, matching the category `build_gx8002_source_
  candidate.py` already uses for `wakeword-parameters` (data placed by
  reviewed source at an exact stock offset, checked byte-for-byte, as
  opposed to `compiled_c`/`compiled_assembly` for instruction bodies).
- `tests/test_gx8002_image_a_stage1_tail.py`: runs the verifier, checks the
  zero-fill assumption directly against the blob, re-derives the CRC
  trailer a second, independent way (straight off the raw stage-1 block
  bytes rather than through the cached `parse_main_image` result), and
  checks the comparison is discriminating (a mutated copy no longer matches
  stock).

## Boundary behavior and ownership

The CRC-32/MPEG-2 trailer is a checksum over content that is *itself* still
mostly `retained_stock` (CD-008's header+code span). Recomputing a checksum
of still-proprietary content does not license that content; it only proves
the trailer word itself carries no independent proprietary information
beyond "checksum of whatever is next to it," exactly as
`build_gx8002_source_candidate.py`'s own FWPK/UART header regeneration in
`compose()` already treats record CRCs. The XIP length word is likewise a
public format field (payload size), not itself executable or model content.

Neither fact changes the identity, license, or redistribution status of the
bytes the checksum covers. `runtime_gx8002_image_a_stage1_boundary.c` and
`runtime_gx8002_image_a_xip_boundary.c` are untouched by this item and keep
authenticating their full monolithic spans (12,288 and 36,484 bytes
respectively) against the unmodified stock image; this item's 4,100 bytes
are a strict subset of what those boundaries already cover, reclassified
here at finer grain, not removed from their existing coverage.

## Readiness delta (this item only; central GX8002 ledger not edited)

| | Before | After |
|---|---:|---:|
| Reviewed source-generated (this item) | 0 B | 4,100 B |
| Opaque/typed-external (this item) | 4,292 B | 192 B |

`docs/research/gx8002-source-readiness-ledger.md` and
`tools/manifests/gx8002-source-readiness.tsv` still fold this item's whole
4,292-byte range into their existing monolithic `image_a_stage1` /
`image_a_xip_text` rows; splitting those rows to reflect this finer-grained
accounting is left as follow-up (see `docs/progress.md` entry) rather than
edited here, to avoid an uncoordinated concurrent edit to that
cross-cutting, actively-shared ledger while other GX8002 items are in
flight.

## Registration

Registered as a `generated_source_data` tranche in
`tools/build_gx8002_source_candidate.py` (import + one tuple entry) and in
the `gx8002-source-candidate` test list in `Makefile`, under the CD-009
integration lock, alongside the existing ~150 registered GX8002 tranches.

## Verification

```sh
python3 g2/tools/verify_gx8002_image_a_stage1_tail.py
python3 -m unittest g2.tests.test_gx8002_image_a_stage1_tail
make -C g2 gx8002-source-candidate
make -C g2 codec-source-experimental
```

All software-only. Hardware qualification remains **blocked by unavailable
physical evidence**, unaffected by this item (this item makes no runtime
mapping or execution claim; it only reconstructs container bookkeeping
bytes already parsed and checked by existing tooling).

## Remaining work in this item's range

The 192-byte remainder (`[0x0000C590, 0x0000C650)`, the start of image-A
stage-2 XIP text) has varied, dense byte content — real code, not padding —
and was not decompiled by this item. No Ghidra function-level analysis of
image A's own XIP/stage-1 address space exists yet in this repository (the
existing `gx8002-known-function-harvest.json` load address, `0x10003000`,
is image B's backup-runtime base, not image A's). Follow-up should either
attempt C-SKY decompilation of that 192-byte entry stub against an assumed
public-default XIP base (`0x10200000` + flash offset, per
`gx8002-image-a-xip-boundary.md`) with the same decoded-trace-verifier
pattern used elsewhere in this codec, or leave it to the existing
`runtime_gx8002_image_a_xip_boundary.c` typed boundary.
