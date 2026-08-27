# G2 bootloader platform-setup source closure

The complete bootloader platform-setup entry at
`[0x0041FA50,0x0041FA98)` is now replaced by maintained clean-room C. It is a
first-party G2 compatibility service; no separate upstream identity is
claimed.

## Authenticated stock and ingress bounds

The 72-byte stock body hashes to
`fa00cb13624ecad4499a72574fa77edf5fc20471e6e6602cdae20441c7745f6f`.
The whole-image aligned Thumb `BL` scan finds exactly one direct caller at
`0x0041B87E`. The preceding authenticated 16 bytes at
`[0x0041FA40,0x0041FA50)` contain initializer-table pointers, alignment, and
the stored comparator pointer. The following entry starts exactly at
`0x0041FA98`, so the replacement does not consume either neighboring data or
the guarded-teardown body.

## Recovered contract

`runtime_platform_setup_41fa50.c` is 5,487 bytes, SHA-256
`5126096f05bd4d66f7148fd564c7defdb9b4b49729d358f6a768579fcfe372d1`,
under GPL-3.0-or-later. It preserves the authenticated sequence:

- invoke the guarded teardown through patched stock entry `0x0041FA99`;
- call the reset seam `0x0041C4B5`;
- call mode seam `0x0041C86D` with `(0, 0)`;
- call derive seam `0x0041CA2D` with a stack output and `25.0f` in the VFP
  argument ABI;
- copy exactly 20 bytes from stock configuration `0x00433A9C` through copy
  seam `0x004156AD`;
- submit that stack configuration through `0x00422417`; and
- invoke channel seam `0x004222A1` for channels four and five, each with two
  zero arguments.

The host adapter pins call order, every scalar argument, the exact IEEE-754
bits for `25.0f`, copy length, configuration bytes received by submit, and
both channel calls. A warning-clean freestanding Cortex-M55 compile gate pins
the explicit `aapcs-vfp` function-pointer boundary.

## Dual-profile production evidence

Apple Clang 21 and exact-root Linux Clang 22.1.8 emit the same relocation-free
96-byte leaf, SHA-256
`e064ce74a17db06a9bb9d6dab1bbaf807c01215d270c916c02782c90a55a4a67`,
at overlay offsets 9,392 and 9,376. Apple produces a 9,488-byte overlay ending
at `0x00436988`, SHA-256
`da89534353b40e8787963c24dc0aa6209b11948cd128b8d05115525685b53adc`,
and a 158,088-byte provider, SHA-256
`5283432f02f86b2c62dea8eac44c567f99b3c4d261c3412ab638b67535486145`.
Linux produces 9,472 / 158,072 bytes with SHA-256
`1b97e43f2615b0281850b16c5f14aeb31bd6af3d792008bb62a9c60cff2b4b5b`
and `991fc763c08fdf890d18840d84b6a386864dae812757035faa4e216a1c4663e3`.
Canonical accounting is 9,475 source-owned, 10,772 generated patch, 14
alignment, and 137,827 retained official bytes across 157 functions, 138
relocated leaves, and 155 patch sites. Apple retains 5,752 bytes of overlay
headroom.

The unsigned Apple package is 4,739,666 bytes, SHA-256
`761b09380b08493d69eee02b2912cb1edeb6f14c584973df52d6bcf3e058dae1`.
Its 4,493,898-byte flash plan hashes to
`cd3249fd3f5ef5b1866e2b3b7d1187070f913ef83f4705717da0383f09184d60`
and records 6,461 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,515,660 bytes, SHA-256
`8a447d867e6303ed6075ad83067c53350a1e189956d2dc8c7ae6e93b287c12ea`;
its 2,393,331-byte plan hashes to
`190e9bf7159a3c6137ad4df619cb48a91a78f1a1f148af5d2cbc3f30da236266`
and records 3,430 placed regions with the same unresolved/container/protected
boundaries.

No signer, device, debugger, UART, transport, flasher, reset, or boot path was
accessed. Live teardown/reset/configuration/pin/channel side effects, VFP
callee behavior, and cold-boot evidence remain blocked: there is no authorized
responsive right G2 temple, and the authorized left temple must remain stock.
Later retained executable bootloader bodies remain software gaps, so
firmware-wide functional completeness is not claimed.
