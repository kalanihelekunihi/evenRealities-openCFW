# Vendor-source admission policy

The production reconstruction uses an identifiable vendor or upstream implementation whenever the
recovered firmware can be attributed to one. Decompilation is used to select the version,
configuration, call boundary, and R1-specific behavior; it is not used to rewrite third-party
library internals. Clean-room source is limited to R1 application logic, board configuration,
ports, adapters, safety corrections, and functionality for which no vendor source can be
identified or lawfully obtained.

The machine-readable inventory is
`../third-party/fetched/manifest.json`. Each entry has one of
these dispositions:

- `pinned_upstream`, `pinned_upstream_bundled`, `pinned_upstream_snapshot`,
  `pinned_upstream_snapshot_adapter_required`, `pinned_upstream_license_review`, or
  `pinned_upstream_adapter_required`, `pinned_upstream_compatible_adapter_required`, or
  `pinned_vendor_binary`: selected input,
  hash/version checked; the license-review variant cannot ship until its inconsistent notices are
  resolved;
- `vendor_source_required_not_redistributable`: integrate a lawfully obtained matching vendor SDK,
  and do not substitute a clean-room implementation of the proprietary algorithm;
- `clean_room_configuration_only_use_pinned_provider`: write only the recovered product
  configuration/adapter while linking the identifiable provider implementation;
- `clean_room_adapter_only_use_nordic_sdk_and_cmsis`: write only byte-pinned R1 state/status and
  timeout policy while linking Nordic TWI/delay and authenticated CMSIS-FreeRTOS kernel/tick/
  semaphore implementations;
- `version_correlation_required`, `installed_variant_and_version_required`, or
  `official_source_required_before_implementation`: keep the boundary
  stubbed until the exact upstream source can be selected;
- `clean_room_allowed`: evidence establishes R1-specific code or no attributable provider; and
- `clean_room_reimplementation_owner_authorized`: see the next section.

Component-level admission is refined by the one-row-per-entry
[`FUNCTION-OWNERSHIP.csv`](reference/FUNCTION-OWNERSHIP.csv). Its generator covers the 2,972 Ghidra function
records plus audit-confirmed executable entries that Ghidra omitted. Unclassified and
vendor-candidate entries remain implementation gates; lack of a symbol is never treated as proof
that code is eligible for rewriting.

## Admitted providers

| Provider | Evidence-selected input | Production ownership |
| --- | --- | --- |
| Nordic | nRF5 SDK 17.1.0 (`ddde560`) and S140 7.2.0 | CMSIS/nrfx including SAADC, TWIM0/TWIM1, SPIM2, SoftDevice integration, BLE stack/services, Peer Manager, clocks, timers, and platform utilities |
| SEGGER | RTT 6.18a and 6.14d-derived printf formatter bundled in Nordic SDK 17.1.0 | RTT debug transport and formatter engine; R1 may only supply its bounded clock-prefix hook |
| FreeRTOS | Kernel 10.0.0 bundled unmodified in Nordic's pinned SDK | scheduler, queues, semaphores, task notifications, timers, `heap_4`, and Nordic Cortex-M4F RTOS port |
| Arm | CMSIS-FreeRTOS v10.5.1 commit `d213f261...` with CMSIS 5.9.0 headers | CMSIS-RTOS2 adapter over FreeRTOS; authenticated repository snapshot, source hash checked |
| Armink | FlashDB 2.0.0 commit `4e567740...` | `health.db` TSDB implementation only; not `kv.bin` |
| Armink | authenticated CmBacktrace 1.4.2-compatible commit `73714489...` | unwind, stack scan, register capture, and fault diagnosis; R1 supplies only configuration and ports |
| Armink/RT-Thread ecosystem | FAL 0.5.99 nested in the FlashDB tag | Apache-2.0 flash-device and partition framework |
| Goodix | `gh3x2x-v2.23_7ecd2a` | optical sensor/algorithm implementation; public democode driver layer is pinned upstream, algorithm interiors under owner-authorized reduction (see above) |
| GoMore | exact embedded health-algorithm SDK/version unresolved | no public or licensed source route; under owner-authorized reduction (see above) |
| Flipper FZCO / Azoteq | Flipper One IQS7211E driver commit `0a88e26b...` under its MIT REUSE map; Azoteq-authored settings header at `436d3c42...` with an in-file MIT grant | admitted compatible provider/settings references; only R1 values, nRF5 transport/board port, communication glue, and recovery policy are local; exact stock checkout is not claimed |
| GXCAS | GXT310 part and public datasheet identified; official catalog now lists a 2025 STM32 driver V1.0 archive, but its bytes/license and relationship to the older R1 image remain unauthenticated | owner-authorized five-entry reduction landed in `reconstructed/gxt310/`; the official archive remains documentation evidence only |
| YHMICROS | YHM2710 part family identified; exact R1 driver source/version/license unresolved | under owner-authorized reduction (see above); the R1 three-client ownership policy keeps its semantic-provider seam |
| Bosch Sensortec | BMA456 SensorAPI v2.29.0 commit `3266db2c...` | BMA456W register, configuration-stream, FIFO, and feature driver; R1 adapters only outside it |
| STMicroelectronics | LIS2DW12 v2.1.0 commit `8d4bd522...`, selected as newest release in the proven compatible interval | LIS2DW12 register/FIFO/tap driver; `LIS2DOC` is the R1 diagnostic label |
| STMicroelectronics | ST25DVxxKC component from fp-sns-stbox1 commit `e9a35449...`, authenticated compatible BSD-3-Clause snapshot | NFC dynamic-tag register, security-session, GPO, energy-harvesting, and FTM mailbox driver; seven R1 board/policy adapters remain local |
| kokke / tiny-AES-c contributors | tiny-AES-c v1.0.0 commit `e72b6eff...`, selected compatible snapshot | AES-128 block implementation; local code owns only the recovered R1 two-pass chaining adapter |
| QST | QMA6100 V1.0 lineage proven from unlicensed correlation evidence; exact checkout unresolved | owner-authorized complete 17-entry provider/adapter reduction landed in `reconstructed/qma6100/`; no QST source is linked |

The SDK archive is not copied into the repository. Nordic's own license inventory must remain with
it. The authenticated Arm wrapper/header and Armink CmBacktrace snapshots are shared with the
existing openCFW research at `g2/third_party`; openR1 verifies their commits, exact source
hashes, and offline snapshot proofs before use.
`../third-party/fetched/fetch.sh` downloads the other pinned
archives into an explicit external/cache directory and rejects hash mismatches. The audit command
checks the source markers and exact S140 artifact:

```sh
openR1/tools/fetch_vendor.sh /absolute/cache/openr1-vendor
python3 openR1/vendor/verify_vendor.py \
  --sdk-root /absolute/cache/openr1-vendor/nRF5_SDK_17.1.0_ddde560 \
  --flashdb-root /absolute/cache/openr1-vendor/FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a \
  --bma456-root /absolute/cache/openr1-vendor/BMA456_SensorAPI-3266db2c5de15be1a00232b8c0f2fd23e07934e0 \
  --lis2dw12-root /absolute/cache/openr1-vendor/lis2dw12-pid-8d4bd522015004a9646102702901ba5a15ec6d39 \
  --st25dvxxkc-root /absolute/cache/openr1-vendor/fp-sns-stbox1-e9a35449b777699b5e1dd0f1466de0ead554893a/Drivers/BSP/Components/st25dvxxkc \
  --tiny-aes-root /absolute/cache/openr1-vendor/tiny-AES-c-e72b6eff0884673997d0ca6385169bbd9b31936d
```

## Owner-authorized full reduction (2026-08-14)

By explicit decision of the project owner, the reconstruction goal is a firmware image built
entirely from compilable source, including the third-party interiors that earlier revisions of
this policy kept hard-gated. The following named families are therefore re-routed from
`vendor_source_required_not_redistributable` / `investigate_before_implementing` to the new
disposition `clean_room_reimplementation_owner_authorized` as their reductions land:

- the six Bravechip BCL603M middleware families (generic device registry, software-TWI engines,
  sensor-stream framework, RTC-device framework, time/calendar provider, shared quantized neural
  runtime — 164 entries),
- the gated Goodix GH3X2X entries (319: closed algorithm-library closures, the `goodix_mem`
  apparatus, and the documented residue, including neural weight/constant tables),
- the GoMore health/sleep algorithm families (362),
- YHMICROS YHM2710 (36), GXCAS GXT310 (5), and QST QMA6100 (3).

Progress at this snapshot: 160 Goodix and 49 GoMore functions now compile from the reconstructed
Goodix primitive/heap and quantized-runtime modules and the two reconstructed GoMore modules. This moves 141
previously opaque Goodix entries and 49 opaque GoMore entries into the owner-authorized
disposition; 178 Goodix and 313 GoMore entries remain. Seventeen of the 160 Goodix functions
also replace already-admitted public-democode source, and two replace R1 product entries, so
those nineteen do not reduce the opaque count. The complete Goodix heap boundary now has local
C for its twelve allocator bodies, all twenty provider call-site helpers, and the R1 byte-fill.
The first four heap-dependent descriptor lifecycle bodies are local as well.
The six-descriptor channel state and enclosing two-channel session state now have paired,
failure-clean constructor/destructor implementations.
Twenty-four Goodix generated-model/runtime routines are also local: the owner wrapper, model instance initializer, both graph builders, generated layer-block builder, both complete generated graph executors, complete quantized layer executor, recurrent layer, complete recurrent executor and helper closure (including both exact range-adjust instantiations), four typed stage-pipeline helpers, aligned arena descriptor,
packed pooling descriptor, external executor accessor, and cursor-pair int8-add descriptor.
Their enclosing preprocessing session constructor/destructor is also local and releases all 34
owned allocations on complete teardown.
The GH_HR integrity-bit encoder and validator are local as well, with all four recovered parity
masks expressed as transparent constants and their selector/parity behavior covered by tests.
The paired packed-float converters and their explicit-callback vector adapter are also local,
including the recovered shared-tail extents and exact subnormal bit adjustments.

Method and limits:

- Implementations are written from the recovered decompilation evidence in `r1/research/` as
  independently compiled C, with per-function provenance (image, address, size, evidence hash)
  recorded in the ownership ledger and the family correlation docs. They are not vendor source
  and must never be presented as such; every reconstructed file carries a provenance banner.
- Constant and weight tables that exist only as data in the stock image are embedded as C arrays
  generated from the recovered bytes, with the extraction tool and source range documented; they
  are evidence-derived data, not authored content.
- Reconstructed providers live under `r1/reconstructed/<family>/`, separate from R1-owned product
  code (`r1/src/`), platform glue (`r1/platform/`), and R1-authored ports (`r1/port/`).
- Security invariants are preserved: pointer+length discipline, explicit failure, bounded queues,
  and the documented security non-goals (withheld dispatch commands, fail-closed authorization)
  remain excluded behavior, not opacity to be reduced.
- Reconstructed modules carry host tests where portable and are compiled into the SDK image as
  they land; fail-closed stubs are retired only when their replacement is built and tested.

This section supersedes the hard-gate language for the named families elsewhere in this document
and in `boundaries/` docs; those docs remain the provenance record of why upstream source was
unavailable or unusable.

## R1-owned boundaries

The compact EUS application protocol, authorization policy, product state, recovered health wire
formats, R1 flash ports/configuration, and `sleep.db` circular journal are R1-specific boundaries.
The recovered FreeRTOS configuration (`1024` Hz, 56 priorities, 256-word default stack) and the two
R1 task entry points are also product configuration/glue, not replacements for RTOS internals.
The recovered notification policy likewise remains R1-owned configuration: raw queue/credit/retry
timeouts are `100`/`200`/`1000` ticks, while the CMSIS-FreeRTOS provider owns tick acquisition,
thread-flag waits, queues, semaphores, and scheduling. The clean runtime does not relabel those raw
values as milliseconds; physical timing remains an owned-hardware validation gate.
The TWI register-transfer/completion/wait/lifecycle layer follows the same rule: fifteen R1 adapters
own framing/bounds, event/status mapping, the kernel-state semaphore gate, timeout conversion,
recovered polling policy, GPIO/bus configuration, and shutdown power-cycle policy, while Nordic
and CMSIS-FreeRTOS supply every GPIO/TWI/TWIM driver, delay, fatal-error, kernel, tick, and
semaphore implementation; see
[`TWI-SYNCHRONIZATION-CORRELATION.md`](correlation/TWI-SYNCHRONIZATION-CORRELATION.md).
Four of those adapters only release the recovered software-bus clock/data pins through Nordic
`nrf_gpio_cfg_default`; no GPIO-driven bit engine is admitted or recreated.
Six separately pinned bus-record wrappers are admitted only as R1 fixed configuration. Their
functional equivalent uses direct typed Nordic/vendor bindings; the unidentified global registry
and software-I2C engines remain blocked. See
[`BUS-REGISTRATION-CORRELATION.md`](correlation/BUS-REGISTRATION-CORRELATION.md).
The four stock software-TWI instances are now exhaustively bounded as forty SHA-pinned functions
covering open/read/write/start/stop/ACK behavior. Repeated compiler output and recovered wire
semantics do not establish authorship. Until an exact attributable source, version, and license are
found, OpenR1 uses Nordic hardware TWIM where validated and otherwise keeps the software provider
disabled; see
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md).
The adjacent RTC-device layer is independently split. Exact Nordic `nrfx_rtc_init` is compiled
from SDK 17.1.0, and one fixed initcall record wrapper is admitted only as direct typed R1
configuration. Seven generic epoch/calendar/named-record/callback bodies have no exact attributable
source and remain disabled behind an abstract provider; see
[`RTC-DEVICE-PROVIDER-BOUNDARY.md`](boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md).
The following `device_stacmd` initcall is configuration-only. All fourteen P1.01 framing, parity,
edge-wait, retry, and read/write bodies and the 22 coupled YHM device/register bodies are now
independently reconstructed under the owner-authorized full reduction. The adjacent
watchdog uses SDK 17.1.0 `nrfx_wdt.c`; OpenR1 owns only the recovered 10-second, priority-6,
single-channel configuration and scheduler feed seam. See
[`YHM2710-I2C5-RESOURCE-BOUNDARY.md`](boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md),
[`YHM2710-REDUCTION-CORRELATION.md`](correlation/YHM2710-REDUCTION-CORRELATION.md), and
[`WATCHDOG-DEVICE-CORRELATION.md`](correlation/WATCHDOG-DEVICE-CORRELATION.md).
The sensor-algorithm path uses a separate thirteen-function private heap initialized directly by
the Goodix-candidate boundary. Its two-bin tagged-block implementation is neither Nordic's
source-admitted FreeRTOS `heap_4` nor the pinned TLSF v3.1 source. Because no attributable
source/version/license is established, the heap remains disabled with its dependent provider path
instead of being translated or silently replaced; see
[`SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md`](boundaries/SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md).
Nordic's FreeRTOS app-timer backend omits two read-only legacy counters required by Peer Manager;
the local compatibility adapter delegates those reads to the upstream RTOS tick. The recovered
image does not contain `osDelayUntil`; the incompatible unused v10.5.1 wrapper section is therefore
garbage-collected instead of recreating a newer FreeRTOS kernel function locally.
The Nordic target compiles and retains the authenticated Bosch and ST motion-provider translation
units behind a clean R1 selector and Nordic port. Recovered evidence supplies TWIM1 at 400 kHz,
P0.11/P0.14, address `0x18`, P0.15 interrupt input, the LIS2DW12/BMA456W/QMA6100 stock probe order,
fixed provider configuration, and six-byte FIFO normalization. The owner-authorized QMA6100 source
reduction is compiled and selectable through the portable motion boundary; Nordic board binding and
owned-ring validation of that fallback remain explicit hardware-adoption gaps.
In particular, static evidence labels `health.db` as FlashDB TSDB, `kv.bin` as an R1-specific
fixed-class snapshot store, and `sleep.db` as a separate ring-specific journal. Consequently,
upstream FlashDB supplies only `health.db`; the two product formats are appropriate clean-room
implementations. The `kv.bin` ownership and audit-hardening split is documented in
[`KV-STORE-CORRELATION.md`](correlation/KV-STORE-CORRELATION.md).
The release discrimination, exact FlashDB/FAL address map, source hashes, and local-port boundary
are documented in [`FLASHDB-FAL-CORRELATION.md`](correlation/FLASHDB-FAL-CORRELATION.md).
The physical provider is now resolved as nRF52840 internal flash. Nordic `nrf_fstorage_sd` owns
mutation mechanics, FAL owns its table/partition machinery, and the local port owns only the
recovered 36-page geometry, bounds, serialization, and direct binding. The generic stock registry
is not recreated. Exact UICR/FDS/linker separation is documented in
[`INTERNAL-FLASH-CORRELATION.md`](correlation/INTERNAL-FLASH-CORRELATION.md).

CmBacktrace is source-admitted through the compatible interval and adapter split documented in
[`CMBACKTRACE-CORRELATION.md`](correlation/CMBACKTRACE-CORRELATION.md). Bosch BMA456 and ST LIS2DW12 are now
source-admitted through the exact provider/adapter split in
[`MOTION-PROVIDER-CORRELATION.md`](correlation/MOTION-PROVIDER-CORRELATION.md). The complete QMA6100
reduction and its intentional fail-closed divergences are recorded in
[`QMA6100-REDUCTION-CORRELATION.md`](correlation/QMA6100-REDUCTION-CORRELATION.md); installed-part
confirmation and Nordic board adoption remain hardware-validation tasks rather than opaque-source
dependencies.
ST25DVxxKC is independently source-admitted through the 27-provider/seven-adapter split in
[`ST25DVXXKC-CORRELATION.md`](correlation/ST25DVXXKC-CORRELATION.md). In particular, the local mailbox
receive adapter must enforce the recovered destination's 20-byte capacity before it calls ST's
provider; this security correction is product policy, not a local reconstruction of the driver.
The Goodix version string is exact and the 53 individually reviewed provider/demo functions, 116
byte-pinned graph-closure candidates, and 16 R1 adapter seams are documented in
[`GOODIX-PROVIDER-BOUNDARY.md`](boundaries/GOODIX-PROVIDER-BOUNDARY.md),
with the repeated integrity convention independently pinned in
[`GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md`](boundaries/GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md),
but source availability and redistribution rights are not. Under the owner-authorized full-reduction
policy (above), the Goodix biometric interiors are being reduced to reconstructed source with
per-function provenance; the reconstructed code is not vendor source and is never presented as
such. The local adapter preserves only power/lifecycle ordering,
delays, and opaque recovered mask values, and fails closed
when no provider binding is present. Behavioral models may remain in host tests as black-box compatibility
oracles.
Nordic application ownership is refined further in
[`NORDIC-SDK-CORRELATION.md`](correlation/NORDIC-SDK-CORRELATION.md). Five hundred seventeen application entries
now route to Nordic source, thirteen to SDK-bundled SEGGER source, and the R1-modified clock prefix,
four-characteristic BAE8 write handler, and four analog seams are six bounded adapters. Product configuration wrappers
and ambiguous example-derived handlers
remain separate or gated. This prevents local code from silently replacing Nordic BLE, Peer
Manager, DFU SVCI, SoftDevice RAM negotiation, logging, RTT, or formatter internals.
The exact application `SystemInit` and `nvmc_config` bodies, plus the two recovered UICR build
switches, are separately pinned in
[`NORDIC-SYSTEM-INIT-CORRELATION.md`](correlation/NORDIC-SYSTEM-INIT-CORRELATION.md); no startup body is local.
The exact static TWIM transfer-completeness helper is likewise routed to `nrfx_twim.c` and pinned
in [`NORDIC-TWIM-COMPLETENESS-CORRELATION.md`](correlation/NORDIC-TWIM-COMPLETENESS-CORRELATION.md).
Ten exact Peer Manager GATT-cache functions are pinned in
[`NORDIC-GATT-CACHE-CLOSURE.md`](closures/NORDIC-GATT-CACHE-CLOSURE.md).
Five exact Nordic BLE/Peer Manager static helpers, including the complete inline jump-table extent,
are pinned in
[`NORDIC-BLE-STATIC-HELPERS-CORRELATION.md`](correlation/NORDIC-BLE-STATIC-HELPERS-CORRELATION.md).
The tagged FAL subtree's `LICENSE` and linked source headers consistently identify Apache-2.0. The
exact upstream code is exercised by the host integration test and remains subject to the normal
license-notice obligations recorded in the vendor manifest.
