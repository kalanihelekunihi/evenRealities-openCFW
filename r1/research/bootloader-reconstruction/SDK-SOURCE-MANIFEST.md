# Nordic SDK and third-party source-correlation manifest

## Pinned reference inputs

The reference is the official nRF5 SDK `17.1.0` secure BLE bootloader for
`pca10056_s140_ble`. It is used as a symbol-bearing comparison corpus, not asserted to be the
unmodified original R1 source tree.

```text
nRF5 SDK archive:
  https://developer.nordicsemi.com/nRF51_SDK/nRF5_SDK_v17.x.x/nRF5_SDK_17.1.0_ddde560.zip
  SHA-256 5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061

Arm GNU Toolchain:
  gcc-arm-none-eabi-9-2020-q2-update-mac.tar.bz2
  arm-none-eabi-gcc 9.3.1 20200408
  SHA-256 bbb9b87e442b426eca3148fa74705c66b49a63f148902a0ea46f676ec24f9ac6
  MD5 75a171beac35453fd2f0f48b3cb239c3 (publisher checksum)
```

The production build guard in the SDK example rejects its bundled debug key. For this local
reference build, only `dfu_public_key.c` was replaced with the R1's recovered public verification
key. Signature verification stayed enabled; no private key or verifier bypass was used.

Reference result:

```text
target: examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc
ELF SHA-256: c9e3a6a089c1838b8eda759a6068105f965324765c05fb2ffe409fa45176c409
size: text 24016, data 184, bss 21976
Ghidra flash functions: 321
```

## Correlation method

Ghidra imports the reference ELF with its DWARF and symbols, imports the raw R1 image separately,
then computes `medium_nosize` BSim semantic vectors for both. The durable output contains 12 ranked
candidates for each of 298 signature-bearing R1 functions. Names are accepted only after additional
corroboration from vector position, constants, instruction semantics, call topology, known audit
behavior, or a coherent library-family cluster.

This method recovers optimized functions that byte hashing cannot match across ArmCC and GCC. It
also exposes compiler outlining: for example, the live `nrf_atomic_internal_*` helpers match the
SDK's ArmCC assembly exactly even though the GCC ELF presents related public atomic functions.

## Source families present

The correlation identifies these source families in the live bootloader:

- Nordic secure bootloader core, application handoff, timers, activation, info, and watchdog;
- BLE Secure DFU transport, request handler, flash, MBR, settings, validation, and version policy;
- Nordic nrf_crypto and CC310 bootloader backends;
- CryptoCell PKA and SaSi support routines;
- nrf_atfifo, nrf_atomic, nrf_balloc, fstorage, section iterators, scheduler, CRC-32, and NVMC;
- SoftDevice handler/observer infrastructure; and
- nanopb `pb_common.c`, `pb_decode.c`, and generated `dfu-cc.pb.c`.

The exact implicated SDK paths are listed by DWARF in
[`generated/reference-headless.log`](generated/reference-headless.log). The SDK license should be
reviewed before vendoring its sources; this repository records hashes, paths, an independently
written functional model, and a small configuration overlay instead of copying the SDK tree.
