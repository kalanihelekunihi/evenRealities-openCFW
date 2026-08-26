# G2 sensor_hub dependency boundary

The five retained-path anchors (across two path cells, 0x004A6EDC and
0x004A73E8) expand to thirty-one functions / 4,026 body bytes in
`[0x004A6644,0x004A777C)`, a 4,408-byte physical object with 382 noncode bytes
in three literal pools (0x004A6ECA, 0x004A713A, 0x004A7344) and the trailing
pool at 0x004A774E. Twenty-six source-order functions Ghidra missed restore
the thread lifecycle (init/entry/terminate and state enter/exit), the message
processor and record senders, the ALS timer trio, the IMU collection and
set-mode handlers, the role pair, the empty hook, and the two big IMU
func-open/func-close handlers that carry the second path cell's eleven
references. Sixty-one whole-image BL sites reach starts (33 external, from the
ALS and IMU drivers, OTA, settings, and UI callers); three stored entry
pointers (thread init/exit table and the ALS timer callback); four raw
unaligned words collide with interiors (odd packed-data cells); no strict
interior ingress and no pseudo-BL into pools.

The single indirect call at 0x004A6916 is a bounded runtime dispatch:
`HUB_MessageProcesser` matches message IDs against an eight-entry
`{uint16 id, handler}` table in `.bss` (hub state struct 0x20003664+0x24)
populated only through runtime registration; the table base cell is referenced
from this object alone. The table handlers are the HUB_*Handler functions.

All 254 external calls terminate at admitted EasyLogger (130), admitted LVGL
label/layout primitives (69, seam identical to previously closed GUI objects),
closed first-party providers (36: imu_icm45608, als, ota_service,
service_settings, rtos, nvdb_product_mode, thread_manager,
nvdb_sensor_caldata), exact CMSIS-FreeRTOS v10.5.1 wrappers (9:
osKernelGetTickCount, osThreadNew/osThreadTerminate, osTimerNew/Start/Stop,
osMessageQueueNew/Put/Get), first-party translation lookups (8), the admitted
nanopb seam (1), and a bounded frontier-open role getter (1). No direct
FreeRTOS kernel call exists.

## Sensor-fusion provenance (negative evidence)

No sensor-fusion or vendor driver library body (amb/Invensense/Bosch
candidates) is embedded in this object. All IMU register, FIFO, and mode work
is delegated to the already closed `imu_icm45608.c` driver object (25 call
edges) and ALS work to the closed `als.c` object (3 edges); the calibration
matrix is loaded from the closed `service_nvdb_sensor_caldata.c` provider.
This is recorded as negative provenance evidence: sensor_hub.c is policy and
message routing only.

The object embeds no reusable third-party body and no version/commit
discriminator. Its complete software surface is now production-routed through
`components/apollo_main/core_overlay/sensor_hub.c`: 31 selector-isolated
functions emit 1,602 Thumb text bytes plus 36 alignment bytes with 106 strict
relocations. Thirty guarded redirects replace 4,024 stock bytes. The
unreachable two-byte empty hook and 382 bytes of authenticated pools remain as
384 compatibility bytes; the source-owned entry calls the corresponding source
hook directly.

Host oracles cover thread/queue/timer lifecycle, the bounded eight-entry
handler dispatch, role and open/close policy, OTA-gated ALS polling, IMU
collection/work-mode transitions, calibration loading, mutual exclusion, and
calibration-display feedback. Every selector compiles under the strict
Cortex-M55 production profile. Live IMU/ALS samples, timing, calibration, and
display behavior remain explicitly blocked: the authorized right temple is
nonresponsive, the authorized left temple must remain stock, and no responsive
authorized sensor path or golden IMU/ALS trace is available. Reproduce the
software gate with `make sensor-hub-closure`.
