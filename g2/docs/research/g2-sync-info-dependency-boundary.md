# G2 sync-info dependency boundary

Retained path `app\gui\sync_info\sync_info.c` (string at run `0x0070643C`,
pointer cell `0x00472208`). The three path-anchored functions are the
complete object: 780 body bytes in `[0x00471EE8,0x00472244)`, an 860-byte
physical object whose trailing pool `[0x004721F4,0x00472244)` (80 bytes)
holds the path pointer cell and body literals. Ghidra discovered all three
functions; no restoration was required. The following function at
`0x00472244` is the anchored start of the ring-service object; the preceding
unanchored helper and its pool belong to the previous translation unit.

## Extent and inventory

- 3 linked functions; 3 Ghidra-discovered; 3 path-anchored; 0 restored.
- 326 reachable instructions; bodies contiguous; only the trailing pool is
  noncode.
- Six raw LDR-literal references to the path cell span all three functions.

## Ingress proof

- 8 whole-image direct BL sites reach exact starts; no strict interior
  ingress; no pseudo-BL into the pool; no indirect call.
- One stored Thumb pointer at `0x006A4664`→`0x00472103`, registering the
  decode/dispatch entry as a callback.
- No raw interior word collision exists.

## Provider boundary

56 direct body calls; 1 internal (the decode entry calls the source-order
builder); 55 external, partitioned:

- EasyLogger diagnostics: 30 (`0x0043CE9E`, `0x0043D0CE`, `0x0043D574`).
- Bounded IAR DLIB memory primitives: 8 (`0x00439C04`, `0x0043C0E4`).
- Admitted nanopb runtime: 6 (`0x0048F49C`, `0x00490120`, `0x004905F4`,
  `0x00490C32` — generic stream decode/encode helpers, 0.4.7–0.4.9.1
  compatible, selected 0.4.9 commit
  `98bf4db69897b53434f3d0ba72e0a3ab1a902824`); schemas and dispatch remain
  first-party.
- Closed first-party providers: 11 (display-thread LVGL-integration seam
  `0x00443504`, file-runtime pair `0x00474CD2`/`0x00474D16`,
  thread-ble-message transport `0x00475B14`/`0x00475C1A`).

No CMSIS-FreeRTOS or FreeRTOS seam, no embedded reusable third-party body,
no new version/commit discriminator, and no observable private producing
commit. Not production routed. Reproduce with
`python3 tools/analyze_g2_sync_info.py` and
`python3 -m unittest tests.test_analyze_g2_sync_info -v`.

## Limitations

- Function names are source-order labels; the exact nanopb schema layout
  owned by this object is not re-derived here.
- The display-thread target `0x00443504` is a closed first-party function
  that another closed object also classifies as an LVGL-integration seam;
  this closure records it as a bounded closed provider only.
