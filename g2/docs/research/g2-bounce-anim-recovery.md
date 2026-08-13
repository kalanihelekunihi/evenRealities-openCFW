# G2 app\gui\anim\bounce_anim.c zero-anchor recovery

- Retained path: `app\gui\anim\bounce_anim.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\bounce_anim.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-bounce-anim-closure.tsv` (sha256 `b7c2cc320c32c5fd27063dff1e0849fc37829dcc626d009a5359ce9a27a963cc`)
- Function map: `tools/manifests/g2-bounce-anim-function-map.tsv` (sha256 `b423eac380ef9b78b0de21cf2bd129e52147bc2ad3e6f56d917a8e9d5129502a`)
- Audit: `tools/analyze_g2_bounce_anim.py`; test: `tests/test_analyze_g2_bounce_anim.py`

## Identity evidence

- Path string at 0x007097A4; pointer cell(s) 0x0058A860; 11 literal reference(s), all inside the mapped blocks.
- 11 module log-tag strings loaded by the mapped blocks, including:
- `0x006DF884` `[bounce.anim]Starting bounce animation: direction=%s, distance=%dpx, total_duration=%dms`
- `0x007009EC` `[bounce.anim]phase1_ready_cb: animation was stopped, cleaning up`
- `0x00700A30` `[bounce.anim]phase2_ready_cb: animation was stopped, cleaning up`
- `0x0071C5B0` `[bounce.anim]Phase 2 animation started: duration=%dms`
- `0x0071C5E8` `[bounce.anim]Phase 1 animation started: duration=%dms`
- `0x00727304` `[bounce.anim]Phase 1 completed, starting phase 2`
- `0x0072736C` `[bounce.anim]Bounce animation stopped for obj=%p`
- `0x00731D84` `[bounce.anim]phase1_ready_cb: invalid context`

## Linked extents

Physical interval `[0x0058A3FC, 0x0058A8E0)` = 1252 bytes (1114 body + 138 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x58a3fc-0x58a408 | 12 | 0 | 5 | `10bde49153aab4b5...` |
| 0x58a408-0x58a596 | 398 | 4 | 152 | `9c1cacc0735c8b51...` |
| 0x58a598-0x58a5a4 | 12 | 0 | 5 | `bd438698ebf73eaa...` |
| 0x58a5a4-0x58a680 | 220 | 3 | 92 | `794c7445a062fcfb...` |
| 0x58a680-0x58a7d2 | 338 | 3 | 139 | `3d686436336ecb4a...` |
| 0x58a7d2-0x58a83e | 108 | 1 | 45 | `d5e3af05c59029dc...` |
| 0x58a83e-0x58a858 | 26 | 0 | 13 | `188a5ed3273331d4...` |

## Ingress (whole-image scans)

- direct BL entry sites: 7; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 1

## Boundary attribution and notes

Seven blocks in gap [0x58A3FC, 0x58A8E0). Identity: 11 path references across 4 blocks and 11 `[bounce.anim]` tags (two-phase bounce animation lifecycle). Registration: callback cells 0x58A8C4/0x58A8C8 stored in the object's own trailing pool; external callers 0x556146/0x556298 and 0x5B2A8A/0x5B2A98; one indirect `blx` site at 0x58A5F8. The head bytes [0x58A30C, 0x58A3FC) belong to the preceding object and are excluded by guard.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_bounce_anim -v
```
