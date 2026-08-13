# G2 app\gui\terminal\terminal_query_panel_ui.c zero-anchor recovery

- Retained path: `app\gui\terminal\terminal_query_panel_ui.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_query_panel_ui.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-terminal-query-panel-ui-closure.tsv` (sha256 `1369bc2d6485d331c33565e6954bdcfc327f5749bb1e7ce548081576940f3e1a`)
- Function map: `tools/manifests/g2-terminal-query-panel-ui-function-map.tsv` (sha256 `871b04348f40f6f005827a13eb7684e2538f78c13fa60430432fc0252677776d`)
- Audit: `tools/analyze_g2_terminal_query_panel_ui.py`; test: `tests/test_analyze_g2_terminal_query_panel_ui.py`

## Identity evidence

- Path string at 0x006F0448; pointer cell(s) 0x005EBC40; 2 literal reference(s), all inside the mapped blocks.
- 2 module log-tag strings loaded by the mapped blocks, including:
- `0x006D1788` `[terminal.ui]query align before clamp: idx=%u keep2=%d panel_h=%d view_h=%d pad_t=%d pad_b=%d gap_b=%d safe=%d options_top=%d sel_bottom=%d anchor_bottom=%d target_y=%d max_y=%d browsing=%d`
- `0x0072EBAC` `[terminal.ui]query align target: idx=%u target_y=%d`

## Linked extents

Physical interval `[0x005EB438, 0x005EB8DA)` = 1186 bytes (1186 body + 0 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5eb438-0x5eb47a | 66 | 0 | 26 | `f3bbedd8f9a550df...` |
| 0x5eb47a-0x5eb4f6 | 124 | 0 | 51 | `ffcc70b862c327a3...` |
| 0x5eb4f6-0x5eb576 | 128 | 0 | 50 | `d90803a243a04294...` |
| 0x5eb576-0x5eb61e | 168 | 0 | 63 | `2153eb0fd7c4ca46...` |
| 0x5eb61e-0x5eb646 | 40 | 0 | 15 | `3ec86d6dcad53219...` |
| 0x5eb646-0x5eb8da | 660 | 2 | 230 | `804e53119db58930...` |

## Ingress (whole-image scans)

- direct BL entry sites: 11; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Six blocks in gap [0x5EB438, 0x5EB8DA). Only the 660-byte block 0x5EB646 carries the 2 path references; its `[terminal.ui]query align...` tags confirm the query-panel layout role. The five preceding helper blocks have no references but are called from the terminal cluster (0x5E4D5C, 0x5E4DC2, 0x5E6466, 0x5E79B6, 0x5E7A40, 0x5E7A6E) and from inside the reference block; they are included by contiguity and caller evidence. The path cell 0x5EBC40 is pooled outside the interval.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_terminal_query_panel_ui -v
```
