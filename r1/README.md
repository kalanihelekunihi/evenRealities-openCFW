# openR1

`openR1` is a clean-room, portable C implementation of the observable Even Realities R1
firmware contract. It is derived from the repository's recovered protocol, behavioral, memory,
and security-audit evidence; it is not reconstructed vendor source and is not byte-identical to
the stock image.

The first milestone implements the normal EUS transport, both direction-specific inner checksum
schemes, bounded reassembly, safe system-command dispatch, device state, the recovered flash
partition map, and the two recovered notification queues. Hardware access is behind a platform
interface. The vendor-backed target additionally links Nordic S140 integration, BAE8 service,
Peer Manager/FDS bond storage, `nrf_ble_gatt`, and Nordic advertising sources. The host build and
tests remain the portable reference implementation. Scheduling in the device image comes from the
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
TWIM1 P0.11/P0.14 address-`0x18` bus in LIS2DW12-then-BMA456W order; QST QMA6100 remains disabled
until official licensed source is authenticated. The P0.15 interrupt worker, downstream motion
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
full-state gate, and stalled-charge recovery. Battery acquisition returns unsupported until a
licensed YHM power provider binds the semantic power interface; no YHM wire/register body or raw
ADC BLE surface is implemented.
Portable health code also implements the recovered R1-owned automatic synchronization gate: an
active phone-role link triggers HR, SpO2, HRV, activity, and unsynchronized-sleep history in exact
order at initial time, clock rewind, or a 10,800-second boundary. Explicit history queries share
and reset the same cooldown timestamp. The Nordic image retains the integration API, while the
periodic wall-clock producer remains pending and all GoMore/Goodix algorithms stay provider-gated.
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
The software-bus close paths call Nordic `nrf_gpio_cfg_default`; their bit-level open/read/write
engines remain source-gated and are not recreated locally.

```sh
make -C r1 test
make -C r1 sanitize
make -C r1 arm-objects
make -C r1 sim
```

For example, `r1/build/openr1_sim 01 get` prints a synthetic `deviceStatus` response as an EUS
BLE value. Mutating requests require the final `authorized` argument.

See [`docs/README.md`](docs/README.md) for evidence
provenance, coverage, safety differences, and remaining hardware work. The function-level motion
split is in
[`docs/MOTION-PROVIDER-CORRELATION.md`](docs/correlation/MOTION-PROVIDER-CORRELATION.md).
The GoMore health/sleep algorithm boundary remains disabled until a matching licensed provider is
authenticated; see
[`docs/GOMORE-PROVIDER-BOUNDARY.md`](docs/boundaries/GOMORE-PROVIDER-BOUNDARY.md).
The IQS7211E path uses pinned MIT provider/settings references and the R1-only adapter in
`src/r1_iqs7211e.c`; its Nordic TWIM0/GPIOTE board binding is recorded in
[`docs/IQS7211E-PROVIDER-BOUNDARY.md`](docs/boundaries/IQS7211E-PROVIDER-BOUNDARY.md)
and remains unavailable until identity, shared-power, and wear/factory lease gates are provisioned.
The GXCAS GXT310 and YHMICROS YHM2710 boundaries are documented in
[`docs/NAMED-PERIPHERAL-BOUNDARIES.md`](docs/boundaries/NAMED-PERIPHERAL-BOUNDARIES.md).
The R1-owned three-client power lease and shared NFC/YHM conductor arbitration are implemented
separately in `src/r1_power_lease.c` and `platform/nrf52840/sdk/openr1_i2c5_resources.c`; see
[`docs/YHM2710-I2C5-RESOURCE-BOUNDARY.md`](docs/boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md).
The lease calls only a semantic provider and contains no YHM register/framing data. Without a
licensed YHM provider, touch power remains fail closed. NFC receives the recovered P1.10 lifecycle
and an exclusive CMSIS mutex but still starts disabled and exposes no raw transfer surface.
The Goodix GH3X2X demo/config/event boundary remains licensed-provider-only; see
[`docs/GOODIX-PROVIDER-BOUNDARY.md`](docs/boundaries/GOODIX-PROVIDER-BOUNDARY.md).
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
