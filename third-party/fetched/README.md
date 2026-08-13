# Fetched dependencies

Upstreams that cannot be redistributed from this repository. They are downloaded
into a local cache directory, checked against pinned archive hashes, and then
authenticated file-by-file before any build consumes them.

- [`manifest.json`](manifest.json) — the pin: provider, version, archive URL,
  archive SHA-256, license path, the recovered evidence that fixed the version,
  and the production role each component is allowed to play.
- [`verify_vendor.py`](verify_vendor.py) — offline authenticator. Reads the
  manifest, hashes the fetched trees, and fails closed on any mismatch. It also
  cross-checks the CMSIS-FreeRTOS, CmBacktrace, and FreeRTOS-Kernel snapshots
  vendored at [`../../g2/third_party`](../../g2/third_party).
- [`fetch.sh`](fetch.sh) — downloads and unpacks the fetchable subset, then runs
  the authenticator.

## Fetching

```sh
third-party/fetched/fetch.sh /absolute/path/to/vendor-cache
```

The path must be absolute. Each archive's SHA-256 is checked before it is
unpacked, anything already present is skipped, and the run ends by invoking
`verify_vendor.py` across the full set. Nothing is written outside the cache
directory you name.

## Roots the R1 build expects

The R1 targets take each dependency root as a variable rather than assuming a
layout, so the cache can live anywhere:

| Variable | Component | Notes |
| --- | --- | --- |
| `SDK_ROOT` | `nordic-nrf5-sdk` | nRF5 SDK 17.1.0; also supplies SEGGER RTT and the FreeRTOS nRF52 port |
| `FLASHDB_ROOT` | `flashdb` + `fal` | `health.db` only; `kv.bin` is R1-owned |
| `BMA456_ROOT` | `bosch-bma456-sensorapi` | one of the two resolved accelerometer variants |
| `LIS2DW12_ROOT` | `st-lis2dw12-pid` | the other resolved accelerometer variant |
| `ST25DVXXKC_ROOT` | `st-st25dvxxkc-bsp` | point at `.../Drivers/BSP/Components/st25dvxxkc` |
| `TINY_AES_ROOT` | `tiny-aes-c` | AES-128 inverse core |
| `IQS7211E_ROOT` | `flipperone-iqs7211e` | touch controller reference; audit only |
| `AZOTEQ_SETTINGS_ROOT` | `azoteq-iqs7211e-settings` | touch settings reference; audit only |
| `GNU_INSTALL_ROOT` | — | Arm GNU toolchain prefix, for `sdk-image` |

Example:

```sh
make -C r1 vendor-audit SDK_ROOT=$CACHE/nRF5_SDK_17.1.0_ddde560 \
  FLASHDB_ROOT=$CACHE/FlashDB-4e56774 BMA456_ROOT=$CACHE/BMA456_SensorAPI-3266db2 \
  LIS2DW12_ROOT=$CACHE/lis2dw12-pid-8d4bd52 \
  ST25DVXXKC_ROOT=$CACHE/fp-sns-stbox1-e9a3544/Drivers/BSP/Components/st25dvxxkc \
  TINY_AES_ROOT=$CACHE/tiny-AES-c-e72b6ef \
  IQS7211E_ROOT=$CACHE/flipperone-mcu-firmware-0a88e26 \
  AZOTEQ_SETTINGS_ROOT=$CACHE/zmk-driver-iqs7211e-436d3c4
```

## Components with no fetch step

Some manifest entries are pinned but deliberately not downloaded by `fetch.sh`:

- `nordic-s140` is a vendor SoftDevice binary distributed with the SDK.
- `goodix-gh3x2x` is not redistributable and has no public archive; the Goodix
  health/biometric boundary stays disabled until a licensed provider is
  supplied. See [`../../r1/docs/boundaries/GOODIX-PROVIDER-BOUNDARY.md`](../../r1/docs/boundaries/GOODIX-PROVIDER-BOUNDARY.md).
- `qst-qma6100` awaits official licensed source; the third accelerometer variant
  is disabled.
- `r1-sleep-journal` is not an upstream at all — it marks the R1-specific
  behavior where clean-room implementation is permitted.

An absent optional provider makes the corresponding feature return
`R1_ERROR_UNSUPPORTED`. It never causes fabricated data.
