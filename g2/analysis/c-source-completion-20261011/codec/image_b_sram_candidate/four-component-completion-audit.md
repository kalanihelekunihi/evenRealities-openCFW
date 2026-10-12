# Four-component C completion audit (2026-10-11)

This is a finite audit of the current **source** evidence, not a claim that any
complete product image is ready to flash. Counts describe the named candidate
graphs and are not interchangeable with whole native-body coverage.

| Component | Confirmed current source result | Precise remaining source/image gate | Next evidence that can close it |
| --- | --- | --- | --- |
| CASE | Experimental ARM source ELF links with zero undefined symbols (`m0/case_semantic_corrected_round.elf.receipt.json`); native-address-named B/D symbols checked in the local source ELF have no observed placement mismatch. CRT's 420 initialized bytes and the retained logger format corpus have bounded native/source oracles (`m0/WHOLE_IMAGE_GAPS.md`). | ELF text exceeds official CASE occupied payload; entry/section ordering, package fields, and whole executable-body equivalence remain unproved. Zero command/startup imports is only graph closure. | Authoritative flash partition/loader constraints, final relocatable section map, and whole-body/indirect-root comparisons. Stock occupied length alone is not a hardware partition bound. |
| Touch | 58/58 selected C units compile; four genuine generated-data imports remain (`touch/REPORT.md`). Named reset-copy objects account for all but one 426-byte interval. | `touch_generated_lp_history` at RAM `0x2000065e` has an unknown generated element count; the next named object at `0x20000808` bounds a gap, not necessarily allocation size. `touch_generated_internal_context` at `0x20000c50` has native writes through offset 117 but no complete generated declaration. ROM common/widget configuration at `0xb2a8`/`0xb0f8` lacks the product option set. Final ROM/RAM scatter is open. | Product `cycfg_capsense.c/.h` or equivalent authenticated generated map/configuration. The pinned v6 PDL proves `cy_stc_capsense_lp_historic_context_t` is `uint16_t` (`capsense-v6-reference/cy_capsense_structure.h:1914`) and the context contains a pointer (`:1968`); it does not prove the array count or optional fields. |
| Codec A | Latest combined source-coherent receipt `g2/build/c-firmware/20261011/codec-reset-entry-layout-round/receipt.json` compiles 233 source inputs. The isolated known-data placement receipt places the vector, source-owned fixed data and one BSS slot at named addresses. | `source_complete=false`, `full_payload_linked=false`. XIP final code placement/callable map, resolved pointer relocations, executable/data alias or scatter behavior, both loader branches, reset execution and conditional BSS state remain open (`codec/known-data-placement/receipt.json`). An isolated relocatable placement object is not a complete executable. | Final source-linked XIP ELF/map and authenticated loader/alias transition with bounded entry and BSS-state proof. Selected source count is not a complete native catalogue proof. |
| Codec B | Distinct stage1 11-unit candidate and stage2 301-unit selected archive. The source-fit stage2 ELF contains 305 selected/experimental objects, has zero undefined symbols, places the four newly corrected BSS slots at native addresses, and emits exactly 82,060 bytes within the unchanged stock stage2 transfer (`build-stock-length-bss-slot-round/receipt.json`, `stock-length-fit-receipt.json`). Full sourced IMCRA fixtures pass 89/89 for three inputs. | Experimental source-fit ELF has `source_complete=false`, `bootable=false`. Stage1/stock product loader and IRAM/DRAM alias are not executed; 15 typed address/data contracts persist in the selected archive. Twelve are retained/writer-owned runtime slots whose lifecycles are not all proved. The offline BINH stage pair does not authenticate package fields or hardware execution. CRC bitwise and quarter-wave cosine reductions prove results/bytes in tested domains, not native instruction schedule or timing. | Authenticated stage1 loader trace, IRAM/DRAM alias proof, startup preservation path, runtime producer and consumer proof for the remaining RAM slots, and whole native callback/indirect-root qualification. |

## Actionable source conversion completed during this audit

Codec B's 1024-byte CRC lookup was replaced by a 62-byte target object using
the same reflected polynomial and verified against pinned NationalChip source
in 264 host cases. The 2052-byte IMCRA cosine table was represented as 129
quarter-wave words plus two native residuals; the generator proves all 513
float32 words reconstruct byte-for-byte, and three full IMCRA QEMU fixtures
pass. This recovered enough section space to place the complete selected audio
callbacks inside the unchanged 82,060-byte transfer. Four previously generic
`.bss` symbols were assigned explicit sections/addresses, with linker asserts:
`platform_shadow=0x20017398`, `mode_loop=0x2002d2b4`,
`mode_index=0x2002d2b8`, `token_cursor=0x2002d3e0`.

The `0x1000314c` stage2 system initializer clears BSS only when its
`preserve_memory_10003ffc` child returns zero. Therefore no ambient RAM
contract was assigned an invented zero initializer. The current source-fit
receipt is an offline placement result, not product runtime certification.

## Finite evidence boundary

The pinned Touch v6 PDL and current source/native readers establish LP
history **element type and pointer**, but no generated array dimension; no
source-owned history definition can be admitted from the 426-byte gap alone.
Codec B source-fit is now achieved under the stock transfer length, so a
further size-only change would not close its loader, runtime-state or indirect
effect gates. CASE and Codec A still have final image layout/entry obligations
even though their current source groups compile. These are concrete missing
evidence classes for this corpus; they do not assert that all firmware source
investigation is globally exhausted.
