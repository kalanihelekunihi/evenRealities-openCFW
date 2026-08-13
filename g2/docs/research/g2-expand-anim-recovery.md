# G2 app\gui\anim\expand_anim.c zero-anchor recovery

- Retained path: `app\gui\anim\expand_anim.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\expand_anim.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-expand-anim-closure.tsv` (sha256 `aba13fb1bd08bc1748116eedcd7660f2de370bc206b4bafcd1114c1bc951c1c3`)
- Function map: `tools/manifests/g2-expand-anim-function-map.tsv` (sha256 `6888537893138007684b7d46f912d6c23d946235ce71baeac69c436c620ef844`)
- Audit: `tools/analyze_g2_expand_anim.py`; test: `tests/test_analyze_g2_expand_anim.py`

## Identity evidence

- Path string at 0x0070BF24; pointer cell(s) 0x005B790C; 2 literal reference(s), all inside the mapped blocks.
- 2 module log-tag strings loaded by the mapped blocks, including:
- `0x00729BD8` `[expand.anim]expand_animation_play: obj is invalid`
- `0x00734304` `[expand.anim]expand_animation_play: cfg is NULL`

## Linked extents

Physical interval `[0x005B7684, 0x005B7934)` = 688 bytes (638 body + 50 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5b7684-0x5b76a4 | 32 | 0 | 14 | `e298e73f77da749b...` |
| 0x5b76a4-0x5b76c4 | 32 | 0 | 14 | `549b1b52f4ff78fc...` |
| 0x5b76c4-0x5b76e4 | 32 | 0 | 14 | `d0062163e4d03f27...` |
| 0x5b76e4-0x5b7704 | 32 | 0 | 14 | `68fc156d37e5b312...` |
| 0x5b7704-0x5b7902 | 510 | 2 | 215 | `4d49ef5288214e1c...` |

## Ingress (whole-image scans)

- direct BL entry sites: 4; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 4
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks in interval [0x5B7684, 0x5B7934): four 32-byte callbacks registered through the object's own trailing table cells 0x5B7920-0x5B792C, plus the 510-byte entry 0x5B7704 with the 2 path references and the `[expand.anim]` tags. The gap is shared with `app\gui\conversate\conversate_ui_prep_note_page.c` (open, anchored); that path's blocks (0x5B7116, 0x5B7138, 0x5B74BA, 0x5B7518, 0x5B7556 and their pools, stored cells in the 0x686Axx/0x5B76xx range) were left to its own closure. The left boundary at 0x5B7684 and the trailing pool carrying the path cell 0x5B790C are guard-pinned.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_expand_anim -v
```
