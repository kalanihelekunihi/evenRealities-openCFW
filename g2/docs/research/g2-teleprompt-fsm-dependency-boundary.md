# G2 teleprompt FSM dependency boundary

The three retained-path anchors / 1,902 bytes expand to fifteen functions /
2,994 body bytes for `teleprompt_fsm.c`. The complete physical object is
`[0x0058C836,0x0058D51C)`, 3,302 bytes. Eight source-order handlers missed by
Ghidra complete the state table, transition dispatcher, role checks, page-data
updates, timer policy, and diagnostic paths.

The closure records 1,131 reachable instructions, 179 direct calls, 29
whole-image BL entry sites, and nine stored handler pointers. The one indirect
call at `0x0058C9DA` is bounded by the checked state index and the nine-entry
Thumb table at `0x0074EF50`; every entry targets a recovered function in this
object. The raw BL-looking site at `0x0048BF90` is the second halfword of the
valid four-byte `mul` at `0x0048BF8E`, not strict-interior ingress.

All 172 external direct calls terminate at admitted EasyLogger (140), LVGL
(1), and nanopb (2), bounded runtime primitives (3), or first-party teleprompt,
role, UI, audio, page-data, file-list, and timer providers (26). No direct
CMSIS-FreeRTOS or FreeRTOS edge appears. The object embeds no reusable
implementation and adds no version or historical producing-commit
discriminator. Remaining work is first-party FSM recreation and device/UI
validation; the object is not production-routed.
