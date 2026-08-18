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
The one-page `pKey.bin` region at offset `0xA000` now binds the recovered
736-byte GoMore prior-state restore/append/compaction format. Existing valid
64-byte key prefixes are preserved; an entirely erased page receives an explicit
all-zero openR1 prefix used only as the state-layout anchor, never as an
authorization credential.
The separate three-page settings partition uses Zephyr NVS to persist SMP bond,
identity, and CCC state before advertising starts. Product advertising restores
the exact fixed-width serial/`FF` sentinel from `nv_r1`, includes the serial only
when provisioned, runs at 100 ms for 60 seconds then 1 second, restarts after the
first connection for the second role, and stops after phone plus glasses roles
are occupied. Recovered `nv_r1` byte `0x70` marker `0x55` selects the `_FAC`
name and 100-ms fast-indefinite factory lifecycle.
The same partition holds a separate CRC-protected `openr1_auth/owner` record.
Only the first pairing that completes with bonding may enroll it. Encryption,
an existing bond, and `pairAuth` remain independent transport/routing facts and
cannot create or replace the owner. Resolved sessions match the persisted BLE
identity before the runtime receives product authorization; malformed records
fail closed. A local-only platform API deletes the record, unpairs, clears live
authorization, and disconnects the owner. Physical ATT, replay, and persistence
validation remain open.
The source nRF POWER HAL enables the main DC/DC converter before Bluetooth,
matching the recovered stock startup action. Authorized system-settings type-zero
writes persist their normalized flag before applying the corresponding register
write. This surface controls REG1 enable only: it is not a CPU-frequency control
or a regulator measurement. The independently authorized glasses-status route
now binds the recovered wear-driven immediate-disable/delayed-enable policy,
touch lease, and immediate-fast/exact-delayed-slow BLE profiles; physical power,
timing, and coexistence validation remains gated.
The Zephyr ADC driver also owns the exact recovered SAADC routes: battery on
AIN5/P0.29 and PMIC current on AIN3/P0.05 use gain 1/2 and 40-us acquisition;
the NFC rectifier on AIN2/P0.04 uses gain 1/6 and 10-us acquisition. All are
12-bit without oversampling. The PMIC-current and rectifier diagnostic APIs are
live. Battery conversion now takes client bit 0 from the reconstructed YHM2710
shared-power lease before sampling and releases it afterward. Startup decodes the exact
four-byte persisted `power` record and adopts battery types 1...4 plus valid signed voltage
compensation into the runtime controller. A boot seed and each read-only device-status access now
take five live samples and read YHM2710 register 6 before dispatch snapshots the response. Status
0xA...0xC maps to charging and 0xD to full; transport failures leave the previous state intact.
No autonomous cadence is claimed because none is yet proven by the recovered call graph. PMIC
event-driven refresh, physical calibration, and owned-ring validation remain open.
The one-byte `r_size` class is also strictly decoded and exposed only for values 6...15. It does
not provision IQS7211E because ring size alone cannot prove the independent physical layout.
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
uses Zephyr's monotonic tick source and the reconstructed exact Unix/Gregorian
converter for query APIs and health local-day boundaries. It
reports time unavailable until a valid phone synchronization is received. In
parallel, the reconstructed `sys rtc` object and generic registry are live:
RTC2 is source-bound through Zephyr's counter driver at prescaler 4095 and IRQ
priority 6, its eight hardware ticks advance the recovered epoch service, and
phone time is routed through the recovered slot-0x14 request path. RTC0 remains
with Bluetooth and RTC1 remains the Zephyr system clock.
The motion adapter binds Zephyr's source TWIM1 driver at 400 kHz on recovered
P0.11/P0.14, with P0.15 rising-edge accounting. It compiles hash-pinned Bosch
BMA456 SensorAPI 2.29.0 and ST LIS2DW12 2.1-compatible C plus the transparent
QMA6100 reconstruction, probes in stock LIS-at-`0x18`, BMA-at-`0x18`, then
QMA-at-`0x12`/`0x13` order, and configures 25 Hz operation. The QMA path binds
the recovered 64,000-cycle delay, locked transport, raw FIFO, tap-disable, and
interrupt-to-worker seams; the common adapter applies the exact signed `/4`
normalization once. The target initializes and polls the reconstructed
1,024-Hz sensor-stream framework, creates its exact `"acc"`/188-byte and
`"temp"`/two-byte singletons, and binds them to the normalized FIFO plus signed
Int16LE `nv_r1` axis offsets and calibrated one-pair GXT310 read respectively.
No algorithm listener is registered at startup. A retained typed control can register the exact
`"gomore"` rate-1 batch listener and stage the recovered 25-sample axis transform without running
the health engine or publishing results. The retained typed one-shot control can also register
the exact `"once"` listener at rate 1/per-sample mode, enforce the recovered 30-attempt and
five-consistent-value policy, then store its event-9 result in the hourly temperature cache.
Physical-axis/channel labels, a public BLE trigger, and owned-ring behavior remain validation work.
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

The dual GXT310 acquisition boundary is source-bound through the same reconstructed software-TWI
engine. A shared Zephyr owner installs the recovered GPIO operations once, serializes complete
bit-level transfers, and assigns `i2c_2` to SCL P1.13/SDA P0.28 while retaining the existing
Goodix `i2c_4` mapping. Startup performs the recovered fail-closed two-address ID check at raw
addresses `0x90`/`0x94`; absent or mismatched hardware leaves the provider unavailable without
blocking BLE recovery. Typed reads preserve register `0x00`, signed big-endian conversion by
`125/16` to integer milli-units, 80-ms startup, ten paired samples at 5-ms intervals, extrema
trimming, and read-only application of the persisted six-byte `nv_r1` calibration at offset
`0x3E` when it is not erased. The target does not expose caller-supplied calibration. Its exact
two-byte stream vtable performs the recovered one-pair calibrated average with 32-bit wrapping
and signed truncation toward zero. The exact one-shot listener/event-9/daily-cache path is now
bound behind an explicit dormant API; no boot activation, BLE control, channel role, or clinical
unit is inferred.

The optical acquisition boundary is source-bound without enabling biometrics by
implication. The target hash-gates and compiles the admitted Goodix GH3X2X demo/
driver sources and exact SpO2 configuration table; no `.a` archive is consumed.
The recovered software `i2c_4` provider uses SCL P1.09, SDA P0.31, eight-bit
device ID `0x28`, and a big-endian 16-bit read register. P0.21 supplies the
falling-edge interrupt, P0.10 controls the emitter, and P1.04 controls reset.
Board preparation acquires YHM2710 client bit 1 and shutdown releases it after
the pins are made inactive. Startup only binds this lifecycle; it does not power
the sensor or start sampling, and no BLE route invokes the retained start/switch/
stop APIs. Raw frames are counted only. The Goodix 20-row global frame table now
passes through a vendor-free checked provider ABI, including lifecycle, versions,
virtual registers, and mask/count-validated 16-word results. A retained source composer reproduces
the exact separate HR/HBA, HRV, and SpO2 input construction, lifecycle, public update masks and
HR-to-HRV carry, including R1's `0x00FF` SpO2 mask, word-0 mirror, and cleared zero tail. The
persistent biometric root executors are target-bound with explicit HBA/HRV/SpO2
plan/state/workspace ownership. Normal acquisition starts only requested HR/HRV/HSM/SpO2 bits;
factory masks are not used as a substitute. An independent observer accepts only bridge-validated updated
records. The public Goodix HR and SpO2 layouts are narrowed into the recovered R1 one-shot result
plans and stored through the exact scalar cache consumers only while the persisted `dev_info`
health bit is enabled. The exact product-side `raw_hr` backing is live: HSM mask `0x08` observes
the first checked Goodix frame word, appends it once to the 30-word container, and never produces a
fake biometric result. Physical wavelength, scale, and clinical meaning remain unproven.

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
SpO2, and HRV; temperature and stress use separate module-owned live caches but are not restored
by the recovered crash record;
short, invalid-time, or otherwise rejected records are counted and skipped.
The same storage owner now exposes exact eight-byte HR, SpO2, and HRV event consumers with
firmware-clock/local-hour sampling and independent rolling accumulators. HR and SpO2 are fed by
the checked Goodix result observer, which also routes validated HRV results to the HRV consumer.
After the first valid clock sample, each actual local-hour change multicasts the
new hour on recovered event slot 1. The listener builds the exact zero-initialized
128-byte body from the previous runtime cache slot and appends it through FlashDB;
hour zero then resets all six cache families and attempts the recovered empty slot-2
follow-up. Temperature remains zero unless the dormant one-shot API completes successfully, and
stress remains zero because no producer is bound. Append failures are counted, and the stock
destructive format-and-retry behavior is deliberately not exposed. Slot 0 consumes the
exact 12-byte old/new offset/timestamp tuple. Its admitted actions recover the current day
when the clock first becomes valid and reset all six caches on a local-day transition.
Failed day-start conversion or recovery-workspace allocation is counted without running an
unbounded query.
The exact 24-byte `hsync` class is decoded at startup. Slot-0 reset/clamp reconciles only
the four named cursors, preserves both unresolved words byte-for-byte, and commits the result
through the hardened `kv.bin` snapshot writer. REG1, public health-settings, and hsync mutations
share one Zephyr mutex. The exact health-settings planner queues its ACK before persisting only a
normalized enable transition at `dev_info` byte 24 bit 0 and timestamp offset 32; raw-only private
event `0x100D` transitions reconcile the exact seven-slot GoMore authorization state. Global health
selects slots 0 and 3 and therefore opens only their shared accelerometer dependency; optical
listeners are opened only by slots whose recovered masks require them. Successful cursor commits
and failures are counted separately. Destructive health-database formatting remains deliberately
suppressed, but the recovered backward-time and failure-60 GoMore reinitializations are live: they
disable dynamic slot 4, discard resume state, clear staged topics, and initialize a fresh engine.
Normal health-enable/profile reconciliation allocates and initializes the transparent sleep engine.
Live topics execute all 16 recovered stages, copy the exact output snapshot, dynamically reconcile
sleep optical authorization, aggregate cumulative activity, and persist validated final sleep.

Public HR, SpO2, HRV, and activity daily-history requests use the recovered 259,200-second FlashDB window. Exact
128-byte records are decoded and calendar-normalized, prior local days flow through the pinned
oldest-first scalar merge callbacks, current RAM is appended last, and every emitted packet carries
an ACK context. HRV uses its independent seven-byte UInt16 slot merge and six-byte current-latest
prefix; activity uses its independent 144-bucket packed-word merge. The invalid-clock FIFO is
merged between flash and RAM; mode-1 ACKs consume its
matching prefix, while only mode-0/2 ACKs commit the corresponding named `hsync` word.
Encoded activity pages are capped by the same 50-fragment EUS queue boundary. Reaching that
boundary completes the current page successfully; per-packet ACKs consume the exact offline FIFO
prefix or advance the durable cursor, so a later query resumes without an atomic enqueue failure.
Accepted HR, SpO2, and HRV storage events also execute their recovered common `0x8B138`
post-storage action: they re-evaluate the same authenticated three-hour gate and opportunistically
start its first drain-aware leg. No separate unsolicited sample wire format is invented.
The main wall-clock cadence also drives the recovered 10,800-second automatic history gate.
Only an encrypted, bonded, authorized phone-role link can schedule its exact HR, SpO2, HRV,
activity, and unsynchronized-sleep order. A five-bit pending set and empty-queue admission service
publish one serial-zero leg at a time, preserving the recovered 50-record BLE queue at maximum
history sizes and discarding unfinished work on phone disconnect.

The custom `openr1_nrf52840` board deliberately exposes only SoC resources
whose package-level presence is established. The recovered motion, touch, and
analog pins are in devicetree; additional sensor pins will move there only with typed
Zephyr adapters and hardware validation. The image currently provides the BAE8 transport, core
protocol runtime, KV/health/sleep storage, wall-clock, REG1, reset/watchdog lifecycle,
payload-redacting EP recovery, the twelve-page `log.bin` writer, the exact 8-KiB structured-log
cache/encoders/periodic persistence service, and the exact bounded composite diagnostic source.
The source is retained as an internal C API only, admits one encrypted/bonded/independently
authorized phone-role snapshot, and tears it down on disconnect or authorization loss; no raw
flash handle or undocumented BLE export command is exposed. The image also binds all three motion fallbacks, fail-closed touch
transport/lifecycle, the recovered analog acquisition seam, and
on-demand optical transport/lifecycle. Transparent HBA, HRV, SpO2, and GoMore biometric/activity/
sleep calculation is live; destructive or unresolved slot-0 actions are not silently enabled. The bounded hourly health
writer uses only existing caches and never fabricates measurements. Touch remains
identity/wear gated and NFC remains policy-disabled.

The repository wrapper preserves west's Python environment across sysbuild,
pins the board root, checks every source checkout before packaging, and verifies
the final signature and member union. On macOS it also serializes and temporarily
hides only the pinned 2020 `gdb-py` configure probe, which can hang under current
Rosetta, and restores it on exit; GDB is not a firmware input. Build and package with:

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

Before any owned-device installation, capture the complete 1-MiB internal-flash
recovery basis and the complete 776-byte architected UICR register extent
`0x10001000..<0x10001308` through an authorized read path, then run the offline
preflight. When retail memory isolation prevents a direct read below `0x27000`,
`tools/assemble_r1_ace_recovery.py` may reconstruct only that protected extent
from the hash-pinned official S140 7.2.0 HEX, source-prove the two MBR words from
the byte-exact bootloader plus live UICR, and mirror the ACL-protected primary
settings page only from its CRC-valid live backup under the pinned Nordic
redundancy source and prior same-device identity evidence. All 216 readable
pages, the complete live application, and the owner bootloader must pass their
byte-exact checks. Its evidence JSON is mandatory in that case:

```sh
python3 tools/prepare_zephyr_deployment.py \
  build/openr1-zephyr/openr1-source-built.zip \
  --flash-backup /secure/r1-internal-flash-1MiB.bin \
  --flash-backup-provenance /secure/r1-recovery-basis.json \
  --uicr-backup /secure/r1-uicr-0x308.bin \
  --output build/r1-deployment-preflight
```

The generated plan forbids mass erase, requires sector erase of the complete
source-built install partition plus exact readback, hashes every preserved
product partition, requires UICR to remain byte-identical, and provides
separate canonical internal-flash and UICR recovery HEX files. It does not
provide exact retail rollback on-device; that recovery requires authorized
debug access and exact internal-flash plus UICR readback verification. Once the
source boot partition is installed, its `OPENR1-RECOVERY` GATT service can
replace an interrupted or invalid signed application without modifying the
bootloader.

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

`tools/build_zephyr_bundle.py --encrypted-signing-key` is the preferred local
owner build path. It retrieves the passphrase from Keychain service
`com.sybilsight.r1-owner-signing`, decrypts the P-256 key into a mode-0600
temporary file for sysbuild/imgtool, and removes that file on every exit.

After the source boot partition has been installed, upload a newly verified
owner-signed application without touching the bootloader or product data:

```sh
python3 tools/upload_zephyr_recovery.py \
  build/openr1-zephyr/openr1-source-built.zip --match OPENR1-RECOVERY
```

The flash layout places source-built MCUboot plus its BLE recovery loader at
`0x00000000..<0x00027000` and the signed application at
`0x00027000..<0x000D1000`. The offline first-install preflight recognizes the
settings range only when it is fully erased or has the exact Nordic FDS
two-data/one-swap page geometry, retains those original bytes in the recovery
image, and erases `0x000D1000..<0x000D4000` for a fresh three-sector Zephyr
NVS store. Retail bond credentials are not imported, so the owner must pair
again. It preserves the recovered 36-page product data extent at
`0x000D4000..<0x000F8000`. The former retail
bootloader/settings window at `0x000F8000..<0x00100000` is erased and verified
before a recovery upload so opaque executable bytes cannot survive. The default
MCUboot development P-256 key is transparent but is not a production trust
anchor; an owner-controlled key remains required before deployment.
The bundle verifier includes the derived public key, checks the ECDSA signature,
and records whether the transparent MCUboot development key was used.
The pinned MCUboot `imgtool` path uses randomized ECDSA nonces, so rebuilt
signed images and ZIP files are not claimed to be byte-for-byte identical even
when the unsigned application is unchanged. Every generated signature and
artifact hash is verified independently.
The preflight rejects unknown or interrupted settings layouts, requires reset
to remain held through the exact 1-MiB readback, and retains byte-exact retail
rollback artifacts. Physical erase/readback, fresh NVS first boot, and owner
re-pairing still require validation on the owned ring.
