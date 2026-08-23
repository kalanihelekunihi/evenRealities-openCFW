# G2 functional-capability gap ledger

Status date: 2026-08-23
Target: official G2 `s200_v2.2.6.10`

This ledger is the domain-organized record of every known functional-capability
gap between the current openCFW G2 build and a fully source-compilable firmware
that replicates the stock image's functionality. It consolidates the per-closure
audit corpus under [`research/`](research) and the reference documents
([`source-coverage.md`](source-coverage.md),
[`upstream-inventory.md`](upstream-inventory.md),
[`memory-map.md`](memory-map.md), [`progress.md`](progress.md)) into one row per
capability, organized by domain: protocol, security, platform, health, system,
storage, sensors, hardware services, deployment.

## Status definitions

- `implemented-in-source` — compiled from source in a current build profile,
  with its verifiers and tests green. This asserts offline build/verification
  only; **no source-divergent image has ever been installed on G2 hardware**
  (see the deployment domain).
- `software-gap` — locally actionable: closing the row needs only software
  work (analysis, clean-room or upstream-attributed C, provider binding,
  placement, redirects, package verification, tests). No physical hardware and
  no unavailable proprietary input is required to write the code.
- `hardware-dependent` — closing or validating the row requires physical G2
  hardware, a debug probe, instrumentation, golden media captures, or on-device
  traffic. As of 2026-08-22 none of that is available in this workspace (see
  the hardware-availability audit below), so every such row is explicitly
  **blocked by unavailable physical evidence**.
- `proprietary-blocked` — closing the row requires unavailable licensed or
  vendor-proprietary source, keys, factory-matched binaries, or trained-model
  data. These rows are blocked by unavailable proprietary inputs, not by
  missing analysis.

A capability that functions in the byte-exact profile only through retained
stock bytes is still a gap row (its source replacement is open); it is not
`implemented-in-source`.

## Completeness rule

Functional completeness is not declared while any row remains both
unimplemented and unblocked. Every `software-gap` row must be implemented in
compilable C with the build profiles, verifiers, and test suite green; every
`hardware-dependent` row must be validated on authorized hardware or recorded
as blocked by unavailable physical evidence; every `proprietary-blocked` row
must name the unavailable input.

## Hardware-availability audit (2026-08-22)

A direct audit of this workspace host found:

- no USB J-Link, CMSIS-DAP, DAPLink, ST-Link, Black Magic, Nordic, or Ambiq
  debug interface in `system_profiler SPUSBDataType`;
- one `/dev/cu.usbserial-210` endpoint is present in addition to the generic
  macOS Bluetooth/debug-console endpoints. Its USB identity is generic
  QinHeng/CH340 (`idVendor=0x1a86`, `idProduct=0x7523`, product `USB Serial`),
  with no G2, debug-probe, capture-tool, or owner-authorization evidence, and
  therefore is not treated as authorized target hardware;
- no `nrfjprog`, `JLinkExe`, `JLinkGDBServer`, `pyocd`, `openocd`, `probe-rs`,
  `cargo-embed`, `nrfutil`, or `adafruit-nrfutil` executable;
- no owned-device flash readback, golden 32 MiB external-flash capture, BLE
  traffic capture, logic-analyzer trace, or power-rail measurement on file.

Consequently every `hardware-dependent` row below is blocked by unavailable
physical evidence until the owner connects authorized hardware and capture
tooling. The first hardware action, when hardware exists, remains the
non-destructive backup/preflight; the Apollo application update is single-slot
with no proven autonomous rollback.

## Row counts

| Domain | implemented-in-source | software-gap | hardware-dependent | proprietary-blocked |
| --- | ---: | ---: | ---: | ---: |
| Protocol | 2 | 16 | 3 | 3 |
| Security | 4 | 4 | 1 (shared with protocol) | 1 |
| Platform | 14 | 4 | 5 | 1 |
| Health | 1 | 3 | 1 | 1 |
| System | 3 | 3 | 3 | 0 |
| Storage | 2 | 4 | 2 | 0 |
| Sensors | 5 | 6 | 1 (touch validation) | 1 |
| Hardware services | 6 | 7 | 5 | 2 |
| Deployment | 3 | 0 | 2 | 1 |

Counts are row counts, not bytes; the unreviewed first-party remainder
(1,911 functions / 299,736 body bytes per
[`research/g2-apollo-unanchored-census.md`](research/g2-apollo-unanchored-census.md))
is carried as a single system-domain row that bounds all domains.

## Protocol

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| Cordio ATT server modules (`atts_*`: main/proc/read/write/ind/ccc/csf) | software-gap | ~7 modules, all source-identified 95–98%, production-excluded | `research/cordio-atts-*-source-recovery.md`; `research/cordio-aggregate-closure-audit.md` | per-module analyzers green; production admission/placement; controller validation is the hardware tail |
| Cordio ATT client modules (`attc_*`: main/proc/read/write/disc) | software-gap | e.g. client core 3,540 code bytes; r20.05–r20.05c exact Apache source | `research/cordio-attc-*-source-recovery.md`; `upstream-inventory.md` | EATT/signing are config exclusions, not gaps (`cordio-attc-sign-exclusion.md`, `cordio-attc-eatt-exclusion.md`) |
| Cordio L2CAP (main/master/slave) | software-gap | 3 modules closed; CoC config-excluded | `research/cordio-l2c-*-source-recovery.md`; `cordio-l2c-coc-exclusion.md` | production admission + hardware tail |
| Cordio DM modules (adv/adv-leg/conn/conn-sm/conn-master/slave/dev/phy/priv/main) | software-gap | 13 modules source-identified to r20.05+/Ambiq R4 family | `research/cordio-dm-*-source-recovery.md` | production admission + hardware tail |
| Cordio WSF (timer, buffer/message, OS/queue, assert/trace, wstr) | software-gap | 5 modules; exact r19.02/AmbiqSuite-2.5.1 definitions | `research/cordio-wsf-*.md`; `cordio-wstr-source-recovery.md` | production admission + hardware tail |
| Cordio HCI layer + Ambiq HCI driver + VS reset/NVDS | software-gap | mixed Apollo3-R2.5.1/R3.1.1/R4.4.1-Cooper lineage; clean-room behavior recorded | `research/cordio-hci-driver-source-recovery.md`; `cordio-hci-vs-reset-sequence-recovery.md` | production admission; controller-facing behavior needs EM9305 hardware validation |
| Packetcraft GATT profile object (`gatt_main.c`) | software-gap | 6 functions; exact r20.05c source admitted under Apache-2.0 | `research/cordio-gatt-profile-source-recovery.md` | production admission/placement |
| AmbiqSuite ANCC profile (12 Ambiq + 9 G2-local functions) | software-gap | 21 functions; exact AmbiqSuite 2.5.1 oracle admitted | `research/ambiqsuite-ancc-profile-source-recovery.md` | production admission; 9 G2-local functions need clean-room qualification |
| AmbiqSuite app framework + G2 pairing/privacy/connection/UI delta | software-gap (also security) | 50 functions / 29,110 B pinned + 14 legacy functions; stock MRAM/privacy/pairing/connection/diagnostic/UI delta is first-party reconstruction work | `research/ambiqsuite-cordio-app-framework-source-recovery.md` | clean-room the first-party delta; production routing; hardware validation |
| Even BLE services EUS/ESS/EFS/NUS (Cordio provider adapters) | software-gap | 21 functions / 2,374 body B / 3,000 B contiguous `[0x004BDE4C,0x004BEA04)`; proven G2-local | `research/g2-ble-transport-profiles-recovery.md` | `make ble-transport-profiles-closure`; clean-room must qualify WSF msg alloc, provider-handle ABI, connection races, CCC transitions, OTA gates, dual-device behavior |
| Even OTA BLE profile (AMOTA skeleton + 3 G2-local actions) | software-gap | 7 functions / 620 B `[0x004BDB90,0x004BDE4C)`; AmbiqSuite 2.5.1 AMOTA admitted | `research/g2-ble-ota-ring-profiles-recovery.md` | `make ble-ota-ring-profiles-closure`; qualify OTA reset/disconnect timing + dual-device behavior |
| Ring BLE profile (left/right ring sync client) | software-gap | 7 functions / 1,446 B `[0x004C46C0,0x004C4CEC)`; no public source | `research/g2-ble-ota-ring-profiles-recovery.md` | same closure target; qualify discovery/CCC epoch/ATT handle lifetimes |
| G2 multipart transport protocol (`transport_protocol.c`, `0xAA` framing) | software-gap | 13 functions / 4,134 B `[0x004B892C,0x004B9A80)`; wire format/lifecycle/CRC fully recovered; CRC-16/CCITT leaf already production source-owned | `research/g2-transport-protocol-recovery.md` | `make transport-protocol-closure`; clean-room needs callback ABI spec, target placement, hardware traffic validation tail |
| TinyFrame dual-glasses sync transport | implemented-in-source | 31 functions / 2,994 code B; production-admitted atomic 14-function graph; dual-profile overlays | `research/tinyframe-source-admission-boundary-audit.md` | only remaining gate: hardware golden frames for master/slave roles (hardware tail) |
| `AT^NUS` command handler | implemented-in-source | clean-room `at_nus.c` (597 B) authored and routed 2026-08-19; 18-byte leaf replaces the 16-byte stock object `[0x005A5520,0x005A5530)` | `research/g2-at-nus-recovery.md`; `components/apollo_main/core_overlay/at_nus.c`; `tests/test_at_nus_candidate.py` | host oracle test (response bytes, single provider call, return 1) + freestanding symbol probe + routing validation green |
| OTA service (`ota_service.c` — frame dispatch, flash backends, FS heal) | software-gap | 25 functions / 15,394 body B `[0x004448F4,0x004488EC)` | `research/g2-ota-service-recovery.md` | analyzer+tests green; production requires independently authored implementation and routing |
| OTA transport (`ota_transport.c`) | software-gap | 3 functions / 2,004 B `[0x0048D8D8,0x0048E1CC)` | `research/g2-ota-transport-dependency-boundary.md` | `make ota-transport-closure` |
| EFS file service (import/export over BLE) | software-gap | 12 functions / 9,276 body B, 9,934 B object | `research/g2-efs-service-recovery.md`; `g2-efs-transport-dependency-boundary.md` | analyzer/tests; clean-room + routing |
| Product-test protocol (`pt_protocol_procsr.c`, 66-command dispatcher) | software-gap | 73 functions / 32,866 body B `[0x0056F178,0x00577C3C)`; dependency boundary fully closed | `research/g2-pt-protocol-procsr-dependency-boundary.md` | `tools/analyze_g2_pt_protocol.py` green; hardware policy must be validated on hardware before routing |
| Touch-controller I2C protocol (device-side command/report layer) | software-gap (analysis complete) | 10 byte-pinned spans; transport/commands/reports/power confirmed at byte level | `research/g2-touch-i2c-protocol-recovery.md` | `analyze_g2_touch_i2c_protocol.py` + 11 fail-closed tests green |
| — touch command slot indices + resident dispatch table `0xB0C4` | hardware-dependent | 9-slot table is resident flash, not shipped | `research/g2-touch-i2c-protocol-recovery.md` | resident-table readback; blocked by unavailable physical evidence |
| — touch resident DFU engine (0x38-family commands) + boot-vector management | proprietary-blocked (also security) | engine not in shipped prefix `[0,0x867C)`; requires factory-matched resident flash image | `research/g2-touch-i2c-protocol-recovery.md` | resident image is not available as a blob |
| — touch gesture/calibration internals, ACT/ALR/WOT state machine | software-gap | MSC sensing loop `0x36C0–0x376C` mapped but not behavior-closed | `research/g2-touch-i2c-protocol-recovery.md` | behavioral closure of the mapped loop |
| Touch host-side DFU (`service_touch_dfu.c`) | software-gap | 32 functions / 6,430 body B `[0x0055FCB4,0x00561810)` | `research/g2-service-touch-dfu-recovery.md` | analyzer/tests; no production candidate yet |
| Glasses↔case UART protocol (glasses side `box_uart_mgr.c`) | software-gap | linked-unanchored closure; CRC/pack/unpack mirrors case side | `research/g2-box-uart-mgr-recovery.md`; `g2-box-stm32g0-platform-recovery.md` | `analyze_g2_box_uart_mgr.py` + tests |
| Case-side UART/update protocol (frame `5A A5 FF`, OTA state machine) | software-gap | frame format + checksums fully resolved (additive sums; no polynomial CRC); 22 pinned OTA step strings | `research/g2-box-function-map-recovery.md` | 10+12 fail-closed tests green |
| Charging-case firmware remainder (STM32G0) | software-gap | 428+7 functions / 40,664 B mapped of 55,752 B; 261 unresolved helpers | `research/g2-box-function-map-recovery.md` | Ghidra-lane naming of remaining helpers; no hardware needed for the map |
| — case battery/charging/thermal policy, bit-banged PMIC/charger/watchdog, `nSWAP_BANK` flow | hardware-dependent | log/code-evidenced only | `research/g2-box-stm32g0-platform-recovery.md` | requires physical case hardware execution |
| EM9305 BLE controller source replacement | proprietary-blocked | 1,494 exact functions / 157,122 B identified; 33,658 B unresolved; public Packetcraft ends at r20.05c | `upstream-inventory.md`; `research/em9305-expanded-sdk-archive-census.md` | licensed modern Packetcraft/EM source is the only path to source ownership |
| EM9305 residual segment classification | software-gap | 173 residual segments / 28,728 B | `research/em9305-controller-cluster-recovery.md`; `em9305-residual-segment-census.md` | bounded tranche in the existing analyzer lane |
| EM9305 QP/C 6.5.1 RTEF | software-gap | 3,052 cluster B 100% source/archive identified; bytes stock-retained | `progress.md`; `em9305-qpc-arcompact-audit.md` | source replacement + license review |
| EM9305 vendor libs (PML, sleep manager/timer, protocol timer, unitimer) | proprietary-blocked | 98 exact functions / 7,172 B authenticated to SDK v4.2 blobs; source unavailable | `progress.md`; `upstream-inventory.md` | recover or recreate proprietary source; retain exact stock spans meanwhile |
| BLE controller validation of any source-replaced Cordio path | hardware-dependent (also security) | — | `research/cordio-aggregate-closure-audit.md` | hardware/controller/concurrency validation on physical G2; blocked by unavailable physical evidence |

## Security

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| Apollo510 secure-OTA descriptor addition (`open_cfw_secure_ota_add`) | implemented-in-source | 86 B routine source-compiled; sole caller keeps stock ABI | `source-coverage.md`; `memory-map.md` | host execution covers MRAM bounds, eight-image guard, pending-bit encoding, descriptor selection, failure propagation |
| BLE pairing/bonding — SMP core (`smp_main.c`) | implemented-in-source | all 20 linked functions / 3,076 stock B redirect to 20 Apache-2.0 equivalents plus one private helper / 2,146 compiled B plus 24 alignment B; r20 `keyReady`/LESC and Ambiq stale-AES cleanup preserved | `research/cordio-smp-main-source-recovery.md`; `components/apollo_main/core_overlay/cordio_smp_main.c`; readiness `smp-main/` | host lifecycle/L2CAP/crypto/key/handler contracts, exact 21-leaf routing, component, manifest, package, and flash-plan gates green; real controller/peer validation remains in the shared hardware row |
| BLE pairing — SMP database (`smp_db.c`, failure-count/backoff) | implemented-in-source | all 11 linked functions / 2,952 stock B redirect to 11 Apache-2.0 leaves / 698 compiled B plus 14 alignment B; `SMP_DB_MAX_DEVICES=10` and r20 event ABI preserved | `research/cordio-smp-db-source-recovery.md`; `components/apollo_main/core_overlay/cordio_smp_db.c`; readiness `smp-db/` | host state/timer/backoff contracts, exact Thumb routing, component, manifest, package, and flash-plan gates green; repeated-pairing/controller validation remains in the shared hardware row |
| BLE pairing — SMP Secure Connections main (`smp_sc_main.c`) | implemented-in-source | all 18 linked functions / 2,626 stock B redirect to 18 Apache-2.0 leaves / 2,278 compiled text B plus 452 closure/alignment B; G2 SRAM/config ABI preserved | `research/cordio-smp-sc-main-source-recovery.md`; `components/apollo_main/core_overlay/cordio_smp_sc_main.c`; readiness `smp-sc-main/` | host scratch/CMAC/F4/PDU/passkey/retry/diagnostic contracts, exact Thumb routing, component, manifest, package, and flash-plan gates green; public-key/DH-check/passkey/OOB/reconnect/repeated-attempt validation remains in the shared hardware row |
| Cordio SMP common actions (`smp_act.c`) | implemented-in-source | all 25 linked definitions / 2,924 stock B replaced by 24 guarded redirects plus one exact 2-byte in-place leaf; 1,758 compiled B + 20 alignment B | `research/cordio-smp-act-source-recovery.md`; `components/apollo_main/core_overlay/cordio_smp_act.c` | six host behavior contracts, exact Thumb leaves, all production routes, component, manifest, package, and flash-plan gates green; controller validation is carried by the shared hardware row |
| SMP Secure Connections state machines and role actions | software-gap | remaining SC state/action units; both DH-key-check paths characterized | `progress.md`; `research/cordio-smp-sc-act-source-recovery.md` | source recreation and compiler/linker equivalence remain promotion gates |
| Cordio DM LE Secure Connections (`dm_sec_lesc.c`) | implemented-in-source | all seven live functions / 222 stock B redirect to seven Apache-2.0 leaves / 278 compiled B; four absent APIs proven dead-stripped | `research/cordio-dm-sec-lesc-source-recovery.md`; `components/apollo_main/core_overlay/cordio_dm_sec_lesc.c` | host behavior, exact Thumb surface, ten-relocation route analyzer, component, manifest, and package gates green |
| Cordio DM security core (`dm_sec.c`) | implemented-in-source | all eight live functions / 462 stock B redirect to eight Apache-2.0 leaves / 506 compiled B; four absent APIs proven dead-stripped | `research/cordio-dm-sec-source-recovery.md`; `components/apollo_main/core_overlay/cordio_dm_sec.c` | host behavior, exact Thumb surface, 19-relocation route analyzer, component, manifest, package, and flash-plan gates green; controller validation is carried by the shared hardware row |
| Cordio DM security role modules (`dm_sec_slave.c`, `dm_sec_master.c`) | implemented-in-source | all six live functions / 292 stock B redirect to six Apache-2.0 leaves / 332 compiled B plus 6 alignment B | `research/cordio-dm-sec-slave-source-recovery.md`; `research/cordio-dm-sec-master-source-recovery.md`; `components/apollo_main/core_overlay/cordio_dm_sec_roles.c` | host behavior, exact Thumb surface, 14-relocation route analyzers, component, manifest, package, and flash-plan gates green; controller validation is carried by the shared hardware row |
| App-level pairing/privacy/bonding policy (G2 delta) | software-gap | part of the unquantified first-party app-framework delta | `research/cordio-aggregate-closure-audit.md` | clean-room reconstruction; hardware validation tail |
| Apollo secure bootloader / secure-boot chain (ROM `0x00400000–0x00410000`) | proprietary-blocked (retained by design) | 64 KiB, absent from EVENOTA, protected | `memory-map.md`; `freertos-g2-config-port-audit.md` | not OTA-updatable; replacement would require Ambiq secure-boot keys — outside project scope by design |
| G2 cryptographic backend (first-party Even code) | software-gap | unbounded; named only as an uncertain/proprietary first-party boundary | `upstream-inventory.md` | re-create only from a reviewed behavioral contract and host/target tests; no dedicated audit exists yet — weakest-grounded row |

Security-relevant recorded facts (not gap rows): case-UART integrity and case
OTA verification are additive sums with no polynomial CRC and no signature
(`research/g2-box-function-map-recovery.md`); the BLE OTA image path uses CRC
checks and read-after-write with no documented signature verification; overall
update security rests on the protected Apollo bootloader.

## Platform

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| FreeRTOS kernel identity/config/port (V10.5.1 pin, recovered config, G2 TCB patch, CM55_NTZ port) | implemented-in-source | TCB patch compiles to exact 112-byte ABI; BASEPRI=0x30; 1,024 Hz STIMER tick | `upstream-inventory.md`; `research/freertos-g2-config-port-audit.md`; `freertos-g2-tcb-vendor-patch-audit.md` | 21-span verifier; patch analyzer |
| FreeRTOS list primitives | implemented-in-source | 4 leaves at `[0x0045607C,0x0045610E)` | `upstream-inventory.md`; `source-coverage.md` | upstream-oracle, ABI, topology, manifest gates |
| FreeRTOS queue/mutex/semaphore subset (creators, generic send, take, delete, predicates, ISR paths, event-list) | implemented-in-source | named stock spans; strict closures | `upstream-inventory.md`; `research/freertos-queue-next-closure-audit.md` | per-tranche focused + production suites; both profiles pinned |
| FreeRTOS task/scheduler-state leaves | implemented-in-source | individual 6–518 B spans; fixed-address global seams `0x20074A20`–`0x20074A58` | `upstream-inventory.md`; `research/freertos-task-next-closure-audit.md` | focused writer/caller topology + integration contracts |
| FreeRTOS `heap_4` adapter | implemented-in-source | 4 functions at `[0x00456110,0x00456338)` | `upstream-inventory.md`; `source-coverage.md` | source-owned with `vQueueDelete` closing over source heap free |
| FreeRTOS scheduler cluster (yield, critical sections, reset-next-unblock, increment-tick, resume-all) | implemented-in-source | 6 functions promoted as one tranche | `research/freertos-scheduler-cluster-production-promotion-plan.md` | production cluster verifier 9/9; dual-profile chains green |
| FreeRTOS CM55_NTZ port assembly (7 leaves) | implemented-in-source | 182 source-owned in-place bytes `[0x005FA058,0x005FA132)` | `upstream-inventory.md`; `source-coverage.md` | exact ELF relocation allowlist; `in_place_leaves` rejects overlap |
| FreeRTOS scheduler-start core (`vTaskStartScheduler`, `xPortStartScheduler`, `vTaskSwitchContext` + G2 trace ring) | implemented-in-source | three stock entries redirect atomically to four strict-relocation leaves (including non-returning fail-stop); Apple/Linux overlays and packages pinned | `research/freertos-task-start-scheduler-source-candidate-audit.md`; `freertos-port-start-scheduler-source-candidate-audit.md`; `freertos-task-switch-context-source-candidate-audit.md` | `make freertos-scheduler-start-core-closure`; dual-profile overlay/component/package gates green |
| FreeRTOS scheduler-start on-device preemption/overflow/trace/first-task evidence | hardware-dependent | source chain complete offline; validation needs live CM55 exception/timer behavior and trace capture | same scheduler-start audits; 2026-08-22 hardware audit | authorized G2 + probe/capture; blocked by unavailable physical evidence |
| FreeRTOS Apollo STIMER tick/tickless port with first-party power hooks | hardware-dependent | tickless `[0x00456498,0x0045655C)`; bounded STIMER algorithms recreated as candidates | `progress.md`; `research/freertos-apollo-tickless/stimer-tick/stimer-setup-source-candidate-audit.md` | 14 focused tests pass both profiles; remaining gate is real WFI/counter-wrap/IRQ-latency/compare-timing on device — blocked by unavailable physical evidence |
| FreeRTOS task/queue-private closure (`vTaskPlaceOnEventList`, task-context receive, `xQueueGenericReset`, `vTaskGetInfo`) | implemented-in-source | all four authenticated V10.5.1 functions production-routed; final `vTaskGetInfo` promotion replaces 128 stock bytes with a 120-byte leaf at `0x007BC6DC` | `research/freertos-queue-next-closure-audit.md`; `research/freertos-agent-a-exact-source-candidates-audit.md`; `research/freertos-task-get-info-source-audit.md` | `make freertos-task-get-info-closure`; host behavior, TCB/status ABI, four-provider relocation, stock redirect, component, manifest, and package gates green |
| CMSIS-FreeRTOS v10.5.1 wrapper (43-function object) | implemented-in-source | `[0x0044900E,0x00449ED2)`, 3,780 B; frontier declared closed | `progress.md`; `upstream-inventory.md`; `research/cmsis-freertos-linked-function-census.md` | both profile pins; census fail-closed analyzer |
| AmbiqSuite 5.1.0 HAL selected leaves (MSPI interrupt-clear, SPOT, MCUCTRL, oscillators, trim) | implemented-in-source | 48 B MSPI leaf ×2 images; SPOT init + 13-entry callback layer | `source-coverage.md`; `g2/README.md`; `upstream-inventory.md` | vendored snapshot verifier; section-GC retained leaf pins |
| AmbiqSuite HAL wider ordinal/port reconciliation; system-sleep/task-vote power policy | hardware-dependent | unnamed bulk; product-rtos task-vote policy | `progress.md`; `research/g2-product-rtos-recovery.md` | clean-room task-vote/hook implementation + on-device power-state/watchdog validation — blocked by unavailable physical evidence |
| Ambiq GPU patch exports (11 Nema patch functions) | hardware-dependent | 4,232 exact section bytes; 11 exports source-qualified as clean-room candidates | `research/nemagfx-ambiq-g2-provenance-audit.md`; `ambiq-gpu-patch-*-source-candidate-audit.md` | rendered-output/command-stream comparison on Apollo510 — blocked by unavailable physical evidence |
| Nema bare-metal HAL (18 stock functions) | hardware-dependent | 614 B candidate, production-excluded | `research/ambiq-nema-bare-metal-hal-source-candidate-audit.md` | Apollo510 IRQ/cache/ring/retention/render tests — blocked by unavailable physical evidence |
| IAR DLIB bounded runtime (13 code units) | implemented-in-source | 10/10 units production-integrated; final 72 executable bytes moved opaque→generated | `progress.md`; `iar-runtime-memory-source-candidate.md`; `iar-runtime-math-errno-source-candidate.md` | runtime candidate tests; optional Unicorn target runs |
| IAR DLIB formatted-I/O cluster (printf/scanf cores, scanf_s, constraint handler, wrapper) | software-gap | ~6,938 B across 5 string-signature functions + 6 topology neighbours | `research/g2-iar-dlib-format-io-recovery.md`; `g2-apollo-unanchored-census.md` | bounded audit to the 13-unit standard; target-compiled-section gates open |
| IAR DLIB exact release/archive provenance | proprietary-blocked | identification 40–50%; 9.60.2 leading candidate | `progress.md`; `iar-dlib-runtime-census.md` | licensed IAR archive for byte comparison; functional recreation already done clean-room — provenance-only |
| CmBacktrace fault handler | software-gap | identity 70–80%; MIT snapshot vendored; `get-cur-thread-name` leaf production source-owned | `upstream-inventory.md`; `cmbacktrace-identity-audit.md` | source port needs recovered `CmBacktraceConfig` + CM55 fault glue; fault-path device validation tail |
| Apollo (Even) bootloader — littlefs/EasyLogger/Ambiq leaves | implemented-in-source | ~25 named leaves + builder records | `memory-map.md`; `source-coverage.md`; `upstream-inventory.md` | `components/bootloader/core_overlay/EVIDENCE.md`; per-leaf redirect pins |
| Apollo (Even) bootloader — remaining body | software-gap | ~146 KB official retained; identification 85–90% | `progress.md`; `source-coverage.md` | continue source closure; do not cross the protected secure-loader boundary |
| Ambiq secure bootloader (ROM `0x00400000`–`0x00410000`) | hardware-dependent (policy: preserve boundary) | 64 KiB, absent from EVENOTA, protected | `memory-map.md`; `progress.md` | owned-device readout or authoritative vendor source; blocked by unavailable physical evidence |

## Health

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| Health mutex + common-event handler (`health.c`) | implemented-in-source | four guarded stock redirects / 504 replaced body B; four strict-relocation leaves / 198 compiled B | `research/g2-health-recovery.md`; `components/apollo_main/core_overlay/health.c` | host oracle, Thumb surface, route analyzer, component, manifest, and package gates green; diagnostic-only EasyLogger calls deliberately omitted |
| Health on-device mutex/role/display-gating validation | hardware-dependent | source-complete event-0/event-5 policy and service-one record path | same health audit; 2026-08-23 hardware audit | authorized G2 plus display/transport trace; explicitly blocked by unavailable physical evidence |
| Health data manager (`health_data_manager.c`) | software-gap | 10 functions / 2,644 body B; object `[0x005597F0,0x0055A350)` | `research/g2-health-data-manager-dependency-boundary.md` | object/dependency closure analyzer pinned; schema/policy recreation + device data validation tail |
| Health protobuf service (`pb_service_health.c`, service `0x0E`) | software-gap | 8 functions / 3,092 body B; object `[0x0055A558,0x0055B2A4)` | `research/g2-pb-service-health-recovery.md` | closure analyzer + pinned manifests; first-party schema/source recreation (nanopb seam already admitted) |
| Health UI page (`ui_health_page.c`) | software-gap | 12 functions / 9,414 body B; object `[0x004FB1FA,0x004FD940)` | `research/g2-ui-health-page-dependency-boundary.md` | `make ui-health-page-closure`; all 666 external calls terminate at admitted seams |
| Health-metric algorithms (provider boundary) | proprietary-blocked | not bounded on the G2 side; no `g2/` doc names the algorithm provider — genuine documentation hole | root `README.md` (Goodix/GoMore/YHM boundary policy); `research/g2-health-recovery.md` (first-party protobuf provider model) | explicit "unsupported" return per repo policy; closure would require licensed provider source |

## System

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| Startup/init sequencing (power/clock/RTC/SPOT/low-power/display-subsystem initializers, startup app-ID policy, onboarding gate) | implemented-in-source | named leaf set in core_overlay profile | `g2/README.md` "Current source replacement" | complete-package Apple/Linux profile pins per release |
| SystemAlert UI (`systemAlert.c`) | software-gap | 2,346 B / 7 blocks, zero production source | `research/g2-system-alert-recovery.md` | `tests.test_analyze_g2_system_alert`; clean-room replacement not yet routed |
| SystemClose UI (`systemClose.c`) | software-gap | 20 functions / 5,368 B; "not yet production-routed" | `research/g2-system-close-dependency-boundary.md` | `tools/analyze_g2_system_close.py` + unittest; close/confirm/cancel/minimize/scroll/IMU-reflash policy needs clean-room source |
| System monitor peer-reboot callback (`system_monitor.c`) | implemented-in-source | complete 510-byte stock body redirects to one 650-byte strict-relocation clean-room leaf; descriptor-only ingress retained | `research/g2-system-monitor-recovery.md`; `components/apollo_main/core_overlay/system_monitor.c` | host oracle, Thumb symbol/43-relocation closure, analyzer route, component, manifest, and package gates green |
| System monitor on-device peer-reboot orchestration | hardware-dependent | offline record validation, display quiescence, bounded wait, scheduler-idle dispatch, five-reset sequence, and lens-status publication are source-complete | same system-monitor audit; 2026-08-22 hardware audit | paired authorized G2 reboot/display/scheduler trace; blocked by unavailable physical evidence |
| UX system-status sync (`ux_system.c` — peer OTA/BLE/ring status) | hardware-dependent | 11 functions / 2,868 B fully recovered | `research/g2-ux-system-recovery.md` | `make ux-system-closure` passes; production admission requires paired-hardware transition validation — blocked by unavailable physical evidence |
| Watchdog driver | implemented-in-source | two complete stock entries / 140 body B redirect to two strict-relocation clean-room leaves / 28 source B; selector-zero/value-one policy preserved over retained providers | `research/g2-watchdog-recovery.md`; `components/apollo_main/core_overlay/watchdog.c` | host oracle, Thumb symbol surface, analyzer routing, component, and package gates green |
| Watchdog on-device enable/reset behavior | hardware-dependent | offline selector/provider chain complete; physical nPMx watchdog response is not observable in this workspace | same watchdog audit; 2026-08-22 hardware audit | authorized G2 + reset-cause/timing capture; blocked by unavailable physical evidence |
| Product startup/main thread (`s200_config_main.c`, product RTOS glue) | software-gap | reset chain identified; main-thread body + LVGL widget constructors + init hook bounded, analysis-only | `research/g2-s200-config-main-recovery.md`; `g2-product-rtos-recovery.md` | `tests.test_analyze_g2_s200_config_main`; `make product-rtos-closure`; clean-room source + device power validation tail |
| Unreviewed first-party remainder frontier (bounds all domains) | software-gap | 1,911 functions / 299,736 B `investigation required`; first-party bucket 1,782 fn / 216,564 B | `research/g2-apollo-unanchored-census.md` | `tests/test_analyze_g2_apollo_unanchored_census.py` (18 fail-closed tests); ranked follow-ups: FreeType engine, LVGL `0x5Dxxxx` sea, IAR format-I/O, liblc3 internals, peripheral-register cluster |

## Storage

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| littlefs v2.10.1 utility/private leaves (dual-image) | implemented-in-source | 30 Apollo-main + 26 bootloader functions; the public `lfs_file_size` wrapper joined them 2026-08-18 (recovered `lfs_t` mlist offset `0x28`) | `g2/README.md`; `upstream-inventory.md`; `source-coverage.md`; `research/littlefs-next-closed-leaves-audit.md` | `make littlefs-snapshot` verifier + per-tranche tests; fail-closed hash pins both profiles |
| littlefs complete core + G2 block port / MSPI transport (MX25U25643G 32 MiB external flash) | hardware-dependent | block-port callback ABI bounded; read-only port design complete | `g2/README.md`; `research/littlefs-g2-block-port-audit.md`; `littlefs-g2-mspi-transport-audit.md` | golden 32 MiB external-flash capture; host mount comparison vs stock; blocked by unavailable physical evidence |
| FlashDB 2.1.1 KVDB/FAL snapshot + read-only FAL port | hardware-dependent (admission) | 14-file KVDB/FAL closure byte-exact; `kvdb@0x01FC0000/0x38000`, `NVdb@0x01FF8000/0x8000` | `g2/README.md`; `research/flashdb-configuration-recovery-audit.md`; `flashdb-readonly-port-source-candidate-audit.md` | host differential tests green; promotion blocked on golden `kvdb`/`NVdb` capture + non-destructive mount policy — blocked by unavailable physical evidence |
| G2 KVDB service objects (setting, time, time-format, temperature-unit, universal-setting, als-scale, terminal-mode, onboarding-config, ring, module-configure) | implemented-in-source | all 10 objects production-routed 2026-08-18/19 (apple component 3,673,918 B; 275 relocated leaves total in overlay) | `progress.md`; `research/g2-kvdb-*-recovery.md`; `components/apollo_main/core_overlay/kvdb_*.c` | per-object host tests + analyzer production flips + package verification green; device data validation remains a hardware tail |
| G2 KVDB system service (`service_kvdb.c`) incl. `kvbooCount` lifecycle + 11 migrations | software-gap | `kvMagic=0x5A000020`; lifecycle + migration callbacks bounded | `research/g2-service-kvdb-recovery.md`; `g2/README.md` | production mount blocked by golden-media validation, schema semantics, non-destructive reset policy |
| G2 NVDB service objects (all six record objects routed; `service_nvdb.c` core remains) | software-gap | sensor-caldata + buzzer + product-mode + mac + adv-magic + sys-dt routed 2026-08-18/20 (apple component 3,679,078 B); `service_nvdb.c` (`nvMagic=0x55550022` lifecycle) has no candidate and owns zero package bytes | `progress.md`; `research/g2-nvdb-*-recovery.md`; `g2-service-nvdb-recovery.md` | host tests per candidate green; `service_nvdb.c` needs clean-room authorship; read-only golden `NVdb` capture + non-destructive mount policy gate production mount |
| FreeRTOS-Plus-CLI filesystem commands (`prvCommand_filesystem.c`) | software-gap | 12 entries / ~2,026 B at `[0x57E826,0x57F550)`; proven first-party | `research/g2-freertos-plus-cli-filesystem-recovery.md` | analyzer test green; clean-room rewrite not yet production-routed |

## Sensors

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| EvenHub IMU enable policy (parser cmd `0x12` / UI teardown entry) | implemented-in-source | 60 B `[0x004E1406,0x004E1442)` | `components/apollo_main/core_overlay/EVIDENCE.md`; `memory-map.md`; `source-coverage.md` | core_overlay profile build + host substitution tests pin every transition/no-op case |
| Sensor-hub policy/message routing (`sensor_hub.c`) | software-gap | 31 functions / 4,026 body B; object `[0x004A6644,0x004A777C)` | `research/g2-sensor-hub-dependency-boundary.md` | `tools/analyze_g2_sensor_hub.py` + focused test; all 254 external calls terminate at closed/admitted seams; negative evidence: no sensor-fusion library body |
| IMU driver (`imu_icm45608.c`: FIFO, sample ring, orientation, quaternion→Euler, AID/tilt/tap/head-up/compass) | software-gap | 53 functions / 11,674 body B; object `[0x004A35B0,0x004A6644)` | `research/g2-imu-icm45608-recovery.md` | analyzer + test green; byte ledger pinned; clean-room candidate absent |
| ALS driver (`als.c` + private TI OPT3007 register adapter) | software-gap | 38 functions / 3,858 body B; `[0x004AD9B8,0x004AEA40)` | `research/g2-als-dependency-boundary.md` | `make als-closure`; production routing disabled |
| NVDB sensor-calibration records (`service_nvdb_sensor_caldata.c`) | implemented-in-source | 8 functions; object `[0x00509764,0x00509B48)`; production-routed 2026-08-18 (8 relocated leaves, 8 guarded `b_w` redirects, package pins advanced) | `research/g2-nvdb-sensor-caldata-recovery.md`; `components/apollo_main/core_overlay/nvdb_sensor_caldata.c` | host tests + component/overlay/package verification green; device data validation remains a hardware tail |
| KVDB ALS-scale record (`service_kvdb_als_scale.c`) | implemented-in-source | 3 functions; `[0x004AECA4,0x004AEE28)`; candidate production-routed 2026-08-18 under the reviewed apple-clang profile | `research/g2-kvdb-als-scale-recovery.md`; `components/apollo_main/core_overlay/kvdb_als_scale.c` | host tests + overlay/package pins green; device data validation remains a hardware tail |
| eAT sensor command cluster (`AT^IMU_RAWDATA`, `AT^IMU_EULER`, `AT^ALS*`, `AT^BRIGHTNESS*`, `AT^SCRN_*`, `AT^INFO/RESET/PSN`) | implemented-in-source | clean-room `at_core_sensor.c` (13,890 B) authored and routed 2026-08-19; 12 relocated leaves replace the 12 stock handlers `[0x005A5720,0x005A5984)`; registry remains 21 records | `research/g2-eat-core-sensor-recovery.md`; `g2-eat-registry-recovery.md`; `components/apollo_main/core_overlay/at_core_sensor.c`; `tests/test_at_core_sensor_candidate.py` | host oracle tests + analyzer production flip green; stock quirks preserved (SCRN_Y accepts 0) |
| eAT touch-panel command (`at_tp.c` / `AT^TP`) | software-gap | 2 bodies / 898 body B; `[0x005A5984,0x005A5D94)` | `research/g2-at-tp-recovery.md` | object analyzer pins all subcommands, bounds, ingress topology |
| Gesture processor (`service_gesture_processor.c`) | software-gap | 5 blocks / 1,236 body B; `[0x00502D56,0x00503298)` | `research/g2-service-gesture-processor-recovery.md` | analyzer test green; closure manifests pinned |
| Host touch driver (`drv_cy8c4046fni.c`) | software-gap | 23 functions / 1,754 body B; `[0x0055B2EC,0x0055BA70)` | `research/g2-drv-cy8c4046fni-dependency-boundary.md` | analyzer + test green; all indirect bus-ops calls bounded; first-party private source |
| Touch-controller shipped application layer (PSoC 4000T) | software-gap (analysis) with hardware validation tail | 34,428 B programmed prefix `[0,0x867C)` | `research/g2-touch-identity-recovery.md`; `g2-touch-i2c-protocol-recovery.md` | device-free analyzers + fail-closed mutation tests green; slot-index confirmation needs resident readback — blocked by unavailable physical evidence |
| Touch-controller resident region (dispatch tables, HAL descriptors, resident DFU engine, boot vectors) | proprietary-blocked | resident flash `≥0x8680`; not shipped in any blob | `research/g2-touch-i2c-protocol-recovery.md` | requires factory resident-image readout or vendor source |
| Goodix-derived error utility (`util_error_check.c`) | implemented-in-source | 178 B stock handler replaced by a 254 B clean-room leaf; retained authenticated 344 B table; exact GR551x SDK 1.7.0 provenance; production-routed 2026-08-21 | `research/g2-util-error-check-goodix-recovery.md`; `components/apollo_main/core_overlay/util_error_check.c`; `tests/test_util_error_check_candidate.py` | `make util-error-check-closure`; host oracle, single-leaf Thumb closure, routing, component, and package pins green; bounded unknown-code fallback is the reviewed safety correction |

## Hardware services

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| LVGL Ambiq display port (`lv_ambiq_display.c`) | implemented-in-source | 7 functions / 638 stock bytes; frontier explicitly closed | `research/lvgl-ambiq-display-port-closure-audit.md` | `make lvgl-display-port-closure` fail-closed analyzer |
| Apollo display pipeline first-party core (display-thread command loop, input handler, display-mode state machine, subsystem initializer, dynamic callback) | implemented-in-source | 2,558 + 1,780 + 1,370 + 300 + 12 B source-owned | `source-coverage.md`; `research/g2-display-thread-recovery.md` | profile build + fail-closed pins |
| Display driver manager + remaining display state/event helpers | software-gap | 1,035 instructions / 184 calls bounded; not production-routed | `research/g2-displaydrv-manager-recovery.md`; `g2-display-thread-recovery.md` | analyzers + focused tests green; clean-room recreation then hardware/UI validation tail |
| ULED display preprocess | implemented-in-source | candidate `uled_display_preprocess.c` production-routed 2026-08-20 (242 B text + 28 B rodata leaf replacing the 584 B stock body; overlay tool rodata allow-list extended for `.L__const` locals) | `research/g2-uled-display-preprocess-recovery.md`; `components/apollo_main/core_overlay/uled_display_preprocess.c` | host tests pin all 9 assertions + GPU-failure path; analyzer production flip + package verification green |
| LVGL core library production integration (v9.3.0-dev hybrid fork) | hardware-dependent | 65 TUs, 252 headers verified offline; config recovered | `upstream-inventory.md`; `research/lvgl-version-recovery-audit.md`; `lvgl-ambiq-source-abi-recovery-audit.md` | snapshot verifier green; admission gated on atomic integration + Apollo510 hardware validation — blocked by unavailable physical evidence; link-strategy question is a software sub-item |
| NemaGFX/NemaVG + Ambiq GPU patch (11 exports) | hardware-dependent | 4,232 exact section bytes source-qualified as candidates; identity closed (NemaGFX 1.4.12, NemaVG 1.1.8) | `research/nemagfx-ambiq-g2-provenance-audit.md` | candidates not admitted; gate: admission decision + atomic integration + Apollo510 validation — blocked by unavailable physical evidence |
| Ambiq bare-metal Nema HAL | hardware-dependent | 18 functions / 614 B; candidate deliberately not linked | `research/ambiq-nema-bare-metal-hal-source-candidate-audit.md` | candidate tests green; atomic binding (software) + Apollo510 tests (hardware) — blocked by unavailable physical evidence |
| FreeType 2.9.1 engine | hardware-dependent (font payload recovery) + software sub-items (toggles/promotion review) | 297 byte-exact upstream files authenticated; production-excluded | `g2/README.md`; `research/freetype-2.9.1-snapshot-audit.md`; `freetype-recovery-audit.md` | snapshot + config audits green; external font asset identities/payloads need flash contents — blocked by unavailable physical evidence |
| LVGL font manager + external font assets | software-gap (manager) / hardware-dependent (assets) | manager bounded: 4-entry font chains, XIP header validation, FreeType face lifecycle | `research/g2-lvgl-font-manager-recovery.md` | not production-routed; font assets blocked by unavailable physical evidence |
| Audio codec/DSP image (NationalChip GX8002 fwpack/BINH, KWS/NPU payload) | proprietary-blocked | image-A stage2 split proven; 129,964 B KWS payload is proprietary trained-model data | `research/g2-codec-fwpk-segments-recovery.md`; `g2-codec-stage2-sections-recovery.md` | container/wire formats match MIT public SDKs; capstone C-SKY support is a tooling sub-item; boot selection/XIP base are hardware tails |
| Apollo-side codec services (`service_codec_host`, `service_codec_dfu`, `service_codec_porting`, `at_codec`, `drv_gx8002b`) | software-gap | all binary-closed; zero production ownership each | `research/g2-service-codec-host-recovery.md`; `g2-service-codec-dfu-recovery.md`; `g2-service-codec-porting-recovery.md`; `g2-at-codec-recovery.md`; `g2-drv-gx8002b-recovery.md` | per-object analyzers + tests green; independently authored implementation + routing pending |
| Apollo-side touch DFU service (`service_touch_dfu`) | software-gap | 32 bodies / 394 calls bounded; 12 exact symbols | `research/g2-service-touch-dfu-recovery.md` | analyzer test green; clean-room implementation + routing pending |
| Apollo-side case services (`box_uart_mgr`, box-detect state machine) | software-gap with hardware validation tail | box-detect object: 209 direct calls, all classified; not production-routed | `research/g2-box-uart-mgr-recovery.md`; `g2-service-box-detect-dependency-boundary.md` | analyzers + tests green; recreation + case/box hardware validation tail |
| Ring gesture forwarding (`ring_gesture` component) | implemented-in-source | 160-byte GPL-3.0-only overlay, attributed to `jimrandomh/g2flash` | `components/apollo_main/ring_gesture/NOTICE.md`; `g2/README.md`; `g2/Makefile` | `make ring-source` builds + verifies under both toolchain profiles; never installed on hardware (see deployment) |
| Apollo charger services (`charger_common` battery-sync/policy layer) | implemented-in-source | 11 leaves / 2,400 stock body bytes replaced 2026-08-20; five file-static state cells bound to recovered SRAM addresses; apple component 3,680,920 B | `research/g2-charger-common-recovery.md`; `components/apollo_main/core_overlay/charger_common.c` | host tests + analyzer production flip + package verification green; on-device charge-policy validation is a hardware tail |
| Apollo charger drivers (`chg_bq25180` charger IC, `chg_bq27427` fuel gauge) | implemented-in-source | both production-routed: BQ25180 has 22 leaves / 1,792 replaced stock body bytes; BQ27427 has 33 leaves / 4,464 replaced stock body bytes plus retained hardware-configuration data | `research/g2-chg-bq25180-recovery.md`; `g2-chg-bq27427-recovery.md`; `components/apollo_main/core_overlay/chg_bq25180.c`; `chg_bq27427.c` | host wire/data/runtime oracles, target closure, guarded redirects, analyzer flips, component, and package verification green; rail/charge behavior validation remains blocked by unavailable physical evidence |
| Ring service stack (`ring_service`, `thread_ring`, `ring_connect_policy`, `pb_service_ring`, `service_ring_battery`, `cb_ring_battery`) | software-gap | ring_service: 18 fn / 2,412 body B; all proven G2-local first-party, zero ownership | `research/g2-ring-service-dependency-boundary.md`; `g2-thread-ring-dependency-boundary.md`; `g2-ring-connect-policy-dependency-boundary.md`; `g2-pb-service-ring-recovery.md`; `g2-service-ring-battery-recovery.md`; `g2-cb-ring-battery-recovery.md` | per-object analyzers green; implementation must qualify WSF allocation, ATT handle lifetimes, dual-device behavior before routing |

## Deployment

| Capability | Gap status | Size/bounds | Evidence | Acceptance gate |
| --- | --- | --- | --- | --- |
| EVENOTA packaging + wrap tooling (main / case / touch) | implemented-in-source | reference package byte-identical (SHA-256 pinned); wrap commands for 3 payload types | `g2/README.md`; `tools/open_cfw.py` | `make reference` reproduces the official bundle byte-for-byte under any profile |
| Linux reproducible builds (toolchain profiles) | implemented-in-source | `reference`, `ring-source`, full `source` profiles build and verify fail-closed under `linux-clang` | `linux-reproducible-build.md`; `g2/Makefile` | per-profile recorded pins; detection rejects unreviewed compilers |
| Offline flasher inspection of the source-divergent artifact | implemented-in-source | structural checks + offline flasher inspection passed | `g2/README.md` "Safety and provenance" | build never opens a serial port, debugger, or flasher |
| Codec + EM9305 source wrappers | proprietary-blocked (toolchains) + software sub-item (install semantics) | wrappers intentionally absent; package formats parsed only | `g2/README.md` "Replacing more blobs with source" | needs C-SKY (codec) / MetaWare ARC (EM9305) source toolchains + complete install semantics |
| Physical installation of any source-divergent image | hardware-dependent | nothing source-divergent has ever been installed on G2 hardware; bootloader materially riskier than application | `g2/README.md` "Safety and provenance" | gate: per-device state backup, preserve case serial-number windows, keep secure bootloader/update flag outside application artifacts; blocked by unavailable physical evidence |
| Update rollback / safety net | hardware-dependent | Apollo application update is single-slot with no proven autonomous rollback | `g2/README.md` | no acceptance path defined; requires physical device experiments — blocked by unavailable physical evidence |

## Cross-cutting notes

- The third-party attribution frontier is declared closed: "zero locally
  actionable bounded third-party functional gaps" across all 26 dependency
  families (`research/third-party-dependency-closure-audit.md`,
  `research/third-party-utility-gap-priority.md`). Remaining work is
  first-party source recreation, production admission/placement, and hardware
  validation — not identification. Do not reopen identification rows for
  declared-closed frontiers (CMSIS-FreeRTOS wrapper, mpaland/printf, LVGL
  display port, littlefs leaves, Cordio reusable paths).
- The dominant pattern is "source-identified, production-excluded": many rows
  have exact upstream source or host-tested clean-room candidates in
  `components/apollo_main/core_overlay/` that own zero production bytes. The
  residual work is mechanical but must follow the established admission
  discipline: provider binding, placement, guarded redirects, package
  verification, fail-closed tests, per-closure audit doc.
- The single biggest shared blocker across storage and hardware services is
  the golden external-flash capture (`upstream-inventory.md` priority 1 and
  4): it gates littlefs core/block-port admission, FlashDB production mount,
  and FreeType font-asset recovery. All three stay fail-closed by design
  until that capture exists.
- Fixed-address FreeRTOS global seams (`0x20074A20`–`0x20074A58`) make the
  complete kernel link a single atomic integration event that unblocks
  several platform rows at once.
- Ownership context (`source-coverage.md`): 287,533 B (6.44%) of the package is
  source-compiled or generator-owned; 4,179,797 B (93.56%) remains opaque
  (retained stock bytes functioning in the byte-exact profile). The ledger
  rows above are the documented, bounded part of that remainder; the
  unanchored-census frontier row bounds the rest.
- progress.md's touch summary row predates the completed touch
  identity/memory-map/I2C-protocol closures and should be refreshed when that
  document is next updated.

## Safe resume prerequisites for hardware rows

Work on `hardware-dependent` rows may resume when the owner supplies or
connects, at minimum:

1. an owned G2 unit (and, for case/touch rows, the matching case) plus an
   authorized debug/readback path capable of exact flash read-back;
2. a pre-install per-device state backup accepted before any flash operation;
3. capture tooling appropriate to the row: BLE traffic capture, logic
   analyzer, power-rail instrumentation, golden external-flash capture; and
4. explicit owner authorization for any install, given the single-slot update
   path with no proven autonomous rollback.

No mass erase or flash operation is authorized by this document.

## Production-routing re-pin checklist (learned 2026-08-18)

Routing one candidate into the Apollo overlay changes shared aggregates that
are pinned across the whole test fleet, not just in the candidate's own
focused tests. A closure is not done until ALL of these are advanced
consistently (values below are the post-nvdb_sensor_caldata state):

1. `components/apollo_main/core_overlay/overlay.json`: leaf entries,
   `functions`, `patch_sites`, and `expected` (apple-clang overlay
   144,966 / component 3,668,362; linux-clang profile where applicable).
2. `manifests/g2-2.2.6.10-core-source.json`: region pins, provider
   size/SHA-256, package size/SHA-256 (4,446,856 / `e709d945…`).
3. `third_party/littlefs/verify_snapshot.py`: `aggregate_pins` and
   `EXPECTED_TAG_ID_MANIFEST_PROVIDERS` (it pins the whole-overlay expected
   block, not only littlefs leaves).
4. Fleet-wide whole-overlay aggregate pins in ~65 `tests/test_*.py` modules:
   overlay/component/package sizes and SHA-256 (watch BOTH `3_668_362`
   underscore and `3668362` plain forms, and 64-hex hashes stored as full
   strings or 32-char split halves).
5. Overlay accounting dicts: `source_owned_bytes`, `generated_patch_site_bytes`,
   `opaque_base_bytes`, `replaced_stock_function_bytes` move together
   (source +N, patch-site/replaced +stock-bytes, opaque −stock-bytes).
6. `current_layout_rollback_sha256` (test_runtime_littlefs_disk_version_parts).
7. Tail-arithmetic comments of the form "all later admissions through …"
   in accounting tests — extend the term, don't just change the number.
8. `PROVENANCE_SHA256` pins when a `third_party/<family>/PROVENANCE.json`
   changes; confirm direction against the live file hash before propagating
   (a stale pin in one module is not evidence of the correct value).
9. Pinned docs (`source-coverage.md` etc.) require matching updates to
   `test_runtime_nanopb_decode_svarint_production.py` /
   `test_runtime_nanopb_decode_varint32_production.py`.
10. Docs: audit-doc append, `EVIDENCE.md` entry, README + progress narrative.

Verification order: candidate + analyzer focused tests → the six
littlefs-family modules (fastest aggregate-pin detectors) →
`test_core_overlay` → full `./make.sh test` with NO concurrent tree edits.
