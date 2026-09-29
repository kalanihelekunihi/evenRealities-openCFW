# Shared third-party dependencies

This directory is the single registry for every upstream dependency used by
either firmware target. It records what is depended on, at exactly which
revision, under which license, and which target consumes it.

Dependencies reach the build in one of two ways:

| Class | Where the source lives | How it is authenticated |
| --- | --- | --- |
| **Vendored snapshot** | [`../g2/third_party/<name>/`](../g2/third_party) | `verify_snapshot.py` per dependency, offline |
| **Fetched at build time** | a local cache directory you choose | [`fetched/verify_vendor.py`](fetched/verify_vendor.py) against [`fetched/manifest.json`](fetched/manifest.json) |

Nothing here is fetched implicitly. Both classes fail closed: a hash, commit,
tree, or file-set mismatch aborts the build rather than downgrading to a
warning.

## Why the vendored snapshots live under `g2/`

The vendored snapshots are physically stored at `g2/third_party/` rather than
in this directory. That is deliberate, not an oversight.

Each snapshot carries a self-referential integrity net that names its own
repository-relative path:

- `g2/third_party/*/PROVENANCE.json` records `third_party/<name>/...` paths that
  the verifiers resolve against the G2 tree root;
- several verifiers implement a *production-exclusion gate* that scans the G2
  `Makefile`, `manifests/`, and `components/` for the literal token
  `third_party/<name>` and fails closed unless the only matches are an exact
  allow-listed pair of lines (for example `NANOPB_DIR := third_party/nanopb`);
- 62 test modules verify the verifiers, and several pin the verifier script's
  exact byte size and SHA-256.

Relocating the directory would mean editing those paths and then re-pinning the
hashes that exist precisely to detect such edits — which would quietly retire
the byte-exactness guarantee that the G2 reconstruction rests on. The snapshots
stay put; this directory is the shared index over them.

The sharing is real rather than nominal: the R1 nRF52840 target already compiles
three of the G2 snapshots directly, via `../g2/third_party/...` in
[`../r1/platform/nrf52840/sdk/Makefile`](../r1/platform/nrf52840/sdk/Makefile).

## Vendored snapshots

Verified by `make third-party` from the repository root. All are pinned to an
exact upstream commit and reconstructed offline from the Git object closure.

| Dependency | Upstream pin | License | G2 | R1 |
| --- | --- | --- | :-: | :-: |
| `ambiqsuite-amota-profile` | `de5c6ba3` | BSD-3-Clause (Ambiq per-file) | • | |
| `ambiqsuite-ancc-profile` | `de5c6ba3` | BSD-3-Clause (Ambiq per-file) | • | |
| `ambiqsuite-apollo510` | `5efc0228` | BSD-3-Clause | • | |
| `ambiqsuite-cordio-app-framework` | `de5c6ba3` | Apache-2.0 | • | |
| `cmbacktrace` | `73714489` | MIT | • | • |
| `cmsis-core` | `d23a6949` | Apache-2.0 | • | |
| `cmsis-freertos` | v10.5.1 | Apache-2.0 | • | • |
| `cordio` | `3656312d` (r20.05c) | Apache-2.0 | • | |
| `cJSON` | `3c893567` (v1.7.12; proven interval v1.7.9–v1.7.12) | MIT | • | |
| `easylogger` | `a596b264` | MIT | • | |
| `flashdb` | `714d6159` (2.1.1) | Apache-2.0 | • | |
| `freertos-kernel` | `def7d2df` (V10.5.1) | MIT | • | • |
| `freertos-plus-cli` | `43defa56` | MIT | • | |
| `freetype` | 2.9.1 | FTL | • | |
| `goodix-gr551x-app-error` | see `PROVENANCE.json` | BSD-3-Clause (Goodix per-file) | • | |
| `liblc3` | `96a3af0b` | Apache-2.0 | • | |
| `littlefs` | `0494ce71` (v2.10.1) | BSD-3-Clause | • | |
| `lvgl` | `344c7c31` (9.3-dev) | MIT | • | |
| `lz4` | `ebb370ca` (1.10.0) | BSD-2-Clause | • | |
| `nanopb` | `98bf4db6` (0.4.9) | Zlib | • | |
| `npmx` | `e1aaec53` | BSD-3-Clause | • | |
| `packetcraft-gatt-profile` | `3656312d` | Apache-2.0 | • | |
| `qpc` | `416dcec8` (6.5.1) | GPL-3.0-or-later (GPL option selected) | • | |
| `ring-buffer` | `190e30be` | MIT | • | |
| `tinyframe` | `eb75483e` | MIT | • | |
| `tlsf` | see `SNAPSHOT.sha256` | BSD-3-Clause | • | |

A `•` in the R1 column means the R1 nRF52840 target compiles that snapshot
directly out of `g2/third_party/` — currently CMSIS-FreeRTOS, FreeRTOS-Kernel,
and CmBacktrace, which `verify_vendor.py` also re-authenticates during the R1
vendor audit. Everything else is G2-only today. Note that R1 uses FlashDB too,
but takes it from the fetched set rather than from this snapshot.

Many snapshots are **production-excluded**: authenticated and retained as
attribution evidence, but not linked into any shipped image. Each dependency's
`README.openCFW.md` states its own status. Do not infer from this table that a
dependency is compiled in.

## Fetched dependencies

[`fetched`](fetched) covers upstreams that are not redistributable here —
principally the Nordic nRF5 SDK and the sensor-vendor SensorAPIs. They are
downloaded into a cache directory of your choosing, checked against pinned
archive hashes, and then authenticated file-by-file.

```sh
third-party/fetched/fetch.sh /absolute/path/to/vendor-cache
```

The script refuses relative paths, verifies each archive's SHA-256 before
unpacking, skips anything already present, and finishes by running
`verify_vendor.py` over the whole set. See [`fetched/README.md`](fetched/README.md)
for the per-dependency roots and the environment variables the R1 build expects.

## Vendor firmware blobs

The official Even Realities OTA payloads that the G2 reconstruction is verified
against are vendor-proprietary and are **not** in this repository.
[`../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md)
records their origin and SHA-256 digests so a local copy can be reproduced and
checked. Place them at the path that file names before running any G2 target
beyond `make reference`'s prerequisites.

## Git submodules

`.gitmodules` pins 24 upstreams under [`upstream/`](upstream) at the same
commits as the vendored snapshots and the fetched manifest. The pins were
checked against the live remotes on 2026-09-29. No build consumes them yet.
They are the long-term update path: a reconstruction that builds against
`upstream/<name>` can move to a newer upstream commit and pick up its fixes.
Initialise only what you need:

```sh
git submodule update --init --depth 1 third-party/upstream/freertos-kernel
```

`cmsis-5-590` and `cmsis-core` are two different commits of the same CMSIS_5
repository, and both are needed. `freertos-plus-cli` clones the whole
FreeRTOS/FreeRTOS repository for two files, so initialise it shallowly.

### Proposed additional pins

The upstreams below are identified by repository evidence but are not yet
submodules. Each commit was checked against the upstream remote on
2026-09-29. Suggested paths are `upstream/<name>` for code that a rebuild
compiles, `reference/<name>` for comparison-only sources (`update = none`), and
`tools/<name>` for analysis tools. Library identities and the evidence behind
them are in [`g2/docs/reference/libraries.md`](../g2/docs/reference/libraries.md)
and [`r1/docs/toolchain-and-dependencies.md`](../r1/docs/toolchain-and-dependencies.md).

| Name | Repository | Commit | Consumer | Confidence | Licence / note |
| --- | --- | --- | --- | --- | --- |
| `upstream/mpaland-printf` | github.com/mpaland/printf | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e` | G2 Apollo | High | MIT |
| `upstream/ambiq-lvgl` | github.com/AmbiqMicro/LVGL | `5be8e0ae5077aa3880aba8a322b1487d6bc73c07` | G2 Apollo (Ambiq draw backend) | High | MIT; replaces the `lvgl-ambiq-backend` snapshot |
| `upstream/ambiqhal-nema` | github.com/AmbiqMicro/ambiqhal_ambiq | `b853fded7e545f005727e13bf2ce83018c7e242d` | G2 Apollo (NemaGFX 1.4.12 / NemaVG 1.1.8 headers) | High | headers only; the NemaGFX implementation is binary-only |
| `upstream/infineon-mtb-pdl-cat2` | github.com/Infineon/mtb-pdl-cat2 | `35f1714623cfea682d5e285af80d50416b4c7bbc` (release-v2.21.0) | G2 touch (PSoC 4000T PDL, `psoc4000t.svd`) | High | Apache-2.0 |
| `upstream/infineon-capsense` | github.com/Infineon/capsense | `25fa1cd5abb4cc66981b04f8872d57d74e398976` (release-v3.0.1) | G2 touch | Medium | Infineon EULA. One analyzer cites release-v10.0.0 (`b68b744eb75fe976fc5ddd7b16e04e1a5a54bdd3`) instead; settle this before pinning |
| `upstream/infineon-emeeprom` | github.com/Infineon/emeeprom | `6bbde322b7193528674dbf7fcdc2e971d0cff4fa` (release-v2.70.1) | G2 touch | Medium | Infineon EULA |
| `upstream/stm32g0xx-hal-driver` | github.com/STMicroelectronics/stm32g0xx-hal-driver | `a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9` (v1.4.7) | G2 case | Low: family proven, release not | BSD-3-Clause; latest tag, a candidate only |
| `upstream/cmsis-device-g0` | github.com/STMicroelectronics/cmsis-device-g0 | `f576c24e123edf3332988ecd49512c0f35f85186` (v1.4.5) | G2 case | Low | Apache-2.0; candidate |
| `upstream/nationalchip-lvp-kws` | github.com/NationalChip/lvp_kws | `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` | G2 GX8002 | High/Medium | MIT; large, so shallow |
| `upstream/nationalchip-gxdnn` | github.com/NationalChip/gxDNN | `0637b47c8fa0031f8f5651a903cd7d14716382fd` | G2 GX8002 NPU models | Medium | no licence declared |
| `upstream/fdlibm` | github.com/freemint/fdlibm | `61c059fed98e2ed8d26ca39617321134b33e535a` | G2 GX8002 maths | Medium | Sun fdlibm permissive |
| `upstream/flashdb-2.0.0` | github.com/armink/FlashDB | `4e5677408256f82d47cd56a6b04605dcee35ed9a` (2.0.0) | R1 (G2 uses 2.1.1) | High | Apache-2.0; also in `fetched/` |
| `upstream/bosch-bma456` | github.com/boschsensortec/BMA456_SensorAPI | `3266db2c5de15be1a00232b8c0f2fd23e07934e0` (v2.29.0) | R1 | High | BSD-3-Clause; also in `fetched/` |
| `upstream/st-lis2dw12` | github.com/STMicroelectronics/lis2dw12-pid | `8d4bd522015004a9646102702901ba5a15ec6d39` (v2.1.0) | R1 | High | BSD-3-Clause; also in `fetched/` |
| `upstream/st-fp-sns-stbox1` | github.com/STMicroelectronics/fp-sns-stbox1 | `e9a35449b777699b5e1dd0f1466de0ead554893a` (v2.1.0) | R1 (ST25DVxxKC BSP) | High | BSD-3-Clause; also in `fetched/` |
| `upstream/tiny-aes-c` | github.com/kokke/tiny-AES-c | `e72b6eff0884673997d0ca6385169bbd9b31936d` (v1.0.0) | R1 | Medium | Unlicense; also in `fetched/` |
| `upstream/goodix-gh3x2x` | github.com/coredevices/pebbleos-nonfree | `2c0034a23b675a5f9a29e4a47e8b504c7a88e321` | R1 (GH3x2x democode) | High | Goodix restrictive licence; also in `fetched/` |
| `reference/goodix-gr551x-micropython` | github.com/goodix-ble/GR551x-MicroPython | `fe8706b37dee646aaa4643edbd75364357ec1dbf` | G2 (`app_error` lineage) | Medium | carrier for the `goodix-gr551x-app-error` snapshot |
| `reference/iqs7211e-flipperone` | github.com/flipperdevices/flipperone-mcu-firmware | `0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067` | R1 touch | Medium | compatible reference, not the vendor checkout |
| `reference/iqs7211e-zmk` | github.com/sekigon-gonnoc/zmk-driver-iqs7211e | `436d3c42172abf812ec104521f29384fc02fc50e` | R1 touch settings | Medium | MIT |
| `reference/ambiq-neuralspot` | github.com/AmbiqAI/neuralSPOT | `4264b9309e03064ffad13a0468d5d0c1110c5288` | G2 Apollo (AmbiqSuite R4.4.1 Cordio oracle) | Medium | BSD-3-Clause and bundled terms |
| `reference/ambiq-nsx-sdk` | github.com/AmbiqAI/nsx-ambiq-sdk | `9f36432d875060ca301675131b40452ecf8377ca` | G2 Apollo (Cordio/WSF variant oracle) | Medium | BSD-3-Clause / Apache-2.0 |
| `reference/g2flash` | github.com/jimrandomh/g2flash | `6d5c58598e047ca5980065a9ee7570ce2d172ca7` | G2 community patch base and hardware notes | High | GPL-3.0-only |
| `tools/asm-differ` | github.com/simonlindholm/asm-differ | `0dd09af8f8008f1f880327cf0aca3b26d2562ea2` | byte matching | — | Unlicense |
| `tools/decomp-permuter` | github.com/simonlindholm/decomp-permuter | `059609d4aec73eb0650726772954e1ad575825f8` | byte matching | — | MIT |
| `tools/ghidra-svd` | github.com/antoniovazquezblanco/GhidraSVD | `893dfbe02d889dfb7c4cf69b7a395051a8307828` (v0.6.6) | Ghidra SVD import | — | Apache-2.0 |
| `tools/ghidra-csky` | github.com/taligentx/ghidra_csky_WinnerMicro | `0daaa056e8c570ba514fc0d0226384ecf9f9df05` | GX8002 decompilation | — | licence unverified |

Not proposed:

- The EM9305 SDK v4.2 mirror (`C0R3YY2/em9305_original`) has no licence. Treat
  it as an external oracle.
- The Ghidra ARC module exists only as NSA pull request 3006. Fork it before
  pinning.
- The nRF5 SDK, the full AmbiqSuite 5.1.0, the NemaGFX implementation, the
  Packetcraft/EM link layer and GoMore have no public Git repository. The nRF5
  SDK stays an archive in [`fetched/`](fetched).
- The Zephyr 3.7.2 / MCUboot / TinyCrypt entries in `fetched/manifest.json`
  exist only for the clean-room openR1 runtime. They are not stock
  dependencies.

## G2 firmware emulator

The project wants
[`PaulMcMillan/g2-firmware-emulator`](https://github.com/PaulMcMillan/g2-firmware-emulator)
as a submodule for testing, debugging and validating rebuilt images before
they go on real hardware. As of 2026-09-29 the repository could not be reached
anonymously: `git ls-remote` asks for credentials, and it is not among the
owner's public repositories. It is therefore not pinned yet. Once access is
available, add it as `third-party/tools/g2-firmware-emulator` at a reviewed
commit and record that commit here.
