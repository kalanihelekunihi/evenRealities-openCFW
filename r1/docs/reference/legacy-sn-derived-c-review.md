# R1 derived SN command in C, 2026-11-11

The locked application command at `0x62bec` reads the word at offset 76 of
the existing 124-byte `nv_r1` class. Selector zero returns its low byte,
except that erased value `0xffffffff` makes it decode the product SN and
use byte zero of the selected touch-model table. Selector one persists the
request byte as a full 32-bit word through stock setter `0x7ca44`, reads
the word again, and replies with its low byte. Other selectors return zero
without sending. Both reply branches send five bytes and return the
sender's result. The C bodies live in
`r1/src/application/board/native_legacy_reply.c` and
`r1/src/application/runtime/native_device_configuration.c`. They reuse the
current cached-class handle, getter, product decoder, model table and
reply sender.

The ignored host probe at `build/r1-sn-derived-c-20261111/probe.c` passed
all 256 selectors, the erased fallback, and a full-width setter check under
ASan and UBSan. The R1-only source receipt at
`build/sources-r1-sn-derived-c-20261111/report.json` compiled 931/931
application and 82/82 bootloader units without failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-sn-derived-c-20261111/report.json` has 22 undefined
functions and uses 639,896 of 696,320 flash bytes without overflow. The
bootloader strict link passes.

The cached-class read status is ignored as in stock. Rejected reads,
physical hardware behavior and stock byte identity remain unverified.
