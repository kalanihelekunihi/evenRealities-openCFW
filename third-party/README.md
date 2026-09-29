# Third-party dependencies

This directory is the single registry of every upstream that either device
links, or that the analysis relies on. The rule is to consume official
upstream source at the exact revision the firmware used, never to
re-implement it. Each pin can later move forward to test what an upstream fix
changes.

| Class | Where | Authenticated by |
| --- | --- | --- |
| Git submodules | [`upstream/`](upstream) (compiled), [`reference/`](reference) (comparison only), [`tools/`](tools) (analysis) | the gitlink commit in this repository |
| Archive fetch | [`fetched/`](fetched): the nRF5 SDK (no public Git) plus archive forms of the R1 sensor and crypto sources | archive SHA-256 and per-file hashes in `fetched/manifest.json` |
| Licensed or binary-only | not stored; documented in [`../docs/tooling.md`](../docs/tooling.md) and the device references | local fingerprint (`tools/bootstrap/bootstrap.py --licensed`) |

Nothing is fetched implicitly. Initialise only what you need:

```sh
git submodule update --init --depth 1 third-party/upstream/freertos-kernel
git submodule update --init --depth 1 --checkout third-party/reference/g2flash   # update=none entries
```

Every submodule is `shallow = true`. Large and comparison-only trees are
`update = none`. `cmsis-5-590`/`cmsis-core`, `ambiqhal-apollo510`/`ambiqhal-nema`
and `flashdb`/`flashdb-2.0.0` are distinct commits of the same repository, and
each commit is needed.

The G2 vendored snapshots that used to live in `g2/third_party/` were removed
on 2026-09-29. Every one of them is covered by a submodule at the same commit.
FreeRTOS-Kernel, CMSIS-FreeRTOS, CMSIS_5 and CmBacktrace were re-verified
file by file against the old snapshot hashes. The G2-specific configuration
and patches recovered alongside the snapshots are in
[`../g2/config-recovered/`](../g2/config-recovered/README.md).

## Pinned upstreams (original set)

| Submodule | Upstream pin | Licence | G2 | R1 |
| --- | --- | --- | :-: | :-: |
| `ambiqsuite-sdk` (SparkFun mirror; AMOTA, ANCC, Cordio app framework) | `de5c6ba3` (v2.5.1) | BSD-3-Clause / Apache-2.0 | • | |
| `ambiqhal-apollo510` | `5efc0228` (AmbiqSuite 5.1.0 HAL import) | BSD-3-Clause | • | |
| `cmbacktrace` | `73714489` | MIT | • | • |
| `cmsis-core` | `d23a6949` | Apache-2.0 | • | |
| `cmsis-5-590` | `2b7495b8` (5.9.0) | Apache-2.0 | • | • |
| `cmsis-freertos` | `d213f261` (v10.5.1) | Apache-2.0 | • | • |
| `cordio` | `3656312d` (r20.05c; includes the Packetcraft GATT profiles) | Apache-2.0 | • | |
| `cjson` | `3c893567` (v1.7.12; interval v1.7.9–v1.7.12) | MIT | • | |
| `easylogger` | `a596b264` | MIT | • | |
| `flashdb` | `714d6159` (2.1.1) | Apache-2.0 | • | |
| `freertos-kernel` | `def7d2df` (V10.5.1) | MIT | • | • |
| `freertos-plus-cli` | `43defa56` | MIT | • | |
| `freetype` | `86bc8a95` (2.9.1) | FTL | • | |
| `invensense-icm45608` | `b79ae575` (1.1.2) | TDK | • | |
| `liblc3` | `96a3af0b` (v1.1.3) | Apache-2.0 | • | |
| `littlefs` | `0494ce71` (v2.10.1) | BSD-3-Clause | • | |
| `lvgl` | `344c7c31` (9.3-dev) | MIT | • | |
| `lz4` | `ebb370ca` (v1.10.0) | BSD-2-Clause | • | |
| `nanopb` | `98bf4db6` (0.4.9) | Zlib | • | |
| `npmx` | `e1aaec53` | BSD-3-Clause | • | |
| `qpc` | `416dcec8` (v6.5.1; EM9305) | GPL-3.0-or-later | • | |
| `ring-buffer` | `190e30be` | MIT | • | |
| `tinyframe` | `eb75483e` | MIT | • | |
| `tlsf` | `deff9ab5` (interval ceiling) | BSD-3-Clause | • | |

Versions, evidence and recovered configuration for each library are in
[`../g2/docs/reference/libraries.md`](../g2/docs/reference/libraries.md) and
[`../r1/docs/toolchain-and-dependencies.md`](../r1/docs/toolchain-and-dependencies.md).

## Pins added on 2026-09-29

Each commit was checked against its upstream remote.

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

Deliberately not pinned:

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
