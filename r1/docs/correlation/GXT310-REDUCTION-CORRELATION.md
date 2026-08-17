# GXCAS GXT310 reduction correlation

Snapshot: 2026-08-14. This document records the owner-authorized reduction of
the eight `gxcas_gxt310_candidate` entries into independently compiled C under
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
| `0x0006F600` | 56 | `f8e7e7060dc42cc772ec9e0c75bb0cd0210f4160c792f73398df0557e24dc87e` | shared signed big-endian temperature read/scale |
| `0x0006F648` | 106 | `c2dd528f1696a7dec0fff2859d0940930d8f75de84d7d582a962e4fc9f9190fa` | shared mode writer |
| `0x0006F738` | 92 | `996e62bb9f1dfdb48ae224674b0771b1e6783d32fe4d8c81a003a1b21824e7b1` | shared one-shot writer |
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
operation number, signed read conversion, non-short-circuit pair behavior, callback failure reporting,
and invalid-address rejection. The module is built by the host, sanitizer,
Cortex-M object, and Nordic SDK-image source lists.

## Source-built Zephyr adoption

The alternate Zephyr target now installs the reconstructed software-TWI GPIO provider once and
binds `i2c_2` to its recovered SCL P1.13/SDA P0.28 pair. The GXT310 adapter translates each exact
two-byte mode command into the registry ABI's register byte plus one data byte, probes register
`0x03` at raw addresses `0x90` and `0x94` for ID `0x50`, and always disables both channels before
releasing the bus. A failed probe is retained as diagnostics and leaves the provider unavailable
without preventing BLE recovery.

The admitted R1 register-0 conversion is exposed as a pure tested function: two signed
big-endian bytes are multiplied by the exact `0.0078125 C/LSB` scale and truncated to integer
milli-units, equivalently `raw * 125 / 16`. The typed target API preserves both the immediate
paired read and the recovered 80-ms startup plus ten paired samples separated by 5 ms before the
existing extrema-trim/calibration reducer. Target startup reads the exact six-byte calibration at
persisted `nv_r1` offset `0x3E`; all-`0xFF` is absent, direction `0` subtracts, direction `1` adds,
and other direction bytes are disabled. This is a read-only consumer and the acquisition API does
not accept caller-supplied calibration.

The adjacent R1 product body `0x00050E4C..<0x00050EC8` and fixed stream vtable
`0x0009A5A8` are now adopted on target. A `"temp"` read enables both channels,
waits 80 ms, samples each register once, disables both channels, applies each
calibration magnitude as unsigned UInt16 under direction 0/1 with 32-bit
wrapping, adds the adjusted channels, adds the sum sign bit, and extracts bits
1...16. This preserves signed division by two toward zero and the exact
two-byte result. Its open/close hooks (`0x000918F8`/`0x000918FC`) remain no-op
success stubs and its read hook (`0x00091900`) rejects every length except two.
The target creates the singleton without registering a listener at startup. A separately
evidenced dormant one-shot API registers the exact `"once"` listener and composes event 9 with
the hourly cache. Neither channel is labelled skin/ambient and no clinical unit or public trigger
is inferred; those remain explicit owned-hardware gates.
