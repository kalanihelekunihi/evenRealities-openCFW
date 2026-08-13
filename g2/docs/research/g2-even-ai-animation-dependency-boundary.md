# G2 EvenAI animation dependency boundary

The two retained-path anchors / 1,310 bytes expand to five functions / 2,036
body bytes for `even_ai_animation.c`. The complete physical object is
`[0x005537CC,0x00554080)`, 2,228 bytes, bounded below by the closed
`text_stream_service.c` object (ends exactly at `0x005537CC`) with both
boundary faces hash-pinned.

## Function inventory

Ghidra discovered two functions (`0x005537CC`, `0x005538D8`), both
path-anchored. Three source-order functions Ghidra missed are restored:
`0x0055389A..0x005538D8` (eight external BL callers; already a pinned
first-party provider of the closed `ui_even_ai.c` audit), the 20-byte leaf
`0x00553D28..0x00553D3C`, and `0x00553D64..0x00553FE8` (the animation
step/driver, 33 calls, references the retained path six times). One internal
call links the driver to its helper.

## Extent exclusion evidence

The eight-function cluster at `0x00554080..0x00554170` is excluded: all of
its 40 BL callers sit in teleprompt objects (`teleprompt_ui.c`,
`teleprompt_fsm.c`, `teleprompt.c`), the closed `teleprompt_fsm` audit
already classifies two of them (`0x005540B2`, `0x005540BC`) as its own
first-party providers, and no cluster function can reference this retained
path (the path cell at `0x00553FFC` lies below every cluster function).

## Ingress proof

Twenty-eight whole-image BL sites reach exact starts (16 to the entry
function, 8 to the restored helper, 4 to the remaining functions). No
stored function-entry pointer, no indirect call, no raw interior word
collision, and no strict-interior BL site exists.

## Provider boundary

All 79 external direct calls terminate at admitted EasyLogger (60), one
bounded IAR memory primitive (1), admitted LVGL object providers (2), one
exact CMSIS-FreeRTOS v10.5.1 seam — `osKernelGetTickCount` at `0x004490CC`,
pinning the animation start timestamp — or bounded first-party providers
(15): the unclosed `generic_animation.c` cluster (`0x00463E9A` and
neighbors) plus UI and formatting leaves. No FreeRTOS kernel call appears
(the CMSIS wrapper inlines the tick read). The object embeds no reusable
third-party implementation and adds no version or historical
producing-commit discriminator.

## Noncode accounting

192 noncode bytes: literal pool `0x00553D3C..0x00553D64` (40 bytes) behind
the small leaf, and `0x00553FE8..0x00554080` (152 bytes) behind the driver,
holding the retained-path cell `0x00553FFC`. All 12 path literal references
are digest-pinned.

## Limitations

Remaining work is first-party source recreation of the five animation
functions and device/UI validation; the object is not production-routed.
The two non-anchored restored leaves carry no path reference; membership
rests on source-order contiguity, direct BL ingress, pool adjacency, and
cross-closure provider agreement. Reproduce with
`python3 tools/analyze_g2_even_ai_animation.py` and its focused test.
