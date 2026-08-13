# G2 `common_image_container.c` dependency boundary

Status: complete fail-closed linked-object/provider audit; not production-routed.

The two retained-path anchors expand to three functions / 1,554 body bytes in
the exact physical object `[0x004DC5AE,0x004DCCD8)`, which includes 280 bytes
of literals, strings, alignment, and data. The pathless 62-byte CRC helper at
`0x004DCC98` belongs here, confirming the boundary previously recorded by the
adjacent common-list audit. Three whole-image BL entries, no stored entries,
no indirect calls, and zero strict-interior ingress close the object.

All 80 external direct calls terminate at known providers: 70 EasyLogger, three
LVGL, three production TLSF-backed synchronized frees, one production
Apollo510 cache-clean leaf, one bounded signed-absolute helper, and two
first-party image/navigation providers. The relevant selected commits are
EasyLogger `a596b264…`, LVGL `344c7c318…`, TLSF `deff9ab5…`, and AmbiqSuite
public replay `5efc0228…`. No implementation from those dependencies is
embedded here, and the object adds no new version or historical-commit
discriminator.

Run `python3 tools/analyze_g2_common_image_container.py` and
`python3 -m unittest tests.test_analyze_g2_common_image_container` to reproduce.
