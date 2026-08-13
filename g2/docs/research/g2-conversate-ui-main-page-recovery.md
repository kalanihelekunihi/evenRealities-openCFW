# G2 conversate main-page recovery

The three retained-path anchors expand to fifteen functions / 4,132 body bytes
in `[0x005B23E4,0x005B3570)`, a 4,492-byte physical object. Eleven source-order
UI lifecycle and callback routines were restored beyond Ghidra's four function
entries. Six whole-image BL sites and twenty-one stored pointers reach exact
starts. Two BL sites and one stored callback deliberately enter authenticated
instruction interiors; the stored `0x005B305D` callback is the alternate entry
into the large UI-construction routine, not an overlapping function.

All 283 external calls terminate at admitted EasyLogger (130) and LVGL (98),
bounded/source-recreated IAR `snprintf` (2), or first-party conversate providers
(53). The object reuses EasyLogger commit `a596b264…` and LVGL commit
`344c7c318…`; it embeds no reusable implementation and adds no IAR release or
private producing-commit discriminator. Remaining work is first-party source
recreation and hardware display/input validation. Reproduce with
`python3 tools/analyze_g2_conversate_ui_main_page.py` and its focused test.
