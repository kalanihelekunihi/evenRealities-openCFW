# G2 teleprompt UI recovery

The eight retained-path anchors / 3,034 bytes for `teleprompt_ui.c` expand to
55 functions / 12,228 body bytes. The complete physical object is
`[0x00554170,0x005574B0)`, 13,120 bytes including 892 bounded noncode bytes.
Thirty-eight restored functions recover the presentation-mode callback table,
text/resource rendering, scrolling, configuration, and screen lifecycle.

All 724 external direct calls terminate at EasyLogger (330), LVGL (252), IAR
DLIB (10), or 132 bounded first-party teleprompt/display providers. One
indirect call dispatches through the object's 4-by-19 mode/event callback table.
Twenty-seven stored pointers select function entries, five select two
authenticated interior callback labels, and six apparent odd pointers are unaligned word
coincidences whose targets are second halfwords of 32-bit instructions.

The object reuses EasyLogger commit `a596b264…` and LVGL 9.3-compatible commit
`344c7c318…`; it embeds no reusable implementation or new version
discriminator. Remaining work is clean-room teleprompt UI/policy reconstruction
and hardware/display validation. The object is not production-routed.
