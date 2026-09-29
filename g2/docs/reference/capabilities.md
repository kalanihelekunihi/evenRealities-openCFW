# G2 firmware capability checklist (s200_v2.2.6.10)

Coverage aid for pseudocode review. Derived from the domain rows of the legacy
`g2/docs/functional-capability-ledger.md` (status date 2026-09-04) with all
status, ownership, build and acceptance-gate columns removed. A row means "the
stock firmware contains this capability"; it says nothing about how far its
pseudocode has progressed.

Columns:

- **Payload**: `apollo_main` (run base `0x00438000`), `bootloader`
  (`0x00410000`), `ble_em9305` (`0x00300000`), `codec` (GX8002 package),
  `touch` (payload offsets; linked address = offset + `0x3300`), `case`
  (`0x08000000`).
- **Stock interval / key entries**: the authenticated object interval
  `[start,end)` or the most useful entry addresses; blank means the capability
  is spread over several objects (use `symbols/<payload>.tsv` by module).
- **Legacy evidence**: the research document that bounded it (paths relative to
  `g2/docs/`; recoverable from git history).

Two ledger rows describe project additions rather than stock behavior and are
omitted: the ring-gesture forwarding overlay and the source-built secure-OTA
descriptor helper replacement (the stock descriptor routine itself is listed
under Security).

## Protocol

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| Cordio ATT server CSF (`atts_csf`) | apollo_main | `[0x0052C6C0,0x0052DA0C)` | `research/cordio-atts-csf-source-recovery.md` |
| Cordio ATT server CCC (`atts_ccc`) | apollo_main | `[0x0052BB64,0x0052C6C0)` | `research/cordio-atts-ccc-source-recovery.md` |
| Cordio ATT server write processors (`atts_write`) | apollo_main | `[0x005A5D94,0x005A6260)` | `research/cordio-atts-write-source-recovery.md` |
| Cordio ATT common server processors (`atts_proc`; peer MTU floor 247) | apollo_main | `[0x0056C550,0x0056CDC0)` | `research/cordio-atts-proc-source-recovery.md` |
| Cordio ATT server indication/notification (`atts_ind`) | apollo_main | `[0x005338AC,0x00533EF4)` | `research/cordio-atts-ind-source-recovery.md` |
| Cordio ATT optional server read processors (`atts_read`) | apollo_main | `[0x0056D93C,0x0056E4F8)` | `research/cordio-atts-read-source-recovery.md` |
| Cordio ATT server owner/dispatcher (`atts_main`) | apollo_main | `[0x0053498C,0x00535488)` | `research/cordio-atts-main-source-recovery.md` |
| Cordio ATT client optional writes (`attc_write`) | apollo_main | `[0x00539DCC,0x00539E48)` | `research/cordio-attc-write-source-recovery.md` |
| Cordio ATT client optional reads (`attc_read`) | apollo_main | `[0x0056C3B0,0x0056C550)` | `research/cordio-attc-read-source-recovery.md` |
| Cordio ATT client PDU processor (`attc_proc`) | apollo_main | `[0x004B5230,0x004B59C0)` | `research/cordio-attc-proc-source-recovery.md` |
| Cordio ATT client core (`attc_main`) | apollo_main | `[0x00530D74,0x00531BD4)` | `research/cordio-attc-main-source-recovery.md` |
| Cordio ATT client discovery (`attc_disc`) | apollo_main | `[0x0056B7EC,0x0056C3B0)` | `research/cordio-attc-disc-source-recovery.md` |
| Cordio L2CAP main/master/slave (20 linked definitions; CoC dead-stripped) | apollo_main | `0x00530538`..`0x00537278` (several objects) | `research/cordio-l2c-*-source-recovery.md`, `research/cordio-l2c-coc-exclusion.md` |
| Cordio DM common advertising (`dm_adv`) | apollo_main | `[0x004B3098,0x004B32CA)` | `research/cordio-dm-adv-source-recovery.md` |
| Cordio DM legacy advertising (`dm_adv_leg`) | apollo_main | `[0x004B9A80,0x004BAC4E)` | `research/cordio-dm-adv-leg-source-recovery.md` |
| Cordio DM connection state machine (`dm_conn_sm`) | apollo_main | `[0x00533EF4,0x00534532)` | `research/cordio-dm-conn-sm-source-recovery.md` |
| Cordio DM local-device management (`dm_dev`) | apollo_main | `[0x004B2DF8,0x004B3098)` | `research/cordio-dm-dev-source-recovery.md` |
| Cordio DM main router (`dm_main`) | apollo_main | `[0x004D299C,0x004D2B98)` | `research/cordio-dm-main-source-recovery.md` |
| Cordio DM PHY manager (`dm_phy`) | apollo_main | `[0x004C5734,0x004C5874)` | `research/cordio-dm-phy-source-recovery.md` |
| Cordio DM legacy-master connection (`dm_conn_master_leg`) | apollo_main | `[0x00536A28,0x00536AC8)` | `research/cordio-dm-conn-master-leg-source-recovery.md` |
| Cordio DM legacy-slave connection (`dm_conn_slave_leg`) | apollo_main | `[0x00536AC8,0x00536B40)` | `research/cordio-dm-conn-slave-leg-source-recovery.md` |
| Cordio DM slave connection updates (`dm_conn_slave`) | apollo_main | `[0x0056E4F8,0x0056E5CC)` | `research/cordio-dm-conn-slave-source-recovery.md` |
| Cordio DM master connection updates (`dm_conn_master`) | apollo_main | `[0x0055BC5C,0x0055BCE8)` | `research/cordio-dm-conn-master-source-recovery.md` |
| Cordio optional device privacy (`dm_dev_priv`) | apollo_main | dead-stripped; data reference only | `research/cordio-dm-dev-priv-exclusion.md` |
| Cordio DM privacy manager (`dm_priv`) | apollo_main | `[0x004D254C,0x004D293C)` | `research/cordio-dm-priv-source-recovery.md` |
| Cordio DM connection manager (`dm_conn`) | apollo_main | `[0x004B5B24,0x004B7426)` | `research/cordio-dm-conn-source-recovery.md` |
| Cordio WSF: timer, buffer/message, OS/queue, assert/trace, `wstr` (43 functions) | apollo_main | WSF `0x0052A3FC`..`0x00569ADE`; msg `[0x004BF990,0x004BFA0E)`; wstr `[0x0056D8C4,0x0056D93A)` | `research/cordio-wstr-source-recovery.md`, WSF audits |
| Cordio HCI layer + Ambiq HCI driver + vendor reset/NVDS chain | apollo_main | driver `[0x004B48A6,0x004B4D2C)`; transport `[0x0053013C,0x00530364)`; VS reset `[0x00569B04,0x00569D4C)` | `research/cordio-hci-*-source-recovery.md`, `research/cordio-hci-vs-reset-sequence-recovery.md` |
| Packetcraft GATT profile object (`gatt_main.c`) | apollo_main | `[0x004B59C0,0x004B5B24)` | `research/cordio-gatt-profile-source-recovery.md` |
| AmbiqSuite ANCC profile (12 Ambiq + 9 G2-local functions) | apollo_main | `[0x004BEA04,0x004BF990)` | `research/ambiqsuite-ancc-profile-source-recovery.md` |
| AmbiqSuite app framework + G2 pairing/privacy/connection/UI delta (61 functions) | apollo_main | spread `0x004B2A04`..`0x0050345E` | `research/ambiqsuite-cordio-app-framework-source-recovery.md` |
| Product BLE startup (`app_ble.c`: callbacks, `bleProcMsg`, `_bleCommHandler`, `_bleExactleStackInit`) | apollo_main | `[0x004B7478,0x004B8122)` | `research/g2-app-ble-startup-recovery.md` |
| BLE peripheral policy (`app_ble_peripheral.c`, 31 functions) | apollo_main | `[0x0046DB04,0x0046F4A4)` | `research/g2-app-ble-peripheral-recovery.md` |
| BLE central / RingLink policy (`app_ble_central.c`, 44 functions) | apollo_main | `[0x0049F828,0x004A35B0)` | `research/g2-app-ble-central-recovery.md` |
| BLE discovery policy (`APP_StartServiceDiscovery`, `APP_BleServerDiscCback`) | apollo_main | 3,724-byte object | `research/g2-app-ble-discovery-recovery.md` |
| BLE connection parameters (`app_connect_params.c`, 14 functions) | apollo_main | `[0x00476CBC,0x004787A4)` | `research/g2-app-connect-params-recovery.md` |
| BLE message TX/RX threads (`ble_msgtx`, `ble_msgrx`) | apollo_main | TX `[0x00475290,0x00475FC0)`; RX `[0x0048EDB0,0x0048F3A4)` | `research/g2-thread-ble-message-recovery.md` |
| Even BLE services EUS/ESS/EFS/NUS (Cordio provider adapters, 25 functions) | apollo_main | `[0x004BDE4C,0x004BEA04)` | `research/g2-ble-transport-profiles-recovery.md` |
| Even OTA BLE profile (AMOTA skeleton + 3 G2-local actions) | apollo_main | `[0x004BDB90,0x004BDE4C)` | `research/g2-ble-ota-ring-profiles-recovery.md` |
| Ring BLE profile (ring client, CCC schedule) | apollo_main | `[0x004C46C0,0x004C4CEC)` | `research/g2-ble-ota-ring-profiles-recovery.md` |
| Glasses-case protobuf service (`0x81`) | apollo_main | `[0x00510A0C,0x00510FD8)` | `research/g2-pb-service-glasses-case-recovery.md` |
| Conversate protobuf service (`0x0B`) | apollo_main | `[0x005B1B4C,0x005B22BC)` | `research/g2-pb-service-conversate-recovery.md` |
| Teleprompt protobuf service (`0x06`) | apollo_main | `[0x005885B4,0x00588D74)` | `research/g2-pb-service-teleprompt-recovery.md` |
| Even-AI protobuf service (`0x07`) | apollo_main | `[0x004E31CC,0x004E54C8)` | `research/g2-pb-service-even-ai-recovery.md` |
| Terminal protobuf service (`0x30`) | apollo_main | `[0x005CE7C4,0x005CF2B4)` | `research/g2-pb-service-terminal-recovery.md` |
| Translate protobuf service (`0x05`) | apollo_main | `[0x0059F53C,0x0059FAE0)` | `research/g2-pb-service-translate-recovery.md` |
| Device-config protobuf service (`0x80`) | apollo_main | `[0x004D83D8,0x004D8F4C)` | `research/g2-pb-service-dev-config-recovery.md` |
| Onboarding protobuf service (`0x10`) | apollo_main | `[0x004A78D0,0x004A8560)` | `research/g2-pb-service-onboarding-recovery.md` |
| Notification protobuf service (`0x04`) | apollo_main | `[0x004D6BA8,0x004D798C)` | `research/g2-pb-service-notification-recovery.md` |
| Setting protobuf service (`0x09`) | apollo_main | `[0x0049B198,0x0049C070)` | `research/g2-pb-service-setting-recovery.md` |
| Device-setting protobuf service (`0x80`) | apollo_main | `[0x00542DC4,0x00543C48)` | `research/g2-pb-service-dev-setting-recovery.md` |
| Quicklist protobuf service (`0x0C`) | apollo_main | `[0x0055894C,0x005597F0)` | `research/g2-pb-service-quicklist-recovery.md` |
| Pair-manager protobuf service (`0x80`) | apollo_main | `[0x004BB3DC,0x004BD054)` | `research/g2-pb-service-pair-mgr-recovery.md` |
| Ring protobuf relay service (`0x91`) | apollo_main | `[0x005CE1DC,0x005CE7C4)` | `research/g2-pb-service-ring-recovery.md` |
| Health protobuf service (`0x0E`) | apollo_main | see Health | `research/g2-pb-service-health-recovery.md` |
| nanopb runtime (0.4.9-compatible) | apollo_main | from `0x0048F3A4` | `research/g2-thread-ble-message-recovery.md`, nanopb audits |
| Multipart transport (`transport_protocol.c`, `0xAA` framing; `TPL_Init` `0x004B892C`, `TPL_ReceivePacket` `0x004B910C`, `TPL_SendPacket` `0x004B9640`) | apollo_main | `[0x004B892C,0x004B9A80)`; CRC-16/CCITT leaf `0x0049ACD4` | `research/g2-transport-protocol-recovery.md` |
| TinyFrame dual-glasses sync transport (31 functions) | apollo_main | core `[0x004916C8,0x004922F6)`; `TF_AcceptChar` `0x00491BE4` | `research/tinyframe-*-audit.md` |
| UART sync worker (`uart_sync.c`) | apollo_main | `[0x00541790,0x00541AF8)` | `research/g2-uart-sync-recovery.md` |
| Sync framework / interface API / sync info | apollo_main | `[0x0045A578,0x0045EC7C)`; `[0x004646F0,0x00466010)`; `[0x00471EE8,0x00472244)` | `research/g2-sync-*.md` |
| `AT^NUS` command handler | apollo_main | `[0x005A5520,0x005A5530)` | `research/g2-at-nus-recovery.md` |
| eAT core (`AT_CoreInit`, `AT_Handler`) and command registry (21 records) | apollo_main | `[0x005412E0,0x005415B4)`; table `[0x006C9260,0x006C93B0)` | `research/g2-at-core-recovery.md`, `research/g2-eat-registry-recovery.md` |
| OTA service (`ota_service.c`: frame dispatch, flash backends, FS heal, 25 functions) | apollo_main | `[0x004448F4,0x004488EC)` | `research/g2-ota-service-recovery.md` |
| OTA transport (`ota_transport.c`) | apollo_main | `[0x0048D8D8,0x0048E1CC)` | `research/g2-ota-transport-dependency-boundary.md` |
| EFS transport (`efs_transport.c`) | apollo_main | `[0x004D0D80,0x004D15E8)` | `research/g2-efs-transport-dependency-boundary.md` |
| EFS file service (import/export over BLE, 12 functions) | apollo_main | `[0x00456722,0x00458DF0)` | `research/g2-efs-service-recovery.md` |
| Product-test protocol (`pt_protocol_procsr.c`, 66-command dispatcher at `0x0056F4A0`) | apollo_main | `[0x0056F178,0x00577C3C)` | `research/g2-pt-protocol-procsr-dependency-boundary.md` |
| BLE production-test thread (`5A A5 7F` framing) | apollo_main | `[0x005382E4,0x00538C24)` | `research/g2-thread-ble-production-dependency-boundary.md` |
| Touch-controller I2C protocol (device side: 1..16-byte RX, commands 0..8, 16-byte reports, attention line) | touch | slave init `0x0378`; IRQ/dispatch `[0x0400,0x05A0)`; report builder `0x0824` | `research/g2-touch-i2c-protocol-recovery.md` |
| Touch command dispatch table (9 slots) | touch | payload `0x7DC4` (linked `0xB0C4`) | `research/g2-touch-relocated-vector-and-code-partition.md` |
| Touch device-side DFU engine (`0x38`-family) and boot-vector management | touch | not in the shipped payload; entered via mailbox `0x20000000` + reset (`0x4B14`) | `research/g2-touch-i2c-protocol-recovery.md` |
| Touch gesture/calibration internals, ACT/ALR/WOT power state machine | touch | MSC loop `0x36C0`..`0x376C`; power `[0x703A,0x70A4)` | `research/g2-touch-sensing-source-closure.md` |
| Touch host-side DFU (`service_touch_dfu.c`, 32 functions) | apollo_main | `[0x0055FCB4,0x00561810)` | `research/g2-service-touch-dfu-recovery.md` |
| Glasses<->case UART protocol, glasses side (`box_uart_mgr.c`) | apollo_main | `[0x00539E92,0x0053A414)` | `research/g2-box-uart-mgr-recovery.md` |
| Case-side UART/update protocol (`5A A5 FF` frames, dual-bank OTA) | case | frame check `0x08001E94`; image sum `0x08002CC0`; packers `0x08008FA8`, `0x08009004` | `research/g2-box-function-map-recovery.md`, `research/g2-case-uart-update-source-closure.md` |
| Charging-case firmware remainder (STM32G0, 222 functions) | case | `[0x08000000,0x0800D9C8)` | `research/g2-box-function-map-recovery.md`, `research/g2-case-final-classification.md` |
| Case battery/charging/thermal policy, bit-banged PMIC/charger/watchdog, `nSWAP_BANK` flow | case | log/code evidence only | `research/g2-box-stm32g0-platform-recovery.md` |
| EM9305 BLE controller application (Packetcraft LL/BB/PAL + EM HAL; MetaWare T-2022.09 `-Os`) | ble_em9305 | app record `[0x00302400,0x00335BC8)`; entry `0x00302028` | `research/em9305-expanded-sdk-archive-census.md` |
| EM9305 residual segments (175 segments / 33,658 B) and vendor-modified controller clusters | ble_em9305 | e.g. slave connection `[0x00329888,0x0032A4BE)`, master connection `[0x0031DFD0,0x0031E5EC)`, PAwR `[0x00321C30,0x0032233C)` | `research/em9305-residual-segment-census.md`, `research/em9305-controller-cluster-recovery.md` |
| EM9305 QP/C 6.5.1 RTEF (QF/QK, hook table) | ble_em9305 | `[0x00310D18,0x003117EC)`; QK port `[0x00302518,0x00302664)`; hooks `[0x00335B94,0x00335BB8)` | `research/em9305-qpc-arcompact-audit.md` |
| EM9305 record-table image (4 records) | ble_em9305 | `0x00300000`, `0x00300400`, `0x00302000` (FHDR), `0x00302400` | `memory-map.md` |
| EM9305 vendor libs (PML, sleep manager/timer, protocol timer, unitimer; 98 exact functions) | ble_em9305 | e.g. `SLEEP_MANAGER_GoToSleep` `[0x003126E0,0x003128E4)`; `ProtTimer_*` `0x00310BE0`.. | `research/em9305-sdk-archive-match-audit.md` |

## Security

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| Apollo510 secure-OTA descriptor addition routine (86 B) | apollo_main | see `memory-map.md` | `source-coverage.md`, `memory-map.md` |
| SMP core (`smp_main.c`) | apollo_main | `[0x00537278,0x00537EEC)` | `research/cordio-smp-main-source-recovery.md` |
| SMP database (`smp_db.c`, failure count/backoff) | apollo_main | `[0x00541E34,0x005429F2)` | `research/cordio-smp-db-source-recovery.md` |
| SMP Secure Connections main (`smp_sc_main.c`) | apollo_main | `[0x0056CDC0,0x0056D8C4)` | `research/cordio-smp-sc-main-source-recovery.md` |
| SMP common actions (`smp_act.c`) | apollo_main | `[0x0056E5CC,0x0056F178)` | `research/cordio-smp-act-source-recovery.md` |
| SMP shared Secure Connections actions (`smp_sc_act.c`) | apollo_main | `[0x005E267C,0x005E3118)` | `research/cordio-smp-sc-act-source-recovery.md` |
| SMP Secure Connections state machines and role actions | apollo_main | `[0x00537F14,0x005380DC)` + role action objects | `research/cordio-smp-sc-state-machines-source-recovery.md`, `research/cordio-smpi-sc-act-source-recovery.md`, `research/cordio-smpr-sc-act-source-recovery.md` |
| SMP legacy initiator/responder role actions | apollo_main | `[0x005E3118,0x005E3474)` | `research/cordio-smpi-act-source-recovery.md`, `research/cordio-smpr-act-source-recovery.md` |
| SMP legacy initiator/responder state machines | apollo_main | `[0x00537EEC,0x00537F02)` | `research/cordio-smp-legacy-state-machines-source-recovery.md` |
| DM LE Secure Connections (`dm_sec_lesc.c`) | apollo_main | `[0x00534894,0x0053498C)` | `research/cordio-dm-sec-lesc-source-recovery.md` |
| DM security core (`dm_sec.c`) | apollo_main | `[0x004D2364,0x004D254C)` | `research/cordio-dm-sec-source-recovery.md` |
| DM security role modules (`dm_sec_slave.c`, `dm_sec_master.c`) | apollo_main | `[0x0052BACC,0x0052BB64)` | `research/cordio-dm-sec-slave-source-recovery.md`, `research/cordio-dm-sec-master-source-recovery.md` |
| App-level pairing/privacy/bonding policy (bond lookup, resolving list, address resolution, DB hash) | apollo_main | within app framework | `research/ambiqsuite-cordio-app-framework-source-recovery.md` |
| App BLE peer manager (`findConnIdByAddr`, `AppBleMasterPeerMgrUnpairDev`) | apollo_main | `[0x004D8F4C,0x004D914C)` | `research/g2-app-ble-peer-manager-recovery.md` |
| Cordio security API / crypto-service boundary (`sec_api`) | apollo_main | `[0x00536234,0x005367D2)` | `research/cordio-sec-api-source-recovery.md` |
| Ambiq secure bootloader / secure-boot chain | (ROM) | `0x00400000`..`0x00410000`, absent from EVENOTA | `memory-map.md` |

## Platform

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| Notification thread (`thread_notification.c`) | apollo_main | `[0x0048E154,0x0048E484)` | `research/g2-thread-notification-recovery.md` |
| FreeRTOS V10.5.1 kernel config/port (G2 TCB patch 112 B, BASEPRI `0x30`, 1,024 Hz STIMER tick, CM55_NTZ) | apollo_main | globals `0x20074A20`..`0x20074A58` | `research/freertos-g2-config-port-audit.md` |
| FreeRTOS list primitives | apollo_main | `[0x0045607C,0x0045610E)` | `upstream-inventory.md` |
| FreeRTOS queue/mutex/semaphore subset (creators, send, take, delete, ISR paths) | apollo_main | e.g. `[0x00441A42,0x00441B0A)`; `vQueueDelete` `0x00441EA2` | `research/freertos-queue-next-closure-audit.md` |
| FreeRTOS task/scheduler-state leaves | apollo_main | e.g. `xTaskGetTickCount` `0x00454EFE` | `research/freertos-task-next-closure-audit.md` |
| FreeRTOS `heap_4` adapter | apollo_main | `[0x00456110,0x00456338)` | `upstream-inventory.md` |
| FreeRTOS scheduler cluster (yield, critical sections, increment tick, resume all) | apollo_main | from `0x004420BC` | `research/freertos-scheduler-cluster-production-promotion-plan.md` |
| FreeRTOS CM55_NTZ port assembly (7 leaves) | apollo_main | `[0x005FA058,0x005FA132)` | `upstream-inventory.md` |
| FreeRTOS scheduler start (`vTaskStartScheduler`, `xPortStartScheduler`, `vTaskSwitchContext` + G2 trace ring) | apollo_main | from `0x00454CEC` | `research/freertos-task-start-scheduler-source-candidate-audit.md` |
| FreeRTOS Apollo STIMER tick / tickless idle with power hooks | apollo_main | tickless `[0x00456498,0x0045655C)` | `research/freertos-apollo-stimer-setup-source-candidate-audit.md`, `research/freertos-apollo-stimer-tick-source-candidate-audit.md` |
| FreeRTOS task/queue private functions (`vTaskPlaceOnEventList`, `xQueueGenericReset`, `vTaskGetInfo`) | apollo_main | several | `research/freertos-queue-next-closure-audit.md` |
| CMSIS-FreeRTOS v10.5.1 wrapper (43 functions) | apollo_main | `[0x0044900E,0x00449ED2)` | `research/cmsis-freertos-linked-function-census.md` |
| AmbiqSuite 5.1.0 HAL leaves (MSPI, SPOT, MCUCTRL, oscillators, trim; I2S) | apollo_main | I2S `0x0059005E`..`0x00590C62` | `upstream-inventory.md`, `research/g2-drv-gx8002b-recovery.md` |
| Product RTOS task vote, Apollo510 sleep/watchdog hooks | apollo_main | `[0x0046D67C,0x0046D8A0)` | `research/g2-product-rtos-recovery.md` |
| Ambiq GPU patch exports (11 Nema patch functions) | apollo_main | 4,232 B GPU-patch section | `research/nemagfx-ambiq-g2-provenance-audit.md` |
| Nema bare-metal HAL (18 functions) | apollo_main | `[0x00513F34,0x0051419A)` | `research/ambiq-nema-bare-metal-hal-source-candidate-audit.md` |
| IAR DLIB runtime (memory, math/errno, 13 code units) | apollo_main | e.g. `memcpy` `0x00439BE4` | `research/iar-dlib-runtime-census.md` |
| IAR DLIB formatted I/O (printf/scanf cores, `scanf_s`, constraint handler) | apollo_main | several | `research/g2-iar-dlib-format-io-recovery.md` |
| CmBacktrace fault handler | apollo_main | `[0x005944BC,0x005947CE)` | `research/cmbacktrace-fault-source-closure.md` |
| Even bootloader: platform bring-up, clocks (SYSPLL/CLKGEN/HFADJ), pin groups, littlefs, EasyLogger transport | bootloader | image `[0x00410000,0x00434477)`; bring-up `0x00430000` | `research/g2-bootloader-platform-bringup-430000-source-closure.md`, `memory-map.md` |
| Even bootloader: per-instance hardware initializer | bootloader | `[0x0042308E,0x004232C8)` | `research/g2-bootloader-hw-initializer-42308e-4232c8-source-closure.md` |
| Even bootloader: MSPI device configuration | bootloader | `[0x00424120,0x0042488E)` | `research/g2-bootloader-mspi-device-configure-424120-42488e-source-closure.md` |
| Even bootloader: MSPI PIO-mixed configuration | bootloader | `[0x0042488E,0x00424976)` | `research/g2-bootloader-mspi-piomixed-configure-42488e-424976-source-closure.md` |
| Even bootloader: MSPI handle initializer | bootloader | `[0x00424A5A,0x00424AEA)` | `research/g2-bootloader-mspi-initialize-424a5a-424aea-source-closure.md` |
| Even bootloader: MSPI controller configure (`am_hal_mspi_configure`) | bootloader | `[0x00424AF0,0x00424BD4)` | `research/g2-bootloader-mspi-configure-424af0-424bd4-source-closure.md` |
| Even bootloader: public MSPI device configure | bootloader | `[0x00424BE4,0x00425066)` | `research/g2-bootloader-mspi-device-configure-public-424be4-425066-source-closure.md` |
| Even bootloader: MSPI control | bootloader | `[0x004251C0,0x004262E0)` | `research/g2-bootloader-mspi-control-4251c0-4262e0-source-closure.md` |
| Even bootloader: DFU service task, image CRC check, payload programmer, vector handoff to `0x00438000` | bootloader | `[0x0042DE58,0x0042E104)`, `[0x0042D890,0x0042D9F0)`, `[0x0042DAE8,0x0042DC90)` | `research/g2-bootloader-dfu-*-source-closure.md` |
| Ambiq secure bootloader | (ROM) | `0x00400000`..`0x00410000` | `memory-map.md` |

## Health

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| Health mutex + common-event handler (`health.c`) | apollo_main | `[0x004FFBD8,0x004FFE14)` | `research/g2-health-recovery.md` |
| Health data manager (`health_data_manager.c`) | apollo_main | `[0x005597F0,0x0055A350)` | `research/g2-health-data-manager-dependency-boundary.md` |
| Health protobuf service (`pb_service_health.c`, `0x0E`) | apollo_main | `[0x0055A558,0x0055B2A4)` | `research/g2-pb-service-health-recovery.md` |
| Health UI page (`ui_health_page.c`) | apollo_main | `[0x004FB1FA,0x004FD940)` | `research/g2-ui-health-page-dependency-boundary.md` |
| Health-metric algorithms | apollo_main | provider not bounded on the G2 side (documentation gap) | `functional-capability-ledger.md` |

## System

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| Startup/init sequencing (power, clock, RTC, SPOT, low-power, display-subsystem initializers; startup app-ID policy; onboarding gate); startup entry `0x005CE01E` -> initializer table `0x005BF0BC` | apollo_main | see `s200_config_main.c` | `hardware-validation-2026-08-23.md`, `source-coverage.md` |
| Product startup/main thread (`s200_config_main.c`) | apollo_main | `[0x005CDB46,0x005CE140)` | `research/g2-s200-config-main-recovery.md` |
| S200 board-dependent charger init (`board_config.c`, record 3, families 1/2) | apollo_main | `[0x005093D0,0x0050968C)` | `research/g2-s200-board-config-recovery.md` |
| SystemAlert UI (`systemAlert.c`) | apollo_main | `[0x004D2B9A,0x004D34C4)` | `research/g2-system-alert-recovery.md` |
| SystemClose UI (`systemClose.c`) | apollo_main | `[0x00469BF4,0x0046B0EC)` | `research/g2-system-close-dependency-boundary.md` |
| System monitor peer-reboot callback (`system_monitor.c`) | apollo_main | `[0x00584EE4,0x00585134)` | `research/g2-system-monitor-recovery.md` |
| Charge and message-count callback facades (`cb_charge.c`, `cb_msg_notif.c`) | apollo_main | `[0x004AEA40,0x004AEB20)` | `research/g2-callback-facades-recovery.md` |
| Generic callback manager (`callback_manager.c`) | apollo_main | `[0x005100A0,0x005105F0)` | `research/g2-callback-manager-recovery.md` |
| Ring-battery callback facade (`cb_ring_battery.c`) | apollo_main | `[0x00500378,0x00500410)` | `research/g2-cb-ring-battery-recovery.md` |
| BLE-status callback facade (`cb_ble_status.c`) | apollo_main | `[0x004ABCC6,0x004ABD90)` | `research/g2-cb-ble-status-recovery.md` |
| Quicklist data manager | apollo_main | `[0x0058D51C,0x0058D668)` | `research/g2-quicklist-data-manager-recovery.md` |
| Audio service algorithm (`service_algo.c`) | apollo_main | `[0x005915DC,0x00591D14)` | `research/g2-service-algo-recovery.md` |
| EvenAI common/heartbeat timer manager | apollo_main | `[0x004E2E10,0x004E31CC)` | `research/g2-even-ai-timer-recovery.md` |
| Teleprompt file-list store | apollo_main | `[0x0058BCE0,0x0058BDA8)` | `research/g2-teleprompt-file-list-recovery.md` |
| Legal/regulatory event handler | apollo_main | `[0x005BF7B8,0x005BF964)` | `research/g2-legal-regulatory-recovery.md` |
| Calendar/RTC and peer time service (`service_time.c`) | apollo_main | `[0x00449ED4,0x0044A43C)` | `research/g2-service-time-recovery.md` |
| UX system-status sync (peer OTA/BLE/ring status, `ux_system.c`) | apollo_main | `[0x0047CE90,0x0047D9C4)` | `research/g2-ux-system-recovery.md` |
| Watchdog driver | apollo_main | `[0x0052F2E0,0x0052F38C)` | `research/g2-watchdog-recovery.md` |
| Firmware event loop | apollo_main | `[0x004764E0,0x00476BF0)` | function map `g2-fw-event-loop` |
| Unanchored first-party remainder (1,911 functions / 299,736 body bytes without retained-path anchors) | apollo_main | census in `tools/manifests/g2-apollo-unanchored-census-functions.tsv` | `research/g2-apollo-unanchored-census.md` |

## Storage

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| littlefs v2.10.1 (30 main + 26 bootloader leaves; full core) | apollo_main, bootloader | main leaves from `0x004CA6F8`; bootloader `0x00410400`.. | `research/littlefs-next-closed-leaves-audit.md`, `memory-map.md` |
| littlefs G2 block port / MSPI transport (MX25U25643G 32 MiB external flash) | apollo_main | flash driver `0x0046F4A4`..`0x004710A2` | `research/littlefs-g2-block-port-audit.md`, `research/littlefs-g2-mspi-transport-audit.md` |
| FlashDB 2.1.1 KVDB/FAL (`kvdb@0x01FC0000/0x38000`, `NVdb@0x01FF8000/0x8000`) | apollo_main | from `0x00544000` | `research/flashdb-configuration-recovery-audit.md` |
| G2 KVDB objects (setting, time, time format, temperature unit, universal setting, ALS scale, terminal mode, onboarding config, ring, module configure) | apollo_main | several (`g2-kvdb-*` modules) | per-object `research/g2-kvdb-*-recovery.md` |
| G2 KVDB system service (`kvbooCount` lifecycle, 11 migrations) | apollo_main | `[0x004D9530,0x004D9B34)` | `research/g2-service-kvdb-recovery.md` |
| G2 NVDB objects (adv magic, buzzer, MAC, product mode, sensor caldata, sys dt) + `service_nvdb.c` core | apollo_main | core `0x005105F0`..`0x00510992` | `research/g2-service-nvdb-recovery.md` |
| FreeRTOS+CLI filesystem commands (`prvCommand_filesystem.c`) | apollo_main | `[0x0057E898,0x0057F550)` | `research/g2-freertos-plus-cli-filesystem-recovery.md` |
| File runtime wrappers | apollo_main | `0x00474550`..`0x00474E3C` | function map `g2-file-runtime` |

## Sensors

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| EvenHub IMU enable policy (parser cmd `0x12`) | apollo_main | `[0x004E1406,0x004E1442)` | `memory-map.md` |
| Sensor-hub policy/message routing (`sensor_hub.c`) | apollo_main | `[0x004A6644,0x004A777C)` | `research/g2-sensor-hub-dependency-boundary.md` |
| IMU driver ICM-45608 (FIFO, orientation, quaternion->Euler, tilt/tap/head-up/compass) | apollo_main | `[0x004A35B0,0x004A6644)` | `research/g2-imu-icm45608-recovery.md` |
| ALS driver (`als.c`) | apollo_main | `[0x004AD9B8,0x004AEA40)` | `research/g2-als-dependency-boundary.md` |
| TI OPT3007 register-map initializer | apollo_main | `[0x005135E0,0x00513748)` | `research/g2-opt3007-registers-recovery.md` |
| NVDB sensor-calibration records | apollo_main | `[0x00509764,0x00509B48)` | `research/g2-nvdb-sensor-caldata-recovery.md` |
| KVDB ALS-scale record | apollo_main | `[0x004AECA4,0x004AEE28)` | `research/g2-kvdb-als-scale-recovery.md` |
| eAT sensor/core commands (`AT^INFO/RESET/PSN/IMU_*/SCRN_*/ALS*/BRIGHTNESS*`) | apollo_main | `[0x005A5720,0x005A5984)` | `research/g2-eat-core-sensor-recovery.md` |
| eAT touch-panel command (`AT^TP`) | apollo_main | `[0x005A5984,0x005A5D94)` | `research/g2-at-tp-recovery.md` |
| eAT BLE bond/connect (`AT^CLEANBOND`, `AT^BLE_KEEPCONNECT`) | apollo_main | `[0x005A4FA4,0x005A4FD0)` | `research/g2-eat-bond-connect-recovery.md` |
| eAT buzzer (`_atBuzzerTest`) | apollo_main | `[0x005A4FD0,0x005A5488)` | `research/g2-at-buzzer-recovery.md` |
| eAT filesystem (`AT^RM/LS/MKDIR`) | apollo_main | `[0x005A5530,0x005A5720)` | `research/g2-at-fs-recovery.md` |
| Gesture processor | apollo_main | `[0x00502D56,0x00503298)` | `research/g2-service-gesture-processor-recovery.md` |
| Input manager / input thread | apollo_main | `0x004C5886`..`0x004C6148`; `0x00512C84`..`0x005134B2` | function maps `g2-service-input-manager`, `g2-thread-input` |
| Host touch driver (`drv_cy8c4046fni.c`) | apollo_main | `[0x0055B2EC,0x0055BA70)` | `research/g2-drv-cy8c4046fni-dependency-boundary.md` |
| Touch-controller shipped application (PSoC 4000T CY8C4046FNI, Cortex-M0+) | touch | payload `[0x0000,0x867C)` + CRC at `0x867C`; reset handler payload `0x1374` | `research/g2-touch-identity-recovery.md` |
| Touch configuration/const tables and callback registry | touch | payload `0x7DC4`..`0x8650` (linked `0xB0C4`..) | `research/g2-touch-relocated-vector-and-code-partition.md` |
| Goodix-derived error utility (`util_error_check.c`) | apollo_main | `[0x00509B48,0x00509C1C)` | `research/g2-util-error-check-goodix-recovery.md` |

## Hardware services

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| LVGL Ambiq display port (`lv_ambiq_display.c`, 7 functions) | apollo_main | see LVGL census | `research/lvgl-ambiq-display-port-closure-audit.md` |
| Display pipeline core (display thread, input handler, display-mode state machine, subsystem init) | apollo_main | `[0x0044228A,0x004448F4)` | `research/g2-display-thread-recovery.md` |
| Display driver manager + display state/event helpers | apollo_main | `[0x00473952,0x00474550)` | `research/g2-displaydrv-manager-recovery.md` |
| ULED display drivers (JBD4010, A6NG, MSPI common, manager, preprocess) | apollo_main | preprocess `[0x0046C73C,0x0046C984)` | `research/g2-uled-display-preprocess-recovery.md` |
| Production diagnostic gray screen | apollo_main | `[0x005CF634,0x005CF7A8)` | `research/g2-pdt-gray-screen-recovery.md` |
| Production diagnostic distortion-test screen | apollo_main | `[0x005CF2B4,0x005CF634)` | `research/g2-pdt-distortion-test-recovery.md` |
| LVGL core (v9.3.0-dev Ambiq/Even fork) | apollo_main | census `tools/manifests/g2-lvgl-vendor-fork-census.tsv` | `research/lvgl-version-recovery-audit.md`, `research/lvgl-ambiq-source-abi-recovery-audit.md` |
| NemaGFX 1.4.12 / NemaVG 1.1.8 + Ambiq GPU patch | apollo_main | several | `research/nemagfx-ambiq-g2-provenance-audit.md` |
| FreeType 2.9.1 engine (base, autofit, CFF, psaux, pshinter, psnames, sfnt, smooth, truetype) | apollo_main | autofit from `0x005A6260`; base from `0x005242FC` | `research/freetype-2.9.1-snapshot-audit.md`, `tools/manifests/g2-freetype-*-function-map.json` |
| LVGL font manager + external font assets | apollo_main | `[0x0046CAE0,0x0046D67C)` | `research/g2-lvgl-font-manager-recovery.md` |
| Audio codec/DSP image (GX8002: FWPK, UART boot stages, dual BINH images, KWS NPU payload) | codec | stage1 IRAM `0x10000000`; A SRAM `0x10023400` (entry `0x10023500`); XIP `0x10200000`; B SRAM `0x10003000` | `research/g2-codec-fwpk-segments-recovery.md`, `research/g2-codec-stage2-sections-recovery.md` |
| Codec UART lifecycle (`service_codec_porting`) | apollo_main | `[0x0058FB52,0x0058FCF0)` | `research/g2-service-codec-porting-recovery.md` |
| Codec audio control (`AT^AUDIO`, `_atAudioCtrl`) | apollo_main | `[0x005A5488,0x005A5520)` | `research/g2-at-codec-recovery.md` |
| GX8002B host driver (I2S/DMA, `drv_gx8002b.c`) | apollo_main | `[0x0057A46C,0x0057A900)` | `research/g2-drv-gx8002b-recovery.md` |
| GX8002 codec-host service (`BUXX` commands) | apollo_main | `[0x0057BA88,0x0057DC40)` | `research/g2-service-codec-host-recovery.md` |
| GX8002 codec DFU (`SVC_CodecDfu`, `SVC_CodecCheckAndUpgrade`) | apollo_main | `[0x00577D7C,0x0057A46C)` | `research/g2-service-codec-dfu-recovery.md` |
| Audio service, audio manager, audio thread, PDM mic, LC3 encoder | apollo_main | service `0x0057A900`..; manager `0x0054F364`..; thread `0x0053C2BE`..; PDM `0x0057B704`..; LC3 setup `[0x0059123A,0x00591374)` | `research/g2-service-audio-recovery.md`, `research/g2-liblc3-service-audio-*.md` |
| Touch DFU service (`service_touch_dfu`) | apollo_main | `[0x0055FCB4,0x00561810)` | `research/g2-service-touch-dfu-recovery.md` |
| EM9305 DFU service (`service_em9305_dfu.c`) | apollo_main | `[0x0052F442,0x0052FF4C)` | `research/g2-service-em9305-dfu-recovery.md` |
| Case services (`box_uart_mgr`, box-detect state machine) | apollo_main | `[0x00539E92,0x0053A414)`; box detect `0x004ABEC8`..`0x004ACD46` | `research/g2-box-uart-mgr-recovery.md`, `research/g2-service-box-detect-dependency-boundary.md` |
| Charger services (`charger_common`) | apollo_main | `[0x004ACE10,0x004AD908)` | `research/g2-charger-common-recovery.md` |
| UX battery-sync service-record callback | apollo_main | `[0x005F958C,0x005F98D0)` | `research/g2-ux-battery-sync-recovery.md` |
| Charger drivers BQ25180 / BQ27427; nPMx driver | apollo_main | `[0x0053A670,0x0053AF4C)`; `0x0053AFC0`..`0x0053C1C4`; nPMx `0x00511002`.. | `research/g2-chg-bq25180-recovery.md`, `research/g2-chg-bq27427-recovery.md` |
| Buzzer driver (`DRV_BuzzerPlayNote` `0x00502BF8`, `DRV_BuzzerPlay` `0x00502BF0`) | apollo_main | `0x005026BC`..`0x00502D56` | function map `g2-drv-buzzer` |
| RTC, I2C HAL wrappers | apollo_main | RTC `0x0047EE78`; I2C `0x0050412C`..`0x0050475C` | function maps `g2-drv-rtc`, `g2-hal-i2c` |
| Ring service stack (`ring_service`, `thread_ring`, `ring_connect_policy`, `pb_service_ring`, `service_ring_battery`, `cb_ring_battery`) | apollo_main | `[0x00472244,0x00472C7C)`; thread `0x004C4CEC`..; policy `[0x0049F020,0x0049F828)`; battery `[0x004FF8E4,0x004FFA70)` | `research/g2-ring-service-dependency-boundary.md` and siblings |

## Deployment

| Capability | Payload | Stock interval / key entries | Legacy evidence |
|---|---|---|---|
| EVENOTA container and per-payload wrappers (main 32-B preamble, case `EVEN`, touch/codec `FWPK`, EM9305 record table) | all | container format | `memory-map.md`, `g2/tools/open_cfw.py` |
| Update flag / install handshake (`0x007FE000`) | bootloader, apollo_main | 16-B record | `memory-map.md` |
| Update rollback (single-slot main image; no proven autonomous rollback) | bootloader | - | `functional-capability-ledger.md` |

## Appendix: modules covered by legacy function maps

Every `tools/manifests/*-function-map.tsv` with at least one stock address,
with its function count and address span. Use together with
`symbols/<payload>.tsv` to check that every module has reviewed pseudocode.
Spans may interleave with other modules; they are not exclusive object
bounds.

| Payload | Module (legacy function map) | Functions | First entry | Last end |
|---|---|---:|---|---|
| apollo_main | `g2-aging-test` | 5 | `0x0043C400` | `0x0043C758` |
| apollo_main | `g2-compress-log-core` | 8 | `0x0043C7CC` | `0x0043D0C8` |
| apollo_main | `g2-display-thread` | 27 | `0x0044228A` | `0x0044484C` |
| apollo_main | `g2-ota-service` | 25 | `0x004448F4` | `0x00448844` |
| apollo_main | `cmsis-freertos-v10.5.1-linked` | 43 | `0x0044900E` | `0x00449ED2` |
| apollo_main | `g2-service-time` | 11 | `0x00449ED4` | `0x0044A3F0` |
| apollo_main | `g2-compress-log-port` | 12 | `0x0044A474` | `0x0044A9B4` |
| apollo_main | `g2-efs-service` | 12 | `0x00456722` | `0x00458D34` |
| apollo_main | `g2-logger-setting` | 8 | `0x00458DF0` | `0x0045A462` |
| apollo_main | `g2-sync-framework` | 43 | `0x0045A578` | `0x0045EB76` |
| apollo_main | `g2-page-manager` | 45 | `0x0045EC7C` | `0x0045FE88` |
| apollo_main | `g2-menu-page` | 34 | `0x0046018E` | `0x00463B8E` |
| apollo_main | `g2-generic-animation` | 17 | `0x00463C68` | `0x004642BE` |
| apollo_main | `g2-sync-interface-api` | 13 | `0x004646F0` | `0x00465FA2` |
| apollo_main | `g2-service-universal-setting` | 15 | `0x00466010` | `0x004667EA` |
| apollo_main | `g2-setting` | 18 | `0x0046687C` | `0x00467F02` |
| apollo_main | `g2-onboarding-controller` | 12 | `0x00467FF0` | `0x0046908C` |
| apollo_main | `g2-silent-mode` | 10 | `0x0046916C` | `0x00469B2E` |
| apollo_main | `g2-system-close` | 20 | `0x00469BF4` | `0x0046B004` |
| apollo_main | `g2-service-settings` | 31 | `0x0046B0EC` | `0x0046C64E` |
| apollo_main | `g2-uled-display-preprocess` | 1 | `0x0046C73C` | `0x0046C984` |
| apollo_main | `g2-lvgl-font-manager` | 8 | `0x0046CAE0` | `0x0046D588` |
| apollo_main | `g2-product-rtos` | 13 | `0x0046D67C` | `0x0046D8A0` |
| apollo_main | `g2-app-ble-peripheral` | 31 | `0x0046DB04` | `0x0046F3A2` |
| apollo_main | `g2-drv-mx25u25643g` | 40 | `0x0046F4A4` | `0x004710A2` |
| apollo_main | `g2-general-configure` | 10 | `0x00471164` | `0x00471AC2` |
| apollo_main | `g2-sync-info` | 3 | `0x00471EE8` | `0x004721F4` |
| apollo_main | `g2-ring-service` | 18 | `0x00472244` | `0x00472BB0` |
| apollo_main | `g2-displaydrv-manager` | 19 | `0x00473952` | `0x00474474` |
| apollo_main | `g2-file-runtime` | 18 | `0x00474550` | `0x00474E3C` |
| apollo_main | `g2-thread-ble-message` | 34 | `0x00475290` | `0x0048F324` |
| apollo_main | `g2-fw-event-loop` | 6 | `0x004764E0` | `0x00476BF0` |
| apollo_main | `g2-app-connect-params` | 14 | `0x00476CBC` | `0x004786B4` |
| apollo_main | `g2-ux-system` | 11 | `0x0047CE90` | `0x0047D8FC` |
| apollo_main | `g2-onboarding-data-manager` | 7 | `0x0047E2D0` | `0x0047E60A` |
| apollo_main | `g2-drv-rtc` | 1 | `0x0047EE78` | `0x0047EEFA` |
| apollo_main | `g2-ota-transport` | 3 | `0x0048D8D8` | `0x0048E0AC` |
| apollo_main | `g2-thread-notification` | 12 | `0x0048E154` | `0x0048E42E` |
| apollo_main | `g2-service-android-notify` | 5 | `0x0048E484` | `0x0048E850` |
| apollo_main | `g2-thread-pool` | 3 | `0x0049110C` | `0x00491616` |
| apollo_main | `g2-kvdb-module-configure` | 6 | `0x004922F8` | `0x00492BE6` |
| apollo_main | `g2-evenhub-loading-page` | 4 | `0x00492CB4` | `0x004934FE` |
| apollo_main | `g2-evenhub-ui` | 26 | `0x004935CC` | `0x0049718C` |
| apollo_main | `g2-service-ancc` | 12 | `0x0049729C` | `0x00497D24` |
| apollo_main | `g2-service-even-ai` | 9 | `0x00497DE6` | `0x004985A6` |
| apollo_main | `g2-kvdb-universal-setting` | 3 | `0x0049AD0C` | `0x0049AE60` |
| apollo_main | `g2-kvdb-time-format` | 3 | `0x0049AE90` | `0x0049AFE2` |
| apollo_main | `g2-kvdb-temperature-unit` | 3 | `0x0049B014` | `0x0049B166` |
| apollo_main | `g2-pb-service-setting` | 11 | `0x0049B198` | `0x0049BF98` |
| apollo_main | `g2-dashboard` | 24 | `0x0049C070` | `0x0049EA04` |
| apollo_main | `g2-ux-wear-detect` | 7 | `0x0049EAD8` | `0x0049EFAC` |
| apollo_main | `g2-ring-connect-policy` | 15 | `0x0049F020` | `0x0049F744` |
| apollo_main | `g2-app-ble-central` | 44 | `0x0049F828` | `0x004A34B0` |
| apollo_main | `g2-imu-icm45608` | 53 | `0x004A35B0` | `0x004A656E` |
| apollo_main | `g2-sensor-hub` | 31 | `0x004A6644` | `0x004A774E` |
| apollo_main | `g2-kvdb-onboarding-config` | 6 | `0x004A777C` | `0x004A789A` |
| apollo_main | `g2-pb-service-onboarding` | 9 | `0x004A78D0` | `0x004A84D2` |
| apollo_main | `g2-onboarding-main-page` | 52 | `0x004A8560` | `0x004AAB5E` |
| apollo_main | `g2-cb-ble-status` | 3 | `0x004ABCC6` | `0x004ABD6E` |
| apollo_main | `g2-nvdb-product-mode` | 6 | `0x004ABD90` | `0x004ABE9E` |
| apollo_main | `g2-service-box-detect` | 32 | `0x004ABEC8` | `0x004ACD46` |
| apollo_main | `g2-charger-common` | 14 | `0x004ACE10` | `0x004AD908` |
| apollo_main | `g2-als` | 38 | `0x004AD9B8` | `0x004AE94C` |
| apollo_main | `g2-callback-facades` | 10 | `0x004AEA40` | `0x004E1B06` |
| apollo_main | `g2-kvdb-setting` | 3 | `0x004AEB20` | `0x004AEC74` |
| apollo_main | `g2-kvdb-als-scale` | 3 | `0x004AECA4` | `0x004AEDF6` |
| apollo_main | `g2-nvdb-sys-dt` | 13 | `0x004AEE28` | `0x004B030A` |
| apollo_main | `g2-kvdb-terminal-mode` | 3 | `0x004B03E0` | `0x004B052E` |
| apollo_main | `ambiqsuite-cordio-app-framework` | 14 | `0x004B2A04` | `0x0050345E` |
| apollo_main | `packetcraft-cordio-dm-dev` | 12 | `0x004B2DF8` | `0x004B3096` |
| apollo_main | `packetcraft-cordio-dm-adv` | 9 | `0x004B3098` | `0x004B32CA` |
| apollo_main | `ambiq-cordio-hci-driver` | 12 | `0x004B47AE` | `0x004B4D2C` |
| apollo_main | `packetcraft-cordio-att-main` | 21 | `0x004B4DE0` | `0x004B522E` |
| apollo_main | `packetcraft-cordio-attc-proc` | 15 | `0x004B5230` | `0x004B598C` |
| apollo_main | `packetcraft-cordio-gatt-profile` | 6 | `0x004B59C0` | `0x004B5B24` |
| apollo_main | `packetcraft-cordio-dm-conn` | 57 | `0x004B5B24` | `0x004B7426` |
| apollo_main | `g2-app-ble-startup` | 13 | `0x004B7478` | `0x004B8122` |
| apollo_main | `g2-transport-protocol` | 13 | `0x004B892C` | `0x004B99B6` |
| apollo_main | `packetcraft-cordio-dm-adv-leg` | 17 | `0x004B9A80` | `0x004BAC4E` |
| apollo_main | `g2-pb-service-pair-mgr` | 20 | `0x004BB3DC` | `0x004BCF9C` |
| apollo_main | `g2-ble-ota-ring-profiles` | 14 | `0x004BDB90` | `0x004C4C66` |
| apollo_main | `g2-ble-transport-profiles` | 25 | `0x004BDE4C` | `0x004BE9B0` |
| apollo_main | `ambiqsuite-ancc-profile` | 21 | `0x004BEA04` | `0x004BF8B0` |
| apollo_main | `packetcraft-cordio-wsf-msg` | 7 | `0x004BF990` | `0x004BFA0E` |
| apollo_main | `g2-thread-ring` | 17 | `0x004C4CEC` | `0x004C5632` |
| apollo_main | `packetcraft-cordio-dm-phy` | 6 | `0x004C5734` | `0x004C5868` |
| apollo_main | `g2-service-input-manager` | 10 | `0x004C5886` | `0x004C6148` |
| apollo_main | `g2-device-mgr` | 20 | `0x004C6240` | `0x004C6BF4` |
| apollo_main | `g2-thread-manager` | 17 | `0x004C94C8` | `0x004C9C56` |
| apollo_main | `g2-uled-manager` | 14 | `0x004C9D44` | `0x004CA662` |
| apollo_main | `g2-thread-ble-wsf` | 12 | `0x004D0A4C` | `0x004D0CDC` |
| apollo_main | `g2-efs-transport` | 2 | `0x004D0D80` | `0x004D1546` |
| apollo_main | `packetcraft-cordio-dm-sec` | 8 | `0x004D2364` | `0x004D254C` |
| apollo_main | `packetcraft-cordio-dm-priv` | 21 | `0x004D254C` | `0x004D2920` |
| apollo_main | `packetcraft-cordio-dm-main` | 16 | `0x004D299C` | `0x004D2B98` |
| apollo_main | `g2-system-alert` | 7 | `0x004D2B9A` | `0x004D341A` |
| apollo_main | `g2-service-whitelist` | 7 | `0x004D5930` | `0x004D6AC0` |
| apollo_main | `g2-pb-service-notification` | 9 | `0x004D6BA8` | `0x004D78E8` |
| apollo_main | `g2-json-parser` | 21 | `0x004D798C` | `0x004D83D8` |
| apollo_main | `g2-pb-service-dev-config` | 3 | `0x004D83D8` | `0x004D8EAA` |
| apollo_main | `g2-app-ble-peer-manager` | 4 | `0x004D8F4C` | `0x004D910A` |
| apollo_main | `g2-service-kvdb` | 7 | `0x004D9530` | `0x004D9A98` |
| apollo_main | `g2-evenhub-data-parser` | 19 | `0x004D9B34` | `0x004DC5AE` |
| apollo_main | `g2-common-image-container` | 3 | `0x004DC5AE` | `0x004DCCD6` |
| apollo_main | `g2-common-list-container` | 14 | `0x004DCCD8` | `0x004DEDC2` |
| apollo_main | `g2-common-text-container` | 13 | `0x004DEE64` | `0x004E0B20` |
| apollo_main | `g2-evenhub-main` | 5 | `0x004E0CCE` | `0x004E1956` |
| apollo_main | `g2-message-notify` | 4 | `0x004E1B30` | `0x004E1F28` |
| apollo_main | `g2-even-ai` | 7 | `0x004E1F7C` | `0x004E2D6C` |
| apollo_main | `g2-even-ai-timer` | 13 | `0x004E2E10` | `0x004E31CC` |
| apollo_main | `g2-pb-service-even-ai` | 25 | `0x004E31CC` | `0x004E543A` |
| apollo_main | `g2-ui-even-ai` | 43 | `0x004E54C8` | `0x004E74FA` |
| apollo_main | `g2-dashboard-main-screen` | 31 | `0x004E772C` | `0x004E9CE8` |
| apollo_main | `g2-ui-stock-page` | 34 | `0x004E9DD4` | `0x004ED6E0` |
| apollo_main | `g2-ui-calendar-page` | 15 | `0x004ED7D8` | `0x004EFEE8` |
| apollo_main | `g2-ui-widget-news-page` | 45 | `0x004EFF94` | `0x004F4F5C` |
| apollo_main | `g2-ui-quicklist-page` | 80 | `0x004F5596` | `0x004FB1BE` |
| apollo_main | `g2-ui-health-page` | 12 | `0x004FB1FA` | `0x004FD870` |
| apollo_main | `g2-dashboard-data-process` | 14 | `0x004FE0AA` | `0x004FF850` |
| apollo_main | `g2-service-ring-battery` | 5 | `0x004FF8E4` | `0x004FFA44` |
| apollo_main | `g2-quicklist` | 4 | `0x004FFA70` | `0x004FFBA6` |
| apollo_main | `g2-health` | 4 | `0x004FFBD8` | `0x004FFDD0` |
| apollo_main | `g2-page-state-sync` | 8 | `0x004FFE14` | `0x005002F0` |
| apollo_main | `g2-cb-ring-battery` | 5 | `0x00500378` | `0x005003F2` |
| apollo_main | `g2-dashboard-watchface-manager` | 17 | `0x00500410` | `0x005007CC` |
| apollo_main | `g2-dashboard-ext` | 16 | `0x0050083E` | `0x005025E2` |
| apollo_main | `g2-drv-buzzer` | 17 | `0x005026BC` | `0x00502D56` |
| apollo_main | `g2-service-gesture-processor` | 5 | `0x00502D56` | `0x00503230` |
| apollo_main | `g2-hal-i2c` | 9 | `0x0050412C` | `0x0050475C` |
| apollo_main | `g2-s200-board-config` | 1 | `0x005093D4` | `0x00509446` |
| apollo_main | `g2-nvdb-sensor-caldata` | 8 | `0x00509764` | `0x00509AEA` |
| apollo_main | `g2-util-error-check` | 1 | `0x00509B48` | `0x00509BFA` |
| apollo_main | `g2-ui-common-api` | 9 | `0x00509C1C` | `0x00509F98` |
| apollo_main | `g2-onboarding-news-page` | 35 | `0x0050A094` | `0x0050C95E` |
| apollo_main | `g2-onboarding-stock-page` | 17 | `0x0050CA24` | `0x0050E8DC` |
| apollo_main | `g2-onboarding-animation` | 11 | `0x0050F8CC` | `0x005100A0` |
| apollo_main | `g2-callback-manager` | 8 | `0x005100A0` | `0x005105EE` |
| apollo_main | `g2-service-nvdb` | 5 | `0x005105F0` | `0x00510992` |
| apollo_main | `g2-pb-service-glasses-case` | 4 | `0x00510A0C` | `0x00510F5C` |
| apollo_main | `g2-npmx-main-driver` | 30 | `0x00511002` | `0x00512BB2` |
| apollo_main | `g2-thread-input` | 23 | `0x00512C84` | `0x005134B2` |
| apollo_main | `g2-opt3007-registers` | 1 | `0x005135E0` | `0x00513734` |
| apollo_main | `ambiqsuite-cordio-wsf-timer` | 11 | `0x0052A3FC` | `0x0052A614` |
| apollo_main | `ambiqsuite-cordio-wsf-assert-trace` | 2 | `0x0052A63C` | `0x00569ADE` |
| apollo_main | `ambiq-cordio-hci-core` | 22 | `0x0052A67C` | `0x0052AE38` |
| apollo_main | `ambiq-cordio-hci-cmd` | 50 | `0x0052AE38` | `0x0052B8A4` |
| apollo_main | `ambiqsuite-cordio-wsf-os` | 12 | `0x0052B8A4` | `0x0052BAB8` |
| apollo_main | `packetcraft-cordio-dm-sec-slave` | 3 | `0x0052BACC` | `0x0052BB60` |
| apollo_main | `packetcraft-cordio-atts-ccc` | 14 | `0x0052BB64` | `0x0052C66A` |
| apollo_main | `packetcraft-cordio-atts-csf` | 10 | `0x0052C6C0` | `0x0052DA0C` |
| apollo_main | `packetcraft-cordio-atts-sign` | 4 | `0x0052DA58` | `0x0052DBF0` |
| apollo_main | `g2-watchdog` | 2 | `0x0052F2E0` | `0x0052F36C` |
| apollo_main | `g2-service-em9305-dfu` | 7 | `0x0052F442` | `0x0052FF46` |
| apollo_main | `ambiq-cordio-hci-tr` | 3 | `0x0053013C` | `0x00530348` |
| apollo_main | `ambiqsuite-cordio-wsf-buf` | 3 | `0x00530364` | `0x00530512` |
| apollo_main | `packetcraft-cordio-l2c-main` | 11 | `0x00530538` | `0x00530BFE` |
| apollo_main | `ambiq-cordio-hci-core-ps` | 9 | `0x00530C00` | `0x00530D68` |
| apollo_main | `packetcraft-cordio-attc-main` | 20 | `0x00530D74` | `0x00531B90` |
| apollo_main | `packetcraft-cordio-atts-ind` | 13 | `0x005338AC` | `0x00533EF4` |
| apollo_main | `packetcraft-cordio-dm-conn-sm` | 2 | `0x00533EF4` | `0x006ECCA8` |
| apollo_main | `packetcraft-cordio-dm-sec-lesc` | 7 | `0x00534894` | `0x00534972` |
| apollo_main | `packetcraft-cordio-atts-main` | 17 | `0x0053498C` | `0x00535440` |
| apollo_main | `g2-app-ble-discovery` | 2 | `0x005354C2` | `0x0053609C` |
| apollo_main | `packetcraft-cordio-dm-conn-master-leg` | 3 | `0x00536A28` | `0x00536AB0` |
| apollo_main | `packetcraft-cordio-dm-conn-slave-leg` | 5 | `0x00536AC8` | `0x00536B30` |
| apollo_main | `packetcraft-cordio-l2c-slave` | 6 | `0x00536B40` | `0x00536FBA` |
| apollo_main | `packetcraft-cordio-l2c-master` | 3 | `0x00536FBC` | `0x00537278` |
| apollo_main | `packetcraft-cordio-smp-main` | 20 | `0x00537278` | `0x00537E9E` |
| apollo_main | `packetcraft-cordio-smp-legacy-sm` | 2 | `0x00537EEC` | `0x005380F2` |
| apollo_main | `packetcraft-cordio-smp-sc-sm` | 4 | `0x00537F14` | `0x00538236` |
| apollo_main | `g2-thread-ble-production` | 14 | `0x005382E4` | `0x00538B46` |
| apollo_main | `ambiqsuite-cordio-wsf-queue` | 6 | `0x00538C24` | `0x00538D16` |
| apollo_main | `packetcraft-cordio-attc-write` | 2 | `0x00539DCC` | `0x00539E48` |
| apollo_main | `cordio-hci-cmd-phy` | 1 | `0x00539E48` | `0x00539E92` |
| apollo_main | `g2-box-uart-mgr` | 5 | `0x00539E92` | `0x0053A3A4` |
| apollo_main | `g2-chg-bq25180` | 28 | `0x0053A670` | `0x0053AF4C` |
| apollo_main | `g2-chg-bq27427` | 37 | `0x0053AFC0` | `0x0053C1C4` |
| apollo_main | `g2-thread-audio` | 31 | `0x0053C2BE` | `0x0053CE72` |
| apollo_main | `g2-service-db-api` | 11 | `0x00540ED0` | `0x0054125C` |
| apollo_main | `g2-at-core` | 5 | `0x005412E0` | `0x0054157A` |
| apollo_main | `g2-uart-sync` | 5 | `0x00541790` | `0x00541A86` |
| apollo_main | `packetcraft-cordio-smp-db` | 11 | `0x00541E34` | `0x005429F2` |
| apollo_main | `g2-pb-service-dev-setting` | 10 | `0x00542DC4` | `0x00543B88` |
| apollo_main | `g2-navigation-ui` | 61 | `0x00545588` | `0x0054ED36` |
| apollo_main | `g2-service-audio-manager` | 7 | `0x0054F364` | `0x0054F976` |
| apollo_main | `g2-ui-msg-notif-list` | 50 | `0x0054FF36` | `0x00552CDC` |
| apollo_main | `g2-text-stream-service` | 26 | `0x00552B30` | `0x005537CC` |
| apollo_main | `g2-even-ai-animation` | 5 | `0x005537CC` | `0x00553FE8` |
| apollo_main | `g2-teleprompt-ui` | 55 | `0x00554170` | `0x005573E8` |
| apollo_main | `g2-dashboard-layout` | 11 | `0x00558030` | `0x005588A2` |
| apollo_main | `g2-pb-service-quicklist` | 10 | `0x0055894C` | `0x00559778` |
| apollo_main | `g2-health-data-manager` | 10 | `0x005597F0` | `0x0055A2B0` |
| apollo_main | `g2-pb-service-health` | 8 | `0x0055A558` | `0x0055B20A` |
| apollo_main | `g2-drv-cy8c4046fni` | 23 | `0x0055B2EC` | `0x0055B9C6` |
| apollo_main | `packetcraft-cordio-dm-sec-master` | 3 | `0x0055BBC4` | `0x0055BC54` |
| apollo_main | `packetcraft-cordio-dm-conn-master` | 5 | `0x0055BC5C` | `0x0055BCE6` |
| apollo_main | `g2-service-touch-dfu` | 32 | `0x0055FCB4` | `0x00561710` |
| apollo_main | `ambiq-cordio-hci-vs` | 4 | `0x00569B04` | `0x00569D26` |
| apollo_main | `ambiq-cordio-hci-evt` | 79 | `0x00569D4C` | `0x0056B7BC` |
| apollo_main | `packetcraft-cordio-attc-disc` | 15 | `0x0056B7EC` | `0x0056C3B0` |
| apollo_main | `packetcraft-cordio-attc-read` | 4 | `0x0056C3B0` | `0x0056C54E` |
| apollo_main | `packetcraft-cordio-atts-proc` | 9 | `0x0056C550` | `0x0056CD96` |
| apollo_main | `packetcraft-cordio-smp-sc-main` | 18 | `0x0056CDC0` | `0x0056D812` |
| apollo_main | `cordio-wstr` | 2 | `0x0056D8C4` | `0x0056D93A` |
| apollo_main | `packetcraft-cordio-atts-read` | 7 | `0x0056D93C` | `0x0056E4E4` |
| apollo_main | `packetcraft-cordio-dm-conn-slave` | 5 | `0x0056E4F8` | `0x0056E5C6` |
| apollo_main | `packetcraft-cordio-smp-act` | 25 | `0x0056E5CC` | `0x0056F144` |
| apollo_main | `g2-pt-protocol` | 73 | `0x0056F178` | `0x00577B7A` |
| apollo_main | `g2-service-codec-dfu` | 16 | `0x00577D7C` | `0x0057A360` |
| apollo_main | `g2-drv-gx8002b` | 12 | `0x0057A46C` | `0x0057A870` |
| apollo_main | `g2-service-audio` | 14 | `0x0057A900` | `0x0057B378` |
| apollo_main | `g2-drv-pdm-production` | 6 | `0x0057B444` | `0x0057B6A6` |
| apollo_main | `g2-drv-pdm` | 7 | `0x0057B704` | `0x0057BA1E` |
| apollo_main | `g2-service-codec-host` | 26 | `0x0057BA88` | `0x0057DB58` |
| apollo_main | `g2-freertos-plus-cli-filesystem` | 12 | `0x0057E898` | `0x0057F550` |
| apollo_main | `g2-system-monitor` | 1 | `0x00584EE4` | `0x005850E2` |
| apollo_main | `g2-kvdb-time` | 3 | `0x00585618` | `0x00585806` |
| apollo_main | `g2-navigation` | 5 | `0x00585CBA` | `0x0058638A` |
| apollo_main | `g2-navigation-data-handler` | 22 | `0x00586448` | `0x005885B4` |
| apollo_main | `g2-pb-service-teleprompt` | 7 | `0x005885B4` | `0x00588CF2` |
| apollo_main | `g2-teleprompt-timer-mgr` | 13 | `0x00588D74` | `0x0058934E` |
| apollo_main | `g2-list-anim` | 11 | `0x005893F0` | `0x00589934` |
| apollo_main | `g2-teleprompt-controller` | 10 | `0x005899A4` | `0x0058A30C` |
| apollo_main | `g2-bounce-anim` | 7 | `0x0058A3FC` | `0x0058A858` |
| apollo_main | `g2-teleprompt-page-data` | 21 | `0x0058A8E0` | `0x0058BC06` |
| apollo_main | `g2-teleprompt-file-list` | 3 | `0x0058BCE0` | `0x0058BD86` |
| apollo_main | `g2-exit-prompt` | 5 | `0x0058BDA8` | `0x0058C0B6` |
| apollo_main | `g2-fade-anim` | 11 | `0x0058C12C` | `0x0058C836` |
| apollo_main | `g2-teleprompt-fsm` | 15 | `0x0058C836` | `0x0058D410` |
| apollo_main | `g2-quicklist-data-manager` | 3 | `0x0058D51C` | `0x0058DACA` |
| apollo_main | `g2-product-common` | 4 | `0x0058F1EC` | `0x0058F49A` |
| apollo_main | `g2-production-mic` | 6 | `0x0058F4E4` | `0x0058F866` |
| apollo_main | `g2-nvdb-buzzer` | 5 | `0x0058F9D4` | `0x0058FA90` |
| apollo_main | `g2-service-codec-porting` | 2 | `0x0058FB52` | `0x0058FCA8` |
| apollo_main | `g2-service-algo` | 10 | `0x005915DC` | `0x00591C8C` |
| apollo_main | `g2-uled-jbd4010` | 24 | `0x00592658` | `0x005938CA` |
| apollo_main | `g2-conversate-tag-data` | 12 | `0x00595F4C` | `0x00596A2A` |
| apollo_main | `g2-translate-fsm` | 8 | `0x00596B00` | `0x00597018` |
| apollo_main | `g2-terminal-data` | 44 | `0x005970A8` | `0x00597C02` |
| apollo_main | `g2-uled-mspi-common` | 13 | `0x0059C820` | `0x0059D156` |
| apollo_main | `g2-iar-float-exponent` | 3 | `0x0059D244` | `0x0059D350` |
| apollo_main | `g2-translate-ui` | 29 | `0x0059D380` | `0x0059E9E2` |
| apollo_main | `g2-translate` | 11 | `0x0059E9E2` | `0x0059F3FE` |
| apollo_main | `g2-pb-service-translate` | 4 | `0x0059F53C` | `0x0059FA68` |
| apollo_main | `g2-eat-bond-connect` | 2 | `0x005A4FA4` | `0x005A4FC6` |
| apollo_main | `g2-at-buzzer` | 1 | `0x005A4FD0` | `0x005A53C6` |
| apollo_main | `g2-at-codec` | 1 | `0x005A5488` | `0x005A54FE` |
| apollo_main | `g2-at-nus` | 1 | `0x005A5520` | `0x005A552C` |
| apollo_main | `g2-at-fs` | 4 | `0x005A5530` | `0x005A56D0` |
| apollo_main | `g2-eat-core-sensor` | 12 | `0x005A5720` | `0x005A595E` |
| apollo_main | `g2-at-tp` | 2 | `0x005A5984` | `0x005A5D08` |
| apollo_main | `packetcraft-cordio-atts-write` | 4 | `0x005A5D94` | `0x005A6258` |
| apollo_main | `g2-conversate-controller` | 12 | `0x005B0114` | `0x005B09DE` |
| apollo_main | `g2-conversate-ui` | 23 | `0x005B0B58` | `0x005B1A64` |
| apollo_main | `g2-pb-service-conversate` | 6 | `0x005B1B4C` | `0x005B223C` |
| apollo_main | `g2-conversate-ui-main-page` | 15 | `0x005B23E4` | `0x005B34CC` |
| apollo_main | `g2-conversate-timer-mgr` | 24 | `0x005B3570` | `0x005B3E0C` |
| apollo_main | `g2-conversate-comm-data` | 12 | `0x005B3EF8` | `0x005B4846` |
| apollo_main | `g2-conversate-pb-msg-handler` | 15 | `0x005B48F8` | `0x005B57AC` |
| apollo_main | `g2-conversate-ui-menu-page` | 8 | `0x005B57AC` | `0x005B5DE4` |
| apollo_main | `g2-conversate-ui-tag-page` | 11 | `0x005B5DE4` | `0x005B6942` |
| apollo_main | `g2-conversate-ui-prep-note-page` | 16 | `0x005B69D4` | `0x005B7604` |
| apollo_main | `g2-expand-anim` | 5 | `0x005B7684` | `0x005B7902` |
| apollo_main | `g2-dashboard-watchface-layout1` | 19 | `0x005B7934` | `0x005B872A` |
| apollo_main | `g2-dashboard-watchface-layout2` | 19 | `0x005B90E8` | `0x005B9C5A` |
| apollo_main | `g2-dashboard-watchface-layout3` | 19 | `0x005B9CEC` | `0x005BAA1E` |
| apollo_main | `g2-dashboard-watchface-layout4` | 23 | `0x005BABA6` | `0x005BBDA4` |
| apollo_main | `g2-uled-a6ng` | 22 | `0x005BBD48` | `0x005BD3A0` |
| apollo_main | `g2-legal-regulatory` | 1 | `0x005BF7B8` | `0x005BF8A2` |
| apollo_main | `g2-s200-config-main` | 6 | `0x005CDB46` | `0x005CE138` |
| apollo_main | `g2-pb-service-ring` | 4 | `0x005CE1DC` | `0x005CE72E` |
| apollo_main | `g2-pb-service-terminal` | 13 | `0x005CE7C4` | `0x005CF1BE` |
| apollo_main | `g2-pdt-distortion-test` | 4 | `0x005CF2B4` | `0x005CF606` |
| apollo_main | `g2-pdt-gray-screen` | 3 | `0x005CF634` | `0x005CF788` |
| apollo_main | `g2-production-test-screen` | 3 | `0x005CF7A8` | `0x005CF8C6` |
| apollo_main | `g2-kvdb-ring` | 3 | `0x005D9B6C` | `0x005D9E88` |
| apollo_main | `g2-nvdb-adv-magic` | 3 | `0x005D9ED0` | `0x005D9F3E` |
| apollo_main | `g2-nvdb-mac` | 3 | `0x005D9F48` | `0x005DA060` |
| apollo_main | `packetcraft-cordio-smp-sc-act` | 20 | `0x005E267C` | `0x005E30E2` |
| apollo_main | `packetcraft-cordio-smpi-act` | 10 | `0x005E3118` | `0x005E3474` |
| apollo_main | `packetcraft-cordio-smpi-sc-act` | 16 | `0x005E3474` | `0x005E38A2` |
| apollo_main | `packetcraft-cordio-smpr-act` | 10 | `0x005E38C8` | `0x005E3D7A` |
| apollo_main | `packetcraft-cordio-smpr-sc-act` | 20 | `0x005E3D7C` | `0x005E4206` |
| apollo_main | `g2-terminal-core` | 9 | `0x005E42EC` | `0x005E4764` |
| apollo_main | `g2-terminal-ui` | 99 | `0x005E47CC` | `0x005E7E0C` |
| apollo_main | `g2-terminal-timer` | 6 | `0x005E7EA4` | `0x005E8124` |
| apollo_main | `g2-terminal-pb-msg-handler` | 27 | `0x005E8178` | `0x005EA152` |
| apollo_main | `g2-terminal-query-panel-ui` | 6 | `0x005EB438` | `0x005EB8DA` |
| apollo_main | `g2-terminal-session-list-ui` | 10 | `0x005ED1EC` | `0x005ED9BC` |
| apollo_main | `g2-tracepoint-setting` | 21 | `0x005EDADC` | `0x005EEFAA` |
| apollo_main | `g2-ux-battery-sync` | 1 | `0x005F958C` | `0x005F98D0` |
| apollo_main | `g2-ux-production` | 1 | `0x005F98D0` | `0x005F9C26` |
| apollo_main | `g2-ux-settings` | 2 | `0x005F9C8C` | `0x005F9EC8` |
| case | `g2-box` | 435 | `0x080000C0` | `0x0800D250` |
| touch | `g2-touch-prefix` | 63 | payload `0x0268` | payload `0x772C` |
