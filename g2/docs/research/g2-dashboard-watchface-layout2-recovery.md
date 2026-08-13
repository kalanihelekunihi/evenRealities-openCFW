# G2 dashboard watchface layout 2 recovery

The single 1,484-byte retained-path anchor expands to nineteen functions /
2,844 body bytes in `[0x005B90E8,0x005B9CEC)`, a 3,076-byte physical object.
Thirteen source-order lifecycle/widget routines were restored beyond Ghidra.
One whole-image BL entry and eighteen stored entries reach exact starts; there
are no indirect calls or strict-interior ingress.

All 181 external calls terminate at admitted EasyLogger (20), LVGL (104), and
mpaland printf (5), bounded IAR memset (9), or first-party dashboard providers
(43). The object reuses commits `a596b264…`, `344c7c318…`, and `d3b98468…`;
it embeds no reusable implementation and adds no version/private-commit signal.
Remaining work is first-party recreation and display validation. Reproduce with
`python3 tools/analyze_g2_dashboard_watchface_layout2.py` and its focused test.
