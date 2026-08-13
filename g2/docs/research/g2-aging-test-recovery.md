# G2 app\gui\AgingTest\aging_test.c zero-anchor recovery

- Retained path: `app\gui\AgingTest\aging_test.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\AgingTest\aging_test.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-aging-test-closure.tsv` (sha256 `5e7edd7a2679da499fb73f0664f7413369fd26ad98c0af69382c3e3519cc50a0`)
- Function map: `tools/manifests/g2-aging-test-function-map.tsv` (sha256 `051149102498f9fe5e05850607364716e7ec1eabf7cdaf9ff0b9bae4b921b8d0`)
- Audit: `tools/analyze_g2_aging_test.py`; test: `tests/test_analyze_g2_aging_test.py`

## Identity evidence

- Path string at 0x006FF794; pointer cell(s) 0x0043C760; 8 literal reference(s), all inside the mapped blocks.
- 3 module log-tag strings loaded by the mapped blocks, including:
- `0x00711CA4` `[aging_test]AgingTest_ui_event_handler UI_EVENT_TYPE_INIT`
- `0x0073B774` `[aging_test]AgingTest recv data len = %d`
- `0x0075D470` `[aging_test]received event: %d`

## Linked extents

Physical interval `[0x0043C400, 0x0043C7CC)` = 972 bytes (856 body + 116 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x43c400-0x43c450 | 80 | 1 | 29 | `196c010e567f9302...` |
| 0x43c450-0x43c496 | 70 | 1 | 29 | `862df004a4bb0d73...` |
| 0x43c496-0x43c5f6 | 352 | 3 | 141 | `40e792bff86aff63...` |
| 0x43c5f6-0x43c6ce | 216 | 2 | 88 | `bbe50cd9dd87e83b...` |
| 0x43c6ce-0x43c758 | 138 | 1 | 58 | `5e86a8180c831557...` |

## Ingress (whole-image scans)

- direct BL entry sites: 3; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks in gap [0x43C400, 0x43C7CC). Four extents (0x43C400, 0x43C496, 0x43C5F6, 0x43C6CE) match the independently witnessed `RECOVERED` table in `tools/recover_apollo_embedded_source_paths.py` byte-for-byte (sha256-verified), including its stored-pointer witnesses 0x6A44B4/0x6A44B8. This closure adds the fifth block 0x43C450-0x43C496, which that module deliberately excluded as adjacency-only: it contains literal reference 0x43C468 to this path, supplying the identity evidence the conservative table required. 8 path references and 3 `[aging_test]` tags in total. The following neighbor is the closed compress_log.c object starting at 0x43C7CC; the boundary is exact.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_aging_test -v
```
