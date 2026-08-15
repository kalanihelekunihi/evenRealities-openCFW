# GXCAS GXT310 reduction correlation

Snapshot: 2026-08-14. This document records the owner-authorized reduction of
the five `gxcas_gxt310_candidate` entries into independently compiled C under
`reconstructed/gxt310/`. The result is not GXCAS, Even Realities, or
Bravechip source.

## Evidence and recovered contract

The stock application image has load base `0x00027000` and SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Ghidra bodies and the rebuilt-image bytes establish two addressed channels,
`0x90` and `0x94`, using generic write operation `1`. Mode switching writes
the two little-endian command bytes `00 C2` when enabled and `01 C2` when
disabled. One-shot triggering writes `01 C1`. Pair enable calls both channels,
does not short-circuit after a failure, and returns the bitwise AND of the two
0/1 statuses.

| Stock entry | Inventory bytes | SHA-256 | Reconstructed role |
| --- | ---: | --- | --- |
| `0x00050F9C` | 138 | `e85aa5da2c0263ec52b56abad76046a18eca7a341efe9f9b8a1ebead6ce6276d` | `gxt310_enable_pair` |
| `0x0006F804` | 8 | `0a099318ad9c76b025b0aa229e8de6332ef6956114081adf0972d7ab88684700` | channel-`0x90` mode veneer |
| `0x0006F818` | 98 | `4820600616f6417670ae3535521aa4e72c9759af8070d999489955bc1d26fd4e` | channel-`0x90` one-shot folded body |
| `0x0006F81E` | 8 | `4811461d8532e3b7b0f3a00ac062c333edd814247df6d0f610af4887153ded1f` | channel-`0x94` mode veneer |
| `0x0006F832` | 6 | `f90cb138b31c3ba9bccefdd8fff04b86cd25268c55f846f56b347f703d0273ec` | channel-`0x94` one-shot veneer |

The tiny entries are compiler/linker veneers into shared bodies; the
inventory byte counts and digests preserve the recovered accounting while the
C API represents the shared typed operation directly.

## Explicit provider seams and safety divergences

The recovered generic registry write is represented by a bounded callback
receiving address, operation, two-byte buffer, and length. No registry object,
raw pointer, or opaque binary is linked. A missing callback or invalid address
fails explicitly. The optional failure callback replaces stock diagnostic-log
side effects without changing the transport result.

`tests/test_reconstructed_gxt310.c` pins both command byte pairs, addresses,
operation number, non-short-circuit pair behavior, callback failure reporting,
and invalid-address rejection. The module is built by the host, sanitizer,
Cortex-M object, and Nordic SDK-image source lists.
