# R1 source-constructed secure bootloader

This is the complete Cortex-M4 firmware project for the functionally reconstructed Even Realities
R1 bootloader. It compiles identified upstream nRF5 SDK 17.1.0, nrfx/CMSIS, nanopb, S140 interface,
and Nordic crypto components directly from the hash-pinned source subset under `vendor/`. The only
product-authored C unit is the recovered public verification key; product configuration and build
integration are kept outside the upstream tree.

This is functionally reconstructed source, not the unavailable vendor source tree and not a
byte-identical claim. The captured retail binary contains 285 optimized function boundaries; this
GCC build exposes 321 flash function addresses from 74 source objects. The source families and
behavioral mapping are documented in [`FUNCTIONAL-COVERAGE.md`](FUNCTIONAL-COVERAGE.md).

## Requirements

- GNU Make;
- Python 3; and
- Arm GNU Toolchain `9-2020-q2-update`, `arm-none-eabi-gcc 9.3.1`.

The Nordic/third-party source subset and S140 7.2.0 image are already present and verified by
`vendor/vendor-sha256.txt`. The compiler is intentionally not copied into the repository. Exact
input hashes and the full upstream comparison result are recorded in
[`verification/upstream-inputs.json`](verification/upstream-inputs.json).

## Build

If `arm-none-eabi-gcc` is on `PATH`:

```sh
make
make verify PROFILE=captured
```

With an explicit compiler location:

```sh
make clean PROFILE=captured GNU_INSTALL_ROOT=/absolute/toolchain/bin/
make verify PROFILE=captured GNU_INSTALL_ROOT=/absolute/toolchain/bin/
```

The default `captured` profile reproduces the observed `NRF_DFU_DEBUG_VERSION` validation behavior.
It still requires a valid ECDSA-P256/SHA-256 signature on DFU packages. The alternative `hardened`
profile repairs the installed-application CRC fail-open behavior without changing valid signed-DFU
operation:

```sh
make verify PROFILE=hardened GNU_INSTALL_ROOT=/absolute/toolchain/bin/
```

Run both target builds plus the clean behavioral-model tests with:

```sh
make test GNU_INSTALL_ROOT=/absolute/toolchain/bin/
```

Check deterministic output by building each profile twice:

```sh
python3 tools/check_reproducible.py --toolchain-root /absolute/toolchain/bin
```

## Outputs

Each profile writes to `build/<profile>/`:

| File | Purpose |
| --- | --- |
| `r1_bootloader.out` | symbol-bearing ARM ELF for review/debugging |
| `r1_bootloader.hex` | bootloader payload plus UICR bootloader/MBR-parameter words |
| `r1_bootloader.bin` | exactly `0x6000` bytes for `0x000f8000...0x000fdfff`, padded with `0xff` |
| `r1_bootloader.map` | full linker map |
| `build-manifest.json` | hashes, sizes, vectors, function count, key address, and security status |

The linker layout is inherited unchanged from Nordic's identified
`pca10056_s140_ble` secure-bootloader target: flash at `0x000f8000`, RAM at `0x20005978`, MBR
parameters at `0x000fe000`, settings at `0x000ff000`, and UICR words at `0x10001014` and
`0x10001018`.

## Source boundary

- `vendor/nrf5-sdk/` is an unmodified, minimal upstream dependency closure with 316 hash-pinned
  files and retained license notices.
- `config/r1_recovered_config.h` contains evidence-backed R1 configuration values.
- `src/r1_dfu_public_key.c` contains the public trust anchor recovered from flash.
- `Makefile` and `tools/` are reconstruction/build/verification integration.

See [`LICENSES.md`](LICENSES.md) and [`vendor/README.md`](vendor/README.md) for provenance. Nordic's
CC310 BL and Oberon implementations are linked as the licensed upstream object libraries supplied
with nRF5 SDK. The bootloader logic, BLE DFU transport, nanopb parser, flash/settings management,
activation, and application handoff are compiled from source. S140 itself is a separately licensed
runtime binary and is not part of the bootloader ELF.

## Security and deployment boundary

The project contains the public R1 trust anchor but no private key, package-signing facility,
unsigned acceptance profile, verification-gate patch, or flashing command. Installing a DFU image
through an existing secure bootloader still requires an authorized signature. Hardware deployment
must also account for the installed S140 version, settings/MBR pages, UICR state, and board-specific
validation on owned test hardware.
