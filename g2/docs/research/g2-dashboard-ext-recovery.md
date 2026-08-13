# G2 dashboard extension recovery

The six retained-path anchors / 2,498 bytes expand to sixteen functions / 5,904
body bytes for `dashboard_ext.c`. The complete physical object is
`[0x0050083E,0x005026BC)`, 7,806 bytes. Ten restored routines complete dashboard
message dispatch, role-aware peer transfer, file lifecycle, protobuf record
processing, and resource lookup.

The three retained path cells span two large Ghidra-missed bodies and their
literal pools. The audit separates 1,902 non-code bytes, rejects thirteen
unaligned whole-image word coincidences with instruction-interior addresses,
and pins 2,142 instructions, 315 direct calls, 32 whole-image BL entries, no
indirect calls, and no strict-interior ingress.

All 291 external calls terminate at EasyLogger (220), bounded IAR DLIB (18),
production-owned littlefs file wrappers (16), admitted nanopb runtime (5), the
source-owned FreeRTOS delay (3), or first-party dashboard providers (29). This
reuses EasyLogger `a596b264…`, littlefs `0494ce71…`, nanopb `98bf4db6…`, and
FreeRTOS-Kernel `def7d2df…`; it embeds no third-party implementation and adds
no version or private generating-commit discriminator. Remaining work is
first-party schema/transport policy and device validation; the object is not
production-routed.
