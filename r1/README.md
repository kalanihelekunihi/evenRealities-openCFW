# openR1

`openR1` is a clean-room, portable C implementation of the observable Even Realities R1
firmware contract. It is derived from the repository's recovered protocol, behavioral, memory,
and security-audit evidence; it is not reconstructed vendor source and is not byte-identical to
the stock image.

The first milestone implements the normal EUS transport, both direction-specific inner checksum
schemes, bounded reassembly, safe system-command dispatch, device state, the recovered flash
partition map, and the two recovered notification queues. Hardware access is behind a platform
interface. The legacy vendor-backed target additionally links Nordic S140 integration, BAE8 service,
Peer Manager/FDS bond storage, `nrf_ble_gatt`, and Nordic advertising sources. A second nRF52840
target replaces S140 and the retail boot dependency with pinned, source-built Zephyr 3.7.2
Bluetooth host/controller and ECDSA-P256 MCUboot, producing a self-contained full-flash bundle.
It currently binds BAE8, persistent Zephyr SMP settings, the portable runtime, source-backed
KV/sleep flash storage, the pinned FlashDB/FAL `health.db` TSDB, the exact three-channel SAADC geometry, phone-synchronized wall time with reconstructed exact calendar conversion,
reset-reason capture, the recovered watchdog, the Bosch/ST motion bus, the IQS7211E TWIM0/GPIO
lifecycle, and the reconstructed YHM2710 shared-power service. Touch remains deliberately unpowered
until ring identity and a wear/factory lease are provisioned. The pinned ST25DVxxKC provider,
bounded mailbox adapter, P0.03 GPO worker, exact P1.10 dock-enable lifecycle, and
dock-preempts-motion TWIM1 handoff are source-bound; NFC remains disabled until an explicit product
policy requests it. The health startup uses the recovered six-schema contract, retained crash-time
handoff, exact 128-byte hourly-body codec, and live startup recovery into the runtime
activity/HR/SpO2/HRV caches. Valid local-hour changes now flow from the source clock through
event slot 1 to exact non-destructive FlashDB appends, with previous-hour selection and six-cache
midnight reset. The exact slot-0 old/new time tuple now drives initial-valid current-day recovery
and cross-day resets; destructive format/retry and GoMore reinitialization remain suppressed
diagnostics. The exact 24-byte `hsync` class is loaded and persisted through hardened `kv.bin`
snapshots: only HR/SpO2/HRV/activity cursors reset or clamp, while both unresolved words round-trip
unchanged. Startup also decodes the exact four-byte persisted `power` record and adopts battery
types 1...4 into the runtime controller without enabling an unproven periodic sampler. The exact
one-byte `r_size` class is decoded read-only but cannot select touch calibration without the
independent physical layout identity. The reconstructed 1,024-Hz sensor-stream runtime is now
polled on target; its exact `"acc"`/188-byte provider applies the persisted three-axis
calibration, and its exact `"temp"`/two-byte provider performs one calibrated GXT310 pair read
with the recovered wrapping arithmetic. Its dormant typed one-shot control now binds the exact
rate-1/per-sample listener, 30-attempt/five-consistent-value reducer, event 9 payload, and hourly
temperature cache without starting at boot or assigning physical/clinical semantics. The public
measurement route and owned-hardware validation remain open. The exact GoMore `acc`, `raw_hr`,
`hr`, and `hrv` topic callbacks, 25/4-sample bounds, axis transform, readiness barrier, and
successful-update cleanup now compile as transparent C. A dormant `"gomore"` batch listener can
stage the existing `"acc"` stream on target, but startup does not register it and no health engine
or biometric publisher is activated. The exact product-side `raw_hr`/`adt` bounded accumulators
and two-byte Goodix living-object update also compile from their callback-table extents without
assigning waveform or physical-channel semantics. The source-built target now hash-gates the transparent Goodix demo/driver subset and
binds the recovered software-`i2c_4` optical pins, interrupt worker, reset/emitter lifecycle, and
YHM client bit 1. It does not start sampling at boot or expose a BLE control route, and its global
algorithm ABI remains fail-closed rather than fabricating health results.
The host build and tests remain the
portable reference implementation. Scheduling in the legacy Nordic device image comes from the
authenticated upstream FreeRTOS-Kernel 10.5.1 core, Nordic SDK 17.1.0's nRF52 Cortex-M port, and
Arm's authenticated CMSIS-FreeRTOS v10.5.1 wrapper; openR1 contributes only the recovered
configuration and R1 task/wake glue.
The Nordic image also compiles the authenticated MIT CmBacktrace 1.4.2-compatible core; openR1
contributes only the recovered configuration, static task-stack map, exception-entry glue, and a
bounded retained diagnostic sink.
Official Bosch BMA456 SensorAPI v2.29.0 and ST LIS2DW12 v2.1.0-compatible sources are pinned for
the two resolved accelerometer variants; openR1 may provide only R1-specific board/configuration
adapters around them. Both provider translation units and the clean-room selector/configuration/
FIFO adapters compile and remain retained in the Nordic target. Startup probes the recovered
TWIM1 P0.11/P0.14 address-`0x18` bus in LIS2DW12-then-BMA456W order. The owner-authorized
QMA6100/QMA6100P source reduction now supplies the third stock-order fallback without an opaque
provider; its Nordic board binding still requires installed-part confirmation. The P0.15 interrupt worker, downstream motion
consumer, NFC/TWIM1 coexistence, and owned-ring validation remain explicit gaps.
The authenticated ST25DVxxKC BSP component supplies the recovered NFC dynamic-tag driver. Its
translation units compile and remain linked through the Nordic target; openR1 supplies only the
R1 bus/resource port, session/configuration orchestration, identity boundary, and bounded 20-byte
mailbox policy. NFC starts disabled; Nordic startup binds the recovered P1.10 board-enable sequence
and a static CMSIS mutex for exclusive `i2c_5` ownership.
The AES-128 inverse core is supplied by pinned tiny-AES-c v1.0.0-compatible source; openR1 owns
only the recovered R1 two-pass reverse/forward chaining adapter and its safety checks.
The recovered `kv.bin` partition is R1-owned rather than FlashDB: openR1 implements its seven fixed
classes and four-snapshot layout with a documented power-loss-safe commit/rollover correction.
FlashDB remains the upstream provider for `health.db` only.
The Nordic target binds all seven partitions to the recovered 36-page nRF52840 internal-flash
region using Nordic `nrf_fstorage_sd` and upstream FAL 0.5.99. Its linker and FDS configuration
reserve the exact non-overlapping application/FDS/data/bootloader layout; no external NOR driver or
generic stock device-registry rewrite is used.
The Nordic target also links Nordic's unmodified `nrfx_saadc.c` and retains a clean R1 adapter for
the recovered battery AIN5/P0.29, PMIC-current AIN3/P0.05, and NFC-rectifier AIN2/P0.04 routes.
Portable code implements the byte-pinned five-sample conversion, battery curves, charging cadence,
full-state gate, and stalled-charge recovery. The complete YHM2710 transport/register closure is
now reconstructed as transparent C; battery acquisition remains unsupported until the Nordic
board binds it and owned-ring electrical behavior is validated. No raw ADC BLE surface exists.
Portable health code also implements the recovered R1-owned automatic synchronization gate: an
active phone-role link triggers HR, SpO2, HRV, activity, and unsynchronized-sleep history in exact
order at initial time, clock rewind, or a 10,800-second boundary. Explicit history queries share
and reset the same cooldown timestamp. The Nordic image retains the integration API, while the
periodic wall-clock producer remains pending. The Goodix and GoMore algorithm bodies and model
constants are transparent C; their remaining gap is typed live-runtime adoption on hardware.
The activity path additionally owns the recovered 144-record offline FIFO, including exact packed
records, time rejection, oldest overwrite, acknowledgement-prefix consumption, consecutive
day/offset packet merging, duplicate-bucket replacement, and hardened index/state checks.
Heart rate, SpO2, and HRV own separate recovered 24-record offline FIFOs. HR/SpO2 use exact
16-byte UInt8 aggregate records and HRV uses exact 20-byte UInt16 aggregate records; the portable
implementation preserves retained bytes, FIFO-prefix consumption, consecutive day/offset
grouping, repeated-hour replacement, and the HRV callback's distinct ACK clock policy.
The activity daily-cache adapter additionally resets days, writes bounded six-bucket hours, and
replays the recovered legacy-clock return/redaction path into the admitted offline queue.
The activity day builder merges caller-owned RAM cache data and typed records decoded by the
storage provider, preserves midnight/UTC-offset boundaries, and emits the established public
packet through a caller callback. Allocation, FlashDB decoding, calendar conversion, and EUS
transport remain external provider seams.
The health-database binding and startup controller preserve the recovered provider-object accessor,
six-schema size gate, exact
FlashDB control/init and time-listener order, retained-clock handoff, local-day recovery interval,
zeroed 128-byte iterator workspace, allocation-failure path, and one-shot crash restore. Pinned
FlashDB/RTOS code supplies attributable mechanisms. The Nordic image now wires the startup
controller to the platform clock, CMSIS mutex, and FreeRTOS heap at boot; see
[`docs/correlation/STORAGE-PRODUCTION-WIRING-CORRELATION.md`](docs/correlation/STORAGE-PRODUCTION-WIRING-CORRELATION.md). The event-bus time subscription and health record
decode consumers remain provider seams.
The shared TWI layer now preserves fifteen byte-pinned R1 register-transfer, synchronization, and
lifecycle adapters: two primary and two secondary register operations, two shutdown paths, distinct
primary and secondary initializers, four software-bus pin-release paths, the completion callback, and two wait paths. Local code owns only framing,
the 80-byte write bound, status mapping, recovered timeout policy, GPIO/bus configuration, and
shutdown power-cycle policy; Nordic GPIO/TWI/TWIM/delay/fatal handling and authenticated
CMSIS-FreeRTOS kernel/tick/semaphore operations remain their upstream implementations.
The software-bus close paths call Nordic `nrf_gpio_cfg_default`. Their bit-level open/read/write
engines are reconstructed transparent C; the Zephyr target binds exact software `i2c_4` to
the Goodix optical provider and exact software `i2c_2` to the fail-closed dual-GXT310
temperature adapter. The dormant `i2c_3` and shared-rail `i2c_5` software roles remain without
live consumers because their active target paths use separately typed Nordic/YHM providers.

```sh
make -C r1 test
make -C r1 sanitize
make -C r1 arm-objects
make -C r1 sim
make -C r1 zephyr-source-verify
```

For example, `r1/build/openr1_sim 01 get` prints a synthetic `deviceStatus` response as an EUS
BLE value. Mutating requests require the final `authorized` argument.

The source-built full-flash bundle is reproduced with a Zephyr 3.7.2 west
workspace and GNU Arm Embedded 9.3.1 toolchain:

```sh
make -C r1 zephyr-bundle \
  WEST=/absolute/zephyr-venv/bin/west \
  ZEPHYR_WORKSPACE=/absolute/zephyr-workspace \
  ZEPHYR_TOOLCHAIN=/absolute/gcc-arm-none-eabi-9-2020-q2-update \
  BMA456_ROOT=/absolute/BMA456_SensorAPI-3266db2c \
  LIS2DW12_ROOT=/absolute/lis2dw12-pid-8d4bd52 \
  ST25DVXXKC_ROOT=/absolute/fp-sns-stbox1/Drivers/BSP/Components/st25dvxxkc \
  FLASHDB_ROOT=/absolute/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  GOODIX_DEMOCODE_ROOT=/absolute/pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321/gh3x2x
make -C r1 zephyr-verify
```

The default transparent MCUboot development key is not a deployment key. Set
`ZEPHYR_SIGNING_KEY=/secure/owner-mcuboot-ec-p256.pem` for an owner-controlled
trust anchor. The full closure and exact preserved flash ranges are documented
in [`docs/closures/SOURCE-BUILT-ZEPHYR-BUNDLE.md`](docs/closures/SOURCE-BUILT-ZEPHYR-BUNDLE.md).

See [`docs/README.md`](docs/README.md) for evidence
provenance, coverage, safety differences, and remaining hardware work. The function-level motion
split is in
[`docs/MOTION-PROVIDER-CORRELATION.md`](docs/correlation/MOTION-PROVIDER-CORRELATION.md).
All 362 GoMore functions—including 343 primitives/shared-runtime graph, persistence, activity,
locomotion-crossing, optical-period, respiratory, sleep, and output-orchestration routines plus
nineteen tensor-runtime routines—are reconstructed in transparent C. See
[`docs/GOMORE-PROVIDER-BOUNDARY.md`](docs/boundaries/GOMORE-PROVIDER-BOUNDARY.md).
The three byte-pinned R1 GoMore adapters are transparent too: exact accelerometer/raw-optical topic
input plus the backward-clock reset dispatcher. The latter is source-bound on Zephyr to an explicit
suppressed action until live engine state and result composition are hardware-validated.
The IQS7211E path uses pinned MIT provider/settings references and the R1-only adapter in
`src/r1_iqs7211e.c`; its Nordic TWIM0/GPIOTE board binding is recorded in
[`docs/IQS7211E-PROVIDER-BOUNDARY.md`](docs/boundaries/IQS7211E-PROVIDER-BOUNDARY.md)
and remains unavailable until identity and wear/factory lease gates are provisioned; Zephyr now
binds its shared-power client to the reconstructed YHM2710 service.
The GXCAS GXT310 and YHMICROS YHM2710 provenance boundaries are documented in
[`docs/NAMED-PERIPHERAL-BOUNDARIES.md`](docs/boundaries/NAMED-PERIPHERAL-BOUNDARIES.md).
The five GXT310 mode/one-shot bodies are transparent C. The source-built Zephyr target now probes
both exact addresses over P1.13/P0.28, decodes signed big-endian register-0 values, and exposes the
recovered immediate and ten-sample acquisition paths. The latter reads the exact six-byte
calibration at `nv_r1` offset `0x3E`, treats an erased record as absent, and applies only recovered
subtract/add direction values. It does not assign skin/ambient semantics or feed the daily cache. See
[`docs/GXT310-REDUCTION-CORRELATION.md`](docs/correlation/GXT310-REDUCTION-CORRELATION.md).
All 36 YHM2710 transport, device, register, status, and policy bodies are likewise reconstructed;
see [`docs/YHM2710-REDUCTION-CORRELATION.md`](docs/correlation/YHM2710-REDUCTION-CORRELATION.md).
The R1-owned three-client power lease and shared NFC/YHM conductor arbitration are implemented
separately in `src/r1_power_lease.c`, the Nordic resource adapter, and the Zephyr YHM/dock adapters; see
[`docs/YHM2710-I2C5-RESOURCE-BOUNDARY.md`](docs/boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md).
The portable lease calls only a semantic provider and contains no YHM register/framing data. On
Zephyr it is bound to reconstructed P1.01 transport and exact `0xA8`/`0x28` boundary actions;
optical lifecycle now adopts client bit 1 on demand, while touch remains identity/wear gated. NFC
receives the recovered P1.10 lifecycle and an exclusive
session mutex but still starts disabled and exposes no raw transfer surface.
All 339 Goodix mappings now compile from transparent C with hidden table and executor
addresses replaced by typed bindings; 320 came from the opaque closure, seventeen replace
public-democode source, and two replace R1 product entries. No Goodix function remains opaque; see
[`docs/GOODIX-PROVIDER-BOUNDARY.md`](docs/boundaries/GOODIX-PROVIDER-BOUNDARY.md).
The complete twelve-function `goodix_mem`/`GdMem` core is reconstructed without the vendor binary;
all twenty Goodix heap call-site helpers, the R1 pool byte-fill, and the first four descriptor
lifecycle bodies are also compiled locally. The paired channel/session constructor-destructor
layer is compiled locally as well. Four Goodix generated-model descriptor helpers now build their
records from typed parameters and bind reconstructed pooling/add executors directly. The adjacent
recurrent-layer constructor now allocates its state transparently and partitions the model arena
with checked arithmetic. Its full quantized recurrent executor and five-helper closure are now
local, including checked caller-supplied model-region/workspace APIs and a target-ABI adapter;
the first complete generated-model graph builder emits a typed
352-byte schema from an explicit 439-word model input. Its enclosing `0x344`-byte model instance
is now typed, failure-clean, and built from an explicit 3,924-word model input; its recovered
owner configuration wrapper is local as well. Its complete three-mode `0x742E4` executor retains
the recovered 99→49→24→12 graph, scratch banks, head/tail branches, and final copy while replacing
the stock callback table with explicit typed stage plans. The complete `0x617F8` sibling likewise
retains its four 180-sample branches, five quantized layers, overlapping arena move, and concatenated
960-byte output through explicit plans and caller-owned scratch. The enclosing `0xD4` preprocessing session now has
a failure-clean 34-allocation constructor/destructor pair. The full SpO2 version report and its
DSP component string are also built locally from explicit text inputs;
see [`docs/GOODIX-HEAP-REDUCTION-CORRELATION.md`](docs/correlation/GOODIX-HEAP-REDUCTION-CORRELATION.md).
Twenty-three callback/helper entries that Ghidra omitted from its function CSV are independently
byte-pinned and routed to the existing transparent PMIC, connection, temperature, touch-power,
motion, GoMore topic, tensor-runtime, LIS2DW12, and FlashDB source seams; see
[`docs/THUMB-CALLBACK-ENTRY-CORRELATION.md`](docs/correlation/THUMB-CALLBACK-ENTRY-CORRELATION.md).
`src/r1_goodix.c` implements only the recovered R1 power/lifecycle/profile adapter. It requires an
explicit provider binding and returns `R1_ERROR_UNSUPPORTED` instead of fabricating biometric data
when that provider is absent.
The ST25DVxxKC provider/adapter split and source hashes are in
[`docs/ST25DVXXKC-CORRELATION.md`](docs/correlation/ST25DVXXKC-CORRELATION.md).
The storage format and intentional audit corrections are in
[`docs/KV-STORE-CORRELATION.md`](docs/correlation/KV-STORE-CORRELATION.md).
The physical storage provider and exact UICR/FDS layout are in
[`docs/INTERNAL-FLASH-CORRELATION.md`](docs/correlation/INTERNAL-FLASH-CORRELATION.md).
The Nordic/R1 analog split, exact routes, byte hashes, and battery behavior are in
[`docs/ANALOG-BATTERY-CORRELATION.md`](docs/correlation/ANALOG-BATTERY-CORRELATION.md).
The recovered health scheduler evidence and provider separation are in
[`docs/AUTOMATIC-HEALTH-SYNC-CORRELATION.md`](docs/correlation/AUTOMATIC-HEALTH-SYNC-CORRELATION.md).
The activity offline queue and acknowledgement boundary are in
[`docs/ACTIVITY-OFFLINE-SYNC-CORRELATION.md`](docs/correlation/ACTIVITY-OFFLINE-SYNC-CORRELATION.md).
The scalar-health offline queues and acknowledgement boundary are in
[`docs/SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md`](docs/correlation/SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md).
The bounded HR/SpO2/HRV daily-cache callbacks and invalid-clock routing are in
[`docs/SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md`](docs/correlation/SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md).
The provider-separated HR/SpO2/HRV sample consumers, latest-point rules, and hourly storage
aggregation are in
[`docs/SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md`](docs/correlation/SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md).
The exact health registration lookup and bounded internal history-record routing are in
[`docs/HEALTH-HISTORY-ROUTING-CORRELATION.md`](docs/correlation/HEALTH-HISTORY-ROUTING-CORRELATION.md).
The product/provider split for the health TSDB startup controller is in
[`docs/HEALTH-DATABASE-STARTUP-CORRELATION.md`](docs/correlation/HEALTH-DATABASE-STARTUP-CORRELATION.md).
The pure material-time/local-hour planners and exact known-cursor reconciliation are in
[`docs/TIME-HEALTH-ROLLOVER-CORRELATION.md`](docs/correlation/TIME-HEALTH-ROLLOVER-CORRELATION.md).
The provider-separated temperature/stress storage aggregation and daily-cache callbacks are in
[`docs/TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md`](docs/correlation/TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md).
The activity daily-cache callback boundary is in
[`docs/ACTIVITY-DAILY-CACHE-CORRELATION.md`](docs/correlation/ACTIVITY-DAILY-CACHE-CORRELATION.md).
The activity RAM/decoded-flash merge and packet-flush boundary is in
[`docs/ACTIVITY-DAY-MERGE-CORRELATION.md`](docs/correlation/ACTIVITY-DAY-MERGE-CORRELATION.md).
The private event-bus publisher, subscriber table, and multicast contract are in
[`docs/EVENT-BUS-CORRELATION.md`](docs/correlation/EVENT-BUS-CORRELATION.md).
