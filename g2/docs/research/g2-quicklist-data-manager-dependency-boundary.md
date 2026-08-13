# G2 quicklist data-manager dependency boundary

The three retained-path anchors / 1,350 bytes are the complete function set
of `quicklist_data_manager.c`: no source-order function is missing. The
complete physical object is `[0x0058D51C,0x0058DAE4)`, 1,480 bytes, bounded
below by the closed `teleprompt_fsm.c` object (ends exactly at `0x0058D51C`)
with both boundary faces hash-pinned.

## Function inventory

All three functions are Ghidra-discovered and path-anchored:
`0x0058D51C..0x0058D668` (list load/parse, 18 calls),
`0x0058D668..0x0058D9C0` (record save/update, 44 calls), and
`0x0058DA28..0x0058DACA` (record delete/reset, 7 calls). Two internal calls
link the save path to the load helper.

## Extent exclusion evidence

The trailing 0xD4-byte leaf at `0x0058DAE4` is excluded from this object:
its literal loads reach `0x900` bytes forward into the pool of the
following unclosed function cluster (shared literal region, so its bytes
cannot close against this object), none of its bytes or callers reference
this retained path, and its two callers sit in `teleprompt_ui.c` and an
unclosed `0x00584xxx` region, inconsistent with quicklist data-manager
membership.

## Ingress proof

Four whole-image BL sites reach exact starts (one per function, two to the
delete helper). No stored function-entry pointer, no indirect call, no raw
interior word collision, and no strict-interior BL site exists.

## Provider boundary

All 67 external direct calls terminate at admitted EasyLogger (60), bounded
IAR memory primitives (5), or the bounded first-party shared leaf
`0x0044A1C6` (2). No LVGL, nanopb, CMSIS-FreeRTOS, or FreeRTOS kernel seam
exists in this object. The object embeds no reusable third-party
implementation and adds no version or historical producing-commit
discriminator.

## Noncode accounting

130 noncode bytes: literal pool `0x0058D9C0..0x0058DA28` (104 bytes, holds
path cell `0x0058D9C4`) and `0x0058DACA..0x0058DAE4` (26 bytes, holds path
cell `0x0058DAD0`). All 12 path literal references are digest-pinned.

## Limitations

Remaining work is first-party source recreation of the three data-manager
functions and persistence validation; the object is not production-routed.
Reproduce with `python3 tools/analyze_g2_quicklist_data_manager.py` and its
focused test.
