# Source-built Zephyr runtime

This target replaces the proprietary S140 host/controller boundary with the
Apache-licensed Zephyr 3.7.2 Bluetooth host and controller. It compiles the
portable openR1 runtime, every checked-in reconstructed source module, the
model-data constants, Nordic radio HAL, Cortex-M startup, and BAE8 GATT bridge
into one nRF52840 image. Its Zephyr flash-map adapter directly binds the
recovered 36-page product-data region, `kv.bin`, and `sleep.db` through the
source nRF NVMC driver; REG1 settings persistence uses the portable KV store.
Pinned Apache-2.0 FlashDB 2.0.0 and bundled FAL 0.5.99 bind the six-page
`health.db` TSDB at offset `0x2000` with the recovered 32-bit write granularity.
The separate three-page settings partition uses Zephyr NVS to persist SMP bond,
identity, and CCC state before advertising starts.
The source nRF POWER HAL enables the main DC/DC converter before Bluetooth,
matching the recovered stock startup action. Authorized system-settings type-zero
writes persist their normalized flag before applying the corresponding register
write. This surface controls REG1 enable only: it is not a CPU-frequency control
or a regulator measurement, and the wear-driven automatic policy remains gated
until its typed wear/touch/power lifecycle is bound.
The Zephyr ADC driver also owns the exact recovered SAADC routes: battery on
AIN5/P0.29 and PMIC current on AIN3/P0.05 use gain 1/2 and 40-us acquisition;
the NFC rectifier on AIN2/P0.04 uses gain 1/6 and 10-us acquisition. All are
12-bit without oversampling. The PMIC-current and rectifier diagnostic APIs are
live. Battery conversion now takes client bit 0 from the reconstructed YHM2710
shared-power lease before sampling and releases it afterward; periodic battery
production and physical calibration remain open.
Reset causes are decoded directly from the nRF POWER register into the portable
reset model, with a CRC-protected no-init trace record. The source nRF watchdog
driver is configured for one 10-second reset channel, runs while the CPU sleeps,
pauses under a debugger, and is fed by a lowest-priority thread every 1,024
ticks at the recovered 1,024-Hz scheduler rate. Zephyr's fatal policy handler
captures the exception PC/LR and bounded reason code into that retained record,
then resets through CMSIS; the complete fault/reset route remains hardware-test
gated.
The portable wall clock is also active: a lowest-priority 1,024-tick worker
adopts phone-supplied Unix time and signed UTC offset from command `0x05`, then
uses Zephyr's monotonic tick source and newlib `gmtime_r` for query APIs. It
reports time unavailable until a valid phone synchronization is received.
The motion adapter binds Zephyr's source TWIM1 driver at 400 kHz on recovered
P0.11/P0.14, address `0x18`, with P0.15 rising-edge accounting. It compiles
hash-pinned Bosch BMA456 SensorAPI 2.29.0 and ST LIS2DW12 2.1-compatible C,
probes in stock LIS-first/BMA-second order, configures 25 Hz operation, and
exposes the portable bounded, normalized FIFO API. The provider interrupt hooks
are recovered no-ops; production sensor-stream ingestion and axis calibration
remain hardware-validation work.
The touch adapter binds Zephyr's source TWIM0 driver at 400 kHz on recovered
SDA P0.01/SCL P0.12 and the IQS7211E address `0x56`. P0.30 owns the LDO and
P0.17 supplies the falling-edge RDY interrupt. A lowest-priority worker retains
the recovered reset delays, 33-byte write bound, restart timer, wear/factory
source bits, and `0x800`-tick power-release request. Runtime `touchSwitch`
changes reach this adapter, and client bit 2 is bound to the reconstructed
YHM2710 provider. No ring identity or wear/factory lease is installed at
startup, so it still cannot energize or configure the controller.
The NFC adapter hash-gates and links ST's pinned BSD-3-Clause ST25DVxxKC
component. It retains the two-byte register address, 256-byte write bound,
20-byte product mailbox limit, session/GPO configuration, and rising-edge
P0.03 worker. The shared TWIM1 owner switches atomically between motion on
P0.11/P0.14 and dock NFC on P1.11/P1.14; NFC may preempt only between completed
motion transfers, and motion cannot preempt an active dock session. The exact
P1.10 low/10-tick/high/10-tick enable sequence and a typed dock-session mutex
are bound at startup. NFC nevertheless starts disabled and has no automatic or
wire-facing enable policy.
None of those physical behaviors is claimed hardware-validated.

The optical acquisition boundary is source-bound without enabling biometrics by
implication. The target hash-gates and compiles the admitted Goodix GH3X2X demo/
driver sources and exact SpO2 configuration table; no `.a` archive is consumed.
The recovered software `i2c_4` provider uses SCL P1.09, SDA P0.31, eight-bit
device ID `0x28`, and a big-endian 16-bit read register. P0.21 supplies the
falling-edge interrupt, P0.10 controls the emitter, and P1.04 controls reset.
Board preparation acquires YHM2710 client bit 1 and shutdown releases it after
the pins are made inactive. Startup only binds this lifecycle; it does not power
the sensor or start sampling, and no BLE route invokes the retained start/switch/
stop APIs. Raw frames are counted only. The Goodix global algorithm ABI remains
fail-closed, so HR, SpO2, and HRV values are never synthesized.

Health storage starts after the source wall clock and before `sleep.db`, matching
the recovered task order. Its exact `{3,3,3,3,24,6}` schema, control values 2/3,
`health`/`health.db` names, 128-byte record limit, no-init crash-time handoff,
local-day iterator, and one-shot restore are source-bound. Crash restore writes
the live runtime activity, HR, SpO2, and HRV histories; the separate HR averaging
accumulator remains module-owned. Existing exact-length record bodies are decoded
from the bounded recovery workspace, including signed UTC offset, recorded timestamp,
four UInt8 aggregate families, six packed activity buckets, HRV aggregates, and the
preserved reserved tail. The body timestamp and signed offset select the recovered
prior-hour slot, including hour 23 of the previous local day at midnight; the FlashDB
timestamp remains the bounded query/index key. Startup restores only activity, HR,
SpO2, and HRV because temperature and stress have no live runtime cache fields;
short, invalid-time, or otherwise rejected records are counted and skipped.
After the first valid clock sample, each actual local-hour change multicasts the
new hour on recovered event slot 1. The listener builds the exact zero-initialized
128-byte body from the previous runtime cache slot and appends it through FlashDB;
hour zero then resets all six cache families and attempts the recovered empty slot-2
follow-up. Temperature and stress currently contribute their module-owned zero
histories because no producers are bound. Append failures are counted, and the stock
destructive format-and-retry behavior is deliberately not exposed. Slot 0 consumes the
exact 12-byte old/new offset/timestamp tuple. Its admitted actions recover the current day
when the clock first becomes valid and reset all six caches on a local-day transition.
Failed day-start conversion or recovery-workspace allocation is counted without running an
unbounded query.
Requests for destructive formatting, GoMore reinitialization, and unresolved sync-cursor
reset/clamping are counted as suppressed diagnostics.

The custom `openr1_nrf52840` board deliberately exposes only SoC resources
whose package-level presence is established. The recovered motion, touch, and
analog pins are in devicetree; additional sensor pins will move there only with typed
Zephyr adapters and hardware validation. The image currently provides the BAE8 transport, core
protocol runtime, KV/health/sleep storage, wall-clock, REG1, reset/watchdog lifecycle,
motion, fail-closed touch transport/lifecycle, the recovered analog acquisition seam, and
on-demand fail-closed optical transport/lifecycle. Biometric calculation and destructive/
unresolved slot-0 actions are not silently claimed as live; the bounded hourly health
writer uses only existing caches and never fabricates measurements. Touch remains
identity/wear gated and NFC remains policy-disabled.

The repository wrapper preserves west's Python environment across sysbuild,
pins the board root, checks every source checkout before packaging, and verifies
the final signature and member union. Build and package with:

```sh
make zephyr-bundle \
  WEST=/absolute/zephyr-venv/bin/west \
  ZEPHYR_WORKSPACE=/absolute/zephyr-workspace \
  ZEPHYR_TOOLCHAIN=/absolute/gcc-arm-none-eabi-9-2020-q2-update \
  BMA456_ROOT=/absolute/BMA456_SensorAPI-3266db2c \
  LIS2DW12_ROOT=/absolute/lis2dw12-pid-8d4bd52 \
  ST25DVXXKC_ROOT=/absolute/fp-sns-stbox1/Drivers/BSP/Components/st25dvxxkc \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x
```

This produces `build/openr1-zephyr/openr1-source-built.zip`. `zephyr-image`
builds without packaging, `zephyr-package` packages an existing sysbuild tree,
and `zephyr-verify` runs both the offline source-boundary check and bundle
verification.

For a deployable trust anchor, pass an unencrypted owner-controlled MCUboot
ECDSA-P256 PEM to the build. The private key is read by the external build and
is never copied into the output ZIP:

```sh
make zephyr-bundle \
  WEST=/absolute/zephyr-venv/bin/west \
  ZEPHYR_WORKSPACE=/absolute/zephyr-workspace \
  ZEPHYR_TOOLCHAIN=/absolute/gcc-arm-none-eabi-9-2020-q2-update \
  ZEPHYR_SIGNING_KEY=/secure/owner-mcuboot-ec-p256.pem
```

The flash layout places source-built MCUboot at `0x00000000..<0x0000C000` and
the signed application at `0x0000C000..<0x000D1000`. It preserves the retail
settings address range at `0x000D1000..<0x000D4000`, now formatted as a
three-sector Zephyr NVS store, and preserves the recovered 36-page product
data extent at `0x000D4000..<0x000F8000`, and reserves the former retail
bootloader/settings window for an explicit migration procedure. The default
MCUboot development P-256 key is transparent but is not a production trust
anchor; an owner-controlled key remains required before deployment.
The bundle verifier includes the derived public key, checks the ECDSA signature,
and records whether the transparent MCUboot development key was used.
The pinned MCUboot `imgtool` path uses randomized ECDSA nonces, so rebuilt
signed images and ZIP files are not claimed to be byte-for-byte identical even
when the unsigned application is unchanged. Every generated signature and
artifact hash is verified independently.
The NVS schema is intentionally not claimed to be compatible with the retail
Nordic FDS contents; migration or clearing behavior must be validated on owned
hardware before installation over an existing retail layout.
