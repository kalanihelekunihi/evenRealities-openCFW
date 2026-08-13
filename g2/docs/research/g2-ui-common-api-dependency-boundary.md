# G2 UI common API dependency boundary

Retained path `app\gui\common\ui_common_api.c` (string at run `0x0070797C`,
pointer cell `0x00509FA0`). The three path-anchored functions expand to nine
functions / 892 body bytes in `[0x00509C1C,0x00509FDC)`, a 960-byte physical
object. Ghidra discovered all nine; no restoration was required. The object
starts exactly where the closed util-error-check object ends (`0x00509C1C`)
and ends before the ui-onboarding-news-page cluster (whose first function at
`0x00509FDC` is called by that object's anchored function). The trailing
pool `[0x00509F98,0x00509FDC)` (68 bytes) holds the path pointer cell and
the body literals.

## Extent and inventory

- 9 linked functions; 9 Ghidra-discovered; 3 path-anchored (`0x00509C1C`,
  `0x00509CA2`, `0x00509E14`); 0 restored.
- 330 reachable instructions; bodies contiguous; only the trailing pool is
  noncode.
- Seven raw LDR-literal references to the path cell span the three anchored
  functions.
- Six small source-order helpers round out the object: two leaf field
  accessors, two field writers, the message-count query (tail call to the
  closed `service_ancc_message_count_get`), and the battery query (tail call
  to closed `CHG_GetSoc`; charger-common records this BL at `0x00509F90`).

## Ingress proof

- 182 whole-image direct BL sites reach exact starts — this is a widely
  used common API; no strict interior ingress; no pseudo-BL into the pool;
  no indirect call.
- No stored Thumb entry pointer and no raw interior word collision exists.

## Provider boundary

41 direct body calls; 0 internal; 41 external, partitioned:

- EasyLogger diagnostics: 35 (`0x0043CE9E`, `0x0043D0CE`, `0x0043D574`).
- Bounded IAR DLIB memory primitive: 2 (`0x0043C0E4` memset).
- Closed first-party providers: 4 (file-runtime pair `0x00474CD2`/
  `0x00474D16`, service-ancc message count `0x004974D4`, charger SOC
  `0x004AD8FA`).

No CMSIS-FreeRTOS or FreeRTOS seam, no embedded reusable third-party body,
no new version/commit discriminator, and no observable private producing
commit. Not production routed. Reproduce with
`python3 tools/analyze_g2_ui_common_api.py` and
`python3 -m unittest tests.test_analyze_g2_ui_common_api -v`.

## Limitations

- Function names are source-order labels; behavior claims cite only call
  targets and cross-recorded BL sites.
- The 182 inbound BL sites prove wide usage but per-caller UI semantics are
  owned by the calling objects.
