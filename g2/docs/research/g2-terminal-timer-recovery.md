# G2 app\gui\terminal\terminal_timer.c zero-anchor recovery

- Retained path: `app\gui\terminal\terminal_timer.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_timer.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-terminal-timer-closure.tsv` (sha256 `05e6f476bcafadc3625490afce97af1b6828ec5f443dc431b64758f0038eafdf`)
- Function map: `tools/manifests/g2-terminal-timer-function-map.tsv` (sha256 `7517d01de3b6df6117e5aa3abff74c745bec751081e9cfeafc5cdbd559eaf6d5`)
- Audit: `tools/analyze_g2_terminal_timer.py`; test: `tests/test_analyze_g2_terminal_timer.py`

## Identity evidence

- Path string at 0x006FDF64; pointer cell(s) 0x005E8130; 6 literal reference(s), all inside the mapped blocks.
- 6 module log-tag strings loaded by the mapped blocks, including:
- `0x00719D50` `[terminal.timer]asr result wait 20s timeout, back to idle`
- `0x00724308` `[terminal.timer]asr result timeout start, due in %d ms`
- `0x0072ECB0` `[terminal.timer]voice timeout start, due in %d ms`
- `0x00744CFC` `[terminal.timer]voice recording 60s timeout`
- `0x0074F7E4` `[terminal.timer]asr result timeout stop`
- `0x0075B5D4` `[terminal.timer]voice timeout stop`

## Linked extents

Physical interval `[0x005E7EA4, 0x005E8178)` = 724 bytes (624 body + 100 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5e7ea4-0x5e7ec4 | 32 | 0 | 16 | `4fecc17cd604a753...` |
| 0x5e7ed4-0x5e7f26 | 82 | 1 | 33 | `d602e385d1f00d77...` |
| 0x5e7f26-0x5e7f6e | 72 | 1 | 30 | `b16d4a3124a813c4...` |
| 0x5e7f6e-0x5e7fc0 | 82 | 1 | 33 | `2f5e35bb95cc5412...` |
| 0x5e7fc0-0x5e8008 | 72 | 1 | 30 | `fdecdc34fa243593...` |
| 0x5e8008-0x5e8124 | 284 | 2 | 115 | `48cf16cce6e126d8...` |

## Ingress (whole-image scans)

- direct BL entry sites: 18; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Six blocks in the shared terminal gap. Identity: 6 path references across 5 blocks and 6 `[terminal.timer]` tags (ASR result and voice recording timeout management). The 32-byte helper 0x5E7EA4 is called only from this object's block 0x5E8008 and is mapped. The 16-byte block 0x5E7EC4 interleaved between the helper and the first reference block is foreign (called from the terminal cluster site 0x5E7212): it is pinned as `interleaved_foreign_blocks` and not claimed. The bulk of the surrounding gap belongs to `app\gui\terminal\terminal_ui.c` (anchored, closed by its own closure); this interval is exactly bounded.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_terminal_timer -v
```
