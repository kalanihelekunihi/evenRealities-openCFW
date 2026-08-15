# Motion-sensor provider correlation

This note applies the source-admission rule to the three accelerometer paths recovered from the R1
application. Production firmware must compile an authenticated official driver where one is
available. Local source is limited to R1 configuration, bus callbacks, buffer bounds, logging,
identity selection, and normalized event glue.

## Bosch BMA456W

The official provider is Bosch's BMA456 SensorAPI v2.29.0,
[published here](https://github.com/boschsensortec/BMA456_SensorAPI) and pinned to commit
`3266db2c5de15be1a00232b8c0f2fd23e07934e0` under BSD-3-Clause. The archive and the retained
`bma4.c`/`bma456w.c` files are independently hash-checked by `third-party/fetched/verify_vendor.py`.

The revision discriminator is executable, not merely a version string. Recovered
`null_pointer_check` at `0x0007B61C` checks `bma4_dev`, `bus_read` at offset `0x24`, `bus_write` at
`0x28`, and `delay_us` at `0x2C`. Bosch v2.24.1 checked `intf_ptr` in the fourth condition. The only
functional `bma4.c` change from v2.24.1 to v2.29.0 replaces that check with `delay_us`, exactly as
the R1 image does. The surrounding device layout, error values, register addresses, delay values,
feature-transfer loops, and BMA456W initialization also match v2.29.0.

Provider-routed recovered entries are:

| Address | Official Bosch symbol |
| --- | --- |
| `0x000543C4` | `bma456w_init` |
| `0x00054408` | `bma4_get_advance_power_save` |
| `0x00054440` | `bma4_get_fifo_length` |
| `0x0005447E` | `bma4_init` |
| `0x00054534` | `bma4_read_regs` |
| `0x000545CA` | `bma4_set_accel_config` |
| `0x00054640` | `bma4_set_accel_enable` |
| `0x0005468E` | `bma4_set_advance_power_save` |
| `0x000546D0` | `bma4_set_fifo_config` |
| `0x0005475A` | `bma4_write_regs` |
| `0x00070FDA` | `increment_feature_config_addr` |
| `0x0007B61C` | `null_pointer_check` |
| `0x00087BBC` | `read_regs` |
| `0x00087E58` | `read_within_len_regs` |
| `0x0008EDD8` | `set_feature_config_start_addr` |
| `0x00096820` | `validate_odr_bandwidth_perfmode` |
| `0x0009756A` | `write_regs` |
| `0x000976B8` | `write_within_len_regs` |

The R1-only boundary begins with the byte-pinned delay, I2C-read, I2C-write, and `bma4_dev`
configuration ports at `0x00053AA4`, `0x00053AB4`, `0x00053AD0`, and `0x00053AEC`. It also
includes `0x00053B2C` identity probing, `0x00053C6C` fixed product configuration, `0x000541A8`
FIFO acquisition/event handling, and `0x000544C8` the product's bounded FIFO transfer. Those
adapters must call the Bosch API; they are not permission to reproduce Bosch internals.

## ST LIS2DW12 (R1 diagnostic name “LIS2DOC”)

The recovered strings say `LIS2DOC`, but the executable path reads WHO_AM_I register `0x0F` and
requires value `0x44` (`'D'`). Its register addresses, bitfields, FIFO, power, filter, interrupt,
and tap operations match ST's LIS2DW12, not a distinct LIS2DOC provider. The official provider is
ST's [lis2dw12-pid](https://github.com/STMicroelectronics/lis2dw12-pid) standard C driver under
BSD-3-Clause.

The exact original checkout is not uniquely provable, so the manifest does not claim one:

- the recovered `stmdev_ctx_t` invokes read/write callbacks at offsets `4`/`0` and passes `handle`
  at `0x0C`; the intervening `mdelay` slot requires commit
  `18b0866fb6907dd5f4f52b79da36b3be88af719d` or later;
- `lis2dw12_pin_int1_route_set` at `0x000756DA` performs the second read only if the first succeeds,
  matching the guarded pre-v2.2 body and excluding commit
  `24580d635896d81ed2abad30c4309f8e1c65b152` and later;
- `lis2dw12_reset_set` at `0x000757EC` accepts and writes a caller-provided bit, excluding the
  parameterless v2.3+ API; and
- v2.0.1 and v2.1.0 retained function bodies are equivalent for this recovered subset. v2.1.0
  commit `8d4bd522015004a9646102702901ba5a15ec6d39` is selected as the newest compatible official
  release, not asserted as the stock vendor checkout.

Provider-routed entries are:

| Address range/list | Official ST symbols |
| --- | --- |
| `0x000750B8`, `0x00075120`, `0x0007517C` | `lis2dw12_block_data_update_set`, `lis2dw12_data_rate_set`, `lis2dw12_device_id_get` |
| `0x000753AC`–`0x000754AC` | FIFO level/mode/watermark, full-scale, filter-path, and filter-bandwidth setters/getters selected in the image |
| `0x000756CC`, `0x000756DA` | `lis2dw12_pin_int1_route_get`, `lis2dw12_pin_int1_route_set` |
| `0x0007575A` | `lis2dw12_power_mode_set` |
| `0x000757C4`, `0x000759E6` | `lis2dw12_read_reg`, `lis2dw12_write_reg` |
| `0x000757D2`, `0x000757EC` | `lis2dw12_reset_get`, `lis2dw12_reset_set` |
| `0x0007581A`–`0x000759B8` | tap-axis enables, duration, mode, quiet, shock, and X/Y/Z threshold setters |

The R1-only boundary is `0x000750A0` burst acquisition, `0x000750E8` bounded FIFO read,
`0x0007518A` product register-`0x17` setup, `0x000751B8` double-tap disable policy,
`0x000754DC` identity probe, and `0x00075510` fixed product configuration/reset loop. These six
functions may be independently implemented only as adapters around the pinned ST driver.

An earlier ledger revision incorrectly included `0x000759F4` as a seventh LIS identity helper.
Direct-call inspection shows that it invokes the integrity helper at `0x0005A5EC` from the
Goodix-adjacent heart-rate core at `0x0006D51C`, beside the recovered `GH_HR` version markers. All
three bodies are now byte-pinned as `goodix_gh3x2x_candidate` and remain licensed-provider-only.

## R1 common selector and normalization adapters

Twenty-three recovered functions belong to product motion policy rather than either driver. Thirteen
were absent from Ghidra's function inventory but have unambiguous call-table, return/tail-call, and
next-function boundaries; the ownership ledger records their exact extents as byte-pinned manual
supplements.

| Address | Clean-room role |
| --- | --- |
| `0x00050208` | probe and select LIS2DW12, then BMA456W, then the QMA6100 fallback |
| `0x0005025C` | refresh the selected-provider state |
| `0x00050270` | initialize/configure the selected provider |
| `0x00050128`–`0x000501C8` | interrupt/bus lookup, acquire/release, and bounded read/write request glue |
| `0x00050294` | dispatch the selected provider's interrupt hook; this is a no-op for LIS2DW12 and BMA456W |
| `0x000502AC` | call the selected provider's bounded FIFO reader |
| `0x0006F1A8`, `0x0006F1BC`, `0x0006F1DA` | BMA456W probe/configure wrappers and two-byte interrupt no-op |
| `0x0006F1DC` | convert BMA456W six-byte FIFO samples to three signed axes |
| `0x0006F228`, `0x0006F304` | product orientation accumulator and motion-sample event adapter |
| `0x0006F380`, `0x0006F394`, `0x0006F3B2` | LIS2DW12 probe/configure wrappers and two-byte interrupt no-op |
| `0x0006F3B4` | convert LIS2DW12 six-byte FIFO samples to three signed axes |
| `0x0006F400` | product motion initialization entry |
| `0x0006F4A0` | produce a 188-byte batch containing at most 30 samples, count, padding, and timestamp |

Both normalization wrappers decode little-endian signed 16-bit X/Y/Z values and apply a Cortex-M
arithmetic right shift by two to each axis. `src/r1_motion.c` implements that behavior without
depending on implementation-defined signed shifts, limits every read to 31 six-byte samples, and
rejects provider over-reporting. Its policy can disable motion, auto-select all three providers in
stock order, or force any one variant. QMA6100 is supplied by the owner-authorized reduction in
[`QMA6100-REDUCTION-CORRELATION.md`](QMA6100-REDUCTION-CORRELATION.md), not by the unlicensed
correlation snapshot.

The recovered board mapping is now concrete: Nordic TWIM1 at 400 kHz, SCL P0.11, SDA P0.14,
seven-bit address `0x18`, and rising interrupt input P0.15 with no pull. The clean Nordic port is
`platform/nrf52840/sdk/openr1_motion.c`; startup binds both official providers and selects the
installed admitted part. A GPIOTE IN event on P0.15 (rising edge, no pull) defers each interrupt
to a motion worker thread whose dispatch mirrors `r1_motion_selected_interrupt_dispatch`
(`0x00050294`): it routes to the selected variant's hook, and both admitted hooks are the
recovered two-byte no-ops. A retained `.openr1_motion_api` table keeps FIFO read, double-tap disable,
variant, and enabled-state entry points in the linked image.

The fixed product configurations are also recovered rather than guessed:

- BMA456W maps 25/50/100/200 Hz to ODR values 6/7/8/9, uses 8 g range, bandwidth/performance zero,
  initializes and enables acceleration, clears all FIFO selection bits, enables headerless
  acceleration FIFO, and brackets FIFO access with advanced-power-save disable/enable. FIFO
  length is bounded before reading register `0x26`; the stock 450-microsecond settle interval is
  preserved.
- LIS2DW12 maps 25/50/100/200 Hz to ODR values 3/4/5/6, with 150 Hz also selecting 200 Hz. It
  resets and polls at two-millisecond intervals, enables register-address auto increment and BDU,
  selects ODR/10 bandwidth, filter path zero, 4 g range, watermark 31, stream FIFO mode, and
  low-power mode 3. After the 100-millisecond settle interval it discards at most five initial
  samples. The double-tap-disable adapter clears INT1 tap routing and X/Y/Z tap enables and restores
  the recovered single-tap/filter/rate policy through ST APIs.

## QST QMA6100

The QMA6100 operation table and diagnostics establish a QST provider boundary. A public evaluation
snapshot contains `qma6100.cpp` identifying `Yangzhiqiang@qst`, version V1.0, and date 2020-05-27.
Its retry loops, two-address identity search, register sequence, FIFO limit, range scaling, and
interrupt/configuration structure establish QST V1.0 lineage for the recovered cluster. The
correlation pins commit `3903bd7d...` and the source/header hashes in the vendor manifest.

The available snapshot is not an official QST distribution channel, has no license, and is
correlation evidence only. Three provider bodies were formerly gated as
`vendor_source_required_not_redistributable`; owner authorization now routes them to independently
compiled reconstructed C:

| Address | Provider role |
| --- | --- |
| `0x00086E34` | `qma6100_chip_id` |
| `0x00087188` | `qma6100_set_range` |
| `0x000871C4` | `qma6100_soft_reset` lineage |

Four call-table wrappers at `0x0006F404`, `0x0006F418`, `0x0006F436`, and `0x0006F448` cover
QMA6100 probe, configuration, interrupt, and FIFO normalization. Ten additional functions retain
the QST skeleton but add R1 configuration or integration seams:

| Address | R1 adapter boundary |
| --- | --- |
| `0x00086D40` | any-motion configuration and chip-specific thresholds |
| `0x00086E48` | delay callback port |
| `0x00086E68` | identity acceptance and orientation layout |
| `0x00086EE4` | ODR/range/FIFO/tap initialization policy |
| `0x00086FA8` | interrupt-to-product-event callbacks |
| `0x00086FF4` | bounded FIFO read, R1 logging, and count return |
| `0x0008714C` | five-retry R1 I2C read transport |
| `0x00087250` | step-counter configuration |
| `0x000872E4` | tap configuration and thresholds |
| `0x000873F4` | five-retry R1 I2C write transport |

Those seams and the three provider interiors now share the complete 17-entry source reduction in
`reconstructed/qma6100/`. The ledger disposition is
`clean_room_reimplementation_owner_authorized`; the code is not QST source, and the public
unlicensed snapshot is not a build dependency. Nordic board adoption remains disabled until an
installed QMA part is confirmed, but source availability is no longer the gate.

## Build consequence

`r1/tools/fetch_vendor.sh` fetches and verifies the Bosch v2.29.0 and selected ST v2.1.0
archives beside Nordic SDK and FlashDB. The Nordic image now compiles and retains both official
provider paths plus the R1 selector, configuration, bus, and FIFO adapters. Host tests prove probe
priority, forced selection, error behavior, FIFO bounds, over-report rejection, and negative-axis
normalization.

Coverage remains partial: the P0.15 interrupt-to-worker path is now wired — a GPIOTE IN event on
the recovered rising-edge input defers to a motion worker thread, and its dispatch routes to the
selected variant's hook, which is a recovered two-byte no-op for both admitted variants
(LIS2DW12 `0x0006F3B2`, BMA456W `0x0006F1DA`), so the wired path intentionally performs no
per-interrupt work — but no higher-level motion/step/sleep consumer is wired yet (that ingestion
goes through the blocked sensor-stream framework), and the implementation has not been tested on
an owned R1 ring. TWIM1 contention between motion and NFC is resolved: the R1-owned arbiter
`platform/nrf52840/sdk/openr1_twim1_arbiter.c` serializes the substituted hardware instance
between the worn motion client and the dock NFC client with a documented dock-preempts-worn
handoff. NFC remains disabled at startup for separate reasons — the identity, shared-power, and
dock gates — not because of bus ownership. QMA6100 remains unselected in Nordic startup until an
installed QMA part is confirmed and the reconstructed fallback is tested on owned hardware.
