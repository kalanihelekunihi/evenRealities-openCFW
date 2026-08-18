# Source-built Zephyr/MCUboot bundle closure

## Closed opaque-runtime boundary

The `openr1_nrf52840` target provides an alternate complete flash image that
does not consume Nordic S140, the retail R1 bootloader, a stock application, a
binary algorithm library, or any other executable firmware blob. Its executable
members are built from openR1 C plus pinned Zephyr 3.7.2, hal_nordic, CMSIS,
TinyCrypt, and MCUboot source revisions recorded in
`third-party/fetched/manifest.json`. The same gate now covers FlashDB 2.0.0
and its bundled FAL 0.5.99; their consumed headers, licenses, and six translation
units are individually hash-pinned. It also covers the admitted 59-file Goodix
GH3X2X source/header/license subset; no vendor algorithm or driver archive enters
the build.

The custom board layout is:

| Region | Address range | Policy |
| --- | --- | --- |
| source-built MCUboot | `0x00000000..<0x0000C000` | ECDSA-P256 validation on every boot |
| signed openR1 application | `0x0000C000..<0x000D1000` | Zephyr host/controller and all retained reconstructed modules |
| openR1 Bluetooth settings | `0x000D1000..<0x000D4000` | three-sector Zephyr NVS store for persistent SMP bond, identity, and CCC state |
| recovered product data | `0x000D4000..<0x000F8000` | complete 36-page data extent, preserved |
| migration reserve | `0x000F8000..<0x00100000` | held for a hardware-tested retail-layout migration |

MCUboot is configured as a single-slot boot path and validates slot 0 at every
boot. This makes the source-built bundle a bootable-image replacement rather
than an application that calls into a preinstalled SoftDevice. The default
MCUboot development key is transparent and suitable only for development;
`ZEPHYR_SIGNING_KEY` supplies an owner-controlled P-256 trust anchor.

## Retained recovered corpus

Zephyr normally garbage-collects unreachable translation-unit sections. The
target's `openr1_reconstructed.ld` explicitly retains all 14 reconstructed
families, including Goodix, GoMore, generated model data, quantized runtime,
and reconstructed peripheral/middleware modules. The offline verifier requires
the CMake source list and linker `KEEP` list to contain the same exact corpus.

The BAE8 service is implemented over Zephyr's source-built Bluetooth host and
controller. It exposes service `BAE80001` and characteristics `BAE80010` through
`BAE80013`, routes channel 2 into `r1_runtime_receive_eus`, keeps channel 1
fail-closed, and uses a completion-tracked four-slot notification pool. Zephyr
settings are loaded after Bluetooth initialization and before advertising, so
SMP bonds, local identity, and CCC state survive restart in the dedicated NVS
partition.

The product power adapter also closes the recovered direct REG1 action without
an S140 SVC. Zephyr's source SoC initialization and the explicit product startup
both enable the nRF52840 main DC/DC converter before Bluetooth starts. A changed,
authorized type-zero system setting first commits its normalized flag to
`kv.bin`, then writes and reads back `POWER.DCDCEN` through the pinned Nordic
source HAL. This is an enable control, not a CPU-frequency or physical-regulator
measurement. The separate glasses-wear automatic policy remains unbound until
its wear, touch-lease, and shared-power lifecycle is source-bound.

The source nRF SAADC driver is configured with the recovered physical routing
and conversion geometry: AIN5/P0.29 battery and AIN3/P0.05 PMIC current at
gain 1/2 and 40 us, plus AIN2/P0.04 NFC rectifier at gain 1/6 and 10 us. Every
channel is 12-bit with oversampling disabled. The adapter retains the recovered
sample counts and portable voltage conversion models. Battery acquisition is
now bracketed by client bit 0 of the reconstructed YHM2710 shared-power lease.
The provider probes chip ID `0xA0`, runs the exact five-register initialization,
and fails closed without binding clients if the device is absent. Database startup decodes the
exact four-byte persisted `power` class, adopts a valid battery type into the runtime controller,
and applies valid signed voltage compensation. A boot seed and each read-only device-status access
take five live samples plus a fail-closed YHM register-6 charge-state read before dispatch. PMIC
event-driven refresh, physical calibration, and owned-ring validation remain open.
The adjacent one-byte `r_size` class is decoded with its exact 6...15 validity gate and retained
read-only; it is not treated as sufficient IQS7211E layout identity.

Motion acquisition is now source-bound too. The custom board routes Zephyr's
TWIM1 driver at 400 kHz over P0.11/P0.14 to address `0x18`, with P0.15 as the
rising-edge input. The build requires externally supplied Bosch and ST source
roots and hashes every consumed source, header, and license against the
repository manifest before packaging. Bosch BMA456 SensorAPI 2.29.0 and ST
LIS2DW12 2.1-compatible C feed the portable stock-order selector, exact 25 Hz
configuration, 31-sample bound, FIFO normalization, and LIS double-tap-disable
surface. All three provider objects must have nonempty loadable linker-map
spans. The target now initializes and polls the reconstructed sensor-stream
framework at 1,024 Hz, composes its lists with the reconstructed generic-registry
family, creates the exact `"acc"`/188-byte and `"temp"`/two-byte streams, and binds the motion FIFO
reader. Each batch carries at most 30 normalized XYZ samples, the recovered
count/padding/timestamp layout, and read-only signed axis offsets decoded from
`nv_r1` bytes 68...73. The exact seven-slot GoMore authorization state owns reference-counted
`acc`, `raw_hr`, `hr`, and `hrv` listeners with masks `02/1E/1E/02/04/0C/00`; global health requests
slots 0/3 and therefore starts only `acc`. The reducers and readiness barrier compile from
transparent C. The staged record is serialized across one engine attempt; readiness clears before
the attempt and acc/raw counts clear only after success. The target initializes a dynamic
source-built 0x39E0-byte engine with its exact filter designers and profile while health is enabled.
Its 0x2E0-byte prior state restores from and appends to the recovered `pKey.bin` slots. Existing
valid key prefixes remain untouched; a wholly erased page receives a source-visible all-zero
layout anchor that the engine never consumes for authorization. HSM mask `0x08` supplies checked frame word0
to the exact `raw_hr` container without assigning waveform semantics. The 16-stage engine executor
is target-composed from transparent C. Live `acc`, `raw_hr`, `hr`, and `hrv` topic batches enter the
exact host adapter, cross the recovered readiness barrier, execute every recovered stage in stock
order, copy the 264-byte host result snapshot, and enter the recovered output lifecycle. That
lifecycle dynamically reconciles slot-4 optical authorization, feeds the exact packed cumulative
activity words into the ten-minute/daily accumulator, and constructs, validates, serializes, and
persists final sleep records through `sleep.db`. No dormant output field is relabeled or published
without a proven stock consumer.
Validated updated HR, SpO2, and HRV results from the target-bound admitted provider traverse a
separate observer, recovered result planner, and exact scalar storage consumer. The persisted
global-health bit/timestamp is restored before that route is bound. Physical-axis, wavelength,
biometric-equivalence, and owned-hardware validation remain explicit gates.

Touch transport and lifecycle are source-bound without pretending the product
identity is known. Zephyr TWIM0 runs at 400 kHz on recovered
SDA P0.01/SCL P0.12 to IQS7211E address `0x56`; P0.30 controls the LDO and P0.17
is the falling-edge RDY input. The worker retains the 33-byte maximum register
write, exact raw-tick reset sequence, restart timer, wear/factory request bits,
and client-bit-2/`0x800`-tick power contract. Runtime `touchSwitch` changes reach
the adapter. Client bit 2 is bound to the YHM2710 lease with its delayed release,
but no validated ring layout/size or wear/factory request is supplied at startup.
The controller therefore remains de-energized and touch samples remain unavailable
by construction.

The NFC digital path is source-bound behind the same honest resource policy.
The build hashes both ST25DVxxKC C files, both consumed headers, and the
BSD-3-Clause license before linking, then requires nonempty loadable spans from
both provider objects. The product adapter preserves the two-byte register
address, 256-byte transport write bound, 20-byte mailbox limit, security-session
and GPO configuration, and a rising-edge P0.03 worker. A single R1-owned TWIM1
mutex switches the source Nordic peripheral between motion P0.11/P0.14 and NFC
P1.11/P1.14 only between completed transfers. Dock NFC may preempt motion;
motion never preempts an active dock session. Startup also binds the exact P1.10
low/10-tick/high/10-tick dock-enable lifecycle and a typed dock-session mutex.
NFC remains disabled because no automatic or wire-facing enable policy requests
activation, not because an opaque resource implementation is missing.

The shared battery/optical/touch rail is source-bound through the transparent
YHM2710 reduction. P1.01 uses the recovered seven-bit state-command framing,
13/52 us symbol pulses, 209 us recovery, parity, nine attempts, chip-ID check,
and initialization sequence. The portable three-client lease emits register 2
`0xA8` only on zero-to-one and `0x28` only on one-to-zero. The source-built
optical adapter now adopts client bit 1 around its on-demand board lifecycle;
startup does not acquire the rail or start sampling. Every physical rail meaning
remains owned-hardware validation.

The source-built target also adopts the recovered software `i2c_2` GXT310 path. A single Zephyr
software-TWI owner installs all recovered board-pin operations and serializes bit-level transfers;
GXT310 uses SCL P1.13/SDA P0.28 while Goodix keeps its separate `i2c_4` pins. Startup performs the
exact two-address (`0x90`/`0x94`) register-`0x03` ID check and fails closed without preventing BLE
recovery when either device is absent. The typed acquisition surface implements register-`0x00`
signed big-endian conversion (`raw * 125 / 16` integer milli-units), 80-ms startup, ten paired
samples separated by 5 ms, extrema trimming, and read-only application of the exact six-byte
calibration at persisted `nv_r1` offset `0x3E` when that record is not erased. It does not accept
caller-supplied calibration. The exact `"temp"` stream provider now performs one paired read,
applies the two unsigned 16-bit calibration magnitudes with recovered 32-bit wrapping semantics,
averages with signed truncation toward zero, and returns the low two bytes. The exact dormant
`"once"` listener is retained at rate 1/per-sample mode; when explicitly started it applies the
30-attempt/five-consistent-value reducer, publishes the exact event-9 payload, and feeds the
product-owned hourly temperature cache. It is not registered at startup and assigns neither
physical channel labels nor clinical units. The final-sleep timing and record path is composed, but
the retail physical-temperature source used by its body-temperature field is not yet semantically
resolved; the source implementation therefore records zero rather than inventing a channel or
unit. The separate dormant stress producer remains uncomposed.

The Goodix raw-acquisition boundary is now source-bound. The target compiles and
retains the public Goodix demo kernel, register driver, AGC/motion/soft-ADT modules,
and exact SpO2 configuration table, plus the transparent R1 port and adapter. The
recovered software `i2c_4` engine drives SCL P1.09 and SDA P0.31 with device ID
`0x28`; P0.21 is the falling-edge interrupt, P0.10 is the emitter control, and
P1.04 is reset. Interrupt work reaches `Gh3x2xDemoInterruptProcess`, and the
bounded motion FIFO can supply the democode accelerometer callback. Start, profile
switch, and stop are retained typed APIs only; no BLE route invokes them. Raw
frames are counted without being relabeled as biometric results. The democode's
20-row global frame table now crosses a checked vendor-free provider ABI with
bounded lifecycle, version/register routing, and mask/count-validated 16-word
results. Transparent HBA, HRV, and SpO2 roots are target-bound with caller-owned persistent
plan/state/workspace objects. Normal acquisition starts only requested HR/HRV/HSM/SpO2 bits and
never substitutes factory profiles; malformed mixed-mask initialization rolls back earlier roots.

The reset/watchdog lifecycle is source-bound as well. Startup decodes and
clears the nRF RESETREAS register through the portable reset model, preserving
a CRC-protected trace in Zephyr no-init RAM. A single source nRF watchdog
channel resets after 10 seconds, runs during CPU sleep, pauses under debugger
halt, and is fed from the lowest-priority thread every 1,024 ticks at a
1,024-Hz kernel rate. The strong Zephyr fatal policy handler records the
exception PC/LR and bounded fatal reason in that retained trace before a CMSIS
system reset. Fault injection and reset-retention behavior remain owned-hardware
validation items.

The R1-owned clock is live on the same recovered 1,024-Hz cadence. It adopts
the Unix epoch and signed UTC offset written by phone command `0x05`, advances
that epoch from Zephyr's monotonic ticks, and supplies UTC-offset and local
`struct tm` queries plus health local-day boundaries through the reconstructed
exact Unix/Gregorian converter. It remains explicitly unsynchronized until
the phone provides a valid timestamp rather than fabricating wall time.

## Bundle proof

The ZIP contains only:

- `manifest.json` with source locks, flash layout, limitations, and hashes;
- the MCUboot public key;
- source-built MCUboot Intel HEX;
- the signed openR1 application as canonical BIN and Intel HEX; and
- their canonical non-overlapping full-flash Intel HEX union.

`tools/package_zephyr_bundle.py` rejects source checkout drift, modified or untracked
provider files, address-range violations, mismatched build configurations, and
invalid ECDSA signatures. It also parses the final linker map and rejects any
reconstructed object without a nonempty loadable application span. It separately
requires nonempty linker-map spans for all Bosch/ST motion, ST NFC, FlashDB/FAL
health-storage, and 16 Goodix source-provider/port objects.
`tools/verify_zephyr_bundle.py` independently checks
every member hash, the BIN/HEX identity, canonical HEX union, MCUboot hash TLV,
P-256 signature, and public-key fingerprint.

The build inputs and unsigned application are deterministic for an identical
pinned workspace, but the pinned MCUboot `imgtool` signer requests randomized
ECDSA nonces from Python `cryptography`. Consequently, two valid builds may
have different signature bytes (and may differ by one byte in DER-encoded
signature length), so neither the signed BIN nor the ZIP is claimed to be
byte-for-byte reproducible. Each produced bundle is instead independently
validated against its recorded hashes and bundled public key.

## Remaining product work

This closes the opaque BLE/controller and bootloader dependency, not all device
integration. The Zephyr target presently binds BAE8, the portable runtime,
direct NVMC access to the recovered 36-page product region, `kv.bin`, pinned
FlashDB/FAL `health.db`, `sleep.db`, REG1 control, exact SAADC acquisition, the Bosch/ST motion bus,
fail-closed IQS7211E transport/lifecycle, and fail-closed ST25DVxxKC mailbox/
TWIM1 handoff, reconstructed YHM2710 shared-power binding, and P1.10 dock lifecycle;
public health-settings are canonicalized, ACK-ordered, and durably update the live global
health gate, exact seven-slot authorization state, and transparent engine ownership. Live sensor
topics now drive all 16 recovered GoMore stages, dynamic sleep optical authorization, cumulative
activity aggregation, final-sleep construction, `sleep.db` persistence, and the synchronized sleep
commit hook. HR, SpO2, HRV, and activity daily
queries now use the exact three-day FlashDB merge callbacks and persist named `hsync` cursors only
after matching notification ACKs; HRV uses the independent recovered UInt16 FlashDB/FIFO/RAM
merge and named cursor, while activity uses its independent recovered packed-word merge and
cursor. The admitted wall-clock cadence drives the exact 10,800-second
five-leg automatic history order, and a bounded empty-queue service emits one serial-zero leg at a
time without exceeding the recovered 50-record BLE queue. Encoded fragment cost is also checked
before each response/notification is admitted; a maximally fragmented activity FIFO therefore
returns an ACK-resumable page rather than failing the complete atomic enqueue. Accepted HR, SpO2,
and HRV storage events also execute their recovered call to the common automatic-sync gate and
attempt the first drain-aware leg immediately. Touch identity/wear provisioning, an explicit NFC
activation policy, the destructive slot-0 format/retry actions, the dormant stock-unreachable
stress producer, and the unresolved physical-temperature binding remain intentionally fail-closed
or evidence-constrained boundaries, not opaque inputs. Backward-time and failure-60 GoMore resets
now perform the recovered fresh-engine lifecycle without resume state. The composed motion,
Goodix, GoMore, biometric, activity, and sleep paths still require calibration, equivalence testing,
fault injection, and owned-ring validation before their outputs can be treated as product- or
clinically equivalent. The former retail bootloader
window remains reserved until a recoverable migration procedure is tested.
Zephyr NVS is not asserted to decode the retail Nordic FDS settings format, so
settings migration or clearing also remains an owned-hardware validation item.
No flash/install claim is made by this build closure.

## Reproduction

```sh
make zephyr-source-verify
make zephyr-bundle \
  WEST=/absolute/zephyr-venv/bin/west \
  ZEPHYR_WORKSPACE=/absolute/zephyr-workspace \
  ZEPHYR_TOOLCHAIN=/absolute/gcc-arm-none-eabi-9-2020-q2-update \
  BMA456_ROOT=/absolute/BMA456_SensorAPI-3266db2c \
  LIS2DW12_ROOT=/absolute/lis2dw12-pid-8d4bd52 \
  ST25DVXXKC_ROOT=/absolute/fp-sns-stbox1/Drivers/BSP/Components/st25dvxxkc \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x
make zephyr-verify
```

On macOS, the wrapper temporarily hides the pinned toolchain's configure-only
`arm-none-eabi-gdb-py` probe under an advisory lock because that 2020 x86_64
debugger can hang under current Rosetta. It restores the executable on every
exit. GCC, binutils, source inputs, signatures, and bundle members are unchanged.
