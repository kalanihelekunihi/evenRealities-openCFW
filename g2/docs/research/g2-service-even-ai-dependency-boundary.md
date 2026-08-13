# G2 EvenAI service dependency boundary

Retained path `platform\service\evenAI\service_even_ai.c` (string at run
`0x006EF8B8`, pointer cell `0x004985B8`). The three path-anchored functions
expand to nine functions / 1,984 body bytes in `[0x00497DE6,0x00498634)`, a
2,126-byte physical object immediately after the closed service-ancc object
(which ends at `0x00497DE6`). Three source-order functions missed by Ghidra
restore the large state builder and two of the three protobuf notification
bridges. The trailing pool `[0x004985A6,0x00498634)` (142 bytes) holds the
path pointer cell and every body literal; the six tiny LVGL helpers at
`0x00498634..0x00498680` belong to the following lv_image cluster (lv_image's
first anchored function calls three of them) and are excluded.

## Extent and inventory

- 9 linked functions; 6 Ghidra-discovered (3 path-anchored: `0x00497E08`,
  `0x0049832E`, `0x00498528`); 3 restored (`0x00498092`, `0x004982D4`,
  `0x004982F2`).
- 753 reachable instructions; bodies contiguous; only the trailing pool is
  noncode.
- Eleven raw LDR-literal references to the path cell span 4 functions,
  including the Ghidra-missed state builder — ownership evidence independent
  of Ghidra.
- Cross-confirmation from already-closed providers: even-ai-timer records
  exterior BL at `0x00497EAC`; pb-service-even-ai records exterior BLs at
  `0x004982EC`, `0x0049830A`, and `0x00498328` — three of them inside
  Ghidra-missed functions of this object.

## Ingress proof

- 30 whole-image direct BL sites reach exact starts (including the three
  intra-object calls); no strict interior ingress; no pseudo-BL into the
  pool; no indirect call.
- One stored Thumb pointer at `0x0049861C`→`0x00497E09` (the diagnostic
  wrapper), held in the object's own pool.
- Three raw unaligned words collide with interior halfwords
  (`0x004485D7`→`0x00497FD5`, `0x0052AC03`→`0x004983B5`,
  `0x0064A583`→`0x00497DFF`); none is a stored entry pointer.

## Provider boundary

127 direct body calls; 3 internal; 124 external, partitioned:

- EasyLogger diagnostics: 55 (`0x0043CE9E`, `0x0043D0CE`, `0x0043D574`).
- Bounded IAR DLIB memory primitives: 9 (`0x00439BE4`, `0x0043C0E4`).
- Exact CMSIS-FreeRTOS v10.5.1 wrapper: 2 — seam `osKernelGetTickCount`
  (`0x004490CC`) for heartbeat scheduling. No direct FreeRTOS kernel seam.
- Closed first-party providers: 23 (OTA gate `0x004487AC`,
  sync-interface-api `0x00464F76`, onboarding-controller `0x00468034`,
  silent-mode `0x00469AE2`, NVDB product mode `0x004ABE60`, even-ai-timer
  `0x004E304C`, pb-service-even-ai encoders `0x004E3788`/`0x004E3B80`/
  `0x004E4CB8`, ui-even-ai `0x004E5672`/`0x004E5D54`).
- Bounded unclosed first-party providers: 35 (display readiness
  `0x00467F08`, callback dispatch `0x004E1FA6`/`0x004E1FBE`).

## AI/NN negative evidence

No embedded AI/NN library body exists in this object: all 124 external calls
terminate at the admitted EasyLogger, bounded IAR DLIB, exact CMSIS-FreeRTOS
tick, or bounded first-party providers above; there is no NN-kernel, DSP, or
inference provider edge, and `embedded_third_party_definitions` is empty.
The object is glue between the control decoder, heartbeat timer, and the
closed pb-service-even-ai encoders. No new version/commit discriminator and
no observable private producing commit. Not production routed. Reproduce
with `python3 tools/analyze_g2_service_even_ai.py` and
`python3 -m unittest tests.test_analyze_g2_service_even_ai -v`.

## Limitations

- Restored function names are source-order labels; behavior claims cite only
  recorded cross-object BL sites and call targets.
- The bounded callback-dispatch providers `0x004E1FA6`/`0x004E1FBE` are
  pinned by address and neighborhood (closed service-ancc provider set)
  only; their own closures are tracked elsewhere.
