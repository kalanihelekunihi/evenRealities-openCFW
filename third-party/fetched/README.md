# Fetched dependencies (R1)

These are R1 upstreams in archive form. They are downloaded into a local
cache, checked against pinned archive hashes, and then authenticated file by
file. The nRF5 SDK has no public Git repository, so this is its only pinned
form. Every other entry here is also pinned as a Git submodule under
[`../upstream/`](../upstream) (see [`../README.md`](../README.md)).

- [`manifest.json`](manifest.json) records each pin: provider, version,
  archive URL and SHA-256, licence, and the recovered evidence that fixed the
  version.
- [`verify_vendor.py`](verify_vendor.py) is the offline authenticator. It
  hashes the fetched trees and checks the FreeRTOS-Kernel, CMSIS-FreeRTOS,
  CMSIS_5 and CmBacktrace submodules at their pinned commits. It fails closed
  on any mismatch.
- [`fetch.sh`](fetch.sh) downloads and unpacks the fetchable set, then runs
  the authenticator.

## Fetching

```sh
git submodule update --init --depth 1 third-party/upstream/freertos-kernel \
  third-party/upstream/cmsis-freertos third-party/upstream/cmsis-5-590 \
  third-party/upstream/cmbacktrace
third-party/fetched/fetch.sh /absolute/path/to/vendor-cache
```

The cache path must be absolute. Each archive's SHA-256 is checked before it is
unpacked, and anything already present is skipped. Nothing is written outside
the cache directory.

## Roots

| Variable | Component | Notes |
| --- | --- | --- |
| `SDK_ROOT` | `nordic-nrf5-sdk` | nRF5 SDK 17.1.0; also supplies S140 7.2.0, SEGGER RTT and the FreeRTOS nRF52 port |
| `FLASHDB_ROOT` | `flashdb` + `fal` | FlashDB 2.0.0 with FAL 0.5.99 |
| `BMA456_ROOT` | `bosch-bma456-sensorapi` | one of the three probed accelerometer variants |
| `LIS2DW12_ROOT` | `st-lis2dw12-pid` | another probed accelerometer variant |
| `ST25DVXXKC_ROOT` | `st-st25dvxxkc-bsp` | point at `.../Drivers/BSP/Components/st25dvxxkc` |
| `TINY_AES_ROOT` | `tiny-aes-c` | AES-128 core (tiny-AES-c 1.0.0-compatible) |
| `IQS7211E_ROOT` | `flipperone-iqs7211e` | touch controller reference; comparison only |
| `AZOTEQ_SETTINGS_ROOT` | `azoteq-iqs7211e-settings` | touch settings reference; comparison only |
| `GOODIX_DEMOCODE_ROOT` | `goodix-gh3x2x-democode` | GH3x2x demo/driver source (point at `.../gh3x2x`) |

```sh
make -C r1 vendor-audit SDK_ROOT=$CACHE/nRF5_SDK_17.1.0_ddde560 \
  FLASHDB_ROOT=$CACHE/FlashDB-4e56774 BMA456_ROOT=$CACHE/BMA456_SensorAPI-3266db2 \
  LIS2DW12_ROOT=$CACHE/lis2dw12-pid-8d4bd52 \
  ST25DVXXKC_ROOT=$CACHE/fp-sns-stbox1-e9a3544/Drivers/BSP/Components/st25dvxxkc \
  TINY_AES_ROOT=$CACHE/tiny-AES-c-e72b6ef \
  IQS7211E_ROOT=$CACHE/flipperone-mcu-firmware-0a88e26 \
  AZOTEQ_SETTINGS_ROOT=$CACHE/zmk-driver-iqs7211e-436d3c4
```

## Entries with no fetch step

- `nordic-s140` is the SoftDevice binary distributed inside the SDK archive.
  Its hash is pinned.
- `qst-qma6100` has no licensed public source. It remains an attribution
  reference, and its behaviour is recorded as pseudocode in
  [`../../r1/reconstructed/`](../../r1/reconstructed/README.md).
- The GoMore algorithms and the Goodix algorithm libraries are binary-only.
  The stock image links them as vendor objects, so a byte-identical build needs
  the vendor's original objects or byte-matched decompiled C for those
  functions. See [`../../docs/roadmap.md`](../../docs/roadmap.md).
