# Apollo main AM-015 bounded reconstruction audit

Date: 2026-09-12. Scope: `0x0044FA5E..0x004501D2` (32 retained functions,
1,676 function bytes; 1,908-byte assigned span).

## Evidence and current conclusion

The current `g2/build/source/flash-plan.json` still classifies the intersecting
production region as `official_blob` (`0x0044F76A..0x00454770`); no AM-015
entry is routed in `components/apollo_main/core_overlay/overlay.json`, and no
function in this range is present in `tools/transparent/reviewed_sources.json`.
The range therefore remains entirely unresolved and no source-owned bytes are
claimed.

The bounded corpus record is
`research/corpus/apollo-main/ghidra/decomp/functions.jsonl`. It provides exact
body ranges and SHA-256 values, but identifies every target as `FUN_*` with an
unknown calling convention or decompiled signature. The first twelve targets
(`0x0044FA5E..0x0044FC62`, 462 bytes) share helper `0x0044FA1A`; the next five
(`0x0044FC62..0x0044FD68`, 238 bytes) share `0x0044D25C` and
`0x0044FA1A`; later targets call `0x0044FFE6`/`0x004503xx` or other retained
addresses. This is evidence of a related helper cluster, not proof of LVGL or
an identified upstream family.

The prior AM-015 result recorded no completed segments and no validation. The
parallel LVGL source files in the working tree cover different addresses
(`0x0048C7B4..0x0048D866`) and are deliberately not reused for this item.

## Next discriminating work

Recover bounded decompiler body excerpts and caller/callee context for the
`0x0044FA1A`, `0x0044D25C`, `0x004503xx`, and `0x00482F8A` dependencies; then
classify the first helper cluster against the pinned upstream inventories before
writing production C. A candidate is admissible only after ABI review,
source-authored implementation, host oracle tests, overlay routing, and the
component/source gates. Hardware qualification remains blocked by unavailable
physical evidence; no hardware operation was performed.

## 2026-09-12 bounded helper-cluster evidence

The authenticated Ghidra excerpt in `research/corpus/apollo-main/ghidra/full64-j64/logs/apollo-01.log` (lines 9540--9650) shows `FUN_0044FA5E` as a null-defaulting setter for 32-bit fields at object offsets `0x10` and `0x14`, followed by invalidation through the object word at `0x2BC`. Paired accessors select dimensions using mode bits `0..2` at offset `0x2FC`; callers show UI layout use. The object ABI, callback, and exact LVGL configuration remain unproven, so no bytes are admitted.

## 2026-09-12 bounded oracle receipt

`python3 g2/tools/emulate_g2_lvgl_display_accessors.py --iterations 40 --seed 0x4c56474c` passed all 13 accessor leaves (520 vectors), including result, object writes, and mocked callback traces. This is differential evidence only: the candidate still calls retained callbacks at `0x0044FA1A` and `0x00440656`, and remains unrouted.

Input hashes: `lv_display_accessors.c` `7c08fcad51f616508639ac517108ac20b8994cf7e7e1b630b902d3d585fe7b28`; verifier `463af7124eab22beba346bf4988d7f16095ff4bce7fa4fa30dfea2a0f56c84e7`.

## 2026-09-12 reconstruction-tooling continuation

Fresh retention inspection still reports only the containing official region
`0x0044F76A..0x00454770`; the assigned interval is not routed. The existing
13-leaf emulator was rerun and passed 520 vectors, including object writes and
mocked callback traces. This strengthens differential evidence only: the
candidate still depends on retained callbacks `0x0044FA1A` and `0x00440656`,
and the remaining 19 functions lack a reviewed source/configuration closure.
No AM-015 bytes are source-owned. Hardware qualification remains blocked by
unavailable physical evidence; no hardware operation was performed.

## 2026-09-12 bounded callback-closure probe

The decompiler bundle identifies the shared null-object dependency
`FUN_0044FA1A` as a read of `*(uint32_t *)(DAT_0044FCF0 + 0x14)`; the first
12 accessor-like leaves in the assigned span call it when their object
argument is null. Their non-null paths read distinct object offsets, while
the error paths call `FUN_0044D25C` with retained format/global operands.
This proves a global-backed object-provider dependency, but not the type,
ownership, initialization order, or a clean-room replacement. The dependent
`FUN_0044D25C` logging ABI is likewise unresolved. No source ownership or
production routing is claimed.

## 2026-09-12 bounded continuation: exact ABI boundary remains open

The authenticated Ghidra log excerpt at `full64-j64/logs/apollo-01.log`
lines 9540--9650 confirms that `FUN_0044FA5E` is a four-argument setter:
null selects `FUN_0044FA1A`; non-null stores arguments 2 and 3 at object
offsets `0x10` and `0x14`, then calls `FUN_00440656` with the word at offset
`0x2BC`; it returns argument 4. The adjacent accessors at `0x0044FA7E`,
`0x0044FAA8`, `0x0044FAD2`, and `0x0044FB10` select words from the first
four-word record according to the low three bits of byte offset `0x2FC`, with
the null case again delegated to `FUN_0044FA1A`.

This narrows the semantic shape but does not establish a source-owned object
type or initialization owner. The remaining leaves have independent calls to
`FUN_0044D25C` and `0x00450346/0x00450388/0x00450390`; the corpus identifies
those callees but supplies no reviewed ABI/configuration closure. Therefore
zero AM-015 bytes are admitted, and the next wake condition is provider
initialization plus logging ABI evidence.
