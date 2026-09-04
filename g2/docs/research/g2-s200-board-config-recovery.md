# G2 product\s200\app\config\board_config.c zero-anchor recovery

- Retained path: `product\s200\app\config\board_config.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\board_config.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-s200-board-config-closure.tsv` (sha256 `3f5a2fddfa09d75b593e32d65333f519cca06435f604f61eb310315da8a9135e`)
- Function map: `tools/manifests/g2-s200-board-config-function-map.tsv` (sha256 `34a932a1bc300c05d8b9f505269c266d1cd55a5d5cf6532f915c41099cb95eff`)
- Audit: `tools/analyze_g2_s200_board_config.py`; test: `tests/test_analyze_g2_s200_board_config.py`

## Identity evidence

- Path string at 0x006F1BDC; pointer cell(s) 0x005094B8; 1 literal reference(s), all inside the mapped blocks.
- 1 module log-tag strings loaded by the mapped blocks, including:
- `0x00752568` `[BSP]hw_version: %d, hw_adc_val: %d`

## Linked extents

Physical interval `[0x005093D0, 0x0050968C)` = 700 bytes (114 body + 586 pool/data). The four zero bytes at `0x005093D0` are retained pool prefix, not executable instructions; the function begins at `0x005093D4`.

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5093d4-0x509446 | 114 | 1 | 46 | `80e6eecae3fce4e7...` |

## Ingress (whole-image scans)

- direct BL entry sites: 0; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 1 (`0x006D1E0C -> 0x005093D5`)
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

A data-dominated object: 114 bytes of code (1 path reference, tag `[BSP]hw_version: %d, hw_adc_val: %d`) plus 586 bytes of board configuration data (including the four-byte zero prefix and pinmux/peripheral constant words) up to the next corpus-discovered function at 0x50968C.

Board-config access code is corpus-covered and already documented elsewhere: the watchdog closure records selector provider `0x0050938E`, and init-table cell `0x006D1E0C` stores the Thumb entry `0x005093D5`. Treating the zero prefix as code previously hid that stored pointer; the corrected topology is pinned by the analyzer and manifests.

## Production source route

`components/apollo_main/core_overlay/s200_board_config.c` is the clean-room production implementation. It selects board record 3, dispatches charger family 1 to the retained nPMx initializer, dispatches family 2 to the existing source-routed BQ25180 initializer followed by BQ27427, treats other families as no-ops, and returns zero. Diagnostic logging is omitted because it does not control behavior.

Both canonical compiler profiles build one 38-byte freestanding C leaf with four strict `R_ARM_THM_CALL` relocations. The Apple and Linux build receipts, final component branches, effective relocated bodies, manifest ownership, package hashes, and zero unresolved flash regions are checked fail-closed. Host runtime tests cover both supported families and unknown-family no-op behavior.

Software closure is complete for this object. Hardware qualification remains **blocked by unavailable physical evidence**: an authorized G2 example of each supported charger family, or authenticated golden traces, is required to prove selector-3 record decoding, family dispatch, BQ25180-before-BQ27427 ordering, and resulting rail, charge, and fuel-gauge behavior. No hardware operation was performed.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_s200_board_config -v
```
