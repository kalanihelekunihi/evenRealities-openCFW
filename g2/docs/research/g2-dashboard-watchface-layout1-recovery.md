# G2 dashboard watchface layout 1 recovery

The two retained-path anchors / 1,928 bytes expand to nineteen functions /
3,500 body bytes for `dashboard_watchface_layout1.c`. The complete physical
object is `[0x005B7934,0x005B873C)`, 3,592 bytes. Ten source-order routines
missed by Ghidra complete initialization, LVGL construction, time/battery/BLE
widget updates, configuration formatting, and the stored layout operation
table.

The closure records 1,301 reachable instructions, 231 direct calls, twenty
whole-image BL entry sites, and thirteen stored function pointers with no
strict-interior ingress. One raw word collision at `0x0043A802` overlaps the
second halfword of the valid four-byte branch at `0x0043A800`; it is not an
aligned stored pointer. The two `blx` sites at `0x005B847A` and `0x005B8490`
are not open dispatch: PC-relative constants at `0x005B89E0` and `0x005B89E4`
bind them to recovered local callbacks `0x005B84AC` and `0x005B86D2`.

All 215 external direct calls terminate at admitted EasyLogger (20), LVGL
(154), and mpaland printf (10), bounded IAR DLIB primitives (13), or
first-party dashboard/resource providers (18). This reuses EasyLogger
`a596b264…`, LVGL `344c7c31…`, and mpaland printf `d3b98468…`. The object
embeds no third-party implementation and adds no new version or private
generating-commit discriminator. Remaining work is first-party watchface
recreation and device display validation; the object is not production-routed.
