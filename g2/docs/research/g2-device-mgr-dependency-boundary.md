# G2 device manager dependency boundary

Retained path `platform\device_mgr\device_mgr.c` (string at run `0x006F9C74`,
pointer cell `0x004C6BFC`). The four Ghidra-discovered, path-anchored
functions expand to twenty functions / 2,484 body bytes in
`[0x004C6240,0x004C6D04)`, a 2,756-byte physical object. Sixteen source-order
functions missed by Ghidra restore the initialization/teardown pair, the
queue-draining message loop, a bounded command dispatcher, two registered
table handlers, the charger gauge init path, role-gated sync, product-mode
gates, and the status-sync routine. The pool `[0x004C6BF4,0x004C6D04)` (272
bytes) holds every literal referenced from the body plus the path pointer
cell; the preceding pool at `0x004C6148..0x004C6240` is referenced only by
the neighboring object and is excluded.

## Extent and inventory

- 20 linked functions; 4 Ghidra-discovered (all path-anchored:
  `0x004C659A`, `0x004C6810`, `0x004C691C`, `0x004C6AD8`); 16 restored.
- 931 reachable instructions; bodies are contiguous with no interior pools.
- Fifteen raw LDR-literal references to the path cell span 8 of the 20
  functions, including restored ones — ownership evidence independent of
  Ghidra.
- Cross-confirmation from already-closed providers: charger-common records
  exterior BLs at `0x004C632E`/`0x004C64A6`, DRV_Bq25180 at `0x004C6886`,
  DRV_Bq27427 at `0x004C688A`, charger-common again at `0x004C6896`, and
  NVDB sys dt at `0x004C6AD0`/`0x004C6BDC` — all inside restored or anchored
  functions of this object.

## Ingress proof

- 18 whole-image direct BL sites reach exact function starts; none reaches
  an instruction interior; no pseudo-BL lands in the pool.
- Four stored Thumb pointers: `0x007490D0`→`0x004C6639` and
  `0x007490E0`→`0x004C66F1` (slots 2 and 4 of the dispatch table), plus
  `0x00791BCC`→`0x004C6241` and `0x00791BD0`→`0x004C64A5` (external
  registration of the init and deinit wrappers).
- One raw unaligned word at `0x00509985` collides with an interior halfword
  (`0x004C6AB5`); it is not a stored entry pointer.
- One indirect call: `blx r1` at `0x004C6544`, bounded to the fixed
  five-slot `{u16 id, pad, fn}` table at `0x007490C4` with handlers
  `0x0053A0B7`, `0x004C6639` (internal), `0x004AC279`, `0x004C66F1`
  (internal), and a NULL-guarded fifth slot.

## Provider boundary

152 direct body calls; 15 internal; 137 external, partitioned:

- EasyLogger diagnostics: 75 (`0x0043CE9E`, `0x0043D0CE`, `0x0043D574`).
- Exact CMSIS-FreeRTOS v10.5.1 wrappers: 10 — seams `osThreadNew`
  (`0x004490E2`), `osThreadTerminate` (`0x004491FE`), `osDelay`
  (`0x00449376`), `osTimerNew` (`0x004493B0`), `osTimerStart`
  (`0x00449498`), `osMessageQueueNew` (`0x00449A32`), `osMessageQueuePut`
  (`0x00449ABE`), `osMessageQueueGet` (`0x00449B3C`).
- Exact FreeRTOS V10.5.1 kernel call: 1 — `xTaskGetTickCount`
  (`0x00454EFE`).
- Bounded IAR DLIB memory primitive: 3 (`0x00439C04`); no discriminator.
- Closed first-party providers: 34 (display thread, OTA gate, service-time,
  sync-interface-api, universal-setting, service-settings, NVDB product
  mode/sys dt, charger-common, dashboard-data-process interior targets
  `0x004FF8D4`/`0x004FF8DC`, ring-battery, buzzer, nPMX, watchdog,
  bq25180/bq27427 gauges, thread-audio).
- Bounded unclosed first-party providers: 14 (sync transport `0x0045A568`,
  box-detect region, glasses-case region, watchdog selector `0x0050938E`,
  DFU region, board cache seam `0x0053A5BE`).

No embedded reusable third-party body, no new version/commit discriminator,
and no observable private producing commit. The object is not production
routed. Reproduce with `python3 tools/analyze_g2_device_mgr.py` and
`python3 -m unittest tests.test_analyze_g2_device_mgr -v`.

## Limitations

- Restored function names in the function map are source-order labels; only
  behavior visible from calls and cross-recorded BL sites is claimed.
- The two dashboard-data-process BL targets are interior addresses of a
  closed function body; ownership is bounded by that closed object, but the
  local entry semantics are not re-derived here.
- Unclosed bounded providers are pinned by address and neighborhood only;
  their own closures are tracked by their respective objects.
