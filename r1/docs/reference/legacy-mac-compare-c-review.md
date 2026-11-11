# R1 legacy address compare command in C, 2026-11-11

The locked `r1-2.2.6.0009` application contains address setter `0x7ca10`
and legacy command `0x62412`. The setter reads the existing 124-byte `nv_r1`
class, writes six request bytes at offsets 62..67, writes the record back,
and waits for pending NV work. The command acts only on selector zero: it
calls the setter with packet bytes 4..9, reads the same six bytes through
stock getter `0x7badc`, compares them with the request, writes byte 4 to one
for equality or zero otherwise, and sends the five-byte reply. Other
selectors return zero without sending. The C bodies are in
`r1/src/application/runtime/native_device_configuration.c` and
`r1/src/application/board/native_legacy_reply.c`, sharing the existing
`r1_device_info_kv_handle`, cached-class accessors, comparison helper and
legacy reply sender.

The ignored host probe at `build/r1-mac-compare-command-c-20261111/probe.c`
exercised all 256 selector bytes, a deliberately mismatched readback, and
the setter's full return value under ASan and UBSan. It checked the record
write span, read/write/idle/get/send calls, response byte and packet
preservation. The full all-device source build at
`build/sources-r1-dual-router-all-20261111/report.json` compiled all
930 application and 82 bootloader units with no failures or duplicate
strong symbols. Its R1 manifest hash matches the current manifest. The
strict application receipt at
`build/r1-link-mac-compare-c-20261111/report.json` is down to 25 undefined
references and uses 639,336 of 696,320 flash bytes, with no overflow; the
strict bootloader link passes.

The cached-class read status is ignored as in stock. A rejected or damaged
record can still lead to undefined source-level stack contents in the setter;
this command does not establish a safe storage failure policy. Physical
R1 behavior and stock byte identity remain unverified.
