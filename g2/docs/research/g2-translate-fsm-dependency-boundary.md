# G2 translate FSM dependency boundary

Two retained-path anchors / 1,000 bytes expand to eight functions / 1,304 body
bytes for `app\gui\translate\translate_fsm.c`. The physical object is
`[0x00596B00,0x005970A8)`, 1,448 bytes. The preceding 120-byte string-pointer
table at `0x00596A88` is referenced exclusively by closed
`conversate_tag_data.c` functions and is excluded; it is pinned as the
boundary neighbor instead. Six source-order functions restore what Ghidra
missed: the four-instruction state accessor `0x00596B00` (called four times by
the first anchor) and the five state handlers `0x00596EF4`, `0x00596F02`,
`0x00596F10`, `0x00596F48`, `0x00596F9E`, proven by the six-entry stored
handler table at `0x00773B8C`–`0x00773BA0` (all six aligned Thumb pointers
land inside the object; the first entry is the anchored dispatcher
`0x00596C98`). The trailing 144-byte pool carries the path cell `0x00597024`;
functions from `0x005970A8` onward reference the `terminal_data.c` pool region
instead and are excluded.

The object has 90 direct calls and one indirect call: the FSM dispatch
`blx r3` at `0x00596C48`, bounded by the stored six-entry state table above
(all targets are object state handlers). All 86 external direct calls
terminate at admitted EasyLogger (55), bounded IAR memory primitives (4),
source-admitted nanopb decode helpers (3 at `0x0048EB32`), or bounded
first-party providers (24: closed `translate_ui.c`/`translate.c` bodies
`0x0059D9D4`–`0x0059EC28`, display/sync policy `0x00443504`, `0x0045A568`,
`0x0045A8EE`, `0x0054F50E`, and the audio-enable provider `0x0054F380`). No
CMSIS-FreeRTOS or FreeRTOS kernel seam exists. The object adds no reusable
implementation, version signal, or observable private producing commit.

Whole-image ingress is closed by 11 BL sites (4 internal, all to the state
accessor) and the six stored table pointers. No strict interior BL and no raw
interior word collision exists. Remaining work is first-party FSM behavior
recreation and device validation; the object is not production-routed.
Reproduce with `python3 tools/analyze_g2_translate_fsm.py` and its focused
test.
