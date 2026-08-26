# G2 platform\device_mgr\box_uart_mgr.c zero-anchor recovery

- Retained path: `platform\device_mgr\box_uart_mgr.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\platform\device_mgr\box_uart_mgr.c`
- Disposition: **linked-unanchored, production source-routed** (code present;
  zero Ghidra-anchored/discovered functions)
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
- two apparent strict-interior targets (`0x449F02`, `0x44A008`) begin in the
  second halfword of valid 32-bit instructions and are overlapping
  pseudo-decodes, not executable ingress; the remaining strict-interior site
  is the real intra-object call at `0x53A1C4 -> 0x539E94`
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks in gap [0x539E92, 0x53A414). Identity: 11 path references across 2 blocks and 10 `[box_uart_mgr]` log tags (UART unpack/CRC/flush error paths of the charging-box UART manager). Registration: entry 0x53A0B6 via external table cell 0x7490C8, entry 0x53A01C via its own trailing-pool cell 0x53A3CC; external callers at 0x4C649E, 0x449F02/0x44A008 (strict-interior), and intra-object sites.

## Production source route

`components/apollo_main/core_overlay/box_uart_mgr.c` now owns all five callable
entries. Five guarded redirects replace 1,296 authenticated stock bytes; only
the two-byte leading alignment word and 112-byte official pool/data tail remain
as compatibility bytes. The selector-isolated Cortex-M55 output is 514 text
bytes plus four alignment bytes with 21 strict relocations.

The clean-room source implements the recovered leading-zero scan, ASCII `T`
passthrough, additive checksum validation, five rotating 1,024-byte receive
slots, channel-2 callback registration/resume/start lifecycle, stop/clear,
product-test dispatch, two-tick response delay, asynchronous send/flush,
unconditional restart, and post-restart product-test execution. Host tests
cover framing success/failure, rotation and zero-fill, length rejection,
registration, and every handler failure gate. All five leaves also compile
independently for Cortex-M55 with `-Wall -Wextra -Werror`.

The canonical overlay/component/package identities are 332,666 / 3,856,062 /
4,634,556 bytes with SHA-256 `80f7aae90196045102d6f1f59be0b49d84b3ed58f017a8f5d56109a2788b8561`,
`96a369aa58d9570a0c6eeb5cde5fd5b309e827bd5f6dcf979eae88df971ccf3a`,
and `430bf420dc4ebcf49dcef43177e134bdb9046f3a93ebb244089552d37deb7933`.
The flash plan is 3,116,640 bytes / SHA-256
`4c4ef626ec165aede17768250dce2a6b163bdd64cf9fb50b084b863e9eae3e40`
with 4,495 placed, two unresolved, five container-only, and six protected
regions. Nothing was signed or flashed.

Live temple-to-case voltage levels, baud/timing, callback concurrency,
restart/flush ordering, case-firmware interoperability, and product-test
traffic remain blocked by unavailable authorized responsive temple/case
hardware and golden UART evidence.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_box_uart_mgr tests.test_box_uart_mgr_candidate -v
```
