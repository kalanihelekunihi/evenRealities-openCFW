# G2 app\gui\MessageNotify\message_notify.c zero-anchor recovery

- Retained path: `app\gui\MessageNotify\message_notify.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\message_notify.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-message-notify-closure.tsv` (sha256 `6a02b22eb5af7660a8cc12cb5a328aababb1cd8922d2c8e99fe6145da4b4eded`)
- Function map: `tools/manifests/g2-message-notify-function-map.tsv` (sha256 `d03e9acd547ed1fe9cd92b6c197deebd2edf14477d1bd8e2889b40bef9dd0623`)
- Audit: `tools/analyze_g2_message_notify.py`; test: `tests/test_analyze_g2_message_notify.py`

## Identity evidence

- Path string at 0x006F45B8; pointer cell(s) 0x004E1F38; 5 literal reference(s), all inside the mapped blocks.
- 5 module log-tag strings loaded by the mapped blocks, including:
- `0x006FB654` `[message_notify.page]MSG_NOTIF_EVENT_BASICINFO_UPDATE, update_type = %d`
- `0x00720408` `[message_notify.page]MessageNotify recv data len = %d`
- `0x00735774` `[message_notify.page]recv msg_notif startup:%d`
- `0x0074B4DC` `[message_notify.page]UI_EVENT_TYPE_INIT`
- `0x0074B504` `[message_notify.page]UI_EVENT_TYPE_EXIT`

## Linked extents

Physical interval `[0x004E1B30, 0x004E1F7C)` = 1100 bytes (1016 body + 84 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x4e1b30-0x4e1c42 | 274 | 2 | 108 | `d7fd9497495e95a0...` |
| 0x4e1c42-0x4e1cc4 | 130 | 0 | 57 | `c424f347635158ea...` |
| 0x4e1cc4-0x4e1dd4 | 272 | 1 | 116 | `b3736479dbae334b...` |
| 0x4e1dd4-0x4e1f28 | 340 | 2 | 141 | `e943296f07aca7f7...` |

## Ingress (whole-image scans)

- direct BL entry sites: 1; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Four blocks in interval [0x4E1B30, 0x4E1F7C). Identity: 5 path references across 3 blocks and 5 `[message_notify.page]` tags. Registration: screen-descriptor cells 0x6A4584 (entry 0x4E1B30) and 0x6A4588 (entry 0x4E1DD4). The 46-byte lazy-singleton helper at [0x4E1F7C, 0x4E1FA6) that immediately follows is mapped under `app\gui\EvenAI\even_ai.c`: its only callers are even_ai blocks (sites 0x4E297E and 0x4E2C84). It is excluded here and guard-pinned.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_message_notify -v
```
