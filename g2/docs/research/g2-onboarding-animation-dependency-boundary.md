# G2 onboarding animation dependency boundary

The four retained-path anchors / 1,290 bytes expand to eleven functions /
1,598 body bytes for `onboarding_animation.c`. The complete physical object
is `[0x0050F8CC,0x005100A0)`, 2,004 bytes, bounded above by the closed
`callback_manager.c` object (starts exactly at `0x005100A0`) with both
boundary faces hash-pinned. The unclosed code below `0x0050F8CC` (LVGL
roller and onboarding support objects) carries no reference to this
retained path and is not absorbed.

## Function inventory

Ghidra discovered four functions (`0x0050F8CC`, `0x0050FBB6`, `0x0050FC86`,
`0x0050FD1A`), all path-anchored. Seven source-order functions Ghidra
missed are restored: the 56-byte helper `0x0050FC4E`, the shared
page-transition helpers `0x0050FE0E` and `0x0050FE56`, the LVGL
message/delete-driven cleanup helpers `0x0050FEF8` and `0x0050FF0E`, the
allocation wrapper `0x0051008A`, and the four-byte heap-free tail thunk
`0x0051009C` (`b.w #0x474D16`). The anchored `0x0050FD1A` calls restored
`0x0050FE0E` internally; three internal calls close the object. The closed
`onboarding_main_page`, `dashboard_main_screen`, and `ui_msg_notif_list`
audits already classify several restored entries as first-party providers.

## Ingress proof

Thirty-five whole-image BL sites reach exact starts. The single raw word
matching a function entry (`0x0050FF0E` at container `0x00631937`) sits at
an odd, unaligned address and is a raw instruction-word collision, not a
stored pointer. Four raw word collisions point into function interiors
(containers `0x00630155`, `0x0063033E`, `0x00630BC8` unaligned;
`0x006319FC` an aligned data word whose value cannot name an entry). No
stored function-entry pointer, no indirect call, and no strict-interior BL
site exists. One tail branch (`b.w` at `0x0051009C`) targets the
source-owned TLSF heap-free wrapper and is pinned separately.

## Provider boundary

All 80 external direct calls terminate at admitted EasyLogger (30), bounded
IAR memory primitives (11), admitted LVGL object/animation/message
providers (21), admitted nanopb decode helper (1), the source-owned TLSF
heap-allocation wrapper (1, plus 1 tail branch to the free wrapper), or
bounded first-party providers (16): the unclosed `generic_animation.c`
cluster and first-party helper thunks. No direct CMSIS-FreeRTOS or FreeRTOS
kernel seam exists in this object. The object embeds no reusable
third-party implementation and adds no version or historical
producing-commit discriminator.

## Noncode accounting

406 noncode bytes: literal pool `0x0050FE7A..0x0050FEF8` (126 bytes, holds
the retained-path cell `0x0050FEB8`) and `0x0050FF72..0x0051008A` (280
bytes) behind the cleanup helpers. All 6 path literal references are
digest-pinned.

## Limitations

The seven restored functions carry no path reference; membership rests on
source-order contiguity, direct BL ingress, internal call linkage, pool
adjacency, and cross-closure provider agreement. The cleanup helpers are
shared with dashboard and message-notification pages, consistent with a
reusable onboarding animation API but noted as an attribution assumption.
Remaining work is first-party source recreation and device/UI validation;
the object is not production-routed. Reproduce with
`python3 tools/analyze_g2_onboarding_animation.py` and its focused test.
