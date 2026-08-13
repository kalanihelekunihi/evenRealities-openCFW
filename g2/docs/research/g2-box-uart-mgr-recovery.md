# G2 platform\device_mgr\box_uart_mgr.c zero-anchor recovery

- Retained path: `platform\device_mgr\box_uart_mgr.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\platform\device_mgr\box_uart_mgr.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-box-uart-mgr-closure.tsv` (sha256 `5eb1b748847610c1098d5fa3c46cd35ff1e08074ec63e5e3cc03367217052230`)
- Function map: `tools/manifests/g2-box-uart-mgr-function-map.tsv` (sha256 `59b450ae9ad9341eef8350bdb74d425df7cb44d73845801e85603d9ede19005a`)
- Audit: `tools/analyze_g2_box_uart_mgr.py`; test: `tests/test_analyze_g2_box_uart_mgr.py`

## Identity evidence

- Path string at 0x006F890C; pointer cell(s) 0x0053A3AC; 11 literal reference(s), all inside the mapped blocks.
- 10 module log-tag strings loaded by the mapped blocks, including:
- `0x006DCB14` `[box_uart_mgr]crc check failed, data len = %d, tmp_crc: 0x%x, tmp_buf[idx + tmp_len - 1]: 0x%x`
- `0x0073C770` `[box_uart_mgr]uart clear buffer failed: %d
`
- `0x00747EF4` `[box_uart_mgr]box uart unpack err:%d
`
- `0x00747F1C` `[box_uart_mgr]uart tx flush failed: %d
`
- `0x00747F44` `[box_uart_mgr]uart start failed: %d
`
- `0x00747F6C` `[box_uart_mgr]pt cmd execute err:%d
`
- `0x0075261C` `[box_uart_mgr]uart stop failed: %d
`
- `0x00752640` `[box_uart_mgr]box uart pack err:%d
`

## Linked extents

Physical interval `[0x00539E92, 0x0053A414)` = 1410 bytes (1298 body + 112 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x539e92-0x53a010 | 382 | 2 | 144 | `3a65a5ae52ea8b0e...` |
| 0x53a010-0x53a01c | 12 | 0 | 5 | `a5f829f06e244f84...` |
| 0x53a01c-0x53a09c | 128 | 0 | 45 | `31560e97fe7eb6c8...` |
| 0x53a09c-0x53a0b6 | 26 | 0 | 9 | `5db4d56d0b081f45...` |
| 0x53a0b6-0x53a3a4 | 750 | 9 | 299 | `8cf6dda5fc9dd79b...` |

## Ingress (whole-image scans)

- direct BL entry sites: 2; strict-interior BL targets: 3
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks in gap [0x539E92, 0x53A414). Identity: 11 path references across 2 blocks and 10 `[box_uart_mgr]` log tags (UART unpack/CRC/flush error paths of the charging-box UART manager). Registration: entry 0x53A0B6 via external table cell 0x7490C8, entry 0x53A01C via its own trailing-pool cell 0x53A3CC; external callers at 0x4C649E, 0x449F02/0x44A008 (strict-interior), and intra-object sites.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_box_uart_mgr -v
```
