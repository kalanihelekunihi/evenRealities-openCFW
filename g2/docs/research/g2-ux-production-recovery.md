# G2 app\ux\ux_production\ux_production.c zero-anchor recovery

- Retained path: `app\ux\ux_production\ux_production.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_production\ux_production.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-ux-production-closure.tsv` (sha256 `e19c6bb08304f06ddd256556f9c719f8f1b9c862c7cbffd6224313332e26b45e`)
- Function map: `tools/manifests/g2-ux-production-function-map.tsv` (sha256 `78c906447e95e3ca279c039d7f46408e1f1aa32b0e7eadd0cab8507e97e3a7ab`)
- Audit: `tools/analyze_g2_ux_production.py`; test: `tests/test_analyze_g2_ux_production.py`

## Identity evidence

- Path string at 0x006F7CA4; pointer cell(s) 0x005F9C30; 10 literal reference(s), all inside the mapped blocks.
- 10 module log-tag strings loaded by the mapped blocks, including:
- `0x006FF62C` `[ux.production]DEVICE_SYNC_RECV_DATA, set device_sync_test_flag = true`
- `0x00708708` `[ux.production]DEVICE_SYNC_SEND_DATA, send DEVICE_SYNC_RECV_DATA`
- `0x00711C24` `[ux.production]pMsg->head.msg_self_role = %d(MASTER_ROLE = %d)`
- `0x00726100` `[ux.production]eDevCfgCommandId_PRODUCTION_CLOSE_MIC`
- `0x00726138` `[ux.production]eProductionCommandId_DEVICE_SYNC_TEST`
- `0x0073B594` `[ux.production]pMsg->head.msg_peer_role = %d %d`
- `0x0073B5C4` `[ux.production]eProductionCommandId_OPEN_MIC`
- `0x0073B5F4` `[ux.production]pMsg->head.msg_len is invalid`

## Linked extents

Physical interval `[0x005F98D0, 0x005F9C8C)` = 956 bytes (854 body + 102 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5f98d0-0x5f9c26 | 854 | 10 | 349 | `214ce1531f4ff69b...` |

## Ingress (whole-image scans)

- direct BL entry sites: 0; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 2; indirect blx sites: 0

## Boundary attribution and notes

A single 854-byte block with 10 path references and 10 `[ux.production]` tags (device sync test and production command handling), plus a 102-byte trailing pool carrying path cell 0x5F9C30. Two tail-call escapes leave the interval downward into corpus-covered code (pinned). Zero static ingress across BL, B.W, 16-bit B, stored-word, and movw/movt scans; dispatch is presumed dynamic and is recorded as a scanned fact.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_ux_production -v
```
