# G2 bootloader no-op callback source closure

Date: 2026-09-01

The entries at `0x0042DD98`, `0x0042E276`, and `0x0042E39A` are complete
two-byte no-op callbacks (`bx lr`). They are MIT production C in
`runtime_noop_callbacks_42dd98.c`; both reviewed compilers reproduce each
entry exactly without relocations. Direct callers are respectively
`0x0042DD22`, `0x0042E302`, and `0x0042E36C`, with no stored ingress.

Host tests invoke all callbacks and authenticate the exact dual-toolchain
bodies. Any surrounding hardware-service behavior remains **blocked by
unavailable physical evidence**. No hardware operation or firmware-wide
completeness claim occurred.
