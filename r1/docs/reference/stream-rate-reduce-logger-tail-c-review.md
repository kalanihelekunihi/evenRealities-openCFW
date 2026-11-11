# Stream logger tail transfer in C

The stock stream rate reducer forwards the four argument registers to Nordic
`nrf_log_frontend_std_2` and returns with the logger's residual R0. The SDK
declares that logger `void`, so the ordinary SDK C interface does not expose
this native result. The R1 source now gives that one call site a local
`uint32_t` raw-ABI declaration and uses Clang `musttail` to preserve LR, SP,
the argument registers and the residual R0. This removes the handwritten
`b.w` from `r1/src/application/runtime/native_stream_rate_reduce.c`.

The current R1 Clang profile emits the same four-byte `b.w` with the same
`R_ARM_THM_JUMP24` relocation for the C tail call as for the prior naked
wrapper. The full unit's disassembly and raw section bytes match; ELF object
files differ in non-executable metadata. A fresh `./make.sh r1-source-link`
run compiles 963/963 application and 82/82 bootloader units, then links both
regions with no undefined symbols or archive members. Its application raw
image is byte-identical to the prior source-linked image, SHA-256
`2c3bf3d374eb1df387c8bf0ae942e983420065b69c814d7de8460c4f26c579ab`;
the bootloader image also retains SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
The build receipts are under `build/r1-source-logger-tail-c-20261111/`,
`build/r1-app-logger-tail-c-20261111/`, and
`build/r1-boot-logger-tail-c-20261111/`. The isolated before/after object
disassemblies are under `build/r1-stack-builtin-c-20261111/`.

The local result declaration intentionally differs from Nordic's `void`
prototype in another translation unit. Its result is an ARM ABI observation,
not a portable ISO C function contract. Current-image identity establishes
that this change does not alter the linked execution for the checked build;
it does not establish stock byte identity or hardware behavior. The source
scan now finds 24 `__asm__` tokens on 20 lines across nine R1 files.
