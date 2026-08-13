# G2 conversate protobuf message-handler dependency boundary

The five retained-path anchors / 1,428 bytes expand to fifteen functions /
3,440 body bytes for `conversate_pb_msg_handler.c`. The complete physical
object is `[0x005B48F8,0x005B57AC)`, 3,764 bytes, bounded below by the closed
`conversate_comm_data.c` object (`[0x005B3EF8,0x005B48F8)`) and above by the
closed `conversate_ui_menu_page.c` object (`[0x005B57AC,0x005B5DE4)`); both
boundary faces are hash-pinned.

## Function inventory

Ghidra discovered five functions (`0x005B4904`, `0x005B4A90`, `0x005B4CC8`,
`0x005B4D10`, `0x005B4DBA`), all path-anchored. Ten source-order functions
Ghidra missed are restored:

- `0x005B48F8`: 12-byte static table-lookup leaf called only from
  `0x005B4904` (4 sites); its literal cell at `0x005B53F8` lives inside this
  object's pool, proving same-object membership.
- `0x005B4E98`, `0x005B4F72`, `0x005B5150`, `0x005B52E0`, `0x005B5428`,
  `0x005B55B4`: message handlers witnessed by the authenticated dispatch
  table; each references the retained path string.
- `0x005B5720`, `0x005B5752`, `0x005B577C`: small non-logging helpers with
  direct BL ingress, already classified as first-party providers by the
  closed `conversate_ui_menu_page` audit.

## Ingress proof

Eighteen whole-image BL sites reach exact starts (four to the static leaf,
ten to `0x005B4904`, four to the tail helpers). Ten stored Thumb pointers at
`0x00727BC4..0x00727BF0` form the 13-word message dispatch table at
`0x00727BC0` (three NULL slots). The single indirect call (`blx r3` at
`0x005B4A40`) is bounded: the message type is `uxtb`-masked, the entry is
loaded from the pinned table (base cell `0x005B5404` stores `0x00727BC0`),
NULL entries are skipped, and all ten non-NULL entries target recovered
handlers in this object; the instruction bytes are hash-pinned. Two raw
instruction-word interior collisions (`0x0064AA03` unaligned halfword,
`0x006A41EC` aligned rodata word) point into function interiors and are not
ingress. No strict-interior BL site exists.

## Provider boundary

All 214 external direct calls terminate at admitted EasyLogger (165),
bounded IAR memory primitives (3), admitted LVGL display-state leaf
accessors (4), admitted nanopb decode sink helper (2), or bounded
first-party providers (40): closed `conversate.c`, `conversate_tag_data.c`,
`conversate_comm_data.c`, `conversate_ui_menu_page.c` entries plus unclosed
first-party conversate UI, audio, and service leaves. No direct
CMSIS-FreeRTOS or FreeRTOS kernel seam exists in this object. The object
embeds no reusable third-party implementation and adds no version or
historical producing-commit discriminator.

## Noncode accounting

324 noncode bytes: literal pools `0x005B52CA..0x005B52E0`,
`0x005B53F6..0x005B5428`, `0x005B55A8..0x005B55B4`, and
`0x005B5630..0x005B5720`; the two retained-path pointer cells sit at
`0x005B52D4` and `0x005B56D0` inside the first and last pools. All 33 path
literal references are digest-pinned.

## Limitations

Remaining work is first-party source recreation of the fifteen handlers and
device/UI validation; the object is not production-routed. The three tail
helpers carry no path reference; membership rests on source-order
contiguity, direct BL ingress, and cross-closure provider agreement.
Reproduce with `python3 tools/analyze_g2_conversate_pb_msg_handler.py` and
its focused test.
